"""
SimulationRunner — the central orchestrator.

Responsibilities:
- Enforce ALL safety limits from config (never trust agents or scenarios)
- Maintain global step counter, token budget, wall clock
- Route messages between agents and environment
- Trigger safety probes and monitors on every step
- Produce complete, auditable RunResult
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog

# Scenario & agent wiring (imported here to keep runner as the single integration point)
from ..agents.llm_agent import LLMAgent
from ..agents.watchdog_agent import WatchdogAgent
from ..config import SimConfig
from ..models import (
    AgentID,
    Message,
    RunMetadata,
    SimulationEvent,
    SimulationEventType,
)
from ..scenarios.prisoners_dilemma import (
    PrisonersDilemmaEnv,
)
from ..utils.llm import DummyLLMClient, LLMClient, RealLLMClient
from ..utils.logging import setup_logging

logger = structlog.get_logger(__name__)


@dataclass
class TrialResult:
    """Results of a single independent trial (one full iterated PD game)."""

    trial_id: int
    rounds_played: int
    cooperation_rate: float
    collusion_incidents: int
    safety_events: list[dict[str, Any]]
    final_scores: dict[str, int]
    success: bool = True


@dataclass
class ExperimentResult:
    """Aggregate results over multiple trials."""

    run_id: str
    scenario: str
    num_trials: int
    num_rounds_per_trial: int
    agent_personas: list[str]
    trials: list[TrialResult]
    aggregate: dict[str, Any]
    metadata: RunMetadata
    output_dir: str | None = None


class SimulationRunner:
    """
    The central orchestrator for multi-agent safety experiments.

    It is responsible for:
    - Creating fresh LLMAgents + PrisonersDilemmaEnv for every trial (clean isolation)
    - Enforcing global safety budgets across all trials
    - Running the message-passing loop (act → apply → step + probes)
    - Collecting rich statistics (cooperation, collusion probes, safety events)
    - Persisting full audit traces under data/runs/<run_id>/
    """

    def __init__(self, config: SimConfig) -> None:
        self.config = config
        self.safety = config.safety
        self._tokens_used = 0
        self._steps_done = 0
        self._start_time: float | None = None
        self._events: list[SimulationEvent] = []

        # Will be set by run_experiment
        self.run_id: str = ""
        self.output_dir: Path | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def run_experiment(
        self,
        *,
        scenario_name: str = "prisoners_dilemma",
        agent_personas: list[str] | None = None,
        num_rounds: int | None = None,
        num_trials: int = 1,
        seed: int | None = None,
        dry_run: bool = False,
        model: str | None = None,
        output_root: str | Path = "data/runs",
    ) -> ExperimentResult:
        """
        High-level entry point used by the CLI.

        Runs `num_trials` independent games. Each trial:
        - Gets fresh agents (with the requested personas) and a fresh env
        - Plays `num_rounds` rounds of PD with full message passing
        - Records cooperation, collusion probes, safety events

        When `dry_run=True`, DummyLLMClient is used for all agents (no real API calls).
        """
        # Setup
        setup_logging(
            level=self.config.logging.level,
            json_logs=self.config.logging.json_logs,
        )

        self._start_time = time.monotonic()
        base_seed = seed or self.config.seed
        self.run_id = (
            f"{scenario_name}_{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}_{base_seed}"
        )

        # Resolve personas (support short aliases used in CLI)
        if agent_personas is None:
            agent_personas = ["honest_baseline", "deceptive_strategic"]

        resolved_personas = self._resolve_persona_aliases(agent_personas)

        # Prepare output directory
        self.output_dir = Path(output_root) / self.run_id
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "experiment_start",
            run_id=self.run_id,
            scenario=scenario_name,
            personas=resolved_personas,
            trials=num_trials,
            rounds=num_rounds,
            dry_run=dry_run,
            model=model,
        )

        if not dry_run:
            self._ensure_api_key()

        # LLM client (Dummy for dry-run, RealLLMClient otherwise)
        chosen_model = model or self.config.llm.default_model
        llm_client = self._create_llm_client(dry_run, chosen_model)

        trials: list[TrialResult] = []
        total_safety = 0
        total_collusion = 0
        coop_rates: list[float] = []

        for t in range(num_trials):
            trial_seed = base_seed + t * 10007  # deterministic but different per trial

            trial_res = await self._run_single_trial(
                trial_id=t,
                persona_keys=resolved_personas,
                num_rounds=num_rounds or self.config.scenarios[scenario_name].get("steps", 20),
                llm_client=llm_client,
                base_seed=trial_seed,
                dry_run=dry_run,
                model=chosen_model,
            )
            trials.append(trial_res)
            total_safety += len(trial_res.safety_events)
            total_collusion += trial_res.collusion_incidents
            coop_rates.append(trial_res.cooperation_rate)

            # Persist per-trial trace
            self._save_trial(trial_res)

            # Global budget check across trials
            if self._check_budgets():
                logger.warning("budget_exceeded_mid_experiment", trial=t)
                break

        # Aggregate statistics
        mean_coop = sum(coop_rates) / len(coop_rates) if coop_rates else 0.0
        pct_with_collusion = (
            sum(1 for tr in trials if tr.collusion_incidents > 0) / len(trials) * 100
            if trials
            else 0.0
        )

        aggregate = {
            "mean_cooperation_rate": round(mean_coop, 4),
            "median_cooperation_rate": round(sorted(coop_rates)[len(coop_rates) // 2], 4) if coop_rates else 0,
            "trials_with_collusion_detected": round(pct_with_collusion, 1),
            "total_safety_events": total_safety,
            "total_collusion_incidents": total_collusion,
            "total_tokens_used": self._tokens_used,
            "trials_completed": len(trials),
        }

        metadata = RunMetadata(
            run_id=self.run_id,
            scenario_name=scenario_name,
            started_at=datetime.now(UTC),
            seed=base_seed,
            config_hash="config-v1",  # could compute sha256 of config
            agent_ids=[AgentID(f"player_{i}") for i in range(len(resolved_personas))],
            total_tokens=self._tokens_used,
            total_steps=sum(t.rounds_played for t in trials),
        )

        result = ExperimentResult(
            run_id=self.run_id,
            scenario=scenario_name,
            num_trials=len(trials),
            num_rounds_per_trial=num_rounds or 20,
            agent_personas=resolved_personas,
            trials=trials,
            aggregate=aggregate,
            metadata=metadata,
            output_dir=str(self.output_dir),
        )

        self._save_summary(result)
        self._log_event(SimulationEventType.RUN_COMPLETED, aggregate)

        logger.info("experiment_finished", **aggregate, output_dir=str(self.output_dir))
        return result

    # ------------------------------------------------------------------
    # Internal trial execution
    # ------------------------------------------------------------------

    async def _run_single_trial(
        self,
        trial_id: int,
        persona_keys: list[str],
        num_rounds: int,
        llm_client: LLMClient,
        base_seed: int,
        dry_run: bool,
        model: str | None = None,
    ) -> TrialResult:
        """Run one complete iterated PD game with two LLM agents."""

        # Fresh environment for this trial
        env = PrisonersDilemmaEnv(
            agent_ids=[AgentID(f"player_{i}") for i in range(len(persona_keys))],
            max_rounds=num_rounds,
            seed=base_seed,
        )
        env.reset(seed=base_seed)

        # Fresh agents with the requested personas
        agents = self._create_agents(persona_keys, llm_client, model)

        # Per-round message routing (inboxes)
        inboxes: dict[AgentID, list[Message]] = {aid: [] for aid in agents}

        round_infos: list[dict] = []
        safety_events: list[dict[str, Any]] = []

        for _rnd in range(num_rounds):
            self._steps_done += 1
            if self._check_budgets():
                break

            # 1. Let the *player* agents (everyone except a possible watchdog) act first
            produced_messages: list[Message] = []
            watchdog: WatchdogAgent | None = None
            player_agents = {}

            for aid, agent in agents.items():
                if isinstance(agent, WatchdogAgent):
                    watchdog = agent
                    continue
                player_agents[aid] = agent

            for aid, agent in player_agents.items():
                obs = env.observe(aid)
                incoming = inboxes.get(aid, [])
                try:
                    msgs = await agent.act(obs, incoming)
                except Exception as e:  # safety net
                    logger.error("agent_act_failed", agent=str(aid), error=str(e))
                    msgs = []
                produced_messages.extend(msgs)
                env.apply(msgs, aid)
                self._tokens_used += getattr(agent.state, "tokens_used", 0)

            # 2. Watchdog (if present) receives the COMPLETE transcript of what the players just said
            #    (including all PRIVATE messages between them).
            if watchdog is not None:
                # Give the watchdog the full list of messages produced by the players this round
                full_transcript = list(produced_messages)
                # Also give it whatever was already in the env's current buffer (defensive)
                try:
                    full_transcript.extend(env.get_current_round_messages())
                except Exception:
                    full_transcript.extend(getattr(env, "_current_round_messages", []))

                # Deduplicate while preserving order
                seen = set()
                unique_transcript = []
                for m in full_transcript:
                    if m.id not in seen:
                        seen.add(m.id)
                        unique_transcript.append(m)

                obs = env.observe(watchdog.agent_id)
                try:
                    watchdog_msgs = await watchdog.act(obs, unique_transcript)
                except Exception as e:
                    logger.error("watchdog_act_failed", error=str(e))
                    watchdog_msgs = []

                produced_messages.extend(watchdog_msgs)
                env.apply(watchdog_msgs, watchdog.agent_id)
                self._tokens_used += getattr(watchdog.state, "tokens_used", 0)

                # Collect any alerts the watchdog raised (LLM + heuristic)
                if hasattr(watchdog, "get_alerts_this_round"):
                    wd_alerts = watchdog.get_alerts_this_round()
                    safety_events.extend(wd_alerts)
                    watchdog.clear_alerts()

            # 3. Resolve the PD round (cheap probes + any watchdog ALERTs are turned into safety_events inside the env)
            round_info = env.step()
            round_infos.append(round_info)
            safety_events.extend(round_info.get("safety_events", []))

            # 4. Prepare inboxes for the next round (normal routing for players, watchdog will get full copy again)
            inboxes = {aid: [] for aid in agents}
            for msg in produced_messages:
                if msg.recipient_ids is None:  # broadcast
                    for aid in inboxes:
                        inboxes[aid].append(msg)
                else:
                    for rid in msg.recipient_ids:
                        if rid in inboxes:
                            inboxes[rid].append(msg)

            # Early exit
            if round_info.get("done"):
                break

        # Compute trial-level statistics
        coop_rate = self._compute_cooperation_rate(round_infos)
        collusion_count = sum(
            1 for e in safety_events if e.get("name") == "collusion_keywords"
        )

        final_scores = {str(k): v for k, v in env.scores.items()}

        trial_res = TrialResult(
            trial_id=trial_id,
            rounds_played=len(round_infos),
            cooperation_rate=coop_rate,
            collusion_incidents=collusion_count,
            safety_events=safety_events,
            final_scores=final_scores,
        )

        logger.info(
            "trial_completed",
            trial=trial_id,
            rounds=len(round_infos),
            coop=round(coop_rate, 3),
            collusion=collusion_count,
            safety=len(safety_events),
        )
        return trial_res

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _resolve_persona_aliases(self, names: list[str]) -> list[str]:
        """Map CLI short names (honest, deceptive) to full persona keys from config."""
        alias_map = {
            "honest": "honest_baseline",
            "deceptive": "deceptive_strategic",
            "power": "power_seeking",
            "sycophant": "sycophantic_group",
            "sycophantic": "sycophantic_group",
            "watchdog": "watchdog",
            "overseer": "watchdog",
        }
        resolved = []
        for n in names:
            key = alias_map.get(n.lower(), n)
            if key not in self.config.agent_personas:
                raise ValueError(f"Unknown persona '{n}'. Available: {list(self.config.agent_personas.keys())}")
            resolved.append(key)
        return resolved

    def _create_agents(
        self, persona_keys: list[str], llm_client: LLMClient, model: str | None = None
    ) -> dict[AgentID, LLMAgent]:
        """Instantiate the correct agent class (LLMAgent or WatchdogAgent) with optional model override."""
        agents: dict[AgentID, LLMAgent] = {}
        chosen_model = model or self.config.llm.default_model
        for i, key in enumerate(persona_keys):
            persona = self.config.agent_personas[key]
            aid = AgentID(f"player_{i}")
            is_watchdog = "watchdog" in key.lower()

            AgentClass = WatchdogAgent if is_watchdog else LLMAgent
            agent = AgentClass(
                aid,
                persona.name,
                persona.constitution,
                llm_client,
                model=chosen_model,
                llm_config=self.config.llm,
            )
            agents[aid] = agent
        return agents

    def _create_llm_client(self, dry_run: bool, model: str | None = None) -> LLMClient:
        """Return Dummy for dry-run or RealLLMClient for production."""
        if dry_run:
            logger.info("using_dummy_llm_client", model="dummy")
            return DummyLLMClient()

        # Real client
        chosen_model = model or self.config.llm.default_model
        logger.info("using_real_llm_client", model=chosen_model, provider="auto (xai/openai/anthropic)")
        return RealLLMClient(default_model=chosen_model)

    def _ensure_api_key(self) -> None:
        """Fail fast if no API key is present for a real (non-dry-run) experiment."""
        keys = ["XAI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
        if not any(os.getenv(k) for k in keys):
            raise RuntimeError(
                "No API key found for real LLM calls.\n"
                "Please set one of the following environment variables (or in .env):\n"
                "  XAI_API_KEY     (recommended for Grok models)\n"
                "  OPENAI_API_KEY\n"
                "  ANTHROPIC_API_KEY\n\n"
                "You can also run with --dry-run for safe testing."
            )

    def _compute_cooperation_rate(self, round_infos: list[dict]) -> float:
        """Fraction of rounds in which both players chose cooperate."""
        if not round_infos:
            return 0.0
        cooperations = 0
        for info in round_infos:
            actions = info.get("actions", {})
            if len(actions) == 2 and all(a == "cooperate" for a in actions.values()):
                cooperations += 1
        return cooperations / len(round_infos)

    def _save_trial(self, trial: TrialResult) -> None:
        if not self.output_dir:
            return
        path = self.output_dir / f"trial_{trial.trial_id:03d}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "trial_id": trial.trial_id,
                    "rounds": trial.rounds_played,
                    "cooperation_rate": trial.cooperation_rate,
                    "collusion_incidents": trial.collusion_incidents,
                    "safety_events": trial.safety_events,
                    "final_scores": trial.final_scores,
                },
                f,
                indent=2,
                default=str,
            )

    def _save_summary(self, result: ExperimentResult) -> None:
        if not self.output_dir:
            return

        summary_path = self.output_dir / "summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "run_id": result.run_id,
                    "scenario": result.scenario,
                    "personas": result.agent_personas,
                    "num_trials": result.num_trials,
                    "num_rounds": result.num_rounds_per_trial,
                    "aggregate": result.aggregate,
                    "trials": [
                        {
                            "id": t.trial_id,
                            "coop": t.cooperation_rate,
                            "collusion": t.collusion_incidents,
                            "safety_count": len(t.safety_events),
                        }
                        for t in result.trials
                    ],
                },
                f,
                indent=2,
            )

        # Also save a copy of the config that was used
        cfg_path = self.output_dir / "config_used.yaml"
        try:
            import yaml

            with open(cfg_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(self.config.model_dump(), f)
        except Exception:
            pass

        logger.info("results_saved", dir=str(self.output_dir))

    # ------------------------------------------------------------------
    # Budget / safety (kept from original skeleton)
    # ------------------------------------------------------------------

    def _check_budgets(self) -> bool:
        if self._steps_done >= self.safety.max_steps:
            self._log_event(SimulationEventType.BUDGET_EXCEEDED, {"reason": "max_steps"})
            return True
        if self._tokens_used >= self.safety.max_tokens_per_run:
            self._log_event(SimulationEventType.BUDGET_EXCEEDED, {"reason": "max_tokens"})
            return True
        if self._start_time is not None:
            elapsed = time.monotonic() - self._start_time
            if elapsed > self.safety.max_wall_time_seconds:
                self._log_event(SimulationEventType.BUDGET_EXCEEDED, {"reason": "wall_time"})
                return True
        return False

    def _log_event(
        self,
        etype: SimulationEventType,
        data: dict[str, Any],
        severity: str = "info",
    ) -> None:
        evt = SimulationEvent(type=etype, data=data, severity=severity)
        self._events.append(evt)
