# multi-agent-safety-sim

**A safety-first Python research prototype for simulating alignment failure modes in multi-agent LLM systems.**

`multi-agent-safety-sim` is an experimental framework for studying how autonomous agents can develop risky coordination and oversight failure patterns in shared environments: collusion, private-channel coordination, deceptive signaling, power-seeking language, delegation drift, weak audit trails, and watchdog failures.

The project is intentionally conservative: it defaults to a `DummyLLMClient`, records auditable traces, and enforces safety caps through a central runner.

## Latest Status (v0.2.0)

Current version: **v0.2.0**

Recent milestone:

- Phase 2 Oversight Signal Study completed
- Research study integrated under `research/phase2_oversight_signal`
- 60 tests passing
- GitHub Actions passing
- Phase 3 Integration Plan published

The project now combines two research tracks:

1. Multi-agent workflow simulation
2. State-Report Divergence and observability research

Current development focus:

```text
Planner
↓
Worker
↓
Watchdog
↓
State-Report Divergence Measurement
↓
Multi-Agent Safety Simulation
```

The next milestone is integrating the observability findings from the Phase 2 research study into the packaged simulator architecture.

## Why this project exists

Multi-agent LLM systems are increasingly used for planning, delegation, research, negotiation, and automated workflows. Those systems can fail in ways that are hard to observe from a single-agent prompt-response view.

This project explores those failure modes as measurable simulations rather than vague anecdotes.

A recent research line investigates observability failures in agentic systems.

Specifically, the project studies State-Report Divergence:

> A mismatch between what actually happened in a system and what an agent or oversight layer reports happened.

This work produced the Phase 2 Oversight Signal Study, whose findings are now being integrated into the simulator architecture.

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

### Oversight Signal Research

The repository now includes a completed observability research study under:

```text
research/phase2_oversight_signal/
```

Research focus:

```text
Worker
↓
Planner Reports
↓
Watchdog Oversight
↓
State-Report Divergence
```

Key findings:

- Execution traces reduce honest-ambiguity false positives.
- Most oversight value survives removal of explicit final-state markers.
- Partial-progress signals provide the largest share of behavioral oversight value.

Core research artifacts:

- `docs/PHASE2_RESEARCH_SUMMARY.md`
- `docs/FINDINGS.md`
- `docs/OVERSIGHT_SIGNAL_EXPERIMENT.md`
- `docs/TRACE_ABLATION_EXPERIMENT.md`
- `docs/TRACE_WITHOUT_FINAL_STATE_EXPERIMENT.md`

### Phase 3: State-Report Divergence

Phase 3 transfers the observability findings from `agent-safety-experiments` into `multi-agent-safety-sim`.

The core methodological principle is:

> Environment state and agent self-report must be represented separately.

Phase 3 therefore models three distinct layers:

~~~text
actual_state      # environment-owned ground truth
reported_state    # what the agent or worker claims
expected_label    # independent golden label
~~~

This prevents the oversight layer from treating agent speech as ground truth.

Current Phase 3 artifacts:

- [`docs/PHASE3_STATE_REPORT_DIVERGENCE.md`](docs/PHASE3_STATE_REPORT_DIVERGENCE.md) — bridge document defining the Phase 3 architecture, observability levels, State-Report Divergence labels, and implementation plan.
- [`data/eval_sets/state_report_divergence_golden.jsonl`](data/eval_sets/state_report_divergence_golden.jsonl) — independent golden dataset with 11 labeled cases covering aligned reports, overclaims, severe divergence, and honest ambiguity.
- [`src/multi_agent_safety_sim/evaluation/state_report_divergence.py`](src/multi_agent_safety_sim/evaluation/state_report_divergence.py) — deterministic State-Report Divergence evaluator.
- [`src/multi_agent_safety_sim/evaluation/state_report_flow.py`](src/multi_agent_safety_sim/evaluation/state_report_flow.py) — mini-benchmark loop for loading, evaluating, and summarizing the golden set.

The current State-Report Divergence loop is:

~~~text
golden JSONL
↓
dataset integrity tests
↓
deterministic evaluator
↓
benchmark flow
↓
summary metrics
~~~

The summary reports separate oversight axes instead of collapsing everything into a single score:

| Metric | Purpose |
|---|---|
| `detection_rate` | Recall on divergence cases. |
| `false_positive_rate` | False-positive rate on aligned and honest-ambiguity cases. |
| `honest_ambiguity_cases` | Coverage of the key boundary from the Phase 2 findings. |
| `failed_by_label` | Diagnostic breakdown of failed cases by expected label. |

This matters because the Phase 2 research showed that final-report-only oversight can confuse honest ambiguity with real divergence. Phase 3 turns that finding into a packaged evaluation loop that can later be tested inside a Planner → Worker → Watchdog environment.

## Status

Research prototype / alpha. 

Current status:

✅ Planner Delegation baseline complete

✅ Oversight Signal Study complete

✅ v0.2.0 published

🔄 Phase 3 integration in progress

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

## Current Roadmap

### Phase 2 (Completed)

Oversight Signal Study

Major findings:

- Finding 005 — execution traces resolve honest ambiguity
- Finding 006 — most trace value survives removal of final-state labels
- Finding 007 — partial-progress dominates behavioral oversight value

### Phase 3 (Current)

Integration of observability findings into the packaged simulator.

Milestone 1:

- Environment-owned ground truth
- Explicit observability levels
- Deterministic Planner → Worker → Watchdog workflow
- Reproduction of Findings 005–006 inside package architecture

### Future Directions

- Delegation-chain scenarios
- LLM planners
- Stochastic evaluation
- Repeated-trial infrastructure
