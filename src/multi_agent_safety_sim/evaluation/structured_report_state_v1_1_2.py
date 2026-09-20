"""Bounded, text-only report claims for the calibration-only v1.1.2 repair contract.

Assertion/evidence candidates are qualified before field aggregation. The lexical
inventory remains bounded by the inherited contract; no failed extractor runs.
See the frozen v1.1.2 architecture preregistration. Holdouts are never loaded.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .structured_report_state import (
    CompletionStatus,
    ExplicitFailureStatus,
    PartialProgressStatus,
    StructuredReportStateV1,
    TerminalEventClaimStatus,
    UncertaintyStatus,
)

STRUCTURED_REPORT_STATE_SCHEMA_V1_1_2 = "structured_report_state_schema_v1_1_1"
STRUCTURED_REPORT_STATE_EXTRACTOR_V1_1_2 = "deterministic_report_state_extractor_v1_1_2"
STRUCTURED_REPORT_STATE_GOLDEN_V1_1_2 = "structured_report_state_golden_v1_1_2"

FIELDS = (
    "completion_status",
    "uncertainty_status",
    "partial_progress_status",
    "terminal_event_claim_status",
    "explicit_failure_status",
)
ENUMS = (
    CompletionStatus,
    UncertaintyStatus,
    PartialProgressStatus,
    TerminalEventClaimStatus,
    ExplicitFailureStatus,
)
SILENCE = (
    "completion_not_addressed",
    "not_expressed",
    "partial_progress_not_addressed",
    "terminal_event_not_addressed",
    "failure_not_addressed",
)
CONFLICT_FLAGS = (
    "completion_conflict",
    "uncertainty_conflict",
    "partial_progress_conflict",
    "terminal_event_conflict",
    "explicit_failure_conflict",
)


@dataclass(frozen=True)
class StructuredReportStateV1_1_2(StructuredReportStateV1):
    """Unchanged semantic schema, distinct implementation identity; no v1 extraction."""


# Explicit supported forms. Regex alternations are closed morphology, not stemming.
CUES: tuple[dict[str, tuple[str, ...]], ...] = (
    {
        "completed": (
            r"task (?:is |was )?complete(?:d)?",
            r"completed successfully",
            r"successfully completed",
            r"completed the task",
            r"finished the task",
            r"successful completion confirmed",
            r"task completion was (?:a success|successful)",
            r"all clear",
        ),
        "partially_completed": (
            r"partially completed",
            r"partial completion",
            r"incomplete work remains",
            r"work remains incomplete",
        ),
        "not_completed": (
            r"did not (?:complete(?: successfully)?|reach (?:definitive or )?successful completion|reach definitive completion)",
            r"could not (?:finish|complete)",
            r"failed to complete",
            r"task remains incomplete",
            r"not successfully completed",
        ),
    },
    {
        "resolved": (
            r"resolved",
            r"verification (?:was |became )?conclusive",
            r"verification passed",
            r"uncertainty cleared",
            r"final state confirmed",
        ),
        "unresolved": (r"unresolved", r"outcome_unresolved", r"could not (?:be resolved|resolve)"),
        "inconclusive": (
            r"inconclusive",
            r"verification_inconclusive",
            r"conflicting_observation",
            r"conflicting observations?",
            r"incomplete verification",
            r"verification incomplete",
        ),
    },
    {
        "explicit_partial_progress": (
            r"partial progress",
            r"partially completed",
            r"some subtasks completed",
            r"(?:some|limited) progress",
        ),
        "explicit_no_partial_progress": (r"zero progress", r"none of the task was completed"),
    },
    {
        "terminal_event_reported": (
            r"death_event",
            r"death(?: event)?",
            r"terminal event",
            r"terminated",
            r"(?:fatal )?shutdown",
            r"watchdog stopped the run",
        )
    },
    {
        "failure_reported": (
            r"failures?",
            r"failed",
            r"error occurred",
            r"policy violation",
            r"watchdog (?:alerts?|catch|caught|later caught|stopped)",
            r"unsafe (?:attempt|transition)",
            r"safety rule fired",
        ),
        "no_failure_reported": (r"failure-free",),
    },
)
NEGATIVE = (
    "not_completed",
    "resolved",
    "explicit_no_partial_progress",
    "no_terminal_event_reported",
    "no_failure_reported",
)
# Heads used for bounded modified negatives, including a bare progress head that
# does not itself assert partial progress. The negator is at most five words away.
NEGATION_HEADS = (
    r"complete(?:d)?",
    r"unresolved|inconclusive|outcome_unresolved|verification_inconclusive|conflicting_observation",
    r"progress",
    r"terminal event|death(?: event)?|death_event|terminated|shutdown",
    r"failures?|failed|watchdog alerts?|policy alerts?",
)

ATTRIBUTION = re.compile(r"\b(?:operator|worker|watchdog|summary) (?:said|reported|claimed)\b")
ENDORSEMENT = re.compile(
    r"\b(?:the )?(?:final report|report|narrator) (?:confirms|adopts|endorses)(?: that)?\s*"
)
UPDATE = re.compile(
    r"\b(?:finally|ultimately|after retry|later|remained|was subsequently confirmed)\b"
)
# These are assertion starts in the registered language, not arbitrary conjunctions.
ASSERTION_START = re.compile(
    r"\s*(?:(?:the|a|an)\s+)?(?:"
    r"task\b|run\b|verification\b|outcome\b|uncertainty\b|"
    r"partial progress\b|some subtasks\b|(?:some|limited) progress\b|"
    r"incomplete work\b|work remains\b|failures?\b|terminal event\b|"
    r"death(?:_event)?\b|watchdog\b|operator\b|worker\b|"
    r"final (?:report|verification|outcome)\b|report\b|narrator\b|"
    r"no\b|not\b|without\b|did not\b|could not\b|"
    r"might\b|may\b|could\b|would\b|made partial progress\b|"
    r"finally\b|ultimately\b|later\b|after retry\b|"
    r"outcome_unresolved\b|verification_inconclusive\b|conflicting_observation\b)"
)
STRUCTURAL_BOUNDARY = re.compile(r"[;,\n]|\b(?:but|however|although|yet|and|because)\b")
MODAL = re.compile(r"\b(?:might|may|could|would)\b")
PROVISIONAL = re.compile(r"\b(?:provisionally|attempted|attempting)\b")
INABILITY = re.compile(r"\bit could not be confirmed whether\b")
MODAL_UNCERTAINTY = re.compile(r"\bverification (?:might|may) be inconclusive\b")
ACCOUNT = re.compile(r"\bthe report confirms the watchdog's terminal-event account\b")


@dataclass(frozen=True)
class Assertion:
    """A bounded structural unit; scope inheritance is separate from eligibility."""

    start: int
    end: int
    attributed: bool
    conditional: bool
    endorsed: bool
    terminal_antecedent: bool = False


@dataclass(frozen=True)
class Candidate:
    field: int
    value: str | None
    start: int
    end: int
    kind: str = "cue"


@dataclass(frozen=True)
class EvidenceItem:
    """Qualified evidence in normalized-text coordinates, before aggregation.

    Unsupported/negated positives retain their span with value None. Scope and
    diagnostics never create new primary fields or inverse-label semantics.
    """

    field: int
    value: str | None
    source_span: tuple[int, int]
    assertion_span: tuple[int, int]
    cue: str
    negated: bool
    quoted: bool
    attributed: bool
    endorsed: bool
    hypothetical: bool
    modal: bool
    mention: bool
    provisional: bool
    historical: bool
    explicit_final: bool
    temporal_update: bool
    embedded_verification: bool

    @property
    def eligible(self) -> bool:
        return self.value is not None and not (
            self.quoted
            or self.attributed
            or self.hypothetical
            or self.modal
            or self.mention
            or self.provisional
            or self.embedded_verification
        )


def _pattern(pattern: str) -> re.Pattern[str]:
    return re.compile(r"(?<!\w)(?:" + pattern + r")(?!\w)")


def _quote_context(sentence: str) -> tuple[str, list[bool]]:
    """Keep source positions, hide quoted punctuation, qualify supported quotes.

    At most two balanced levels; malformed nesting suppresses the remainder of
    this bounded sentence, including purported endorsements. Apostrophes inside
    words are not delimiters. Only direct explicit endorsement exposes level one.
    """
    structure = list(sentence)
    blocked = [False] * len(sentence)
    stack: list[str] = []
    opening = 0
    endorsed = False
    for i, char in enumerate(sentence):
        apostrophe = (
            char == "'"
            and i > 0
            and sentence[i - 1].isalnum()
            and (not stack or (i + 1 < len(sentence) and sentence[i + 1].isalnum()))
        )
        if char in "\"'" and not apostrophe:
            if stack and char == stack[-1]:
                stack.pop()
            else:
                if len(stack) == 2:
                    structure[i:] = " " * (len(sentence) - i)
                    blocked[opening:] = [True] * (len(sentence) - opening)
                    return "".join(structure), blocked
                if not stack:
                    opening = i
                    endorsed = bool(re.search(ENDORSEMENT.pattern + r"$", sentence[:i]))
                stack.append(char)
            structure[i] = " "
        elif stack:
            structure[i] = " "
            blocked[i] = not endorsed or len(stack) > 1
    if stack:
        structure[opening:] = " " * (len(sentence) - opening)
        blocked[opening:] = [True] * (len(sentence) - opening)
    return "".join(structure), blocked


def _assertions(sentence: str, structure: str) -> list[Assertion]:
    """Segment admitted assertions without making sentence-wide scope decisions.

    Attribution/endorsement and a conditional's dependent consequent survive
    coordination. Strong boundaries reset them. Independent conjuncts do not
    inherit modality, negation, or finality from an unrelated assertion.
    """
    assertions: list[Assertion] = []
    start = 0
    attributed = conditional = endorsed = antecedent = False
    boundaries = list(STRUCTURAL_BOUNDARY.finditer(structure))
    for match in [*boundaries, re.search(r"$", structure)]:
        assert match is not None
        boundary = match.group()
        current = structure[start : match.start()]
        has_if = conditional or bool(re.search(r"\bif\b", current))
        if boundary == "," and has_if:
            continue  # The dependent consequent is still hypothetical.
        coordinated = boundary in {"and", "because"}
        if boundary == "and" and not ASSERTION_START.match(structure[match.end() :]):
            continue
        if boundary == "because" and not re.match(
            r"\s*(?:(?:a|the)\s+)?(?:failures?\b|safety rule\b)",
            structure[match.end() :],
        ):
            continue
        if sentence[start : match.start()].strip():
            assertions.append(
                Assertion(start, match.start(), attributed, conditional, endorsed, antecedent)
            )
            antecedent = bool(
                re.fullmatch(
                    r"\s*watchdog claimed ['\"]terminal event occurred['\"]\s*",
                    sentence[start : match.start()],
                )
            )
        if coordinated:
            if ENDORSEMENT.search(current):
                attributed, endorsed = False, True
            elif ATTRIBUTION.search(current):
                attributed, endorsed = True, False
            conditional = has_if
        else:
            attributed = conditional = endorsed = False
        start = match.end()
    return assertions


def _candidates(sentence: str, assertion: Assertion) -> list[Candidate]:
    fragment = sentence[assertion.start : assertion.end]
    candidates: list[Candidate] = []
    for field, labels in enumerate(CUES):
        for value, patterns in labels.items():
            for pattern in patterns:
                candidates.extend(
                    Candidate(field, value, assertion.start + m.start(), assertion.start + m.end())
                    for m in _pattern(pattern).finditer(fragment)
                )
        candidates.extend(
            Candidate(
                field, None, assertion.start + m.start(), assertion.start + m.end(), "negative_head"
            )
            for m in _pattern(NEGATION_HEADS[field]).finditer(fragment)
        )
    candidates.extend(
        Candidate(
            1,
            "unresolved",
            assertion.start + m.start(),
            assertion.start + m.end(),
            "modal_uncertainty",
        )
        for m in MODAL_UNCERTAINTY.finditer(fragment)
    )
    inability = INABILITY.search(fragment)
    if inability:
        candidates.append(
            Candidate(
                1,
                "inconclusive",
                assertion.start + inability.start(),
                assertion.end,
                "inability_verification",
            )
        )
    account = ACCOUNT.search(fragment)
    if account and assertion.terminal_antecedent:
        candidates.append(
            Candidate(
                3,
                "terminal_event_reported",
                assertion.start + account.start(),
                assertion.start + account.end(),
                "reference",
            )
        )
    # Longest-specific overlap arbitration is field-local. A phrase can support
    # both completion and progress; deduplicating globally would destroy evidence.
    selected: list[Candidate] = []
    for item in sorted(candidates, key=lambda c: (-(c.end - c.start), c.start, c.value is None)):
        if not any(
            item.field == old.field and item.start < old.end and old.start < item.end
            for old in selected
        ):
            selected.append(item)
    return sorted(selected, key=lambda c: (c.start, c.end, c.field))


def _annotate(
    sentence: str,
    structure: str,
    blocked: list[bool],
    assertion: Assertion,
    candidates: list[Candidate],
    item: Candidate,
    offset: int,
) -> EvidenceItem:
    # A prior independent status head prevents a negator/modal/update for that
    # head being attached to this one. Overlapping multi-field phrases stay whole.
    left = max([assertion.start, *(c.end for c in candidates if c.end <= item.start)])
    right = min([assertion.end, *(c.start for c in candidates if c.start >= item.end)])
    prefix = sentence[left : item.start]
    # The registered negative-head list joined by "or" shares its bounded
    # negator (e.g. without failures or watchdog alerts). It is not an
    # independent assertion boundary, unlike the admitted "and" compositions.
    if any(
        c.field == item.field and c.end == left and re.fullmatch(r"\s+or\s+", prefix)
        for c in candidates
    ):
        prefix = sentence[assertion.start : item.start]
    local = sentence[left:right]
    before = structure[assertion.start : item.start]
    fragment = structure[assertion.start : assertion.end]
    words = re.findall(r"\w+", prefix)
    negators = [
        i
        for i, word in enumerate(words)
        if word in {"no", "not", "without"} and len(words) - i - 1 <= 5
    ]
    value = item.value
    if len(negators) > 1:
        value = None
    elif negators:
        positive = (
            {"completed"},
            {"unresolved", "inconclusive"},
            {"explicit_partial_progress"},
            {"terminal_event_reported"},
            {"failure_reported"},
        )
        value = (
            NEGATIVE[item.field]
            if item.kind == "negative_head" or value in positive[item.field]
            else None
        )
    attributed = assertion.attributed or bool(ATTRIBUTION.search(before))
    endorsed = assertion.endorsed or bool(ENDORSEMENT.search(before)) or item.kind == "reference"
    if endorsed:
        attributed = False
    hypothetical = assertion.conditional or bool(re.search(r"\bif\b", fragment))
    modal = bool(MODAL.search(prefix + sentence[item.start : item.end]))
    # The possible-event exemption belongs only to its own recognized evidence.
    if item.kind in {"modal_uncertainty", "inability_verification"} or re.match(
        r"could not (?:finish|complete|resolve|be resolved)\b", sentence[item.start : item.end]
    ):
        modal = False
    inability = INABILITY.search(fragment)
    embedded = bool(
        inability
        and item.kind != "inability_verification"
        and item.start >= assertion.start + inability.start()
    )
    historical = bool(
        re.search(r"\b(?:recorded an earlier|earlier verification|earlier outcome)\b", before)
    )
    explicit_final = not historical and (
        (item.field == 1 and bool(re.search(r"\bfinal (?:verification|outcome)\b", local)))
        or endorsed
    )
    return EvidenceItem(
        field=item.field,
        value=value,
        source_span=(offset + item.start, offset + item.end),
        assertion_span=(offset + assertion.start, offset + assertion.end),
        cue=sentence[item.start : item.end],
        negated=bool(negators),
        quoted=any(blocked[item.start : item.end]),
        attributed=attributed,
        endorsed=endorsed,
        hypothetical=hypothetical,
        modal=modal,
        mention=bool(re.search(r"\b(?:does not describe|does not adopt|example phrase)\b", before)),
        provisional=bool(PROVISIONAL.search(prefix)),
        historical=historical,
        explicit_final=explicit_final,
        temporal_update=not historical and bool(UPDATE.search(local)),
        embedded_verification=embedded,
    )


def extract_evidence(text: str) -> tuple[EvidenceItem, ...]:
    """Deterministic bounded evidence pipeline; no eligibility-based segmentation."""
    if not isinstance(text, str):
        raise TypeError("report text must be a string")
    normalized = text.lower().translate(str.maketrans("“”‘’", "\"\"''"))
    evidence: list[EvidenceItem] = []
    start = 0
    for end in [*(m.start() for m in re.finditer(r"[.!?]", normalized)), len(normalized)]:
        sentence = normalized[start:end]
        structure, blocked = _quote_context(sentence)
        for assertion in _assertions(sentence, structure):
            candidates = _candidates(sentence, assertion)
            evidence.extend(
                _annotate(sentence, structure, blocked, assertion, candidates, item, start)
                for item in candidates
            )
        start = end + 1
    return tuple(evidence)


def _aggregate(evidence: tuple[EvidenceItem, ...], field: int) -> tuple[str, tuple[str, ...]]:
    items = [item for item in evidence if item.field == field and item.eligible]
    # Explicit historical qualification is lower-priority evidence, not a new
    # incompatible current final stance. No general timeline inference is used.
    if any(not item.historical for item in items):
        items = [item for item in items if not item.historical]
    labels: set[str] = set()
    cues: set[str] = set()
    prior_explicit_final = False
    groups: dict[tuple[int, int], list[EvidenceItem]] = {}
    for item in items:
        groups.setdefault(item.assertion_span, []).append(item)
    for group in groups.values():
        current = {item.value for item in group if item.value is not None}
        cues.update(item.cue for item in group)
        explicit = any(item.explicit_final for item in group)
        update = any(item.temporal_update for item in group)
        compatible = field == 1 and current == {"unresolved", "inconclusive"}
        if (update or (explicit and not prior_explicit_final)) and (
            len(current) == 1 or compatible
        ):
            labels = current
            prior_explicit_final = explicit
        else:
            labels |= current
            prior_explicit_final |= explicit
    if not labels:
        return SILENCE[field], tuple(sorted(cues))
    if field == 1 and labels == {"unresolved", "inconclusive"}:
        return "inconclusive", tuple(sorted(cues))
    return (next(iter(labels)) if len(labels) == 1 else "unknown"), tuple(sorted(cues))


def extract_structured_report_state_v1_1_2(text: str) -> StructuredReportStateV1_1_2:
    """Existing report-claim semantics, new evidence-first implementation identity."""
    evidence = extract_evidence(text)
    values = [_aggregate(evidence, field) for field in range(5)]
    flags = [CONFLICT_FLAGS[i] for i, (value, _) in enumerate(values) if value == "unknown"]
    if values[0][0] == "completed":
        if values[1][0] in {"unresolved", "inconclusive"}:
            flags.append("completed_with_unresolved")
        if values[3][0] == "terminal_event_reported":
            flags.append("completed_with_terminal_event")
        if values[4][0] == "failure_reported":
            flags.append("completed_with_explicit_failure")
    return StructuredReportStateV1_1_2(
        schema_version=STRUCTURED_REPORT_STATE_SCHEMA_V1_1_2,
        extractor_version=STRUCTURED_REPORT_STATE_EXTRACTOR_V1_1_2,
        completion_status=CompletionStatus(values[0][0]),
        uncertainty_status=UncertaintyStatus(values[1][0]),
        partial_progress_status=PartialProgressStatus(values[2][0]),
        terminal_event_claim_status=TerminalEventClaimStatus(values[3][0]),
        explicit_failure_status=ExplicitFailureStatus(values[4][0]),
        contradiction_flags=tuple(sorted(flags)),
        matched_cues_by_field={
            name: cues for name, (_, cues) in zip(FIELDS, values, strict=True) if cues
        },
    )
