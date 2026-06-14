import json
import re
from collections import defaultdict
from pathlib import Path


EVAL_PATH = Path("eval/ambiguity_cases.json")
RESULTS_PATH = Path("experiments/trace_ablation_results.json")


ABLATIONS = {
    "baseline": [],
    "remove_partial_progress": [
        r"processed=\d+",
        r"total=\d+",
        r"completed_steps=\d+",
        r"failed_steps=\d+",
        r"skipped_later=true",
    ],
    "remove_retry": [
        r"retry_allowed=false",
        r"retry_attempted=true",
    ],
    "remove_recovery": [
        r"first_attempt=failed",
        r"recovery=succeeded",
        r"recovery=partial",
    ],
    "remove_timeout": [
        r"timeout=true",
    ],
    "remove_blocked": [
        r"blocked=true",
        r"policy_block=true",
    ],
    "remove_warning": [
        r"warning=true",
        r"warning=non_critical",
    ],
}


def clean_trace(trace: str, patterns: list[str]) -> str:
    cleaned = trace

    # Always remove explicit final_state to test behavioral trace value.
    cleaned = re.sub(r";?\s*final_state=[A-Z_]+", "", cleaned)

    for pattern in patterns:
        cleaned = re.sub(r";?\s*" + pattern, "", cleaned)

    cleaned = re.sub(r";\s*;", ";", cleaned)
    return cleaned.strip("; ")


def predict_divergence(case: dict, observed_trace: str) -> bool:
    observed = " ".join([
        case["planner_report"],
        case["worker_output"],
        observed_trace,
    ]).lower()

    reported_state = case["reported_state"]

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

    if "blocked=true" in observed and "retry_attempted=true" in observed:
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


def evaluate_condition(name: str, patterns: list[str], cases: list[dict]) -> dict:
    overall_counts = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
    by_category_counts = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0, "tn": 0})
    rows = []

    for case in cases:
        observed_trace = clean_trace(case["execution_trace"], patterns)
        actual_divergence = case["actual_state"] != case["reported_state"]
        predicted_divergence = predict_divergence(case, observed_trace)

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
            "observed_trace": observed_trace,
        })

    return {
        "condition": name,
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
        name: evaluate_condition(name, patterns, cases)
        for name, patterns in ABLATIONS.items()
    }

    baseline = output["baseline"]["overall"]

    for name, payload in output.items():
        overall = payload["overall"]
        overall["detection_drop"] = round(
            baseline["detection_rate"] - overall["detection_rate"],
            3,
        )
        overall["fpr_increase"] = round(
            overall["false_positive_rate"] - baseline["false_positive_rate"],
            3,
        )

    ranking_detection = sorted(
        [
            (name, payload["overall"]["detection_drop"])
            for name, payload in output.items()
            if name != "baseline"
        ],
        key=lambda x: x[1],
        reverse=True,
    )

    ranking_fpr = sorted(
        [
            (name, payload["overall"]["fpr_increase"])
            for name, payload in output.items()
            if name != "baseline"
        ],
        key=lambda x: x[1],
        reverse=True,
    )

    final_output = {
        "results": output,
        "impact_ranking_detection": ranking_detection,
        "impact_ranking_fpr": ranking_fpr,
    }

    with open(RESULTS_PATH, "w") as f:
        json.dump(final_output, f, indent=2)

    print("\nTRACE ABLATION EXPERIMENT")
    print("=" * 80)
    print(f"cases: {len(cases)}")

    for name, payload in output.items():
        overall = payload["overall"]
        print(f"\n{name}")
        print(f"tp: {overall['tp']}")
        print(f"fp: {overall['fp']}")
        print(f"fn: {overall['fn']}")
        print(f"tn: {overall['tn']}")
        print(f"detection_rate: {overall['detection_rate']}")
        print(f"false_positive_rate: {overall['false_positive_rate']}")
        print(f"detection_drop: {overall['detection_drop']}")
        print(f"fpr_increase: {overall['fpr_increase']}")

    print("\nIMPACT RANKING — DETECTION")
    for name, score in ranking_detection:
        print(f"{name}: {score}")

    print("\nIMPACT RANKING — FPR")
    for name, score in ranking_fpr:
        print(f"{name}: {score}")

    print(f"\nSaved results to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
