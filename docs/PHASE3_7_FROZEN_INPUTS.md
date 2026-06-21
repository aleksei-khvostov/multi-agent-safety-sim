# Phase 3.7 Frozen Inputs

This document records the frozen pre-data input conditions for the planned Phase 3.7 controlled real-model pilot.

No real-model run was performed in this PR. No API calls were added, and no result artifacts were generated.

The frozen files are:

- `configs/phase3_7_real_model_pilot.yaml`
- `prompts/phase3_7/system_base.md`
- `prompts/phase3_7/honest_duo.md`
- `prompts/phase3_7/deceptive_duo.md`
- `prompts/phase3_7/deceptive_watchdog.md`
- `prompts/phase3_7/power_duo.md`
- `prompts/phase3_7/power_watchdog.md`
- `prompts/phase3_7/final_report_instruction.md`

These files define input conditions, not measured outcomes. Architecture labels are used only for grouping and aggregation after the run. Final report integrity is measured later from trace evidence and final report text under the frozen reported-outcome classifier.

The setup preserves the Phase 3.7 anti-tautology principle:

```text
persona-label = input condition, not measured outcome
```

The reported-outcome classifier remains architecture-blind, and the calibration set is frozen before real-model outputs are observed.
