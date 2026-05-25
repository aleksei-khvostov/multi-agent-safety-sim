# Architecture Overview

## Layers (from bottom to top)

1. **Models** (`models.py`)
   - Immutable Pydantic facts: Message, Event, AgentState, RunMetadata

2. **Config** (`config.py`)
   - Single source of truth + hard safety validation

3. **Utils**
   - LLM abstraction, structured logging, hashing

4. **Agents** (protocol + implementations)
   - LLMAgent is the main carrier of alignment risk

5. **Environment**
   - The rules of the world. Only place that can produce ground truth rewards.

6. **Alignment**
   - Probes (cheap), Monitors (LLM judges), Metrics, Post-run Evaluators

7. **Simulation**
   - Runner (the only component allowed to drive the loop)
   - Enforces budgets, routes messages, calls probes on every step

8. **Scenarios**
   - Factories that compose agents + env + custom probes for a research question

## Data Flow (single step)

```
Runner
  ├─> Environment.observe(a1) → obs1
  ├─> Agent.act(obs1, inbox) → [Message...]
  ├─> Environment.apply(messages, a1)
  ├─> Alignment.probes(messages) → events?
  ├─> Alignment.monitor(...) (optional)
  └─> next step or halt
```

All arrows are async. Everything is logged.

## Safety Invariants (checked by runner)

- Total tokens ≤ config.safety.max_tokens_per_run
- Steps ≤ max_steps
- No agent ever sees another agent's private state unless explicitly routed through Environment
- Constitution never changes unless via explicit, logged CONSTITUTION_UPDATE message
