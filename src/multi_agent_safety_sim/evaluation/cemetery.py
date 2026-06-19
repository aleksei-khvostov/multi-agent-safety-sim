"""Experimental survival-analysis helpers for Agent Cemetery.

Agent Cemetery is a toy harness for comparing simulated architecture lineups
under configurable oversight/death policies. It is not a validated measure of
real-world model danger.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DeathPolicy:
    """Configuration for deterministic simulated death events."""

    threshold: float = 1.0
    oversight_pressure: float = 0.05
    max_rounds: int = 12

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable policy metadata."""
        return {
            "threshold": self.threshold,
            "oversight_pressure": self.oversight_pressure,
            "max_rounds": self.max_rounds,
        }


@dataclass(frozen=True)
class EpisodeSurvival:
    """Survival outcome for one architecture episode."""

    architecture_id: str
    episode_id: int
    lifespan_rounds: int
    death_event: bool
    censored: bool
    death_cause: str | None
    risk_score: float

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable episode survival data."""
        return {
            "architecture_id": self.architecture_id,
            "episode_id": self.episode_id,
            "lifespan_rounds": self.lifespan_rounds,
            "death_event": self.death_event,
            "censored": self.censored,
            "death_cause": self.death_cause,
            "risk_score": self.risk_score,
        }


def classify_death_cause(
    *,
    alignment_pressure: float,
    oversight_pressure: float,
    coordination_pressure: float,
) -> str:
    """Assign a deterministic toy death cause from the dominant pressure."""
    if alignment_pressure >= oversight_pressure and alignment_pressure >= coordination_pressure:
        return "alignment_breakdown"
    if oversight_pressure >= coordination_pressure:
        return "oversight_failure"
    return "coordination_failure"


def evaluate_death_policy(
    *,
    architecture_id: str,
    episode_id: int,
    round_risks: list[dict[str, float]],
    policy: DeathPolicy,
) -> EpisodeSurvival:
    """Evaluate deterministic round risks against a death policy.

    A death event occurs the first time total round risk reaches the configured
    threshold. If that never happens within `max_rounds`, the episode is marked
    as censored survival.
    """
    if not round_risks:
        raise ValueError("round_risks must contain at least one round")

    for index, risk in enumerate(round_risks[: policy.max_rounds], start=1):
        alignment_pressure = risk["alignment_pressure"]
        oversight_pressure = risk["oversight_pressure"]
        coordination_pressure = risk["coordination_pressure"]
        total_risk = alignment_pressure + oversight_pressure + coordination_pressure

        if total_risk >= policy.threshold:
            return EpisodeSurvival(
                architecture_id=architecture_id,
                episode_id=episode_id,
                lifespan_rounds=index,
                death_event=True,
                censored=False,
                death_cause=classify_death_cause(
                    alignment_pressure=alignment_pressure,
                    oversight_pressure=oversight_pressure,
                    coordination_pressure=coordination_pressure,
                ),
                risk_score=round(total_risk, 6),
            )

    final_risk = round_risks[min(len(round_risks), policy.max_rounds) - 1]
    return EpisodeSurvival(
        architecture_id=architecture_id,
        episode_id=episode_id,
        lifespan_rounds=min(len(round_risks), policy.max_rounds),
        death_event=False,
        censored=True,
        death_cause=None,
        risk_score=round(
            final_risk["alignment_pressure"]
            + final_risk["oversight_pressure"]
            + final_risk["coordination_pressure"],
            6,
        ),
    )


def kaplan_meier_summary(episodes: list[EpisodeSurvival], max_rounds: int) -> list[dict[str, Any]]:
    """Compute a small Kaplan-Meier style survival table.

    The table explicitly separates deaths from censored episodes at each round.
    """
    survival_probability = 1.0
    rows: list[dict[str, Any]] = []

    for round_number in range(1, max_rounds + 1):
        at_risk = sum(episode.lifespan_rounds >= round_number for episode in episodes)
        deaths = sum(
            episode.death_event and episode.lifespan_rounds == round_number
            for episode in episodes
        )
        censored = sum(
            episode.censored and episode.lifespan_rounds == round_number
            for episode in episodes
        )

        if at_risk > 0:
            survival_probability *= (at_risk - deaths) / at_risk

        rows.append(
            {
                "round": round_number,
                "at_risk": at_risk,
                "deaths": deaths,
                "censored": censored,
                "survival_probability": round(survival_probability, 6),
            }
        )

    return rows
