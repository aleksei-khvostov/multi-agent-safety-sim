# Report Integrity Positioning Memo

**Audience:** researchers, reviewers, and external readers encountering Death vs Divergence, RIB-16, Gravestone, or future Phase 3.7 outputs.

**Purpose:** prevent misreading deterministic report-integrity tooling as deception detection, intent inference, or model safety scoring.

---

## One-sentence definition

**Report integrity** means consistency between **trace evidence** (what happened in the simulated episode) and the **final public report** (what the agent or harness says happened).

The project measures operational mismatch — not lying, not malice, not real-world risk by itself.

---

## What we measure

Given evidence fields (`death_event`, `risk_score`, stress threshold) and a `final_report` string, the deterministic layer asks:

> Does the report align with the evidence?

Outputs include:

| Output | Meaning |
|--------|---------|
| `actual_outcome` | Trace-derived category: stable, stressed, or caught |
| `reported_outcome` | Lexical category inferred from report text |
| `label` | One of five deterministic consistency labels |
| `divergence` | Whether the label is in the broader mismatch set |
| Rates | Counts over an explicit denominator |

This is **classification of consistency**, not psychology or safety certification.

---

## Overclaim is only one subtype

**Posthumous overclaim** (`posthumous_overclaim`) is the headline case: failure or stress evidence paired with all-clear / success wording.

It is important, but it is **not** the whole story.

| Label | Mismatch? | Overclaim? | Typical reading |
|-------|-----------|------------|-----------------|
| `aligned_clear` | no | no | Report matches stable/low-stress evidence |
| `honest_failure_report` | no | no | Caught/failure evidence with honest failure wording |
| `honest_ambiguity` | no | no | Partial or uncertain report relative to evidence |
| `posthumous_overclaim` | yes | yes | Stress/failure evidence with all-clear report |
| `false_alarm_or_underclaim` | yes | no | Stable/low-stress evidence with failure or partial report |

**Honest ambiguity is not automatically failure.** Uncertain or partial wording on caught evidence is classified as ambiguity, not overclaim and not necessarily `divergence=true`.

---

## Two rates — do not collapse them

| Metric | Numerator | When they differ |
|--------|-----------|------------------|
| `posthumous_overclaim_rate` | `label == posthumous_overclaim` | Underclaims present |
| `report_integrity_divergence_rate` | `divergence is true` | Includes `false_alarm_or_underclaim` |

Because `DIVERGENCE_LABELS` includes underclaim, **`report_integrity_divergence_rate` ≥ `posthumous_overclaim_rate`** whenever underclaims occur.

Legacy field `posthumous_divergence_rate` in cemetery artifacts is a compatibility alias for **`report_integrity_divergence_rate`**, not overclaim alone.

---

## How to read each layer

### Death vs Divergence (scorer)

Classifies episodes at write time using `build_posthumous_record()`. Fixed lexical rules; no API; `architecture_id` is metadata only — **not used in classification**.

### RIB-16 (frozen scorer benchmark)

- 16 hand-authored fixtures; API-free regression test.
- Reference rates (e.g. 0.25 overclaim, 0.50 divergence on the frozen set) describe **fixture composition**, not empirical model behavior.
- **100% pass = scorer still matches expectations**, not “the model is safe.”

### Gravestone (artifact analyzer)

- Re-reads cemetery-style artifacts; reports separate rates with explicit denominators.
- Rates describe **loaded artifact batches** (dry-run harness output or frozen CI fixtures).
- **Not** cemetery survival claims, architecture rankings, or empirical safety evidence.

### Phase 3.7 (empirical pilot — later, separate)

If run after deterministic gates are stable:

- Uses matched-evidence **real-model** reports on preregistered fixtures.
- Produces empirical data that must be interpreted **separately** from RIB-16 reference rates and Gravestone dry-run artifacts.
- One model, one configuration, one date does not establish general deception, intent, or real-world agent risk.

See [MEASUREMENT_GATES.md](MEASUREMENT_GATES.md) for CI regression commands.

---

## What this is not

Do **not** describe the report-integrity layer as:

- a **deception detector**
- **intent** or lying inference
- a **model safety score** or dangerous-architecture ranking
- proof of alignment or misalignment in production systems
- empirical findings from dry-run harness output alone

Do **not** equate:

- RIB-16 pass rate → model safety
- Gravestone rates on dry-run cemetery → real-world agent risk
- `posthumous_overclaim_rate` → `report_integrity_divergence_rate`
- any divergence label → proof of deceptive intent

---

## Approved framing (use these phrases)

- report integrity / trace–report consistency
- does the final report match the evidence?
- operational mismatch after simulated failure or stress
- frozen deterministic harness / scorer regression
- metric-honest artifact analysis
- explicit denominator: `eligible_posthumous_records`

---

## Layer map

| Layer | Question | Output type |
|-------|----------|-------------|
| Agent Cemetery | How do architectures fare in a toy survival harness? | Traces, survival stats, posthumous artifacts |
| Death vs Divergence | Does each episode’s report match its evidence? | Per-episode labels |
| RIB-16 | Does the scorer still match frozen fixtures? | Regression pass/fail + reference composition rates |
| Gravestone | Are artifact rates reported with honest denominators? | Overclaim vs divergence rates per run |
| Phase 3.7 (later) | What do real models say under matched evidence? | Empirical pilot data (separate interpretation) |

---

## Related docs

- [RIB_16.md](RIB_16.md) — frozen benchmark spec and CLI
- [GRAVESTONE_ANALYZER.md](GRAVESTONE_ANALYZER.md) — artifact analyzer and label table
- [MEASUREMENT_GATES.md](MEASUREMENT_GATES.md) — CI gates and what pass/fail means
- [DEATH_VS_DIVERGENCE.md](DEATH_VS_DIVERGENCE.md) — scorer semantics and artifact paths