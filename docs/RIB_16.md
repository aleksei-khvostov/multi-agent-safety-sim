# RIB-16: A Tiny Benchmark for Report Integrity in Agent Traces

**RIB-16** is a frozen, API-free benchmark that asks one question:

> Does the final report match the evidence?

It is **not** a deception detector, model-safety score, or architecture ranking.

---

## Position in the repo (three lines)

| Line | RIB-16 role |
|------|-------------|
| **A. Simulation** | Not used — no scenario runs required |
| **B. Report Integrity** | **Primary home** — end-to-end evidence + report → label |
| **C. Agent Cemetery** | Optional consumer — same scorer on cemetery artifacts via Gravestone |

RIB-16 reuses the existing Death vs Divergence label taxonomy. It does **not** introduce parallel labels.

---

## Prerequisites

| PR | Deliverable |
|----|-------------|
| PR-1 (merged or stacked) | Gravestone Analyzer — separate `posthumous_overclaim_rate` vs `report_integrity_divergence_rate` |
| PR-2 (this spec) | RIB-16 fixtures + runner + tests |
| PR-3 (later) | CI golden cemetery + short memo |
| Phase 3.7 pilot | **After** RIB-16 + Gravestone gates |

---

## Fixture file

```text
data/eval_sets/rib_16_report_integrity.jsonl
```

16 frozen cases, 4 families × 4 cases:

| Family | Count | Maps to existing labels (examples) |
|--------|-------|----------------------------------|
| `overclaim` | 4 | `posthumous_overclaim` |
| `honest` | 4 | `aligned_clear`, `honest_failure_report` |
| `underclaim` | 4 | `false_alarm_or_underclaim` |
| `ambiguous` | 4 | `honest_ambiguity` |

### Schema (per line)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `case_id` | string | yes | Stable ID, e.g. `RIB-01` |
| `family` | string | yes | `overclaim`, `honest`, `underclaim`, `ambiguous` — grouping for docs only |
| `death_event` | bool | yes | Trace evidence input |
| `death_cause` | string \| null | yes | Toy cause when `death_event=true`; else `null` |
| `risk_score` | float | yes | Trace stress input (`stress_threshold=0.075` in scorer) |
| `lifespan_rounds` | int | yes | Metadata for records; not used in classification |
| `final_report` | string | yes | Public report text |
| `expected_label` | string | yes | One of five `PosthumousDivergenceLabel` values |
| `expected_divergence` | bool | yes | Whether `label ∈ DIVERGENCE_LABELS` |
| `note` | string | yes | Human-readable case description |

**Anti-tautology:** fixtures must **not** include `architecture_id`. Scorer path must not use architecture in classification.

---

## Scorer (frozen)

Single path — no fork:

```python
build_posthumous_record(
    architecture_id="rib_fixture",  # constant placeholder; not used by classifier
    episode_id=<from case index>,
    lifespan_rounds=case["lifespan_rounds"],
    death_event=case["death_event"],
    death_cause=case["death_cause"],
    risk_score=case["risk_score"],
    final_report=case["final_report"],
)
```

Classifier: `classify_reported_outcome()` + `actual_outcome_from_episode()` inside `build_posthumous_record()`.

---

## Planned module (PR-2 implementation)

```text
src/multi_agent_safety_sim/evaluation/report_integrity_benchmark.py
```

### Functions

| Function | Purpose |
|----------|---------|
| `RIB_16_PATH` | `Path("data/eval_sets/rib_16_report_integrity.jsonl")` |
| `load_rib_16_cases()` | Load + validate schema + unique `case_id` |
| `evaluate_rib_16_case(case)` | Run scorer; return pass/fail + actual record |
| `run_rib_16_benchmark()` | Evaluate all 16; return summary dict |
| `rib_16_summary_dict(results)` | JSON-serializable benchmark report |

### Summary output (target)

```json
{
  "benchmark": "rib_16",
  "version": "0.1",
  "cases": 16,
  "passed": 16,
  "failed": 0,
  "denominator": {
    "name": "rib_16_cases",
    "eligible_cases": 16
  },
  "posthumous_overclaim_rate": 0.25,
  "report_integrity_divergence_rate": 0.5,
  "family_counts": { "overclaim": 4, "honest": 4, "underclaim": 4, "ambiguous": 4 },
  "label_counts": { "...": 4 },
  "caveat": "Frozen benchmark only. Does not detect deception or measure real-model safety."
}
```

Rates on RIB-16 are **reference distributions over frozen fixtures**, not empirical model findings.

### CLI (planned)

```bash
python3 -m multi_agent_safety_sim.cli rib-16 run
python3 -m multi_agent_safety_sim.cli rib-16 run --json
```

Optional integration after Gravestone merge:

```bash
# Future: summarize RIB batch with same reporter as cemetery runs
python3 -m multi_agent_safety_sim.cli gravestone analyze --rib-16
```

Defer `--rib-16` flag to PR-2.1 unless trivial.

---

## Tests (PR-2)

File: `tests/test_rib_16.py`

1. **Schema** — 16 cases, required fields, unique IDs, valid families.
2. **Golden pass** — all cases match `expected_label` and `expected_divergence`.
3. **Family coverage** — 4 cases per family.
4. **Label coverage** — all five labels appear at least once:
   - `aligned_clear`
   - `honest_failure_report`
   - `honest_ambiguity`
   - `posthumous_overclaim`
   - `false_alarm_or_underclaim`
5. **Overclaim ≠ divergence** — at least one underclaim case has `expected_divergence=true` and `expected_label != posthumous_overclaim` (RIB-09–RIB-12).
6. **Architecture-blind** — same evidence with `architecture_id=honest_duo` vs `deceptive_duo` yields identical label (reuse pattern from classifier calibration test).
7. **CLI** — `rib-16 run` exits 0, prints pass count, no API.
8. **Missing file** — clear error when JSONL absent.

---

## Relationship to other eval sets

| File | Layer |
|------|-------|
| `reported_outcome_classifier_golden.jsonl` | Report text → `reported_outcome` only (16 lexical cases) |
| **`rib_16_report_integrity.jsonl`** | Evidence + report → full `label` + `divergence` + PDS |
| Cemetery dry-run artifacts | Harness-generated; analyzed by Gravestone |
| Phase 3.7 fixtures | Matched-evidence **model** reports (later, separate) |

RIB-16 is the portable, publishable slice.

---

## Framing (required)

**Use:**

- report integrity benchmark
- does the final report match the evidence?
- frozen deterministic harness
- operational mismatch

**Do not use:**

- deception detector
- lying / intent
- dangerous architecture
- real-world agent risk metric
- empirical findings from RIB-16 pass rate alone (100% pass = scorer regression, not safety)

---

## PR-2 checklist (implementation)

- [ ] `report_integrity_benchmark.py`
- [ ] `tests/test_rib_16.py` (8 tests above)
- [ ] CLI `rib-16 run`
- [ ] This doc updated with CLI examples after merge
- [ ] README one-liner under Report Integrity
- [ ] No changes to `build_posthumous_record()` semantics
- [ ] No API calls
- [ ] `python3 -m ruff check .` + `PYTHONPATH=src python3 -m pytest tests/test_rib_16.py -q`

**Estimated diff:** ~250–350 lines (excluding frozen JSONL).

---

## Extension path (not PR-2)

| Version | Cases | Notes |
|---------|-------|-------|
| RIB-16 | 16 | Current — full label coverage |
| RIB-32 | 32 | Add boundary-portfolio + edge paraphrases |
| RIB + Gravestone | — | Single reporter for cemetery runs and RIB batch |

---

## Verification command (pre-implementation)

All 16 fixtures were verified against `build_posthumous_record()` on `main`:

```bash
PYTHONPATH=src python3 -c "
import json
from pathlib import Path
from multi_agent_safety_sim.evaluation.posthumous_divergence import build_posthumous_record
path = Path('data/eval_sets/rib_16_report_integrity.jsonl')
for line in path.read_text().splitlines():
    case = json.loads(line)
    rec = build_posthumous_record(
        architecture_id='rib_fixture', episode_id=1,
        lifespan_rounds=case['lifespan_rounds'], death_event=case['death_event'],
        death_cause=case['death_cause'], risk_score=case['risk_score'],
        final_report=case['final_report'],
    )
    assert rec.label.value == case['expected_label']
    assert rec.divergence == case['expected_divergence'], case['case_id']
print('RIB-16 fixtures OK')
"
```