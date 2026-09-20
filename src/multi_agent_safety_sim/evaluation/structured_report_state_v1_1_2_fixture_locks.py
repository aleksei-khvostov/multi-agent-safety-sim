"""Literal locks for builder-visible v1.1.2 inputs; never opens the sealed holdout."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from .fixture_locks import FixtureLockError

ARCHITECTURE_LOCK_PATH = Path(
    "data/eval_sets/structured_report_state_v1_1_2_architecture_freeze_lock.json"
)
ARCHITECTURE_LOCK_SHA256 = "bc4ad0fa79833ac074f1cddaa24edbb508d00ffd503ec0f70af25028dc803c70"
CONTROL_MANIFEST_PATH = Path("data/eval_sets/structured_report_state_v1_1_2_control_manifest.json")
CONTROL_MANIFEST_SHA256 = "722ed3db447e96d614b1c6a1130b27dc8e355c3f9c77dd44b67310f83863bbb2"
ARCHITECTURE_CONTROLS_SHA256 = "4473d9a8ccbd4fb2952751b78b8211040dd5837ae7901d579e60e49d4f6a27a8"
DISCLOSED_REGRESSION_SHA256 = "dd287f1d3296242fa2a0cf22cca9140c394e0036ba53746965d90778618254a1"
# Only these active documents received authorized post-freeze governance updates.
# Their original hashes remain provenance in the unchanged architecture lock.
HISTORICAL_STATUS_PATHS = frozenset(
    {"README.md", "docs/CURRENT_RESEARCH_STATE.md", "docs/MEASUREMENT_GATES.md"}
)


def _read_locked(path: Path, expected: str) -> bytes:
    content = path.read_bytes()
    if sha256(content).hexdigest() != expected:
        raise FixtureLockError(f"SHA mismatch for {path}")
    return content


def load_frozen_inputs() -> tuple[dict[str, Any], dict[str, bytes]]:
    """Check the frozen graph before parsing any fixture or running extraction.

    The architecture lock's historical statements and hashes are not rewritten.
    Authorized active-status updates are not frozen measurement inputs: require
    those documents to remain readable, but do not return their current bytes as
    hash-verified content. The exception applies only to their provenance entries,
    never to measurement artifacts or manifest references. This loader has no
    caller-provided override and never enumerates files or opens a holdout artifact.
    """
    lock = json.loads(_read_locked(ARCHITECTURE_LOCK_PATH, ARCHITECTURE_LOCK_SHA256))
    content: dict[str, bytes] = {}
    for group in ("artifact_sha256", "protected_source_and_failed_snapshot_sha256"):
        for path, digest in lock[group].items():
            if (
                group == "protected_source_and_failed_snapshot_sha256"
                and path in HISTORICAL_STATUS_PATHS
            ):
                Path(path).read_bytes()
                continue
            content[path] = _read_locked(Path(path), digest)
    if sha256(content[str(CONTROL_MANIFEST_PATH)]).hexdigest() != CONTROL_MANIFEST_SHA256:
        raise FixtureLockError("control manifest identity drift")
    manifest: dict[str, Any] = json.loads(content[str(CONTROL_MANIFEST_PATH)])
    for path, digest in manifest["artifact_sha256"].items():
        if path not in content or sha256(content[path]).hexdigest() != digest:
            raise FixtureLockError(f"manifest reference drift: {path}")
    for component in manifest["input_components"]:
        if sha256(content[component["path"]]).hexdigest() != component["sha256"]:
            raise FixtureLockError("input component reference drift")
    for basename, digest in (
        ("architecture_controls", ARCHITECTURE_CONTROLS_SHA256),
        ("disclosed_regression", DISCLOSED_REGRESSION_SHA256),
    ):
        path = f"data/eval_sets/structured_report_state_v1_1_2_{basename}.jsonl"
        if sha256(content[path]).hexdigest() != digest:
            raise FixtureLockError(f"independent disclosed-input lock drift: {path}")
    # Also retain every predecessor freeze edge, including its original meanings.
    old_lock = json.loads(content[manifest["inherited_contract"]["freeze_lock_path"]])
    for group in ("artifact_sha256", "failed_snapshot_and_historical_sha256"):
        for path, digest in old_lock[group].items():
            if path not in content or sha256(content[path]).hexdigest() != digest:
                raise FixtureLockError(f"historical preservation mismatch: {path}")
    return manifest, content
