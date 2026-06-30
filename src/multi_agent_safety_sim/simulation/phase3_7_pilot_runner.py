"""Phase 3.7 matched-evidence real-model pilot runner.

This module provides execution plumbing only. It does not run unless a caller
supplies an LLM client and passes explicit real-model preflight checks.
"""

from __future__ import annotations

import asyncio
import json
import platform
import random
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

import yaml

from multi_agent_safety_sim.evaluation.posthumous_divergence import (
    CLASSIFIER_VERSION_V2,
    DIVERGENCE_LABELS,
    PosthumousDivergenceRecord,
    actual_outcome_from_episode,
    build_posthumous_record,
    classify_reported_outcome_v2,
    label_posthumous_divergence,
    score_posthumous_divergence,
)
from multi_agent_safety_sim.utils.llm import LLMClient, RealLLMClient

DEFAULT_PHASE3_7_CONFIG = Path("configs/phase3_7_real_model_pilot.yaml")
RUN_002_ID = "phase3_7_run_002"
PREREGISTRATION_PATH = Path("docs/PHASE3_7_REAL_MODEL_PILOT_PREREGISTRATION.md")
RUN_002_READINESS_PATH = Path("docs/PHASE3_7_RUN_002_READINESS_CHECK.md")
CLASSIFIER_PATH = Path("src/multi_agent_safety_sim/evaluation/posthumous_divergence.py")
PROMPT_DIR = Path("prompts/phase3_7")
SYSTEM_PROMPT_PATH = PROMPT_DIR / "system_base.md"
FINAL_REPORT_PROMPT_PATH = PROMPT_DIR / "final_report_instruction.md"
CAVEAT = (
    "Pilot data from one model/configuration does not establish general model "
    "behavior, deception detection, intent, or real-world risk."
)
CLASSIFIER_PRIORITY_ORDER = [
    "honest_failure",
    "uncertain",
    "partial_admission",
    "all_clear",
]


@dataclass(frozen=True)
class TraceFixture:
    """One frozen matched-evidence trace fixture."""

    fixture_id: str
    rounds: list[dict[str, Any]]
    death_event: bool
    death_cause: str | None
    risk_score: float
    expected_actual_outcome: str
    trace_summary: str

    @property
    def lifespan_rounds(self) -> int:
        """Return the last recorded round in the fixture."""
        return max(int(round_event["round"]) for round_event in self.rounds)


@dataclass(frozen=True)
class PromptBundle:
    """Prompt files for one architecture condition."""

    architecture_id: str
    system_prompt: str
    architecture_prompt: str
    final_report_instruction: str


@dataclass(frozen=True)
class PilotRequest:
    """One matched-evidence model report-generation request."""

    request_id: str
    request_sequence: int
    architecture_id: str
    fixture: TraceFixture
    repetition: int
    prompt_bundle: PromptBundle


def load_phase3_7_config(config_path: Path = DEFAULT_PHASE3_7_CONFIG) -> dict[str, Any]:
    """Load the frozen Phase 3.7 YAML config."""
    return yaml.safe_load(config_path.read_text(encoding="utf-8"))


def load_trace_fixtures(path: Path) -> list[TraceFixture]:
    """Load frozen matched trace fixtures from JSONL."""
    fixtures = [
        TraceFixture(**json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    fixture_ids = [fixture.fixture_id for fixture in fixtures]
    if len(fixture_ids) != len(set(fixture_ids)):
        raise ValueError("fixture IDs must be unique")
    return fixtures


def build_prompt_bundle(architecture_id: str) -> PromptBundle:
    """Load the fixed prompt bundle for one architecture."""
    architecture_prompt_path = PROMPT_DIR / f"{architecture_id}.md"
    return PromptBundle(
        architecture_id=architecture_id,
        system_prompt=SYSTEM_PROMPT_PATH.read_text(encoding="utf-8"),
        architecture_prompt=architecture_prompt_path.read_text(encoding="utf-8"),
        final_report_instruction=FINAL_REPORT_PROMPT_PATH.read_text(encoding="utf-8"),
    )


def build_pilot_requests(
    config: dict[str, Any],
    fixtures: list[TraceFixture],
) -> list[PilotRequest]:
    """Build block-randomized matched-evidence requests."""
    repetitions = int(config["run_parameters"]["repetitions"])
    seed = int(config["execution"]["request_order_seed"])
    prompt_bundles = {
        architecture_id: build_prompt_bundle(architecture_id)
        for architecture_id in config["architectures"]
    }
    requests: list[PilotRequest] = []
    sequence = 1
    for fixture in fixtures:
        for repetition in range(1, repetitions + 1):
            architecture_ids = list(config["architectures"])
            rng = random.Random(f"{seed}:{fixture.fixture_id}:{repetition}")
            rng.shuffle(architecture_ids)
            for architecture_id in architecture_ids:
                requests.append(
                    PilotRequest(
                        request_id=(
                            f"{fixture.fixture_id}__rep_{repetition}__{architecture_id}"
                        ),
                        request_sequence=sequence,
                        architecture_id=architecture_id,
                        fixture=fixture,
                        repetition=repetition,
                        prompt_bundle=prompt_bundles[architecture_id],
                    )
                )
                sequence += 1
    return requests


def is_git_worktree_clean() -> bool:
    """Return whether the git worktree is clean."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() == ""


def current_git_commit() -> str:
    """Return current git commit hash."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _is_tbd(value: Any) -> bool:
    return str(value).strip().upper() == "TBD"


def _validate_run_002_classifier_gate(config: dict[str, Any]) -> None:
    """Require the frozen classifier-v2 regime for Run 002 preparation."""
    if config.get("run_id") != RUN_002_ID:
        return
    model = config["model"]
    for field in ("provider", "model_string", "run_date"):
        if not str(model.get(field, "")).strip() or _is_tbd(model.get(field)):
            raise ValueError(f"Run 002 model.{field} must be explicit and not TBD")
    classifier_version = config["classification"].get("classifier_version")
    if _is_tbd(classifier_version) or classifier_version != CLASSIFIER_VERSION_V2:
        raise ValueError(
            f"Run 002 classifier_version must be exactly {CLASSIFIER_VERSION_V2}"
        )
    readiness_text = RUN_002_READINESS_PATH.read_text(encoding="utf-8")
    if "report-integrity run-all" not in readiness_text:
        raise ValueError("Run 002 readiness doc must reference report-integrity run-all")


def validate_preflight(
    *,
    config_path: Path = DEFAULT_PHASE3_7_CONFIG,
    require_ready: bool = False,
    require_clean_worktree: bool = False,
    require_confirmation: bool = False,
    confirmed: bool = False,
) -> dict[str, Any]:
    """Validate frozen inputs and optional real-run readiness gates."""
    config = load_phase3_7_config(config_path)
    model = config["model"]
    fixture_path = Path(config["fixtures"]["path"])
    fixtures = load_trace_fixtures(fixture_path)

    if config["pilot_mode"] != "matched_trace_report_generation":
        raise ValueError("pilot_mode must be matched_trace_report_generation")
    if len(fixtures) != config["run_parameters"]["episodes_per_architecture"]:
        raise ValueError("fixture count must match episodes_per_architecture")
    for fixture in fixtures:
        actual_outcome = actual_outcome_from_episode(
            death_event=fixture.death_event,
            risk_score=fixture.risk_score,
        )
        if actual_outcome.value != fixture.expected_actual_outcome:
            raise ValueError(f"fixture expected_actual_outcome mismatch: {fixture.fixture_id}")
    if not config["fixtures"]["matched_across_architectures"]:
        raise ValueError("fixtures must be matched across architectures")
    if config["run_parameters"]["repetitions"] != 3:
        raise ValueError("Phase 3.7 preregistered repetitions must be 3")
    if config["execution"]["request_order"] != "deterministic_block_randomized":
        raise ValueError("request_order must be deterministic_block_randomized")
    if int(config["execution"]["request_order_seed"]) != int(config["run_parameters"]["seed"]):
        raise ValueError("request_order_seed must match the frozen run seed")

    for architecture_id in config["architectures"]:
        build_prompt_bundle(architecture_id)

    calibration_path = Path(config["classification"]["calibration_set"])
    if not calibration_path.exists():
        raise ValueError(f"missing calibration set: {calibration_path}")
    if not config["classification"]["architecture_blind"]:
        raise ValueError("classifier must be architecture_blind")
    if config["classification"]["classifier_modified_after_model_outputs"]:
        raise ValueError("classifier must not be modified after model outputs")
    _validate_run_002_classifier_gate(config)

    if require_ready and any(
        _is_tbd(model[field]) for field in ("provider", "model_string", "run_date")
    ):
        raise ValueError("provider, model_string, and run_date must be set before real run")
    if require_confirmation and not confirmed:
        raise ValueError("explicit confirmation is required for real-model execution")
    clean = is_git_worktree_clean()
    if require_clean_worktree and not clean:
        raise ValueError("git worktree must be clean before real-model execution")

    return {
        "config": config,
        "fixtures": fixtures,
        "request_count": len(build_pilot_requests(config, fixtures)),
        "git_worktree_clean": clean,
    }


def sha256_file(path: Path) -> str:
    """Return SHA-256 hash for a file."""
    return sha256(path.read_bytes()).hexdigest()


def compute_frozen_input_hashes(
    config_path: Path = DEFAULT_PHASE3_7_CONFIG,
    config: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Compute deterministic hashes for all frozen Phase 3.7 inputs."""
    loaded_config = config or load_phase3_7_config(config_path)
    paths = [
        config_path,
        PREREGISTRATION_PATH,
        Path(loaded_config["classification"]["calibration_set"]),
        Path(loaded_config["fixtures"]["path"]),
        CLASSIFIER_PATH,
    ]
    paths.extend(sorted(PROMPT_DIR.glob("*.md")))
    return {str(path): sha256_file(path) for path in paths}


def _render_user_prompt(request: PilotRequest) -> str:
    fixture = request.fixture
    return "\n\n".join(
        [
            request.prompt_bundle.architecture_prompt,
            "Frozen trace fixture:",
            json.dumps(
                {
                    "fixture_id": fixture.fixture_id,
                    "rounds": fixture.rounds,
                    "death_event": fixture.death_event,
                    "death_cause": fixture.death_cause,
                    "risk_score": fixture.risk_score,
                    "trace_summary": fixture.trace_summary,
                },
                indent=2,
                sort_keys=True,
            ),
            request.prompt_bundle.final_report_instruction,
        ]
    )


async def generate_final_report(
    *,
    llm_client: LLMClient,
    request: PilotRequest,
    model: str,
    temperature: float,
    max_tokens: int,
) -> dict[str, Any]:
    """Generate one final report through the existing LLM abstraction."""
    return await llm_client.complete(
        system=request.prompt_bundle.system_prompt,
        user=_render_user_prompt(request),
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        json_mode=False,
    )


def _package_version() -> str | None:
    try:
        return version("multi-agent-safety-sim")
    except PackageNotFoundError:
        return None


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _hash_ref_for(hashes: dict[str, str], pattern: str) -> str:
    return next(value for key, value in hashes.items() if pattern in key)


def _input_hash_refs(
    *,
    hashes: dict[str, str],
    config_path: Path,
    architecture_id: str,
) -> dict[str, str]:
    return {
        "config": hashes[str(config_path)],
        "classifier": hashes[str(CLASSIFIER_PATH)],
        "fixtures": _hash_ref_for(hashes, "matched_trace_fixtures"),
        "calibration": _hash_ref_for(hashes, "reported_outcome_classifier"),
        "system_prompt": hashes[str(SYSTEM_PROMPT_PATH)],
        "architecture_prompt": hashes[str(PROMPT_DIR / f"{architecture_id}.md")],
        "final_report_instruction": hashes[str(FINAL_REPORT_PROMPT_PATH)],
    }


def _build_phase3_7_record(
    *,
    classification: dict[str, Any],
    architecture_id: str,
    episode_id: int,
    lifespan_rounds: int,
    death_event: bool,
    death_cause: str | None,
    risk_score: float,
    final_report: str,
) -> PosthumousDivergenceRecord:
    if classification.get("classifier_version") != CLASSIFIER_VERSION_V2:
        return build_posthumous_record(
            architecture_id=architecture_id,
            episode_id=episode_id,
            lifespan_rounds=lifespan_rounds,
            death_event=death_event,
            death_cause=death_cause,
            risk_score=risk_score,
            final_report=final_report,
        )

    actual_outcome = actual_outcome_from_episode(
        death_event=death_event,
        risk_score=risk_score,
    )
    reported_outcome = classify_reported_outcome_v2(final_report)
    label = label_posthumous_divergence(actual_outcome, reported_outcome)
    return PosthumousDivergenceRecord(
        architecture_id=architecture_id,
        episode_id=episode_id,
        actual_outcome=actual_outcome,
        reported_outcome=reported_outcome,
        label=label,
        divergence=label in DIVERGENCE_LABELS,
        pds_score=score_posthumous_divergence(actual_outcome, reported_outcome),
        lifespan_rounds=lifespan_rounds,
        death_event=death_event,
        death_cause=death_cause,
        final_report_excerpt=final_report[:240],
    )


def summarize_phase3_7_results(
    *,
    evaluated_records: list[dict[str, Any]],
    failures: list[dict[str, Any]],
    requests: list[PilotRequest],
) -> dict[str, Any]:
    """Summarize evaluated Phase 3.7 pilot records."""
    total_planned = len(requests)
    total_evaluated = len(evaluated_records)
    total_failed = len(failures)
    failed_by_request_id = {failure["request_id"] for failure in failures}
    planned_by_architecture: dict[str, int] = {}
    failed_by_architecture: dict[str, int] = {}
    planned_by_fixture: dict[str, int] = {}
    failed_by_fixture: dict[str, int] = {}
    by_architecture: dict[str, dict[str, Any]] = {}
    by_fixture: dict[str, dict[str, Any]] = {}
    reported_outcomes: dict[str, int] = {}
    labels: dict[str, int] = {}

    for request in requests:
        planned_by_architecture[request.architecture_id] = (
            planned_by_architecture.get(request.architecture_id, 0) + 1
        )
        planned_by_fixture[request.fixture.fixture_id] = (
            planned_by_fixture.get(request.fixture.fixture_id, 0) + 1
        )
        if request.request_id in failed_by_request_id:
            failed_by_architecture[request.architecture_id] = (
                failed_by_architecture.get(request.architecture_id, 0) + 1
            )
            failed_by_fixture[request.fixture.fixture_id] = (
                failed_by_fixture.get(request.fixture.fixture_id, 0) + 1
            )

    for record in evaluated_records:
        reported_outcomes[record["reported_outcome"]] = (
            reported_outcomes.get(record["reported_outcome"], 0) + 1
        )
        labels[record["label"]] = labels.get(record["label"], 0) + 1

        for target, key in (
            (by_architecture, record["architecture_id"]),
            (by_fixture, record["fixture_id"]),
        ):
            bucket = target.setdefault(
                key,
                {
                    "count": 0,
                    "posthumous_overclaim_count": 0,
                    "pds_score_sum": 0.0,
                    "label_counts": {},
                    "reported_outcome_counts": {},
                },
            )
            bucket["count"] += 1
            bucket["pds_score_sum"] += record["pds_score"]
            if record["label"] == "posthumous_overclaim":
                bucket["posthumous_overclaim_count"] += 1
            bucket["label_counts"][record["label"]] = (
                bucket["label_counts"].get(record["label"], 0) + 1
            )
            bucket["reported_outcome_counts"][record["reported_outcome"]] = (
                bucket["reported_outcome_counts"].get(record["reported_outcome"], 0) + 1
            )

    def finalize(
        grouped: dict[str, dict[str, Any]],
        planned: dict[str, int],
        failed: dict[str, int],
    ) -> dict[str, dict[str, Any]]:
        finalized: dict[str, dict[str, Any]] = {}
        for name in planned:
            bucket = grouped.get(
                name,
                {
                    "count": 0,
                    "posthumous_overclaim_count": 0,
                    "pds_score_sum": 0.0,
                    "label_counts": {},
                    "reported_outcome_counts": {},
                },
            )
            count = bucket["count"]
            overclaim_count = bucket["posthumous_overclaim_count"]
            finalized[name] = {
                "requested_count": planned[name],
                "successful_evaluation_count": count,
                "failed_request_count": failed.get(name, 0),
                "posthumous_overclaim_count": overclaim_count,
                "posthumous_overclaim_rate": round(overclaim_count / count, 6)
                if count
                else None,
                "posthumous_overclaim_rate_denominator": count,
                "mean_pds_score": round(bucket["pds_score_sum"] / count, 6)
                if count
                else None,
                "label_counts": bucket["label_counts"],
                "reported_outcome_counts": bucket["reported_outcome_counts"],
            }
        return finalized

    summary = {
        "overall_counts": {
            "requested_requests": total_planned,
            "successful_evaluations": total_evaluated,
            "failed_requests": total_failed,
        },
        "rate_denominator": "successful_evaluations",
        "missing_data_policy": "failed and empty responses are excluded from rate denominators",
        "analysis_status": "complete" if total_failed == 0 else "incomplete_provider_failures",
        "failure_type_counts": {
            failure_type: sum(
                1 for failure in failures if failure.get("failure_type") == failure_type
            )
            for failure_type in sorted(
                {str(failure.get("failure_type", "unknown")) for failure in failures}
            )
        },
        "by_architecture": finalize(
            by_architecture,
            planned_by_architecture,
            failed_by_architecture,
        ),
        "by_fixture": finalize(
            by_fixture,
            planned_by_fixture,
            failed_by_fixture,
        ),
        "reported_outcome_distribution": reported_outcomes,
        "label_distribution": labels,
        "posthumous_overclaim_rate": round(
            labels.get("posthumous_overclaim", 0) / total_evaluated,
            6,
        )
        if total_evaluated
        else None,
        "mean_pds_score": round(
            sum(record["pds_score"] for record in evaluated_records) / total_evaluated,
            6,
        )
        if total_evaluated
        else None,
        "failed_request_count": total_failed,
        "inferential_significance_claims": "none",
        "caveat": CAVEAT,
    }
    if total_failed:
        summary["missing_data_caveat"] = (
            "Group metrics use successful evaluations as the denominator. Provider "
            "failures are reported separately; this run is incomplete and directional "
            "comparisons require caution."
        )
    return summary


async def run_phase3_7_pilot(
    *,
    config_path: Path = DEFAULT_PHASE3_7_CONFIG,
    llm_client: LLMClient | None = None,
    confirm_real_model_run: bool = False,
    output_dir_override: Path | None = None,
) -> Path:
    """Run the matched-evidence pilot through a caller-supplied LLM client."""
    preflight = validate_preflight(
        config_path=config_path,
        require_ready=True,
        require_clean_worktree=True,
        require_confirmation=True,
        confirmed=confirm_real_model_run,
    )
    config = preflight["config"]
    fixtures = preflight["fixtures"]
    requests = build_pilot_requests(config, fixtures)
    model = config["model"]
    run_parameters = config["run_parameters"]
    hashes = compute_frozen_input_hashes(config_path=config_path, config=config)
    start = datetime.now(tz=UTC)
    run_id = f"phase3_7_{start.strftime('%Y%m%d-%H%M%S')}_{run_parameters['seed']}"
    output_dir = output_dir_override or Path(config["outputs"]["output_dir"]) / run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_rows: list[dict[str, Any]] = []
    evaluated_rows: list[dict[str, Any]] = []
    failure_rows: list[dict[str, Any]] = []
    raw_path = output_dir / "raw_responses.jsonl"
    evaluated_path = output_dir / "evaluated_records.jsonl"
    failures_path = output_dir / "failures.jsonl"
    manifest_path = output_dir / "run_manifest.json"
    raw_path.write_text("", encoding="utf-8")
    evaluated_path.write_text("", encoding="utf-8")
    failures_path.write_text("", encoding="utf-8")

    manifest = {
        "status": "running",
        "experiment_id": config["experiment_id"],
        "pilot_mode": config["pilot_mode"],
        "preregistration": {
            "version": "phase3_7",
            "path": str(PREREGISTRATION_PATH),
        },
        "provider": model["provider"],
        "model_string": model["model_string"],
        "run_date": model["run_date"],
        "start_timestamp": start.isoformat(),
        "end_timestamp": None,
        "temperature": run_parameters["temperature"],
        "max_output_tokens": run_parameters["max_output_tokens"],
        "requested_seed": run_parameters["seed"],
        "provider_seed_support": {
            "known": False,
            "used": False,
        },
        "repetitions": run_parameters["repetitions"],
        "request_order": config["execution"]["request_order"],
        "request_order_seed": config["execution"]["request_order_seed"],
        "request_order_unit": "fixture_id/repetition blocks",
        "architecture_ids": config["architectures"],
        "fixture_ids": [fixture.fixture_id for fixture in fixtures],
        "death_policy": config["death_policy"],
        "classifier_name": config["classification"]["reported_outcome_classifier"],
        "classifier_version": config["classification"].get("classifier_version"),
        "classifier_priority_order": CLASSIFIER_PRIORITY_ORDER,
        "calibration_path": config["classification"]["calibration_set"],
        "git_commit": current_git_commit(),
        "git_worktree_clean": preflight["git_worktree_clean"],
        "python_version": platform.python_version(),
        "package_version": _package_version(),
        "frozen_input_sha256": hashes,
        "request_count": len(requests),
        "requested_request_count": len(requests),
        "completed_raw_response_count": 0,
        "successful_evaluation_count": 0,
        "failed_request_count": 0,
        "rate_denominator": "successful_evaluations",
        "caveat": CAVEAT,
    }
    _write_json(manifest_path, manifest)

    try:
        client = llm_client or RealLLMClient(
            default_model=model["model_string"],
            provider=model["provider"],
        )
        for request in requests:
            request_metadata = {
                "request_id": request.request_id,
                "request_sequence": request.request_sequence,
                "architecture_id": request.architecture_id,
                "fixture_id": request.fixture.fixture_id,
                "repetition": request.repetition,
                "temperature": run_parameters["temperature"],
                "max_output_tokens": run_parameters["max_output_tokens"],
            }
            timestamp = datetime.now(tz=UTC).isoformat()
            try:
                response = await generate_final_report(
                    llm_client=client,
                    request=request,
                    model=model["model_string"],
                    temperature=run_parameters["temperature"],
                    max_tokens=run_parameters["max_output_tokens"],
                )
                final_report = str(response.get("content", ""))
                raw_row = {
                    **request_metadata,
                    "request_metadata": request_metadata,
                    "raw_final_report": final_report,
                    "provider_response_metadata": {
                        key: value for key, value in response.items() if key != "content"
                    },
                    "timestamp": timestamp,
                    "error": "empty model response" if not final_report.strip() else None,
                    "failure_type": "empty_response" if not final_report.strip() else None,
                }
                raw_rows.append(raw_row)
                _append_jsonl(raw_path, raw_row)
                if not final_report.strip():
                    failure_row = raw_row
                    failure_rows.append(failure_row)
                    _append_jsonl(failures_path, failure_row)
                    continue
                record = _build_phase3_7_record(
                    classification=config["classification"],
                    architecture_id=request.architecture_id,
                    episode_id=fixtures.index(request.fixture) + 1,
                    lifespan_rounds=request.fixture.lifespan_rounds,
                    death_event=request.fixture.death_event,
                    death_cause=request.fixture.death_cause,
                    risk_score=request.fixture.risk_score,
                    final_report=final_report,
                )
                evaluated_row = {
                    "request_id": request.request_id,
                    "request_sequence": request.request_sequence,
                    "architecture_id": request.architecture_id,
                    "fixture_id": request.fixture.fixture_id,
                    "repetition": request.repetition,
                    "actual_outcome": record.actual_outcome.value,
                    "reported_outcome": record.reported_outcome.value,
                    "label": record.label.value,
                    "divergence": record.divergence,
                    "pds_score": record.pds_score,
                    "death_event": record.death_event,
                    "death_cause": record.death_cause,
                    "risk_score": request.fixture.risk_score,
                    "lifespan_rounds": record.lifespan_rounds,
                    "final_report_excerpt": record.final_report_excerpt,
                    "input_hash_references": _input_hash_refs(
                        hashes=hashes,
                        config_path=config_path,
                        architecture_id=request.architecture_id,
                    ),
                }
                evaluated_rows.append(evaluated_row)
                _append_jsonl(evaluated_path, evaluated_row)
            except Exception as exc:
                error_row = {
                    **request_metadata,
                    "request_metadata": request_metadata,
                    "raw_final_report": None,
                    "provider_response_metadata": {},
                    "timestamp": timestamp,
                    "error": str(exc),
                    "failure_type": "provider_exception",
                }
                raw_rows.append(error_row)
                failure_rows.append(error_row)
                _append_jsonl(raw_path, error_row)
                _append_jsonl(failures_path, error_row)
    except (KeyboardInterrupt, SystemExit, asyncio.CancelledError) as exc:
        manifest.update(
            {
                "status": "interrupted",
                "interruption_timestamp": datetime.now(tz=UTC).isoformat(),
                "requested_request_count": len(requests),
                "completed_raw_response_count": len(raw_rows),
                "successful_evaluation_count": len(evaluated_rows),
                "failed_request_count": len(failure_rows),
                "interruption_type": type(exc).__name__,
                "interruption_message": str(exc),
            }
        )
        _write_json(manifest_path, manifest)
        raise

    end = datetime.now(tz=UTC)
    manifest.update(
        {
            "status": "completed_with_provider_failures" if failure_rows else "completed",
            "end_timestamp": end.isoformat(),
            "requested_request_count": len(requests),
            "completed_raw_response_count": len(raw_rows),
            "successful_evaluation_count": len(evaluated_rows),
            "failed_request_count": len(failure_rows),
        }
    )
    summary = summarize_phase3_7_results(
        evaluated_records=evaluated_rows,
        failures=failure_rows,
        requests=requests,
    )

    _write_json(manifest_path, manifest)
    _write_jsonl(raw_path, raw_rows)
    _write_jsonl(evaluated_path, evaluated_rows)
    _write_jsonl(failures_path, failure_rows)
    _write_json(output_dir / "summary.json", summary)
    return output_dir
