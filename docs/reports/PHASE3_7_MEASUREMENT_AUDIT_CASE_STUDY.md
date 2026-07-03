# When the Metric Is Lying: Phase 3.7 Measurement-Audit Case Study

This is a report-integrity measurement-audit case study. It is not a deception finding, an intent claim, a model-safety claim, or a real-world risk assessment.

## Plain-Language Narrative

Phase 3.7 asked a narrow question: when the underlying evidence is fixed, do different prompt/persona conditions change how a model reports what happened?

The setup held trace evidence constant. Each request showed the model the same kind of episode evidence: what happened during the simulated run, whether a failure or catch event occurred, and whether the trace was stable, stressed, or caught. The model was then asked for a final public report. The measurement layer compared the final report against the fixed trace evidence.

That is much narrower than deception detection. The benchmark does not know what a model "intended." It does not measure whether a system is safe in the real world. It only checks whether a generated report is consistent with the evidence the model was given.

The interesting part of Phase 3.7 was not a dramatic behavioral signal. The interesting part was the measurement audit cycle: first the metric produced suspicious artifacts, then the artifacts were audited, then the classifier was preregistered before reuse, and then the next run exposed a new boundary case.

## Run 001: Negated Success Language

Run 001 completed cleanly: 75 out of 75 requests produced successful evaluations, with 0 provider failures.

The original Run 001 result showed 0 `posthumous_overclaim` records. But the post-run audit found that some stable, successful reports were being counted as false alarms or underclaims because the classifier reacted to failure words inside negated success phrases.

Examples included:

- "without failures"
- "no watchdog alerts"
- "without terminal failures"

Those phrases were semantically successful, but the lexical classifier could over-weight the words "failures" or "alerts." The original result was preserved. Instead of silently patching the metric, classifier-v2 was preregistered before reuse. A Run 001-v2 rescore was then performed as diagnostic-only and non-replacement.

In plain terms, the mean PDS moved from about 0.11 to about 0.10. The exact values are in the appendix.

## Measurement Gates

Before treating Phase 3.7 outputs as interpretable, the project added deterministic measurement gates around the report-integrity layer.

These included a frozen evidence/report benchmark, artifact denominator checks, a nested-delegation benchmark, and fixture drift protection. Their purpose is regression protection: they help catch changes in measurement behavior, denominator handling, or fixture identity.

They are not model-safety claims. Passing the gates does not mean a model is safe, honest, or deceptive. It means the measurement harness is behaving as expected on frozen test cases.

## Run 002: A New Boundary Case

Run 002 also completed cleanly: 75 out of 75 requests produced successful evaluations, with 0 provider failures. It used the frozen classifier-v2 measurement regime.

Run 002 produced 1 apparent `posthumous_overclaim` out of 75 evaluated records. Manual audit weakened the behavioral interpretation of that single case.

The audited report mentioned:

- conflicting observation
- inconclusive verification
- recovery attempted
- unresolved outcome
- no definitive or successful completion
- no `death_event`

The key audit lesson was simple: "no death_event occurred" is not equivalent to all-clear.

The report was not semantically saying that everything was fine. It was describing an unresolved, inconclusive, partially recovered state. The apparent overclaim is therefore likely a classifier boundary artifact rather than strong evidence of persona-conditioned report overclaim.

Architecture-level comparison should not be interpreted from one artifact-like case.

## Classifier-v3 Status

After Run 002, the project added a classifier-v3 issue note and preregistration.

Classifier-v3 is not implemented. No v3 rescore has been run. The original Run 001 and Run 002 results remain preserved.

Any future v3 rescore must be diagnostic-only and non-replacement. It must be explicitly labeled, compared against preserved original results, and not used to rewrite prior runs.

## Takeaway

The goal is not to produce the cleanest-looking metric. The goal is to know when the metric is lying to you.

## Appendix: Exact Numbers

### Run 001 Original

- Mean PDS: `0.112`
- `posthumous_overclaim`: `0`

### Run 001-v2 Diagnostic

- Mean PDS: `0.098667`
- `false_alarm_or_underclaim`: `13 -> 11`
- `posthumous_overclaim`: `0 -> 0`

### Run 002

- `posthumous_overclaim_rate`: `0.013333`
- `mean_pds_score`: `0.100`

Label distribution:

| Label | Count |
|---|---:|
| `aligned_clear` | 5 |
| `false_alarm_or_underclaim` | 10 |
| `honest_ambiguity` | 29 |
| `honest_failure_report` | 30 |
| `posthumous_overclaim` | 1 |

Reported outcome distribution:

| Reported outcome | Count |
|---|---:|
| `all_clear` | 6 |
| `honest_failure` | 44 |
| `partial_admission` | 14 |
| `uncertain` | 11 |

### Measurement Gate Mapping

- `RIB-16`: frozen evidence/report benchmark
- `Gravestone`: artifact denominator checks
- `NDB-20`: nested-delegation benchmark
- `NDB-20 SHA lock`: fixture drift protection

These are regression gates, not model-safety claims.

## Links

- [Run 001 post-run audit](../PHASE3_7_RUN_001_POSTRUN_AUDIT.md)
- [Classifier-v2 preregistration](../PHASE3_7_CLASSIFIER_V2_PREREGISTRATION.md)
- [Run 001 classifier-v2 diagnostic rescore](../PHASE3_7_RUN_001_CLASSIFIER_V2_DIAGNOSTIC_RESCORE.md)
- [Run 002 post-run audit](PHASE3_7_RUN_002_POSTRUN_AUDIT.md)
- [Classifier-v3 issue note](../PHASE3_7_CLASSIFIER_V3_ISSUE_NOTE.md)
- [Classifier-v3 preregistration](../PHASE3_7_CLASSIFIER_V3_PREREGISTRATION.md)
- [Measurement gates](../MEASUREMENT_GATES.md)
- [RIB-16](../RIB_16.md)
- [Gravestone analyzer](../GRAVESTONE_ANALYZER.md)
- [Nested Delegation Benchmark](../NESTED_DELEGATION_BENCHMARK.md)
