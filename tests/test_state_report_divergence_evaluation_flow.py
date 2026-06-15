"""Tests for the State-Report Divergence evaluation flow."""

from __future__ import annotations

from pathlib import Path

import pytest

from multi_agent_safety_sim.evaluation.state_report_flow import (
    EvaluationSummary,
    evaluate_state_report_cases,
    format_evaluation_summary,
    load_state_report_cases,
    main,
    run_state_report_benchmark,
    summarize_state_report_evaluations,
)

DATASET_PATH = Path("data/eval_sets/state_report_divergence_golden.jsonl")


def test_load_state_report_cases_returns_nonempty_dataset() -> None:
    cases = load_state_report_cases(DATASET_PATH)

    assert len(cases) == 11


def test_load_state_report_cases_rejects_empty_lines(tmp_path: Path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text('{"case_id": "ok"}\n\n', encoding="utf-8")

    with pytest.raises(ValueError, match="Empty line"):
        load_state_report_cases(path)


def test_evaluate_state_report_cases_covers_all_cases() -> None:
    cases = load_state_report_cases(DATASET_PATH)
    evaluations = evaluate_state_report_cases(cases)

    assert len(evaluations) == len(cases)
    assert all(evaluation.case_id for evaluation in evaluations)


def test_run_state_report_benchmark_returns_summary_type() -> None:
    summary = run_state_report_benchmark(DATASET_PATH)

    assert isinstance(summary, EvaluationSummary)


def test_summary_counts_are_consistent() -> None:
    summary = run_state_report_benchmark(DATASET_PATH)

    assert summary.total_cases == 11
    assert summary.total_cases == summary.passed_cases + summary.failed_cases
    assert 0.0 <= summary.pass_rate <= 1.0
    assert 0.0 <= summary.detection_rate <= 1.0
    assert 0.0 <= summary.false_positive_rate <= 1.0


def test_summary_keeps_detection_and_false_positive_axes_separate() -> None:
    summary = run_state_report_benchmark(DATASET_PATH)

    assert hasattr(summary, "detection_rate")
    assert hasattr(summary, "false_positive_rate")
    assert summary.detection_rate == 1.0
    assert summary.false_positive_rate == 0.0


def test_summary_reports_label_counts() -> None:
    summary = run_state_report_benchmark(DATASET_PATH)

    assert summary.label_counts["honest_ambiguity"] == 4
    assert summary.label_counts["overclaim_divergence"] == 2
    assert summary.label_counts["severe_divergence"] == 1
    assert summary.label_counts["severe_overclaim_divergence"] == 1


def test_summary_reports_honest_and_divergence_case_counts() -> None:
    summary = run_state_report_benchmark(DATASET_PATH)

    assert summary.honest_cases == 7
    assert summary.honest_ambiguity_cases == 4
    assert summary.divergence_cases == 4


def test_summary_reports_no_failures_for_current_golden_set() -> None:
    summary = run_state_report_benchmark(DATASET_PATH)

    assert summary.failed_cases == 0
    assert summary.failed_by_label == {}
    assert summary.failed_case_ids == []


def test_summarize_state_report_evaluations_reports_failed_breakdown() -> None:
    cases = load_state_report_cases(DATASET_PATH)
    evaluations = evaluate_state_report_cases(cases)

    broken_evaluation = evaluations[0]
    failed_version = type(broken_evaluation)(
        case_id=broken_evaluation.case_id,
        predicted_label=broken_evaluation.predicted_label,
        predicted_divergence=broken_evaluation.predicted_divergence,
        passed=False,
        checks=broken_evaluation.checks,
    )
    modified = [failed_version, *evaluations[1:]]

    summary = summarize_state_report_evaluations(modified)

    assert summary.failed_cases == 1
    assert summary.failed_by_label == {broken_evaluation.predicted_label: 1}
    assert summary.failed_case_ids == [broken_evaluation.case_id]

def test_format_evaluation_summary_includes_core_metrics() -> None:
    summary = run_state_report_benchmark(DATASET_PATH)
    output = format_evaluation_summary(summary)

    assert "State-Report Divergence benchmark" in output
    assert "total_cases: 11" in output
    assert "passed_cases: 11" in output
    assert "pass_rate: 1.000" in output
    assert "detection_rate: 1.000" in output
    assert "false_positive_rate: 0.000" in output
    assert "honest_ambiguity_cases: 4" in output


def test_main_prints_benchmark_summary(capsys: object) -> None:
    main()
    captured = capsys.readouterr()

    assert "State-Report Divergence benchmark" in captured.out
    assert "total_cases: 11" in captured.out
    assert "failed_case_ids: []" in captured.out
