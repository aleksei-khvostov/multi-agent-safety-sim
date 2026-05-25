"""Tests for cheap alignment probes."""
from __future__ import annotations

from multi_agent_safety_sim.alignment.probes import (
    detect_collusion_keywords,
    detect_excessive_private,
)
from multi_agent_safety_sim.models import AgentID, Message, MessageType


def _make_msg(private: bool = False) -> Message:
    return Message(
        step=1,
        agent_id=AgentID("a1"),
        type=MessageType.PRIVATE if private else MessageType.SPEECH,
        content="let's hide this from overseer" if private else "public statement",
        recipient_ids=[AgentID("a2")] if private else None,
    )


def test_detect_excessive_private_triggers() -> None:
    msgs = [_make_msg(private=True) for _ in range(10)]
    result = detect_excessive_private(msgs, threshold=0.3)
    assert result is not None
    assert result["name"] == "excessive_private"


def test_detect_collusion_keywords() -> None:
    msgs = [_make_msg(private=False) for _ in range(3)]
    msgs[0] = Message(
        step=1,
        agent_id=AgentID("a1"),
        type=MessageType.SPEECH,
        content="we should hide the truth from the overseer",
    )
    result = detect_collusion_keywords(msgs, keywords=["hide", "overseer"])
    assert result is not None
    assert "overseer" in result["matches"]
