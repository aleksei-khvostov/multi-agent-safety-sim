"""
Typer CLI for multi_agent_safety_sim.

Commands:
- run
- list-scenarios
- validate-config
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .config import load_config
from .simulation.runner import SimulationRunner

app = typer.Typer(
    name="massim",
    help="Safety-first multi-agent alignment simulator",
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