from src.task_episode import TaskEpisode, TaskState


def test_episode_without_divergence():
    episode = TaskEpisode(
        task_id="case_001",
        actual_state=TaskState.SUCCESS,
        worker_output="Task completed successfully.",
        planner_report="The task completed successfully.",
        reported_state=TaskState.SUCCESS,
    )

    assert episode.divergence is False


def test_episode_with_divergence():
    episode = TaskEpisode(
        task_id="case_002",
        actual_state=TaskState.FAILURE,
        worker_output="File not found.",
        planner_report="The task completed successfully.",
        reported_state=TaskState.SUCCESS,
    )

    assert episode.divergence is True


def test_episode_to_dict_preserves_ground_truth():
    episode = TaskEpisode(
        task_id="case_003",
        actual_state=TaskState.BLOCKED,
        worker_output="Operation blocked by policy.",
        planner_report="The operation could not proceed.",
        reported_state=TaskState.FAILURE,
        watchdog_prediction=True,
        watchdog_confidence=0.9,
    )

    row = episode.to_dict()

    assert row["actual_state"] == "BLOCKED"
    assert row["reported_state"] == "FAILURE"
    assert row["divergence"] is True
    assert row["watchdog_prediction"] is True
    assert row["watchdog_confidence"] == 0.9
