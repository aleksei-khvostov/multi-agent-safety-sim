"""Tests for the deterministic State-Report delegation scenario."""

from __future__ import annotations

from multi_agent_safety_sim.evaluation.state_report_divergence import (
    evaluate_state_report_case,
)
from multi_agent_safety_sim.scenarios.state_report_delegation import (
    State,
    build_baseline_cases,
    case_to_state_report_eval_case,
    run_scenario,
)


def divergence(case: object) -> bool:
    """Compare reported state against environment-owned actual state."""
    return case.report.reported_state != case.execution.actual_state


def test_planner_cannot_read_actual_state() -> None:
    """Same handoff signal with different actual states yields the same report."""
    partial_lossy = run_scenario("x", "partial_lossy")
    complete = run_scenario("y", "complete")

    assert partial_lossy.execution.handoff_signal == complete.execution.handoff_signal
    assert partial_lossy.execution.actual_state != complete.execution.actual_state
    assert partial_lossy.report.reported_state == complete.report.reported_state


def test_aligned_case_has_no_divergence() -> None:
    case = run_scenario("a", "complete")

    assert case.execution.actual_state == State.COMPLETED
    assert case.report.reported_state == State.COMPLETED
    assert not divergence(case)


def test_overclaim_case_diverges_from_lossy_partial_handoff() -> None:
    case = run_scenario("b", "partial_lossy")

    assert case.execution.actual_state == State.PARTIAL
    assert case.execution.handoff_signal == "done"
    assert case.report.reported_state == State.COMPLETED
    assert divergence(case)


def test_blocked_honest_case_has_no_divergence() -> None:
    case = run_scenario("c", "blocked_honest")

    assert case.execution.actual_state == State.BLOCKED
    assert case.execution.handoff_signal == "blocked"
    assert case.report.reported_state == State.BLOCKED
    assert not divergence(case)


def test_blocked_lossy_case_creates_severe_divergence() -> None:
    case = run_scenario("d", "blocked_lossy")

    assert case.execution.actual_state == State.BLOCKED
    assert case.execution.handoff_signal == "done"
    assert case.report.reported_state == State.COMPLETED
    assert divergence(case)


def test_baseline_has_expected_divergence_mix() -> None:
    cases = build_baseline_cases()

    assert len(cases) == 4
    assert [case.case_id for case in cases] == [
        "aligned_001",
        "overclaim_001",
        "aligned_blocked_001",
        "severe_001",
    ]
    assert sum(1 for case in cases if divergence(case)) == 2


def test_generated_cases_can_feed_state_report_evaluator() -> None:
    generated = [
        (
            run_scenario("aligned_001", "complete"),
            "aligned",
            False,
        ),
        (
            run_scenario("overclaim_001", "partial_lossy"),
            "overclaim_divergence",
            True,
        ),
        (
            run_scenario("aligned_blocked_001", "blocked_honest"),
            "aligned_blocked",
            False,
        ),
        (
            run_scenario("severe_001", "blocked_lossy"),
            "severe_divergence",
            True,
        ),
    ]

    for case, expected_label, expected_divergence in generated:
        eval_case = case_to_state_report_eval_case(
            case,
            expected_label=expected_label,
            expected_divergence=expected_divergence,
        )
        evaluation = evaluate_state_report_case(eval_case)

        assert evaluation.predicted_label == expected_label
        assert evaluation.predicted_divergence is expected_divergence
        assert evaluation.passed
