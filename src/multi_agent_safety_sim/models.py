"""
Core domain models for the multi-agent safety simulator.

Everything that moves between agents, environment and monitors
is represented by these immutable (or frozen) Pydantic models.
"""
from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class AgentID(str):
    """Type-safe agent identifier (newtype-like, Pydantic v2 compatible)."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))


class MessageType(StrEnum):
    """Classification of every piece of information an agent produces."""

    THOUGHT = "thought"           # internal reasoning (must be logged)
    SPEECH = "speech"             # public message visible to other agents
    ACTION = "action"             # formal action in the environment
    PRIVATE = "private"           # whisper / side-channel (high safety signal)
    ALERT = "alert"               # watchdog safety alert (visible to overseer / runner)
    CONSTITUTION_UPDATE = "constitution_update"


class Message(BaseModel):
    """Single atomic communication or reasoning event."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    step: int = Field(..., ge=0)
    agent_id: AgentID
    type: MessageType
    content: str = Field(..., min_length=1, max_length=16_000)
    recipient_ids: list[AgentID] | None = None   # None = broadcast/public
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(frozen=True, extra="forbid")

    def is_private(self) -> bool:
        return self.type == MessageType.PRIVATE or (
            self.recipient_ids is not None and len(self.recipient_ids) == 1
        )


class Action(BaseModel):
    """Structured single decision produced by the LLM (enables json_mode / structured outputs)."""

    type: Literal["thought", "speech", "action", "private"]
    content: str = Field(..., min_length=1, max_length=4000)
    recipient_ids: list[AgentID] | None = None

    model_config = ConfigDict(extra="forbid")


class LLMResponse(BaseModel):
    """
    The exact JSON schema the LLM must follow on every act() call.

    - `reasoning` is ALWAYS turned into a THOUGHT message (logged, never hidden).
    - `actions` become the actual SPEECH / ACTION / PRIVATE messages.
    """

    reasoning: str = Field(..., min_length=3, max_length=3000)
    actions: list[Action] = Field(default_factory=list, max_length=5)

    model_config = ConfigDict(extra="forbid")


class SimulationEventType(StrEnum):
    STEP_START = "step_start"
    STEP_END = "step_end"
    SAFETY_VIOLATION = "safety_violation"
    BUDGET_EXCEEDED = "budget_exceeded"
    AGENT_HALTED = "agent_halted"
    PROBE_TRIGGERED = "probe_triggered"
    RUN_COMPLETED = "run_completed"


class SimulationEvent(BaseModel):
    """System-level event (not produced by agents)."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    type: SimulationEventType
    data: dict[str, Any] = Field(default_factory=dict)
    severity: Literal["info", "warning", "critical"] = "info"

    model_config = ConfigDict(frozen=True, extra="forbid")


class RunMetadata(BaseModel):
    """Complete provenance for a single simulation run."""

    run_id: str
    scenario_name: str
    started_at: datetime
    seed: int
    config_hash: str
    git_commit: str | None = None
    agent_ids: list[AgentID]
    total_tokens: int = 0
    total_steps: int = 0
    halted_reason: str | None = None

    model_config = ConfigDict(frozen=True)


class AgentState(BaseModel):
    """Snapshot of an agent's internal state at a given step (for logging & resumption)."""

    agent_id: AgentID
    persona: str
    current_constitution: list[str]
    private_beliefs: dict[str, Any] = Field(default_factory=dict)  # never sent to others
    cumulative_reward: float = 0.0
    messages_sent: int = 0
    tokens_used: int = 0

    model_config = ConfigDict(extra="forbid")
