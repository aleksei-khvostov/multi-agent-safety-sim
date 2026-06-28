"""Frozen fixture SHA locks for report-integrity measurement gates."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

NDB_20_FIXTURE_PATH = Path("data/eval_sets/ndb_20_nested_delegation.jsonl")
NDB_20_FIXTURE_SHA256 = (
    "0d34a69c05f08b4a46f3495698f402087fc2302c3ac03e8cdc824a1cc66179db"
)

RIB_16_FIXTURE_PATH = Path("data/eval_sets/rib_16_report_integrity.jsonl")
RIB_16_FIXTURE_SHA256 = (
    "256651e0e62cd4c5b9b3ded6ecd85a5233017e590bfa16d9135eec2335925baa"
)

STATE_REPORT_GOLDEN_PATH = Path("data/eval_sets/state_report_divergence_golden.jsonl")
STATE_REPORT_GOLDEN_SHA256 = (
    "94f427400d25e3599b0d04817f8f529273fcfaafdf2ed684226359118a194d82"
)

GRAVESTONE_GOLDEN_PATH = Path("data/fixtures/gravestone_golden/")


class FixtureLockError(ValueError):
    """Raised when a frozen fixture SHA does not match the lock."""


@dataclass(frozen=True)
class FrozenFixtureLock:
    """Metadata for one frozen report-integrity fixture."""

    name: str
    path: str
    case_count: int | None
    sha256: str | None
    status: str
    what_it_tests: str
    primary_rates: str
    diagnostic_fields: str
    ci_gate: bool


FROZEN_FIXTURE_LOCKS: tuple[FrozenFixtureLock, ...] = (
    FrozenFixtureLock(
        name="state_report_divergence_golden",
        path=str(STATE_REPORT_GOLDEN_PATH),
        case_count=11,
        sha256=STATE_REPORT_GOLDEN_SHA256,
        status="frozen",
        what_it_tests="Single-layer state/report mismatch (Phase 3 evaluator)",
        primary_rates="pass_rate, detection_rate, false_positive_rate (pytest)",
        diagnostic_fields="none",
        ci_gate=False,
    ),
    FrozenFixtureLock(
        name="rib_16_report_integrity",
        path=str(RIB_16_FIXTURE_PATH),
        case_count=16,
        sha256=RIB_16_FIXTURE_SHA256,
        status="frozen",
        what_it_tests="Cemetery evidence vs final report (Death vs Divergence scorer)",
        primary_rates="posthumous_overclaim_rate, report_integrity_divergence_rate",
        diagnostic_fields="none",
        ci_gate=True,
    ),
    FrozenFixtureLock(
        name="gravestone_golden",
        path=str(GRAVESTONE_GOLDEN_PATH),
        case_count=4,
        sha256=None,
        status="frozen",
        what_it_tests="Gravestone analyzer on cemetery-style artifacts",
        primary_rates="posthumous_overclaim_rate, report_integrity_divergence_rate",
        diagnostic_fields="legacy_field_note",
        ci_gate=True,
    ),
    FrozenFixtureLock(
        name="ndb_20_nested_delegation",
        path=str(NDB_20_FIXTURE_PATH),
        case_count=20,
        sha256=NDB_20_FIXTURE_SHA256,
        status="frozen",
        what_it_tests="Nested delegation consolidation vs rollup evidence",
        primary_rates=(
            "nested_report_integrity_divergence_rate, "
            "consolidation_overclaim_rate, consolidation_underclaim_rate"
        ),
        diagnostic_fields="watchdog_fp_on_nested_ambiguity, watchdog_flag_matches_expected",
        ci_gate=True,
    ),
)


def sha256_file(path: Path) -> str:
    """Return SHA-256 hex digest for a file."""
    return sha256(path.read_bytes()).hexdigest()


def assert_fixture_sha256(path: Path, expected_sha256: str, *, fixture_name: str) -> None:
    """Raise FixtureLockError when fixture bytes drift from the frozen lock."""
    if not path.exists():
        raise FileNotFoundError(f"{fixture_name} fixture file not found: {path}")

    actual = sha256_file(path)
    if actual != expected_sha256:
        raise FixtureLockError(
            f"{fixture_name} fixture SHA mismatch at {path}: "
            f"expected {expected_sha256}, got {actual}"
        )