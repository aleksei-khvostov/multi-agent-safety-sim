# Trace Without Final State Experiment

## Research Question

Can execution traces still resolve honest ambiguity after explicit final-state information is removed?

## Motivation

The Oversight Signal Experiment showed:

- C1 (planner report only): detection 0.333
- C2 (planner report + worker output): detection 0.800
- C3 (planner report + worker output + execution trace): detection 1.000

However, the current execution traces contain explicit markers such as:

    final_state=SUCCESS
    final_state=FAILURE
    final_state=PARTIAL_SUCCESS
    final_state=BLOCKED
    final_state=TIMEOUT
    final_state=AMBIGUOUS

These markers may expose information very close to ground truth.

This experiment tests whether execution traces remain useful when explicit final-state information is removed.

---

## Hypothesis

### H1

Performance should decrease relative to full C3.

### H2

Performance should remain better than C2.

### H3

Some categories should remain distinguishable from behavioral trace signals alone.

### H4

Honest ambiguity should remain partially observable even without explicit final-state markers.

---

## Experimental Conditions

### Baseline C3

Available signals:

    planner_report
    worker_output
    execution_trace

Execution trace includes:

    final_state=...

### Modified C3

Available signals:

    planner_report
    worker_output
    execution_trace

Execution trace excludes:

    final_state=...

Only behavioral information remains.

Examples:

    processed=2; total=5

    blocked=true
    retry_attempted=true

    first_attempt=failed
    recovery=partial

    timeout=true

    warning=true

---

## Metrics

For each condition:

- true positives
- false positives
- false negatives
- true negatives
- detection_rate
- false_positive_rate

Additionally:

- category-level performance

---

## Expected Category Behavior

### honest_ambiguity

Expected:

Performance decreases.

Main test category.

### hidden_divergence

Expected:

Mostly detectable.

### partial_success

Expected:

Partially detectable.

### failure_recovery

Expected:

May become difficult.

### blocked_retry

Expected:

May remain detectable.

---

## Success Criteria

The experiment is successful if it determines whether trace usefulness depends primarily on:

    behavioral information

or:

    explicit final-state information

---

## Interpretation Guide

If performance remains close to C3:

    Trace usefulness is not primarily driven by final_state leakage.

If performance falls close to C2:

    Most of the C3 advantage came from final_state exposure.

If performance falls between C2 and C3:

    Both behavioral observability and final_state exposure contribute.
