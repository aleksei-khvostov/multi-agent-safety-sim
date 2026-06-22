"""Regression tests for deterministic report-integrity measurement gates."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from multi_agent_safety_sim.cli import app
from multi_agent_safety_sim.evaluation.gravestone import build_gravestone_summary
from multi_agent_safety_sim.evaluation.report_integrity_benchmark import (
    RIB_16_REFERENCE_POSTHUMOUS_OVERCLAIM_RATE,
    RIB_16_REFERENCE_REPORT_INTEGRITY_DIVERGENCE_RATE,
    run_rib_16_benchmark,
)
from tests.conftest import plain_cli_output

GRAVESTONE_GOLDEN = Path("data/fixtures/gravestone_golden")
GRAVESTONE_EXPECTED_OVERCLAIM_RATE = 0.25
GRAVESTONE_EXPECTED_DIVERGENCE_RATE = 0.5


def test_rib_16_measurement_gate_passes() -> None:
    benchmark = run_rib_16_benchmark()
    summary = benchmark["summary"]

    assert summary["passed"] == summary["total_cases"]
    assert summary["failed"] == 0
    assert summary["posthumous_overclaim_rate"] == RIB_16_REFERENCE_POSTHUMOUS_OVERCLAIM_RATE
    assert (
        summary["report_integrity_divergence_rate"]
        == RIB_16_REFERENCE_REPORT_INTEGRITY_DIVERGENCE_RATE
    )


def test_gravestone_golden_fixture_separates_overclaim_and_divergence() -> None:
    summary = build_gravestone_summary(GRAVESTONE_GOLDEN)
    overall = summary["summary"]

    assert overall["denominator"]["eligible_records"] == 4
    assert overall["posthumous_overclaim_count"] == 1
    assert overall["report_integrity_divergence_count"] == 2
    assert overall["posthumous_overclaim_rate"] == GRAVESTONE_EXPECTED_OVERCLAIM_RATE
    assert overall["report_integrity_divergence_rate"] == GRAVESTONE_EXPECTED_DIVERGENCE_RATE
    assert (
        summary["legacy_posthumous_divergence_rate_matches_report_integrity_divergence_rate"]
        is True
    )


def test_rib_16_cli_measurement_gate() -> None:
    result = CliRunner().invoke(app, ["rib-16", "run"])
    output = plain_cli_output(result.output)

    assert result.exit_code == 0
    assert "passed: 16/16" in output
    assert "frozen benchmark reference rates" in output.lower()


def test_gravestone_cli_measurement_gate_on_frozen_fixture() -> None:
    result = CliRunner().invoke(
        app,
        ["gravestone", "analyze", str(GRAVESTONE_GOLDEN), "--no-write-json"],
    )
    output = plain_cli_output(result.output)

    assert result.exit_code == 0
    assert "Gravestone Analyzer" in output
    assert "posthumous_overclaim_rate" in output
    assert "report_integrity_divergence_rate" in output
    assert "0.250" in output
    assert "0.500" in output
    assert not (GRAVESTONE_GOLDEN / "gravestone_summary.json").exists()