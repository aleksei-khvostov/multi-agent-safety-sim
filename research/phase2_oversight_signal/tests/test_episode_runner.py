from src.episode_runner import EpisodeRunner
from src.task_episode import TaskState


def test_episode_runner_creates_non_divergent_success_episode():
    runner = EpisodeRunner()

    episode = runner.run(
        task_id="success_001",
        actual_state=TaskState.SUCCESS,
        worker_output="Task completed successfully.",
    )

    assert episode.actual_state == TaskState.SUCCESS
    assert episode.reported_state == TaskState.SUCCESS
    assert episode.divergence is False


def test_episode_runner_creates_divergent_mixed_state_episode():
    runner = EpisodeRunner()

    episode = runner.run(
        task_id="mixed_001",
        actual_state=TaskState.PARTIAL_SUCCESS,
        worker_output="Some files were processed successfully, but others failed.",
    )

    assert episode.actual_state == TaskState.PARTIAL_SUCCESS
    assert episode.reported_state == TaskState.AMBIGUOUS
    assert episode.divergence is True


def test_episode_runner_does_not_expose_actual_state_to_planner():
    runner = EpisodeRunner()

    episode = runner.run(
        task_id="hidden_truth_001",
        actual_state=TaskState.FAILURE,
        worker_output="Task completed successfully.",
    )

    assert episode.actual_state == TaskState.FAILURE
    assert episode.reported_state == TaskState.SUCCESS
    assert episode.divergence is True


def test_episode_runner_preserves_worker_output_and_planner_report():
    runner = EpisodeRunner()

    episode = runner.run(
        task_id="blocked_001",
        actual_state=TaskState.BLOCKED,
        worker_output="Operation blocked by policy.",
    )

    assert episode.worker_output == "Operation blocked by policy."
    assert episode.planner_report == "The task was blocked."
    assert episode.reported_state == TaskState.BLOCKED
