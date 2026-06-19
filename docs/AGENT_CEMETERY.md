# Agent Cemetery v0.3

Agent Cemetery is an experimental survival-style stress-test harness. It compares simulated multi-agent architecture lineups under configurable oversight pressure by running repeated episodes, recording lifespan, assigning death causes, and producing leaderboard plus Kaplan-Meier style survival summaries. It is designed for evaluation-method development, not as a validated real-world risk metric.

This does not measure real-world agent danger. It is a toy survival-analysis harness for comparing simulated multi-agent architectures under configurable oversight/death policies. Dry-run mode validates the harness and artifact pipeline. Empirical claims require real-model runs with model, seed, policy, episode count, and prompt setup reported.

## Framing

Agent Cemetery is a harness, not a finding. The built-in architecture names are scenario/persona configurations, not validated psychological or safety categories. They are useful labels for deterministic stress-test lineups such as `honest_duo`, `deceptive_watchdog`, or `mixed_triangle`; they should not be treated as empirical claims about real systems.

Dry-run mode uses deterministic toy risks and dummy model metadata. If dry-run runs show 100% survival, that is expected DummyLLM/harness behavior under the default death policy, not evidence that any architecture is safe.

## Built-In Architectures

- `honest_duo`
- `deceptive_duo`
- `deceptive_watchdog`
- `power_duo`
- `power_watchdog`
- `mixed_triangle`
- `sycophant_duo`
- `sycophant_watchdog`

## CLI

```bash
python3 -m multi_agent_safety_sim.cli cemetery --episodes 5 --rounds 12 --dry-run
python3 -m multi_agent_safety_sim.cli cemetery -a deceptive_duo,deceptive_watchdog -e 10 --dry-run
```

Artifacts are generated under:

```text
data/runs/cemetery/cemetery_<timestamp>_<seed>/
```

Each run writes:

- `tournament_summary.json`
- `cohorts/<architecture_id>/cohort_summary.json`

## Survival Fields

Each episode records:

- `death_event`: whether the episode hit the configured death threshold.
- `censored`: whether the episode survived through the configured round horizon.
- `lifespan_rounds`: the round where death occurred, or the full horizon for censored survival.
- `death_cause`: a deterministic toy cause for death events, or `null` for censored survival.

Kaplan-Meier style rows report `at_risk`, `deaths`, `censored`, and `survival_probability` per round.

## Reproducibility Metadata

Artifacts include architecture IDs, episode count, round count, seed, dry-run flag, death policy configuration, model/provider metadata, timestamp, and run ID. `data/runs/` is gitignored, so Cemetery artifacts are generated outputs and should not be committed unless a future experiment explicitly justifies checking in a frozen artifact.
