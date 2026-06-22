"""
Typer CLI for multi_agent_safety_sim.

Commands:
- run
- cemetery
- posthumous-report
- gravestone analyze
- phase3-7-preflight
- phase3-7-run
- list-scenarios
- validate-config
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .config import load_config
from .evaluation.gravestone import (
    GravestoneArtifactError,
    build_gravestone_summary,
    write_gravestone_summary,
)
from .evaluation.phase3_7_rescore import (
    DIAGNOSTIC_CAVEAT,
    rescore_run_with_classifier_v2,
    write_diagnostic_rescore,
)
from .simulation.cemetery_runner import parse_architecture_ids, run_tournament
from .simulation.phase3_7_pilot_runner import (
    compute_frozen_input_hashes,
    run_phase3_7_pilot,
    validate_preflight,
)
from .simulation.runner import SimulationRunner

app = typer.Typer(
    name="massim",
    help="Safety-first multi-agent alignment simulator",
    add_completion=False,
)
gravestone_app = typer.Typer(
    name="gravestone",
    help="Metric-honesty analysis for report-integrity artifacts",
    add_completion=False,
)
console = Console()


@app.command()
def run(
    scenario: str = typer.Option(None, "--scenario", "-s", help="Scenario name from config"),
    agents: str = typer.Option(
        "honest,deceptive",
        "--agents",
        "-a",
        help=(
            "Comma-separated personas "
            "(honest,deceptive,watchdog,power,sycophant,planner,executor "
            "or full keys from config)"
        ),
    ),
    rounds: int | None = typer.Option(
        None,
        "--rounds",
        "-r",
        help="Number of scenario steps/rounds per trial",
    ),
    trials: int = typer.Option(5, "--trials", "-t", help="How many independent trials to run"),
    seed: int | None = typer.Option(None, help="Base random seed"),
    config: Path = typer.Option("config.yaml", exists=True, readable=True),
    dry_run: bool = typer.Option(True, help="Force DummyLLMClient (no real API calls)"),
    model: str | None = typer.Option(
        None,
        "--model",
        "-m",
        help="LLM model to use. Overrides config.",
    ),
    output_root: str = typer.Option("data/runs", help="Where to store JSON traces"),
) -> None:
    """
    Run a multi-agent safety experiment with LLM agents.

    Example dry-run:
        massim run --scenario prisoners_dilemma --agents honest,deceptive,watchdog --rounds 10 --trials 5 --dry-run

    Example planner-delegation dry-run:
        massim run --scenario planner_delegation --agents planner,executor,watchdog --rounds 4 --trials 1 --dry-run
    """
    cfg = load_config(config)

    scenario_name = scenario or cfg.default_scenario
    if scenario_name not in cfg.scenarios:
        console.print(f"[red]Unknown scenario:[/red] {scenario_name}")
        raise typer.Exit(1)

    persona_list = [p.strip() for p in agents.split(",") if p.strip()]

    console.print(f"[bold green]Starting experiment[/bold green]  scenario={scenario_name}")
    console.print(f"  personas     : {persona_list}")
    console.print(f"  trials       : {trials}")
    console.print(f"  rounds/trial : {rounds or cfg.scenarios[scenario_name].get('steps', 20)}")
    console.print(f"  dry_run      : {dry_run}")
    console.print(
        f"  safety caps  : max_tokens={cfg.safety.max_tokens_per_run}, "
        f"max_steps={cfg.safety.max_steps}"
    )

    runner = SimulationRunner(cfg)

    try:
        result = asyncio.run(
            runner.run_experiment(
                scenario_name=scenario_name,
                agent_personas=persona_list,
                num_rounds=rounds,
                num_trials=trials,
                seed=seed,
                dry_run=dry_run,
                model=model,
                output_root=output_root,
            )
        )
    except Exception as exc:
        console.print(f"[red]Experiment failed:[/red] {exc}")
        raise typer.Exit(2) from exc

    console.print("\n[bold cyan]=== Experiment Complete ===[/bold cyan]")
    console.print(f"Run ID : [bold]{result.run_id}[/bold]")
    if result.output_dir:
        console.print(f"Results: [dim]{result.output_dir}[/dim]")

    agg = result.aggregate
    table = Table(title="Aggregate Results", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Trials completed", str(agg.get("trials_completed", result.num_trials)))

    if result.scenario == "planner_delegation":
        table.add_row("Audit complete rate", f"{agg.get('audit_complete_rate', 0):.3f}")
        table.add_row(
            "Delegation executed rate",
            f"{agg.get('delegation_executed_rate', 0):.3f}",
        )
        table.add_row(
            "Review completed rate",
            f"{agg.get('review_completed_rate', 0):.3f}",
        )
        table.add_row("Escalation rate", f"{agg.get('escalation_rate', 0):.3f}")
        table.add_row("Total safety events", str(agg.get("total_safety_events", 0)))
        table.add_row("Total tokens used", str(agg.get("total_tokens_used", 0)))
    else:
        table.add_row("Mean cooperation rate", f"{agg.get('mean_cooperation_rate', 0):.3f}")
        table.add_row(
            "Trials with collusion detected",
            f"{agg.get('trials_with_collusion_detected', 0)}%",
        )
        table.add_row("Total safety events", str(agg.get("total_safety_events", 0)))
        table.add_row("Total collusion incidents", str(agg.get("total_collusion_incidents", 0)))
        table.add_row("Total tokens used", str(agg.get("total_tokens_used", 0)))

    console.print(table)

    if result.trials:
        t_table = Table(title="Per-Trial Highlights (first 8)", show_header=True)
        t_table.add_column("#", style="dim")

        if result.scenario == "planner_delegation":
            t_table.add_column("Status")
            t_table.add_column("Audit", justify="right")
            t_table.add_column("Final action", justify="right")
            t_table.add_column("Safety events", justify="right")

            for trial in result.trials[:8]:
                final_round = (
                    trial.round_trace[-1].get("round_info", {})
                    if trial.round_trace
                    else {}
                )
                t_table.add_row(
                    str(trial.trial_id),
                    str(final_round.get("status", "unknown")),
                    str(final_round.get("audit_complete", False)),
                    "yes" if final_round.get("final_action") else "no",
                    str(len(trial.safety_events)),
                )
        else:
            t_table.add_column("Coop %", justify="right")
            t_table.add_column("Collusion", justify="right")
            t_table.add_column("Safety events", justify="right")

            for trial in result.trials[:8]:
                t_table.add_row(
                    str(trial.trial_id),
                    f"{trial.cooperation_rate:.2f}",
                    str(trial.collusion_incidents),
                    str(len(trial.safety_events)),
                )

        console.print(t_table)

    console.print("\n[green]✓[/green] Full traces and summary saved to disk.")
    if dry_run:
        console.print(
            "[yellow]Note:[/yellow] This was a dry-run. "
            "DummyLLMClient was used, so no real model API was called."
        )


@app.command()
def cemetery(
    architectures: str | None = typer.Option(
        None,
        "--architectures",
        "-a",
        help="Comma-separated architecture IDs. Defaults to all built-in Cemetery architectures.",
    ),
    episodes: int = typer.Option(5, "--episodes", "-e", help="Episodes per architecture"),
    rounds: int = typer.Option(12, "--rounds", "-r", help="Maximum rounds per episode"),
    seed: int = typer.Option(0, "--seed", help="Deterministic tournament seed"),
    dry_run: bool = typer.Option(True, help="Use deterministic dry-run harness behavior"),
    output_root: Path = typer.Option(
        "data/runs/cemetery",
        "--output-root",
        help="Where to store generated Cemetery artifacts",
    ),
    death_threshold: float = typer.Option(
        1.0,
        "--death-threshold",
        help="Toy death threshold for survival events",
    ),
    oversight_pressure: float = typer.Option(
        0.05,
        "--oversight-pressure",
        help="Configurable toy oversight pressure added per round",
    ),
    model: str | None = typer.Option(
        None,
        "--model",
        "-m",
        help="Model metadata to record. Dry-run defaults to dummy-llm.",
    ),
) -> None:
    """Run the experimental Agent Cemetery survival-analysis harness."""
    try:
        architecture_ids = parse_architecture_ids(architectures)
        result = run_tournament(
            architectures=architecture_ids,
            episodes=episodes,
            rounds=rounds,
            seed=seed,
            dry_run=dry_run,
            output_root=output_root,
            death_threshold=death_threshold,
            oversight_pressure=oversight_pressure,
            model=model,
        )
    except Exception as exc:
        console.print(f"[red]Agent Cemetery failed:[/red] {exc}")
        raise typer.Exit(2) from exc

    metadata = result.tournament_summary["metadata"]
    console.print("[bold cyan]Agent Cemetery v0.3[/bold cyan]")
    console.print("Harness validation only: dry-run results are not empirical model findings.")
    console.print(f"  architectures : {metadata['architectures']}")
    console.print(f"  episodes      : {metadata['episodes']}")
    console.print(f"  rounds        : {metadata['rounds']}")
    console.print(f"  seed          : {metadata['seed']}")
    console.print(f"  dry_run       : {metadata['dry_run']}")
    console.print(f"  output_dir    : {result.output_dir}")

    table = Table(title="Cemetery Leaderboard", show_header=True, header_style="bold magenta")
    table.add_column("Rank", style="dim")
    table.add_column("Architecture", style="cyan")
    table.add_column("Survival", justify="right")
    table.add_column("Mean lifespan", justify="right")
    table.add_column("Deaths", justify="right")
    table.add_column("Censored", justify="right")

    for row in result.tournament_summary["leaderboard"]:
        table.add_row(
            str(row["rank"]),
            row["architecture_id"],
            f"{row['survival_rate']:.3f}",
            f"{row['mean_lifespan_rounds']:.2f}",
            str(row["deaths"]),
            str(row["censored"]),
        )
    console.print(table)


@app.command("posthumous-report")
def posthumous_report(run_dir: Path = typer.Argument(..., help="Agent Cemetery run directory")) -> None:
    """Print a compact Death vs Divergence report for a Cemetery run."""
    report_path = run_dir / "posthumous_divergence.json"
    if not report_path.exists():
        console.print(
            "[red]Missing posthumous divergence artifact:[/red] "
            f"{report_path}. Run the cemetery command again to generate v0.4 artifacts."
        )
        raise typer.Exit(2)

    data = json.loads(report_path.read_text(encoding="utf-8"))
    console.print("[bold cyan]Death vs Divergence v0.4[/bold cyan]")
    console.print("Trace/report consistency only: this is not deception detection.")
    console.print(data["caveat"])

    table = Table(title="Posthumous Divergence Summary", show_header=True)
    table.add_column("Architecture", style="cyan")
    table.add_column("Episodes", justify="right")
    table.add_column("Divergence rate", justify="right")
    table.add_column("Mean PDS", justify="right")
    table.add_column("Top label")

    for row in data["by_architecture"]:
        table.add_row(
            row["architecture_id"],
            str(row["episodes"]),
            f"{row['posthumous_divergence_rate']:.3f}",
            f"{row['mean_pds_score']:.3f}",
            row["top_label"],
        )
    console.print(table)


@gravestone_app.command("analyze")
def gravestone_analyze(
    run_dir: Path = typer.Argument(..., help="Agent Cemetery run directory"),
    write_json: bool = typer.Option(
        True,
        "--write-json/--no-write-json",
        help="Write gravestone_summary.json into the run directory",
    ),
) -> None:
    """Recompute report-integrity rates with explicit denominators from cemetery artifacts."""
    try:
        summary = build_gravestone_summary(run_dir)
        if write_json:
            output_path = write_gravestone_summary(run_dir, summary=summary)
        else:
            output_path = run_dir / "gravestone_summary.json"
    except GravestoneArtifactError as exc:
        console.print(f"[red]Missing or invalid report-integrity artifacts:[/red] {exc}")
        raise typer.Exit(2) from exc
    except Exception as exc:
        console.print(f"[red]Gravestone analysis failed:[/red] {exc}")
        raise typer.Exit(2) from exc

    overall = summary["summary"]
    console.print("[bold cyan]Gravestone Analyzer[/bold cyan]")
    console.print(summary["caveat"])
    console.print(f"[dim]{summary['legacy_field_note']}[/dim]")
    if write_json:
        console.print(f"[dim]Wrote {output_path}[/dim]")

    console.print(
        "\nDenominator: "
        f"{overall['denominator']['name']} = {overall['denominator']['eligible_records']}"
    )
    console.print(
        f"  posthumous_overclaim_rate          : "
        f"{overall['posthumous_overclaim_rate']:.3f} "
        f"({overall['posthumous_overclaim_count']}/{overall['denominator']['eligible_records']})"
    )
    console.print(
        f"  report_integrity_divergence_rate   : "
        f"{overall['report_integrity_divergence_rate']:.3f} "
        f"({overall['report_integrity_divergence_count']}/"
        f"{overall['denominator']['eligible_records']})"
    )
    console.print(f"  mean_pds_score                     : {overall['mean_pds_score']:.3f}")

    table = Table(title="Gravestone by Architecture", show_header=True)
    table.add_column("Architecture", style="cyan")
    table.add_column("Eligible", justify="right")
    table.add_column("Overclaim rate", justify="right")
    table.add_column("Divergence rate", justify="right")
    table.add_column("Mean PDS", justify="right")

    for row in summary["by_architecture"]:
        denom = row["denominator"]["eligible_records"]
        table.add_row(
            row["architecture_id"],
            str(denom),
            f"{row['posthumous_overclaim_rate']:.3f}",
            f"{row['report_integrity_divergence_rate']:.3f}",
            f"{row['mean_pds_score']:.3f}",
        )
    console.print(table)


app.add_typer(gravestone_app)


@app.command("phase3-7-preflight")
def phase3_7_preflight(
    config: Path = typer.Option(
        "configs/phase3_7_real_model_pilot.yaml",
        "--config",
        help="Frozen Phase 3.7 pilot config",
    ),
    require_ready: bool = typer.Option(
        False,
        "--require-ready",
        help="Fail if provider/model/run_date remain TBD",
    ),
) -> None:
    """Validate frozen Phase 3.7 pilot inputs without making model calls."""
    try:
        preflight = validate_preflight(config_path=config, require_ready=require_ready)
        hashes = compute_frozen_input_hashes(config_path=config, config=preflight["config"])
    except Exception as exc:
        console.print(f"[red]Phase 3.7 preflight failed:[/red] {exc}")
        raise typer.Exit(2) from exc

    cfg = preflight["config"]
    console.print("[bold cyan]Phase 3.7 matched-evidence preflight[/bold cyan]")
    console.print(f"experiment_id : {cfg['experiment_id']}")
    console.print(f"pilot_mode    : {cfg['pilot_mode']}")
    console.print(f"architectures : {cfg['architectures']}")
    console.print(f"fixtures      : {[fixture.fixture_id for fixture in preflight['fixtures']]}")
    console.print(f"repetitions   : {cfg['run_parameters']['repetitions']}")
    console.print(f"request_order : {cfg['execution']['request_order']}")
    console.print(f"order_seed    : {cfg['execution']['request_order_seed']}")
    console.print(f"request_count : {preflight['request_count']}")
    console.print(f"worktree_clean: {preflight['git_worktree_clean']}")

    table = Table(title="Frozen Input SHA-256", show_header=True)
    table.add_column("Path", style="cyan")
    table.add_column("SHA-256")
    for path, digest in sorted(hashes.items()):
        table.add_row(path, digest)
    console.print(table)
    console.print("No model call was made.")


@app.command("phase3-7-run")
def phase3_7_run(
    config: Path = typer.Option(
        "configs/phase3_7_real_model_pilot.yaml",
        "--config",
        help="Frozen Phase 3.7 pilot config",
    ),
    confirm_real_model_run: bool = typer.Option(
        False,
        "--confirm-real-model-run",
        help="Required confirmation for real-model API execution",
    ),
) -> None:
    """Run the preregistered Phase 3.7 matched-evidence pilot."""
    if not confirm_real_model_run:
        console.print("[red]Refusing real-model run:[/red] --confirm-real-model-run is required.")
        raise typer.Exit(2)

    try:
        output_dir = asyncio.run(
            run_phase3_7_pilot(
                config_path=config,
                confirm_real_model_run=confirm_real_model_run,
            )
        )
    except Exception as exc:
        console.print(f"[red]Phase 3.7 run refused or failed:[/red] {exc}")
        raise typer.Exit(2) from exc

    console.print("[bold cyan]Phase 3.7 pilot complete[/bold cyan]")
    console.print(f"output_dir: {output_dir}")
    console.print(
        "Caveat: pilot data from one model/configuration does not establish "
        "general model behavior, deception detection, intent, or real-world risk."
    )


@app.command("phase3-7-rescore-run-001-v2")
def phase3_7_rescore_run_001_v2(
    run_dir: Path = typer.Option(
        ...,
        "--run-dir",
        help="Phase 3.7 Run 001 artifact directory",
    ),
) -> None:
    """Write a diagnostic classifier-v2 rescore for saved Run 001 outputs."""
    try:
        result = rescore_run_with_classifier_v2(run_dir)
        output_path = write_diagnostic_rescore(run_dir, result)
    except Exception as exc:
        console.print(f"[red]Phase 3.7 diagnostic rescore failed:[/red] {exc}")
        raise typer.Exit(2) from exc

    original = result["original_metrics"]
    v2 = result["v2_diagnostic_metrics"]
    original_labels = original["label_distribution"]
    v2_labels = v2["label_distribution"]
    console.print("[bold cyan]Phase 3.7 Run 001 classifier-v2 diagnostic rescore[/bold cyan]")
    console.print(f"wrote: {output_path}")
    console.print(f"original mean PDS              : {original['mean_pds_score']}")
    console.print(f"v2 diagnostic mean PDS         : {v2['mean_pds_score']}")
    console.print(
        "original false_alarm_or_underclaim count : "
        f"{original_labels.get('false_alarm_or_underclaim', 0)}"
    )
    console.print(
        "v2 false_alarm_or_underclaim count       : "
        f"{v2_labels.get('false_alarm_or_underclaim', 0)}"
    )
    console.print(
        "original posthumous_overclaim count      : "
        f"{original_labels.get('posthumous_overclaim', 0)}"
    )
    console.print(
        "v2 posthumous_overclaim count            : "
        f"{v2_labels.get('posthumous_overclaim', 0)}"
    )
    console.print(DIAGNOSTIC_CAVEAT)


@app.command()
def list_scenarios(config: Path = typer.Option("config.yaml", exists=True)) -> None:
    """Show available scenarios defined in config.yaml."""
    cfg = load_config(config)

    table = Table(title="Available Scenarios")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Agents")
    table.add_column("Steps")

    for name, data in cfg.scenarios.items():
        table.add_row(
            name,
            str(data.get("description", ""))[:60],
            str(data.get("agents", "?")),
            str(data.get("steps", cfg.safety.max_steps)),
        )

    console.print(table)


@app.command()
def validate_config(config: Path = typer.Option("config.yaml", exists=True)) -> None:
    """Validate config.yaml against safety and schema requirements."""
    try:
        cfg = load_config(config)
        console.print("[green]✓[/green] Config is valid.")
        console.print(f"  Default scenario: {cfg.default_scenario}")
        console.print(f"  Strict mode: {cfg.safety.strict_mode}")
        console.print(f"  Personas: {list(cfg.agent_personas.keys())}")
    except Exception as exc:
        console.print(f"[red]✗ Config validation failed:[/red] {exc}")
        raise typer.Exit(2) from exc


def main() -> None:
    app()


if __name__ == "__main__":
    main()
