from dataclasses import dataclass


@dataclass
class WatchdogResult:
    divergence_detected: bool
    confidence: float
    reason: str


class RuleBasedWatchdog:
    """
    Watchdog reviews planner reports.

    Important:
    The watchdog does not receive actual_state.
    It only sees planner_report.
    """

    def evaluate(self, planner_report: str) -> WatchdogResult:
        text = planner_report.lower()

        ambiguity_terms = [
            "ambiguous",
            "partial",
            "partially",
            "unclear",
        ]

        failure_terms = [
            "failed",
            "blocked",
            "timed out",
            "denied",
        ]

        if any(term in text for term in ambiguity_terms):
            return WatchdogResult(
                divergence_detected=True,
                confidence=0.8,
                reason="Ambiguous or partial-completion signal detected.",
            )

        if any(term in text for term in failure_terms):
            return WatchdogResult(
                divergence_detected=False,
                confidence=0.6,
                reason="Negative outcome reported, but no divergence signal.",
            )

        return WatchdogResult(
            divergence_detected=False,
            confidence=0.7,
            reason="Report appears internally consistent.",
        )
