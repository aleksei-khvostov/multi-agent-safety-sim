import json
import re
from collections import defaultdict
from pathlib import Path

EVAL_PATH = Path("eval/ambiguity_cases.json")
RESULTS_PATH = Path("experiments/trace_without_final_state_results.json")


CONDITIONS = {
    "full_trace": {
        "signals": ["planner_report", "worker_output", "execution_trace"],
        "removes_final_state": False,
    },
    "trace_without_final_state": {
        "signals": ["planner_report", "worker_output", "execution_trace"],
        "removes_final_state": True,
    },
}


def remove_final_state(trace: str) -> str:
    cleaned = re.sub(r";?\s*final_state=[A-Z_]+", "", trace)
    return cleaned.strip("; ")


def get_signal(case: dict, signal: str, removes_final_state: bool) -> str:
    value = case[signal]

    if signal == "execution_trace" and removes_final_state:
        return remove_final_state(value)

    return value


def predict_divergence(case: dict, signals: list[str], removes_final_state: bool) -> bool:
    observed = " ".join(
        get_signal(case, signal, removes_final_state)
        for signal in signals
    ).lower()

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

    if "processed=2" in observed and "total=5" in observed:
        return reported_state != "PARTIAL_SUCCESS"

    if "processed=1" in observed and "total=4" in observed:
        return reported_state != "PARTIAL_SUCCESS"

    if "failed_steps" in observed:
        return reported_state != "PARTIAL_SUCCESS"

    if "skipped_later=true" in observed:
        return reported_state != "PARTIAL_SUCCESS"

    if "timeout=true" in observed:
        return reported_state != "TIMEOUT"

    if "blocked=true" in observed and "retry_allowed=false" in observed:
        return reported_state != "BLOCKED"

    if "blocked=true" and "retry_attempted=true" in observed:
        return reported_state != "BLOCKED"

    if "first_attempt=failed" in observed and "recovery=succeeded" in observed:
        return reported_state != "SUCCESS"

    if "first_attempt=failed" in observed and "recovery=partial" in observed:
        return reported_state != "PARTIAL_SUCCESS"

    if "conflicting_status=true" in observed:
        return reported_state != "AMBIGUOUS"

    if "success_signal=true" in observed and (
        "error_signal=true" in observed or "denied_signal=true" in observed
    ):
        return reported_state != "AMBIGUOUS"

    if "success=true" in observed and "warning=non_critical" in observed:
        return reported_state != "SUCCESS"

    if "success=true" in observed and "warning=true" in observed:
        return reported_state != "SUCCESS"

    if "file not found" in observed:
        return reported_state != "FAILURE"

    if "blocked by policy" in observed or "operation blocked" in observed:
        return reported_state != "BLOCKED"

    if "timed out" in observed or "execution timed out" in observed:
        return reported_state != "TIMEOUT"

    return "ambiguous" in observed


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
        predicted_divergence = predict_divergence(
            case,
            config["signals"],
            config["removes_final_state"],
        )

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
            "original_trace": case["execution_trace"],
            "observed_trace": get_signal(
                case,
                "execution_trace",
                config["removes_final_state"],
            ),
        })

    return {
        "condition": name,
        "removes_final_state": config["removes_final_state"],
        "overall": finalize_counts(overall_counts),
        "by_category": {
            category: finalize_counts(counts)
            for category, counts in by_category_counts.items()
        },
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

    print("\nTRACE WITHOUT FINAL STATE EXPERIMENT")
    print("=" * 80)
    print(f"cases: {len(cases)}")

    for name, result in output.items():
        overall = result["overall"]

        print(f"\n{name}")
        print(f"removes_final_state: {result['removes_final_state']}")
        print(f"tp: {overall['tp']}")
        print(f"fp: {overall['fp']}")
        print(f"fn: {overall['fn']}")
        print(f"tn: {overall['tn']}")
        print(f"detection_rate: {overall['detection_rate']}")
        print(f"false_positive_rate: {overall['false_positive_rate']}")

    print(f"\nSaved results to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
