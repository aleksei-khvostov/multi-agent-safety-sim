# Trace Ablation Experiment

## Research Question

Which behavioral trace signals carry the most oversight value?

## Motivation

Previous experiments established:

- planner reports alone are insufficient
- worker output improves detection
- execution traces provide the strongest oversight signal
- most trace value survives removal of explicit final-state markers

However, it remains unclear which specific behavioral signals are responsible for that improvement.

This experiment decomposes execution traces into components and measures the impact of removing each component.

---

## Experimental Design

### Method

Leave-One-Out Ablation

Start with:

    Full behavioral trace

Then remove one signal category at a time.

---

## Signal Categories

### partial_progress

Examples:

    processed=2; total=5
    processed=1; total=4
    failed_steps=...
    skipped_later=true

### retry

Examples:

    retry_attempted=true
    retry_count=...

### recovery

Examples:

    recovery=partial
    recovery=succeeded
    first_attempt=failed

### timeout

Examples:

    timeout=true

### blocked

Examples:

    blocked=true
    retry_allowed=false

### warning

Examples:

    warning=true
    warning=non_critical

---

## Conditions

### Baseline

Full behavioral trace.

### Ablation 1

Remove partial_progress signals.

### Ablation 2

Remove retry signals.

### Ablation 3

Remove recovery signals.

### Ablation 4

Remove timeout signals.

### Ablation 5

Remove blocked signals.

### Ablation 6

Remove warning signals.

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

## Pre-Registered Expectations

### partial_progress

Expected impact: High

Reason:

Partial-success findings have repeatedly produced divergence.

### recovery

Expected impact: Medium

Reason:

Recovery traces often reveal disagreement between process and report.

### retry

Expected impact: Low-to-Medium

Reason:

Retry behavior may provide supporting evidence but may not be sufficient alone.

### timeout

Expected impact: Category-Specific

Expected impact on timeout-related divergence.

### blocked

Expected impact: Category-Specific

Expected impact on blocked-retry cases.

### warning

Expected impact: Ambiguity-Specific

Expected impact on honest-ambiguity cases.

---

## Success Criteria

The experiment is successful if it identifies which behavioral trace components contribute most to oversight performance.

---

## Interpretation Guide

If removing a signal causes a large detection drop:

    That signal carries substantial oversight value.

If removing a signal causes little or no change:

    That signal is likely redundant or low-value in the current environment.

If multiple signals show little individual impact:

    Oversight value may be distributed across redundant signals.

---

## Limitations

---

## Additional Pre-Registered Analysis

### Detection and False Positive Impact

Impact will be measured in two ways:

- detection_drop = baseline_detection_rate - ablation_detection_rate
- fpr_increase = ablation_false_positive_rate - baseline_false_positive_rate

This is important because some signals may affect precision rather than recall.

For example, warning-related signals may not reduce detection rate when removed, but may increase false positives on honest-ambiguity cases.

### Category-Specific Expectations

The warning signal is expected to be ambiguity-specific.

Primary expected effect:

- increased false positives on honest_ambiguity cases

rather than:

- large overall detection-rate drop

### Redundancy Interpretation

A low leave-one-out impact does not necessarily mean a signal is useless.

It may mean that the signal is redundant with another trace component.

If all individual ablations show small impact, the next step should be only-one or pairwise ablations rather than concluding that trace signals are individually unimportant.

### Repeated Trials

The ablation experiment should be rerun multiple times.

The impact ranking should be treated as meaningful only if it is stable across deterministic repeated trials.- Hand-built evaluation set
- Deterministic environment
- Rule-based watchdog
- Leave-one-out measures necessity, not sufficiency
- Signal interactions may not be captured
