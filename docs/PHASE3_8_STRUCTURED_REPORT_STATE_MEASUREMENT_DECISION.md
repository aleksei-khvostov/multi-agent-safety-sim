# Phase 3.8 Structured Report-State Measurement Decision

**Decision recorded:** 2026-09-20 UTC, under the project owner's explicit measurement-development closure instruction.

**PHASE 3.8 CLOSED AS A MEASUREMENT-DEVELOPMENT RESULT — STRUCTURED REPORT-STATE NOT ADOPTED**

**DECISION: DO NOT ADOPT STRUCTURED REPORT-STATE FOR EMPIRICAL USE; PAUSE FURTHER DETERMINISTIC FREE-TEXT EXTRACTOR DEVELOPMENT**

## 1. Decision and scope

Further deterministic free-text Structured Report-State extractor development is paused at Phase 3.8. No candidate is adopted for empirical measurement. The active v1.1 §18 / v1.1.1 repair §9 stop condition remains in force and is not released by closing this phase.

This decision applies to the current Phase 3.8 line of deterministic extraction of structured claims from free-text reports. It does not reject every structured-reporting or evaluator architecture, establish that deterministic extraction is impossible in principle, or exhaust all technical possibilities. It is a bounded methodological and measurement-governance decision based on three successive failed preregistration-conformance reviews despite complete agreement on authored calibration/test suites.

No next successor is authorized or named. This task selects no next architecture, implements nothing, and creates no new phase. Reconsidering development or using any preserved holdout requires a separate prospective governance decision; closure does not create an automatic restart condition.

## 2. Governing evidence and chronology

The governing semantic records remain the [original preregistration](PHASE3_8_STRUCTURED_REPORT_STATE_PREREGISTRATION.md), [v1.1 amendment](PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_PREREGISTRATION.md), [v1.1.1 repair preregistration](PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_1_REPAIR_PREREGISTRATION.md), and [v1.1.2 architecture preregistration](PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_2_ARCHITECTURE_PREREGISTRATION.md). This decision changes development/adoption disposition, not their frozen semantics or expected labels. The candidate audits and manifests below retain their chronology, identities, authorship limitations, and historical verification facts.

### Historical v1 baseline

The original preregistration was recorded on 2026-07-17; its implementation-status note records the later PR A delivery. Historical v1 supplied the five-field schema, deterministic extractor, 59-case frozen calibration fixture, SHA lock, and calibration gate. It reproduced **59/59** full-state expectations across all 20 registered families.

The [2026-09-05 independent v1 calibration audit](reports/PHASE3_8_STRUCTURED_REPORT_STATE_CALIBRATION_AUDIT.md) found material construct-coverage weaknesses and decided to pause before PR C and preregister a v1.1 amendment. Historical v1 remains frozen and calibration-only. Its 59/59 regression evidence remains valid on its authored fixture; this decision does not retrospectively label v1 under later successor criteria or recast it as an adopted empirical measurement.

### v1.1 — authored calibration passed; conformance failed

The v1.1 amendment was preregistered on 2026-09-06. Its [2026-09-17 conformance audit and disposition](reports/PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_CONFORMANCE_AUDIT.md) records **FAIL / PAUSE** and **PAUSED — NOT CONFORMANT**.

Preserved verification observations include:

- Authored calibration: **267/267**; historical v1: **59/59**.
- The [historical implementation verification record](MEASUREMENT_GATES.md#a1-verification-record) reports **317 combined v1/v1.1 targeted tests** and **593 full regression tests** in an isolated copy, with Ruff and `git diff --check` passing.
- The independent audit reproduced authored calibration, historical v1 calibration, separately labeled `run-all` gates, and in-memory CLI failure handling. It did not independently rerun the full pytest suite.
- Scoped mypy found **six new extractor errors**. The separately reported 24 pre-existing errors outside that scope were not repaired or erased by passing Ruff/pytest results.

Central semantic failures concerned conditional/modal/mention scope preservation, negation scope and polarity, and field-local final-state precedence. Contract-enforcement gaps included insufficient semantic contrast validation, incomplete isolation enforcement, implementation-derived conflict names in tests, and provenance-prefix validation. The source record also retains the historical limitation in establishing pre-implementation adjudication for every baseline expectation. These facts do not negate the observed 267/267 agreement; they delimit what it established.

### v1.1.1 — frozen repairs passed; compositional failures continued

The bounded repair contract and expectations were approved and frozen on 2026-09-19. The [v1.1.1 conformance audit and disposition](reports/PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_1_CONFORMANCE_AUDIT.md) records **FAIL / PAUSE** and **PAUSED — NOT CONFORMANT**.

Preserved results are **11/11** frozen repair cases, **267/267** successor baseline cases, **431 targeted tests PASS**, **1,024 full pytest PASS**, **Ruff PASS**, and **scoped mypy PASS**. The audit reproduced the repair and successor calibration results; the test/tooling totals remain attributed implementation-verification evidence. Full-suite verification used an isolated copy excluding saved runs.

E1–E10 demonstrated continuing compositional failures: operative evidence was lost beside conditional, modal, mention, or provisional material; possible events became operative; negation and finality transferred to unrelated claims; historical evidence became a false current conflict; and segmentation lost attribution. Passing the prospectively frozen repairs did not establish the broader conformance contract.

**Independence qualification:** the v1.1.1 source record explicitly states that its adversarial auditor also authored the implementation earlier in the same conversation. Its FAIL / PAUSE disposition is authoritative and its counterexamples remain evidence, but that review did not satisfy the required independent-review gate. This decision does not retrospectively describe it as an independent sign-off. The later v1.1.2 audit had a fresh reviewer context.

### v1.1.2 — evidence architecture passed disclosed controls; pre-holdout audit failed

The assertion/evidence architecture and disclosed expectations were prospectively frozen on 2026-09-19. The [bounded implementation authorization](reports/PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_2_IMPLEMENTATION_AUTHORIZATION.md) followed independent pre-implementation holdout sealing. The [implementation record](reports/PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_2_IMPLEMENTATION.md) and [implementation manifest](../data/eval_sets/structured_report_state_v1_1_2_implementation_manifest.json) recorded the frozen candidate and passing builder-visible checks on 2026-09-20.

| Verification component | Preserved result |
|---|---|
| Architecture controls | **55/55** |
| Disclosed semantic relations | **66/66**, plus **28/28** inherited relations |
| Disclosed E1–E10 | **10/10** |
| Successor baseline | **267/267** |
| Prior repair contract | **11/11** |
| Total disclosed calibration | **343/343** complete states and flags |
| Targeted pytest, implementation record | **654 PASS** |
| Full pytest, implementation record | **1,678 PASS**, isolated copy excluding saved runs |
| Ruff, implementation record | **PASS** |
| Scoped mypy, implementation record | **PASS** |

The [independent pre-holdout audit and disposition](reports/PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_2_PRE_HOLDOUT_CONFORMANCE_AUDIT.md) found **58 fresh probes: 46 pass / 12 fail**, requiring **FAIL / PAUSE BEFORE HOLDOUT**. Its three reproduced defect classes were **mention-scope leakage (3 failures)**, **modal-event activation (7 failures)**, and **quoted-negator leakage (2 failures)**. The status remains **v1.1.2 PAUSED — NOT CONFORMANT; HOLDOUT UNOPENED**.

The fresh auditor authored none of the three implementations or sealed holdout cases and consulted no builder or holdout-author reasoning. No different-model or external-human independence is claimed. The audit independently reproduced the disclosed calibration and relations, **571 read-only successor tests**, **80 in-memory fail-closed checks**, scoped Ruff, and artifact integrity. It did not rerun the full repository suite; 571 is the audited subset, not a replacement for the recorded 654 implementation-targeted total.

The remaining defects concerned evidence-span localization: incomplete segmentation coverage, modifier attachment that omitted post-cue modality, and raw quoted context participating in negation. The existence of evidence objects and per-field aggregation did not guarantee that evidence was annotated using only its applicable operative context.

**All counts above are verification observations on specified artifacts and probes, not estimates of population-level robustness or accuracy.** Passing facts remain historical facts; failures do not make those executions disappear.

## 3. Methodological finding and research interpretation

**Complete agreement on an authored calibration suite did not establish preregistration conformance for these deterministic extractors.** Internal verification became stronger through separately frozen repair expectations, complete state and literal-flag oracles, isolation/joint coverage, compositional controls, semantic relations, hash locks, and fail-closed tests. Fresh bounded compositions nevertheless exposed violations of distinctions already required by the frozen contract.

The strongest defensible interpretation is that **Phase 3.8 provides a concrete example in which evaluator agreement with its authored golden data was insufficient evidence that the evaluator preserved the preregistered measurement distinctions under fresh bounded compositions.** Agreement demonstrated that particular implementations reproduced particular expectations. It did not establish that scope, polarity, attribution, and field independence generalized across the admitted compositions.

This is evidence about the development and validity of this measurement implementation. It is not a finding that deterministic evaluators are unreliable in general, that regex/rule-based evaluation cannot work, or that model-based graders are superior. No comparative result establishes any such superiority. It is not evidence that the measured agents are deceptive, that intent was inferred, or that SRD has been empirically established by Phase 3.8. The finding concerns neither all evaluators nor all language understanding.

## 4. Why development is paused

Three successive candidates failed conformance review despite complete agreement on their authored calibration suites. The last attempt replaced earlier extraction organization with a prospectively approved assertion/evidence architecture, yet incomplete evidence-span localization remained measurable on supported language.

Continuing to add segmentation coverage and attachment exceptions risks turning bounded implementation of a preregistered measurement contract into open-ended language-parser engineering and adaptation to an expanding test set. That risk is a reason to stop this development line now, not proof that every refinement would fail or that previous expectations were knowingly fitted to outputs.

The stop is deliberate measurement governance, not exhaustion of all technical possibilities. The previously pending choice between further evidence-span refinement and stopping development is resolved here by pausing further deterministic free-text extraction development at this stage. No implementation work is queued by this decision. The stop condition remains active.

## 5. Sealed holdout disposition

The content-free [seal metadata](../data/eval_sets/structured_report_state_v1_1_2_holdout_manifest.json) records **24 independently authored pre-implementation cases**, four per family A–F. It attests that their plaintext was never exposed to the builder and that the fresh custodian had no prior implementation authorship or builder reasoning. These independence, chronology, and access-separation statements remain attributed custodian attestations; this task does not inspect private content to re-prove them.

v1.1.2 failed before holdout opening. The 51,400-byte ciphertext and its manifest remain preserved, and the holdout remains **SEALED / UNOPENED**. Ciphertext SHA-256 was verified as:

```text
c2113a01e9cd609ccc4e62a41f65c1ee817b4306fb11130315e91ffc07f418ec
```

The holdout must not be opened merely to inspect how v1.1.2 would have performed. Future use requires a separate prospective governance decision, including whether the preserved set is appropriate for that future research question. Neither closing this phase nor listing future options authorizes decryption, execution, tuning, or disclosure. **No robustness result may be inferred from the unopened holdout.**

This task verified ciphertext existence, size, and hash only and read the permitted content-free receipt. It did not decrypt or inspect the payload, search for a private identity, access `/Users/alex/ResearchPrivate`, or request holdout expectations.

## 6. Empirical and adoption consequences

| Activity | Decision |
|---|---|
| Structured Report-State empirical measurement | **NOT ADOPTED**; no Phase 3.8 candidate is adopted. |
| B2 | **NOT AUTHORIZED**; closure is not B2 or a successful conformance gate. |
| PR C / saved-run diagnostic processing | **NOT AUTHORIZED**. |
| Empirical adoption / empirical pin | **NOT AUTHORIZED**. |
| Saved-run inspection or rescoring using this measurement | **NOT AUTHORIZED**. |
| Real-model work or collection using this measurement | **NOT AUTHORIZED**. |
| New data collection | **NOT AUTHORIZED**. |
| Next successor or implementation | **NOT AUTHORIZED**. |

No existing run may be reinterpreted through v1.1, v1.1.1, or v1.1.2 as an adopted measurement. Canonical historical results and any already authorized historical diagnostics retain their original identities and meanings. No saved-run inspection, rescoring, or real-model execution is performed here. Classifier-v2 remains the temporary empirical default; this decision changes no classifier or empirical configuration and authorizes no new run under any measurement.

## 7. Preserved artifacts and integrity

Preregistrations, calibration fixtures, failed candidate implementations, conformance audits, architecture controls, disclosed regressions, manifests/locks, the sealed holdout, and historical test/calibration results remain valid research artifacts with their existing meanings and limitations. A failed measurement candidate is evidence about evaluator development, not a reason to erase it.

The integrity review checked the implementation manifest, architecture freeze graph, inherited repair freeze graph, control-manifest references, and ciphertext. **40 of 43 unique pinned files matched their historical hashes.** The only mismatches were README, CURRENT_RESEARCH_STATE, and MEASUREMENT_GATES, whose previous authorized status changes and original hashes are already recorded in the [pre-holdout disposition](reports/PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_2_PRE_HOLDOUT_CONFORMANCE_AUDIT.md#authorized-status-document-changes-and-historical-locks). This task makes further explicitly authorized status updates to those same three documents. No unexpected protected-artifact mismatch was found.

| Frozen candidate artifact | Verified SHA-256 |
|---|---|
| v1.1.2 extractor | `6e80a9523f4d4329d62ae61b8d88451d0f8340a6cddd00245f224f88acde20b1` |
| v1.1.2 implementation manifest | `007ea594fe1d8775e35de7128ed966cf3c4c39305b948c69b7765f5aa83d99ce` |
| v1.1.2 architecture freeze lock | `bc4ad0fa79833ac074f1cddaa24edbb508d00ffd503ec0f70af25028dc803c70` |
| v1.1.2 sealed ciphertext | `c2113a01e9cd609ccc4e62a41f65c1ee817b4306fb11130315e91ffc07f418ec` |

Existing locks, manifests, expected hashes, and historical PASS statements are not rewritten to accept the current status-document bytes. The frozen v1.1.2 loader would reject those later bytes; historical reproduction requires the audited document snapshot along with the implementation and inputs. No lock bypass or new passing calibration is claimed. This task checks hashes, documentation, and preservation; it does not rerun extractor/calibration/test suites or create measurement results.

At task start, 168 existing files were fingerprinted across source, tests, documentation, evaluation artifacts, configurations, prompts, and named root files without enumerating or reading saved runs. Only the three active status documents are modified; the other 165 existing files remain byte-identical. This decision document is the sole new file.

## 8. Future research directions — options only

Future separately governed work could investigate:

- Structured report schemas generated directly by agents instead of post-hoc free-text extraction.
- Dual-channel reporting: free text plus structured claims.
- Schema-compliance measurement.
- Deterministic versus model-based evaluator disagreement.
- Evaluator sensitivity to semantics-preserving compositional transformations.
- Dedicated evaluator-validity benchmarks.
- Alternative bounded deterministic extraction architectures, if prospectively justified.

These are research options only. No option is selected, funded, scheduled, or authorized for implementation by this task. Structured output compliance would not by itself establish semantic truth or agreement with independent ground truth. Evaluator disagreement would not by itself identify which evaluator is correct. Any future work requires its own prospective question, scope, measurement contract, validation design, and explicit authorization; no future phase is created here.

## 9. Repository boundary and next step

The current branch, `phase-3-8-structured-report-state-v1-1-implementation`, retains the uncommitted development artifacts for v1.1, v1.1.1, and v1.1.2. They are not deleted, renamed to imply adoption, or collapsed into one final implementation. No commit, push, separate archive, or merge is performed or claimed.

The [current research state](CURRENT_RESEARCH_STATE.md), [measurement gates](MEASUREMENT_GATES.md), and [README](../README.md) carry the active closure status and link this decision. Earlier preregistrations, implementation records, audits, manifests, and locks retain their historical statements; this later governance decision supplies the current disposition.

**NEXT STEP:** Preserve the closed Phase 3.8 measurement-development record and unopened holdout. Any future research direction requires a separate prospective governance decision. No successor implementation, holdout opening, B2, saved-run use, empirical adoption, model work, or data collection is authorized.
