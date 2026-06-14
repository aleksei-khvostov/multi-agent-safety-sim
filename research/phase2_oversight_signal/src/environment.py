from src.task_episode import TaskEpisode, TaskState


class Environment:
    """
    Environment owns ground truth.

    Planner and Watchdog may interpret state,
    but actual_state belongs only to the Environment.
    """

    def compute_divergence(
        self,
        actual_state: TaskState,
        reported_state: TaskState,
    ) -> bool:
        return actual_state != reported_state

    def create_episode(
        self,
        task_id: str,
        actual_state: TaskState,
        worker_output: str,
        planner_report: str,
        reported_state: TaskState,
    ) -> TaskEpisode:
        return TaskEpisode(
            task_id=task_id,
            actual_state=actual_state,
            worker_output=worker_output,
            planner_report=planner_report,
            reported_state=reported_state,
        )
