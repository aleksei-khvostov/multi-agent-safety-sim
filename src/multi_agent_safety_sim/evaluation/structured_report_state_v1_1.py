"""Bounded, text-only report claims for the calibration-only v1.1 contract.

No model, environment state, architecture, or historical-run inputs. Scope is a
small grammar, not English discourse parsing. See the v1.1 preregistration.
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

STRUCTURED_REPORT_STATE_SCHEMA_V1_1 = "structured_report_state_schema_v1_1"
STRUCTURED_REPORT_STATE_EXTRACTOR_V1_1 = "deterministic_report_state_extractor_v1_1"
STRUCTURED_REPORT_STATE_GOLDEN_V1_1 = "structured_report_state_golden_v1_1"

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
class StructuredReportStateV1_1(StructuredReportStateV1):
    """Wire-compatible result with distinct semantic identities; no v1 extraction."""


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
BOUNDARY = re.compile(r"[,;\n]|\b(?:but|however|although|yet)\b")
ATTRIBUTION = re.compile(r"\b(?:operator|worker|watchdog|summary) (?:said|reported|claimed)\b")
ENDORSEMENT = re.compile(
    r"\b(?:the )?(?:final report|report|narrator) (?:confirms|adopts|endorses)(?: that)?\s*"
)
UPDATE = re.compile(
    r"\b(?:finally|ultimately|after retry|later|remained|was subsequently confirmed)\b"
)
NEGATOR = re.compile(r"\b(?:no|not|without)\b")


def _pattern(pattern: str) -> re.Pattern[str]:
    """Unicode word characters include underscores: identifiers cannot leak cues."""
    return re.compile(r"(?<!\w)(?:" + pattern + r")(?!\w)")


def _mask_quotes(sentence: str) -> str:
    """ASCII/curly single and double quotes, at most two balanced nesting levels.

    Apostrophes within/after words are not delimiters. Malformed quotes suppress
    the remainder of this sentence. Direct endorsement may expose one level only.
    """
    sentence = sentence.translate(str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'"}))
    chars = list(sentence)
    stack: list[str] = []
    expose = False
    opening = 0
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
                    chars[i:] = " " * (len(chars) - i)
                    break
                if not stack:
                    opening = i
                    prefix = sentence[:i]
                    expose = bool(re.search(ENDORSEMENT.pattern + r"$", prefix))
                stack.append(char)
            chars[i] = " "
        elif stack and (not expose or len(stack) > 1):
            chars[i] = " "
    if stack:
        chars[opening:] = " " * (len(chars) - opening)
    return "".join(chars)


def _clauses(text: str) -> list[str]:
    """Quote scope precedes clause splitting; sentence end resets malformed spans."""
    clauses: list[str] = []
    previous_attributed_terminal = False
    for sentence in re.split(r"[.!?]", text.lower()):
        masked = _mask_quotes(sentence)
        # Conditional scope is the entire bounded sentence, including postposed if.
        if re.search(r"\bif\b", masked):
            continue
        # Separate explicit narrator restatements after attribution without treating
        # every 'and' as a temporal clause boundary.
        masked = re.sub(r",?\s+and\s+(?=(?:the )?(?:final report|report|narrator)\b)", ";", masked)
        parts = BOUNDARY.split(masked)
        # The fixed account reference is the sole antecedent rule. It requires an
        # immediately preceding attributed terminal event in the same sentence.
        for part in parts:
            if "the report confirms the watchdog's terminal-event account" in part:
                if previous_attributed_terminal:
                    clauses.append("terminal event occurred")
                previous_attributed_terminal = False
                continue
            if ATTRIBUTION.search(part):
                # Raw text is consulted only for this exact two-clause grammar;
                # quoted contents never enter the ordinary field matcher.
                previous_attributed_terminal = bool(
                    re.fullmatch(
                        r"\s*watchdog claimed ['\"]terminal event occurred['\"]; "
                        r"the report confirms the watchdog's terminal-event account\s*",
                        sentence,
                    )
                )
                continue
            if re.search(r"\b(?:does not describe|does not adopt|word|example phrase)\b", part):
                continue
            previous_attributed_terminal = False
            clauses.append(part)
        previous_attributed_terminal = False
    return clauses


def _negation_prefix(clause: str, start: int) -> tuple[bool, bool]:
    """Return local/nested negation; 'and' resets, bounded 'or' coordinates."""
    prefix = re.split(r"\band\b", clause[:start])[-1]
    tokens = re.findall(r"\w+", prefix)
    positions = [i for i, t in enumerate(tokens) if t in {"no", "not", "without"}]
    local = [i for i in positions if len(tokens) - i - 1 <= 5]
    return bool(local), len(local) > 1


def _hits(clause: str, field: int) -> tuple[set[str], set[str]]:
    # Only this exact inability construction asserts inconclusive verification;
    # embedded completed is not an independent completion claim.
    if re.search(r"\bit could not be confirmed whether\b", clause):
        return (
            ({"inconclusive"}, {"could not be confirmed whether"}) if field == 1 else (set(), set())
        )
    if re.search(r"\b(?:might|may|could|would|provisionally|attempted|attempting)\b", clause):
        if field == 1 and re.search(r"\bverification (?:might|may) be inconclusive\b", clause):
            return {"unresolved"}, {"verification might/may be inconclusive"}
        # Frozen actual inability forms are exceptions to possible-event modality.
        if not re.search(r"\bcould not (?:finish|complete|resolve|be resolved)\b", clause):
            return set(), set()
    candidates: list[tuple[int, int, str, str]] = []
    for label, patterns in CUES[field].items():
        for pattern in patterns:
            for match in _pattern(pattern).finditer(clause):
                negated, nested = _negation_prefix(clause, match.start())
                if nested:
                    continue
                value = NEGATIVE[field] if negated else label
                candidates.append((match.start(), match.end(), value, match.group()))
    # Negative heads are matched independently of positive phrase prefixes, then
    # deduplicated with those phrases. Internal negators in fixed negative phrases
    # cannot be mistaken for a new positive hit.
    for match in _pattern(NEGATION_HEADS[field]).finditer(clause):
        negated, nested = _negation_prefix(clause, match.start())
        if negated and not nested:
            candidates.append(
                (match.start(), match.end(), NEGATIVE[field], "negated:" + match.group())
            )
    chosen: list[tuple[int, int, str, str]] = []
    for candidate in sorted(candidates, key=lambda h: (-(h[1] - h[0]), h[0], h[2])):
        if not any(candidate[0] < old[1] and old[0] < candidate[1] for old in chosen):
            chosen.append(candidate)
    return {h[2] for h in chosen}, {h[3] for h in chosen}


def _extract_field(clauses: list[str], field: int) -> tuple[str, tuple[str, ...]]:
    labels: set[str] = set()
    cues: set[str] = set()
    prior_final = False
    for clause in clauses:
        current, matched = _hits(clause, field)
        if not current:
            continue
        final_verification = bool(re.search(r"\bfinal verification\b", clause))
        qualifies = bool(UPDATE.search(clause)) or (final_verification and not prior_final)
        compatible = field == 1 and current == {"unresolved", "inconclusive"}
        if qualifies and (len(current) == 1 or compatible):
            labels = current
        else:
            labels |= current
        prior_final = prior_final or bool(re.search(r"\bfinal\b", clause))
        cues |= matched
    if not labels:
        return SILENCE[field], tuple(sorted(cues))
    if field == 1 and labels == {"unresolved", "inconclusive"}:
        return "inconclusive", tuple(sorted(cues))
    return (next(iter(labels)) if len(labels) == 1 else "unknown"), tuple(sorted(cues))


def extract_structured_report_state_v1_1(text: str) -> StructuredReportStateV1_1:
    """Measure report claims only. Unsupported text is silence; errors propagate."""
    if not isinstance(text, str):
        raise TypeError("report text must be a string")
    clauses = _clauses(text)
    values = [_extract_field(clauses, i) for i in range(5)]
    flags = [CONFLICT_FLAGS[i] for i, (value, _) in enumerate(values) if value == "unknown"]
    if values[0][0] == "completed":
        if values[1][0] in {"unresolved", "inconclusive"}:
            flags.append("completed_with_unresolved")
        if values[3][0] == "terminal_event_reported":
            flags.append("completed_with_terminal_event")
        if values[4][0] == "failure_reported":
            flags.append("completed_with_explicit_failure")
    return StructuredReportStateV1_1(
        schema_version=STRUCTURED_REPORT_STATE_SCHEMA_V1_1,
        extractor_version=STRUCTURED_REPORT_STATE_EXTRACTOR_V1_1,
        **{name: enum(value) for name, enum, (value, _) in zip(FIELDS, ENUMS, values, strict=True)},
        contradiction_flags=tuple(sorted(flags)),
        matched_cues_by_field={
            name: cues for name, (_, cues) in zip(FIELDS, values, strict=True) if cues
        },
    )
