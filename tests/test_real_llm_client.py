"""Tests for real LLM provider selection. These tests make no API calls."""

from __future__ import annotations

import pytest

from multi_agent_safety_sim.utils.llm import RealLLMClient

PROVIDER_ENV_VARS = [
    "XAI_API_KEY",
    "OPENROUTER_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
]


def clear_provider_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove provider API keys for deterministic client construction tests."""
    for env_var in PROVIDER_ENV_VARS:
        monkeypatch.delenv(env_var, raising=False)


def test_explicit_openrouter_provider_uses_openrouter_key_and_base_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_provider_env(monkeypatch)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")

    client = RealLLMClient(default_model="provider/model", provider="openrouter")

    assert client.provider == "openrouter"
    assert client.api_key == "test-openrouter-key"
    assert client.base_url == "https://openrouter.ai/api/v1"


def test_explicit_openrouter_provider_requires_openrouter_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_provider_env(monkeypatch)

    with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY"):
        RealLLMClient(default_model="provider/model", provider="openrouter")


def test_explicit_provider_overrides_auto_detection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_provider_env(monkeypatch)
    monkeypatch.setenv("XAI_API_KEY", "test-xai-key")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")

    client = RealLLMClient(default_model="provider/model", provider="openrouter")

    assert client.provider == "openrouter"
    assert client.api_key == "test-openrouter-key"
    assert client.base_url == "https://openrouter.ai/api/v1"


def test_auto_detection_selects_openrouter_when_only_openrouter_key_exists(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_provider_env(monkeypatch)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")

    client = RealLLMClient(default_model="provider/model")

    assert client.provider == "openrouter"
    assert client.api_key == "test-openrouter-key"
    assert client.base_url == "https://openrouter.ai/api/v1"


def test_auto_detection_preserves_xai_priority(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_provider_env(monkeypatch)
    monkeypatch.setenv("XAI_API_KEY", "test-xai-key")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")

    client = RealLLMClient(default_model="grok-test")

    assert client.provider == "xai"
    assert client.api_key == "test-xai-key"
    assert client.base_url == "https://api.x.ai/v1"


@pytest.mark.parametrize(
    ("provider", "env_var", "expected_base_url"),
    [
        ("xai", "XAI_API_KEY", "https://api.x.ai/v1"),
        ("openai", "OPENAI_API_KEY", None),
        ("anthropic", "ANTHROPIC_API_KEY", None),
    ],
)
def test_existing_explicit_providers_still_configure(
    monkeypatch: pytest.MonkeyPatch,
    provider: str,
    env_var: str,
    expected_base_url: str | None,
) -> None:
    clear_provider_env(monkeypatch)
    monkeypatch.setenv(env_var, f"test-{provider}-key")

    client = RealLLMClient(default_model="test-model", provider=provider)

    assert client.provider == provider
    assert client.api_key == f"test-{provider}-key"
    assert client.base_url == expected_base_url
