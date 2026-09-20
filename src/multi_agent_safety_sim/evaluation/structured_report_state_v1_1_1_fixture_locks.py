"""Independent frozen-input locks for the bounded v1.1.1 successor only."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from .fixture_locks import FixtureLockError

STRUCTURED_REPORT_STATE_V1_1_1_REPAIR_REGRESSION_PATH = Path(
    "data/eval_sets/structured_report_state_v1_1_1_repair_regression.jsonl"
)
STRUCTURED_REPORT_STATE_V1_1_1_REPAIR_REGRESSION_SHA256 = (
    "9e27f8a32f38d1c089f212297bfeeca0478b8ba61c0bd93c516ec4d8909c05f9"
)
STRUCTURED_REPORT_STATE_V1_1_1_CALIBRATION_MANIFEST_PATH = Path(
    "data/eval_sets/structured_report_state_v1_1_1_calibration_manifest.json"
)
STRUCTURED_REPORT_STATE_V1_1_1_CALIBRATION_MANIFEST_SHA256 = (
    "6751c6063df17089c0469fa87f1620a025ee1a49149d621197ccb1d281345f7f"
)
STRUCTURED_REPORT_STATE_V1_1_1_FREEZE_LOCK_PATH = Path(
    "data/eval_sets/structured_report_state_v1_1_1_freeze_lock.json"
)
STRUCTURED_REPORT_STATE_V1_1_1_FREEZE_LOCK_SHA256 = (
    "7cdc9d0e9faf2a9cb5ed803e4757672faf1c6dacde479cf4c620a483048b9c55"
)
STRUCTURED_REPORT_STATE_V1_1_BASELINE_PATH = Path(
    "data/eval_sets/structured_report_state_v1_1_golden.jsonl"
)
STRUCTURED_REPORT_STATE_V1_1_BASELINE_SHA256 = (
    "533e26a35913904b419fd33ecf1b445a84e6a3b5da51ec33dc43efc2ecd07ec5"
)
STRUCTURED_REPORT_STATE_V1_1_BASELINE_CASE_COUNT = 267
STRUCTURED_REPORT_STATE_V1_1_1_REPAIR_CASE_COUNT = 11


def _read_locked(path: Path, expected: str) -> bytes:
    data = path.read_bytes()
    actual = sha256(data).hexdigest()
    if actual != expected:
        raise FixtureLockError(f"SHA mismatch for {path}: expected {expected}, got {actual}")
    return data


def load_frozen_inputs() -> tuple[dict[str, Any], dict[str, bytes]]:
    """Check all freeze/preservation hashes before parsing fixtures or extraction.

    No public path/hash override. Use these exact checked bytes for calibration,
    rather than reopening files after verification. The lock itself is externally
    pinned here; it cannot authorize its own changed contents.
    """
    lock = json.loads(
        _read_locked(
            STRUCTURED_REPORT_STATE_V1_1_1_FREEZE_LOCK_PATH,
            STRUCTURED_REPORT_STATE_V1_1_1_FREEZE_LOCK_SHA256,
        )
    )
    if lock["implementation_repair_authorized"] is not True:
        raise FixtureLockError("bounded implementation was not authorized")
    content = {
        name: _read_locked(Path(name), expected)
        for group in ("artifact_sha256", "failed_snapshot_and_historical_sha256")
        for name, expected in lock[group].items()
    }
    # Independent declarations must agree with the pre-implementation inventory.
    for path, expected in (
        (
            STRUCTURED_REPORT_STATE_V1_1_1_REPAIR_REGRESSION_PATH,
            STRUCTURED_REPORT_STATE_V1_1_1_REPAIR_REGRESSION_SHA256,
        ),
        (
            STRUCTURED_REPORT_STATE_V1_1_1_CALIBRATION_MANIFEST_PATH,
            STRUCTURED_REPORT_STATE_V1_1_1_CALIBRATION_MANIFEST_SHA256,
        ),
        (STRUCTURED_REPORT_STATE_V1_1_BASELINE_PATH, STRUCTURED_REPORT_STATE_V1_1_BASELINE_SHA256),
    ):
        if sha256(content[str(path)]).hexdigest() != expected:
            raise FixtureLockError(f"independent registry identity drift: {path}")
    manifest: dict[str, Any] = json.loads(
        content[str(STRUCTURED_REPORT_STATE_V1_1_1_CALIBRATION_MANIFEST_PATH)]
    )
    for section in ("preregistration", "predecessor", "repair_regression", "audit"):
        reference = manifest[section]
        if sha256(content[reference["path"]]).hexdigest() != reference["sha256"]:
            raise FixtureLockError(f"manifest reference drift: {section}")
    return manifest, content
