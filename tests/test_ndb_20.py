"""Tests for the NDB-20 nested delegation report-integrity benchmark."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from multi_agent_safety_sim.cli import app
from multi_agent_safety_sim.evaluation.nested_delegation_benchmark import (
    NDB_20_EXPECTED_CASE_COUNT,
    NDB_20_FAMILIES,
    NDB_20_PATH,
    NDB_20_REFERENCE_CONSOLIDATION_OVERCLAIM_RATE,
    NDB_20_REFERENCE_CONSOLIDATION_UNDERCLAIM_RATE,
    NDB_20_REFERENCE_NESTED_REPORT_INTEGRITY_DIVERGENCE_RATE,
    REFERENCE_RATES_NOTE,
    build_ndb_eval_case,
    consolidate_reported_state,
    evaluate_ndb_20_case,
    load_ndb_20_cases,
    rollup_nested_actual_state,
    run_ndb_20_benchmark,
)
from multi_agent_safety_sim.evaluation.state_report_divergence import DIVERGENCE_LABELS
from tests.conftest import plain_cli_output

DATASET_PATH = NDB_20_PATH


def test_ndb_20_schema_validation() -> None:
    cases = load_ndb_20_cases(DATASET_PATH)

    assert len(cases) == NDB_20_EXPECTED_CASE_COUNT
    case_ids = [case["case_id"] for case in cases]
    assert len(case_ids) == len(set(case_ids))

    for case in cases:
        assert case["family"] in NDB_20_FAMILIES
        assert case["watchdog"]["inputs"] == "consolidated_report_only"
        assert "architecture_id" not in case


def test_ndb_20_rollup_golden_matches_fixtures() -> None:
    for case in load_ndb_20_cases(DATASET_PATH):
        actual_state, trace = rollup_nested_actual_state(case["steps"])
        assert actual_state == case["rollup"]["actual_state"], case["case_id"]
        assert trace["partial_progress"] == case["rollup"]["trace"]["partial_progress"]
        assert trace["recovery"] == case["rollup"]["trace"]["recovery"]
        assert trace["final_state"] == case["rollup"]["trace"]["final_state"]


def test_ndb_20_ordering_independence() -> None:
    for case in load_ndb_20_cases(DATASET_PATH):
        steps = case["steps"]
        reversed_steps = list(reversed(steps))
        forward = rollup_nested_actual_state(steps)
        backward = rollup_nested_actual_state(reversed_steps)
        assert forward == backward, case["case_id"]


def test_ndb_20_scorer_golden_pass() -> None:
    benchmark = run_ndb_20_benchmark(DATASET_PATH)
    summary = benchmark["summary"]

    assert summary["passed"] == NDB_20_EXPECTED_CASE_COUNT
    assert summary["failed"] == 0
    assert summary["failed_case_ids"] == []

    for result in benchmark["results"]:
        assert result.evaluation.passed
        assert result.actual_label == result.expected_label
        assert result.actual_divergence == result.expected_divergence


def test_ndb_20_label_coverage() -> None:
    labels = {case["expected_label"] for case in load_ndb_20_cases(DATASET_PATH)}

    assert "overclaim_divergence" in labels
    assert "honest_ambiguity" in labels
    assert "aligned" in labels
    assert "underclaim_divergence" in labels
    assert "severe_divergence" in labels


def test_ndb_20_consolidation_isolation() -> None:
    case = load_ndb_20_cases(DATASET_PATH)[0]
    reported_before = consolidate_reported_state(case["consolidation"])

    mutated_steps = []
    for step in case["steps"]:
        mutated = dict(step)
        mutated["actual_state"] = "failed"
        mutated_steps.append(mutated)

    rollup_nested_actual_state(mutated_steps)
    reported_after = consolidate_reported_state(case["consolidation"])
    assert reported_before == reported_after


def test_ndb_20_primary_reference_rates() -> None:
    summary = run_ndb_20_benchmark(DATASET_PATH)["summary"]

    assert (
        summary["nested_report_integrity_divergence_rate"]
        == NDB_20_REFERENCE_NESTED_REPORT_INTEGRITY_DIVERGENCE_RATE
    )
    assert summary["consolidation_overclaim_rate"] == NDB_20_REFERENCE_CONSOLIDATION_OVERCLAIM_RATE
    assert (
        summary["consolidation_underclaim_rate"] == NDB_20_REFERENCE_CONSOLIDATION_UNDERCLAIM_RATE
    )
    assert summary["nested_report_integrity_divergence_count"] == 8
    assert summary["consolidation_overclaim_count"] == 4
    assert summary["consolidation_underclaim_count"] == 4


def test_ndb_20_family_targets() -> None:
    cases = load_ndb_20_cases(DATASET_PATH)

    overclaim = [case for case in cases if case["family"] == "consolidation_overclaim"]
    underclaim = [case for case in cases if case["family"] == "consolidation_underclaim"]
    honest = [case for case in cases if case["family"] == "consolidation_honest"]
    ambiguity = [case for case in cases if case["family"] == "nested_ambiguity"]
    stress = [case for case in cases if case["family"] == "watchdog_nested_stress"]

    assert len(overclaim) == len(underclaim) == len(honest) == len(ambiguity) == len(stress) == 4

    assert all(case["expected_divergence"] for case in overclaim + underclaim)
    assert all(not case["expected_divergence"] for case in honest + ambiguity + stress)

    assert all(case["expected_label"] in DIVERGENCE_LABELS for case in overclaim)
    assert all(case["expected_label"] == "underclaim_divergence" for case in underclaim)


def test_ndb_20_boundary_fields_remain_separate() -> None:
    for case in load_ndb_20_cases(DATASET_PATH):
        eval_case = build_ndb_eval_case(case)
        assert eval_case["actual_state"] != eval_case.get("reported_state") or (
            eval_case["actual_state"] == eval_case["reported_state"]
            and case["expected_label"].startswith("aligned")
        )
        assert "actual_state" in eval_case
        assert "reported_state" in eval_case


def test_ndb_20_diagnostics_present_without_headline_watchdog_rate() -> None:
    summary = run_ndb_20_benchmark(DATASET_PATH)["summary"]

    assert "diagnostics" in summary
    assert "watchdog_fp_on_nested_ambiguity" in summary["diagnostics"]
    assert "watchdog_fp_on_nested_ambiguity" not in summary


def test_ndb_20_cli_run_exits_zero_and_prints_primary_rates() -> None:
    result = CliRunner().invoke(app, ["nested-delegation", "run"])
    output = plain_cli_output(result.output)

    assert result.exit_code == 0
    assert "NDB-20" in output
    assert "passed: 20/20" in output
    assert REFERENCE_RATES_NOTE in output
    assert "nested_report_integrity_divergence_rate" in output
    assert "consolidation_overclaim_rate" in output
    assert "consolidation_underclaim_rate" in output
    assert "diagnostics" in output.lower()


def test_ndb_20_cli_json_output() -> None:
    result = CliRunner().invoke(app, ["nested-delegation", "run", "--json"])
    payload = json.loads(result.output)

    assert result.exit_code == 0
    assert payload["benchmark"] == "ndb_20"
    assert payload["nested_report_integrity_divergence_rate"] == 0.40
    assert payload["consolidation_overclaim_rate"] == 0.20
    assert payload["consolidation_underclaim_rate"] == 0.20
    assert "diagnostics" in payload


def test_ndb_20_missing_fixture_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.jsonl"

    with pytest.raises(FileNotFoundError, match="NDB-20 fixture file not found"):
        load_ndb_20_cases(missing)

    cli_result = CliRunner().invoke(app, ["nested-delegation", "run", "--path", str(missing)])
    output = plain_cli_output(cli_result.output)
    assert cli_result.exit_code == 2
    assert "NDB-20 fixture file not found" in output


def test_ndb_20_fixture_verification_helper() -> None:
    for case in load_ndb_20_cases(DATASET_PATH):
        result = evaluate_ndb_20_case(case)
        assert result.evaluation.passed, case["case_id"]
