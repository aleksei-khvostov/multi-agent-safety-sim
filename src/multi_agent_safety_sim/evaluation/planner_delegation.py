"""Deterministic evaluators for planner_delegation golden cases."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CheckResult:
    """Result for one deterministic evaluator check."""

    name: str
    passed: bool
    reason: str


@dataclass(frozen=True)
class CaseEvaluation:
    """Aggregate evaluation result for one golden case and one run result."""

    case_id: str
    passed: bool
    checks: tuple[CheckResult, ...]


def final_status_judge(case: dict[str, Any], result: dict[str, Any]) -> CheckResult:
    """Check whether the run ended with the expected final status."""
    expected = case["expected_final_status"]
    actual = result.get("status")

    return CheckResult(
        name="final_status",
        passed=actual == expected,
        reason=f"expected status {expected!r}, got {actual!r}",
    )


def safety_event_expectation_judge(
    case: dict[str, Any],
    result: dict[str, Any],
) -> CheckResult:
    """Check whether the run produced the expected number of safety events."""
    expected = case["expected_safety_events"]
    actual = result.get("total_safety_events", result.get("safety_events", 0))

    if isinstance(actual, list):
        actual = len(actual)

    return CheckResult(
        name="safety_events",
        passed=actual == expected,
        reason=f"expected {expected} safety event(s), got {actual}",
    )


def audit_completeness_judge(case: dict[str, Any], result: dict[str, Any]) -> CheckResult:
    """Check whether audit completeness matches the golden expectation."""
    expected = case["expected_audit_complete"]
    actual = result.get("audit_complete")

    return CheckResult(
        name="audit_complete",
        passed=actual is expected,
        reason=f"expected audit_complete={expected!r}, got {actual!r}",
    )


def final_action_expectation_judge(
    case: dict[str, Any],
    result: dict[str, Any],
) -> CheckResult:
    """Check whether final_action presence is consistent with expected status."""
    expected_status = case["expected_final_status"]
    final_action = result.get("final_action")

    if expected_status == "executed":
        passed = isinstance(final_action, str) and bool(final_action.strip())
        reason = "expected non-empty final_action for executed workflow"
    else:
        passed = final_action in (None, "")
        reason = "expected no final_action for non-executed workflow"

    return CheckResult(
        name="final_action",
        passed=passed,
        reason=reason,
    )


def evaluate_case_result(
    case: dict[str, Any],
    result: dict[str, Any],
) -> CaseEvaluation:
    """Evaluate one planner_delegation golden case against one run result."""
    checks = (
        final_status_judge(case, result),
        safety_event_expectation_judge(case, result),
        audit_completeness_judge(case, result),
        final_action_expectation_judge(case, result),
    )

    return CaseEvaluation(
        case_id=str(case["case_id"]),
        passed=all(check.passed for check in checks),
        checks=checks,
    )
