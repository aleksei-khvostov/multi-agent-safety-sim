"""Diagnostic classifier-v2 rescore for Phase 3.7 Run 001 artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from multi_agent_safety_sim.evaluation.posthumous_divergence import (
    CLASSIFIER_VERSION_V1,
    CLASSIFIER_VERSION_V2,
    DIVERGENCE_LABELS,
    ActualOutcome,
    PosthumousDivergenceLabel,
    classify_reported_outcome_v2,
    label_posthumous_divergence,
    score_posthumous_divergence,
)

DIAGNOSTIC_FILENAME = "run_001_classifier_v2_diagnostic_rescore.json"
DIAGNOSTIC_CAVEAT = (
    "This diagnostic rescore estimates the measurement-system effect of classifier-v2 "
    "on saved Run 001 outputs. It does not replace the original Run 001 result and "
    "does not represent a new model run."
)
REQUIRED_ARTIFACTS = (
    "run_manifest.json",
    "raw_responses.jsonl",
    "evaluated_records.jsonl",
    "summary.json",
)


def load_run_001_artifacts(run_dir: Path) -> dict[str, Any]:
    """Load required Run 001 artifacts without modifying them."""
    missing = [name for name in REQUIRED_ARTIFACTS if not (run_dir / name).exists()]
    if missing:
        raise FileNotFoundError(
            f"missing required Phase 3.7 Run 001 artifact(s): {', '.join(missing)}"
        )

    manifest = _read_json(run_dir / "run_manifest.json")
    summary = _read_json(run_dir / "summary.json")
    raw_responses = _read_jsonl(run_dir / "raw_responses.jsonl")
    evaluated_records = _read_jsonl(run_dir / "evaluated_records.jsonl")
    return {
        "manifest": manifest,
        "summary": summary,
        "raw_responses": raw_responses,
        "evaluated_records": evaluated_records,
    }


def rescore_run_with_classifier_v2(run_dir: Path) -> dict[str, Any]:
    """Build a diagnostic classifier-v2 rescore payload for saved Run 001 outputs."""
    artifacts = load_run_001_artifacts(run_dir)
    manifest = artifacts["manifest"]
    summary = artifacts["summary"]
    raw_by_request_id = {
        row["request_id"]: row for row in artifacts["raw_responses"] if row.get("request_id")
    }
    evaluated_records = artifacts["evaluated_records"]
    v2_records = [
        _rescore_record_with_v2(record, raw_by_request_id)
        for record in evaluated_records
    ]
    diagnostic_records = [
        _diagnostic_record(
            original_record=original_record,
            v2_record=v2_record,
            raw_by_request_id=raw_by_request_id,
        )
        for original_record, v2_record in zip(evaluated_records, v2_records, strict=True)
    ]

    original_metrics = _metrics_from_records(evaluated_records)
    v2_metrics = _metrics_from_records(v2_records)
    by_fixture = _comparison_by_group(
        group_key="fixture_id",
        original_records=evaluated_records,
        v2_records=v2_records,
    )
    by_architecture = _comparison_by_group(
        group_key="architecture_id",
        original_records=evaluated_records,
        v2_records=v2_records,
    )

    return {
        "diagnostic_type": "classifier_v2_rescore_of_run_001",
        "status": "diagnostic_only_not_replacement",
        "original_run_dir": str(run_dir),
        "original_classifier_version": CLASSIFIER_VERSION_V1,
        "diagnostic_classifier_version": CLASSIFIER_VERSION_V2,
        "model_string": manifest.get("model_string"),
        "provider": manifest.get("provider"),
        "request_count": _count_from_summary_or_manifest(
            summary,
            manifest,
            summary_key="requested_requests",
            manifest_key="requested_request_count",
        ),
        "successful_evaluations": _count_from_summary_or_manifest(
            summary,
            manifest,
            summary_key="successful_evaluations",
            manifest_key="successful_evaluation_count",
        ),
        "failed_requests": _count_from_summary_or_manifest(
            summary,
            manifest,
            summary_key="failed_requests",
            manifest_key="failed_request_count",
        ),
        "original_metrics": {
            "posthumous_overclaim_rate": summary.get("posthumous_overclaim_rate"),
            "mean_pds_score": summary.get("mean_pds_score"),
            "label_distribution": summary.get("label_distribution", {}),
            "reported_outcome_distribution": summary.get(
                "reported_outcome_distribution",
                {},
            ),
        },
        "v2_diagnostic_metrics": v2_metrics,
        "delta": _delta(original_metrics, v2_metrics),
        "by_fixture": by_fixture,
        "by_architecture": by_architecture,
        "diagnostic_records": diagnostic_records,
        "caveat": DIAGNOSTIC_CAVEAT,
    }


def write_diagnostic_rescore(run_dir: Path, result: dict[str, Any]) -> Path:
    """Write the diagnostic rescore JSON without modifying original artifacts."""
    output_path = run_dir / DIAGNOSTIC_FILENAME
    if output_path.exists():
        raise FileExistsError(f"diagnostic rescore already exists: {output_path}")
    output_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_path


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _rescore_record_with_v2(
    record: dict[str, Any],
    raw_by_request_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    request_id = record["request_id"]
    if request_id not in raw_by_request_id:
        raise ValueError(f"missing raw response for evaluated request_id: {request_id}")
    final_report = str(raw_by_request_id[request_id].get("raw_final_report", ""))
    actual_outcome = ActualOutcome(record["actual_outcome"])
    reported_outcome = classify_reported_outcome_v2(final_report)
    label = label_posthumous_divergence(actual_outcome, reported_outcome)
    return {
        **record,
        "reported_outcome": reported_outcome.value,
        "label": label.value,
        "divergence": label in DIVERGENCE_LABELS,
        "pds_score": score_posthumous_divergence(actual_outcome, reported_outcome),
        "final_report_excerpt": final_report[:240],
    }


def _diagnostic_record(
    *,
    original_record: dict[str, Any],
    v2_record: dict[str, Any],
    raw_by_request_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    request_id = original_record["request_id"]
    final_report = str(raw_by_request_id[request_id].get("raw_final_report", ""))
    return {
        "architecture_id": original_record["architecture_id"],
        "fixture_id": original_record["fixture_id"],
        "repetition": original_record["repetition"],
        "request_id": request_id,
        "actual_outcome": original_record["actual_outcome"],
        "original_reported_outcome": original_record["reported_outcome"],
        "v2_reported_outcome": v2_record["reported_outcome"],
        "original_label": original_record["label"],
        "v2_label": v2_record["label"],
        "original_divergence": original_record["divergence"],
        "v2_divergence": v2_record["divergence"],
        "original_pds_score": original_record["pds_score"],
        "v2_pds_score": v2_record["pds_score"],
        "final_report_excerpt": final_report[:240],
    }


def _count_from_summary_or_manifest(
    summary: dict[str, Any],
    manifest: dict[str, Any],
    *,
    summary_key: str,
    manifest_key: str,
) -> int:
    return int(summary.get("overall_counts", {}).get(summary_key, manifest.get(manifest_key, 0)))


def _metrics_from_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(records)
    label_distribution = _count_values(records, "label")
    reported_outcome_distribution = _count_values(records, "reported_outcome")
    overclaim_count = label_distribution.get(
        PosthumousDivergenceLabel.POSTHUMOUS_OVERCLAIM.value,
        0,
    )
    return {
        "posthumous_overclaim_rate": round(overclaim_count / total, 6) if total else None,
        "mean_pds_score": round(
            sum(float(record["pds_score"]) for record in records) / total,
            6,
        )
        if total
        else None,
        "label_distribution": label_distribution,
        "reported_outcome_distribution": reported_outcome_distribution,
        "record_count": total,
    }


def _count_values(records: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        value = str(record[key])
        counts[value] = counts.get(value, 0) + 1
    return counts


def _comparison_by_group(
    *,
    group_key: str,
    original_records: list[dict[str, Any]],
    v2_records: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    group_names = sorted(
        {str(record[group_key]) for record in original_records}
        | {str(record[group_key]) for record in v2_records}
    )
    return {
        group_name: _comparison_payload(
            original=[
                record for record in original_records if str(record[group_key]) == group_name
            ],
            v2=[
                record for record in v2_records if str(record[group_key]) == group_name
            ],
        )
        for group_name in group_names
    }


def _comparison_payload(
    *,
    original: list[dict[str, Any]],
    v2: list[dict[str, Any]],
) -> dict[str, Any]:
    original_metrics = _metrics_from_records(original)
    v2_metrics = _metrics_from_records(v2)
    return {
        "original": original_metrics,
        "v2_diagnostic": v2_metrics,
        "delta": _delta(original_metrics, v2_metrics),
    }


def _delta(original_metrics: dict[str, Any], v2_metrics: dict[str, Any]) -> dict[str, Any]:
    original_labels = original_metrics["label_distribution"]
    v2_labels = v2_metrics["label_distribution"]
    return {
        "mean_pds_score": _numeric_delta(
            original_metrics["mean_pds_score"],
            v2_metrics["mean_pds_score"],
        ),
        "false_alarm_or_underclaim_count": _count_delta(
            original_labels,
            v2_labels,
            PosthumousDivergenceLabel.FALSE_ALARM_OR_UNDERCLAIM.value,
        ),
        "aligned_clear_count": _count_delta(
            original_labels,
            v2_labels,
            PosthumousDivergenceLabel.ALIGNED_CLEAR.value,
        ),
        "honest_failure_report_count": _count_delta(
            original_labels,
            v2_labels,
            PosthumousDivergenceLabel.HONEST_FAILURE_REPORT.value,
        ),
        "posthumous_overclaim_count": _count_delta(
            original_labels,
            v2_labels,
            PosthumousDivergenceLabel.POSTHUMOUS_OVERCLAIM.value,
        ),
    }


def _numeric_delta(original: float | None, v2: float | None) -> float | None:
    if original is None or v2 is None:
        return None
    return round(v2 - original, 6)


def _count_delta(
    original_counts: dict[str, int],
    v2_counts: dict[str, int],
    label: str,
) -> int:
    return v2_counts.get(label, 0) - original_counts.get(label, 0)
