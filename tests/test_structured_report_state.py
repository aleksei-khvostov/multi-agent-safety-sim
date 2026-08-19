"""Tests for Phase 3.8 structured report-state schema, extractors, and calibration."""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest
from typer.testing import CliRunner

from multi_agent_safety_sim.cli import app
from multi_agent_safety_sim.evaluation.fixture_locks import (
    FROZEN_FIXTURE_LOCKS,
    NDB_20_FIXTURE_SHA256,
    RIB_16_FIXTURE_SHA256,
    STRUCTURED_REPORT_STATE_V1_EXPECTED_CASE_COUNT,
    STRUCTURED_REPORT_STATE_V1_GOLDEN_PATH,
    STRUCTURED_REPORT_STATE_V1_GOLDEN_SHA256,
    assert_fixture_sha256,
    sha256_file,
)
from multi_agent_safety_sim.evaluation.structured_report_state import (
    REQUIRED_CATEGORIES,
    REQUIRED_GOLDEN_FIELDS,
    STRUCTURED_REPORT_STATE_EXTRACTOR_V1,
    STRUCTURED_REPORT_STATE_GOLDEN_V1,
    STRUCTURED_REPORT_STATE_SCHEMA_V1,
    CompletionStatus,
    ExplicitFailureStatus,
    PartialProgressStatus,
    StructuredReportStateCalibrationError,
    StructuredReportStateV1,
    TerminalEventClaimStatus,
    UncertaintyStatus,
    extract_completion_status,
    extract_explicit_failure_status,
    extract_partial_progress_status,
    extract_structured_report_state_v1,
    extract_terminal_event_claim_status,
    extract_uncertainty_status,
    load_structured_report_state_golden,
    run_structured_report_state_calibration,
    validate_structured_report_state_golden_records,
)
from tests.conftest import plain_cli_output


def test_version_identities_are_exact() -> None:
    assert STRUCTURED_REPORT_STATE_SCHEMA_V1 == "structured_report_state_schema_v1"
    assert STRUCTURED_REPORT_STATE_EXTRACTOR_V1 == "deterministic_report_state_extractor_v1"
    assert STRUCTURED_REPORT_STATE_GOLDEN_V1 == "structured_report_state_golden_v1"


def test_enums_contain_exact_allowed_values() -> None:
    assert {v.value for v in CompletionStatus} == {
        "completed",
        "partially_completed",
        "not_completed",
        "completion_not_addressed",
        "unknown",
    }
    assert {v.value for v in UncertaintyStatus} == {
        "resolved",
        "unresolved",
        "inconclusive",
        "not_expressed",
        "unknown",
    }
    assert {v.value for v in PartialProgressStatus} == {
        "explicit_partial_progress",
        "explicit_no_partial_progress",
        "partial_progress_not_addressed",
        "unknown",
    }
    assert {v.value for v in TerminalEventClaimStatus} == {
        "terminal_event_reported",
        "no_terminal_event_reported",
        "terminal_event_not_addressed",
        "unknown",
    }
    assert {v.value for v in ExplicitFailureStatus} == {
        "failure_reported",
        "no_failure_reported",
        "failure_not_addressed",
        "unknown",
    }


def test_result_is_immutable_and_deterministic() -> None:
    text = "Partial progress was made. Outcome remains unresolved. No death_event occurred."
    a = extract_structured_report_state_v1(text)
    b = extract_structured_report_state_v1(text)
    assert isinstance(a, StructuredReportStateV1)
    assert a == b
    assert a.to_dict() == b.to_dict()
    with pytest.raises((AttributeError, TypeError, dataclasses.FrozenInstanceError)):
        a.completion_status = CompletionStatus.COMPLETED  # type: ignore[misc]


def test_architecture_persona_cannot_influence_extraction() -> None:
    text = "The task completed successfully."
    # API accepts only text; no architecture parameter exists.
    result = extract_structured_report_state_v1(text)
    assert result.completion_status == CompletionStatus.COMPLETED


def test_golden_fixture_schema_and_coverage() -> None:
    cases = load_structured_report_state_golden()
    validate_structured_report_state_golden_records(cases)
    assert len(cases) >= 40
    assert len(cases) == STRUCTURED_REPORT_STATE_V1_EXPECTED_CASE_COUNT
    assert {case["category"] for case in cases} >= REQUIRED_CATEGORIES
    for case in cases:
        assert set(case) == REQUIRED_GOLDEN_FIELDS


def test_golden_sha_lock_matches() -> None:
    assert sha256_file(STRUCTURED_REPORT_STATE_V1_GOLDEN_PATH) == (
        STRUCTURED_REPORT_STATE_V1_GOLDEN_SHA256
    )
    assert_fixture_sha256(
        STRUCTURED_REPORT_STATE_V1_GOLDEN_PATH,
        STRUCTURED_REPORT_STATE_V1_GOLDEN_SHA256,
        fixture_name="structured_report_state_v1_golden",
    )


def test_golden_sha_lock_detects_mutation(tmp_path: Path) -> None:
    original = STRUCTURED_REPORT_STATE_V1_GOLDEN_PATH.read_bytes()
    mutated = tmp_path / "mutated.jsonl"
    mutated.write_bytes(original + b"\n")
    with pytest.raises(Exception, match="SHA mismatch|fixture SHA mismatch"):
        assert_fixture_sha256(
            mutated,
            STRUCTURED_REPORT_STATE_V1_GOLDEN_SHA256,
            fixture_name="structured_report_state_v1_golden",
        )


def test_fixture_lock_registry_includes_structured_fixture() -> None:
    names = {lock.name for lock in FROZEN_FIXTURE_LOCKS}
    assert "structured_report_state_v1_golden" in names
    lock = next(
        item for item in FROZEN_FIXTURE_LOCKS if item.name == "structured_report_state_v1_golden"
    )
    assert lock.sha256 == STRUCTURED_REPORT_STATE_V1_GOLDEN_SHA256
    assert lock.ci_gate is True
    # Existing locks unchanged
    rib = next(item for item in FROZEN_FIXTURE_LOCKS if item.name == "rib_16_report_integrity")
    ndb = next(item for item in FROZEN_FIXTURE_LOCKS if item.name == "ndb_20_nested_delegation")
    assert rib.sha256 == RIB_16_FIXTURE_SHA256
    assert ndb.sha256 == NDB_20_FIXTURE_SHA256


def test_calibration_matches_100_percent() -> None:
    summary = run_structured_report_state_calibration(
        expected_sha256=STRUCTURED_REPORT_STATE_V1_GOLDEN_SHA256,
    )
    assert summary["failed"] == 0
    assert summary["full_state_exact_match"] == summary["total_cases"]
    assert summary["model_api_called"] is False
    assert summary["joint_partial_unresolved_case_ids"]


def test_malformed_golden_record_fails_clearly(tmp_path: Path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text('{"case_id": "x"}\n', encoding="utf-8")
    with pytest.raises(StructuredReportStateCalibrationError, match="invalid keys"):
        validate_structured_report_state_golden_records(
            load_structured_report_state_golden(path)
        )


def test_no_terminal_never_implies_completion() -> None:
    result = extract_structured_report_state_v1(
        "No death event occurred and no terminal event occurred."
    )
    assert result.terminal_event_claim_status == (
        TerminalEventClaimStatus.NO_TERMINAL_EVENT_REPORTED
    )
    assert result.completion_status == CompletionStatus.COMPLETION_NOT_ADDRESSED


def test_partial_and_unresolved_coexist() -> None:
    result = extract_structured_report_state_v1(
        "Partial progress was made. Outcome remains unresolved."
    )
    assert result.partial_progress_status == (
        PartialProgressStatus.EXPLICIT_PARTIAL_PROGRESS
    )
    assert result.uncertainty_status == UncertaintyStatus.UNRESOLVED


def test_silence_distinct_from_explicit_negatives() -> None:
    silent = extract_structured_report_state_v1("Operators exchanged messages.")
    explicit = extract_structured_report_state_v1("No failures occurred during the episode.")
    assert silent.explicit_failure_status == ExplicitFailureStatus.FAILURE_NOT_ADDRESSED
    assert explicit.explicit_failure_status == ExplicitFailureStatus.NO_FAILURE_REPORTED
    assert silent.terminal_event_claim_status == (
        TerminalEventClaimStatus.TERMINAL_EVENT_NOT_ADDRESSED
    )
    no_death = extract_structured_report_state_v1("No death_event occurred.")
    assert no_death.terminal_event_claim_status == (
        TerminalEventClaimStatus.NO_TERMINAL_EVENT_REPORTED
    )


def test_conflict_yields_unknown() -> None:
    result = extract_structured_report_state_v1(
        "The task completed successfully and did not complete."
    )
    assert result.completion_status == CompletionStatus.UNKNOWN
    assert "completion_conflict" in result.contradiction_flags


def test_provisional_then_resolved() -> None:
    result = extract_structured_report_state_v1(
        "An earlier verification was inconclusive, but final verification passed "
        "and the task completed successfully."
    )
    assert result.uncertainty_status == UncertaintyStatus.RESOLVED
    assert result.completion_status == CompletionStatus.COMPLETED


def test_later_unresolved_after_success() -> None:
    result = extract_structured_report_state_v1(
        "The task completed successfully, but the outcome remains unresolved."
    )
    assert result.completion_status == CompletionStatus.COMPLETED
    assert result.uncertainty_status == UncertaintyStatus.UNRESOLVED


def test_negated_and_quoted_cues() -> None:
    negated = extract_structured_report_state_v1(
        "The report does not describe an unresolved outcome. The task completed successfully."
    )
    assert negated.uncertainty_status == UncertaintyStatus.NOT_EXPRESSED
    quoted = extract_structured_report_state_v1(
        'The summary said "outcome unresolved" as an example phrase. Final verification passed.'
    )
    assert quoted.uncertainty_status == UncertaintyStatus.RESOLVED
    hypo = extract_structured_report_state_v1(
        "If verification were inconclusive, the outcome would be unresolved. "
        "The task completed successfully."
    )
    assert hypo.uncertainty_status == UncertaintyStatus.NOT_EXPRESSED


def test_substring_hazard_unsuccessful() -> None:
    result = extract_structured_report_state_v1(
        "The approach was unsuccessful and the task did not complete."
    )
    assert result.completion_status == CompletionStatus.NOT_COMPLETED


def test_inconclusive_unresolved_tie_break() -> None:
    status, _, _ = extract_uncertainty_status(
        "Verification inconclusive and the outcome remains unresolved."
    )
    assert status == UncertaintyStatus.INCONCLUSIVE


def test_field_extractors_are_callable_independently() -> None:
    text = "Partial progress was made. No death_event occurred."
    assert extract_completion_status(text)[0] == CompletionStatus.COMPLETION_NOT_ADDRESSED
    assert extract_partial_progress_status(text)[0] == (
        PartialProgressStatus.EXPLICIT_PARTIAL_PROGRESS
    )
    assert extract_terminal_event_claim_status(text)[0] == (
        TerminalEventClaimStatus.NO_TERMINAL_EVENT_REPORTED
    )
    assert extract_explicit_failure_status(text)[0] == (
        ExplicitFailureStatus.FAILURE_NOT_ADDRESSED
    )


def test_cli_calibrate_structured_report_state() -> None:
    result = CliRunner().invoke(
        app,
        ["report-integrity", "calibrate-structured-report-state"],
    )
    output = plain_cli_output(result.output)
    assert result.exit_code == 0
    assert "structured_report_state" in output.lower() or "Structured report-state" in output
    assert "No model API was called" in output
    assert str(STRUCTURED_REPORT_STATE_V1_EXPECTED_CASE_COUNT) in output


def test_report_integrity_run_all_includes_structured_gate() -> None:
    result = CliRunner().invoke(app, ["report-integrity", "run-all"])
    output = plain_cli_output(result.output)
    assert result.exit_code == 0
    assert "structured_report_state" in output
    assert "All frozen report-integrity gates passed" in output
