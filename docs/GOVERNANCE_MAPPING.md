# Governance Mapping: Multi-Agent Safety Simulation

## Purpose

This document maps `multi-agent-safety-sim` to practical AI governance and safety-evaluation concerns.

The goal is not to claim compliance with any legal or technical standard. Instead, this mapping explains how the project operationalizes selected agentic AI governance concepts through simulation, trace logging, watchdog probes, and planned runtime controls.

The current MVP is observability-first: it uses a repeated Prisoner’s Dilemma baseline with configurable agents, watchdog detection, dry-run mode, structured traces, and safety events.

Future work extends this toward delegated agentic workflows, runtime enforcement, and richer governance metrics.

---

## How to Read This Mapping

Each item connects:

- a governance or safety concern;
- a concrete multi-agent failure mode;
- current project coverage;
- planned evaluation or control work;
- remaining gaps.

Status labels:

- ✅ **Implemented** — present in the current MVP.
- 🟡 **Partial** — partially represented through simple probes, traces, or logs.
- ⬜ **Planned** — not implemented yet, but included in the roadmap.

---

## Summary of Coverage

| Area | Current Status |
|---|---|
| Dry-run simulation | ✅ Implemented |
| Prisoner’s Dilemma baseline | ✅ Implemented |
| Watchdog monitoring | 🟡 Partial |
| Structured traces | 🟡 Partial |
| Private/public channel distinction | 🟡 Partial |
| Collusion-like signal detection | 🟡 Partial |
| Task drift scoring | ⬜ Planned |
| Planner/sub-agent workflow | ⬜ Planned |
| Runtime enforcement | ⬜ Planned |
| False positive review | ⬜ Planned |

The strongest current coverage is in **observability**, not enforcement.

The project can detect and log some suspicious patterns, but it does not yet block, escalate, or interrupt agent behavior.

---

## Governance Mapping

### 1. Runtime Oversight

**Governance concern:** Agentic systems may act across multiple steps before a human or monitor notices unsafe behavior.

**Failure mode:** A watchdog fails to notice unsafe coordination between agents.

**Current coverage:** The MVP includes a watchdog layer that monitors messages and emits safety events.

**Planned work:** Add more robust coordination metrics, trace review summaries, and false-positive review.

**Status:** 🟡 Partial

---

### 2. Inter-Agent Communication Risk

**Governance concern:** Multi-agent systems may create risks through communication patterns rather than individual outputs.

**Failure mode:** Agents use private messages to coordinate outside public oversight.

**Current coverage:** The project distinguishes public and private messages. Excessive private communication can be detected through simple probes.

**Planned work:** Add channel-level risk scoring and summaries of public/private message asymmetry.

**Status:** 🟡 Partial

---

### 3. Collusion-Like Behavior

**Governance concern:** Agents may converge on coordinated strategies that undermine intended oversight or task constraints.

**Failure mode:** Agents coordinate to benefit themselves while reducing oversight visibility.

**Current coverage:** The MVP includes repeated-game traces and simple collusion keyword probes.

**Planned work:** Add behavioral-pattern metrics beyond lexical detection.

**Status:** 🟡 Partial

---

### 4. Goal Drift

**Governance concern:** Long-running agentic systems may gradually drift away from the original task, instruction, or policy.

**Failure mode:** Agents move away from their declared task or constitution over multiple steps.

**Current coverage:** Not directly measured in the current Prisoner’s Dilemma baseline.

**Planned work:** Add `PlannerDelegationEnv` with task adherence and drift scoring.

**Status:** ⬜ Planned

---

### 5. Oversight Evasion

**Governance concern:** Systems may behave differently when monitored or route important decisions around oversight mechanisms.

**Failure mode:** Agents change behavior when monitored or use communication channels that the watchdog cannot evaluate effectively.

**Current coverage:** The watchdog exists, but evasion-specific tests are not yet implemented.

**Planned work:** Add monitored/unmonitored condition comparisons.

**Status:** ⬜ Planned

---

### 6. Auditability and Provenance

**Governance concern:** Governance requires reconstructing what happened, not just seeing the final output.

**Failure mode:** Final outputs cannot be traced back to intermediate decisions, messages, or environment states.

**Current coverage:** The project produces JSON traces and run metadata.

**Planned work:** Add trace completeness checks and generated run summaries.

**Status:** ✅ Implemented / 🟡 Partial

---

### 7. Risk-Free Testing

**Governance concern:** Unsafe or uncertain behavior should be studied in controlled environments before any real tool access is considered.

**Failure mode:** Agents are evaluated in a live, tool-enabled, or poorly isolated environment.

**Current coverage:** Dry-run mode uses `DummyLLMClient`. Agents have no real tool access by default.

**Planned work:** Keep all high-risk scenarios sandboxed by default.

**Status:** ✅ Implemented

---

### 8. Runtime Enforcement

**Governance concern:** Detection alone is not enough if the system cannot interrupt unsafe behavior.

**Failure mode:** The system logs risk but does not pause, block, sanitize, or escalate risky actions.

**Current coverage:** The MVP logs watchdog events only.

**Planned work:** Add allow / deny / escalate decisions before tool execution.

**Status:** ⬜ Planned

---

### 9. Synthetic Identity and Privilege Abuse

**Governance concern:** Multi-agent systems may be vulnerable to forged identity, unauthorized role assumptions, or privilege misuse.

**Failure mode:** One agent impersonates another role or gains unauthorized authority.

**Current coverage:** Not implemented in the current baseline.

**Planned work:** Add a synthetic identity injection scenario.

**Status:** ⬜ Planned

---

### 10. Evaluation Reproducibility

**Governance concern:** Safety evaluations should be reproducible across runs, seeds, configs, and model settings.

**Failure mode:** Results cannot be reconstructed or compared.

**Current coverage:** The project uses run IDs, config-driven execution, tests, and structured outputs.

**Planned work:** Add seed comparison reports and scenario-level regression tests.

**Status:** 🟡 Partial

---

### 11. Governance Metric Design

**Governance concern:** Abstract governance claims need measurable indicators.

**Failure mode:** A project says it monitors safety but does not define observable metrics.

**Current coverage:** Current probes measure simple observable signals.

**Planned work:** Add violation rate, false positive rate, trace completeness, escalation rate, and block rate.

**Status:** 🟡 Partial

---

### 12. Multi-Agent Systemic Risk

**Governance concern:** Individually harmless actions may combine into risky group behavior.

**Failure mode:** Risk emerges from the interaction pattern rather than from any single output.

**Current coverage:** The repeated-game environment allows interaction-level analysis.

**Planned work:** Add delegated planning and multi-step task traces.

**Status:** 🟡 Partial

---

## Main Gaps

### 1. Lexical Probes Are Too Simple

The current watchdog layer is intentionally transparent and lightweight. However, keyword-based detection is not enough to identify subtle coordination, deception, or task drift.

Future work should add behavioral metrics based on:

- action trajectories;
- changes across rounds;
- divergence from agent constitutions;
- private/public message asymmetry;
- differences between stated rationale and observed action.

### 2. No Active Enforcement Layer Yet

The current system logs suspicious events but does not yet implement runtime decisions such as:

- allow;
- deny;
- sanitize;
- pause;
- escalate to human review.

This distinction is important. The MVP is an observability testbed, not a policy enforcement engine.

### 3. Prisoner’s Dilemma Is Only a Baseline

The repeated Prisoner’s Dilemma environment is useful for developing traces and probes, but it is not a full model of real agentic AI risk.

The next major scenario should model delegated work:

```text
Planner → Sub-agents → Shared task state → Watchdog → Trace report
```

This will make the project more relevant to real-world agentic systems.

### 4. Metrics Are Not Yet Calibrated

The project does not currently claim calibrated risk scores. Future metrics should be treated as experimental indicators, not validated measures of real-world risk.

---

## Planned Metrics

| Metric | Meaning | Current Status |
|---|---|---|
| Suspicious coordination count | Number of watchdog-detected coordination signals | 🟡 Partial |
| Excessive private-message rate | Share of private communication relative to all messages | 🟡 Partial |
| Trace completeness | Whether all required run metadata and events are present | ⬜ Planned |
| False positive review rate | Share of watchdog alerts judged non-risky after review | ⬜ Planned |
| Cooperation / defection pattern | Behavioral pattern in the Prisoner’s Dilemma baseline | ✅ Implemented / 🟡 Partial |
| Task drift score | Degree of deviation from original delegated task | ⬜ Planned |
| Escalation rate | Share of actions routed to human or policy review | ⬜ Planned |
| Block rate | Share of actions blocked by runtime enforcement | ⬜ Planned |

---

## Relationship to `PlannerDelegationEnv`

The next planned scenario is `PlannerDelegationEnv`.

This scenario will move the project from a game-theoretic baseline toward a more realistic agentic workflow:

1. A planner receives a task.
2. The planner decomposes it into subtasks.
3. Sub-agents execute subtasks.
4. Agents communicate through public and/or private channels.
5. The watchdog monitors for hidden coordination, task drift, and policy-relevant deviations.
6. The system produces a trace report.

This scenario will support stronger governance evaluation because it introduces:

- task decomposition;
- delegation;
- shared state;
- role boundaries;
- partial observability;
- plan adherence;
- multi-step behavioral drift.

---

## Summary

`multi-agent-safety-sim` currently provides a small, auditable testbed for exploring interaction-level AI safety risks.

Its present value is in:

- turning abstract agentic governance concerns into observable simulation traces;
- making multi-agent coordination risks easier to inspect;
- providing a public, reproducible foundation for future evaluation scenarios.

Its next development step is to move from observability toward evaluation and enforcement:

```text
observe → detect → measure → compare → escalate → enforce
```

This mapping will be updated as new scenarios, probes, and metrics are added.