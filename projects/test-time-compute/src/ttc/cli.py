"""CLI entrypoint — ``python -m ttc ...`` or ``ttc ...``.

Example:

    ttc best-of-n --prompt ATGCGTACGT --n 8 --max-new-tokens 64
    ttc self-consistency --prompt ATGCGTACGT --n 16
    ttc sweep --prompt ATGCGTACGT --budget 64
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict

import typer

from ttc.config import RunConfig, SamplingConfig, StrategyName
from ttc.runner import run_strategy

app = typer.Typer(add_completion=False, help="Test-time compute scaling for BioFM-265M")


def _log_setup(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def _dump(result, as_json: bool) -> None:
    payload = {
        "strategy": result.strategy.value,
        "winner": result.winner.text,
        "winner_tokens": result.winner.tokens_generated,
        "n_candidates": len(result.candidates),
        "compute_budget": result.compute_budget,
        "verifier": result.verifier_name,
        "scores": list(result.scores),
    }
    if as_json:
        typer.echo(json.dumps(payload, indent=2))
    else:
        typer.echo(f"strategy         = {payload['strategy']}")
        typer.echo(f"verifier         = {payload['verifier']}")
        typer.echo(f"compute_budget   = {payload['compute_budget']} tokens")
        typer.echo(f"n_candidates     = {payload['n_candidates']}")
        typer.echo(f"winner (first 80)= {payload['winner'][:80]}")


@app.command("greedy")
def cmd_greedy(
    prompt: str = typer.Option(..., help="DNA seed sequence"),
    max_new_tokens: int = 64,
    model: str = "m42-health/BioFM-265M",
    verifier: str = "gc_content",
    json_out: bool = typer.Option(False, "--json"),
    verbose: bool = False,
) -> None:
    _log_setup(verbose)
    cfg = RunConfig(
        strategy=StrategyName.GREEDY,
        prompt=prompt,
        model_name=model,
        n_samples=1,
        sampling=SamplingConfig(max_new_tokens=max_new_tokens, do_sample=False),
        verifier=verifier,
    )
    _dump(run_strategy(cfg), json_out)


@app.command("best-of-n")
def cmd_best_of_n(
    prompt: str = typer.Option(..., help="DNA seed sequence"),
    n: int = typer.Option(8, help="number of samples"),
    max_new_tokens: int = 64,
    temperature: float = 1.0,
    top_k: int = 4,
    model: str = "m42-health/BioFM-265M",
    verifier: str = "gc_content",
    json_out: bool = typer.Option(False, "--json"),
    verbose: bool = False,
) -> None:
    _log_setup(verbose)
    cfg = RunConfig(
        strategy=StrategyName.BEST_OF_N,
        prompt=prompt,
        model_name=model,
        n_samples=n,
        sampling=SamplingConfig(
            max_new_tokens=max_new_tokens, temperature=temperature, top_k=top_k
        ),
        verifier=verifier,
    )
    _dump(run_strategy(cfg), json_out)


@app.command("self-consistency")
def cmd_sc(
    prompt: str = typer.Option(..., help="DNA seed sequence"),
    n: int = 16,
    max_new_tokens: int = 64,
    temperature: float = 0.8,
    top_k: int = 4,
    model: str = "m42-health/BioFM-265M",
    json_out: bool = typer.Option(False, "--json"),
    verbose: bool = False,
) -> None:
    _log_setup(verbose)
    cfg = RunConfig(
        strategy=StrategyName.SELF_CONSISTENCY,
        prompt=prompt,
        model_name=model,
        n_samples=n,
        sampling=SamplingConfig(
            max_new_tokens=max_new_tokens, temperature=temperature, top_k=top_k
        ),
    )
    _dump(run_strategy(cfg), json_out)


@app.command("sweep")
def cmd_sweep(
    prompt: str = typer.Option(..., help="DNA seed sequence"),
    budget: int = typer.Option(32, help="samples per temperature"),
    max_new_tokens: int = 64,
    model: str = "m42-health/BioFM-265M",
    verifier: str = "gc_content",
    json_out: bool = typer.Option(False, "--json"),
    verbose: bool = False,
) -> None:
    _log_setup(verbose)
    cfg = RunConfig(
        strategy=StrategyName.TEMPERATURE_SWEEP,
        prompt=prompt,
        model_name=model,
        n_samples=budget,
        sampling=SamplingConfig(max_new_tokens=max_new_tokens),
        verifier=verifier,
    )
    _dump(run_strategy(cfg), json_out)


if __name__ == "__main__":  # pragma: no cover
    app()
