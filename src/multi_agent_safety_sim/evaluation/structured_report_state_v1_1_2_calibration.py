"""Builder-visible v1.1.2 calibration and independent frozen contract enforcement.

The frozen manifest, never extractor constants or observed results, supplies the
semantic oracle. A pass is implementation evidence, not conformance/adoption.
"""

from __future__ import annotations

import json
from collections import Counter
from typing import Any

from .structured_report_state import (
    REQUIRED_CATEGORIES,
    StructuredReportStateCalibrationError,
)
from .structured_report_state_v1_1_2 import extract_structured_report_state_v1_1_2
from .structured_report_state_v1_1_2_fixture_locks import load_frozen_inputs

REQUIRED_BASELINE_CATEGORIES = REQUIRED_CATEGORIES | {
    "precedence",
    "field_local_conflict",
    "co_description",
    "required_joint_states",
    "scope_contrasts",
    "quote_boundaries",
    "attribution",
    "modality",
    "bounded_negation",
    "negation_frames",
    "clause_boundaries",
    "litotes",
    "metalinguistic",
    "negation_limitations",
    "lexical_boundaries",
    "token_boundaries",
    "blocked_context",
}
# Named-field projections are the normative section 6 requirements. Silence and
# unknown+stable checks below cover the remaining rows of that section directly.
REQUIRED_JOINT_STATES = (
    {0: "completed", 4: "failure_reported"},
    {0: "completed", 1: "unresolved"},
    {0: "completed", 1: "inconclusive"},
    {0: "partially_completed", 3: "no_terminal_event_reported"},
    {0: "partially_completed", 4: "failure_reported"},
    {0: "partially_completed", 1: "resolved"},
    {0: "not_completed", 1: "unresolved"},
    {0: "not_completed", 1: "inconclusive"},
    {0: "not_completed", 4: "failure_reported"},
    {4: "no_failure_reported", 1: "unresolved"},
    {4: "no_failure_reported", 1: "inconclusive"},
    {3: "terminal_event_reported", 1: "unresolved"},
    {2: "explicit_no_partial_progress", 4: "failure_reported"},
    {2: "explicit_no_partial_progress", 3: "no_terminal_event_reported", 4: "no_failure_reported"},
)
# Semantic families have explicit contrast members, not just category-name checks.
REQUIRED_CONTRAST_GROUPS = (
    *[(f"transition_{i}_later", f"transition_{i}_control") for i in range(12)],
    *[
        tuple(
            f"scope_{i}_{kind}"
            for kind in (
                "operative",
                "single",
                "double",
                "attributed",
                "endorsed",
                "quote_endorsed",
            )
        )
        for i in range(6)
    ],
    *[
        tuple(f"negation_{field}_{gap}" for gap in range(6))
        for field in ("failure", "terminal", "partial", "uncertainty")
    ],
    *[
        tuple(f"token_{i}_{kind}" for kind in ("plain", "embedded", "quoted", "negated"))
        for i in range(4)
    ],
    *[(f"blocked_{i}", f"blocked_{i + 1}") for i in range(0, 14, 2)],
    ("nested_balanced", "malformed_quote", "excess_nesting", "malformed_endorsement"),
    ("modal_failure", "if_4", "scope_4_operative"),
    ("modal_completion", "provisional_completion", "attempt_completion", "scope_0_operative"),
    ("modal_terminal", "if_3", "scope_3_operative"),
    (
        "might_inconclusive",
        "may_inconclusive_joint",
        "would_inconclusive",
        "inability_confirm",
        "modal_uncertainty_control",
    ),
    (
        "litotes_unsuccessful",
        "litotes_incomplete",
        "litotes_independent",
        "meta_unresolved",
        "nested_negation_limit",
        "long_negation_limit",
    ),
    (
        "attribution_colon",
        "attribution_denied",
        "attribution_narrator_negative",
        "bounded_failure_reference",
        "bounded_terminal_reference",
        "unbound_terminal_reference",
        "endorsed_failure_accounts",
        "endorsed_uncertainty_accounts",
    ),
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise StructuredReportStateCalibrationError(message)


def parse_records(data: bytes) -> list[dict[str, str]]:
    """Reject malformed JSONL and non-string records before field access."""
    rows: list[dict[str, str]] = []
    try:
        for number, line in enumerate(data.decode("utf-8").splitlines(), 1):
            _require(bool(line.strip()), f"blank record at line {number}")
            row = json.loads(line)
            _require(isinstance(row, dict), f"invalid record at line {number}")
            _require(
                all(isinstance(value, str) for value in row.values()),
                f"non-string record value at line {number}",
            )
            rows.append(row)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise StructuredReportStateCalibrationError(f"malformed JSONL: {exc}") from exc
    return rows


def _state(row: dict[str, str], fields: list[str]) -> dict[str, str]:
    return {field: row["expected_" + field] for field in fields}


def validate_coverage(states: list[dict[str, str]], manifest: dict[str, Any]) -> None:
    """All 22 values must occur both alone and with another stable field."""
    fields: list[str] = manifest["primary_field_order"]
    silence: dict[str, str] = manifest["literal_silence_values"]
    for field, values in manifest["literal_enum_values"].items():
        for value in values:
            _require(
                any(
                    state[field] == value
                    and all(state[other] == silence[other] for other in fields if other != field)
                    for state in states
                ),
                f"missing isolated enum: {field}={value}",
            )
            _require(
                any(
                    state[field] == value
                    and any(
                        state[other] not in (silence[other], "unknown")
                        for other in fields
                        if other != field
                    )
                    for state in states
                ),
                f"missing joint enum: {field}={value}",
            )
    for joint in REQUIRED_JOINT_STATES:
        _require(
            any(all(state[fields[i]] == value for i, value in joint.items()) for state in states),
            f"missing required joint state: {joint}",
        )


def validate_semantic_contrasts(
    indexed: dict[str, dict[str, str]], manifest: dict[str, Any]
) -> None:
    """Enforce the independent full-state oracle and all 28 frozen relations."""
    fields: list[str] = manifest["primary_field_order"]
    for name, expected in manifest["primary_state_oracle"].items():
        _require(name in indexed, f"missing semantic contrast member: {name}")
        _require(_state(indexed[name], fields) == expected, f"semantic contrast oracle: {name}")
    for relation in manifest["semantic_contrast_requirements"]:
        left = _state(indexed[relation["left"]], fields)
        right = _state(indexed[relation["right"]], fields)
        changed = {field for field in fields if left[field] != right[field]}
        invariant = set(fields) - changed
        _require(
            changed == set(relation["expected_changed_fields"])
            and invariant == set(relation["expected_invariant_fields"]),
            f"lost semantic contrast: {relation['id']}",
        )


def validate_inherited_records(
    baseline: list[dict[str, str]], repair: list[dict[str, str]], manifest: dict[str, Any]
) -> None:
    """Validate schema, exact prefixes, identities, families, coverage and contrasts.

    This pure validator is also used for in-memory negative tests. It cannot
    certify a registered calibration pass; the public gate always checks hashes.
    """
    fields: list[str] = manifest["primary_field_order"]
    keys = {"case_id", "report_text", "category", "rationale", "source_type", "schema_version"}
    keys.update("expected_" + field for field in fields)
    indexed: dict[str, dict[str, str]] = {}
    for component, rows, spec in (
        ("baseline", baseline, manifest["predecessor"]),
        ("repair", repair, manifest["repair_regression"]),
    ):
        _require(len(rows) == spec["expected_case_count"], f"{component} case count drift")
        ids: set[str] = set()
        for row in rows:
            _require(isinstance(row, dict) and set(row) == keys, "invalid record keys")
            _require(all(isinstance(v, str) for v in row.values()), "invalid record value type")
            _require(
                bool(row["case_id"].strip()) and row["case_id"] not in ids,
                "duplicate/empty case_id",
            )
            ids.add(row["case_id"])
            _require(
                row["schema_version"] == spec["schema_version"], "record schema identity drift"
            )
            _require(
                any(
                    row["rationale"].startswith(prefix) and row["source_type"] in types
                    for prefix, types in manifest["exact_provenance_prefixes"].items()
                ),
                "invalid exact provenance prefix/source mapping",
            )
            for field, value in _state(row, fields).items():
                _require(value in manifest["literal_enum_values"][field], "invalid enum value")
            indexed[component + ":" + row["case_id"]] = row
        if component == "repair":
            _require(ids == set(spec["expected_case_ids"]), "repair case identity drift")
        else:
            counts = Counter(row["category"] for row in rows)
            _require(
                all(counts[cat] >= 2 for cat in REQUIRED_BASELINE_CATEGORIES),
                "missing required semantic-family coverage",
            )
            for group in REQUIRED_CONTRAST_GROUPS:
                _require(set(group) <= ids, f"missing inherited contrast members: {group}")
    _require(len(indexed) == manifest["expected_total_case_count"], "total case count drift")
    validate_coverage([_state(row, fields) for row in indexed.values()], manifest)
    validate_semantic_contrasts(indexed, manifest)


def expected_flags(state: dict[str, str], manifest: dict[str, Any]) -> list[str]:
    """Diagnostics follow independently frozen expected states, not actual output."""
    flags = [
        flag
        for field, flag in manifest["literal_field_conflict_flags"].items()
        if state[field] == "unknown"
    ]
    if state["completion_status"] == "completed":
        if state["uncertainty_status"] in ("unresolved", "inconclusive"):
            flags.append("completed_with_unresolved")
        if state["terminal_event_claim_status"] == "terminal_event_reported":
            flags.append("completed_with_terminal_event")
        if state["explicit_failure_status"] == "failure_reported":
            flags.append("completed_with_explicit_failure")
    return sorted(flags)


def validate_disclosed_records(
    components: dict[str, list[dict[str, str]]],
    manifest: dict[str, Any],
    inherited_manifest: dict[str, Any],
) -> dict[str, dict[str, str]]:
    """Check all inherited obligations plus every newly frozen relation/oracle.

    Pure negative-test surface; only run_calibration can certify the registered
    SHA-locked pass. No output from an extractor participates in the oracle.
    """
    validate_inherited_records(
        components["historical_v1_1_baseline"],
        components["historical_v1_1_1_repair"],
        inherited_manifest,
    )
    fields: list[str] = manifest["primary_field_order"]
    indexed = {"repair:" + row["case_id"]: row for row in components["historical_v1_1_1_repair"]}
    for spec in manifest["input_components"]:
        name = spec["name"]
        rows = components[name]
        _require(len(rows) == spec["expected_case_count"], f"{name} case count drift")
        if not name.startswith("disclosed_"):
            continue
        for row in rows:
            _require(set(row) == set(manifest["record_keys"]), "invalid record keys")
            _require(all(isinstance(v, str) for v in row.values()), "invalid record value type")
            key = row["case_id"]
            _require(bool(key.strip()) and key not in indexed, "duplicate/empty case_id")
            _require(
                row["schema_version"] == spec["schema_version"], "record schema identity drift"
            )
            _require(
                any(
                    row["rationale"].startswith(prefix) and row["source_type"] in types
                    for prefix, types in manifest["exact_provenance_prefixes"].items()
                ),
                "invalid exact provenance prefix/source mapping",
            )
            _require(
                all(
                    value in manifest["literal_enum_values"][field]
                    for field, value in _state(row, fields).items()
                ),
                "invalid enum value",
            )
            indexed[key] = row
    oracle = manifest["primary_and_flag_oracle"]
    _require(set(indexed) == set(oracle), "disclosed oracle case identity drift")
    for key, expectation in oracle.items():
        _require(
            _state(indexed[key], fields) == expectation["expected_state"],
            f"semantic contrast oracle: {key}",
        )
        _require(
            sorted(expectation["expected_contradiction_flags"])
            == expected_flags(expectation["expected_state"], manifest),
            f"independent diagnostic oracle drift: {key}",
        )
    for family, keys in manifest["architecture_family_members"].items():
        _require(
            len(keys) == manifest["architecture_family_counts"][family],
            "architecture family count drift",
        )
        _require(
            all(indexed[key]["category"] == "architecture_" + family for key in keys),
            "architecture family category drift",
        )
    relations = manifest["semantic_relations"]
    _require(
        len(relations) == manifest["semantic_relation_count"] == 66, "semantic relation count drift"
    )
    for relation in relations:
        left, right = (oracle[relation[key]] for key in ("from_case", "to_case"))
        changed = {
            field
            for field in fields
            if left["expected_state"][field] != right["expected_state"][field]
        }
        _require(
            changed == set(relation["expected_changed_fields"])
            and set(fields) - changed == set(relation["expected_invariant_fields"]),
            f"lost semantic contrast: {relation['relation_id']}",
        )
        _require(
            left["expected_contradiction_flags"] == relation["expected_flags_from"]
            and right["expected_contradiction_flags"] == relation["expected_flags_to"],
            "semantic relation flags drift",
        )
    _require(
        sum(map(len, components.values()))
        == manifest["expected_disclosed_suite_case_count"]
        == 343,
        "total case count drift",
    )
    return indexed


def run_structured_report_state_v1_1_2_calibration() -> dict[str, Any]:
    """Run only the four disclosed components. No holdout input/path is accepted."""
    manifest, content = load_frozen_inputs()
    inherited = json.loads(content[manifest["inherited_contract"]["path"]])
    components = {
        spec["name"]: parse_records(content[spec["path"]]) for spec in manifest["input_components"]
    }
    validate_disclosed_records(components, manifest, inherited)
    fields: list[str] = manifest["primary_field_order"]
    summaries: dict[str, dict[str, Any]] = {}
    for spec in manifest["input_components"]:
        name = spec["name"]
        rows = components[name]
        failed: list[str] = []
        field_matches = dict.fromkeys(fields, 0)
        for row in rows:
            actual = extract_structured_report_state_v1_1_2(row["report_text"]).to_dict()
            _require(
                actual["schema_version"] == manifest["schema_version"],
                "extractor schema identity drift",
            )
            _require(
                actual["extractor_version"] == manifest["extractor_version"],
                "extractor identity drift",
            )
            expected = _state(row, fields)
            if name == "historical_v1_1_baseline":
                flags = expected_flags(expected, inherited)
            else:
                key = ("repair:" if name == "historical_v1_1_1_repair" else "") + row["case_id"]
                flags = manifest["primary_and_flag_oracle"][key]["expected_contradiction_flags"]
            if {field: actual[field] for field in fields} != expected or actual[
                "contradiction_flags"
            ] != sorted(flags):
                failed.append(row["case_id"])
            for field in fields:
                field_matches[field] += int(actual[field] == expected[field])
        _require(not failed, f"{name} exact full-state/flag mismatch: {failed}")
        summaries[name] = {
            "fixture": spec["path"],
            "sha256": spec["sha256"],
            "source_schema_version": spec["schema_version"],
            "total_cases": len(rows),
            "full_state_exact_match": len(rows),
            "field_exact_matches": field_matches,
            "failed": 0,
        }
    return {
        "schema_version": manifest["schema_version"],
        "extractor_version": manifest["extractor_version"],
        "calibration_identity": manifest["calibration_identity"],
        "components": summaries,
        "total_cases": 343,
        "full_state_exact_match": 343,
        "failed": 0,
        "semantic_relations_verified": 66,
        "inherited_semantic_relations_verified": 28,
        "status": "v1.1.2 IMPLEMENTED — HOLDOUT UNOPENED — PENDING INDEPENDENT CONFORMANCE AUDIT",
        "holdout_opened": False,
        "holdout_executed": False,
        "model_api_called": False,
        "stop_condition_released": False,
        "b2_authorized": False,
        "data_collection_authorized": False,
    }
