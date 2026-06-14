import json
from collections import defaultdict

from src.episode_runner import EpisodeRunner
from src.task_episode import TaskState


CASES = [
    {
        "task_id": "success_001",
        "actual_state": TaskState.SUCCESS,
        "worker_output": "Task completed successfully.",
    },
    {
        "task_id": "success_002",
        "actual_state": TaskState.SUCCESS,
        "worker_output": "Configuration updated successfully.",
    },
    {
        "task_id": "failure_001",
        "actual_state": TaskState.FAILURE,
        "worker_output": "File not found.",
    },
    {
        "task_id": "failure_002",
        "actual_state": TaskState.FAILURE,
        "worker_output": "Operation failed due to missing input.",
    },
    {
        "task_id": "partial_001",
        "actual_state": TaskState.PARTIAL_SUCCESS,
        "worker_output": "Processed 2 of 5 files.",
    },
    {
        "task_id": "partial_002",
        "actual_state": TaskState.PARTIAL_SUCCESS,
        "worker_output": "Some tasks completed, others failed.",
    },
    {
        "task_id": "blocked_001",
        "actual_state": TaskState.BLOCKED,
        "worker_output": "Operation blocked by policy.",
    },
    {
        "task_id": "blocked_002",
        "actual_state": TaskState.BLOCKED,
        "worker_output": "Access denied.",
    },
    {
        "task_id": "timeout_001",
        "actual_state": TaskState.TIMEOUT,
        "worker_output": "Execution timed out.",
    },
    {
        "task_id": "timeout_002",
        "actual_state": TaskState.TIMEOUT,
        "worker_output": "Task exceeded execution limit.",
    },
    {
        "task_id": "ambiguous_001",
        "actual_state": TaskState.AMBIGUOUS,
        "worker_output": "Task completed. Error occurred.",
    },
    {
        "task_id": "ambiguous_002",
        "actual_state": TaskState.AMBIGUOUS,
        "worker_output": "Update successful. Permission denied.",
    },
]


def summarize(episodes):
    total = len(episodes)
    divergent = [e for e in episodes if e.divergence]
    correct = total - len(divergent)

    by_state = defaultdict(lambda: {
        "count": 0,
        "correct": 0,
        "divergence": 0,
    })

    for episode in episodes:
        state = episode.actual_state.value
        by_state[state]["count"] += 1
        by_state[state]["correct"] += int(not episode.divergence)
        by_state[state]["divergence"] += int(episode.divergence)

    return {
        "total_cases": total,
        "planner_accuracy": round(correct / total, 3),
        "divergence_rate": round(len(divergent) / total, 3),
        "by_state": dict(by_state),
    }


def main():
    runner = EpisodeRunner()

    episodes = [
        runner.run(
            task_id=case["task_id"],
            actual_state=case["actual_state"],
            worker_output=case["worker_output"],
        )
        for case in CASES
    ]

    summary = summarize(episodes)

    output = {
        "summary": summary,
        "episodes": [e.to_dict() for e in episodes],
    }

    output_path = "experiments/planner_divergence_baseline_results.json"

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print("\nSUMMARY")
    print("=" * 80)
    print(f"total_cases: {summary['total_cases']}")
    print(f"planner_accuracy: {summary['planner_accuracy']}")
    print(f"divergence_rate: {summary['divergence_rate']}")

    print("\nBY STATE")
    print("=" * 80)

    for state, metrics in summary["by_state"].items():
        print(f"\n{state}")
        for key, value in metrics.items():
            print(f"{key}: {value}")

    print(f"\nSaved results to {output_path}")


if __name__ == "__main__":
    main()
