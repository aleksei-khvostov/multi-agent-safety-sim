"""Safety-critical config validation tests."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
import yaml

from multi_agent_safety_sim.config import load_config


def test_load_config_rejects_unknown_scenario() -> None:
    bad = {
        "project": {"name": "test"},
        "safety": {"max_steps": 10},
        "seed": 1,
        "llm": {},
        "agent_personas": {
            "test": {"name": "t", "constitution": ["be good"], "system_prompt_version": "v1"}
        },
        "default_scenario": "nonexistent",
        "scenarios": {"other": {}},
        "alignment": {},
        "logging": {},
    }
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "bad.yaml"
        p.write_text(yaml.dump(bad))
        with pytest.raises(ValueError, match="not defined"):
            load_config(p)
