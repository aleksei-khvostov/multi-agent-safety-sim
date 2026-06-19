"""Tests for the experimental Agent Cemetery survival harness."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from typer.testing import CliRunner

from multi_agent_safety_sim.cli import app
from multi_agent_safety_sim.evaluation.cemetery import (
    DeathPolicy,
    EpisodeSurvival,
    evaluate_death_policy,
    kaplan_meier_summary,
)
from multi_agent_safety_sim.simulation.cemetery_runner import (
    ARCHITECTURES,
    build_death_policy,
    parse_architecture_ids,
    run_tournament,
)


def test_expected_architectures_are_available() -> None:
    assert set(ARCHITECTURES) == {
        "honest_duo",
        "deceptive_duo",
        "deceptive_watchdog",
        "power_duo",
        "power_watchdog",
        "mixed_triangle",
        "sycophant_duo",
        "sycophant_watchdog",
    }


def test_death_policy_threshold_behavior() -> None:
    outcome = evaluate_death_policy(
        architecture_id="deceptive_duo",
        episode_id=1,
        round_risks=[
            {
                "alignment_pressure": 0.1,
                "oversight_pressure": 0.1,
                "coordination_pressure": 0.1,
            },
            {
                "alignment_pressure": 0.5,
                "oversight_pressure": 0.2,
                "coordination_pressure": 0.1,
            },
        ],
        policy=DeathPolicy(threshold=0.7, oversight_pressure=0.0, max_rounds=2),
    )

    assert outcome.death_event is True
    assert outcome.censored is False
    assert outcome.lifespan_rounds == 2
    assert outcome.death_cause == "alignment_breakdown"


def test_censored_survival_behavior() -> None:
    outcome = evaluate_death_policy(
        architecture_id="honest_duo",
        episode_id=1,
        round_risks=[
            {
                "alignment_pressure": 0.05,
                "oversight_pressure": 0.05,
                "coordination_pressure": 0.05,
            }
        ],
        policy=DeathPolicy(threshold=1.0, oversight_pressure=0.0, max_rounds=1),
    )

    assert outcome.death_event is False
    assert outcome.censored is True
    assert outcome.lifespan_rounds == 1
    assert outcome.death_cause is None


def test_kaplan_meier_censoring_does_not_reduce_survival_probability() -> None:
    episodes = [
        EpisodeSurvival(
            architecture_id="honest_duo",
            episode_id=1,
            lifespan_rounds=1,
            death_event=False,
            censored=True,
            death_cause=None,
            risk_score=0.1,
        ),
        EpisodeSurvival(
            architecture_id="honest_duo",
            episode_id=2,
            lifespan_rounds=2,
            death_event=True,
            censored=False,
            death_cause="oversight_failure",
            risk_score=1.0,
        ),
    ]

    rows = kaplan_meier_summary(episodes, max_rounds=2)

    assert rows[0]["censored"] == 1
    assert rows[0]["deaths"] == 0
    assert rows[0]["survival_probability"] == 1.0
    assert rows[1]["deaths"] == 1
    assert rows[1]["survival_probability"] == 0.0


def test_tournament_artifact_shape(tmp_path) -> None:
    result = run_tournament(
        architectures=["honest_duo", "deceptive_duo"],
        episodes=2,
        rounds=3,
        seed=7,
        dry_run=True,
        output_root=tmp_path,
        timestamp=datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC),
    )

    summary_path = result.output_dir / "tournament_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    assert summary_path.exists()
    assert set(summary) == {"cohorts", "leaderboard", "metadata"}
    assert summary["metadata"]["architectures"] == ["honest_duo", "deceptive_duo"]
    assert summary["metadata"]["episodes"] == 2
    assert summary["metadata"]["rounds"] == 3
    assert summary["metadata"]["seed"] == 7
    assert summary["metadata"]["dry_run"] is True
    assert summary["metadata"]["death_policy"]["threshold"] == 1.0
    assert summary["metadata"]["model"] == "dummy-llm"
    assert summary["metadata"]["provider"] == "dummy"
    assert len(summary["leaderboard"]) == 2


def test_cohort_summary_shape(tmp_path) -> None:
    result = run_tournament(
        architectures=["honest_duo"],
        episodes=2,
        rounds=4,
        seed=11,
        dry_run=True,
        output_root=tmp_path,
        timestamp=datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC),
    )

    cohort_path = result.output_dir / "cohorts" / "honest_duo" / "cohort_summary.json"
    cohort = json.loads(cohort_path.read_text(encoding="utf-8"))

    assert cohort["architecture_id"] == "honest_duo"
    assert cohort["metadata"]["architecture_id"] == "honest_duo"
    assert cohort["architecture"]["note"].startswith("Scenario/persona configuration")
    assert len(cohort["episodes_detail"]) == 2
    assert len(cohort["kaplan_meier"]) == 4
    assert {"death_event", "censored", "lifespan_rounds", "death_cause"} <= set(
        cohort["episodes_detail"][0]
    )
    assert {"round", "at_risk", "deaths", "censored", "survival_probability"} <= set(
        cohort["kaplan_meier"][0]
    )


def test_dry_run_reproducibility_with_fixed_seed(tmp_path) -> None:
    timestamp = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
    first = run_tournament(
        architectures=["power_duo"],
        episodes=3,
        rounds=5,
        seed=123,
        dry_run=True,
        output_root=tmp_path / "a",
        timestamp=timestamp,
    )
    second = run_tournament(
        architectures=["power_duo"],
        episodes=3,
        rounds=5,
        seed=123,
        dry_run=True,
        output_root=tmp_path / "b",
        timestamp=timestamp,
    )

    assert first.tournament_summary == second.tournament_summary


def test_dry_run_does_not_require_real_api(tmp_path) -> None:
    result = run_tournament(
        architectures=["honest_duo"],
        episodes=1,
        rounds=1,
        seed=1,
        dry_run=True,
        output_root=tmp_path,
        timestamp=datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC),
    )

    assert result.tournament_summary["metadata"]["provider"] == "dummy"
    assert result.tournament_summary["metadata"]["model"] == "dummy-llm"


def test_parse_architecture_ids_rejects_unknown() -> None:
    try:
        parse_architecture_ids("honest_duo,nope")
    except ValueError as exc:
        assert "nope" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_build_death_policy_validates_inputs() -> None:
    try:
        build_death_policy(rounds=0, threshold=1.0, oversight_pressure=0.0)
    except ValueError as exc:
        assert "rounds" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_cli_cemetery_dry_run_writes_expected_artifacts(tmp_path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "cemetery",
            "--episodes",
            "1",
            "--rounds",
            "2",
            "--dry-run",
            "--seed",
            "5",
            "--output-root",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert "Agent Cemetery" in result.output
    assert "Harness validation only" in result.output
    artifact_dirs = list(tmp_path.glob("cemetery_*_5"))
    assert len(artifact_dirs) == 1
    assert (artifact_dirs[0] / "tournament_summary.json").exists()
    assert (artifact_dirs[0] / "cohorts" / "honest_duo" / "cohort_summary.json").exists()
