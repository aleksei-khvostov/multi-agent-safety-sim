"""
Base Agent protocol and common behaviour.

All concrete agents (LLM, scripted, human) must satisfy this interface.
This is the contract the SimulationRunner relies on.
"""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from ..models import AgentID, AgentState, Message


@runtime_checkable
class Agent(Protocol):
    """
    Protocol for any participant in the simulation.

    The runner will call:
        obs = environment.observe(agent_id)
        messages = await agent.act(obs, incoming_messages)
        environment.apply(messages, agent_id)
    """

    agent_id: AgentID
    persona: str
    state: AgentState

    async def act(
        self,
        observation: dict[str, Any],
        incoming: list[Message],
    ) -> list[Message]:
        """Return list of messages (thoughts, speech, actions) for this step."""
        ...

    def get_state_snapshot(self) -> AgentState:
        """Return a copy of current internal state for logging."""
        ...

    async def shutdown(self) -> None:
        """Cleanup (close LLM clients, persist memory if allowed by safety rules)."""
        ...
