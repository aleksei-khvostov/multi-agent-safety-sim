"""Tests for the RIB-16 report integrity benchmark."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from multi_agent_safety_sim.cli import app
from multi_agent_safety_sim.evaluation.posthumous_divergence import (
    PosthumousDivergenceLabel,
    build_posthumous_record,
)
from multi_agent_safety_sim.evaluation.report_integrity_benchmark import (
    REFERENCE_RATES_NOTE,
    RIB_16_EXPECTED_CASE_COUNT,
    RIB_16_FAMILIES,
    RIB_16_PATH,
    RIB_16_REFERENCE_POSTHUMOUS_OVERCLAIM_RATE,
    RIB_16_REFERENCE_REPORT_INTEGRITY_DIVERGENCE_RATE,
    evaluate_rib_16_case,
    load_rib_16_cases,
    run_rib_16_benchmark,
)

DATASET_PATH = RIB_16_PATH
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _plain_cli_output(result_output: str) -> str:
    return " ".join(_ANSI_RE.sub("", result_output).split())


def test_rib_16_schema_validation() -> None:
    cases = load_rib_16_cases(DATASET_PATH)

    assert len(cases) == RIB_16_EXPECTED_CASE_COUNT
    case_ids = [case["case_id"] for case in cases]
    assert len(case_ids) == len(set(case_ids))

    for case in cases:
        assert case["family"] in RIB_16_FAMILIES
        assert "architecture_id" not in case


def test_rib_16_golden_pass() -> None:
    benchmark = run_rib_16_benchmark(DATASET_PATH)
    summary = benchmark["summary"]

    assert summary["passed"] == RIB_16_EXPECTED_CASE_COUNT
    assert summary["failed"] == 0
    assert summary["failed_case_ids"] == []

    for result in benchmark["results"]:
        assert result.passed
        assert result.actual_label == result.expected_label
        assert result.actual_divergence == result.expected_divergence


def test_rib_16_family_coverage() -> None:
    summary = run_rib_16_benchmark(DATASET_PATH)["summary"]

    assert summary["by_family"] == {
        "overclaim": 4,
        "honest": 4,
        "underclaim": 4,
        "ambiguous": 4,
    }


def test_rib_16_label_coverage() -> None:
    summary = run_rib_16_benchmark(DATASET_PATH)["summary"]
    labels = set(summary["label_counts"])

    assert labels == {
        PosthumousDivergenceLabel.ALIGNED_CLEAR.value,
        PosthumousDivergenceLabel.HONEST_FAILURE_REPORT.value,
        PosthumousDivergenceLabel.HONEST_AMBIGUITY.value,
        PosthumousDivergenceLabel.POSTHUMOUS_OVERCLAIM.value,
        PosthumousDivergenceLabel.FALSE_ALARM_OR_UNDERCLAIM.value,
    }


def test_rib_16_overclaim_is_not_the_same_as_divergence() -> None:
    cases = load_rib_16_cases(DATASET_PATH)
    underclaim_cases = [case for case in cases if case["family"] == "underclaim"]

    assert len(underclaim_cases) == 4
    assert all(case["expected_divergence"] for case in underclaim_cases)
    assert all(
        case["expected_label"] != PosthumousDivergenceLabel.POSTHUMOUS_OVERCLAIM.value
        for case in underclaim_cases
    )


def test_rib_16_architecture_blind_classification() -> None:
    case = load_rib_16_cases(DATASET_PATH)[0]
    honest = evaluate_rib_16_case(case, episode_id=1, architecture_id="honest_duo")
    deceptive = evaluate_rib_16_case(case, episode_id=1, architecture_id="deceptive_duo")

    assert honest.actual_label == deceptive.actual_label
    assert honest.actual_divergence == deceptive.actual_divergence
    assert honest.record.pds_score == deceptive.record.pds_score


def test_rib_16_frozen_reference_rates() -> None:
    summary = run_rib_16_benchmark(DATASET_PATH)["summary"]

    assert summary["posthumous_overclaim_rate"] == RIB_16_REFERENCE_POSTHUMOUS_OVERCLAIM_RATE
    assert (
        summary["report_integrity_divergence_rate"]
        == RIB_16_REFERENCE_REPORT_INTEGRITY_DIVERGENCE_RATE
    )
    assert summary["posthumous_overclaim_count"] == 4
    assert summary["report_integrity_divergence_count"] == 8


def test_rib_16_cli_run_exits_zero_and_prints_reference_rates() -> None:
    result = CliRunner().invoke(app, ["rib-16", "run"])
    output = _plain_cli_output(result.output)

    assert result.exit_code == 0
    assert "RIB-16" in output
    assert "passed: 16/16" in output
    assert REFERENCE_RATES_NOTE in output
    assert "frozen benchmark reference rates" in output.lower()
    assert "not empirical model findings" in output.lower()
    assert "frozen reference" in output.lower()


def test_rib_16_cli_json_output() -> None:
    result = CliRunner().invoke(app, ["rib-16", "run", "--json"])
    payload = json.loads(result.output)

    assert result.exit_code == 0
    assert payload["benchmark"] == "rib_16"
    assert payload["posthumous_overclaim_rate"] == 0.25
    assert payload["report_integrity_divergence_rate"] == 0.5
    assert payload["reference_rates"]["note"] == REFERENCE_RATES_NOTE


def test_rib_16_missing_fixture_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.jsonl"

    with pytest.raises(FileNotFoundError, match="RIB-16 fixture file not found"):
        load_rib_16_cases(missing)

    cli_result = CliRunner().invoke(app, ["rib-16", "run", "--path", str(missing)])
    output = _plain_cli_output(cli_result.output)
    assert cli_result.exit_code == 2
    assert "RIB-16 fixture file not found" in output


def test_rib_16_fixture_verification_helper() -> None:
    """Sanity check that fixtures still match build_posthumous_record()."""
    for index, case in enumerate(load_rib_16_cases(DATASET_PATH), start=1):
        record = build_posthumous_record(
            architecture_id="rib_fixture",
            episode_id=index,
            lifespan_rounds=case["lifespan_rounds"],
            death_event=case["death_event"],
            death_cause=case["death_cause"],
            risk_score=case["risk_score"],
            final_report=case["final_report"],
        )
        assert record.label.value == case["expected_label"], case["case_id"]
        assert record.divergence == case["expected_divergence"], case["case_id"]