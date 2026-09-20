"""Conformance and invariant protection for the separate v1.1 calibration contract."""

from __future__ import annotations

import copy
import inspect
from pathlib import Path

import pytest
from typer.testing import CliRunner

from multi_agent_safety_sim.cli import app
from multi_agent_safety_sim.evaluation.fixture_locks import (
    FROZEN_FIXTURE_LOCKS,
    STRUCTURED_REPORT_STATE_V1_1_GOLDEN_PATH,
    STRUCTURED_REPORT_STATE_V1_1_GOLDEN_SHA256,
    STRUCTURED_REPORT_STATE_V1_GOLDEN_PATH,
    STRUCTURED_REPORT_STATE_V1_GOLDEN_SHA256,
    FixtureLockError,
    sha256_file,
)
from multi_agent_safety_sim.evaluation.structured_report_state import (
    StructuredReportStateCalibrationError,
    extract_structured_report_state_v1,
    load_structured_report_state_golden,
    run_structured_report_state_calibration,
)
from multi_agent_safety_sim.evaluation.structured_report_state_v1_1 import (
    CONFLICT_FLAGS,
    FIELDS,
    SILENCE,
    extract_structured_report_state_v1_1,
)
from multi_agent_safety_sim.evaluation.structured_report_state_v1_1_calibration import (
    run_structured_report_state_v1_1_calibration,
    validate_structured_report_state_v1_1_records,
)

CASES = load_structured_report_state_golden(STRUCTURED_REPORT_STATE_V1_1_GOLDEN_PATH)


def state(text: str) -> tuple[str, ...]:
    result = extract_structured_report_state_v1_1(text).to_dict()
    return tuple(result[f] for f in FIELDS)


@pytest.mark.parametrize("row", CASES, ids=[r["case_id"] for r in CASES])
def test_frozen_expected_full_state_and_conflict_flags(row: dict[str, str]) -> None:
    result = extract_structured_report_state_v1_1(row["report_text"])
    assert state(row["report_text"]) == tuple(row["expected_" + f] for f in FIELDS)
    assert result == extract_structured_report_state_v1_1(row["report_text"])
    assert result.schema_version == "structured_report_state_schema_v1_1"
    assert result.extractor_version == "deterministic_report_state_extractor_v1_1"
    actual = result.to_dict()
    assert {flag for flag in result.contradiction_flags if flag in CONFLICT_FLAGS} == {
        CONFLICT_FLAGS[i] for i, f in enumerate(FIELDS) if actual[f] == "unknown"
    }
    expected_cross = set()
    if actual[FIELDS[0]] == "completed":
        if actual[FIELDS[1]] in {"unresolved", "inconclusive"}:
            expected_cross.add("completed_with_unresolved")
        if actual[FIELDS[3]] == "terminal_event_reported":
            expected_cross.add("completed_with_terminal_event")
        if actual[FIELDS[4]] == "failure_reported":
            expected_cross.add("completed_with_explicit_failure")
    assert set(result.contradiction_flags) - set(CONFLICT_FLAGS) == expected_cross


def test_mandatory_gate_and_v1_historical_contract() -> None:
    summary = run_structured_report_state_v1_1_calibration()
    assert summary["full_state_exact_match"] == summary["total_cases"] == 267
    assert summary["calibration_identity"] == "structured_report_state_golden_v1_1"
    assert summary["model_api_called"] is False
    assert (
        sha256_file(STRUCTURED_REPORT_STATE_V1_1_GOLDEN_PATH)
        == STRUCTURED_REPORT_STATE_V1_1_GOLDEN_SHA256
    )
    assert (
        STRUCTURED_REPORT_STATE_V1_GOLDEN_SHA256
        == "42e8ba6fc1185abca50888336307143adccf72a75c169a4793c036725af496a7"
    )
    assert (
        sha256_file(STRUCTURED_REPORT_STATE_V1_GOLDEN_PATH)
        == STRUCTURED_REPORT_STATE_V1_GOLDEN_SHA256
    )
    old = run_structured_report_state_calibration(
        expected_sha256=STRUCTURED_REPORT_STATE_V1_GOLDEN_SHA256
    )
    assert old["full_state_exact_match"] == old["total_cases"] == 59
    assert old["schema_version"] == "structured_report_state_schema_v1"
    assert old["extractor_version"] == "deterministic_report_state_extractor_v1"
    assert old["calibration_identity"] == "structured_report_state_golden_v1"
    # Material semantic differences must remain version-local.
    assert (
        extract_structured_report_state_v1("The task was blocked.").explicit_failure_status
        == "failure_reported"
    )
    assert state("The task was blocked.")[4] == "failure_not_addressed"
    assert (
        extract_structured_report_state_v1(
            "Outcome unresolved; verification passed."
        ).uncertainty_status
        == "resolved"
    )
    assert state("Outcome unresolved; verification passed.")[1] == "unknown"
    names = {lock.name for lock in FROZEN_FIXTURE_LOCKS}
    assert {"structured_report_state_v1_golden", "structured_report_state_v1_1_golden"} <= names


def test_gate_rejects_byte_mutation(tmp_path: Path) -> None:
    path = tmp_path / "changed.jsonl"
    path.write_bytes(STRUCTURED_REPORT_STATE_V1_1_GOLDEN_PATH.read_bytes() + b"\n")
    with pytest.raises(FixtureLockError, match="SHA mismatch"):
        run_structured_report_state_v1_1_calibration(path)


@pytest.mark.parametrize(
    "mutation",
    [
        "extra",
        "missing",
        "enum",
        "schema",
        "source",
        "provenance",
        "duplicate",
        "type",
        "family",
        "contrast",
        "joint",
        "unknown",
    ],
)
def test_record_and_coverage_validation_rejects_drift(mutation: str) -> None:
    rows = copy.deepcopy(CASES)
    if mutation == "extra":
        rows[0]["new_provenance"] = "forbidden"
    elif mutation == "missing":
        rows[0].pop("rationale")
    elif mutation == "enum":
        rows[0]["expected_completion_status"] = "maybe"
    elif mutation == "schema":
        rows[0]["schema_version"] = "structured_report_state_schema_v1"
    elif mutation == "source":
        rows[0]["source_type"] = "audit_derived_normalized"
    elif mutation == "provenance":
        rows[0]["rationale"] = "no registered prefix"
    elif mutation == "duplicate":
        rows[1]["case_id"] = rows[0]["case_id"]
    elif mutation == "type":
        rows[0]["report_text"] = 12
    elif mutation == "family":
        for r in rows:
            if r["category"] == "blocked_context":
                r["category"] = "other"
    elif mutation == "contrast":
        next(r for r in rows if r["case_id"] == "transition_0_control")["case_id"] = "replacement"
    elif mutation == "joint":
        for r in rows:
            if r["expected_completion_status"] == "partially_completed":
                r["expected_explicit_failure_status"] = "failure_not_addressed"
    elif mutation == "unknown":
        for r in rows:
            if r["expected_explicit_failure_status"] == "unknown":
                r["expected_explicit_failure_status"] = "failure_not_addressed"
    with pytest.raises(StructuredReportStateCalibrationError):
        validate_structured_report_state_v1_1_records(rows)


@pytest.mark.parametrize(
    "parameter",
    [
        "architecture_id",
        "persona",
        "actual_outcome",
        "death_event",
        "risk_score",
        "environment_state",
    ],
)
def test_text_only_api_rejects_metadata(parameter: str) -> None:
    assert list(inspect.signature(extract_structured_report_state_v1_1).parameters) == ["text"]
    with pytest.raises(TypeError):
        extract_structured_report_state_v1_1("Task completed.", **{parameter: "anything"})


def test_field_independence_order_and_silence() -> None:
    text = "Partial progress occurred. Outcome unresolved."
    assert state(text) == state("Outcome unresolved. Partial progress occurred.")
    assert state(text)[1:3] == ("unresolved", "explicit_partial_progress")
    for phrase in ("No death_event occurred.", "Terminal event occurred."):
        result = state(phrase)
        assert result[0] == SILENCE[0]
        assert result[4] == SILENCE[4]
    assert state("Unsupported status: opaque.") == SILENCE
    explicit = state("Task did not complete. Not unresolved. No progress. No death. No failure.")
    assert all(a != b for a, b in zip(explicit, SILENCE, strict=True))
    for i in range(5):
        row = next(r for r in CASES if r["case_id"] == f"conflict_{i}_joint")
        assert state(row["report_text"])[i] == "unknown"


@pytest.mark.parametrize(
    "marker", ["finally", "ultimately", "after retry", "later", "was subsequently confirmed"]
)
def test_qualified_markers_across_fields(marker: str) -> None:
    pairs = [
        ("Task completed", "Task did not complete", 0, "not_completed"),
        ("Outcome unresolved", "Outcome resolved", 1, "resolved"),
        ("Partial progress occurred", "No progress occurred", 2, "explicit_no_partial_progress"),
        ("No terminal event occurred", "Terminal event occurred", 3, "terminal_event_reported"),
        ("Failure occurred", "No failure occurred", 4, "no_failure_reported"),
    ]
    for first, last, i, value in pairs:
        assert state(f"{first}; {marker}: {last}.")[i] == value
        assert state(f"{first}; however {last}.")[i] == "unknown"


def test_precise_overlap_and_identifier_boundaries() -> None:
    for phrase, i, value in [
        ("No failure occurred", 4, "no_failure_reported"),
        ("Failure-free", 4, "no_failure_reported"),
        ("No partial progress", 2, "explicit_no_partial_progress"),
        ("Not unresolved", 1, "resolved"),
    ]:
        result = extract_structured_report_state_v1_1(phrase)
        assert state(phrase)[i] == value
        assert not result.contradiction_flags
    for token in (
        "outcome_unresolved",
        "verification_inconclusive",
        "conflicting_observation",
        "death_event",
    ):
        assert state(f"prefix_{token}_suffix") == SILENCE
        assert state(f'"{token}"') == SILENCE


def test_cli_runs_both_gates_separately() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["report-integrity", "run-all"], terminal_width=160)
    assert result.exit_code == 0, result.output
    assert "structured_report_state_v1 " in result.output
    assert "structured_report_state_v1_1" in result.output
    assert "59/59" in result.output and "267/267" in result.output
    for command in ("calibrate-structured-report-state", "calibrate-structured-report-state-v1-1"):
        result = runner.invoke(app, ["report-integrity", command])
        assert result.exit_code == 0, result.output
        assert "No model API was called" in result.output
