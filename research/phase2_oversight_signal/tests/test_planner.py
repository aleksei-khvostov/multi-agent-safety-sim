from src.planner import RuleBasedPlanner
from src.task_episode import TaskState


def test_planner_reports_success_from_worker_output():
    planner = RuleBasedPlanner()

    report, state = planner.report("Task completed successfully.")

    assert state == TaskState.SUCCESS
    assert report == "The task completed successfully."


def test_planner_reports_failure_from_worker_output():
    planner = RuleBasedPlanner()

    report, state = planner.report("File not found.")

    assert state == TaskState.FAILURE
    assert report == "The task failed."


def test_planner_reports_blocked_from_worker_output():
    planner = RuleBasedPlanner()

    report, state = planner.report("Operation blocked by policy.")

    assert state == TaskState.BLOCKED
    assert report == "The task was blocked."


def test_planner_reports_timeout_from_worker_output():
    planner = RuleBasedPlanner()

    report, state = planner.report("Execution timed out.")

    assert state == TaskState.TIMEOUT
    assert report == "The task timed out."


def test_planner_reports_ambiguous_for_mixed_status_output():
    planner = RuleBasedPlanner()

    report, state = planner.report(
        "Some files were processed successfully, but others failed."
    )

    assert state == TaskState.AMBIGUOUS
    assert report == "The task result is ambiguous."


def test_planner_does_not_use_actual_state():
    planner = RuleBasedPlanner()

    report, state = planner.report(
        "The task completed successfully."
    )

    assert state == TaskState.SUCCESS
    assert report == "The task completed successfully."
