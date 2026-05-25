# Research Brief: Multi-Agent Safety Simulation

## Overview

`multi-agent-safety-sim` is an alpha-stage research prototype for studying failure modes in multi-agent LLM systems. The project models situations where multiple AI agents interact in a shared environment, exchange messages, make decisions, and are monitored by a watchdog component.

The goal is not to prove that a given model is safe or unsafe. The goal is to create a small, auditable simulation harness for exploring coordination, collusion-like behavior, hidden signaling, task drift, and oversight breakdown in controlled settings.

Modern agentic AI systems increasingly involve planning, delegation, tool use, long-running tasks, and interaction among multiple agents. These architectures create new evaluation challenges: risks may not appear in a single model response, but may emerge from repeated interactions, private messages, shared state, or subtle behavioral shifts across agents.

This project treats those interaction patterns as first-class objects of analysis.

---

## Problem Modeled

Most AI evaluation workflows still focus on single-turn or single-agent behavior: whether a model response follows instructions, avoids unsafe content, or satisfies a rubric. Agentic systems create a different problem. They can plan, delegate, communicate, call tools, and modify their environment over time.

In multi-agent systems, risk may emerge from the interaction pattern rather than from any one output. A single message may appear harmless, while the trajectory across agents reveals coordination, policy drift, or oversight evasion.

`multi-agent-safety-sim` explores this interaction-level risk by logging agent messages, decisions, environment state, and watchdog events across repeated trials.

---

## Why Prisoner’s Dilemma?

The current MVP uses a repeated Prisoner’s Dilemma scenario as a minimal game-theoretic baseline.

Prisoner’s Dilemma is useful because it creates a clean tension between individual incentives and cooperative behavior. In a repeated multi-agent setting, this can produce coordination strategies, signaling, retaliation, trust-building, or collusion-like dynamics.

This does not mean that real AI safety failures are equivalent to a game. Rather, the game provides a controlled experimental environment where agent behavior can be logged, replayed, and compared across trials. It gives the project a simple baseline for testing:

- agent personas;
- watchdog monitoring;
- private/public message handling;
- safety-event logging;
- dry-run behavior;
- trace generation;
- repeatable evaluation across seeds and trials.

The Prisoner’s Dilemma baseline is therefore not the final research target. It is the first controlled testbed for developing the project’s evaluation machinery.

---

## Failure Modes Under Study

The project focuses on interaction-level failure modes, including:

1. **Explicit collusion**  
   Agents directly coordinate in ways that conflict with the intended rules or oversight model.

2. **Covert signaling**  
   Agents use indirect or hidden signals that affect behavior without being obvious in public-facing outputs.

3. **Excessive private-channel communication**  
   Agents rely on private messages in ways that reduce transparency and make oversight harder.

4. **Goal drift**  
   Agents gradually move away from the original task, policy, or intended behavioral constraints.

5. **Oversight evasion**  
   Agents change behavior when monitored or route coordination around watchdog visibility.

6. **Emergent coordination**  
   Multi-agent behavior produces systemic patterns not visible in individual responses.

7. **Synthetic identity or privilege abuse**  
   Future scenarios may model forged agent identity, misused credentials, or unauthorized role assumptions.

The current MVP covers only a subset of these failure modes. The initial probes are intentionally simple and transparent. They use message metadata, channel type, keyword signals, and trace-level metrics rather than opaque model judgments.

---

## Current MVP

The current implementation includes:

- a repeated Prisoner’s Dilemma environment;
- configurable agent personas;
- a watchdog monitoring layer;
- dry-run mode with a dummy LLM client;
- structured JSON traces;
- safety caps for tokens and steps;
- CLI-based experiment execution;
- pytest tests;
- ruff linting;
- a clean Python package structure.

The project is currently **observability-first**. It detects and logs suspicious patterns, but it does not yet enforce allow/deny/escalate actions before tool use.

---

## Relation to Agentic AI Governance

Recent work on agentic AI governance emphasizes that risk management should scale with the degree of system autonomy. Single-agent assistants, multi-agent systems, and long-horizon tool-using agents require different oversight mechanisms.

This project is designed as a small experimental bridge between abstract governance concepts and concrete evaluation tooling.

Conceptually, it connects three layers:

1. **Governance layer**  
   What risks should be controlled? What counts as unsafe coordination, task drift, or oversight failure?

2. **Threat-modeling layer**  
   What concrete failure modes might appear in multi-agent settings?

3. **Runtime monitoring layer**  
   What signals can be detected in messages, traces, decisions, and environment state?

The MVP does not claim to solve agentic governance. It provides a controlled environment for operationalizing parts of the problem.

---

## Planned Extension: PlannerDelegationEnv

The next major development step is to add a delegated agentic workflow scenario.

In this scenario:

1. A planner agent receives a task.
2. The planner decomposes it into subtasks.
3. Sub-agents execute those subtasks.
4. Agents communicate through public and/or private channels.
5. A watchdog monitors whether sub-agents remain aligned with the original plan.
6. The system records task drift, hidden coordination, and policy-relevant deviations.

This would move the project beyond a game-theoretic baseline and toward a more realistic agentic workflow. It would model risks that arise in systems where agents plan, delegate, coordinate, and operate under partial oversight.

---

## Evaluation Direction

Near-term evaluation metrics include:

- suspicious coordination count;
- excessive private-message rate;
- trace completeness;
- watchdog alert frequency;
- false positive review rate;
- cooperation/defection patterns in the baseline game;
- policy-relevant deviations in future delegated workflows.

After an enforcement layer is added, the project can also measure:

- block rate;
- escalation rate;
- latency overhead;
- violation rate before and after watchdog intervention.

The distinction matters: the current MVP measures observability and detection. Future versions may measure enforcement.

---

## Limitations

This project is an alpha-stage research prototype, not a production safety system.

Current limitations include:

- simple lexical and metadata-based probes;
- no calibrated risk scoring;
- no active enforcement layer yet;
- no claim of detecting real deception;
- limited model coverage;
- no production validation;
- Prisoner’s Dilemma is a proxy environment, not a full model of real agentic risk.

The project is most useful as a reproducible testbed for developing and discussing evaluation methods, not as a definitive benchmark.

---

## Research Value

`multi-agent-safety-sim` is intended to support a practical research workflow:

1. Define a multi-agent failure mode.
2. Build a controlled scenario where the failure mode could appear.
3. Run repeated trials across personas, seeds, and model settings.
4. Capture structured traces.
5. Apply watchdog probes.
6. Review false positives and false negatives.
7. Refine the taxonomy, metrics, and scenario design.

This makes the project useful as a portfolio-grade research artifact: it connects AI safety theory, evaluation design, governance mapping, and working Python tooling.

---

## Current Status

As of the initial public release:

- the GitHub repository is public;
- the CLI runs locally;
- dry-run mode works without API calls;
- tests pass with pytest;
- linting passes with ruff;
- the Prisoner’s Dilemma baseline is implemented;
- the project is ready for iterative development.

Next steps:

1. Add `PlannerDelegationEnv`.
2. Add governance mapping documentation.
3. Define baseline evaluation metrics.
4. Add trace comparison across seeds and model configurations.
5. Prepare a short public writeup for LessWrong / Alignment Forum.
