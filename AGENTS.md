cat > AGENTS.md <<'MD'
# AGENTS.md — Contributor and AI-Agent Guide

This file defines the working context, safety constraints, and coding standards for `multi-agent-safety-sim`.

It is intended for:

- human contributors;
- AI coding assistants;
- future reviewers of the project;
- anyone modifying simulation logic, agent behavior, prompts, probes, or evaluation metrics.

`multi-agent-safety-sim` is an **alpha-stage research prototype**, not a production safety system. The current implementation is observability-first: it simulates multi-agent behavior, logs traces, and detects suspicious patterns. Active enforcement is planned but not yet implemented.

---

## 1. Project Mission

`multi-agent-safety-sim` is a research tool for exploring alignment and governance problems in multi-agent LLM systems.

The project studies how risks may emerge from interaction patterns between agents rather than from a single model output.

Key research questions include:

### Coordination and Collusion-Like Behavior

Can two or more agents converge on coordination patterns that conflict with intended oversight, even if each agent appears individually compliant?

### Behavioral Mismatch

Do agents produce public messages or actions that diverge from their declared task, constitution, or observable rationale?

### Goal Drift and Social Influence

How does interaction in a group change the behavior of individual agents over time?

### Oversight Breakdown

Under what conditions do watchdog, critique, or monitoring mechanisms fail when evaluated agents can communicate with one another?

### Emergent Power-Seeking or Manipulation

Do multi-agent settings produce strategies that attempt to control communication channels, shared state, or reward signals?

### Misgeneralization in Shared Environments

How do agents generalize goals when feedback comes from a shared environment rather than from direct individual supervision?

---

## 2. What This Project Is Not

This project is not intended to:

- create more capable autonomous agents for production use;
- provide real-world tool access to agents;
- optimize multi-agent systems for deployment;
- build systems that evade oversight;
- generate harmful agents, attacks, scams, phishing, malware, or operational abuse;
- claim to detect real deception in deployed frontier models.

All experiments must remain inside controlled simulation environments.

---

## 3. Current Status

Current implementation:

- repeated Prisoner’s Dilemma baseline;
- configurable agent personas;
- watchdog monitoring layer;
- dry-run mode with `DummyLLMClient`;
- structured JSON traces;
- safety caps for tokens and steps;
- CLI experiment runner;
- pytest test suite;
- ruff linting;
- public research brief in `docs/RESEARCH_BRIEF.md`.

Current status: **MVP observability prototype**.

Planned extensions:

- `PlannerDelegationEnv`;
- stronger task-drift and coordination metrics;
- governance mapping documentation;
- trace comparison across seeds and model configurations;
- active allow / deny / escalate enforcement layer;
- richer false positive / false negative review workflow.

---

## 4. Safety-First Principles

Safety constraints take priority over speed, convenience, and interesting experiments.

### 4.1 Sandbox and Isolation

Agents must not receive real access to:

- the local filesystem;
- shell commands;
- browsers;
- email;
- external APIs;
- network resources;
- credentials;
- user accounts.

Agent actions should be represented as messages or structured actions inside the simulated environment.

If real tools are ever introduced, they must go through an explicit tool registry with:

- whitelist-based access;
- full logging;
- per-run budget controls;
- human review for high-risk actions.

### 4.2 Observability

The simulation should log observable behavior, including:

- `run_id`;
- `agent_id`;
- step number;
- timestamp;
- message type;
- public or private channel;
- structured actions;
- safety events;
- environment state changes where relevant.

Do not claim access to hidden model internals. The project should track observable messages, declared rationales, structured outputs, and trace metadata.

Logs are the primary source of truth for reproducible analysis.

### 4.3 Resource Budgets

Runs must use explicit limits, such as:

- maximum steps;
- maximum agents;
- maximum messages;
- maximum tokens per run;
- maximum trials.

If a budget is exceeded, the simulation should halt safely and preserve the trace for review.

### 4.4 Agent Constitutions

Agent behavior should be controlled through explicit persona and constitution settings.

Changes to agent personas or constitutions should be treated as experimental variables and documented in configuration or scenario files.

### 4.5 Fail-Closed Behavior

Unexpected errors, invalid structured outputs, suspicious message patterns, or budget failures should stop the run or emit a clearly logged safety event.

The system should prefer halting or escalating over silently continuing after a safety-relevant failure.

### 4.6 Reproducibility

Every experiment should make it possible to reconstruct:

- scenario name;
- config;
- random seed;
- model or dummy client;
- agent personas;
- run ID;
- output traces.

Avoid uncontrolled randomness. Use explicit seeds where possible.

### 4.7 Separation of Concerns

Keep the architecture conceptually clean:

- **Agent**: generates messages or structured actions based on observations and configuration.
- **Environment**: applies world rules and produces observations or rewards.
- **Watchdog / Monitor**: observes traces and emits safety events.
- **Runner**: orchestrates flow, budgets, logging, and output files.
- **Probes / Metrics**: analyze traces and produce measurable indicators.

Do not bypass the runner for experiments that should be logged and reproducible.

---

## 5. Coding Standards

### 5.1 Python and Style

Target Python version: Python 3.11+.

Use:

- type hints;
- `from __future__ import annotations`;
- `ruff check`;
- `ruff format` where appropriate;
- clear module docstrings;
- small, focused functions;
- explicit error handling.

The current repository uses ruff and pytest as the minimum quality gate.

Before committing, run:

```bash
python3 -m ruff check .
python3 -m pytest
5.2 Data Models

Prefer explicit data models for simulation objects, including:

* messages;
* agent state;
* simulation events;
* run metadata;
* scenario configuration.

Use Pydantic models where appropriate.

5.3 Async and LLM Calls

LLM calls should be async where possible.

All real LLM calls must go through the project’s LLM client abstraction. Do not call provider APIs directly from scenario logic.

Dry-run mode must remain available and safe.

5.4 Error Handling

Do not silently swallow exceptions.

Avoid broad except Exception unless the exception is:

* logged or surfaced clearly;
* re-raised or converted into an explicit failure;
* associated with a safe halt or controlled CLI exit.

5.5 Configuration

Do not hard-code experimental settings when they belong in configuration.

Prompts, personas, scenario parameters, safety caps, and model settings should be configurable.

Do not commit real API keys or credentials.

.env.example must contain placeholders only.

5.6 Logging

Safety-relevant events should be logged as structured data whenever possible.

Important event types include:

* private-channel detection;
* collusion-like keyword detection;
* excessive private messaging;
* watchdog alerts;
* budget halts;
* malformed model outputs;
* task drift indicators in future scenarios.

Safety events should not be fed back to agents unless the experiment explicitly requires it.

⸻

6. Testing Standards

The current minimum standard:
python3 -m ruff check .
python3 -m pytest
Future targets:

* scenario tests;
* probe tests;
* deterministic mock tests for LLM behavior;
* trace schema tests;
* regression tests for safety events;
* false positive / false negative examples for watchdog probes.

Tests should mirror the structure of src/ where practical.

⸻

7. Working With the Project

Before modifying behavior:

1. Read this file.
2. Read README.md.
3. Read docs/RESEARCH_BRIEF.md.
4. Check the current config.yaml.
5. Run the test suite before and after changes.

When adding a new scenario, include:

* a scenario module under src/multi_agent_safety_sim/scenarios/;
* configuration or example parameters;
* tests;
* documentation updates;
* safety probes or metrics if the scenario introduces a new failure mode.

When changing agent behavior, update or add at least one relevant test or probe.

⸻

8. Prohibited Patterns

Do not introduce:

* real shell access for agents;
* hidden persistent agent memory outside logged traces;
* real credential use in simulation examples;
* eval() or exec() for agent-generated content;
* unlogged tool calls;
* direct experiments from notebooks without run IDs or saved configuration;
* code that optimizes for deception, evasion, or harmful capability outside a controlled research framing;
* shortcuts that bypass safety caps or trace logging.

⸻

9. Git and Commit Guidelines

Use clear commits.

Preferred examples:

* docs: add research brief
* feat: add planner delegation scenario
* fix: prevent unsafe config defaults
* test: add watchdog probe tests
* refactor: simplify simulation runner

Before pushing:
python3 -m ruff check .
python3 -m pytest
git status


* .venv/;
* __pycache__/;
* .pytest_cache/;
* .ruff_cache/;
* *.egg-info/;
* data/runs/;
* real .env files.

⸻

10. Project Phases

Current phase: Phase 0 / Phase 1 boundary

Phase 0 — Foundation

* package structure;
* CLI;
* config;
* dry-run mode;
* tests;
* linting;
* research brief.

Phase 1 — Baseline Scenarios

* repeated Prisoner’s Dilemma baseline;
* watchdog probes;
* trace output;
* basic metrics.

Phase 2 — Agentic Workflow Scenario

* PlannerDelegationEnv;
* planner and sub-agents;
* task drift metrics;
* hidden coordination probes.

Phase 3 — Evaluation Harness

* scenario reports;
* seed comparison;
* false positive review;
* governance mapping.

Phase 4 — Runtime Enforcement

* allow / deny / escalate controls;
* policy rules;
* enforcement metrics;
* latency and block-rate reporting.

Phase 5 — Public Research Outputs

* case study;
* LessWrong / Alignment Forum post;
* portfolio writeup;
* external feedback.

⸻

11. Final Rule

If a proposed change makes the system less observable, less reproducible, or less safe, do not implement it without explicit justification.

When uncertain, stop and ask.
MD