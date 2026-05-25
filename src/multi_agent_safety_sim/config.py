"""
Configuration loader with strong validation.

All safety limits and experiment parameters come from here.
Never bypass this module for ad-hoc values.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, model_validator


class SafetyConfig(BaseModel):
    max_tokens_per_run: int = Field(120_000, ge=1_000)
    max_steps: int = Field(300, ge=1, le=10_000)
    max_wall_time_seconds: int = 3600
    max_agents: int = Field(12, ge=1, le=50)
    max_messages_per_agent_per_step: int = 5
    strict_mode: bool = True
    kill_on_safety_event: bool = True


class LLMRetryConfig(BaseModel):
    max_attempts: int = 3
    backoff_factor: float = 1.8


class LLMConfig(BaseModel):
    default_provider: Literal["openai", "anthropic", "ollama", "litellm"] = "openai"
    default_model: str = "gpt-4o-mini"
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens_per_call: int = Field(800, ge=64, le=8192)
    timeout_seconds: int = 45
    retry: LLMRetryConfig = Field(default_factory=LLMRetryConfig)


class AgentPersona(BaseModel):
    name: str
    constitution: list[str] = Field(..., min_length=1)
    system_prompt_version: str = "v1.0"


class LoggingConfig(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    json_logs: bool = True
    save_full_transcripts: bool = True
    save_safety_events: bool = True
    output_dir: str = "runs/"


class SimConfig(BaseModel):
    """Root validated configuration object."""

    project: dict[str, Any]
    safety: SafetyConfig
    seed: int = 42
    deterministic: bool = True
    llm: LLMConfig = Field(default_factory=LLMConfig)
    agent_personas: dict[str, AgentPersona]
    default_scenario: str
    scenarios: dict[str, dict[str, Any]]
    alignment: dict[str, Any]
    logging: LoggingConfig

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def validate_scenario_exists(self) -> SimConfig:
        if self.default_scenario not in self.scenarios:
            raise ValueError(f"default_scenario '{self.default_scenario}' not defined in scenarios")
        return self


def load_config(path: str | Path = "config.yaml") -> SimConfig:
    """Load and validate config.yaml. Raises on any safety misconfiguration."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}. Copy config.yaml.example if needed.")

    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    cfg = SimConfig(**raw)
    return cfg


# Convenience for CLI / tests
def get_default_config() -> SimConfig:
    return load_config(Path(__file__).parent.parent.parent.parent / "config.yaml")
