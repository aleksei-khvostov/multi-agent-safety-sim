from src.task_episode import TaskState


class RuleBasedPlanner:
    """
    Planner interprets worker output and produces a reported state.

    Important:
    The planner does not receive actual_state.
    It only sees worker_output.
    """

    def report(self, worker_output: str) -> tuple[str, TaskState]:
        reported_state = self.infer_state(worker_output)

        return self._make_report(reported_state), reported_state

    def infer_state(self, worker_output: str) -> TaskState:
        text = worker_output.lower()

        success = any(x in text for x in [
            "success",
            "successfully",
            "completed",
            "processed",
            "updated",
        ])

        failure = any(x in text for x in [
            "failed",
            "error",
            "not found",
            "missing",
        ])

        blocked = any(x in text for x in [
            "blocked",
            "denied",
            "policy",
            "rejected",
        ])

        timeout = any(x in text for x in [
            "timeout",
            "timed out",
            "execution limit",
            "exceeded",
        ])

        partial = any(x in text for x in [
            "some",
            "partial",
            "partially",
            "only",
            "2 of",
            "3 of",
            "not all",
        ])

        signals = sum([success, failure, blocked, timeout, partial])

        if signals > 1:
            return TaskState.AMBIGUOUS

        if partial:
            return TaskState.PARTIAL_SUCCESS

        if timeout:
            return TaskState.TIMEOUT

        if blocked:
            return TaskState.BLOCKED

        if failure:
            return TaskState.FAILURE

        if success:
            return TaskState.SUCCESS

        return TaskState.UNKNOWN

    def _make_report(self, reported_state: TaskState) -> str:
        if reported_state == TaskState.SUCCESS:
            return "The task completed successfully."

        if reported_state == TaskState.FAILURE:
            return "The task failed."

        if reported_state == TaskState.PARTIAL_SUCCESS:
            return "The task was partially completed."

        if reported_state == TaskState.BLOCKED:
            return "The task was blocked."

        if reported_state == TaskState.TIMEOUT:
            return "The task timed out."

        if reported_state == TaskState.AMBIGUOUS:
            return "The task result is ambiguous."

        return "The task state is unknown."
