import json
import subprocess
import sys
from pathlib import Path


TRIALS = 5

COMMANDS = [
    {
        "name": "oversight_signal_experiment",
        "command": [sys.executable, "experiments/oversight_signal_experiment.py"],
        "results_path": Path("experiments/oversight_signal_experiment_results.json"),
    },
    {
        "name": "trace_without_final_state_experiment",
        "command": [sys.executable, "experiments/trace_without_final_state_experiment.py"],
        "results_path": Path("experiments/trace_without_final_state_results.json"),
    },
]


def load_overall_metrics(path: Path) -> dict:
    with open(path) as f:
        data = json.load(f)

    metrics = {}

    for condition, payload in data.items():
        overall = payload["overall"]
        metrics[condition] = {
            "detection_rate": overall["detection_rate"],
            "false_positive_rate": overall["false_positive_rate"],
            "tp": overall["tp"],
            "fp": overall["fp"],
            "fn": overall["fn"],
            "tn": overall["tn"],
        }

    return metrics


def summarize_trials(trials: list[dict]) -> dict:
    summary = {}

    conditions = trials[0].keys()

    for condition in conditions:
        summary[condition] = {}

        metric_names = trials[0][condition].keys()

        for metric in metric_names:
            values = [trial[condition][metric] for trial in trials]

            summary[condition][metric] = {
                "values": values,
                "min": min(values),
                "max": max(values),
                "mean": round(sum(values) / len(values), 3),
                "stable": len(set(values)) == 1,
            }

    return summary


def main():
    output = {}

    for item in COMMANDS:
        experiment_name = item["name"]
        command = item["command"]
        results_path = item["results_path"]

        trial_metrics = []

        for _ in range(TRIALS):
            subprocess.run(command, check=True, env={"PYTHONPATH": "."})
            trial_metrics.append(load_overall_metrics(results_path))

        output[experiment_name] = {
            "trials": TRIALS,
            "summary": summarize_trials(trial_metrics),
        }

    output_path = Path("experiments/repeated_signal_trials_results.json")

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print("\nREPEATED SIGNAL TRIALS")
    print("=" * 80)
    print(f"trials: {TRIALS}")

    for experiment_name, payload in output.items():
        print(f"\n{experiment_name}")
        print("-" * 80)

        for condition, metrics in payload["summary"].items():
            detection = metrics["detection_rate"]
            fpr = metrics["false_positive_rate"]

            print(f"\n{condition}")
            print(
                "detection_rate:",
                f"mean={detection['mean']}",
                f"min={detection['min']}",
                f"max={detection['max']}",
                f"stable={detection['stable']}",
            )
            print(
                "false_positive_rate:",
                f"mean={fpr['mean']}",
                f"min={fpr['min']}",
                f"max={fpr['max']}",
                f"stable={fpr['stable']}",
            )

    print(f"\nSaved results to {output_path}")


if __name__ == "__main__":
    main()
