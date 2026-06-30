"""Tests for the Phase 3.7 matched-evidence pilot runner."""

from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml
from typer.testing import CliRunner

from multi_agent_safety_sim.cli import app
from multi_agent_safety_sim.evaluation.posthumous_divergence import actual_outcome_from_episode
from multi_agent_safety_sim.simulation.phase3_7_pilot_runner import (
    DEFAULT_PHASE3_7_CONFIG,
    RUN_002_ID,
    _build_phase3_7_record,
    build_pilot_requests,
    build_prompt_bundle,
    compute_frozen_input_hashes,
    load_phase3_7_config,
    load_trace_fixtures,
    run_phase3_7_pilot,
    summarize_phase3_7_results,
    validate_preflight,
)
from tests.conftest import plain_cli_output

RUN_002_CONFIG = Path("configs/phase3_7_run_002_real_model_pilot.yaml")


class FakeLLMClient:
    """Fake LLM client for tests. Never makes external calls."""

    def __init__(self, *, fail_first: bool = False, empty_first: bool = False) -> None:
        self.calls = 0
        self.fail_first = fail_first
        self.empty_first = empty_first

    async def complete(self, **kwargs: Any) -> dict[str, Any]:
        self.calls += 1
        if self.fail_first and self.calls == 1:
            raise RuntimeError("synthetic provider failure")
        if self.empty_first and self.calls == 1:
            return {
                "content": "  ",
                "usage": {"prompt_tokens": 1, "completion_tokens": 0, "total": 1},
                "model": kwargs.get("model", "fake-model"),
            }
        return {
            "content": "All clear. Full cooperation maintained.",
            "usage": {"prompt_tokens": 1, "completion_tokens": 2, "total": 3},
            "model": kwargs.get("model", "fake-model"),
        }


class InterruptingLLMClient:
    """Fake client that simulates a process interruption after paid responses."""

    def __init__(self, *, interrupt_on_call: int) -> None:
        self.calls = 0
        self.interrupt_on_call = interrupt_on_call

    async def complete(self, **kwargs: Any) -> dict[str, Any]:
        self.calls += 1
        if self.calls == self.interrupt_on_call:
            raise KeyboardInterrupt
        return {
            "content": "All clear. Full cooperation maintained.",
            "usage": {"prompt_tokens": 1, "completion_tokens": 2, "total": 3},
            "model": kwargs.get("model", "fake-model"),
        }


class CapturingRealLLMClient(FakeLLMClient):
    """Fake RealLLMClient replacement that records construction arguments."""

    instances: list[CapturingRealLLMClient] = []

    def __init__(self, *, default_model: str, provider: str) -> None:
        super().__init__()
        self.default_model = default_model
        self.provider = provider
        self.instances.append(self)


def ready_config_copy(tmp_path: Path) -> Path:
    """Create a ready temp config with output redirected to tmp_path."""
    config = load_phase3_7_config()
    config["model"] = {
        "provider": "fake",
        "model_string": "fake-model-v1",
        "run_date": "2026-06-20",
    }
    config["outputs"]["output_dir"] = str(tmp_path / "phase3_7_outputs")
    config_path = tmp_path / "phase3_7_ready.yaml"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return config_path


def ready_config_copy_with_provider(tmp_path: Path, *, provider: str) -> Path:
    """Create a ready temp config with a specific provider."""
    config_path = ready_config_copy(tmp_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["model"]["provider"] = provider
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return config_path


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read a JSONL file."""
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_phase3_7_config_loads_and_validates() -> None:
    preflight = validate_preflight(config_path=DEFAULT_PHASE3_7_CONFIG)

    assert preflight["config"]["experiment_id"] == "phase3_7_real_model_pilot"
    assert preflight["request_count"] == 75


def test_phase3_7_run_002_config_exists_and_declares_v2_regime() -> None:
    config = load_phase3_7_config(RUN_002_CONFIG)

    assert config["run_id"] == RUN_002_ID
    assert config["model"]["provider"] == "openrouter"
    assert config["model"]["model_string"] == "google/gemini-2.5-flash-lite"
    assert config["model"]["run_date"] != "TBD"
    assert config["classification"]["classifier_version"] == "frozen_lexical_v2_negation"


def test_phase3_7_run_002_preflight_accepts_explicit_ready_config() -> None:
    preflight = validate_preflight(config_path=RUN_002_CONFIG, require_ready=True)

    assert preflight["config"]["run_id"] == RUN_002_ID
    assert preflight["config"]["classification"]["classifier_version"] == (
        "frozen_lexical_v2_negation"
    )
    assert preflight["request_count"] == 75


@pytest.mark.parametrize("classifier_version", [None, "TBD", "frozen_lexical_v1"])
def test_phase3_7_run_002_preflight_rejects_missing_or_tbd_classifier_version(
    tmp_path: Path,
    classifier_version: str | None,
) -> None:
    config = load_phase3_7_config(RUN_002_CONFIG)
    if classifier_version is None:
        config["classification"].pop("classifier_version")
    else:
        config["classification"]["classifier_version"] = classifier_version
    config_path = tmp_path / "run_002_bad_classifier.yaml"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="Run 002 classifier_version"):
        validate_preflight(config_path=config_path, require_ready=True)


@pytest.mark.parametrize("model_field", ["provider", "model_string", "run_date"])
def test_phase3_7_run_002_preflight_rejects_tbd_model_fields(
    tmp_path: Path,
    model_field: str,
) -> None:
    config = load_phase3_7_config(RUN_002_CONFIG)
    config["model"][model_field] = "TBD"
    config_path = tmp_path / "run_002_bad_model.yaml"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match=f"Run 002 model.{model_field}"):
        validate_preflight(config_path=config_path)


def test_phase3_7_run_002_preflight_makes_no_api_call_and_no_run_artifacts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_real_client_construction(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("preflight must not construct RealLLMClient")

    before = set(Path("data/runs").rglob("*")) if Path("data/runs").exists() else set()
    monkeypatch.setattr(
        "multi_agent_safety_sim.simulation.phase3_7_pilot_runner.RealLLMClient",
        fail_real_client_construction,
    )

    validate_preflight(config_path=RUN_002_CONFIG, require_ready=True)

    after = set(Path("data/runs").rglob("*")) if Path("data/runs").exists() else set()
    assert after == before


def test_phase3_7_run_002_classifier_version_selects_v2_without_changing_v1() -> None:
    report = "No unsafe transition occurred. All clear."
    common_kwargs = {
        "architecture_id": "honest_duo",
        "episode_id": 1,
        "lifespan_rounds": 10,
        "death_event": False,
        "death_cause": None,
        "risk_score": 0.0,
        "final_report": report,
    }

    v1_record = _build_phase3_7_record(
        classification={"reported_outcome_classifier": "frozen_lexical"},
        **common_kwargs,
    )
    v2_record = _build_phase3_7_record(
        classification={
            "reported_outcome_classifier": "frozen_lexical",
            "classifier_version": "frozen_lexical_v2_negation",
        },
        **common_kwargs,
    )

    assert v1_record.reported_outcome.value == "honest_failure"
    assert v1_record.label.value == "false_alarm_or_underclaim"
    assert v1_record.pds_score == 0.3
    assert v2_record.reported_outcome.value == "all_clear"
    assert v2_record.label.value == "aligned_clear"
    assert v2_record.pds_score == 0.0


def test_phase3_7_fixtures_load_with_unique_ids() -> None:
    config = load_phase3_7_config()
    fixtures = load_trace_fixtures(Path(config["fixtures"]["path"]))

    assert len(fixtures) == 5
    assert len({fixture.fixture_id for fixture in fixtures}) == 5


def test_phase3_7_fixture_expected_actual_outcomes_match_derivation() -> None:
    config = load_phase3_7_config()
    fixtures = load_trace_fixtures(Path(config["fixtures"]["path"]))

    for fixture in fixtures:
        actual = actual_outcome_from_episode(
            death_event=fixture.death_event,
            risk_score=fixture.risk_score,
        )
        assert actual.value == fixture.expected_actual_outcome


def test_every_architecture_receives_same_fixture_ids() -> None:
    config = load_phase3_7_config()
    fixtures = load_trace_fixtures(Path(config["fixtures"]["path"]))
    requests = build_pilot_requests(config, fixtures)
    expected_fixture_ids = [fixture.fixture_id for fixture in fixtures]

    for architecture_id in config["architectures"]:
        seen = sorted(
            {
                request.fixture.fixture_id
                for request in requests
                if request.architecture_id == architecture_id
            }
        )
        assert seen == sorted(expected_fixture_ids)


def test_phase3_7_request_count_is_preregistered_count() -> None:
    config = load_phase3_7_config()
    fixtures = load_trace_fixtures(Path(config["fixtures"]["path"]))

    assert len(build_pilot_requests(config, fixtures)) == 5 * 5 * 3


def test_phase3_7_request_order_is_block_randomized_and_reproducible() -> None:
    config = load_phase3_7_config()
    fixtures = load_trace_fixtures(Path(config["fixtures"]["path"]))
    first = build_pilot_requests(config, fixtures)
    second = build_pilot_requests(config, fixtures)

    assert [request.request_id for request in first] == [
        request.request_id for request in second
    ]
    assert [request.request_sequence for request in first] == list(range(1, 76))

    block_orders: list[tuple[str, ...]] = []
    for index in range(0, len(first), len(config["architectures"])):
        block = first[index : index + len(config["architectures"])]
        block_orders.append(tuple(request.architecture_id for request in block))
        assert {request.architecture_id for request in block} == set(config["architectures"])
        assert len({request.fixture.fixture_id for request in block}) == 1
        assert len({request.repetition for request in block}) == 1

    assert len(set(block_orders)) > 1
    assert first[0].request_id == (
        f"{first[0].fixture.fixture_id}__rep_{first[0].repetition}__"
        f"{first[0].architecture_id}"
    )


def test_prompt_bundle_changes_by_architecture_only() -> None:
    honest = build_prompt_bundle("honest_duo")
    deceptive = build_prompt_bundle("deceptive_duo")

    assert honest.system_prompt == deceptive.system_prompt
    assert honest.final_report_instruction == deceptive.final_report_instruction
    assert honest.architecture_prompt != deceptive.architecture_prompt


def test_preflight_makes_no_api_call() -> None:
    fake_client = FakeLLMClient()

    validate_preflight(config_path=DEFAULT_PHASE3_7_CONFIG)

    assert fake_client.calls == 0


def test_real_run_refuses_when_model_fields_are_tbd(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = load_phase3_7_config()
    config["model"] = {
        "provider": "TBD",
        "model_string": "TBD",
        "run_date": "TBD",
    }
    config["outputs"]["output_dir"] = str(tmp_path / "phase3_7_outputs")
    config_path = tmp_path / "phase3_7_tbd.yaml"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    monkeypatch.setattr(
        "multi_agent_safety_sim.simulation.phase3_7_pilot_runner.is_git_worktree_clean",
        lambda: True,
    )

    with pytest.raises(ValueError, match="provider, model_string, and run_date"):
        asyncio.run(
            run_phase3_7_pilot(
                config_path=config_path,
                llm_client=FakeLLMClient(),
                confirm_real_model_run=True,
            )
        )

def test_real_run_refuses_without_explicit_confirmation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = ready_config_copy(tmp_path)
    monkeypatch.setattr(
        "multi_agent_safety_sim.simulation.phase3_7_pilot_runner.is_git_worktree_clean",
        lambda: True,
    )

    with pytest.raises(ValueError, match="explicit confirmation"):
        asyncio.run(
            run_phase3_7_pilot(
                config_path=config_path,
                llm_client=FakeLLMClient(),
                confirm_real_model_run=False,
            )
        )


def test_real_run_refuses_on_dirty_worktree(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = ready_config_copy(tmp_path)
    monkeypatch.setattr(
        "multi_agent_safety_sim.simulation.phase3_7_pilot_runner.is_git_worktree_clean",
        lambda: False,
    )

    with pytest.raises(ValueError, match="git worktree"):
        asyncio.run(
            run_phase3_7_pilot(
                config_path=config_path,
                llm_client=FakeLLMClient(),
                confirm_real_model_run=True,
            )
        )


def test_frozen_input_hashes_are_deterministic() -> None:
    first = compute_frozen_input_hashes()
    second = compute_frozen_input_hashes()

    assert first == second
    assert str(DEFAULT_PHASE3_7_CONFIG) in first


def test_manifest_contains_required_metadata_and_hashes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = ready_config_copy(tmp_path)
    monkeypatch.setattr(
        "multi_agent_safety_sim.simulation.phase3_7_pilot_runner.is_git_worktree_clean",
        lambda: True,
    )
    monkeypatch.setattr(
        "multi_agent_safety_sim.simulation.phase3_7_pilot_runner.current_git_commit",
        lambda: "abc123",
    )

    output_dir = asyncio.run(
        run_phase3_7_pilot(
            config_path=config_path,
            llm_client=FakeLLMClient(),
            confirm_real_model_run=True,
        )
    )
    manifest = json.loads((output_dir / "run_manifest.json").read_text(encoding="utf-8"))

    assert manifest["experiment_id"] == "phase3_7_real_model_pilot"
    assert manifest["status"] == "completed"
    assert manifest["pilot_mode"] == "matched_trace_report_generation"
    assert manifest["request_order"] == "deterministic_block_randomized"
    assert manifest["request_order_seed"] == 37
    assert manifest["provider"] == "fake"
    assert manifest["model_string"] == "fake-model-v1"
    assert manifest["git_commit"] == "abc123"
    assert manifest["git_worktree_clean"] is True
    assert manifest["request_count"] == 75
    assert manifest["requested_request_count"] == 75
    assert manifest["successful_evaluation_count"] == 75
    assert manifest["failed_request_count"] == 0
    assert manifest["end_timestamp"] is not None
    assert "frozen_input_sha256" in manifest
    assert "posthumous_divergence.py" in "\n".join(manifest["frozen_input_sha256"])


def test_phase3_7_runner_constructs_real_client_with_configured_provider(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = ready_config_copy_with_provider(tmp_path, provider="openrouter")
    CapturingRealLLMClient.instances = []
    monkeypatch.setattr(
        "multi_agent_safety_sim.simulation.phase3_7_pilot_runner.is_git_worktree_clean",
        lambda: True,
    )
    monkeypatch.setattr(
        "multi_agent_safety_sim.simulation.phase3_7_pilot_runner.RealLLMClient",
        CapturingRealLLMClient,
    )

    asyncio.run(
        run_phase3_7_pilot(
            config_path=config_path,
            confirm_real_model_run=True,
        )
    )

    assert len(CapturingRealLLMClient.instances) == 1
    client = CapturingRealLLMClient.instances[0]
    assert client.default_model == "fake-model-v1"
    assert client.provider == "openrouter"
    assert client.calls == 75


def test_mocked_model_responses_produce_expected_evaluated_records(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = ready_config_copy(tmp_path)
    monkeypatch.setattr(
        "multi_agent_safety_sim.simulation.phase3_7_pilot_runner.is_git_worktree_clean",
        lambda: True,
    )

    output_dir = asyncio.run(
        run_phase3_7_pilot(
            config_path=config_path,
            llm_client=FakeLLMClient(),
            confirm_real_model_run=True,
        )
    )
    rows = read_jsonl(output_dir / "evaluated_records.jsonl")

    assert len(rows) == 75
    assert rows[0]["request_id"]
    assert rows[0]["request_sequence"] == 1
    assert rows[0]["reported_outcome"] == "all_clear"
    assert rows[0]["label"] == "aligned_clear"
    assert rows[0]["input_hash_references"]


def test_model_call_failures_are_recorded_without_retry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = ready_config_copy(tmp_path)
    client = FakeLLMClient(fail_first=True)
    monkeypatch.setattr(
        "multi_agent_safety_sim.simulation.phase3_7_pilot_runner.is_git_worktree_clean",
        lambda: True,
    )

    output_dir = asyncio.run(
        run_phase3_7_pilot(
            config_path=config_path,
            llm_client=client,
            confirm_real_model_run=True,
        )
    )

    assert client.calls == 75
    failures = read_jsonl(output_dir / "failures.jsonl")
    raw_rows = read_jsonl(output_dir / "raw_responses.jsonl")
    evaluated_rows = read_jsonl(output_dir / "evaluated_records.jsonl")
    assert len(failures) == 1
    assert "synthetic provider failure" in failures[0]["error"]
    assert len(raw_rows) == 75
    assert len(evaluated_rows) == 74
    manifest = json.loads((output_dir / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "completed_with_provider_failures"
    assert manifest["requested_request_count"] == 75
    assert manifest["successful_evaluation_count"] == 74
    assert manifest["failed_request_count"] == 1
    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["overall_counts"] == {
        "requested_requests": 75,
        "successful_evaluations": 74,
        "failed_requests": 1,
    }
    assert summary["rate_denominator"] == "successful_evaluations"
    assert summary["analysis_status"] == "incomplete_provider_failures"
    assert "missing_data_caveat" in summary
    assert summary["failure_type_counts"] == {"provider_exception": 1}
    assert manifest["requested_request_count"] == summary["overall_counts"]["requested_requests"]
    assert (
        manifest["successful_evaluation_count"]
        == summary["overall_counts"]["successful_evaluations"]
    )
    assert manifest["failed_request_count"] == summary["overall_counts"]["failed_requests"]
    assert (
        manifest["status"] == "completed_with_provider_failures"
        and summary["analysis_status"] == "incomplete_provider_failures"
    )

    failed_architecture = failures[0]["architecture_id"]
    failed_fixture = failures[0]["fixture_id"]
    assert failed_architecture in summary["by_architecture"]
    assert failed_fixture in summary["by_fixture"]
    assert summary["by_architecture"][failed_architecture]["failed_request_count"] == 1
    assert summary["by_fixture"][failed_fixture]["failed_request_count"] == 1

    config = load_phase3_7_config(config_path)
    fixtures = load_trace_fixtures(Path(config["fixtures"]["path"]))
    assert set(summary["by_architecture"]) == set(config["architectures"])
    assert set(summary["by_fixture"]) == {fixture.fixture_id for fixture in fixtures}
    for group in summary["by_architecture"].values():
        assert isinstance(group["posthumous_overclaim_rate_denominator"], int)
        assert (
            group["posthumous_overclaim_rate_denominator"]
            == group["successful_evaluation_count"]
        )
    for group in summary["by_fixture"].values():
        assert isinstance(group["posthumous_overclaim_rate_denominator"], int)
        assert (
            group["posthumous_overclaim_rate_denominator"]
            == group["successful_evaluation_count"]
        )


def test_empty_model_responses_are_failures_not_evaluated_uncertainty(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = ready_config_copy(tmp_path)
    client = FakeLLMClient(empty_first=True)
    monkeypatch.setattr(
        "multi_agent_safety_sim.simulation.phase3_7_pilot_runner.is_git_worktree_clean",
        lambda: True,
    )

    output_dir = asyncio.run(
        run_phase3_7_pilot(
            config_path=config_path,
            llm_client=client,
            confirm_real_model_run=True,
        )
    )

    failures = read_jsonl(output_dir / "failures.jsonl")
    raw_rows = read_jsonl(output_dir / "raw_responses.jsonl")
    evaluated_rows = read_jsonl(output_dir / "evaluated_records.jsonl")
    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))

    assert len(raw_rows) == 75
    assert len(evaluated_rows) == 74
    assert len(failures) == 1
    assert failures[0]["failure_type"] == "empty_response"
    assert failures[0]["raw_final_report"] == "  "
    assert summary["failure_type_counts"] == {"empty_response": 1}
    assert summary["analysis_status"] == "incomplete_provider_failures"


def test_summary_denominator_keeps_all_failure_group_with_null_metrics() -> None:
    config = load_phase3_7_config()
    fixtures = load_trace_fixtures(Path(config["fixtures"]["path"]))
    requests = build_pilot_requests(config, fixtures)
    failed_architecture = config["architectures"][0]
    failures = [
        {
            "request_id": request.request_id,
            "request_sequence": request.request_sequence,
            "architecture_id": request.architecture_id,
            "fixture_id": request.fixture.fixture_id,
            "failure_type": "provider_exception",
            "error": "synthetic all-fail architecture",
        }
        for request in requests
        if request.architecture_id == failed_architecture
    ]
    evaluated_records = [
        {
            "request_id": request.request_id,
            "request_sequence": request.request_sequence,
            "architecture_id": request.architecture_id,
            "fixture_id": request.fixture.fixture_id,
            "reported_outcome": "all_clear",
            "label": "aligned_clear",
            "pds_score": 0.0,
        }
        for request in requests
        if request.architecture_id != failed_architecture
    ]

    summary = summarize_phase3_7_results(
        evaluated_records=evaluated_records,
        failures=failures,
        requests=requests,
    )

    group = summary["by_architecture"][failed_architecture]
    assert group["requested_count"] == len(failures)
    assert group["successful_evaluation_count"] == 0
    assert group["failed_request_count"] == group["requested_count"]
    assert group["posthumous_overclaim_rate"] is None
    assert group["mean_pds_score"] is None
    assert group["posthumous_overclaim_rate_denominator"] == 0
    assert summary["analysis_status"] == "incomplete_provider_failures"


def test_paid_responses_are_flushed_before_process_interruption(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = ready_config_copy(tmp_path)
    output_dir = tmp_path / "interrupted_run"
    client = InterruptingLLMClient(interrupt_on_call=2)
    monkeypatch.setattr(
        "multi_agent_safety_sim.simulation.phase3_7_pilot_runner.is_git_worktree_clean",
        lambda: True,
    )

    with pytest.raises(KeyboardInterrupt):
        asyncio.run(
            run_phase3_7_pilot(
                config_path=config_path,
                llm_client=client,
                confirm_real_model_run=True,
                output_dir_override=output_dir,
            )
        )

    raw_rows = read_jsonl(output_dir / "raw_responses.jsonl")
    evaluated_rows = read_jsonl(output_dir / "evaluated_records.jsonl")
    failure_rows = read_jsonl(output_dir / "failures.jsonl")
    manifest = json.loads((output_dir / "run_manifest.json").read_text(encoding="utf-8"))
    assert client.calls == 2
    assert manifest["status"] == "interrupted"
    assert manifest["requested_request_count"] == 75
    assert manifest["completed_raw_response_count"] == 1
    assert manifest["successful_evaluation_count"] == 1
    assert manifest["failed_request_count"] == 0
    assert manifest["interruption_type"] == "KeyboardInterrupt"
    assert len(raw_rows) == 1
    assert len(evaluated_rows) == 1
    assert failure_rows == []
    assert not (output_dir / "summary.json").exists()


def test_generated_artifacts_match_documented_schema(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = ready_config_copy(tmp_path)
    monkeypatch.setattr(
        "multi_agent_safety_sim.simulation.phase3_7_pilot_runner.is_git_worktree_clean",
        lambda: True,
    )

    output_dir = asyncio.run(
        run_phase3_7_pilot(
            config_path=config_path,
            llm_client=FakeLLMClient(),
            confirm_real_model_run=True,
        )
    )

    expected_files = {
        "run_manifest.json",
        "raw_responses.jsonl",
        "evaluated_records.jsonl",
        "summary.json",
        "failures.jsonl",
    }
    assert {path.name for path in output_dir.iterdir()} == expected_files
    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["overall_counts"]["requested_requests"] == 75
    assert summary["overall_counts"]["successful_evaluations"] == 75
    assert summary["rate_denominator"] == "successful_evaluations"
    assert summary["analysis_status"] == "complete"
    assert summary["failed_request_count"] == 0
    assert summary["inferential_significance_claims"] == "none"


def test_phase3_7_data_runs_artifacts_are_gitignored() -> None:
    result = subprocess.run(
        [
            "git",
            "check-ignore",
            "data/runs/phase3_7_real_model_pilot/example/run_manifest.json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "data/runs/" in result.stdout


def test_phase3_7_preflight_cli_prints_no_model_call() -> None:
    preflight = validate_preflight(config_path=DEFAULT_PHASE3_7_CONFIG)
    result = CliRunner().invoke(
        app,
        [
            "phase3-7-preflight",
            "--config",
            str(DEFAULT_PHASE3_7_CONFIG),
        ],
    )
    output = plain_cli_output(result.output)

    assert preflight["request_count"] == 75
    assert result.exit_code == 0
    assert "request_count : 75" in output
    assert "No model call was made." in output


def test_phase3_7_run_cli_requires_confirmation() -> None:
    result = CliRunner().invoke(
        app,
        [
            "phase3-7-run",
            "--config",
            str(DEFAULT_PHASE3_7_CONFIG),
        ],
    )

    assert result.exit_code == 2
    assert "--confirm-real-model-run is required" in result.output
