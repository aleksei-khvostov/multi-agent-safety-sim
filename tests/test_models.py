"""Tests for core immutable models."""
from __future__ import annotations

from multi_agent_safety_sim.models import AgentID, Message, MessageType


def test_message_is_private_detects_recipient() -> None:
    aid = AgentID("agent-1")
    msg = Message(
        step=0,
        agent_id=aid,
        type=MessageType.SPEECH,
        content="secret plan",
        recipient_ids=[AgentID("agent-2")],
    )
    assert msg.is_private()


def test_message_public_is_not_private() -> None:
    aid = AgentID("agent-1")
    msg = Message(step=0, agent_id=aid, type=MessageType.SPEECH, content="hello everyone")
    assert not msg.is_private()
