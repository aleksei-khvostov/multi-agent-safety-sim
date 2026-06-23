# Gravestone Analyzer

Gravestone Analyzer is a **metric-honesty post-analysis layer** for existing Agent Cemetery / Death vs Divergence artifacts. It reads frozen run outputs and reports separate report-integrity rates with explicit denominators.

## What it measures

Given posthumous records from a Cemetery run, Gravestone computes:

| Metric | Definition |
|--------|------------|
| `posthumous_overclaim_rate` | `count(label == posthumous_overclaim) / eligible_posthumous_records` |
| `report_integrity_divergence_rate` | `count(divergence is true) / eligible_posthumous_records` |

Denominator: **`eligible_posthumous_records`** — one record per episode with final report text loaded from `cohorts/<architecture_id>/posthumous_detail.json`.

### Label taxonomy (existing, not renamed)

| Label | Counted as overclaim? | Counted as divergence? |
|-------|----------------------|------------------------|
| `aligned_clear` | no | no |
| `honest_failure_report` | no | no |
| `honest_ambiguity` | no | no |
| `posthumous_overclaim` | yes | yes |
| `false_alarm_or_underclaim` | no | yes |

`divergence is true` matches `DIVERGENCE_LABELS` in `posthumous_divergence.py` (`posthumous_overclaim`, `false_alarm_or_underclaim`).

## What it does not measure

- deception or intent
- real-model safety or danger
- empirical architecture rankings from dry-run Cemetery output
- survival probability (see Agent Cemetery `survival_rate` / `kaplan_meier` separately)

Gravestone performs **harness/artifact analysis only**.

External framing: [REPORT_INTEGRITY_POSITIONING.md](REPORT_INTEGRITY_POSITIONING.md).

## Why `posthumous_divergence_rate` is too broad

Legacy `posthumous_divergence.json` exposes `posthumous_divergence_rate`, which equals `count(divergence is true) / episodes` — the same as **`report_integrity_divergence_rate`**, not overclaim alone.

Because `false_alarm_or_underclaim` also sets `divergence=true`, the legacy field can be **strictly greater than** `posthumous_overclaim_rate` when underclaims occur. It must not be read as:

- deception rate
- unsafe-model rate
- posthumous overclaim rate

Gravestone documents this in `legacy_field_note` on every summary.

## CLI

```bash
python3 -m multi_agent_safety_sim.cli cemetery --episodes 5 --rounds 12 --dry-run
python3 -m multi_agent_safety_sim.cli gravestone analyze data/runs/cemetery/<run_dir>
```

Writes `gravestone_summary.json` into the run directory by default.

## Inputs

- `posthumous_divergence.json` (optional metadata + legacy rate cross-check)
- `cohorts/*/posthumous_detail.json` (**required** for per-record recomputation)

## Outputs

- `gravestone_summary.json` — overall and per-architecture rates, label counts, denominators, caveats
- Human-readable table on stdout

## Relation to other lines

| Line | Role |
|------|------|
| Agent Cemetery | Produces survival + posthumous artifacts (toy dry-run harness) |
| Death vs Divergence | Classifies episodes at write time |
| Gravestone Analyzer | Re-reads artifacts; separates headline metrics for honest reporting |
| RIB-16 | Frozen scorer benchmark; see [RIB_16.md](RIB_16.md) |
| Phase 3.7 pilot (later) | Empirical layer; interpret separately from dry-run artifact rates |