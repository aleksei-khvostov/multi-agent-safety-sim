# Phase 3.8 Structured Report-State v1.1.2 Architecture and Control Preregistration

**Decision recorded:** 2026-09-19 UTC. The external freeze lock records the actual completed freeze time and content hashes, not an inferred timestamp for the owner's message.

**PATH 1: ACCEPTED — implementation-only successor.**

**Prospective identity:** Structured Report-State v1.1.2.

**Status:** APPROVED / FROZEN FOR ARCHITECTURE AND DISCLOSED CONTROLS upon the successful byte-lock and consistency checks recorded in the external freeze lock. This is not an implemented or conformant measurement.

**Implementation authorization:** NO. The owner's closing instruction requires a separately authored, sealed independent holdout set before implementation authorization. Completing this architecture/disclosed-control freeze does not satisfy that additional gate.

**Stop condition:** v1.1 preregistration §18 / v1.1.1 repair §9 remains ACTIVE throughout this stage. v1.1 and v1.1.1 remain immutable **PAUSED — NOT CONFORMANT** candidates.

## 1. Authority, accepted review, and preservation

The owner accepts PATH 1 from the fresh architecture decision review in task `01a0bae2-36b4-7471-b09f-57426a6b9542`. That review context authored none of the v1.1/v1.1.1 implementation and received the review instructions and governing artifacts without the earlier implementation reasoning. Different-model or external-human independence is not claimed. The present builder context transcribes the governance decision and authors disclosed controls; it is not an independent conformance reviewer and cannot author genuinely hidden holdouts for itself.

The accepted decision is that assertion/evidence-level internal representation is compatible with the existing frozen measurement contract. No semantic amendment is required merely for that representation. The review itself authorized neither a successor implementation nor release of the stop condition. This owner's subsequent decision adopts the prospective v1.1.2 identity and authorizes only architecture/control preparation in this task.

Governing sources, in their existing amendment relationship:

1. [Original preregistration](PHASE3_8_STRUCTURED_REPORT_STATE_PREREGISTRATION.md), especially §§3–7 and 13.
2. [v1.1 preregistration](PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_PREREGISTRATION.md), especially §§3–14 and 17–18.
3. [Approved v1.1.1 repair preregistration](PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_1_REPAIR_PREREGISTRATION.md), especially §§2–6 and 8–9, including D1.
4. [v1.1 failed disposition](reports/PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_CONFORMANCE_AUDIT.md) and [v1.1.1 failed disposition](reports/PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_1_CONFORMANCE_AUDIT.md).
5. Historical [measurement gates](MEASUREMENT_GATES.md) and [research state](CURRENT_RESEARCH_STATE.md), read with this later governance decision.

This record prospectively resolves the architecture-decision prerequisite in the earlier status documents. It does not rewrite their historical statements, prior approval records, passing calibration facts, failed findings, or reviewer-independence limitations. Authored calibration agreement did not establish preregistration conformance for either candidate. Neither candidate becomes conformant through this decision.

Preserve all existing extractors, calibration modules, tests, fixtures, manifests, locks, preregistrations, audits, shared CLI/registry files, and historical v1 artifacts byte-for-byte. The new freeze lock records predecessor fingerprints in place; no commit, archive, replacement lock, or separate immutable storage is claimed. Recheck those fingerprints before any future authorized work.

## 2. Semantic boundary and identities

The five fields and all 22 field/value combinations remain unchanged. No new supported language, attribution rule, negation meaning, precedence rule, general English parser, unrestricted coreference, model-assisted interpretation, ground-truth inference, or empirical behavior is introduced. Existing normalization, quote/token boundaries, bounded morphology, provenance, calibration, and CLI fail-closed obligations continue to apply. Earlier failed code and its documented grammar shortcuts are not normative sources.

| Component | Prospective identity |
|---|---|
| Measurement/extractor successor | Structured Report-State v1.1.2 / `deterministic_report_state_extractor_v1_1_2` |
| Calibration | `structured_report_state_golden_v1_1_2` |
| Semantic output schema | `structured_report_state_schema_v1_1_1`, unchanged |
| Architecture/control record | `structured_report_state_v1_1_2_architecture_controls` |

Retaining the semantic schema identity reflects the implementation-only decision: v1.1 §4 required schema versioning for changed semantics; no such change is authorized here. The distinct extractor/calibration identities identify the new implementation and suite. Historical input records retain their own declared schema identities; no historical row or emitted historical identity is relabeled. Structural compatibility is not permission to alias a historical extractor to the successor.

D1 remains exactly: for `Final verification was not resolved.`, completion is `completion_not_addressed`, uncertainty `not_expressed`, partial progress `partial_progress_not_addressed`, terminal event `terminal_event_not_addressed`, explicit failure `failure_not_addressed`, flags `[]`. Unsupported negative phrasing does not become `resolved`, `unresolved`, or `unknown`. Supporting it as unresolved would require a separate prospective amendment.

## 3. Frozen internal architecture

```text
text
→ bounded structural segmentation
→ assertion/evidence candidates
→ per-evidence semantic annotation
→ evidence eligibility
→ per-field aggregation
→ field-local precedence/conflict resolution
→ existing five-field StructuredReportState
```

An internal evidence item may record field, candidate value/polarity, source span, operative/hypothetical/modal status, attribution/endorsement status, mention/metalinguistic status, historical/provisional/current status, and finality/update qualification. Names and storage layout are implementation details. Source spans serve deterministic tracking, not confidence weighting or new proximity-based semantic rules. Candidate cue matches are not operative positive classifications until scope and polarity are resolved.

Structural segmentation preserves the context needed to qualify each assertion; it is not a sentence/fragment-wide eligibility decision. The frozen sequence prohibits the failed approach of first vetoing an entire fragment, then searching all fields in the surviving fragments. It does not require full NLP parsing. `and`, punctuation, or shared spans cannot be universal eligibility or scope rules.

### Architecture invariants

1. Scope suppression applies to the applicable evidence/assertion, not automatically an entire sentence or fragment (v1.1 §§3, 8–9; repair §§3.1–3.3).
2. Evidence for field A cannot erase independent evidence for field B (original §5; v1.1 §§3, 6). Where a supported phrase legitimately bears on multiple fields, predeclare that affected set instead of demanding false independence.
3. One sentence/clause may yield multiple evidence items, including multiple fields (original §7.3; repair §3.2).
4. Negation attaches only under the existing zero-through-five-intervening-word-token bound and phrase/polarity rules; it cannot invert unrelated evidence (v1.1 §§10–11; repair §3.4).
5. One item's hypothetical/modal status cannot automatically suppress or activate another. Actual inability does not activate an independent possible failure; operative modal uncertainty retains its frozen unresolved meaning (v1.1 §9; repair §3.2).
6. Mention/example status is bounded to applicable evidence. A bare word such as `word` cannot veto an ordinary assertion (repair §3.3).
7. Attribution survives segmentation; segmentation cannot manufacture narrator endorsement. Explicit supported endorsement remains distinct from unendorsed content (v1.1 §8).
8. Historical/provisional/current/final qualification attaches to evidence for its applicable field. A document called a final report does not convert its historical observation into a coequal final assertion (repair §3.5).
9. Aggregate per field only after evidence eligibility/qualification is determined. Retain temporal/finality distinctions needed for subsequent field-local resolution; do not blanket-delete historical, quoted, or modal content irrespective of the contract's endorsement and uncertainty rules.
10. Coequal incompatible evidence uses existing field-local `unknown` and literal conflict flags; other fields survive. Compatible unresolved/inconclusive descriptions retain the frozen inconclusive tie-break (v1.1 §5).
11. Position, `but`, punctuation, or an update/final marker elsewhere cannot establish precedence. Only the registered same-field qualified operative update may do so. A temporal-update marker is not automatically a coequal-final marker (v1.1 §7; repair §3.5).
12. D1 is unchanged. Silence, explicit negatives, and conflicts remain distinct. No new failure-to-unknown exception path is added; exceptions remain errors.

## 4. Disclosed controls and admission

Two new immutable JSONL artifacts are admitted prospectively before any successor code exists:

- `data/eval_sets/structured_report_state_v1_1_2_architecture_controls.jsonl`: disclosed property/compositional controls for families A–F below.
- `data/eval_sets/structured_report_state_v1_1_2_disclosed_regression.jsonl`: all E1–E10, verbatim, with complete expected five-field states transcribed from the authoritative audit. These are disclosed regressions, never holdouts. Their actual failed outputs remain audit history and are not oracle labels.

Each fixture retains the existing exact 11-key record format: `case_id`, `report_text`, five `expected_*` fields, `category`, `rationale`, `source_type`, `schema_version`. New rows declare the unchanged semantic schema `structured_report_state_schema_v1_1_1`, `source_type=contrastive`, and the exact prefix `prereg-designed contrastive:`. Audit reproductions explicitly identify their audit provenance after that prefix; they are not misrepresented as unseen probes. Exact full-state and literal flag expectations, field changes/invariants, counts, and hashes are frozen in the separate control manifest.

The builder authors these controls from the contract and disclosed audit expectations before successor implementation; no extractor is imported, run, or used as an oracle. This is independence from implementation outputs/constants, not a claim of independent reviewer authorship. The owner's task authorizes this disclosed specification and freeze; it does not imply an additional reviewer examined the bytes. Independent review remains necessary.

### Property families

| Family | Frozen relation and scope | Existing authority |
|---|---|---|
| A — Field independence | Add an independent B assertion; change only its predeclared field set, retaining A and all other states. Cover ordinary cross-field positives, explicit negatives, a legitimately multi-field phrase, and conflict beside stable evidence. | Original §§4–5, 7.3; v1.1 §§3, 5–6 |
| B — Order/permutation | A+B and B+A have equal complete states/flags only when attribution, polarity, modality, and temporal interpretation are preserved. Include qualified final updates as explicit non-invariance controls, not universal order invariance. | v1.1 §§5, 7; repair §3.5 |
| C — Scope locality | Supported hypothetical, modal, quotation, and mention framing is local. Independent B survives; modal uncertainty and possible events have their distinct registered treatments. Attribution is additionally isolated in F. | v1.1 §§8–9; repair §§3.1–3.3 |
| D — Negation locality | A's supported negation cannot change independent B. Include admitted singular/plural failure morphology and polarity contrasts; retain D1 and the distinct supported `not unresolved` interpretation. | v1.1 §§10–11; repair §3.4 / D1 |
| E — Finality locality | A's final/historical/provisional markers cannot qualify B. Contrast true conflicts, qualified updates, historical evidence, and temporal updates without promoting every marker to finality. | v1.1 §§5, 7; repair §3.5 |
| F — Attribution preservation | Supported attribution covers its coordinated assertions until the admitted boundary; segmentation cannot convert a later conjunct into narrator evidence. Compare unendorsed, explicitly endorsed, and independent narrator clauses. | v1.1 §8; repair §§3.1–3.2 |

The manifest defines each relation's exact endpoints, complete expected states/flags, fields that must change and remain invariant, applicability conditions, and contract rationale. Equality/inequality of labels alone is not semantic adjudication. Test the intended text transformation, not just IDs or categories. Boundary/order controls apply only to their stated constructions; no blanket punctuation or paraphrase invariant is introduced.

### Historical inputs and inherited enforcement

Reference, never copy/relabel or edit, the 267-case v1.1 baseline, the 11-case v1.1.1 repair fixture, and the v1.1.1 frozen contract manifest/lock. Retain all 28 historical semantic relations, every enum's isolated and nontrivial joint witnesses, required joint states, normalization/lexical/morphological boundaries, negative/silence distinctions, and literal flag rules. Report each historical and successor component separately; a combined count is not a robustness score.

The new controls supplement rather than replace inherited coverage. A detected conflict between an inherited expectation and the governing contract pauses progression for prospective adjudication; no exclusions, overrides, relabeling, or relaxed gates are authorized.

Future calibration must independently validate exact record keys, IDs, closed enums, declared input/output identities, source mapping and colon-bearing provenance prefixes, counts, coverage, semantic relations, and all SHA locks before extraction. Expected flags remain literal external oracle data. CLI failure must exit 2 without stdout/passing summary for missing/unreadable or corrupted locked inputs, invalid data, lost coverage/contrast, identity drift, or state/flag mismatch. No public fixture/hash bypass or caller-selected replacement corpus may claim the registered pass. Historical direct commands remain unchanged.

## 5. Independent sealed holdout procedure — content deliberately absent

This builder context cannot create hidden cases without seeing them. No holdout strings, labels, or output artifacts are created here. A separately authorized fresh reviewer/custodian must create them before any implementation begins. Neither this stage nor its lock authorizes launching that task or invoking project models/providers.

The reviewer receives the frozen governing documents and architecture/control contract, including disclosed cases for duplicate avoidance, without builder implementation reasoning. The reviewer must have authored none of the successor implementation. Different-model identity is optional, not a substitute for context/authorship independence. If a model is used as the review assistant, that methodological task requires separate explicit authorization; it is never a model-assisted extractor or empirical run.

The bounded holdout inventory is **24 compositions: four per family A–F**. Within each family, author two contract-justified contrast or metamorphic pairs, with complete five-field states, literal flags, exact applicability conditions, expected changed/invariant fields, and a source-section rationale. Use only frozen vocabulary/constructions; introduce no new semantic attachment rule. Each row must be a new composition, not a verbatim disclosed or historical fixture row. No saved-run text or extractor behavior may select inputs or labels. Unsupported/ambiguous proposed cases are rejected before sealing, not retrospectively interpreted after results. Failure to obtain this bounded set within the existing contract pauses for governance; it is not permission to broaden language.

The private set uses the same 11-key record schema. Its separate private manifest holds flags, transformations, rationales, reviewer/custodian identity, and adjudication timestamp. The custodian keeps both outside the builder-accessible repository/context. The builder must not inspect, import, copy, calibrate on, or receive case-level content before implementation is frozen. Files in an ordinary shared workspace are not operationally secret. If access separation cannot be established, record that limitation and stop before claiming this gate passed; do not pretend that undisclosed filenames make visible files sealed.

Before implementation, publish a content-free seal receipt containing measurement identity, exact hashes of the private fixture and private manifest, count 24, family counts, UTC creation/adjudication/seal times, independent reviewer identity and limitations, the architecture/control freeze hashes it reviewed, and an access-separation attestation. No report strings, expected labels, pair-specific transformations, or case-level feedback goes into the public receipt. An independent consistency/adjudication check must establish that labels derive from the contract before the receipt is issued. The receipt appends a new dated governance artifact; it never overwrites this freeze lock.

After a separate implementation authorization and frozen implementation snapshot, the reviewer executes the sealed audit against exactly those implementation/input hashes and reports the complete results. Builder tests or calibration must not consume holdouts. Failure preserves evidence, maintains the stop condition, and returns to prospective governance. Revealed cases cease to be holdouts and cannot be used for tuning under this authorization; no silent label change, selective deletion, resealing, or retry-driven patching is permitted. This holdout review is not PR B2; a later separately authorized B2 requires its own fresh probes.

## 6. Artifact boundaries and non-self-referential locks

| Artifact | Prospective path / disposition |
|---|---|
| Architecture preregistration | `docs/PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_2_ARCHITECTURE_PREREGISTRATION.md` — created now |
| Architecture controls | `data/eval_sets/structured_report_state_v1_1_2_architecture_controls.jsonl` — created now |
| Disclosed E1–E10 | `data/eval_sets/structured_report_state_v1_1_2_disclosed_regression.jsonl` — created now |
| Control/calibration manifest | `data/eval_sets/structured_report_state_v1_1_2_control_manifest.json` — created now |
| Non-executable architecture/control freeze lock | `data/eval_sets/structured_report_state_v1_1_2_architecture_freeze_lock.json` — created now |
| Extractor/API | `src/multi_agent_safety_sim/evaluation/structured_report_state_v1_1_2.py`; `extract_structured_report_state_v1_1_2(text)` — NOT created |
| Calibration/contract validator | `src/multi_agent_safety_sim/evaluation/structured_report_state_v1_1_2_calibration.py` — NOT created |
| Literal lock registry | `src/multi_agent_safety_sim/evaluation/structured_report_state_v1_1_2_fixture_locks.py` — NOT created |
| Separate fail-closed CLI | `src/multi_agent_safety_sim/evaluation/structured_report_state_v1_1_2_cli.py` — NOT created; no shared CLI changes |
| Semantic/contract tests | `tests/test_structured_report_state_v1_1_2.py` — NOT created |
| CLI tests | `tests/test_structured_report_state_v1_1_2_cli.py` — NOT created |
| Private holdout fixture | Custodian-only `structured_report_state_v1_1_2_holdout_audit.jsonl`, outside builder-accessible workspace — NOT created |
| Private holdout manifest | Custodian-only `structured_report_state_v1_1_2_holdout_manifest.json` — NOT created |
| Public content-free seal receipt | `docs/reports/PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_2_HOLDOUT_SEAL.json` — NOT created |
| Later implementation authorization | `docs/reports/PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_2_IMPLEMENTATION_AUTHORIZATION.md` — NOT created |
| Later conformance disposition | `docs/reports/PHASE3_8_STRUCTURED_REPORT_STATE_V1_1_2_CONFORMANCE_AUDIT.md` — NOT created |

Hash dependency direction: freeze lock → control manifest → this preregistration and disclosed fixtures. The lock also pins existing historical input/failure fingerprints. No artifact contains its own digest; the task result reports the freeze-lock digest externally. The eventual registry pins literal approved hashes, not hashes dynamically accepted from arbitrary current bytes. Subsequent seal/authorization/audit records reference this immutable freeze. Existing SHA/freeze claims are never overwritten or relabeled.

This section is the prospective changelog: adopt evidence-before-field aggregation and scoped annotation to implement existing semantics, freeze property relations and disclosed regressions, retain the semantic schema, introduce distinct implementation/calibration identities, and require an independently sealed pre-implementation holdout gate. No other substantive change is authorized. After freeze, any control/expectation or architecture change requires a new prospective version/changelog decision before dependent implementation, under original §13 and v1.1 §14.2; a validation failure is not permission to amend the oracle until it passes.

## 7. Gates, active stop condition, and next step

Required progression:

`existing contract` → `PATH 1 acceptance / architecture freeze` → `disclosed property + E1–E10 expectation freeze` → `separate fresh reviewer authors/adjudicates/seals hidden holdouts` → `explicit bounded implementation authorization` → `implementation` → `targeted and disclosed/inherited calibration tests` → `historical v1/v1.1/v1.1.1 regression` → `full pytest` → `Ruff` → `scoped mypy` → `calibration` → `independent sealed-holdout and preregistration-conformance audit` → `explicit stop-condition/A1 disposition` → only then consideration of separately authorized B2.

Passing builder tests does not release §18 / repair §9, establish conformance/adoption, or authorize B2. An explicit later governance decision may permit a bounded implementation attempt after the pre-implementation gates; it must identify the precise lock/seal and permitted files. The existing failures remain recorded. Any repeated field-preservation failure, scope contamination, growing exact-string patch family, or need for unsupported semantic inference activates the same pause/escalation obligation. Do not bypass it by classifying semantic changes as internal architecture.

At this stage only document/data/lock consistency and preservation are checked. No extractor, Python implementation/test file, calibration execution, saved-run inspection, model/provider call, B2, empirical collection, commit, or push occurs. Repository-wide historical mypy debt remains out of scope.

**Next step:** separately authorize a fresh independent reviewer/custodian to create and seal the 24-case holdout set under §5, without exposing content to the builder. Then obtain explicit implementation authorization referencing both freezes. Until then: **v1.1.2 IMPLEMENTATION AUTHORIZED: NO; B2: NO; MODEL/SAVED-RUN ACCESS: NONE; DATA COLLECTION: NO.**
