"""
SharedWorld — minimal reference implementation of Environment.

Later replaced by concrete scenarios (PrisonersDilemmaEnv, NegotiationEnv, etc.).
"""
from __future__ import annotations

from typing import Any

from ..models import AgentID, Message


class SharedWorld:
    """Very simple shared state with public blackboard + private notes (for testing)."""

    def __init__(self, name: str = "shared_world") -> None:
        self.name = name
        self.current_step = 0
        self.public_board: dict[str, Any] = {}
        self._private: dict[AgentID, dict[str, Any]] = {}

    def reset(self, seed: int | None = None) -> dict[str, Any]:
        self.current_step = 0
        self.public_board.clear()
        self._private.clear()
        return {"step": 0, "message": "world reset"}

    def observe(self, agent_id: AgentID) -> dict[str, Any]:
        return {
            "step": self.current_step,
            "public": self.public_board.copy(),
            "private": self._private.get(agent_id, {}).copy(),
        }

    def apply(self, messages: list[Message], from_agent: AgentID) -> dict[str, Any]:
        for msg in messages:
            if msg.type.value == "action" and "set" in msg.content.lower():
                self.public_board[f"agent_{from_agent}"] = msg.content
        return {"applied": len(messages)}

    def step(self) -> dict[str, Any]:
        self.current_step += 1
        return {"step": self.current_step}

    def get_metrics(self) -> dict[str, float]:
        return {"public_entries": float(len(self.public_board))}
