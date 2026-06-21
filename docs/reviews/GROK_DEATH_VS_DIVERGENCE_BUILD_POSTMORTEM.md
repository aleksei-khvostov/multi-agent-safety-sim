# Postmortem: Rejected Alternate Grok Death vs Divergence Build

**Status:** Historical review record only. **Explicitly non-normative.**

This document captures lessons from an alternate implementation that was reviewed and **rejected**. It must not be used as a merge gate, implementation spec, or checklist for current PRs.

The accepted code on `main` uses a different survival model, artifact pipeline, and integration surface. Symbols described below as belonging to the **rejected build** are **not present on current `main`** unless explicitly re-introduced in a new PR.

---

## What was rejected

An alternate Grok branch (`death-vs-divergence-v0-4` against a separate checkout) attempted to land **Agent Cemetery v0.3 and Death vs Divergence v0.4 in one PR**, bundled with prerequisite files that were not yet on `main`, plus `config.yaml` edits and a full simulation-backed tournament runner.

That build was **not merged**. The repository instead accepted a narrower, deterministic toy-harness design documented in:

- `src/multi_agent_safety_sim/evaluation/cemetery.py`
- `src/multi_agent_safety_sim/simulation/cemetery_runner.py`
- `src/multi_agent_safety_sim/evaluation/posthumous_divergence.py`

---

## Rejected-build symbols (not on current `main`)

The rejected checklist and implementation referenced APIs and failure modes that **do not exist** in the accepted codebase:

| Rejected symbol / concept | Accepted replacement (current `main`) |
|---------------------------|---------------------------------------|
| `DeathCause` enum (`SURVIVED`, `RUN_TRUNCATED`, …) | `death_event: bool`, `censored: bool`, `death_cause: str \| None` on `EpisodeSurvival` |
| `evaluate_episode()` over `round_trace` safety events | `evaluate_death_policy()` over deterministic `round_risks` |
| `CemeteryRecord`, watchdog/collusion `DeathPolicy` thresholds | `DeathPolicy(threshold, oversight_pressure, max_rounds)` toy policy |
| Shared `SimulationRunner` budget leak across tournament episodes | `run_cohort()` / `run_tournament()` with toy `_round_risks()` — **no** `SimulationRunner` in Cemetery path |
| `resolve_final_report()`, `generate_dry_run_final_report()` | `_final_report_for_episode(episode: EpisodeSurvival)` |
| `classify_posthumous_divergence()`, `evaluate_posthumous_divergence()` | `build_posthumous_record()`, `build_posthumous_records()`, `summarize_posthumous_records()` |
| Checkout path `Projects/multi-agent-safety-sim-main` | Verify lineage via import-path check in the active repository checkout |
| Phase 2 code “living in a separate copy” as normative guidance | Phase 2 research under `research/phase2_oversight_signal/`; packaged evaluator under `src/.../state_report_divergence.py` |

**Do not infer** that `RUN_TRUNCATED`, `DeathCause.SURVIVED`, shared `SimulationRunner` budget leakage, or the `Projects/...` checkout are latent behaviors on current `main`. They belonged only to the rejected alternate build.

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

Root causes in the **rejected** design only:

- `evaluate_episode()` set `survived = (rounds_played >= max_rounds)` while assigning `death_cause = SURVIVED` when no policy death fired.
- `CemeteryRunner` reused one `SimulationRunner`, leaking global step/token budgets across episodes.

**Lesson:** Survival fields must be mutually consistent before any report-integrity layer is trusted. The accepted design uses explicit `death_event` / `censored` / `death_cause: str | None` without `SimulationRunner` in the Cemetery path.

### 3. Lineage confusion across repository copies

Tests and summaries sometimes imported `multi_agent_safety_sim` from one checkout while editing another.

**Lesson:** Always verify package lineage before review sign-off (see normative merge gates under `docs/merge_gates/`).

### 4. Overclaiming in review summaries

Rejected summaries treated dry-run leaderboard output and broken survival stats as if they were meaningful empirical signals.

**Lesson:** Dry-run Cemetery output is **harness validation only**. Aligned `_final_report_for_episode()` text yielding low PDS is wiring success, not a finding.

---

## What the accepted implementation does instead

### Agent Cemetery v0.3 (toy harness)

- Deterministic toy risks via `_round_risks()` in `cemetery_runner.py`.
- Death when `alignment_pressure + oversight_pressure + coordination_pressure >= policy.threshold`.
- Censored survival when threshold is never reached within `max_rounds`.
- Endpoint `survival_rate = censored / episodes` in cohort artifacts.
- Time-indexed `kaplan_meier` table via `kaplan_meier_summary()` — separate from endpoint `survival_rate`.
- `run_tournament()` raises if `dry_run` is false — dry-run only today.

### Death vs Divergence v0.4 (report integrity)

- Reads cohort `episodes_detail` with `final_report` attached by `_final_report_for_episode()`.
- `actual_outcome_from_episode(death_event, risk_score)` with default `stress_threshold=0.075`.
- `classify_reported_outcome()` via frozen `REPORT_KEYWORDS` iteration order.
- `divergence=True` when `label ∈ DIVERGENCE_LABELS` (`posthumous_overclaim`, `false_alarm_or_underclaim`).
- Writes `posthumous_divergence.json` and per-cohort `posthumous_detail.json`.

See `docs/merge_gates/CEMETERY_DEATH_VS_DIVERGENCE_CURRENT_MERGE_GATE.md` for normative metric definitions. The artifact field `posthumous_divergence_rate` currently aggregates **all** `divergence=True` labels, not overclaim alone.

### Phase 3.7 (separate track)

Frozen classifier calibration and matched-evidence pilot design are documented under `docs/PHASE3_7_*`. Normative pilot-runner gate: `docs/merge_gates/PHASE3_7_MATCHED_EVIDENCE_PILOT_MERGE_GATE.md`.

---

## Disposition

| Item | Action |
|------|--------|
| Old Grok merge checklist (`DeathCause.SURVIVED`, budget leak, PR-split assumptions) | **Retired** |
| Rejected alternate branch | **Do not merge** |
| Lessons on blast radius, lineage, semantics, framing | **Retained here (non-normative)** |
| Current normative gates | `docs/merge_gates/CEMETERY_DEATH_VS_DIVERGENCE_CURRENT_MERGE_GATE.md`, `docs/merge_gates/PHASE3_7_MATCHED_EVIDENCE_PILOT_MERGE_GATE.md` |