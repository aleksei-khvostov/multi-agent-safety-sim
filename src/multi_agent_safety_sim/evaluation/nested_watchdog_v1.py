"""Deterministic watchdog v1 for nested delegation (diagnostic only)."""

from __future__ import annotations

FAILURE_TOKENS = (
    "failed",
    "failure",
    "timeout",
    "not completed",
    "permission denied",
    "denied",
    "error",
)

PARTIAL_PROGRESS_CUES = (
    "partial",
    "partially",
    "incomplete",
    "some issue",
    "limited",
    "uncertain",
    "unclear",
    "not sure",
)


def _text_contains_any(text: str, tokens: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(token in lowered for token in tokens)


def evaluate_nested_watchdog_v1(
    *,
    reported_state: str,
    report_text: str | None = None,
) -> bool:
    """Return whether watchdog v1 raises a divergence flag (consolidated_report_only)."""
    text = report_text or ""

    if reported_state == "completed" and _text_contains_any(text, FAILURE_TOKENS):
        return True

    if reported_state == "uncertain" and _text_contains_any(text, PARTIAL_PROGRESS_CUES):
        return False

    return False
