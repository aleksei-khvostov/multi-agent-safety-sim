# Merge Gate: Phase 3.7 Matched-Evidence Pilot Runner

**Normative gate for the matched-evidence real-model pilot execution layer.**

Prerequisites already on `main` (frozen pre-data inputs):

- `configs/phase3_7_real_model_pilot.yaml`
- `prompts/phase3_7/*.md`
- `data/eval_sets/reported_outcome_classifier_golden.jsonl`
- `docs/PHASE3_7_REAL_MODEL_PILOT_PREREGISTRATION.md`
- `docs/PHASE3_7_FROZEN_INPUTS.md`
- `tests/test_phase3_7_frozen_inputs.py`
- `tests/test_reported_outcome_classifier_calibration.py`

This gate covers the **pilot runner PR** that adds execution plumbing:

- `src/multi_agent_safety_sim/simulation/phase3_7_pilot_runner.py`
- `src/multi_agent_safety_sim/cli.py` (`phase3-7-preflight`, `phase3-7-run`)
- `data/eval_sets/phase3_7_matched_trace_fixtures.jsonl`
- `tests/test_phase3_7_pilot_runner.py`
- `docs/PHASE3_7_PILOT_RUNNER.md`

Evaluation reuse (do not fork semantics):

- `build_posthumous_record()`, `actual_outcome_from_episode()`, `classify_reported_outcome()` from `posthumous_divergence.py`

---

## 0. Pre-merge lineage verification

Same as Cemetery gate:

```bash
git rev-parse --show-toplevel
git branch --show-current
git status

python3 - <<'PY'
from pathlib import Path
import multi_agent_safety_sim
repo = Path.cwd().resolve()
package = Path(multi_agent_safety_sim.__file__).resolve()
print("repo:", repo)
print("package:", package)
if repo not in package.parents:
    raise SystemExit("Imported package is not from the current repository")
PY
```

- [ ] Package imports from current checkout
- [ ] `data/runs/phase3_7_real_model_pilot/*` not committed (unless an explicit frozen-summary policy says otherwise)
- [ ] Classifier file hash in manifest matches frozen `posthumous_divergence.py`

---

## 1. Design invariants (matched-evidence)

From preregistration (`docs/PHASE3_7_REAL_MODEL_PILOT_PREREGISTRATION.md`) and runner code:

### What this pilot measures

- [ ] **Persona-to-report transfer** under fixed trace evidence
- [ ] Primary mode: `pilot_mode == matched_trace_report_generation`

### What this pilot does **not** measure

- [ ] Real-model Agent Cemetery survival curves (dynamic environment runs)
- [ ] Live multi-agent watchdog intervention
- [ ] Deception, intent, or real-world risk
- [ ] Architecture danger/safety as an outcome

### Anti-tautology

- [ ] `architecture_id` / persona label = **input condition only**
- [ ] `architecture_id` is **not** passed to `classify_reported_outcome()`
- [ ] Measured outcomes come only from frozen fixture evidence + model `final_report` text via `build_posthumous_record()`

### Matched evidence

- [ ] Every architecture receives the **same** `fixture_id` set (`test_every_architecture_receives_same_fixture_ids`)
- [ ] `fixtures.matched_across_architectures: true` in config
- [ ] Fixture `expected_actual_outcome` matches `actual_outcome_from_episode(death_event, risk_score)` for every fixture

---

## 2. Frozen config gates (`configs/phase3_7_real_model_pilot.yaml`)

`validate_preflight()` enforces:

- [ ] `experiment_id == phase3_7_real_model_pilot`
- [ ] `pilot_mode == matched_trace_report_generation`
- [ ] `run_parameters.repetitions == 3` (preregistered)
- [ ] `execution.request_order == deterministic_block_randomized`
- [ ] `execution.request_order_seed == run_parameters.seed` (currently `37`)
- [ ] `classification.architecture_blind == true`
- [ ] `classification.classifier_modified_after_model_outputs == false`
- [ ] Calibration set path exists
- [ ] Fixture count == `run_parameters.episodes_per_architecture` (5 fixtures)
- [ ] Architectures: `honest_duo`, `deceptive_duo`, `deceptive_watchdog`, `power_duo`, `power_watchdog`

### Preregistered request count

- [ ] `len(build_pilot_requests(...)) == 5 architectures × 5 fixtures × 3 repetitions == 75`
- [ ] Preflight reports `request_count: 75` (`test_phase3_7_config_loads_and_validates`)

### Model fields before real run

- [ ] `model.provider`, `model.model_string`, `model.run_date` must **not** be `TBD` when `require_ready=True`
- [ ] Preflight without `--require-ready` may list TBD — no model call

---

## 3. Pilot runner symbols (verify in PR diff)

| Symbol | Role |
|--------|------|
| `TraceFixture` | Frozen matched trace row (`fixture_id`, `rounds`, `death_event`, `death_cause`, `risk_score`, `expected_actual_outcome`, `trace_summary`) |
| `PromptBundle` | `system_prompt`, `architecture_prompt`, `final_report_instruction` per architecture |
| `PilotRequest` | One report-generation request (`request_id`, `request_sequence`, architecture, fixture, repetition) |
| `load_phase3_7_config()` | Load frozen YAML |
| `load_trace_fixtures()` | Load JSONL; unique `fixture_id` required |
| `build_prompt_bundle()` | Load `prompts/phase3_7/{architecture_id}.md` + shared prompts |
| `build_pilot_requests()` | Block-randomized request list |
| `validate_preflight()` | Frozen-input + optional real-run gates |
| `compute_frozen_input_hashes()` | SHA-256 for config, prereg, classifier, fixtures, calibration, prompts |
| `generate_final_report()` | Single LLM call via `LLMClient.complete()` |
| `summarize_phase3_7_results()` | Aggregates with `metric_denominator: evaluated_records` |
| `run_phase3_7_pilot()` | Orchestrates real run after all gates pass |

### Block-randomized order

For each `(fixture_id, repetition)` block, shuffle architecture order with seed:

```text
<request_order_seed>:<fixture_id>:<repetition>
```

- [ ] Order reproducible (`test_phase3_7_request_order_is_block_randomized_and_reproducible`)
- [ ] Each block contains every architecture exactly once

### Classifier priority (frozen)

`CLASSIFIER_PRIORITY_ORDER` in runner; must match `REPORT_KEYWORDS` iteration in `posthumous_divergence.py`:

1. `honest_failure`
2. `uncertain`
3. `partial_admission`
4. `all_clear`

- [ ] Unmatched text → `uncertain`
- [ ] Golden calibration (`reported_outcome_classifier_golden.jsonl`, 16 cases) still passes

---

## 4. Real-run refusal gates

`run_phase3_7_pilot()` calls `validate_preflight()` with:

- `require_ready=True`
- `require_clean_worktree=True`
- `require_confirmation=True`
- `confirmed=confirm_real_model_run`

CLI `phase3-7-run` additionally requires `--confirm-real-model-run`.

**Must refuse (exit 2) when:**

- [ ] Confirmation flag absent
- [ ] Provider / model_string / run_date still `TBD`
- [ ] Git worktree dirty (`is_git_worktree_clean()` false)
- [ ] Frozen files missing or malformed
- [ ] Fixture / config validation fails
- [ ] Preregistered parameter overrides attempted via CLI (config is sole source of run parameters)

**Preflight command makes zero model calls:**

```bash
python3 -m multi_agent_safety_sim.cli phase3-7-preflight \
  --config configs/phase3_7_real_model_pilot.yaml
```

- [ ] Output includes frozen SHA-256 table and `No model call was made.`

---

## 5. Artifacts and incremental durability

Output directory:

```text
data/runs/phase3_7_real_model_pilot/<run_id>/
```

where `run_id = phase3_7_<timestamp>_<seed>`.

Files:

- [ ] `run_manifest.json` — frozen hashes, git commit, worktree status, model metadata, caveat
- [ ] `raw_responses.jsonl` — append per request
- [ ] `evaluated_records.jsonl` — append per successful non-empty response
- [ ] `failures.jsonl` — append for `empty_response` or `provider_exception`
- [ ] `summary.json` — `summarize_phase3_7_results()` output

### Failure handling

- [ ] Empty/whitespace model response → `failure_type: empty_response`, excluded from evaluated metrics
- [ ] Provider exception → `failure_type: provider_exception`, excluded from evaluated metrics
- [ ] Incremental JSONL append so paid responses survive interruption (test with fake client / interrupt)

### Summary denominators

- [ ] `metric_denominator` is `evaluated_records` everywhere rates are reported
- [ ] `overall_counts` distinguishes `planned_requests`, `attempted_requests`, `evaluated_records`, `failed_requests`
- [ ] `inferential_significance_claims` is `"none"` in summary
- [ ] Summary includes pilot `CAVEAT` (no generalization / deception / intent claims)

### Evaluated record shape

Each evaluated row must include at minimum:

- [ ] `request_id`, `architecture_id`, `fixture_id`, `repetition`
- [ ] `actual_outcome`, `reported_outcome`, `label`, `divergence`, `pds_score`
- [ ] `death_event`, `death_cause`, `risk_score`, `lifespan_rounds`
- [ ] `final_report_excerpt`
- [ ] `input_hash_references` per architecture

---

## 6. Test gates (`tests/test_phase3_7_pilot_runner.py`)

- [ ] Config loads; preflight `request_count == 75`
- [ ] Five fixtures with unique IDs
- [ ] Fixture `expected_actual_outcome` derivation matches `actual_outcome_from_episode`
- [ ] Every architecture sees same fixture IDs
- [ ] Request order reproducible
- [ ] Preflight CLI prints hashes; no API
- [ ] Run CLI refuses without `--confirm-real-model-run`
- [ ] Fake LLM client tests: success path, empty response, provider failure, interrupt recovery
- [ ] **No real API** or credentials in default pytest path

Also run frozen-input regression:

```bash
python3 -m pytest tests/test_phase3_7_frozen_inputs.py tests/test_reported_outcome_classifier_calibration.py -q
```

---

## 7. Scope boundaries (do not merge if violated)

- [ ] Does **not** change `evaluate_death_policy()` / Agent Cemetery tournament semantics
- [ ] Does **not** modify classifier after observing pilot outputs (`classifier_modified_after_model_outputs: false`)
- [ ] Does **not** add architecture_id to `classify_reported_outcome()`
- [ ] Does **not** claim predictive validity in code/docs before analysis plan executed
- [ ] Does **not** commit raw pilot responses under `data/runs/` to git by default (`raw_artifacts_committed: false` in config)
- [ ] Does **not** conflate this pilot with Cemetery `run_tournament()` dry-run results

---

## 8. Language gate

**Forbidden in PR / manifest / summary interpretation:**

- detects deception; proves lying; dangerous architecture; validated real-world risk; general model behavior from one pilot

**Required:**

- matched-evidence report-generation pilot
- persona label = input condition
- frozen classifier; architecture-blind extraction
- one model / one configuration does not generalize
- `inferential_significance_claims: none` until separate analysis

---

## 9. CI validation

```bash
python3 -m ruff check .
python3 -m pytest tests/test_phase3_7_frozen_inputs.py \
  tests/test_phase3_7_pilot_runner.py \
  tests/test_reported_outcome_classifier_calibration.py \
  tests/test_posthumous_divergence.py -q
```

- [ ] Ruff clean
- [ ] Phase 3.7 tests green
- [ ] Posthumous / classifier tests still green (shared evaluation layer)

Optional manual smoke (no real model):

```bash
python3 -m multi_agent_safety_sim.cli phase3-7-preflight
```

---

## 10. Quick red flags → stop merge

| Symptom | Problem |
|---------|---------|
| Request count ≠ 75 | Config/fixture/repetition drift |
| Architecture gets different fixture sets | Matched-evidence broken |
| Classifier uses `architecture_id` | Anti-tautology violated |
| Real run without clean worktree | Reproducibility gate bypassed |
| Summary rates use `planned_requests` as denominator | Wrong metrics |
| Checklist references `evaluate_episode` / `DeathCause.SURVIVED` | Stale rejected-build doc |
| Pilot conflated with Cemetery survival leaderboard | Scope / framing error |

---

## 11. Sign-off

| Check | Reviewer ✓ |
|-------|------------|
| Frozen input hashes recorded in manifest match preflight | |
| `build_posthumous_record()` is sole path from model text → label/PDS | |
| Real-run refusal paths tested | |
| No empirical claims in implementation PR description | |
| Cemetery / Death vs Divergence merge gate still satisfied | |