# Phase 3.8 Structured Report-State v1.1.2 implementation record

**Recorded:** 2026-09-20 UTC. Exact completion/freeze time and hashes are in the accompanying implementation manifest.

**Current status: v1.1.2 IMPLEMENTED — HOLDOUT UNOPENED — PENDING INDEPENDENT CONFORMANCE AUDIT**

This is the active successor implementation record following the [explicit bounded authorization](PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_2_IMPLEMENTATION_AUTHORIZATION.md). It is not a conformance decision, B2, stop-condition release, empirical adoption, or collection authorization. Earlier active-status documents are retained byte-identically because they are fingerprinted in the architecture freeze; this later record supplies the successor status without changing those historical freeze claims.

## Candidate and scope

The extractor has a bounded evidence pipeline: structural assertion segmentation; candidate spans; per-evidence quotation, attribution/endorsement, conditional/modal, mention, negation, historical/provisional and final/update qualification; eligibility; per-field aggregation and precedence/conflict resolution. Evidence carries source spans in normalized-text coordinates. Longest-specific overlap handling is field-local, allowing a supported phrase to contribute independently to multiple fields.

The closed lexical inventory is retained from the inherited supported language; failed extractors are not called by the successor. The bounded shared-negator `or` construction remains supported within its existing five-token limit. Structural coordination preserves attribution/conditional context while independent evidence retains its own polarity, modality and finality. No general English parser, model-assisted interpretation, new output field/enum, new inverse-label rule, or new temporal/endorsement inference is authorized.

The semantic schema remains `structured_report_state_schema_v1_1_1`. The distinct extractor is `deterministic_report_state_extractor_v1_1_2`, with calibration identity `structured_report_state_golden_v1_1_2`. D1 retains the frozen all-field abstention. The new four-component calibration is an independent gate; historical commands and artifacts are unchanged.

The independent oracle resides in unchanged external fixtures/manifests, including complete states, literal diagnostic names, changed/invariant fields, and exact provenance prefixes. Tests enforce all 66 disclosed semantic relations plus all 28 inherited relations, every enum's isolated/joint witnesses, whole-state/flag equality and determinism, and CLI failures for locked-input loss/corruption, invalid records, lost coverage/contrast, output identity drift, state drift, and flag drift. The new CLI accepts no fixture override, expected-hash bypass, holdout path, or collection options.

Run the builder-visible gate from the repository root:

```bash
python3 -m multi_agent_safety_sim.evaluation.structured_report_state_v1_1_2_cli
```

Its runtime loads only disclosed frozen inputs. It does not open either holdout artifact or private custody. A regression test guards file access during the gate against holdout/private paths.

## Verification evidence

| Check | Result |
|---|---|
| Architecture freeze lock | PASS: `bc4ad0fa79833ac074f1cddaa24edbb508d00ffd503ec0f70af25028dc803c70` |
| Sealed blob integrity only | PASS: 51,400 bytes; `c2113a01e9cd609ccc4e62a41f65c1ee817b4306fb11130315e91ffc07f418ec` |
| Architecture controls | 55/55 complete states and flags |
| Disclosed semantic relations | 66/66, plus 28/28 inherited relations |
| E1–E10 | 10/10 complete states and flags |
| Successor on frozen baseline | 267/267 |
| Successor on prior frozen repair | 11/11 |
| Total disclosed calibration | 343/343; components reported separately |
| Historical v1.1 calibration | 267/267 under original identity |
| Historical v1 calibration | 59/59 under original identity |
| Historical v1.1.1 calibration | 267/267 baseline and 11/11 repair under original identity |
| Targeted successor pytest | 654 PASS |
| Full pytest | 1,678 PASS in isolated repository copy |
| Ruff | PASS: `python3 -m ruff check .` |
| Scoped strict mypy | PASS across four new production modules and two new test modules, with `--follow-imports=silent`; historical debt is not repaired or claimed clean |
| Pre-existing task inventory | 151/151 byte-identical, including all prior fingerprints and the sealed artifacts |
| `git diff --check` | PASS; new untracked files also checked separately |

The full-suite copy excludes saved runs and sealed ciphertext. Existing deterministic/mocked tests may create their own temporary synthetic artifacts; no source saved-run directory is enumerated or read. The pre-change isolated suite also passed (1,024 tests) after correcting the copy's missing static fixtures and existing-commit metadata. No commits were created: temporary Git metadata referenced the existing source commit solely for test metadata. Initial incomplete-copy failures were harness setup failures, not candidate results.

Passing builder-visible checks establish agreement with disclosed expectations only. They **do not establish preregistration conformance**, evaluate hidden compositions, repair the independence limitations of earlier reviews, or validate robustness. The builder authored this implementation and its tests and cannot supply its own independent conformance decision.

## Preservation and sealed boundary

Historical v1 remains unchanged. Failed v1.1 and v1.1.1 remain **PAUSED — NOT CONFORMANT**, with their source, tests, fixtures, preregistrations, audits, manifests/locks, passing historical facts, and failure findings intact. No frozen v1.1.2 input or expected label changed. The architecture lock's prior authorization status is historical; the later owner's explicit authorization is recorded separately rather than editing that lock.

The custodian's metadata attests to 24 independently authored pre-implementation holdout cases, four per A–F. The builder verified ciphertext existence, size, and SHA only and read the permitted content-free receipt. It did not decrypt, infer, search for private identities, inspect the authoring context, access `/Users/alex/ResearchPrivate`, execute the holdout, or use it for implementation/test tuning. The receipt's independence and disposal statements remain attributed custodian attestations.

The [implementation manifest](../../data/eval_sets/structured_report_state_v1_1_2_implementation_manifest.json) fixes exact successor source/test/document bytes and frozen input identities. It contains no holdout plaintext or expectations and no self-hash. Its external SHA is reported in the implementation task result. No commit or separate immutable archive is claimed.

## Next gate

Freeze these candidate bytes and hand their identifiers to a separately authorized fresh independent auditor/custodian for preregistration-conformance review and first-time sealed-holdout evaluation. The builder must not open or run the holdout after freezing. Any revealed failure remains evidence for prospective governance; it is not authorization to tune against the holdout or edit expected labels.

**STOP CONDITION RELEASED: NO**

**B2 AUTHORIZED: NO**

**MODEL/SAVED-RUN ACCESS: NONE**

**DATA COLLECTION / ADOPTION AUTHORIZED: NO**

No repair beyond the bounded implementation scope, shared CLI change, historical mypy cleanup, commit, push, model call, saved-run processing, or B2 is performed by this task.
