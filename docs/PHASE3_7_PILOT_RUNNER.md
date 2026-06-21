# Phase 3.7 Pilot Runner

The Phase 3.7 pilot runner implements the preregistered matched-evidence report-generation design. It prepares execution plumbing only; no real model was run in this implementation PR.

## Matched-Evidence Design

Every architecture/persona condition receives the same frozen trace fixtures, final-report instruction, run parameters, classifier, labels, and PDS mapping. Only the architecture/persona prompt changes.

This is designed to test persona-to-report transfer: whether persona-conditioned prompts predict differences in final public reports when the evidence is held constant. It does not estimate real-model Agent Cemetery survival probabilities, because real-model survival would require dynamic environment runs where traces can differ across architectures.

The primary pilot tests prompt-conditioned report generation over fixed evidence, not actual multi-agent watchdog intervention. Watchdog alerts, unsafe transitions, and terminal outcomes are trace-fixture inputs in this pilot.

## Request Order

Requests are executed in deterministic block-randomized order. For each `(fixture_id, repetition)` block, every preregistered architecture appears exactly once, and the architecture order is shuffled with:

```text
<request_order_seed>:<fixture_id>:<repetition>
```

Each request records `request_id`, `request_sequence`, `architecture_id`, `fixture_id`, and `repetition`.

## Commands

Preflight makes no model calls:

```bash
python3 -m multi_agent_safety_sim.cli phase3-7-preflight \
  --config configs/phase3_7_real_model_pilot.yaml
```

Real-model execution requires an explicit confirmation flag and ready model fields:

```bash
python3 -m multi_agent_safety_sim.cli phase3-7-run \
  --config configs/phase3_7_real_model_pilot.yaml \
  --confirm-real-model-run
```

For OpenRouter runs, set `OPENROUTER_API_KEY` in the environment and record the OpenRouter model string exactly in `configs/phase3_7_real_model_pilot.yaml` before execution. The config `provider` field is passed explicitly to the real LLM client so it does not auto-select another provider when multiple API keys are present.

## Refusal Conditions

The real runner refuses execution when:

- the explicit confirmation flag is absent;
- provider, model string, or run date remains `TBD`;
- the git worktree is dirty;
- frozen files are missing or malformed;
- preregistered parameter overrides are attempted through the CLI.

## Artifacts

Runs write under:

```text
data/runs/phase3_7_real_model_pilot/<run_id>/
```

Files:

- `run_manifest.json`
- `raw_responses.jsonl`
- `evaluated_records.jsonl`
- `summary.json`
- `failures.jsonl`

The manifest records SHA-256 hashes of frozen inputs, the git commit, worktree-clean status, Python version, package version when available, model metadata, request counts, fixture IDs, architecture IDs, and the pilot caveat.

`run_manifest.json` is written before the provider client is created and before the first model call. It starts with `status: running`, a start timestamp, request-order metadata, frozen input hashes, provider/model/run metadata, git metadata, and requested request counts. On normal completion the same manifest is updated to `completed` or `completed_with_provider_failures`. If the run is interrupted, the manifest is updated to `interrupted` with interruption type/message and the flushed raw/evaluated/failure counts; `summary.json` is not written for interrupted runs.

`raw_responses.jsonl`, `evaluated_records.jsonl`, and `failures.jsonl` are written incrementally after each request so paid responses are not lost if a run is interrupted before final manifest and summary writing.

Empty or whitespace-only model responses are recorded as `empty_response` failures and are excluded from evaluated metrics. Provider exceptions are recorded as `provider_exception` failures. Summary denominators distinguish `requested_requests`, `successful_evaluations`, and `failed_requests`; rates use `successful_evaluations` as the denominator. The summary records `analysis_status: complete` only when no provider failures occurred, and `analysis_status: incomplete_provider_failures` otherwise.

## Non-Claims

This pilot does not detect deception, prove intent, estimate real-world risk, validate architecture danger/safety, or generalize beyond one model/configuration. Generated pilot data from one model/configuration does not establish general model behavior.
