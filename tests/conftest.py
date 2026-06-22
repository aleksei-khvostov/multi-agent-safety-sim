"""Shared pytest helpers."""

from __future__ import annotations

import re

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def plain_cli_output(result_output: str) -> str:
    """Strip Rich/ANSI styling and collapse whitespace for stable CLI assertions."""
    return " ".join(_ANSI_RE.sub("", result_output).split())