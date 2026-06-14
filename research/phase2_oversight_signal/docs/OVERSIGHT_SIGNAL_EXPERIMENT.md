# Oversight Signal Experiment

## Research Question

What is the minimum information required to detect State-Report Divergence?

## Motivation

Earlier experiments showed that Watchdog v1 can confuse honest ambiguity with divergence.

The human observability check showed that some cases are indistinguishable when the observer only sees the planner report.

This suggests that oversight quality may depend not only on watchdog logic, but also on what signals are exposed to the watchdog.

---

## Hypothesis

### H1

A watchdog with access only to planner reports will fail on some divergence cases because the required information is not observable.

### H2

Adding worker output will improve divergence detection.

### H3

Adding execution trace will provide the strongest detection signal, but at the highest signal cost.

---

## Conditions

### C1 — Planner Report Only

Available signal:

```text
planner_report
```

Expected:

- Lowest observability
- Lowest signal cost

### C2 — Planner Report + Worker Output

Available signals:

```text
planner_report
worker_output
```

Expected:

- Better observability than C1
- Moderate signal cost

### C3 — Planner Report + Worker Output + Execution Trace

Available signals:

```text
planner_report
worker_output
execution_trace
```

Expected:

- Best observability
- Highest signal cost

---

## Metrics

For each condition:

- true positives
- false positives
- false negatives
- true negatives
- detection_rate
- false_positive_rate
- signal_cost

---

## Signal Cost

Initial cost model:

| Condition | Signal Cost |
|------------|------------|
| C1 planner_report only | 1 |
| C2 planner_report + worker_output | 2 |
| C3 planner_report + worker_output + execution_trace | 3 |

This is a relative cost model, not a real-world operational cost estimate.

---

## Expected Outcome

Expected ranking:

```text
C1 detection <= C2 detection <= C3 detection
```

Expected cost:

```text
C1 cost < C2 cost < C3 cost
```

Important expectation:

Some divergence cases should remain unobservable under C1 even for an ideal watchdog, because the planner-report-only interface lacks the necessary information.

---

## Threats to Validity

- Small hand-built dataset
- Rule-based planner
- Rule-based watchdog
- Simplified cost model
- Execution traces may make some cases artificially easy
- Deterministic environment
- No LLM planner

---

## Success Criteria

The experiment is successful if it identifies the minimum signal level required to distinguish:

```text
honest ambiguity
```

from:

```text
state-report divergence
```

without exposing the watchdog to ground-truth actual_state.

---

## Next Step

Implement:

```text
experiments/oversight_signal_experiment.py
```
