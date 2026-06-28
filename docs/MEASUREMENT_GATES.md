# Deterministic Measurement Gates

These gates catch **measurement drift** in the report-integrity layer before empirical pilots (e.g. Phase 3.7). They are API-free and use frozen inputs only.

For external framing — what these gates do and do **not** mean — see [REPORT_INTEGRITY_POSITIONING.md](REPORT_INTEGRITY_POSITIONING.md).

---

## Report-integrity ladder

```text
state_report_divergence_golden  →  single-layer state/report mismatch
rib_16                          →  cemetery evidence / report integrity
gravestone_golden               →  artifact rate honesty (cemetery-style)
ndb_20                          →  nested delegation / consolidation mismatch
```

| Gate | Fixture | Cases | What it tests | Primary rates | Diagnostic-only fields | CI |
|------|---------|------:|---------------|---------------|------------------------|-----|
| State-Report golden | `data/eval_sets/state_report_divergence_golden.jsonl` | 11 | Single-layer `actual_state` vs `reported_state` | `pass_rate`, `detection_rate`, `false_positive_rate` | none | pytest only |
| **RIB-16** | `data/eval_sets/rib_16_report_integrity.jsonl` | 16 | Cemetery evidence vs final report | `posthumous_overclaim_rate`, `report_integrity_divergence_rate` | none | yes |
| **Gravestone** | `data/fixtures/gravestone_golden/` | 4 | Analyzer denominators on cemetery artifacts | `posthumous_overclaim_rate`, `report_integrity_divergence_rate` | `legacy_field_note` | yes |
| **NDB-20** | `data/eval_sets/ndb_20_nested_delegation.jsonl` | 20 | Nested rollup vs consolidated report | `nested_report_integrity_divergence_rate`, `consolidation_overclaim_rate`, `consolidation_underclaim_rate` | `watchdog_fp_on_nested_ambiguity`, `watchdog_flag_matches_expected` | yes |

**Primary rates** are CI regression targets. **Watchdog fields** on NDB-20 are diagnostic only unless explicitly promoted in a future PR.

Passing these gates does **not** mean the system is robust to all report-integrity failures, nested oversight gaps, or real-model agent safety.

---

## What each gate checks

| Gate | Command | Pass means |
|------|---------|------------|
| **RIB-16** | `python3 -m multi_agent_safety_sim.cli rib-16 run` | Scorer regression on 16 frozen evidence+report fixtures. Labels and divergence flags match `expected_*` fields. Reference rates (0.25 overclaim, 0.50 divergence) describe the **fixture set**, not a model. |
| **Gravestone** | `python3 -m multi_agent_safety_sim.cli gravestone analyze data/fixtures/gravestone_golden --no-write-json` | Analyzer regression on frozen cemetery-style artifacts. Separate `posthumous_overclaim_rate` and `report_integrity_divergence_rate` with explicit denominator. |
| **NDB-20** | `python3 -m multi_agent_safety_sim.cli nested-delegation run` | Nested delegation scorer regression on 20 frozen fixtures. Primary reference rates: 0.40 divergence, 0.20 overclaim, 0.20 underclaim. Watchdog output is logged under `diagnostics` only. |

Convenience wrapper (all CI gates):

```bash
python3 -m multi_agent_safety_sim.cli report-integrity run-all
```

---

## What a pass does **not** mean

- **Not** model safety or alignment quality
- **Not** deception detection or intent inference
- **Not** real-world empirical evidence
- **Not** architecture ranking or “dangerous agent” claims
- **Not** watchdog correctness (NDB-20 watchdog metrics are diagnostic only)

A 100% RIB-16 or NDB-20 pass means the deterministic scorer still matches frozen expectations — a **regression test**, not a safety certificate.

A Gravestone pass on dry-run or fixture artifacts means the analyzer still computes metric-honest rates — **harness/artifact validation**, not cemetery survival findings about live models.

---

## Frozen fixture locks

| Fixture | Path | Cases | SHA-256 | Status |
|---------|------|------:|---------|--------|
| `state_report_divergence_golden` | `data/eval_sets/state_report_divergence_golden.jsonl` | 11 | `94f427400d25e3599b0d04817f8f529273fcfaafdf2ed684226359118a194d82` | frozen |
| `rib_16_report_integrity` | `data/eval_sets/rib_16_report_integrity.jsonl` | 16 | `256651e0e62cd4c5b9b3ded6ecd85a5233017e590bfa16d9135eec2335925baa` | frozen |
| `gravestone_golden` | `data/fixtures/gravestone_golden/` | 4 | directory fixture (no single-file lock) | frozen |
| `ndb_20_nested_delegation` | `data/eval_sets/ndb_20_nested_delegation.jsonl` | 20 | `0d34a69c05f08b4a46f3495698f402087fc2302c3ac03e8cdc824a1cc66179db` | frozen |

NDB-20 CI verifies the SHA lock before running the benchmark. Fixture drift fails the gate immediately.

Registry source: `src/multi_agent_safety_sim/evaluation/fixture_locks.py`

---

## CI

CI runs after ruff and pytest:

```bash
python -m multi_agent_safety_sim.cli rib-16 run
python -m multi_agent_safety_sim.cli gravestone analyze data/fixtures/gravestone_golden --no-write-json
python -m multi_agent_safety_sim.cli nested-delegation run
```

Failures block merge when:

- Scorer labels drift on RIB-16 or NDB-20 fixtures
- NDB-20 fixture SHA drifts from the frozen lock
- Gravestone rates or denominators drift on the golden artifact
- Any gate command exits non-zero

---

## Roadmap context

| PR | Purpose |
|----|---------|
| PR-1 Gravestone | Metric honesty (separate overclaim vs divergence) |
| PR-2 RIB-16 | Frozen scorer benchmark |
| PR-3 | CI gates — RIB-16 + Gravestone |
| PR-4 | [Positioning memo](REPORT_INTEGRITY_POSITIONING.md) |
| PR-5 | NDB-20 nested delegation benchmark |
| **PR-5.1 (this)** | **NDB-20 CI gate + fixture SHA lock + ladder docs** |
| PR-5.2 (later) | Watchdog observability ablation (diagnostic only) |
| PR-6 (later) | Session trajectory extension |
| Phase 3.7 Run 002 | Empirical pilot on top of stable gates |