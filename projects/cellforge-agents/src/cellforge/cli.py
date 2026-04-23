"""CLI for the 5-agent group generation PoC."""

from __future__ import annotations

import json
import logging

import typer

from cellforge.agents import build_default_team
from cellforge.orchestrator import Orchestrator
from cellforge.problem import Modality, Problem

app = typer.Typer(add_completion=False, help="CellForge-inspired 5-agent perturbation modelling PoC")


@app.command("run")
def cmd_run(
    perturbation: str = typer.Option(..., help="e.g. 'GSK3B knockout', 'LPS 100 ng/mL'"),
    modality: Modality = typer.Option(Modality.SCRNA),
    cell_type_hint: str = typer.Option(None),
    max_rounds: int = typer.Option(2, min=1, max=5),
    verbose: bool = typer.Option(False),
) -> None:
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO, format="%(message)s")
    problem = Problem(
        perturbation=perturbation,
        modality=modality,
        cell_type_hint=cell_type_hint,
    )
    orch = Orchestrator(build_default_team(), max_rounds=max_rounds)
    result = orch.run(problem)
    payload = {
        "converged": result.converged,
        "consensus_score": round(result.consensus_score, 3),
        "winner_agent": result.winner.agent,
        "winner_content": result.winner.content,
        "winner_rationale": result.winner.rationale,
        "n_rounds": len(result.rounds),
        "n_proposals": len(result.all_proposals),
        "n_critiques": len(result.all_critiques),
    }
    typer.echo(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":  # pragma: no cover
    app()
