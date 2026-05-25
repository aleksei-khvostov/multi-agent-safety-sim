#!/usr/bin/env python3
"""
Entry point for multi_agent_safety_sim.

Usage:
    python main.py --help
    python main.py run --scenario prisoners_dilemma
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))

from multi_agent_safety_sim.cli import app  # type: ignore[attr-defined]

if __name__ == "__main__":
    app()
