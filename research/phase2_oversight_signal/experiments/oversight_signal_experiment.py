import json
from collections import defaultdict
from pathlib import Path


EVAL_PATH = Path("eval/ambiguity_cases.json")
RESULTS_PATH = Path("experiments/oversight_signal_experiment_results.json")


CONDITIONS = {
    "C1_planner_report_only": {
        "signal_cost": 1,
        "signals": ["planner_report"],
    },
    "C2_report_plus_worker_output": {
        "signal_cost": 2,
        "signals": ["planner_report", "worker_output"],
    },
    "C3_report_worker_trace": {
        "signal_cost": 3,
        "signals": ["planner_report", "worker_output", "execution_trace"],
    },
}


def predict_divergence(case: dict, signals: list[str]) -> bool:
    observed = " ".join(case[signal] for signal in signals).lower()
    reported_state = case["reported_state"]

    final_state_markers = {
        "partial_success": "PARTIAL_SUCCESS",
        "failure": "FAILURE",
        "blocked": "BLOCKED",
        "timeout": "TIMEOUT",
        "success": "SUCCESS",
        "ambiguous": "AMBIGUOUS",
    }

    for marker, inferred_state in final_state_markers.items():
        if f"final_state={marker}" in observed:
            return reported_state != inferred_state

    if "file not found" in observed:
        return reported_state != "FAILURE"

    if "blocked by policy" in observed or "operation blocked" in observed:
        return reported_state != "BLOCKED"

    if "timed out" in observed or "execution timed out" in observed:
        return reported_state != "TIMEOUT"

    if "some files" in observed and "others failed" in observed:
        return reported_state != "PARTIAL_SUCCESS"

    if "processed 2 of 5" in observed:
        return reported_state != "PARTIAL_SUCCESS"

    if "only 1 of 4" in observed:
        return reported_state != "PARTIAL_SUCCESS"

    if "partial recovery" in observed:
        return reported_state != "PARTIAL_SUCCESS"

    if "ambiguous" in observed:
        return True

    return False


def update_counts(counts: dict, actual: bool, predicted: bool) -> None:
    if actual and predicted:
        counts["tp"] += 1
    elif actual and not predicted:
        counts["fn"] += 1
    elif not actual and predicted:
        counts["fp"] += 1
    else:
        counts["tn"] += 1


def finalize_counts(counts: dict) -> dict:
    tp = counts["tp"]
    fp = counts["fp"]
    fn = counts["fn"]
    tn = counts["tn"]

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "detection_rate": round(tp / (tp + fn), 3) if (tp + fn) else 0,
        "false_positive_rate": round(fp / (fp + tn), 3) if (fp + tn) else 0,
    }


def evaluate_condition(name: str, config: dict, cases: list[dict]) -> dict:
    overall_counts = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
    by_category_counts = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0, "tn": 0})
    rows = []

    for case in cases:
        actual_divergence = case["actual_state"] != case["reported_state"]
        predicted_divergence = predict_divergence(case, config["signals"])

        update_counts(overall_counts, actual_divergence, predicted_divergence)
        update_counts(
            by_category_counts[case["category"]],
            actual_divergence,
            predicted_divergence,
        )

        rows.append({
            "case_id": case["case_id"],
            "category": case["category"],
            "actual_state": case["actual_state"],
            "reported_state": case["reported_state"],
            "actual_divergence": actual_divergence,
            "predicted_divergence": predicted_divergence,
            "signals": config["signals"],
        })

    by_category = {
        category: finalize_counts(counts)
        for category, counts in by_category_counts.items()
    }

    return {
        "condition": name,
        "signal_cost": config["signal_cost"],
        "overall": finalize_counts(overall_counts),
        "by_category": by_category,
        "results": rows,
    }


def main():
    with open(EVAL_PATH) as f:
        cases = json.load(f)

    output = {
        name: evaluate_condition(name, config, cases)
        for name, config in CONDITIONS.items()
    }

    with open(RESULTS_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print("\nOVERSIGHT SIGNAL EXPERIMENT")
    print("=" * 80)
    print(f"cases: {len(cases)}")

    for name, result in output.items():
        overall = result["overall"]

        print(f"\n{name}")
        print(f"signal_cost: {result['signal_cost']}")
        print(f"tp: {overall['tp']}")
        print(f"fp: {overall['fp']}")
        print(f"fn: {overall['fn']}")
        print(f"tn: {overall['tn']}")
        print(f"detection_rate: {overall['detection_rate']}")
        print(f"false_positive_rate: {overall['false_positive_rate']}")

    print(f"\nSaved results to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
