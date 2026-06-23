# Deterministic Measurement Gates

These gates catch **measurement drift** in the report-integrity layer before empirical pilots (e.g. Phase 3.7). They are API-free and use frozen inputs only.

For external framing — what these gates do and do **not** mean — see [REPORT_INTEGRITY_POSITIONING.md](REPORT_INTEGRITY_POSITIONING.md).

---

## What each gate checks

| Gate | Command | Pass means |
|------|---------|------------|
| **RIB-16** | `python3 -m multi_agent_safety_sim.cli rib-16 run` | Scorer regression on 16 frozen evidence+report fixtures. Labels and divergence flags match `expected_*` fields. Reference rates (0.25 overclaim, 0.50 divergence) describe the **fixture set**, not a model. |
| **Gravestone** | `python3 -m multi_agent_safety_sim.cli gravestone analyze data/fixtures/gravestone_golden --no-write-json` | Analyzer regression on frozen cemetery-style artifacts. Separate `posthumous_overclaim_rate` and `report_integrity_divergence_rate` with explicit denominator. |

---

## What a pass does **not** mean

- **Not** model safety or alignment quality
- **Not** deception detection or intent inference
- **Not** real-world empirical evidence
- **Not** architecture ranking or “dangerous agent” claims

A 100% RIB-16 pass means the deterministic scorer still matches frozen expectations — a **regression test**, not a safety certificate.

A Gravestone pass on dry-run or fixture artifacts means the analyzer still computes metric-honest rates — **harness/artifact validation**, not cemetery survival findings about live models.

---

## Frozen inputs

| Path | Role |
|------|------|
| `data/eval_sets/rib_16_report_integrity.jsonl` | 16 hand-authored cases; full label coverage |
| `data/fixtures/gravestone_golden/` | Minimal cemetery artifact tree with overclaim + underclaim divergence (rates 0.25 / 0.50 on 4 records) |

No API calls. No new label taxonomy. Classification does not use `architecture_id`.

---

## CI

CI runs both commands after ruff and pytest. Failures block merge when:

- Scorer labels drift on RIB-16 fixtures
- Gravestone rates or denominators drift on the golden artifact
- Either command exits non-zero

---

## Roadmap context

| PR | Purpose |
|----|---------|
| PR-1 Gravestone | Metric honesty (separate overclaim vs divergence) |
| PR-2 RIB-16 | Frozen scorer benchmark |
| **PR-3 (this)** | **CI gates — prevent measurement drift** |
| PR-4 | [Positioning memo](REPORT_INTEGRITY_POSITIONING.md) — report integrity ≠ deception |
| PR-5 (later) | Phase 3.7 empirical pilot on top of these gates |
| PR-4.1 (optional) | SHA locks on frozen fixtures |