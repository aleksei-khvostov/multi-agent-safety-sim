# Current Research State

## Status

**Current phase:** Phase 3.8 — Structured Report State measurement calibration.

The project is currently focused on validating the report-side measurement layer before any further empirical architecture comparison or new model run.

Structured Report State v1 has been implemented, frozen, SHA-locked, and audited. It remains **calibration-only**.

The independent v1 calibration audit identified material construct-coverage weaknesses and paused progression to saved-run diagnostics.

Structured Report State v1.1 has been preregistered as a bounded semantic and calibration amendment, but **has not yet been implemented**.

Classifier-v2 remains the temporary empirical measurement default.

Classifier-v3 has been implemented and diagnostically evaluated, but it was not adopted as the production measurement path. Structured Report State supersedes further single-label classifier patching as the active measurement-development direction.

## Current Research Question

Can final public reports be represented by a deterministic, architecture-blind, multi-field structured report state without collapsing semantically independent dimensions such as completion, uncertainty, partial progress, terminal events, and explicit failure—and can that representation be calibrated sufficiently for later diagnostic comparison with independently represented trace evidence?

The broader Phase 3 research program remains concerned with measurable State-Report Divergence (SRD): disagreement between environment-owned actual state and agent-reported state under differing observability conditions.

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

The preregistered amendment requires:

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
- fresh independent adversarial re-audit.

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

## Current Blockers

Before Structured Report State can progress to saved-run diagnostic use:

1. Implement v1.1 extractor semantics.
2. Create a new v1.1 calibration set.
3. Establish complete enum and required joint-state coverage.
4. Freeze a new calibration identity and SHA lock.
5. Add regression tests for the amended semantic constraints.
6. Conduct a fresh independent adversarial calibration audit.
7. Resolve any blocking construct-validity failures found by that audit.

Even after report-side calibration succeeds, full structured SRD accuracy will additionally require stronger independent trace-side ground truth for dimensions such as completion, normalized failure, partial progress, and verification events.

## Next Authorized Step

**PR A1 — implement Structured Report State v1.1.**

PR A1 should include:

- the v1.1 deterministic extractor;
- the new calibration golden set;
- version identities;
- SHA-256 lock;
- regression tests;
- calibration gate.

Completion of PR A1 authorizes only:

**PR B2 — independent frozen calibration re-audit using fresh non-normative adversarial probes.**

Only an explicit successful PR B2 decision may permit progression to diagnostic processing of saved Run 001/002 reports.

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

- `docs/PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_PREREGISTRATION.md`
- `docs/reports/PHASE3_8_STRUCTURED_REPORT_STATE_CALIBRATION_AUDIT.md`
- `docs/PHASE3_8_STRUCTURED_REPORT_STATE_PREREGISTRATION.md`
- `docs/reports/PHASE3_7_CLASSIFIER_V3_MEASUREMENT_DECISION.md`
- `docs/PHASE3_STATE_REPORT_DIVERGENCE.md`
- `docs/MEASUREMENT_GATES.md`
- `README.md`
