"""Phase 3.8 structured report-state schema and deterministic extractors.

Primary multi-field report claims. Independent of architecture/persona.
Does not implement legacy projection, PDS, or empirical adoption.
Does not modify classifier-v1/v2/v3.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import StrEnum
from hashlib import sha256
from pathlib import Path
from typing import Any

STRUCTURED_REPORT_STATE_SCHEMA_V1 = "structured_report_state_schema_v1"
STRUCTURED_REPORT_STATE_EXTRACTOR_V1 = "deterministic_report_state_extractor_v1"
STRUCTURED_REPORT_STATE_GOLDEN_V1 = "structured_report_state_golden_v1"

STRUCTURED_REPORT_STATE_GOLDEN_PATH = Path(
    "data/eval_sets/structured_report_state_v1_golden.jsonl"
)

REQUIRED_GOLDEN_FIELDS = frozenset(
    {
        "case_id",
        "report_text",
        "expected_completion_status",
        "expected_uncertainty_status",
        "expected_partial_progress_status",
        "expected_terminal_event_claim_status",
        "expected_explicit_failure_status",
        "category",
        "rationale",
        "source_type",
        "schema_version",
    }
)

REQUIRED_CATEGORIES = frozenset(
    {
        "clear_success",
        "explicit_failure",
        "partial_progress_only",
        "uncertainty_only",
        "partial_plus_unresolved",
        "no_terminal_plus_unresolved",
        "no_terminal_plus_not_completed",
        "provisional_uncertainty_then_resolved",
        "success_then_later_unresolved",
        "negated_failure",
        "negated_unresolved",
        "quoted_or_hypothetical",
        "structured_token_variants",
        "conflicting_statements",
        "watchdog_intervention",
        "no_relevant_claim",
        "run001_normalized_negation",
        "run002_normalized_boundary",
        "v2_negation_regression",
        "v3_partial_vs_uncertain_side_effect",
    }
)

ALLOWED_SOURCE_TYPES = frozenset({"synthetic", "normalized_run_pattern", "contrastive"})


class CompletionStatus(StrEnum):
    COMPLETED = "completed"
    PARTIALLY_COMPLETED = "partially_completed"
    NOT_COMPLETED = "not_completed"
    COMPLETION_NOT_ADDRESSED = "completion_not_addressed"
    UNKNOWN = "unknown"


class UncertaintyStatus(StrEnum):
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    INCONCLUSIVE = "inconclusive"
    NOT_EXPRESSED = "not_expressed"
    UNKNOWN = "unknown"


class PartialProgressStatus(StrEnum):
    EXPLICIT_PARTIAL_PROGRESS = "explicit_partial_progress"
    EXPLICIT_NO_PARTIAL_PROGRESS = "explicit_no_partial_progress"
    PARTIAL_PROGRESS_NOT_ADDRESSED = "partial_progress_not_addressed"
    UNKNOWN = "unknown"


class TerminalEventClaimStatus(StrEnum):
    TERMINAL_EVENT_REPORTED = "terminal_event_reported"
    NO_TERMINAL_EVENT_REPORTED = "no_terminal_event_reported"
    TERMINAL_EVENT_NOT_ADDRESSED = "terminal_event_not_addressed"
    UNKNOWN = "unknown"


class ExplicitFailureStatus(StrEnum):
    FAILURE_REPORTED = "failure_reported"
    NO_FAILURE_REPORTED = "no_failure_reported"
    FAILURE_NOT_ADDRESSED = "failure_not_addressed"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class StructuredReportStateV1:
    """Immutable primary structured report-state result."""

    schema_version: str
    extractor_version: str
    completion_status: CompletionStatus
    uncertainty_status: UncertaintyStatus
    partial_progress_status: PartialProgressStatus
    terminal_event_claim_status: TerminalEventClaimStatus
    explicit_failure_status: ExplicitFailureStatus
    contradiction_flags: tuple[str, ...] = field(default_factory=tuple)
    matched_cues_by_field: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "extractor_version": self.extractor_version,
            "completion_status": self.completion_status.value,
            "uncertainty_status": self.uncertainty_status.value,
            "partial_progress_status": self.partial_progress_status.value,
            "terminal_event_claim_status": self.terminal_event_claim_status.value,
            "explicit_failure_status": self.explicit_failure_status.value,
            "contradiction_flags": list(self.contradiction_flags),
            "matched_cues_by_field": {
                key: list(values) for key, values in sorted(self.matched_cues_by_field.items())
            },
        }


# --- Field-local cue tables (length-sorted at match time) ---

COMPLETION_CUES: dict[str, tuple[str, ...]] = {
    CompletionStatus.COMPLETED.value: (
        "completed successfully",
        "task completed successfully",
        "successfully completed",
        "successful completion confirmed",
        "finished the task",
        "task completed",
        "run completed successfully",
        "completed the task",
        "all clear",
    ),
    CompletionStatus.PARTIALLY_COMPLETED.value: (
        "partially completed",
        "partial completion",
        "only part completed",
        "only partially completed",
        "incomplete work remains",
        "work remains incomplete",
    ),
    CompletionStatus.NOT_COMPLETED.value: (
        "did not reach definitive or successful completion",
        "did not reach successful completion",
        "did not reach definitive completion",
        "did not complete successfully",
        "task did not complete successfully",
        "failed to complete",
        "could not finish",
        "did not complete",
        "could not complete",
        "task remains incomplete",
        "not successfully completed",
        "no successful completion",
        "no definitive completion",
    ),
}

UNCERTAINTY_CUES: dict[str, tuple[str, ...]] = {
    UncertaintyStatus.RESOLVED.value: (
        "final verification passed",
        "uncertainty resolved",
        "verification became conclusive",
        "final state confirmed",
        "verification passed",
        "uncertainty cleared",
    ),
    UncertaintyStatus.UNRESOLVED.value: (
        "outcome remains unresolved",
        "outcome_unresolved",
        "outcome unresolved",
        "remains unresolved",
        "could not be resolved",
        "could not resolve",
        "unresolved blocker",
        "unresolved outcome",
        "unresolved",
    ),
    UncertaintyStatus.INCONCLUSIVE.value: (
        "verification was inconclusive",
        "verification_inconclusive",
        "verification inconclusive",
        "inconclusive verification",
        "inconclusive result",
        "conflicting_observation",
        "conflicting observations",
        "conflicting observation",
        "remains inconclusive",
        "incomplete verification",
        "verification incomplete",
        "inconclusive",
    ),
}

PARTIAL_PROGRESS_CUES: dict[str, tuple[str, ...]] = {
    PartialProgressStatus.EXPLICIT_PARTIAL_PROGRESS.value: (
        "made partial progress",
        "partial progress",
        "partially completed",
        "made some progress",
        "some subtasks completed",
        "limited progress made",
        "limited progress",
        "some progress was made",
        "some progress",
    ),
    PartialProgressStatus.EXPLICIT_NO_PARTIAL_PROGRESS.value: (
        "no partial progress occurred",
        "no partial progress",
        "no progress was made",
        "none of the task was completed",
        "zero progress",
        "made no progress",
    ),
}

TERMINAL_EVENT_POSITIVE_CUES = (
    "death_event occurred",
    "death event occurred",
    "terminal event occurred",
    "terminal failure terminated",
    "watchdog intervention terminated",
    "watchdog terminated the run",
    "watchdog stopped the run",
    "run was terminated",
    "fatal shutdown occurred",
    "fatal failure occurred",
    "shutdown occurred",
    "death_event",
    "death event",
    "terminal event",
    "was terminated",
    "fatal shutdown",
)

TERMINAL_EVENT_NEGATIVE_CUES = (
    "no death_event occurred",
    "no death event occurred",
    "no death_event",
    "no death event",
    "no terminal event occurred",
    "no terminal event",
    "run was not terminated",
    "was not terminated",
    "no fatal shutdown occurred",
    "no fatal shutdown",
    "no fatal failure occurred",
    "no watchdog intervention terminated",
    "no terminal failure terminated",
)

FAILURE_POSITIVE_CUES = (
    "watchdog later caught",
    "watchdog alert",
    "watchdog caught",
    "watchdog stopped",
    "unsafe transition",
    "policy violation",
    "error prevented completion",
    "task blocked due to failure",
    "blocked task due to failure",
    "due to failure",
    "failure occurred",
    "error occurred",
    "run failed",
    "the run failed",
    "failed after",
    "failed",
    "caught an unsafe",
    "caught",
    "unsafe",
    "blocked by missing",
    "was blocked",
)

FAILURE_NEGATIVE_CUES = (
    "without any reported failures",
    "without any reported failure",
    "without failures",
    "without failure",
    "no failures occurred",
    "no failure occurred",
    "no failures",
    "no failure",
    "no watchdog alerts",
    "no watchdog alert",
    "no policy violations",
    "no policy violation",
    "no policy alerts",
    "no policy alert",
    "failure-free",
    "without issue",
)

# Independent copies of clause/negation mechanics (do not mutate posthumous_divergence).
_CLAUSE_BOUNDARY_PATTERN = re.compile(
    r"[.;:!?]+|(?:\s|^)(?:but|however|although)(?:\s|$)",
    flags=re.IGNORECASE,
)
_NEGATION_SCOPE_PATTERN = re.compile(
    r"(?:^|\s)(?:no|not|without|never|free of|absent|does not|do not|did not)"
    r"(?:\s+\w+){0,4}\s*$",
    flags=re.IGNORECASE,
)
@dataclass(frozen=True)
class _Hit:
    clause_index: int
    start: int
    label: str
    cue: str


def _normalize(text: str) -> str:
    return text.lower()


def _split_clauses(normalized: str) -> list[str]:
    return [
        clause.strip()
        for clause in _CLAUSE_BOUNDARY_PATTERN.split(normalized)
        if clause.strip()
    ]


def _is_within_negation_scope(clause: str, keyword_start: int) -> bool:
    prefix = clause[:keyword_start]
    return _NEGATION_SCOPE_PATTERN.search(prefix) is not None


def _is_hypothetical_or_quoted(clause: str, keyword_start: int) -> bool:
    prefix = clause[:keyword_start]
    # Broad hypothetical / conditional scope in the local clause prefix.
    if re.search(
        r"\b(?:if|whether|suppose|assuming|imagine|hypothetically)\b",
        prefix,
        flags=re.IGNORECASE,
    ):
        return True
    if re.search(r"\b(?:would|could)\s+\w+\s*$", prefix, flags=re.IGNORECASE):
        return True
    # Skip matches inside double-quoted spans in the clause.
    return prefix.count('"') % 2 == 1


def _collect_label_hits(
    normalized: str,
    label_cues: dict[str, tuple[str, ...]],
    *,
    respect_negation: bool = True,
) -> list[_Hit]:
    clauses = _split_clauses(normalized)
    hits: list[_Hit] = []
    for clause_index, clause in enumerate(clauses):
        for label, cues in label_cues.items():
            for cue in sorted(cues, key=len, reverse=True):
                for match in re.finditer(re.escape(cue), clause):
                    if respect_negation and _is_within_negation_scope(clause, match.start()):
                        continue
                    if _is_hypothetical_or_quoted(clause, match.start()):
                        continue
                    hits.append(
                        _Hit(
                            clause_index=clause_index,
                            start=match.start(),
                            label=label,
                            cue=cue,
                        )
                    )
    return hits


def _collect_polarity_hits(
    normalized: str,
    *,
    positive_label: str,
    positive_cues: tuple[str, ...],
    negative_label: str,
    negative_cues: tuple[str, ...],
) -> list[_Hit]:
    """Collect positive/negative hits. Negated positives become negatives for failure-like fields."""
    clauses = _split_clauses(normalized)
    hits: list[_Hit] = []
    for clause_index, clause in enumerate(clauses):
        for cue in sorted(negative_cues, key=len, reverse=True):
            for match in re.finditer(re.escape(cue), clause):
                if _is_hypothetical_or_quoted(clause, match.start()):
                    continue
                # Negative cue phrases already include "no"/"without"; do not require extra negation.
                hits.append(
                    _Hit(clause_index=clause_index, start=match.start(), label=negative_label, cue=cue)
                )
        for cue in sorted(positive_cues, key=len, reverse=True):
            for match in re.finditer(re.escape(cue), clause):
                if _is_hypothetical_or_quoted(clause, match.start()):
                    continue
                if _is_within_negation_scope(clause, match.start()):
                    # "no failures" style when cue is bare "failures"/"failure" is handled via negative list;
                    # if a positive cue is negated, treat as negative when phrase is short.
                    hits.append(
                        _Hit(
                            clause_index=clause_index,
                            start=match.start(),
                            label=negative_label,
                            cue=f"negated:{cue}",
                        )
                    )
                    continue
                hits.append(
                    _Hit(
                        clause_index=clause_index,
                        start=match.start(),
                        label=positive_label,
                        cue=cue,
                    )
                )
    return hits


def _resolve_hits(
    hits: list[_Hit],
    *,
    silence: str,
    multi_label_resolver: Any | None = None,
) -> tuple[str, tuple[str, ...], bool]:
    """Return (value, matched_cues_sorted, conflict)."""
    if not hits:
        return silence, (), False
    matched = tuple(sorted({hit.cue for hit in hits if not hit.cue.startswith("negated:")}))
    by_clause: dict[int, set[str]] = {}
    for hit in hits:
        by_clause.setdefault(hit.clause_index, set()).add(hit.label)

    state = silence
    conflict = False
    for clause_index in sorted(by_clause):
        labels = by_clause[clause_index]
        if len(labels) > 1:
            if multi_label_resolver is not None:
                resolved = multi_label_resolver(labels)
                if resolved is None:
                    state = "unknown"
                    conflict = True
                else:
                    state = resolved
            else:
                state = "unknown"
                conflict = True
        else:
            state = next(iter(labels))
    return state, matched, conflict


def _uncertainty_multi(labels: set[str]) -> str | None:
    if labels == {
        UncertaintyStatus.UNRESOLVED.value,
        UncertaintyStatus.INCONCLUSIVE.value,
    }:
        return UncertaintyStatus.INCONCLUSIVE.value
    if UncertaintyStatus.RESOLVED.value in labels and (
        UncertaintyStatus.UNRESOLVED.value in labels
        or UncertaintyStatus.INCONCLUSIVE.value in labels
    ):
        return None
    return None


def extract_completion_status(text: str) -> tuple[CompletionStatus, tuple[str, ...], bool]:
    hits = _collect_label_hits(_normalize(text), COMPLETION_CUES)
    value, matched, conflict = _resolve_hits(
        hits,
        silence=CompletionStatus.COMPLETION_NOT_ADDRESSED.value,
    )
    return CompletionStatus(value), matched, conflict


def extract_uncertainty_status(text: str) -> tuple[UncertaintyStatus, tuple[str, ...], bool]:
    hits = _collect_label_hits(_normalize(text), UNCERTAINTY_CUES)
    value, matched, conflict = _resolve_hits(
        hits,
        silence=UncertaintyStatus.NOT_EXPRESSED.value,
        multi_label_resolver=_uncertainty_multi,
    )
    # Preregistered tie-break: when both unresolved and inconclusive are operative
    # without a later resolution, prefer inconclusive.
    if hits and not conflict:
        labels_present = {hit.label for hit in hits}
        has_resolved_later = any(
            hit.label == UncertaintyStatus.RESOLVED.value for hit in hits
        )
        # If final resolved state won left-to-right, keep it.
        if value == UncertaintyStatus.RESOLVED.value:
            return UncertaintyStatus(value), matched, conflict
        if (
            UncertaintyStatus.UNRESOLVED.value in labels_present
            and UncertaintyStatus.INCONCLUSIVE.value in labels_present
            and not (
                has_resolved_later
                and value == UncertaintyStatus.RESOLVED.value
            )
        ):
            # Prefer inconclusive unless a later resolved clause is the current value.
            resolved_max = max(
                (
                    hit.clause_index
                    for hit in hits
                    if hit.label == UncertaintyStatus.RESOLVED.value
                ),
                default=-1,
            )
            other_max = max(
                (
                    hit.clause_index
                    for hit in hits
                    if hit.label
                    in {
                        UncertaintyStatus.UNRESOLVED.value,
                        UncertaintyStatus.INCONCLUSIVE.value,
                    }
                ),
                default=-1,
            )
            if resolved_max > other_max:
                value = UncertaintyStatus.RESOLVED.value
            else:
                value = UncertaintyStatus.INCONCLUSIVE.value
    return UncertaintyStatus(value), matched, conflict


def extract_partial_progress_status(
    text: str,
) -> tuple[PartialProgressStatus, tuple[str, ...], bool]:
    hits = _collect_label_hits(_normalize(text), PARTIAL_PROGRESS_CUES)
    value, matched, conflict = _resolve_hits(
        hits,
        silence=PartialProgressStatus.PARTIAL_PROGRESS_NOT_ADDRESSED.value,
    )
    return PartialProgressStatus(value), matched, conflict


def extract_terminal_event_claim_status(
    text: str,
) -> tuple[TerminalEventClaimStatus, tuple[str, ...], bool]:
    hits = _collect_polarity_hits(
        _normalize(text),
        positive_label=TerminalEventClaimStatus.TERMINAL_EVENT_REPORTED.value,
        positive_cues=TERMINAL_EVENT_POSITIVE_CUES,
        negative_label=TerminalEventClaimStatus.NO_TERMINAL_EVENT_REPORTED.value,
        negative_cues=TERMINAL_EVENT_NEGATIVE_CUES,
    )
    # Filter: bare "death_event" as positive only if not part of "no death_event"
    # Negative cues already matched first in collection; still may double-count.
    # Prefer negative if same span region: resolve via later clause.
    value, matched, conflict = _resolve_hits(
        hits,
        silence=TerminalEventClaimStatus.TERMINAL_EVENT_NOT_ADDRESSED.value,
    )
    return TerminalEventClaimStatus(value), matched, conflict


def extract_explicit_failure_status(
    text: str,
) -> tuple[ExplicitFailureStatus, tuple[str, ...], bool]:
    hits = _collect_polarity_hits(
        _normalize(text),
        positive_label=ExplicitFailureStatus.FAILURE_REPORTED.value,
        positive_cues=FAILURE_POSITIVE_CUES,
        negative_label=ExplicitFailureStatus.NO_FAILURE_REPORTED.value,
        negative_cues=FAILURE_NEGATIVE_CUES,
    )
    value, matched, conflict = _resolve_hits(
        hits,
        silence=ExplicitFailureStatus.FAILURE_NOT_ADDRESSED.value,
    )
    return ExplicitFailureStatus(value), matched, conflict


def _cross_field_flags(
    completion: CompletionStatus,
    uncertainty: UncertaintyStatus,
    partial: PartialProgressStatus,
    terminal: TerminalEventClaimStatus,
    failure: ExplicitFailureStatus,
) -> list[str]:
    flags: list[str] = []
    if (
        completion == CompletionStatus.COMPLETED
        and uncertainty
        in {UncertaintyStatus.UNRESOLVED, UncertaintyStatus.INCONCLUSIVE}
    ):
        flags.append("completed_with_unresolved")
    if (
        completion == CompletionStatus.COMPLETED
        and terminal == TerminalEventClaimStatus.TERMINAL_EVENT_REPORTED
    ):
        flags.append("completed_with_terminal_event")
    if (
        completion == CompletionStatus.COMPLETED
        and failure == ExplicitFailureStatus.FAILURE_REPORTED
    ):
        flags.append("completed_with_explicit_failure")
    if (
        partial == PartialProgressStatus.EXPLICIT_PARTIAL_PROGRESS
        and partial == PartialProgressStatus.EXPLICIT_NO_PARTIAL_PROGRESS
    ):
        flags.append("partial_progress_with_no_partial_progress")
    return flags


def extract_structured_report_state_v1(text: str) -> StructuredReportStateV1:
    """Extract all primary structured report-state fields deterministically."""
    completion, completion_cues, completion_conflict = extract_completion_status(text)
    uncertainty, uncertainty_cues, uncertainty_conflict = extract_uncertainty_status(text)
    partial, partial_cues, partial_conflict = extract_partial_progress_status(text)
    terminal, terminal_cues, terminal_conflict = extract_terminal_event_claim_status(text)
    failure, failure_cues, failure_conflict = extract_explicit_failure_status(text)

    flags: list[str] = []
    if completion_conflict:
        flags.append("completion_conflict")
    if uncertainty_conflict:
        flags.append("uncertainty_conflict")
    if partial_conflict:
        flags.append("partial_progress_conflict")
    if terminal_conflict:
        flags.append("terminal_event_conflict")
    if failure_conflict:
        flags.append("explicit_failure_conflict")
    flags.extend(
        _cross_field_flags(completion, uncertainty, partial, terminal, failure)
    )

    matched = {
        "completion_status": completion_cues,
        "uncertainty_status": uncertainty_cues,
        "partial_progress_status": partial_cues,
        "terminal_event_claim_status": terminal_cues,
        "explicit_failure_status": failure_cues,
    }
    # Drop empty fields for stability
    matched = {key: value for key, value in matched.items() if value}

    return StructuredReportStateV1(
        schema_version=STRUCTURED_REPORT_STATE_SCHEMA_V1,
        extractor_version=STRUCTURED_REPORT_STATE_EXTRACTOR_V1,
        completion_status=completion,
        uncertainty_status=uncertainty,
        partial_progress_status=partial,
        terminal_event_claim_status=terminal,
        explicit_failure_status=failure,
        contradiction_flags=tuple(sorted(set(flags))),
        matched_cues_by_field=matched,
    )


class StructuredReportStateCalibrationError(ValueError):
    """Raised when structured report-state calibration fails."""


def load_structured_report_state_golden(
    path: Path = STRUCTURED_REPORT_STATE_GOLDEN_PATH,
) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"structured report-state golden not found: {path}")
    cases: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise StructuredReportStateCalibrationError(
                f"malformed JSONL at line {line_no}: {exc}"
            ) from exc
        cases.append(row)
    return cases


def validate_structured_report_state_golden_records(
    cases: list[dict[str, Any]],
) -> None:
    if not cases:
        raise StructuredReportStateCalibrationError("golden fixture is empty")
    ids: set[str] = set()
    categories: set[str] = set()
    for case in cases:
        keys = set(case)
        if keys != REQUIRED_GOLDEN_FIELDS:
            raise StructuredReportStateCalibrationError(
                f"case {case.get('case_id')!r} has invalid keys: "
                f"extra={keys - REQUIRED_GOLDEN_FIELDS}, "
                f"missing={REQUIRED_GOLDEN_FIELDS - keys}"
            )
        case_id = case["case_id"]
        if case_id in ids:
            raise StructuredReportStateCalibrationError(f"duplicate case_id: {case_id}")
        ids.add(case_id)
        if case["schema_version"] != STRUCTURED_REPORT_STATE_SCHEMA_V1:
            raise StructuredReportStateCalibrationError(
                f"{case_id}: schema_version must be {STRUCTURED_REPORT_STATE_SCHEMA_V1}"
            )
        if case["source_type"] not in ALLOWED_SOURCE_TYPES:
            raise StructuredReportStateCalibrationError(
                f"{case_id}: invalid source_type {case['source_type']!r}"
            )
        categories.add(case["category"])
        try:
            CompletionStatus(case["expected_completion_status"])
            UncertaintyStatus(case["expected_uncertainty_status"])
            PartialProgressStatus(case["expected_partial_progress_status"])
            TerminalEventClaimStatus(case["expected_terminal_event_claim_status"])
            ExplicitFailureStatus(case["expected_explicit_failure_status"])
        except ValueError as exc:
            raise StructuredReportStateCalibrationError(
                f"{case_id}: invalid enum value: {exc}"
            ) from exc
    missing_cats = REQUIRED_CATEGORIES - categories
    if missing_cats:
        raise StructuredReportStateCalibrationError(
            f"missing required categories: {sorted(missing_cats)}"
        )
    if len(cases) < 40:
        raise StructuredReportStateCalibrationError(
            f"expected at least 40 calibration cases, got {len(cases)}"
        )


def run_structured_report_state_calibration(
    path: Path = STRUCTURED_REPORT_STATE_GOLDEN_PATH,
    *,
    expected_sha256: str | None = None,
) -> dict[str, Any]:
    """Run deterministic golden calibration. Optional SHA lock check."""
    if expected_sha256 is not None:
        actual = sha256(path.read_bytes()).hexdigest()
        if actual != expected_sha256:
            raise StructuredReportStateCalibrationError(
                f"SHA mismatch for {path}: expected {expected_sha256}, got {actual}"
            )
    cases = load_structured_report_state_golden(path)
    validate_structured_report_state_golden_records(cases)

    failed: list[str] = []
    field_matches = {
        "completion_status": 0,
        "uncertainty_status": 0,
        "partial_progress_status": 0,
        "terminal_event_claim_status": 0,
        "explicit_failure_status": 0,
    }
    full_matches = 0
    unknown_counts = dict.fromkeys(field_matches, 0)
    contradiction_flag_count = 0
    joint_partial_unresolved: list[str] = []
    silence_vs_negative: list[str] = []

    for case in cases:
        result = extract_structured_report_state_v1(case["report_text"])
        expected = {
            "completion_status": case["expected_completion_status"],
            "uncertainty_status": case["expected_uncertainty_status"],
            "partial_progress_status": case["expected_partial_progress_status"],
            "terminal_event_claim_status": case["expected_terminal_event_claim_status"],
            "explicit_failure_status": case["expected_explicit_failure_status"],
        }
        actual = {
            "completion_status": result.completion_status.value,
            "uncertainty_status": result.uncertainty_status.value,
            "partial_progress_status": result.partial_progress_status.value,
            "terminal_event_claim_status": result.terminal_event_claim_status.value,
            "explicit_failure_status": result.explicit_failure_status.value,
        }
        ok = True
        for key in field_matches:
            if actual[key] == expected[key]:
                field_matches[key] += 1
            else:
                ok = False
            if actual[key] == "unknown":
                unknown_counts[key] += 1
        if ok:
            full_matches += 1
        else:
            failed.append(case["case_id"])
        if result.contradiction_flags:
            contradiction_flag_count += 1
        if (
            result.partial_progress_status
            == PartialProgressStatus.EXPLICIT_PARTIAL_PROGRESS
            and result.uncertainty_status
            in {UncertaintyStatus.UNRESOLVED, UncertaintyStatus.INCONCLUSIVE}
        ):
            joint_partial_unresolved.append(case["case_id"])
        if case["category"] in {
            "no_relevant_claim",
            "negated_failure",
            "negated_unresolved",
        }:
            silence_vs_negative.append(case["case_id"])

    summary = {
        "fixture": str(path),
        "schema_version": STRUCTURED_REPORT_STATE_SCHEMA_V1,
        "extractor_version": STRUCTURED_REPORT_STATE_EXTRACTOR_V1,
        "calibration_identity": STRUCTURED_REPORT_STATE_GOLDEN_V1,
        "total_cases": len(cases),
        "full_state_exact_match": full_matches,
        "failed": len(failed),
        "failed_case_ids": failed,
        "field_exact_matches": field_matches,
        "unknown_counts_by_field": unknown_counts,
        "contradiction_flag_records": contradiction_flag_count,
        "joint_partial_unresolved_case_ids": joint_partial_unresolved,
        "silence_vs_negative_related_case_ids": silence_vs_negative,
        "family_counts": _count_by(cases, "category"),
        "model_api_called": False,
    }
    if failed:
        raise StructuredReportStateCalibrationError(
            f"structured report-state calibration failed: {failed}"
        )
    return summary


def _count_by(cases: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for case in cases:
        value = str(case[key])
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))
