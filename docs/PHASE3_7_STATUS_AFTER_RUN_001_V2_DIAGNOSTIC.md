# Phase 3.7 Status After Run 001 Classifier-v2 Diagnostic

## Current Status

Phase 3.7 Run 001 completed successfully with 75/75 successful evaluations and 0 provider failures.

The original Run 001 classifier-v1 result remains preserved. The post-run audit identified a likely lexical negation artifact in stable-fixture false alarms, where phrases such as "without failures" and "no watchdog alerts" could be classified as failure reports by the frozen lexical classifier.

Classifier-v2 was pre-registered before reuse as `frozen_lexical_v2_negation`. The Run 001-v2 diagnostic rescore was then added as a diagnostic-only, non-replacement analysis over saved Run 001 outputs.

## Main Measured Results

Original Run 001 classifier-v1:

- mean PDS: `0.112`
- `posthumous_overclaim`: `0`
- `false_alarm_or_underclaim`: `13`
- `aligned_clear`: `2`

Run 001 classifier-v2 diagnostic rescore:

- mean PDS: `0.098667`
- `posthumous_overclaim`: `0`
- `false_alarm_or_underclaim`: `11`
- `aligned_clear`: `4`
- `diagnostic_records`: `75`

## Interpretation

Classifier-v2 partially reduced the negation-related measurement artifact. Residual stable-fixture false alarms remain under v2.

`posthumous_overclaim` remained zero under both classifiers. Run 001 did not produce the expected persona-conditioned posthumous overclaim signal.

This is a measurement-system diagnostic, not a new model behavior result. It does not replace or correct Run 001, and it does not make claims about intent, deception, safety, or real-world behavior.

## Methodological Value

The original result is preserved. The post-run audit separated model output from a measurement artifact. Classifier-v2 was pre-registered before reuse. The diagnostic rescore uses saved outputs only and makes no model calls.

Run 002 remains the future proper new model run under classifier-v2.

## Next Step

The next recommended step is Run 002 preparation under `frozen_lexical_v2_negation`, or a short README/report update before Run 002.
