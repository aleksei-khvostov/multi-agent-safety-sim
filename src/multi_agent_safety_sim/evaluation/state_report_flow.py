"""Evaluation flow for State-Report Divergence golden cases.

This module provides a minimal benchmark loop over the golden set before a full
Planner -> Worker -> Watchdog environment exists.

The flow is intentionally simple:

load -> evaluate -> summarize

The summarizer only aggregates evaluator outputs. It does not recompute
divergence labels. Divergence classification is performed in the deterministic
evaluator and checked against the independent golden labels.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from multi_agent_safety_sim.evaluation.state_report_divergence import (
    StateReportEvaluation,
    evaluate_state_report_case,
)

GOLDEN_PATH = Path("data/eval_sets/state_report_divergence_golden.jsonl")

HONEST_LABELS = {
    "aligned",
    "aligned_partial",
    "aligned_blocked",
    "honest_ambiguity",
}

DIVERGENCE_LABELS = {
    "overclaim_divergence",
    "severe_divergence",
    "severe_overclaim_divergence",
}


@dataclass(frozen=True)
class EvaluationSummary:
    """Aggregate summary for a State-Report Divergence benchmark run."""

    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float
    label_counts: dict[str, int]
    divergence_cases: int
    honest_cases: int
    honest_ambiguity_cases: int
    detection_rate: float
    false_positive_rate: float
    failed_by_label: dict[str, int]
    failed_case_ids: list[str]


def load_state_report_cases(path: Path = GOLDEN_PATH) -> list[dict[str, Any]]:
    """Load State-Report Divergence golden cases from JSONL."""
    if not path.exists():
        raise FileNotFoundError(f"Golden set not found at {path}")

    cases: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped:
                raise ValueError(f"Empty line in golden dataset at line {line_number}")

            try:
                record = json.loads(stripped)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Line {line_number} is not valid JSON: {error}"
                ) from error

            if not isinstance(record, dict):
                raise ValueError(
                    f"Line {line_number} in golden dataset is not a JSON object"
                )

            cases.append(record)

    return cases


def evaluate_state_report_cases(
    cases: list[dict[str, Any]],
) -> list[StateReportEvaluation]:
    """Evaluate State-Report Divergence cases with deterministic evaluators."""
    return [evaluate_state_report_case(case) for case in cases]


def summarize_state_report_evaluations(
    evaluations: list[StateReportEvaluation],
) -> EvaluationSummary:
    """Summarize State-Report Divergence evaluation results."""
    total_cases = len(evaluations)
    passed_cases = sum(1 for evaluation in evaluations if evaluation.passed)
    failed_cases = total_cases - passed_cases

    label_counts = dict(Counter(evaluation.predicted_label for evaluation in evaluations))

    divergence_evaluations = [
        evaluation
        for evaluation in evaluations
        if evaluation.predicted_label in DIVERGENCE_LABELS
    ]
    honest_evaluations = [
        evaluation
        for evaluation in evaluations
        if evaluation.predicted_label in HONEST_LABELS
    ]

    detected_divergence = sum(
        1 for evaluation in divergence_evaluations if evaluation.predicted_divergence
    )
    detection_rate = (
        detected_divergence / len(divergence_evaluations)
        if divergence_evaluations
        else 0.0
    )

    false_positives = sum(
        1 for evaluation in honest_evaluations if evaluation.predicted_divergence
    )
    false_positive_rate = (
        false_positives / len(honest_evaluations) if honest_evaluations else 0.0
    )

    failed_evaluations = [
        evaluation for evaluation in evaluations if not evaluation.passed
    ]

    return EvaluationSummary(
        total_cases=total_cases,
        passed_cases=passed_cases,
        failed_cases=failed_cases,
        pass_rate=passed_cases / total_cases if total_cases else 0.0,
        label_counts=label_counts,
        divergence_cases=len(divergence_evaluations),
        honest_cases=len(honest_evaluations),
        honest_ambiguity_cases=sum(
            1
            for evaluation in evaluations
            if evaluation.predicted_label == "honest_ambiguity"
        ),
        detection_rate=detection_rate,
        false_positive_rate=false_positive_rate,
        failed_by_label=dict(
            Counter(evaluation.predicted_label for evaluation in failed_evaluations)
        ),
        failed_case_ids=[evaluation.case_id for evaluation in failed_evaluations],
    )


def format_evaluation_summary(summary: EvaluationSummary) -> str:
    """Format a State-Report Divergence benchmark summary for CLI output."""
    lines = [
        "State-Report Divergence benchmark",
        f"total_cases: {summary.total_cases}",
        f"passed_cases: {summary.passed_cases}",
        f"failed_cases: {summary.failed_cases}",
        f"pass_rate: {summary.pass_rate:.3f}",
        f"detection_rate: {summary.detection_rate:.3f}",
        f"false_positive_rate: {summary.false_positive_rate:.3f}",
        f"honest_ambiguity_cases: {summary.honest_ambiguity_cases}",
        f"failed_case_ids: {summary.failed_case_ids}",
        f"failed_by_label: {summary.failed_by_label}",
        f"label_counts: {summary.label_counts}",
    ]
    return "\n".join(lines)


def run_state_report_benchmark(path: Path = GOLDEN_PATH) -> EvaluationSummary:
    """Run load -> evaluate -> summarize for the State-Report golden set."""
    cases = load_state_report_cases(path)
    evaluations = evaluate_state_report_cases(cases)
    return summarize_state_report_evaluations(evaluations)

def main() -> None:
    """Run the State-Report Divergence benchmark and print a summary."""
    summary = run_state_report_benchmark()
    print(format_evaluation_summary(summary))


if __name__ == "__main__":
    main()
