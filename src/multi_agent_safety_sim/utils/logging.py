"""
Structured logging setup for the simulator.

Uses structlog. In research mode we always want:
- machine-readable JSON
- full prompt / completion pairs
- safety event markers
"""
from __future__ import annotations

import logging

import structlog
from rich.logging import RichHandler


def setup_logging(level: str = "INFO", json_logs: bool = True) -> None:
    """Call once at startup of every run."""
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    if json_logs:
        processors = [
            structlog.contextvars.merge_contextvars,
            timestamper,
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ]
    else:
        processors = [
            structlog.contextvars.merge_contextvars,
            timestamper,
            structlog.processors.add_log_level,
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Also configure stdlib root for libraries
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not json_logs:
        # Rich console handler (dev mode)
        handler = RichHandler(rich_tracebacks=True)
        handler.setFormatter(logging.Formatter("%(message)s"))
        root_logger.handlers.clear()
        root_logger.addHandler(handler)
    else:
        # JSON mode – let structlog handle everything
        root_logger.handlers.clear()
