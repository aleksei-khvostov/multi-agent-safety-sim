from src.environment import Environment
from src.planner import RuleBasedPlanner
from src.task_episode import TaskEpisode, TaskState


class EpisodeRunner:
    """
    Runs one Planner -> Environment episode.

    The runner wires components together but does not own ground truth.
    Ground truth remains owned by Environment.
    """

    def __init__(
        self,
        environment: Environment | None = None,
        planner: RuleBasedPlanner | None = None,
    ) -> None:
        self.environment = environment or Environment()
        self.planner = planner or RuleBasedPlanner()

    def run(
        self,
        task_id: str,
        actual_state: TaskState,
        worker_output: str,
    ) -> TaskEpisode:
        planner_report, reported_state = self.planner.report(worker_output)

        return self.environment.create_episode(
            task_id=task_id,
            actual_state=actual_state,
            worker_output=worker_output,
            planner_report=planner_report,
            reported_state=reported_state,
        )
