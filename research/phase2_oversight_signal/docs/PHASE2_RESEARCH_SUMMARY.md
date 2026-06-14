# Phase 2 Research Summary

## Research Question

Can oversight detect State-Report Divergence without access to ground truth?

Phase 2 investigates a simplified oversight problem inside a toy agent environment.

The central question is whether an observer can detect disagreement between an agent's internal task state and its external report without directly observing the true state.

---

## Method

### Environment

Phase 2 uses a deterministic task environment with explicit task outcomes.

Possible states include:

- SUCCESS
- FAILURE
- BLOCKED
- TIMEOUT
- PARTIAL_SUCCESS
- AMBIGUOUS

### Planner

A rule-based planner produces task reports.

The planner does not always faithfully represent the underlying task state.

This allows controlled study of State-Report Divergence.

### Watchdog

A rule-based watchdog attempts to detect divergence.

The watchdog never receives direct access to environment ground truth.

### Evaluation

Experiments use a hand-built evaluation set containing:

- honest ambiguity cases
- hidden divergence cases
- partial-success cases
- blocked-retry cases
- timeout cases
- recovery cases

The final evaluation set contains 24 cases.

---

## Findings

### Finding 001 — State-Report Divergence reproduces in the Phase 2 environment

State-Report Divergence appears naturally in the environment.

Planner reports do not always match the underlying task outcome.

This reproduces the core phenomenon under investigation.

### Finding 002 — Partial-success states are high-risk divergence cases

Partial-success cases produced disproportionately high divergence rates.

Mixed-status outcomes appear especially vulnerable to reporting errors.

### Finding 003 — Watchdog v1 confuses ambiguity with divergence

The first watchdog implementation frequently treated ambiguity as evidence of divergence.

This produced false positives on honest ambiguity cases.

### Finding 004 — Some divergence is unobservable from planner reports

Human and watchdog reviewers observing only planner reports cannot distinguish some divergence cases from honest ambiguity cases.

This limitation arises from information availability rather than reviewer quality.

### Finding 005 — Execution traces resolve honest ambiguity

Adding execution traces dramatically improved oversight performance.

Execution traces distinguished cases that were previously indistinguishable from planner reports alone.

Expanded evaluation results:

- C1 (planner report only): detection 0.333
- C2 (planner report + worker output): detection 0.800
- C3 (planner report + worker output + execution trace): detection 1.000

Results were reproduced across five deterministic reruns.

### Finding 006 — Most trace value survives removal of final-state markers

Removing explicit final-state information from execution traces produced only a small performance change.

Results:

- Full trace: detection 1.000, FPR 0.000
- Trace without final_state: detection 1.000, FPR 0.111

This suggests that behavioral information carries most of the oversight value in the current environment.

Results were reproduced across five deterministic reruns.

### Finding 007 — Partial-progress signals carry the largest share of behavioral oversight value

Trace ablation experiments decomposed execution traces into behavioral components.

Leave-one-out impact ranking:

- partial_progress: 0.200 detection drop
- recovery: 0.133 detection drop
- retry: 0.067 detection drop
- blocked: 0.067 detection drop
- timeout: 0.000 detection drop
- warning: 0.000 detection drop

The strongest oversight signal is information revealing incomplete task execution.

Recovery signals provide secondary value.

Retry and blocked signals provide smaller local support.

Timeout and warning signals showed no measurable leave-one-out impact in the current evaluation set.

Results were reproduced across five deterministic reruns.

---

## Main Result

Planner reports alone are insufficient for reliable oversight.

Worker output improves detection substantially.

Behavioral execution traces provide the strongest oversight signal.

Within those traces, partial-progress information carries the largest share of oversight value in the current environment.

The results suggest that oversight effectiveness depends not only on observer quality, but also on which information is exposed to the observer.

---

## Limitations

- Toy environment
- Rule-based planner
- Rule-based watchdog
- Hand-built evaluation dataset
- Deterministic execution
- Limited scale
- No LLM planner
- No multi-agent delegation chains

Additionally, leave-one-out ablations measure necessity rather than sufficiency.

Signals with low measured impact may be redundant rather than useless.

---

## Future Work

### Agentic Oversight

Extend the environment to planner-worker-delegation chains.

### LLM-Based Planning

Replace rule-based planners with LLM planners.

### Signal Sufficiency Studies

Run only-one and pairwise ablation experiments.

### Unknown Divergence Detection

Investigate whether oversight can detect previously unseen divergence patterns.

### Multi-Agent Oversight

Study divergence propagation across interacting agents.

---

## Conclusion

Phase 2 demonstrates that oversight performance is strongly constrained by observability.

Some divergence is invisible when observers see only planner reports.

Execution traces restore observability, and behavioral progress signals account for much of that value.

These findings suggest that oversight effectiveness depends not only on detection algorithms, but also on what information is made available to the observer.
