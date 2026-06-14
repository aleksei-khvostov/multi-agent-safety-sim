import json
import subprocess
import sys
from pathlib import Path

TRIALS = 5

EXPERIMENT = {
    "name": "trace_ablation_experiment",
    "command": [sys.executable, "experiments/trace_ablation_experiment.py"],
    "results_file": "experiments/trace_ablation_results.json",
}

OUTPUT_PATH = "experiments/repeated_ablation_trials_results.json"


def summarize(values):
    return {
        "mean": round(sum(values) / len(values), 3),
        "min": round(min(values), 3),
        "max": round(max(values), 3),
        "stable": len(set(values)) == 1,
    }


def main():
    collected = {}

    for _ in range(TRIALS):
        subprocess.run(
            EXPERIMENT["command"],
            check=True,
            env={"PYTHONPATH": "."},
        )

        with open(EXPERIMENT["results_file"]) as f:
            payload = json.load(f)

        for condition, result in payload["results"].items():
            overall = result["overall"]

            if condition not in collected:
                collected[condition] = {
                    "detection_drop": [],
                    "fpr_increase": [],
                }

            collected[condition]["detection_drop"].append(
                overall["detection_drop"]
            )

            collected[condition]["fpr_increase"].append(
                overall["fpr_increase"]
            )

    output = {}

    for condition, values in collected.items():
        output[condition] = {
            "detection_drop": summarize(
                values["detection_drop"]
            ),
            "fpr_increase": summarize(
                values["fpr_increase"]
            ),
        }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print("\nREPEATED ABLATION TRIALS")
    print("=" * 80)
    print(f"trials: {TRIALS}")

    for condition, metrics in output.items():
        print(f"\n{condition}")

        dd = metrics["detection_drop"]
        print(
            "detection_drop:",
            f"mean={dd['mean']}",
            f"min={dd['min']}",
            f"max={dd['max']}",
            f"stable={dd['stable']}",
        )

        fp = metrics["fpr_increase"]
        print(
            "fpr_increase:",
            f"mean={fp['mean']}",
            f"min={fp['min']}",
            f"max={fp['max']}",
            f"stable={fp['stable']}",
        )

    print(f"\nSaved results to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
