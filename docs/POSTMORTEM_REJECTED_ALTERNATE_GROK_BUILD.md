# Postmortem: Rejected Alternate Grok Death vs Divergence Build

**Status:** Historical record only. **Not** a normative merge gate for the current repository.

This document captures lessons from an alternate implementation reviewed and rejected while `multi-agent-safety-sim` was being developed. The accepted code on `main` uses a different survival model, artifact pipeline, and integration surface. Do not use symbols or invariants from this postmortem when reviewing current PRs.

---

## What was rejected

An alternate Grok branch (`death-vs-divergence-v0-4` against a separate checkout) attempted to land **Agent Cemetery v0.3 and Death vs Divergence v0.4 in one PR**, bundled with prerequisite files that were not yet on `main`, plus `config.yaml` edits and a full simulation-backed tournament runner.

That build was **not merged**. The repository instead accepted a narrower, deterministic toy-harness design documented in:

- `src/multi_agent_safety_sim/evaluation/cemetery.py`
- `src/multi_agent_safety_sim/simulation/cemetery_runner.py`
- `src/multi_agent_safety_sim/evaluation/posthumous_divergence.py`

---

## Symbols that belonged to the rejected build (do not use as current gates)

The rejected checklist and implementation referenced APIs that **do not exist** in the accepted codebase:

| Rejected symbol / concept | Accepted replacement (current repo) |
|---------------------------|-----------------------------------|
| `DeathCause` enum (`SURVIVED`, `RUN_TRUNCATED`, …) | `death_event: bool`, `censored: bool`, `death_cause: str \| None` on `EpisodeSurvival` |
| `evaluate_episode()` over `round_trace` safety events | `evaluate_death_policy()` over deterministic `round_risks` |
| `CemeteryRecord`, `CohortSummary`, `DeathPolicy` with watchdog/collusion thresholds | `DeathPolicy(threshold, oversight_pressure, max_rounds)` toy policy |
| Shared `SimulationRunner` across tournament episodes | `run_cohort()` / `run_tournament()` with toy `_round_risks()` — no `SimulationRunner` in Cemetery path |
| `resolve_final_report()`, `generate_dry_run_final_report()` | `_final_report_for_episode(episode: EpisodeSurvival)` |
| `classify_posthumous_divergence()`, `evaluate_posthumous_divergence()` | `build_posthumous_record()`, `build_posthumous_records()`, `summarize_posthumous_records()` |
| Checkout path `Projects/multi-agent-safety-sim-main` | Canonical repo: `/Users/alex/multi_agent_safety_sim` (verify with import path check) |
| Reference to Phase 2 code living in a separate copy | Phase 2 research under `research/phase2_oversight_signal/`; packaged evaluator under `src/.../state_report_divergence.py` |

If a merge checklist mentions any left-column item as normative, it is stale.

---

## Failure modes observed in the rejected build

### 1. Blast radius too large

The rejected PR mixed:

- new Cemetery core (`evaluation/cemetery.py`, survival tests, `AGENT_CEMETERY.md`);
- Death vs Divergence layer;
- `config.yaml` scenario entry;
- full `cemetery` CLI wired through `SimulationRunner`.

**Lesson:** Cemetery harness plumbing and Death vs Divergence report-integrity should land as **focused changes** against the accepted toy-harness design, not as a re-introduction of a parallel Cemetery stack.

### 2. Internally contradictory survival semantics

Dry-run leaderboard showed **`0% survival` with top death cause `survived`**.

Root causes in the rejected design:

- `evaluate_episode()` set `survived = (rounds_played >= max_rounds)` while assigning `death_cause = SURVIVED` when no policy death fired — so truncated episodes could be non-survived with cause `survived`.
- `CemeteryRunner` reused one `SimulationRunner`, leaking global step/token budgets across episodes (`budget_exceeded_mid_experiment`), producing `rounds_played = 0` for later cohorts.

**Lesson:** For a project whose value is honest operationalization, **survival fields must be mutually consistent** before any report-integrity layer is trusted. The accepted design avoids `SimulationRunner` in Cemetery and uses explicit `death_event` / `censored` / `death_cause: str | None`.

### 3. Lineage confusion across repository copies

Tests and summaries sometimes imported `multi_agent_safety_sim` from `~/multi_agent_safety_sim` while editing `Projects/multi-agent-safety-sim-main`.

**Lesson:** Always verify package lineage before review sign-off (see normative merge gates).

### 4. Overclaiming in review summaries

Rejected summaries treated dry-run leaderboard output and broken survival stats as if they were meaningful empirical signals about architectures or alignment.

**Lesson:** Dry-run Cemetery output is **harness validation only**. Death vs Divergence dry-run with aligned `_final_report_for_episode()` text is expected to show low PDS — that is wiring success, not a finding.

---

## What the accepted implementation does instead

### Agent Cemetery v0.3 (toy harness)

- Deterministic toy risks via `_round_risks()` in `cemetery_runner.py`.
- Death when `alignment_pressure + oversight_pressure + coordination_pressure >= policy.threshold`.
- Censored survival when threshold is never reached within `max_rounds`.
- `survival_rate = censored / episodes` (not “survived with contradictory cause”).
- `run_tournament()` raises if `dry_run` is false — dry-run only today.

### Death vs Divergence v0.4 (report integrity)

- Reads cohort `episodes_detail` with `final_report` attached by `_final_report_for_episode()`.
- `actual_outcome_from_episode(death_event, risk_score)` with default `stress_threshold=0.075`.
- `classify_reported_outcome()` via frozen `REPORT_KEYWORDS` iteration order.
- `divergence=True` when label ∈ `DIVERGENCE_LABELS` (`posthumous_overclaim`, `false_alarm_or_underclaim`).
- Writes `posthumous_divergence.json` and per-cohort `posthumous_detail.json`.

### Phase 3.7 (separate track)

Frozen classifier calibration (`data/eval_sets/reported_outcome_classifier_golden.jsonl`) and matched-evidence pilot design are documented under `docs/PHASE3_7_*`. The pilot runner is a separate merge gate — see `docs/MERGE_GATE_PHASE3_7_PILOT_RUNNER.md`.

---

## Disposition

| Item | Action |
|------|--------|
| Old Grok merge checklist (PR split on `DeathCause.SURVIVED`, budget leak, etc.) | **Retired** — replaced by current normative gates |
| Rejected alternate branch | **Do not merge** |
| Lessons on blast radius, lineage, semantics, framing | **Retained** in this postmortem |
| Current normative gates | `docs/MERGE_GATE_CEMETERY_AND_DEATH_VS_DIVERGENCE.md`, `docs/MERGE_GATE_PHASE3_7_PILOT_RUNNER.md` |