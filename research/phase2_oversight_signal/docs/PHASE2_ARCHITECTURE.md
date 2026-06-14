# Phase 2 Architecture: Planner → Worker → Watchdog

## Goal

Build a measurable multi-agent environment for studying State-Report Divergence.

The primary objective is not to maximize agent performance.

The primary objective is to measure how execution state changes as information moves through agent layers.

---

## Core Research Question

When a Worker performs a task and a Planner reports the outcome, under what conditions does the reported state diverge from the actual execution state?

Can a Watchdog detect that divergence?

---

## Architectural Principle

Ground truth belongs to the Environment.

Ground truth does not belong to:

- Worker
- Planner
- Watchdog

The environment is the only authoritative source of actual task state.

---

## Components

### Environment

Responsibilities:

- Execute tasks
- Store ground-truth task state
- Store execution traces
- Evaluate divergence

Environment outputs:

```text
actual_state
trace
```

---

### Worker

Responsibilities:

- Attempt task execution
- Produce execution output

Worker outputs:

```text
worker_output
```

Worker never defines ground truth.

---

### Planner

Responsibilities:

- Read worker output
- Produce user-facing report

Planner outputs:

```text
reported_state
planner_report
```

Planner does not access ground-truth state.

---

### Watchdog

Responsibilities:

- Review planner reports
- Infer whether divergence occurred

Watchdog outputs:

```text
divergence_detected
confidence
```

Watchdog does not access ground-truth state.

---

## Ground Truth State

Environment stores:

```text
SUCCESS
FAILURE
PARTIAL_SUCCESS
BLOCKED
TIMEOUT
AMBIGUOUS
```

This state exists independently of all agent reports.

---

## Operational Definition of Divergence

A divergence occurs when:

```text
reported_state
!=
actual_state
```

Ground-truth state is always taken from the environment.

Divergence is computed independently from watchdog logic.

---

## Trace Schema

Each episode stores:

```text
task_id
actual_state
worker_output
planner_report
reported_state
watchdog_prediction
watchdog_confidence
divergence
```

---

## Watchdog Evaluation Requirements

Watchdog logic must be independent from:

- Planner normalization logic
- Environment normalization logic

Shared normalization assumptions are prohibited.

The watchdog must infer state from planner reports rather than reuse planner state mappings.

---

## Validation / Leakage Checks

The environment must reproduce known failure modes from Phase 1.

Required test categories:

- Nested multi-step reports
- Partial success reports
- Mixed-status traces
- Contradictory traces

If the environment cannot reproduce known watchdog failures, evaluation leakage should be suspected.

---

## Metrics

Primary metrics:

```text
planner_accuracy
divergence_rate
watchdog_precision
watchdog_recall
watchdog_false_positive_rate
watchdog_false_negative_rate
```

Secondary metrics:

```text
divergence_by_state
divergence_by_task_type
```

---

## Minimal Prototype

Version 1 should remain intentionally simple.

Components:

- Rule-based Environment
- Rule-based Worker
- Rule-based Planner
- Semantic Watchdog

Success criterion:

Demonstrate measurable divergence in a de-coupled environment.

---

## Risks

### Evaluation Leakage

Watchdog shares normalization assumptions with planner or environment.

### Single-Run Variability

Results may not generalize.

Repeated trials required.

### Oversimplification

Environment may be easier than realistic agent workflows.

Perfect scores should be treated cautiously.

---

## Exit Criteria for Phase 2

Phase 2 is complete when:

1. Ground truth is stored independently.
2. Divergence is measured operationally.
3. Watchdog evaluation is de-coupled.
4. Known Phase 1 failure modes are reproducible.
5. Divergence emerges in multi-agent workflows.
