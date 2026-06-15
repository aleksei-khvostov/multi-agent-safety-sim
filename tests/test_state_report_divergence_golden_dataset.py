"""Integrity tests for the State-Report Divergence golden dataset.

These tests guard the dataset itself as an independent ground-truth contract.
They deliberately do not import watchdog or evaluator normalization logic.

The golden set defines actual_state, reported_state, and expected_label
independently. Later evaluators must be tested against this dataset, not share
logic with it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

GOLDEN_PATH = Path("data/eval_sets/state_report_divergence_golden.jsonl")

REQUIRED_FIELDS = {
    "case_id",
    "actual_state",
    "reported_state",
    "expected_label",
    "expected_divergence",
    "category",
    "trace",
    "note",
}

VALID_ACTUAL_STATES = {
    "completed",
    "partial",
    "blocked",
    "timeout",
    "not_started",
    "failed",
}

VALID_REPORTED_STATES = {
    "completed",
    "partial",
    "blocked",
    "uncertain",
    "failed",
}

VALID_LABELS = {
    "aligned",
    "aligned_partial",
    "aligned_blocked",
    "honest_ambiguity",
    "overclaim_divergence",
    "severe_divergence",
    "severe_overclaim_divergence",
}

DIVERGENCE_LABELS = {
    "overclaim_divergence",
    "severe_divergence",
    "severe_overclaim_divergence",
}

NON_DIVERGENCE_LABELS = {
    "aligned",
    "aligned_partial",
    "aligned_blocked",
    "honest_ambiguity",
}


def load_records() -> list[dict[str, Any]]:
    """Load the golden dataset with line-number-aware JSON errors."""
    assert GOLDEN_PATH.exists(), f"Golden set not found at {GOLDEN_PATH}"

    records: list[dict[str, Any]] = []
    with GOLDEN_PATH.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped:
                pytest.fail(f"Empty line at {line_number}")

            try:
                record = json.loads(stripped)
            except json.JSONDecodeError as error:
                pytest.fail(f"Line {line_number} is not valid JSON: {error}")

            assert isinstance(record, dict), f"Line {line_number} is not an object"
            records.append(record)

    return records


def test_dataset_exists_and_is_nonempty() -> None:
    records = load_records()

    assert len(records) >= 11


def test_required_fields_present() -> None:
    for record in load_records():
        missing = REQUIRED_FIELDS - record.keys()
        assert not missing, f"{record.get('case_id', '?')} missing {missing}"


def test_case_ids_are_unique() -> None:
    records = load_records()
    case_ids = [record["case_id"] for record in records]
    duplicates = {case_id for case_id in case_ids if case_ids.count(case_id) > 1}

    assert not duplicates, f"Duplicate case_id values: {duplicates}"


def test_states_labels_and_categories_are_valid() -> None:
    for record in load_records():
        case_id = record["case_id"]

        assert record["actual_state"] in VALID_ACTUAL_STATES, case_id
        assert record["reported_state"] in VALID_REPORTED_STATES, case_id
        assert record["expected_label"] in VALID_LABELS, case_id
        assert record["category"] in VALID_LABELS, case_id
        assert record["category"] == record["expected_label"], case_id
        assert isinstance(record["expected_divergence"], bool), case_id


def test_trace_fields_are_present_and_typed() -> None:
    for record in load_records():
        case_id = record["case_id"]
        trace = record["trace"]

        assert isinstance(trace, dict), case_id
        assert trace["final_state"] == record["actual_state"], case_id
        assert isinstance(trace["partial_progress"], bool), case_id
        assert isinstance(trace["recovery"], bool), case_id
        assert isinstance(trace["observability_level"], int), case_id
        assert 0 <= trace["observability_level"] <= 4, case_id


def test_expected_divergence_matches_expected_label() -> None:
    for record in load_records():
        case_id = record["case_id"]
        label = record["expected_label"]

        if label in DIVERGENCE_LABELS:
            assert record["expected_divergence"] is True, case_id
        elif label in NON_DIVERGENCE_LABELS:
            assert record["expected_divergence"] is False, case_id
        else:
            raise AssertionError(f"Unhandled label for {case_id}: {label}")


def test_honest_ambiguity_has_dedicated_coverage() -> None:
    records = load_records()
    honest_ambiguity_cases = [
        record for record in records if record["expected_label"] == "honest_ambiguity"
    ]

    assert len(honest_ambiguity_cases) >= 3


def test_honest_ambiguity_requires_recovery_or_partial_progress() -> None:
    for record in load_records():
        if record["expected_label"] != "honest_ambiguity":
            continue

        trace = record["trace"]
        assert record["reported_state"] == "uncertain", record["case_id"]
        assert trace["recovery"] or trace["partial_progress"], record["case_id"]


def test_overclaim_cases_report_completion_without_completed_truth() -> None:
    for record in load_records():
        if record["expected_label"] != "overclaim_divergence":
            continue

        assert record["reported_state"] == "completed", record["case_id"]
        assert record["actual_state"] != "completed", record["case_id"]


def test_dataset_covers_core_boundaries() -> None:
    labels = {record["expected_label"] for record in load_records()}

    assert "aligned" in labels
    assert "aligned_partial" in labels
    assert "aligned_blocked" in labels
    assert "honest_ambiguity" in labels
    assert "overclaim_divergence" in labels
    assert "severe_divergence" in labels
    assert "severe_overclaim_divergence" in labels
