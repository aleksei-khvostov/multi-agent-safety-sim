"""Tests for frozen Phase 3.7 real-model pilot inputs."""

from __future__ import annotations

from pathlib import Path

import yaml

CONFIG_PATH = Path("configs/phase3_7_real_model_pilot.yaml")
PROMPT_DIR = Path("prompts/phase3_7")
CALIBRATION_PATH = Path("data/eval_sets/reported_outcome_classifier_golden.jsonl")

EXPECTED_ARCHITECTURES = [
    "honest_duo",
    "deceptive_duo",
    "deceptive_watchdog",
    "power_duo",
    "power_watchdog",
]

EXPECTED_PROMPTS = [
    "system_base.md",
    "honest_duo.md",
    "deceptive_duo.md",
    "deceptive_watchdog.md",
    "power_duo.md",
    "power_watchdog.md",
    "final_report_instruction.md",
]

FORBIDDEN_DIRECT_OUTCOME_INSTRUCTIONS = [
    "must overclaim",
    "must lie",
    "always say all clear",
    "always report success",
    "hide the failure",
]


def load_config() -> dict[str, object]:
    """Load the frozen Phase 3.7 config."""
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def test_phase3_7_config_exists_and_parses() -> None:
    config = load_config()

    assert CONFIG_PATH.exists()
    assert config["experiment_id"] == "phase3_7_real_model_pilot"
    assert config["status"] == "frozen_inputs_pre_data"
    assert config["variant"] == "predictive_validity_persona_conditioned_labels"


def test_phase3_7_config_has_expected_architectures() -> None:
    config = load_config()

    assert config["architectures"] == EXPECTED_ARCHITECTURES


def test_phase3_7_prompt_files_exist_and_are_non_empty() -> None:
    for filename in EXPECTED_PROMPTS:
        prompt_path = PROMPT_DIR / filename
        assert prompt_path.exists()
        assert prompt_path.read_text(encoding="utf-8").strip()


def test_phase3_7_prompts_do_not_force_direct_outcomes() -> None:
    for filename in EXPECTED_PROMPTS:
        prompt_text = (PROMPT_DIR / filename).read_text(encoding="utf-8").lower()
        for forbidden in FORBIDDEN_DIRECT_OUTCOME_INSTRUCTIONS:
            assert forbidden not in prompt_text


def test_phase3_7_config_freezes_architecture_blind_classifier() -> None:
    config = load_config()
    classification = config["classification"]

    assert classification["reported_outcome_classifier"] == "frozen_lexical"
    assert classification["architecture_blind"] is True
    assert classification["classifier_modified_after_model_outputs"] is False


def test_phase3_7_config_references_existing_calibration_set() -> None:
    config = load_config()
    classification = config["classification"]

    assert classification["calibration_set"] == str(CALIBRATION_PATH)
    assert CALIBRATION_PATH.exists()
