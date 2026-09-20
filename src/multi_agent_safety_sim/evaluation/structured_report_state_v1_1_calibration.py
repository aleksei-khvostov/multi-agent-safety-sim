"""Independent mandatory SHA gate for calibration-only Structured Report State v1.1."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from .fixture_locks import (
    STRUCTURED_REPORT_STATE_V1_1_EXPECTED_CASE_COUNT,
    STRUCTURED_REPORT_STATE_V1_1_GOLDEN_PATH,
    STRUCTURED_REPORT_STATE_V1_1_GOLDEN_SHA256,
    assert_fixture_sha256,
)
from .structured_report_state import (
    ALLOWED_SOURCE_TYPES,
    REQUIRED_CATEGORIES,
    REQUIRED_GOLDEN_FIELDS,
    StructuredReportStateCalibrationError,
    load_structured_report_state_golden,
)
from .structured_report_state_v1_1 import (
    ENUMS,
    FIELDS,
    SILENCE,
    STRUCTURED_REPORT_STATE_EXTRACTOR_V1_1,
    STRUCTURED_REPORT_STATE_GOLDEN_V1_1,
    STRUCTURED_REPORT_STATE_SCHEMA_V1_1,
    extract_structured_report_state_v1_1,
)

REQUIRED_V1_1_CATEGORIES = REQUIRED_CATEGORIES | {
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


def validate_structured_report_state_v1_1_records(cases: list[dict[str, Any]]) -> None:
    """Validate exact wire schema, provenance, enums, joint and contrast coverage."""
    _require(bool(cases), "empty v1.1 fixture")
    ids: set[str] = set()
    categories: Counter[str] = Counter()
    states: list[tuple[str, ...]] = []
    for row in cases:
        _require(
            isinstance(row, dict) and set(row) == REQUIRED_GOLDEN_FIELDS,
            "invalid keys in v1.1 record",
        )
        _require(all(isinstance(v, str) for v in row.values()), "all record values must be strings")
        _require(bool(row["case_id"]) and row["case_id"] not in ids, "duplicate/empty case_id")
        ids.add(row["case_id"])
        _require(
            row["schema_version"] == STRUCTURED_REPORT_STATE_SCHEMA_V1_1, "invalid schema_version"
        )
        _require(row["source_type"] in ALLOWED_SOURCE_TYPES, "invalid source_type")
        prefix = row["rationale"].split(":", 1)[0]
        valid_provenance = {
            "audit-derived normalized": {"synthetic", "contrastive"},
            "prereg-designed contrastive": {"contrastive"},
            "regression carryover": {"synthetic", "normalized_run_pattern"},
        }
        _require(
            row["source_type"] in valid_provenance.get(prefix, set()), "invalid provenance mapping"
        )
        state = tuple(row["expected_" + f] for f in FIELDS)
        for value, enum in zip(state, ENUMS, strict=True):
            _require(value in {v.value for v in enum}, "invalid enum value")
        states.append(state)
        categories[row["category"]] += 1
    _require(
        len(cases) == STRUCTURED_REPORT_STATE_V1_1_EXPECTED_CASE_COUNT, "v1.1 case count drift"
    )
    _require(
        all(categories[cat] >= 2 for cat in REQUIRED_V1_1_CATEGORIES),
        "missing required semantic-family coverage",
    )
    for group in REQUIRED_CONTRAST_GROUPS:
        _require(set(group) <= ids, f"missing semantic contrast members: {group}")
    _require(tuple(SILENCE) in states, "missing full silence")
    for joint in REQUIRED_JOINT_STATES:
        _require(
            any(all(s[i] == v for i, v in joint.items()) for s in states),
            f"missing joint state {joint}",
        )
    for i, enum in enumerate(ENUMS):
        for value in enum:
            _require(
                any(s[i] == value for s in states), f"missing enum coverage {FIELDS[i]}={value}"
            )
            _require(
                any(
                    s[i] == value
                    and any(s[j] not in {SILENCE[j], "unknown"} for j in range(5) if j != i)
                    for s in states
                ),
                f"missing joint enum coverage {FIELDS[i]}={value}",
            )
        _require(
            any(
                s[i] == "unknown" and all(s[j] == SILENCE[j] for j in range(5) if j != i)
                for s in states
            ),
            f"missing isolated conflict {FIELDS[i]}",
        )


def run_structured_report_state_v1_1_calibration(
    path: Path = STRUCTURED_REPORT_STATE_V1_1_GOLDEN_PATH,
) -> dict[str, Any]:
    """Run the mandatory SHA-checked gate; no caller-supplied lock bypass."""
    assert_fixture_sha256(
        path,
        STRUCTURED_REPORT_STATE_V1_1_GOLDEN_SHA256,
        fixture_name="structured_report_state_v1_1_golden",
    )
    cases = load_structured_report_state_golden(path)
    validate_structured_report_state_v1_1_records(cases)
    failed = []
    field_matches = dict.fromkeys(FIELDS, 0)
    unknown_counts = dict.fromkeys(FIELDS, 0)
    for row in cases:
        actual = extract_structured_report_state_v1_1(row["report_text"]).to_dict()
        _require(
            actual["schema_version"] == STRUCTURED_REPORT_STATE_SCHEMA_V1_1,
            "extractor schema identity drift",
        )
        _require(
            actual["extractor_version"] == STRUCTURED_REPORT_STATE_EXTRACTOR_V1_1,
            "extractor identity drift",
        )
        ok = True
        for f in FIELDS:
            match = actual[f] == row["expected_" + f]
            field_matches[f] += int(match)
            unknown_counts[f] += int(actual[f] == "unknown")
            ok = ok and match
        if not ok:
            failed.append(row["case_id"])
    _require(not failed, f"v1.1 exact full-state mismatch: {failed}")
    return {
        "fixture": str(path),
        "schema_version": STRUCTURED_REPORT_STATE_SCHEMA_V1_1,
        "extractor_version": STRUCTURED_REPORT_STATE_EXTRACTOR_V1_1,
        "calibration_identity": STRUCTURED_REPORT_STATE_GOLDEN_V1_1,
        "sha256": STRUCTURED_REPORT_STATE_V1_1_GOLDEN_SHA256,
        "total_cases": len(cases),
        "full_state_exact_match": len(cases),
        "failed": 0,
        "field_exact_matches": field_matches,
        "unknown_counts_by_field": unknown_counts,
        "family_counts": dict(sorted(Counter(r["category"] for r in cases).items())),
        "model_api_called": False,
    }
