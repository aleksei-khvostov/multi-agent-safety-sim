from src.watchdog import RuleBasedWatchdog


def test_watchdog_accepts_clean_success():
    watchdog = RuleBasedWatchdog()

    result = watchdog.evaluate(
        "The task completed successfully."
    )

    assert result.divergence_detected is False


def test_watchdog_flags_ambiguous_report():
    watchdog = RuleBasedWatchdog()

    result = watchdog.evaluate(
        "The task result is ambiguous."
    )

    assert result.divergence_detected is True


def test_watchdog_flags_partial_report():
    watchdog = RuleBasedWatchdog()

    result = watchdog.evaluate(
        "The task was partially completed."
    )

    assert result.divergence_detected is True


def test_watchdog_accepts_honest_failure():
    watchdog = RuleBasedWatchdog()

    result = watchdog.evaluate(
        "The task failed."
    )

    assert result.divergence_detected is False


def test_watchdog_accepts_blocked_state():
    watchdog = RuleBasedWatchdog()

    result = watchdog.evaluate(
        "The task was blocked."
    )

    assert result.divergence_detected is False
