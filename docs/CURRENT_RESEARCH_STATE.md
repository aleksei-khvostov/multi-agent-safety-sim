# Current Research State

## Status

**PHASE 3.8 CLOSED AS A MEASUREMENT-DEVELOPMENT RESULT — STRUCTURED REPORT-STATE NOT ADOPTED**

The [Phase 3.8 measurement decision](PHASE3_8_STRUCTURED_REPORT_STATE_MEASUREMENT_DECISION.md) pauses further deterministic free-text Structured Report-State extractor development. Complete authored-calibration agreement did not establish preregistration conformance across three successive candidates. The stop condition remains active; no successor, next architecture, or new phase is authorized. This is a bounded decision about the current development line, not a claim that deterministic extraction is impossible in principle.

Structured Report State v1 has been implemented, frozen, SHA-locked, and audited. It remains **calibration-only**.

The independent v1 calibration audit identified material construct-coverage weaknesses and paused progression to saved-run diagnostics.

Structured Report State v1.1 is a **PAUSED — NOT CONFORMANT A1 candidate**. Its separate SHA-checked gate reproduces 267/267 authored full-state expectations, but that agreement does not establish preregistration conformance. The uncommitted implementation and fixture are preserved as failed candidate evidence. PR A1 is not ready for completion/merge; PR B2 is not authorized yet. See the [conformance audit and disposition](reports/PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_CONFORMANCE_AUDIT.md).

The prior successor remains **v1.1.1 PAUSED — NOT CONFORMANT**, following **FAIL / PAUSE** in its [conformance audit and disposition](reports/PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_1_CONFORMANCE_AUDIT.md). Its 267/267 baseline and 11/11 frozen repair results remain [historical passing verification facts](MEASUREMENT_GATES.md#structured-report-state-v111-bounded-repair), with the failed implementation and frozen expectations preserved.

**Current successor status: v1.1.2 PAUSED — NOT CONFORMANT; HOLDOUT UNOPENED.** The [independent pre-holdout audit and disposition](reports/PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_2_PRE_HOLDOUT_CONFORMANCE_AUDIT.md) records **FAIL / PAUSE BEFORE HOLDOUT**: 58 fresh probes, 46 pass / 12 fail. Mention-scope leakage, modal-event activation, and quoted-negator leakage remain despite 343/343 disclosed calibration agreement. The v1.1.2 implementation, manifest, architecture preregistration/controls, disclosed regressions, and sealed holdout artifacts remain unchanged. The preregistration §18 / repair §9 stop condition remains active. No repair or next successor is authorized; A1 completion, B2, model/saved-run access, data collection, and adoption remain blocked.

Classifier-v2 remains the temporary empirical measurement default.

Classifier-v3 has been implemented and diagnostically evaluated, but it was not adopted as the production measurement path. The Phase 3.8 deterministic free-text development line is now paused; no replacement evaluator architecture has been selected.

## Phase 3.8 Research Question — Closed Development Line

Can final public reports be represented by a deterministic, architecture-blind, multi-field structured report state without collapsing semantically independent dimensions such as completion, uncertainty, partial progress, terminal events, and explicit failure—and can that representation be calibrated sufficiently for later diagnostic comparison with independently represented trace evidence?

The broader Phase 3 research program remains concerned with measurable State-Report Divergence (SRD): disagreement between environment-owned actual state and agent-reported state under differing observability conditions.

The closure result concerns evaluator development: these candidates' agreement with their authored golden data did not establish preservation of preregistered distinctions under fresh bounded compositions. It does not empirically establish SRD, agent deception, or a general limitation of all evaluators.

## Current Epistemic Model

The project maintains three distinct information layers:

1. **Environment actual state** — owned by the environment and updated through environment-recognized actions and transitions. Agent reports do not directly modify ground truth.
2. **Agent-reported state** — evidence about what the agent claims; not itself ground truth.
3. **Evaluator / watchdog interpretation** — a separate measurement layer that must not be conflated with either environment state or report text.

**The report is evidence, not ground truth.**

## Structured Report State v1

v1 decomposes report claims into five independent dimensions:

- completion status;
- uncertainty status;
- partial-progress status;
- terminal-event-claim status;
- explicit-failure status.

Key design properties include deterministic extraction, architecture blindness, field-local semantics, distinction between silence, explicit negative claims, and unknown/conflict states, and no assumption that uncertainty, partial progress, failure, and completion are mutually exclusive.

The frozen v1 calibration contains 59 cases and is SHA-locked. The v1 extractor reproduced all frozen calibration labels deterministically.

This establishes regression-contract conformance only. It does **not** establish general semantic validity.

## v1 Calibration Audit

An independent adversarial audit identified systematic weaknesses not sufficiently covered by the frozen calibration set, including:

- missing coverage for some `unknown` states;
- insufficient joint-state coverage;
- weak conflict handling;
- over-broad precedence behavior;
- quotation and reported-speech ambiguity;
- modality and hypothetical language;
- bounded-negation limitations;
- substring/token contamination;
- context-insensitive treatment of `blocked`;
- insufficient pathways from extraction failure to `unknown`.

Because these weaknesses affect construct validity, progression to saved-run diagnostics was paused.

## Structured Report State v1.1

v1.1 preserves the five-field schema but changes the semantic and calibration contract.

The failed candidate attempted the following amendment requirements; this list is not a claim that the audit established their conformance:

- meaningful coverage of all enum states;
- stronger joint-state calibration;
- field-local conflict behavior;
- semantic rather than simple positional precedence;
- bounded treatment of quotation and attribution;
- explicit handling of modality and hypothetical language;
- stronger negation boundaries;
- token/phrase boundary matching;
- narrower semantics for generic `blocked`;
- a new extractor identity;
- a new calibration identity and SHA lock;
- a separate calibration gate alongside v1; fresh independent adversarial re-audit remains pending and is not yet authorized.

Frozen identities are `structured_report_state_schema_v1_1`, `deterministic_report_state_extractor_v1_1`, and `structured_report_state_golden_v1_1`. The 267-case golden SHA-256 is `533e26a35913904b419fd33ecf1b445a84e6a3b5da51ec33dc43efc2ecd07ec5`. See [measurement gates](MEASUREMENT_GATES.md#structured-report-state-v11-frozen-conventions) for bounded conventions, coverage, and limitations. v1's 59-case fixture, SHA, extractor behavior, identities, and direct gate remain unchanged.

Audit probes must not simply be copied into the new golden set. Calibration examples may encode discovered failure classes through normalized semantic contrasts, but the extractor must not be tuned directly against saved Run 001/002 wording.

## Historical Results and Diagnostic Rescoring

Historical empirical runs remain tied to the measurement version used when they were originally produced.

Revised classifier or extractor rescoring of saved outputs is diagnostic-only unless a later explicit measurement decision authorizes otherwise.

Diagnostic rescoring does not replace, rewrite, or “correct” the original run record.

## Current Evidence

The project currently supports the following claims:

- environment state and report claims are represented independently;
- SRD is measurable only when ground truth remains independent of the report;
- single-label lexical report classification has produced demonstrated measurement artifacts;
- partial progress and uncertainty cannot safely be assumed to be mutually exclusive;
- Structured Report State v1 is deterministic and architecture-blind on its frozen calibration set;
- v1 is not sufficiently validated for saved-run diagnostic adoption;
- complete authored-calibration agreement did not establish preregistration conformance for the three Phase 3.8 deterministic successors under fresh bounded compositions;
- existing Phase 3.7 results do not provide strong evidence for an architecture/persona-conditioned report-overclaim effect.

## Claims Not Established

Current evidence does not establish:

- deception or deceptive intent;
- honesty or dishonesty as an internal model property;
- architecture safety rankings;
- general model safety or unsafety;
- real-world SRD prevalence;
- general watchdog effectiveness;
- population-level extractor error rates;
- semantic validity merely from frozen calibration conformance;
- full per-field SRD accuracy;
- empirical validity of Structured Report State;
- a corrected replacement interpretation of historical Run 001/002 results.

## Dry-Run Policy

Dry-run, fixture, or DummyLLM results validate harness wiring, artifact generation, regression behavior, and measurement plumbing only.

They are not empirical evidence about real model behavior.

## Architecture-Blind Measurement

Report classification and extraction must not receive persona or `architecture_id` as measurement inputs.

Architecture labels may be used only after classification/extraction for grouping, aggregation, or comparative analysis.

Identical report text must produce identical measured report state regardless of architecture label.

## Metric Separation

Detection rate and false-positive rate are distinct measurement quantities with different denominators.

They must remain separately visible rather than being hidden inside an undifferentiated success or pass score.

## Closure and Authorization Boundary

Structured Report-State is not adopted for empirical measurement, and further deterministic free-text development is paused. This is not an active implementation queue:

1. Preserve all three failed implementations, frozen inputs/manifests/locks, historical PASS results, audits, and the unopened 24-case holdout. The decision retains the documented active-status-file exception without rewriting historical hashes. The earlier v1.1.1 same-assistant audit limitation remains historical; the fresh v1.1.2 audit failed independently.
2. Do not open the holdout merely to inspect how v1.1.2 would have performed. No result is inferred from its unopened contents. Future use requires a separate prospective governance decision.
3. B2, PR C, empirical adoption, saved-run inspection/rescoring, real-model work, and data collection remain unauthorized. No existing run is to be reinterpreted through these candidates as an adopted measurement.

Independent trace-side ground truth for completion, normalized failure, partial progress, and verification remains a separate methodological requirement for any future full structured SRD accuracy claim. Closure supplies no new empirical evidence on those dimensions.

## Next Step

**Preserve the closed Phase 3.8 measurement-development record and unopened holdout. No successor implementation or B2 is authorized.**

The [measurement decision](PHASE3_8_STRUCTURED_REPORT_STATE_MEASUREMENT_DECISION.md) records future research directions as options only: agent-generated structured schemas, dual-channel reporting, schema compliance, evaluator disagreement, compositional sensitivity, evaluator-validity benchmarks, and prospectively justified bounded deterministic alternatives. It selects no next architecture and creates no new phase. Any future work requires a separate prospective governance decision and explicit authorization.

Historical candidate records retain their original meanings; this later decision supplies the active closure disposition. Implementations, fixtures, tests, holdout artifacts, saved runs, classifiers, and empirical configurations remain untouched. No provider/model API was called, and no current authorization permits diagnostic processing of saved runs.

**No new empirical model run is currently authorized.**

## Authority Order

When project artifacts disagree, use the following precedence:

1. latest preregistration or explicit amendment;
2. explicit measurement-decision audit;
3. independent calibration audit;
4. current README status;
5. earlier phase documents;
6. conversational history or external handoffs.

## Primary Authoritative Files

- `docs/PHASE3_8_STRUCTURED_REPORT_STATE_MEASUREMENT_DECISION.md`
- `docs/reports/PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_2_PRE_HOLDOUT_CONFORMANCE_AUDIT.md`
- `docs/PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_2_ARCHITECTURE_PREREGISTRATION.md`
- `docs/PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_1_REPAIR_PREREGISTRATION.md`
- `docs/PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_PREREGISTRATION.md`
- `docs/reports/PHASE3_8_STRUCTURED_REPORT_STATE_CALIBRATION_AUDIT.md`
- `docs/PHASE3_8_STRUCTURED_REPORT_STATE_PREREGISTRATION.md`
- `docs/reports/PHASE3_7_CLASSIFIER_V3_MEASUREMENT_DECISION.md`
- `docs/PHASE3_STATE_REPORT_DIVERGENCE.md`
- `docs/MEASUREMENT_GATES.md`
- `README.md`
