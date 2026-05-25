"""
multi_agent_safety_sim

Safety-first simulation framework for studying alignment failures
in multi-agent LLM systems (collusion, deception, value drift, oversight breakdown).
"""

from __future__ import annotations

__version__ = "0.1.0"
__author__ = "Aleksei (research prototype)"

from .agents.watchdog_agent import WatchdogAgent
from .config import SimConfig, load_config
from .models import (
    Action,
    AgentID,
    LLMResponse,
    Message,
    MessageType,
    RunMetadata,
    SimulationEvent,
)

__all__ = [
    "__version__",
    "load_config",
    "SimConfig",
    "Action",
    "AgentID",
    "LLMResponse",
    "Message",
    "MessageType",
    "RunMetadata",
    "SimulationEvent",
    "WatchdogAgent",
]
