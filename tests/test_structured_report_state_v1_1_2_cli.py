"""Exercise the standalone CLI through its real gate and injected failure stages."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from multi_agent_safety_sim.evaluation import (
    structured_report_state_v1_1_2_calibration as calibration,
)
from multi_agent_safety_sim.evaluation import structured_report_state_v1_1_2_cli as cli
from multi_agent_safety_sim.evaluation.structured_report_state_v1_1_2 import (
    StructuredReportStateV1_1_2,
    extract_structured_report_state_v1_1_2,
)
from multi_agent_safety_sim.evaluation.structured_report_state_v1_1_2_fixture_locks import (
    load_frozen_inputs,
)

ROOT = Path.cwd()
LOCK_PATH = "data/eval_sets/structured_report_state_v1_1_2_architecture_freeze_lock.json"
LOCK = json.loads(Path(LOCK_PATH).read_bytes())
PINNED_PATHS = [
    LOCK_PATH,
    *LOCK["artifact_sha256"],
    *LOCK["protected_source_and_failed_snapshot_sha256"],
]
# Only the explicit frozen inventory is read. No saved runs are enumerated/copied.
PINNED_CONTENT = {name: Path(name).read_bytes() for name in PINNED_PATHS}
MANIFEST = json.loads(
    PINNED_CONTENT["data/eval_sets/structured_report_state_v1_1_2_control_manifest.json"]
)


@pytest.fixture
def isolated_inputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    for name, content in PINNED_CONTENT.items():
        destination = tmp_path / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["structured_report_state_v1_1_2_cli"])
    return tmp_path


def assert_closed(capsys: pytest.CaptureFixture[str]) -> str:
    assert cli.main() == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "calibration failed:" in captured.err
    assert '"full_state_exact_match"' not in captured.err
    return captured.err


def test_cli_positive_module_execution(isolated_inputs: Path) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-m",
            "multi_agent_safety_sim.evaluation.structured_report_state_v1_1_2_cli",
        ],
        cwd=isolated_inputs,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    summary = json.loads(result.stdout)
    assert summary["full_state_exact_match"] == 343
    assert summary["components"]["historical_v1_1_1_repair"]["full_state_exact_match"] == 11
    assert summary["components"]["historical_v1_1_baseline"]["full_state_exact_match"] == 267
    assert summary["model_api_called"] is False
    assert summary["b2_authorized"] is summary["data_collection_authorized"] is False


@pytest.mark.parametrize("name", PINNED_PATHS)
def test_cli_rejects_each_missing_locked_input(
    name: str,
    isolated_inputs: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (isolated_inputs / name).unlink()
    assert_closed(capsys)


@pytest.mark.parametrize("name", PINNED_PATHS)
def test_cli_rejects_each_locked_input_hash_mismatch(
    name: str,
    isolated_inputs: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = isolated_inputs / name
    path.write_bytes(path.read_bytes() + b"\n")
    assert "SHA mismatch" in assert_closed(capsys)


def test_cli_unreadable_input(
    isolated_inputs: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    original = Path.read_bytes

    def unreadable(path: Path) -> bytes:
        if str(path) == "data/eval_sets/structured_report_state_v1_1_1_repair_regression.jsonl":
            raise PermissionError("unreadable repair fixture")
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", unreadable)
    assert "unreadable" in assert_closed(capsys)


@pytest.mark.parametrize("failure", ["malformed", "invalid_record", "coverage", "contrast"])
def test_cli_failures_after_byte_integrity_validation(
    failure: str,
    isolated_inputs: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Verify the authentic inputs first. Inject only in-memory parser/validator
    # failures to exercise downstream layers without adding a public SHA bypass.
    manifest, content = load_frozen_inputs()
    content = content.copy()
    baseline_path = "data/eval_sets/structured_report_state_v1_1_golden.jsonl"
    repair_path = "data/eval_sets/structured_report_state_v1_1_1_repair_regression.jsonl"
    rows = [json.loads(line) for line in content[baseline_path].splitlines()]
    if failure == "malformed":
        content[repair_path] = b"{bad JSON"
    elif failure == "invalid_record":
        repair = [json.loads(line) for line in content[repair_path].splitlines()]
        repair[0]["extra"] = "invalid"
        content[repair_path] = "\n".join(json.dumps(row) for row in repair).encode()
    elif failure == "coverage":
        # Remove all isolated failure-positive witnesses without removing IDs.
        silence = manifest["literal_silence_values"]
        for row in rows:
            if row["expected_explicit_failure_status"] == "failure_reported" and all(
                row["expected_" + field] == value
                for field, value in silence.items()
                if field != "explicit_failure_status"
            ):
                row["expected_uncertainty_status"] = "unresolved"
        # S6 is also an isolated witness in the repair component.
        repair = [json.loads(line) for line in content[repair_path].splitlines()]
        for row in repair:
            if row["case_id"] == "S6":
                row["expected_uncertainty_status"] = "unresolved"
        content[repair_path] = "\n".join(json.dumps(row) for row in repair).encode()
        content[baseline_path] = "\n".join(json.dumps(row) for row in rows).encode()
    else:
        for row in rows:
            if row["case_id"] in ("transition_0_later", "transition_0_control"):
                row["report_text"] = "Opaque narrative with no status."
                row.update(
                    {
                        "expected_" + field: value
                        for field, value in manifest["literal_silence_values"].items()
                    }
                )
        content[baseline_path] = "\n".join(json.dumps(row) for row in rows).encode()

    def injected_inputs() -> tuple[dict[str, Any], dict[str, bytes]]:
        return manifest, content

    def must_not_extract(text: str) -> StructuredReportStateV1_1_2:
        raise AssertionError("extraction before contract validation")

    monkeypatch.setattr(calibration, "load_frozen_inputs", injected_inputs)
    monkeypatch.setattr(calibration, "extract_structured_report_state_v1_1_2", must_not_extract)
    error = assert_closed(capsys)
    assert {
        "malformed": "malformed JSONL",
        "invalid_record": "invalid record keys",
        "coverage": "missing isolated enum",
        "contrast": "semantic contrast oracle",
    }[failure] in error


@pytest.mark.parametrize(
    "failure",
    [
        "schema",
        "extractor",
        "state",
        *[
            "completion_conflict",
            "uncertainty_conflict",
            "partial_progress_conflict",
            "terminal_event_conflict",
            "explicit_failure_conflict",
            "completed_with_unresolved",
            "completed_with_terminal_event",
            "completed_with_explicit_failure",
        ],
    ],
)
def test_cli_rejects_output_identity_state_or_literal_flag_drift(
    failure: str,
    isolated_inputs: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    original = extract_structured_report_state_v1_1_2

    def drift(text: str) -> StructuredReportStateV1_1_2:
        result = original(text)
        if failure == "schema":
            return replace(result, schema_version="structured_report_state_schema_v1_1")
        if failure == "extractor":
            return replace(result, extractor_version="deterministic_report_state_extractor_v1_1")
        if failure == "state":
            # A schema-valid wrong full state, from another approved fixture text.
            return original("Task completed; if failure occurred, notify the operator.")
        return replace(
            result,
            contradiction_flags=tuple(
                "wrong_flag_name" if flag == failure else flag
                for flag in result.contradiction_flags
            ),
        )

    monkeypatch.setattr(calibration, "extract_structured_report_state_v1_1_2", drift)
    error = assert_closed(capsys)
    assert ("identity drift" if failure in ("schema", "extractor") else "mismatch") in error


def test_cli_has_no_fixture_or_lock_bypass(
    isolated_inputs: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "argv", ["cli", "--expected-sha256", "anything"])
    assert cli.main() == 2
    captured = capsys.readouterr()
    assert captured.out == "" and "No fixture, hash bypass" in captured.err


def test_gate_checks_locks_before_any_extraction(
    isolated_inputs: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def must_not_extract(text: str) -> StructuredReportStateV1_1_2:
        raise AssertionError("extraction before SHA validation")

    monkeypatch.setattr(calibration, "extract_structured_report_state_v1_1_2", must_not_extract)
    path = isolated_inputs / "data/eval_sets/structured_report_state_v1_1_1_repair_regression.jsonl"
    path.write_bytes(path.read_bytes() + b"\n")
    assert "SHA mismatch" in assert_closed(capsys)
