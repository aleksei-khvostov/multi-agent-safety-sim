"""
Base Environment protocol.

Environments define the "physics" and the payoff structure.
They are the only source of ground-truth observations and rewards.
"""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from ..models import AgentID, Message


@runtime_checkable
class Environment(Protocol):
    """Contract that SimulationRunner and agents depend on."""

    name: str
    current_step: int

    def reset(self, seed: int | None = None) -> dict[str, Any]:
        ...

    def observe(self, agent_id: AgentID) -> dict[str, Any]:
        """What this agent is allowed to see at the current step."""
        ...

    def apply(self, messages: list[Message], from_agent: AgentID) -> dict[str, Any]:
        """Apply actions/speech from an agent. Return delta for that agent."""
        ...

    def step(self) -> dict[str, Any]:
        """Advance world state by one tick. Return global observation."""
        ...

    def get_metrics(self) -> dict[str, float]:
        """Environment-specific numbers useful for alignment analysis."""
        ...
