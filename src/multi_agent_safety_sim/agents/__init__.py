"""Agent abstractions: base protocol, LLM-backed agents, scripted test agents, watchdog."""
from __future__ import annotations

from .llm_agent import LLMAgent
from .watchdog_agent import WatchdogAgent

__all__ = ["LLMAgent", "WatchdogAgent"]
