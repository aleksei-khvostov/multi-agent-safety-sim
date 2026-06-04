"""Validation tests for the planner_delegation golden safety dataset."""

from __future__ import annotations

import json
from pathlib import Path

DATASET_PATH = Path("data/eval_sets/planner_delegation_golden.jsonl")

REQUIRED_FIELDS = {
    "case_id",
    "category",
    "original_intent",
    "task_payload",
    "injected_delegation",
    "expected_planner_behavior",
    "expected_executor_behavior",
    "expected_watchdog_behavior",
    "expected_final_status",
    "expected_safety_events",
    "expected_audit_complete",
    "expected_failure_mode",
}

ALLOWED_FINAL_STATUSES = {"executed", "escalated", "reviewed"}
ALLOWED_FAILURE_MODES = {
    None,
    "scenario_design_gap",
    "unsafe_delegation",
    "tool_misuse",
    "fabrication_risk",
    "task_drift",
    "watchdog_false_positive_if_alerted",
    "provenance_loss",
}


def load_cases() -> list[dict[str, object]]:
    """Load JSONL golden cases."""
    rows: list[dict[str, object]] = []

    for line_number, line in enumerate(
        DATASET_PATH.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        assert line.strip(), f"empty line at {line_number}"
        rows.append(json.loads(line))

    return rows


def test_planner_delegation_golden_dataset_exists() -> None:
    assert DATASET_PATH.exists()


def test_planner_delegation_golden_dataset_has_expected_size() -> None:
    cases = load_cases()

    assert len(cases) == 8


def test_planner_delegation_golden_dataset_required_fields() -> None:
    cases = load_cases()

    for case in cases:
        assert set(case) == REQUIRED_FIELDS


def test_planner_delegation_golden_dataset_case_ids_are_unique() -> None:
    cases = load_cases()
    case_ids = [case["case_id"] for case in cases]

    assert len(case_ids) == len(set(case_ids))


def test_planner_delegation_golden_dataset_expected_values_are_valid() -> None:
    cases = load_cases()

    for case in cases:
        assert isinstance(case["case_id"], str)
        assert isinstance(case["category"], str)
        assert isinstance(case["original_intent"], str)
        assert isinstance(case["task_payload"], str)
        assert isinstance(case["expected_planner_behavior"], str)
        assert isinstance(case["expected_executor_behavior"], str)
        assert isinstance(case["expected_watchdog_behavior"], str)
        assert case["expected_final_status"] in ALLOWED_FINAL_STATUSES
        assert isinstance(case["expected_safety_events"], int)
        assert case["expected_safety_events"] >= 0
        assert isinstance(case["expected_audit_complete"], bool)
        assert case["expected_failure_mode"] in ALLOWED_FAILURE_MODES


def test_planner_delegation_golden_dataset_covers_key_failure_modes() -> None:
    cases = load_cases()
    categories = {case["category"] for case in cases}

    assert "benign_pii_redaction" in categories
    assert "missing_task_payload" in categories
    assert "adversarial_pii_exposure" in categories
    assert "unauthorized_external_tool_request" in categories
    assert "executor_fabricates_missing_data" in categories
    assert "planner_executor_mismatch" in categories
    assert "watchdog_false_positive_benign" in categories
    assert "incomplete_provenance" in categories
