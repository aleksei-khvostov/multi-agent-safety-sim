# Phase 3.7 Run 001 Classifier-v2 Diagnostic Rescore

This document describes the diagnostic classifier-v2 rescore for saved Phase 3.7 Run 001 outputs.

The diagnostic rescore applies the pre-registered `frozen_lexical_v2_negation` reported-outcome classifier to the saved Run 001 raw final reports. It estimates the measurement-system effect of classifier-v2 on already generated outputs.

This diagnostic is not a replacement for Run 001. Run 001 remains the original classifier-v1 result.

This diagnostic is not Run 002. Run 002 remains a future new model run under classifier-v2, using the frozen input conditions and ordinary provider/model stochasticity.

The rescore makes no model calls, does not call OpenRouter, and does not add or require credentials. It reads:

```text
run_manifest.json
raw_responses.jsonl
evaluated_records.jsonl
summary.json
```

It writes only:

```text
run_001_classifier_v2_diagnostic_rescore.json
```

The output reports original classifier-v1 metrics, classifier-v2 diagnostic metrics, deltas, by-fixture comparison, by-architecture comparison, per-record `diagnostic_records` for auditability, and the diagnostic caveat. It does not overwrite `summary.json`, `evaluated_records.jsonl`, or any existing Run 001 artifact.

Each per-record diagnostic entry includes the architecture, fixture, repetition, request ID, actual outcome, original and classifier-v2 reported outcomes, original and classifier-v2 labels, original and classifier-v2 divergence flags, original and classifier-v2 PDS scores, and a final-report excerpt from the saved raw response.

The diagnostic caveat is:

```text
This diagnostic rescore estimates the measurement-system effect of classifier-v2 on saved Run 001 outputs. It does not replace the original Run 001 result and does not represent a new model run.
```

This diagnostic makes no claims about deception, intent, safety, real-world risk, or general model behavior.
