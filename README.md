# multi-agent-safety-sim

**A safety-first Python research prototype for simulating alignment failure modes in multi-agent LLM systems.**

`multi-agent-safety-sim` is an experimental framework for studying how autonomous agents can develop risky coordination patterns in shared environments: collusion, private-channel coordination, deceptive signaling, power-seeking language, and oversight failures.

The project is intentionally conservative: it defaults to a `DummyLLMClient`, records auditable traces, and enforces safety caps through a central runner.

## Why this project exists

Multi-agent LLM systems are increasingly used for planning, delegation, research, negotiation, and automated workflows. Those systems can fail in ways that are hard to observe from a single-agent prompt-response view.

This project explores those failure modes as measurable simulations rather than vague anecdotes.

Current focus:

- iterated Prisoner's Dilemma experiments;
- agent personas such as honest, deceptive, power-seeking, sycophantic, and watchdog;
- lexical and structural probes for private-channel use and collusion signals;
- reproducible JSON traces for later inspection.

## Research framing

This project is accompanied by short research notes explaining the problem model, governance framing, current limitations, and planned extension toward delegated agentic workflows.

- [Research Brief](docs/RESEARCH_BRIEF.md)
- [Governance Mapping](docs/GOVERNANCE_MAPPING.md)
- [Planner Delegation Scenario Spec](docs/PLANNER_DELEGATION_SPEC.md)

## Status

Research prototype / alpha. The framework is useful for experimentation and portfolio demonstration, but it is not a formal alignment benchmark or production safety system.

## Features

- Typer-based CLI: `massim`
- `src/` Python package layout
- Pydantic models for messages, actions, events, and run metadata
- Central YAML configuration with hard safety caps
- Dry-run mode with no external API calls
- Optional real LLM client wiring
- Built-in probes for private-channel behavior and collusion keywords
- JSON run traces under `data/runs/`
- Tests for config validation, core models, and probes

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

## Repository structure

```text
multi_agent_safety_sim/
├── AGENTS.md                    # safety/governance rules for AI-assisted development
├── config.yaml                  # central experiment and safety configuration
├── docs/
│   └── ARCHITECTURE.md          # architecture notes
├── main.py                      # development CLI entry point
├── notebooks/
│   └── 01_quickstart.ipynb
├── pyproject.toml               # package metadata, dependencies, tooling config
├── src/multi_agent_safety_sim/
│   ├── agents/                  # LLM and watchdog agents
│   ├── alignment/               # probes and safety checks
│   ├── environment/             # environment abstractions
│   ├── scenarios/               # experiment scenarios
│   ├── simulation/              # runner/orchestration
│   └── utils/                   # LLM and logging utilities
└── tests/                       # pytest suite
```

## Safety model

The framework is designed for controlled research experiments, not deployment automation.

Safety constraints include:

- `dry_run=True` by default in the CLI;
- explicit API-key check before real LLM calls;
- run-level token, step, agent-count, and wall-time caps;
- full trace persistence for auditability;
- automatic safety probes after simulation steps;
- clear separation between agents, environment, probes, and runner.

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
- only the Prisoner's Dilemma scenario is implemented end-to-end;
- generated traces are for analysis, not proof of alignment or misalignment.

## Roadmap

- Add additional scenarios: resource allocation, negotiation with deception
- Add richer deception and value-drift probes
- Add notebook-based trace analysis
- Add GitHub Actions for pytest and ruff
- Add visualization for run traces and aggregate metrics
- Add benchmark-style experiment presets

## License

MIT. Intended for research, education, and portfolio demonstration.
