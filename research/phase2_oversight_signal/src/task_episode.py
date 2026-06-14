from dataclasses import dataclass
from enum import Enum


class TaskState(str, Enum):  # noqa: UP042
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    BLOCKED = "BLOCKED"
    TIMEOUT = "TIMEOUT"
    AMBIGUOUS = "AMBIGUOUS"
    UNKNOWN = "UNKNOWN"


@dataclass
class TaskEpisode:
    task_id: str
    actual_state: TaskState
    worker_output: str
    planner_report: str
    reported_state: TaskState
    watchdog_prediction: bool | None = None
    watchdog_confidence: float | None = None

    @property
    def divergence(self) -> bool:
        return self.actual_state != self.reported_state

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "actual_state": self.actual_state.value,
            "worker_output": self.worker_output,
            "planner_report": self.planner_report,
            "reported_state": self.reported_state.value,
            "watchdog_prediction": self.watchdog_prediction,
            "watchdog_confidence": self.watchdog_confidence,
            "divergence": self.divergence,
        }
