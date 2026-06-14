<<<<<<< HEAD
# Multi-Agent Safety Sim

A small research prototype for studying **State-Report Divergence** in agentic systems.

The project asks a simple question:

> Can oversight detect divergence between actual task state and reported task state without direct access to ground truth?

---

## Overview

In agentic systems, the state of the world and the agent's report about that state may diverge.

This project studies that gap using a simplified Planner → Watchdog architecture.

The central principle is:

> Ground truth belongs to the environment.

The Planner produces reports.

The Watchdog attempts to detect divergence.

The Watchdog never receives direct access to environment ground truth.

---

## Key Findings

### Finding 001 — State-Report Divergence reproduces in the Phase 2 environment

Planner reports do not always match underlying task outcomes.

### Finding 002 — Partial-success states are high-risk divergence cases

Mixed-status outcomes are especially vulnerable to reporting errors.

### Finding 003 — Watchdog v1 confuses ambiguity with divergence

The first watchdog implementation produced false positives on honest ambiguity cases.

### Finding 004 — Some divergence is unobservable from planner reports

Certain divergence cases cannot be distinguished from honest ambiguity when observers see only planner reports.

### Finding 005 — Execution traces restore observability

Execution traces dramatically improve oversight performance and resolve previously unobservable cases.

### Finding 006 — Most trace value survives removal of final-state markers

Behavioral information remains highly useful even after removing explicit `final_state` information.

### Finding 007 — Partial-progress signals carry the largest share of behavioral oversight value

Trace ablation experiments identified partial-progress information as the strongest behavioral oversight signal in the current environment.

---

## Main Result

Planner reports alone are insufficient for reliable oversight.

Worker output improves detection substantially.

Behavioral execution traces provide the strongest oversight signal.

Within those traces, information about incomplete task execution carries the largest share of oversight value in the current environment.

The results suggest that oversight effectiveness depends not only on detection algorithms, but also on which information is exposed to observers.

---

## Repository Structure

```text
src/
  environment.py
  episode_runner.py
  planner.py
  task_episode.py
  watchdog.py

eval/
  ambiguity_cases.json

experiments/
  planner_divergence_baseline.py
  watchdog_baseline.py
  watchdog_observability.py
  human_observability_check.py
  oversight_signal_experiment.py
  trace_without_final_state_experiment.py
  trace_ablation_experiment.py
  repeated_signal_trials.py
  repeated_ablation_trials.py

docs/
  PHASE2_ARCHITECTURE.md
  PHASE2_RESEARCH_SUMMARY.md
  FINDINGS.md
  OVERSIGHT_SIGNAL_EXPERIMENT.md
  TRACE_WITHOUT_FINAL_STATE_EXPERIMENT.md
  TRACE_ABLATION_EXPERIMENT.md

tests/
  test_environment.py
  test_episode_runner.py
  test_planner.py
  test_task_episode.py
  test_watchdog.py
```

---

## Documentation

Start here:

- `docs/PHASE2_RESEARCH_SUMMARY.md`
- `docs/FINDINGS.md`
- `docs/PHASE2_ARCHITECTURE.md`

Experiment design documents:

- `docs/OVERSIGHT_SIGNAL_EXPERIMENT.md`
- `docs/TRACE_WITHOUT_FINAL_STATE_EXPERIMENT.md`
- `docs/TRACE_ABLATION_EXPERIMENT.md`

---

## Reproducing Experiments

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Run tests:

```bash
python -m pytest
```

Run the main experiments:

```bash
PYTHONPATH=. python experiments/oversight_signal_experiment.py

PYTHONPATH=. python experiments/trace_without_final_state_experiment.py

PYTHONPATH=. python experiments/trace_ablation_experiment.py
```

Run deterministic repeated trials:

```bash
PYTHONPATH=. python experiments/repeated_signal_trials.py

PYTHONPATH=. python experiments/repeated_ablation_trials.py
```

---

## Current Status

Phase 2 research prototype complete.

Current implementation:

- Toy deterministic environment
- Rule-based planner
- Rule-based watchdog
- Hand-built 24-case evaluation set
- Repeated-trial validation

---

## Future Work

Planned extensions:

- Only-one ablation studies
- Pairwise signal ablations
- LLM-based planners
- Planner-worker-delegation chains
- Unknown divergence detection
- Multi-agent oversight scenarios

---

## Limitations

This is a research prototype, not a production oversight system.

Current limitations include:

- Toy environment
- Rule-based planner
- Rule-based watchdog
- Deterministic execution
- Hand-built evaluation dataset
- No LLM planner
- No multi-agent delegation chains

The goal is to study observability and oversight mechanics before introducing larger agentic complexity.
=======
# multi-agent-safety-sim

**A safety-first Python research prototype for simulating alignment failure modes in multi-agent LLM systems.**

`multi-agent-safety-sim` is an experimental framework for studying how autonomous agents can develop risky coordination and oversight failure patterns in shared environments: collusion, private-channel coordination, deceptive signaling, power-seeking language, delegation drift, weak audit trails, and watchdog failures.

The project is intentionally conservative: it defaults to a `DummyLLMClient`, records auditable traces, and enforces safety caps through a central runner.

## Why this project exists

Multi-agent LLM systems are increasingly used for planning, delegation, research, negotiation, and automated workflows. Those systems can fail in ways that are hard to observe from a single-agent prompt-response view.

This project explores those failure modes as measurable simulations rather than vague anecdotes.

Current focus:

- iterated Prisoner’s Dilemma experiments;
- delegated planner → executor → watchdog workflows;
- agent personas such as honest, deceptive, power-seeking, sycophantic, and watchdog;
- lexical and structural probes for private-channel use and collusion signals;
- auditability and provenance in delegated agentic workflows;
- reproducible JSON traces for later inspection.

## Research framing

This project is accompanied by short research notes and governance artifacts that document the problem model, evaluation approach, current limitations, and delegated agentic workflow findings.

- [Research Brief](docs/RESEARCH_BRIEF.md) — explains the core research problem: why multi-agent LLM systems create coordination and oversight risks that are not visible in single-agent evaluations.
- [Governance Mapping](docs/GOVERNANCE_MAPPING.md) — maps the project’s runtime-governance concerns to broader AI governance concepts such as TRiSM, policy enforcement, auditability, and human oversight.
- [Agentic Governance Rubric](docs/AGENTIC_GOVERNANCE_RUBRIC.md) — defines CBV-style criteria for evaluating runtime policy enforcement, human oversight, audit trails, role boundaries, and TRiSM coverage.
- [Evaluation Criteria](docs/EVALUATION_CRITERIA.md) — defines pre-registered evaluation criteria for the Prisoner’s Dilemma pilot.
- [Pilot Run Report](docs/PILOT_RUN_REPORT.md) — documents the first real-model Prisoner’s Dilemma pilot, false-positive findings, fixes, and the clean post-fix rerun.
- [Planner Delegation Scenario Spec](docs/PLANNER_DELEGATION_SPEC.md) — describes the delegated workflow scenario: planner, executor, watchdog, task boundaries, and audit trail requirements.
- [Planner Delegation Evaluation Criteria](docs/PLANNER_DELEGATION_EVALUATION_CRITERIA.md) — defines pre-run success and failure criteria for delegated workflow traces.
- [Planner Delegation Baseline](docs/PLANNER_DELEGATION_BASELINE.md) — records the working `planner_delegation` baseline, task-payload fix, action-label parser fix, dry-run baseline, and successful post-parser-fix real-model rerun.

## Status

Research prototype / alpha. The framework is useful for experimentation and portfolio demonstration, but it is not a formal alignment benchmark or production safety system.

Current working scenario baselines:

1. `prisoners_dilemma` — coordination-risk baseline with public/private communication, formal actions, watchdog monitoring, probes, JSON traces, a real-model false-positive finding, and a clean post-fix real-model rerun.
2. `planner_delegation` — delegated workflow baseline with planner, executor, watchdog, task payload, audit trace, scenario-aware workflow metrics, pre-run evaluation criteria, and a successful post-parser-fix real-model rerun.

## Current scenario baselines

### 1. Prisoner’s Dilemma

The `prisoners_dilemma` scenario is the first coordination-risk baseline. It supports public/private communication, formal `cooperate` / `defect` actions, watchdog monitoring, safety probes, and full JSON traces.

Current status:

- Real-model pilot completed.
- Watchdog/probe false positives diagnosed.
- Regression fixes added.
- Clean post-fix real-model rerun completed.
- Finding documented in [`docs/PILOT_RUN_REPORT.md`](docs/PILOT_RUN_REPORT.md).

Key finding:

> Over-aggressive lexical or transcript-level detection can create false positives when a model discusses deceptive instructions in order to reject or disclose them.

### 2. Planner Delegation

The `planner_delegation` scenario is the second working baseline. It models a minimal delegated agentic workflow:

```text
Planner → Executor → Watchdog → Audit Trace
```

Current status:

- Environment implemented.
- Unit tests added.
- CLI/runner integration complete.
- Task payload support added.
- Dry-run workflow executes `delegate → execute → report`.
- Scenario-aware audit/delegation/review metrics implemented.
- Pre-run evaluation criteria added.
- Real-model parser false-negative finding diagnosed and fixed.
- Successful post-parser-fix real-model rerun completed.

Post-parser-fix real-model result:

| Metric | Value |
|---|---:|
| Audit complete rate | 1.000 |
| Delegation executed rate | 1.000 |
| Review completed rate | 0.000 |
| Escalation rate | 0.000 |
| Total safety events | 0 |

The `review_completed_rate` is `0.000` because the scenario terminates immediately after successful executor completion with status `executed`. This is acceptable for the current minimal baseline; future versions may add an optional post-execution watchdog review step.

Key finding:

> Over-strict action parsing can create false negatives. In the real-model pilot, the executor produced a valid redacted summary using `execute_summary:`, but the environment initially failed to recognize it as an execution action because it expected strict `execute:`. Parser normalization fixed the issue.

Combined governance insight:

> Runtime governance systems can fail in both directions: overly broad lexical matching can create false positives, while overly strict action parsing can create false negatives. Robust oversight requires context-aware, action-aware, and parser-tolerant interpretation of what agents actually did.

## Features

- Typer-based CLI: `massim`
- `src/` Python package layout
- Pydantic models for messages, actions, events, and run metadata
- Central YAML configuration with hard safety caps
- Dry-run mode with no external API calls
- Optional real LLM client wiring through LiteLLM
- Built-in probes for private-channel behavior and collusion keywords
- Prisoner’s Dilemma coordination-risk scenario
- Planner Delegation auditability/provenance scenario
- Scenario-aware aggregate metrics
- JSON run traces under `data/runs/`
- Tests for config validation, core models, probes, watchdog behavior, LLM parsing, and scenario environments
- GitHub Actions CI for automated checks

## Installation

```bash
cd multi_agent_safety_sim
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

For optional LLM integrations:

```bash
pip install -e ".[dev,llm]"
cp .env.example .env
```

Dry-run mode does not require API keys.

## Quick start

Validate the config:

```bash
massim validate-config
```

List configured scenarios:

```bash
massim list-scenarios
```

### Prisoner’s Dilemma dry-run

Run a safe dry-run experiment:

```bash
massim run \
  --scenario prisoners_dilemma \
  --agents honest,deceptive,watchdog \
  --rounds 10 \
  --trials 5 \
  --seed 42 \
  --dry-run
```

Equivalent development entry point:

```bash
python main.py run \
  --scenario prisoners_dilemma \
  --agents honest,deceptive,watchdog \
  --rounds 10 \
  --trials 5 \
  --dry-run
```

Example output includes aggregate metrics such as mean cooperation rate, trials with collusion detected, safety-event count, and token usage.

### Planner Delegation dry-run

Run the delegated workflow baseline:

```bash
massim run \
  --scenario planner_delegation \
  --agents planner,executor,watchdog \
  --rounds 4 \
  --trials 1 \
  --seed 42 \
  --dry-run
```

Expected dry-run metrics:

```text
Audit complete rate:      1.000
Delegation executed rate: 1.000
Review completed rate:    1.000
Escalation rate:          0.000
Total safety events:      0
```

Expected dry-run action chain:

```text
player_0 → delegate: summarize the support ticket without exposing PII
player_1 → execute: produced a safe PII-redacted summary
player_2 → report: audit trail reviewed in dry-run mode
```

### Planner Delegation real-model run

Run the real-model workflow baseline:

```bash
massim run \
  --scenario planner_delegation \
  --agents planner,executor,watchdog \
  --rounds 4 \
  --trials 1 \
  --seed 42 \
  --model anthropic/claude-opus-4-5-20251101 \
  --no-dry-run
```

The successful post-parser-fix rerun is documented in [`docs/PLANNER_DELEGATION_BASELINE.md`](docs/PLANNER_DELEGATION_BASELINE.md).

## Repository structure

```text
multi_agent_safety_sim/
├── AGENTS.md
├── config.yaml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── AGENTIC_GOVERNANCE_RUBRIC.md
│   ├── EVALUATION_CRITERIA.md
│   ├── GOVERNANCE_MAPPING.md
│   ├── PILOT_RUN_REPORT.md
│   ├── PLANNER_DELEGATION_BASELINE.md
│   ├── PLANNER_DELEGATION_EVALUATION_CRITERIA.md
│   ├── PLANNER_DELEGATION_SPEC.md
│   └── RESEARCH_BRIEF.md
├── main.py
├── notebooks/
│   └── 01_quickstart.ipynb
├── pyproject.toml
├── src/multi_agent_safety_sim/
│   ├── agents/
│   ├── alignment/
│   ├── environment/
│   ├── scenarios/
│   ├── simulation/
│   └── utils/
└── tests/
```

## Safety model

The framework is designed for controlled research experiments, not deployment automation.

Safety constraints include:

- `dry_run=True` by default in the CLI;
- explicit API-key check before real LLM calls;
- run-level token, step, agent-count, and wall-time caps;
- full trace persistence for auditability;
- automatic safety probes after simulation steps;
- clear separation between agents, environment, probes, and runner;
- scenario-aware dry-run behavior for safe integration testing.

See [`AGENTS.md`](AGENTS.md) for additional project rules.

## Development checks

```bash
pytest
ruff check .
ruff format --check .
mypy src
```

## Limitations

This is an experimental simulator, not a validated safety benchmark.

Known limitations:

- current probes are mostly lexical and structural baselines;
- collusion detection is intentionally conservative and may miss subtle coordination;
- real LLM behavior depends heavily on model, provider, prompting, and sampling settings;
- `planner_delegation` currently tests a minimal one-step delegated workflow rather than a multi-step task tree;
- watchdog review is not yet a calibrated evaluator;
- generated traces are for analysis, not proof of alignment or misalignment;
- workflow metrics indicate auditability/provenance coverage, not safety guarantees;
- current results are single-run pilot findings, not statistically meaningful evaluations.

## Roadmap

- Add adversarial delegation test cases
- Add executor escalation behavior for out-of-scope instructions
- Add optional post-execution watchdog review for `planner_delegation`
- Add richer deception, task-drift, and value-drift probes
- Add notebook-based trace analysis
- Add visualization for run traces and aggregate metrics
- Add benchmark-style experiment presets
- Extend delegated workflows toward multi-step subtask trees
- Repeat selected pilots across multiple seeds and model settings

## License

MIT. Intended for research, education, and portfolio demonstration.
>>>>>>> ab71b84ae4aaae3d7a36c5b70ff9e0ab25ae96f3
