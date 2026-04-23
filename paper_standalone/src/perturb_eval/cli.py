"""CLI: ``perturb-eval preflight | calibrate | evaluate``."""

from __future__ import annotations

import json
import logging

import typer

from perturb_eval.bayesian import BayesianRecommender
from perturb_eval.probe import ProbeSignature

app = typer.Typer(add_completion=False, help="Agentic eval + Bayesian HP tuning for perturb-seq")


@app.command("preflight")
def cmd_preflight(
    ace_norm: float = typer.Option(..., help="probe entropy in [0,1]"),
    mean_conf: float = typer.Option(..., help="mean agent confidence in [0,1]"),
    max_conf: float = typer.Option(..., help="max agent confidence in [0,1]"),
    csd: float = typer.Option(..., help="critique severity dispersion"),
    budget: float = typer.Option(float("inf"), help="FLOPs-proxy upper bound"),
    verbose: bool = typer.Option(False),
) -> None:
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
    sig = ProbeSignature(ace_norm=ace_norm, mean_conf=mean_conf, max_conf=max_conf, csd=csd)
    rec = BayesianRecommender().recommend(sig, budget=budget)
    payload = {
        "config": {
            "n_agents": rec.config.n_agents,
            "n_rounds": rec.config.n_rounds,
            "backbone": rec.config.backbone,
        },
        "log_posterior": rec.log_posterior,
        "budget": rec.budget,
        "calibration_n_tasks": rec.fit_on_n_tasks,
        "ranked": [
            {"n_agents": c.n_agents, "n_rounds": c.n_rounds, "backbone": c.backbone}
            for c in rec.ranked[:5]
        ],
    }
    typer.echo(json.dumps(payload, indent=2))


@app.command("evaluate")
def cmd_evaluate(
    trace_json: str = typer.Option(..., help="path to a RunTrace JSON dump"),
) -> None:  # pragma: no cover - uses filesystem
    """Compute ACE/CSD/ΔACE/ΔC/WFR/TDI for a stored RunTrace JSON dump."""
    raise NotImplementedError("Hook up to your serialiser of choice — see massgen_adapter.py")


if __name__ == "__main__":  # pragma: no cover
    app()
