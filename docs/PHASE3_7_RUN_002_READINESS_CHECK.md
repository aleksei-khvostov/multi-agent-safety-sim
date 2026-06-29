# Phase 3.7 Run 002 Readiness Check

This document records the documentation-only readiness check before Phase 3.7 Run 002. It does not run a model, call a provider API, add credentials, change classifier logic, change benchmark fixtures, modify CI behavior, or create run artifacts.

## Current Baseline

- Run 001 completed 75/75 evaluations with 0 provider failures.
- Run 001 original classifier-v1 result remains preserved.
- Run 001 post-run audit identified a likely lexical negation artifact.
- classifier-v2 was preregistered before reuse.
- Run 001-v2 diagnostic rescore was diagnostic-only, not replacement.
- PR-5.1 measurement gates are merged: RIB-16, Gravestone, NDB-20, NDB-20 SHA lock.

## Measurement Regime For Run 002

- Classifier version: `frozen_lexical_v2_negation`
- Run 002 is a new model run, not a correction or overwrite of Run 001.
- Run 002 should use the same matched-evidence Phase 3.7 inputs unless a future PR explicitly changes inputs.
- Residual stable-fixture false alarms from the Run 001-v2 diagnostic remain a known limitation.
- classifier-v2 is an improvement, not a complete fix.

## Preconditions Before Running

- `main` branch clean.
- `ruff` passes.
- `pytest` passes.
- `report-integrity run-all` passes.
- Provider and model explicitly configured.
- `run_date` explicitly set.
- API key only from environment.
- `data/runs` remains ignored.
- No generated run artifacts committed.

## Commands To Run Before Run 002

```bash
python3 -m ruff check .
PYTHONPATH=src python3 -m pytest
PYTHONPATH=src python3 -m multi_agent_safety_sim.cli report-integrity run-all
git status
```

## Interpretation Guardrails

Avoid claims about deception, intent, safety, or real-world behavior.

Run 002 should answer:

> Does persona-conditioned prompt framing produce measurable report-integrity divergence under this frozen setup?

Run 002 should not answer:

> Does the model deceive?
