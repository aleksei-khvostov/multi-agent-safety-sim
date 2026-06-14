from src.environment import Environment
from src.task_episode import TaskState


def test_environment_creates_episode_with_ground_truth():
    env = Environment()

    episode = env.create_episode(
        task_id="case_001",
        actual_state=TaskState.SUCCESS,
        worker_output="Task completed successfully.",
        planner_report="The task completed successfully.",
        reported_state=TaskState.SUCCESS,
    )

    assert episode.actual_state == TaskState.SUCCESS
    assert episode.reported_state == TaskState.SUCCESS
    assert episode.divergence is False


def test_environment_computes_divergence_independently():
    env = Environment()

    divergence = env.compute_divergence(
        actual_state=TaskState.FAILURE,
        reported_state=TaskState.SUCCESS,
    )

    assert divergence is True


def test_environment_represents_mixed_state_divergence():
    env = Environment()

    episode = env.create_episode(
        task_id="mixed_001",
        actual_state=TaskState.PARTIAL_SUCCESS,
        worker_output="Some files were processed, but others failed.",
        planner_report="The task completed successfully.",
        reported_state=TaskState.SUCCESS,
    )

    assert episode.actual_state == TaskState.PARTIAL_SUCCESS
    assert episode.reported_state == TaskState.SUCCESS
    assert episode.divergence is True
    assert env.compute_divergence(
        episode.actual_state,
        episode.reported_state,
    ) is True


def test_environment_does_not_use_watchdog_prediction_for_truth():
    env = Environment()

    episode = env.create_episode(
        task_id="case_002",
        actual_state=TaskState.BLOCKED,
        worker_output="Operation blocked by policy.",
        planner_report="The operation completed successfully.",
        reported_state=TaskState.SUCCESS,
    )

    episode.watchdog_prediction = False

    assert episode.divergence is True
