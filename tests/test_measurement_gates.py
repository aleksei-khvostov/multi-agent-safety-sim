"""Regression tests for deterministic report-integrity measurement gates."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from multi_agent_safety_sim.cli import app
from multi_agent_safety_sim.evaluation.fixture_locks import (
    NDB_20_FIXTURE_PATH,
    NDB_20_FIXTURE_SHA256,
    assert_fixture_sha256,
    sha256_file,
)
from multi_agent_safety_sim.evaluation.gravestone import build_gravestone_summary
from multi_agent_safety_sim.evaluation.nested_delegation_benchmark import (
    NDB_20_EXPECTED_CASE_COUNT,
    NDB_20_REFERENCE_CONSOLIDATION_OVERCLAIM_RATE,
    NDB_20_REFERENCE_CONSOLIDATION_UNDERCLAIM_RATE,
    NDB_20_REFERENCE_NESTED_REPORT_INTEGRITY_DIVERGENCE_RATE,
    load_ndb_20_cases,
    run_ndb_20_benchmark,
)
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


def test_ndb_20_fixture_exists_with_twenty_records() -> None:
    assert NDB_20_FIXTURE_PATH.exists()
    cases = load_ndb_20_cases(NDB_20_FIXTURE_PATH)
    assert len(cases) == NDB_20_EXPECTED_CASE_COUNT == 20


def test_ndb_20_fixture_sha_matches_lock() -> None:
    assert sha256_file(NDB_20_FIXTURE_PATH) == NDB_20_FIXTURE_SHA256
    assert_fixture_sha256(NDB_20_FIXTURE_PATH, NDB_20_FIXTURE_SHA256, fixture_name="NDB-20")


def test_ndb_20_measurement_gate_passes_primary_rates_only() -> None:
    benchmark = run_ndb_20_benchmark()
    summary = benchmark["summary"]

    assert summary["passed"] == summary["total_cases"] == 20
    assert summary["failed"] == 0
    assert (
        summary["nested_report_integrity_divergence_rate"]
        == NDB_20_REFERENCE_NESTED_REPORT_INTEGRITY_DIVERGENCE_RATE
    )
    assert summary["consolidation_overclaim_rate"] == NDB_20_REFERENCE_CONSOLIDATION_OVERCLAIM_RATE
    assert (
        summary["consolidation_underclaim_rate"]
        == NDB_20_REFERENCE_CONSOLIDATION_UNDERCLAIM_RATE
    )
    assert "diagnostics" in summary
    assert "watchdog_fp_on_nested_ambiguity" in summary["diagnostics"]
    assert "watchdog_fp_on_nested_ambiguity" not in summary


def test_ndb_20_watchdog_diagnostics_do_not_drive_gate_pass_fail() -> None:
    benchmark = run_ndb_20_benchmark()
    summary = benchmark["summary"]
    flagged = [result for result in benchmark["results"] if result.watchdog_actual_flag]

    assert summary["failed"] == 0
    assert summary["passed"] == 20
    assert flagged
    assert all(result.evaluation.passed for result in flagged)


def test_rib_16_cli_measurement_gate() -> None:
    result = CliRunner().invoke(app, ["rib-16", "run"])
    output = plain_cli_output(result.output)

    assert result.exit_code == 0
    assert "passed: 16/16" in output
    assert "frozen benchmark reference rates" in output.lower()


def test_ndb_20_cli_measurement_gate() -> None:
    result = CliRunner().invoke(app, ["nested-delegation", "run"])
    output = plain_cli_output(result.output)

    assert result.exit_code == 0
    assert "passed: 20/20" in output
    assert "nested_report_integrity_divergence_rate" in output
    assert "Diagnostics (secondary)" in output


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


def test_report_integrity_run_all_cli() -> None:
    result = CliRunner().invoke(app, ["report-integrity", "run-all"])
    output = plain_cli_output(result.output)

    assert result.exit_code == 0
    assert "rib_16" in output
    assert "gravestone_golden" in output
    assert "ndb_20" in output
    assert "pass" in output.lower()
    assert "All frozen report-integrity gates passed" in output