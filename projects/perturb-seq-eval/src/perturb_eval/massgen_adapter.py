"""Expose the evaluation pipeline as a MassGen skill.

MassGen (``tools/MassGen/``) supports framework-agnostic skills installed via
``npx skills add <path>``. This module provides the entrypoints a MassGen skill
manifest needs: a ``preflight`` callable and an ``evaluate`` callable, each
taking a dict-like input and returning a JSON-serialisable dict.

The adapter does not import MassGen directly — that way this module stays
importable without the MassGen dev dependencies.
"""

from __future__ import annotations

from typing import Any

from perturb_eval.bayesian import BayesianRecommender
from perturb_eval.metrics import run_metrics
from perturb_eval.probe import ProbeSignature
from perturb_eval.types import RunTrace


def preflight_skill(payload: dict[str, Any]) -> dict[str, Any]:
    """MassGen-shaped entrypoint for the preflight recommender.

    Expected payload fields:
        probe: {ace_norm, mean_conf, max_conf, csd}
        budget: optional float (FLOPs proxy)

    Returns a JSON-friendly dict with the recommendation.
    """
    p = payload.get("probe") or {}
    sig = ProbeSignature(
        ace_norm=float(p["ace_norm"]),
        mean_conf=float(p["mean_conf"]),
        max_conf=float(p["max_conf"]),
        csd=float(p["csd"]),
    )
    budget = float(payload.get("budget", float("inf")))
    rec = BayesianRecommender().recommend(sig, budget=budget)
    return {
        "config": {
            "n_agents": rec.config.n_agents,
            "n_rounds": rec.config.n_rounds,
            "backbone": rec.config.backbone,
        },
        "log_posterior": rec.log_posterior,
        "budget": rec.budget,
        "calibration_n_tasks": rec.fit_on_n_tasks,
    }


def evaluate_skill(payload: dict[str, Any]) -> dict[str, Any]:
    """MassGen-shaped entrypoint for scoring a completed run.

    Expected payload fields:
        run: JSON-serialised RunTrace (already hydrated by the caller; we assume
             it is passed in as a RunTrace instance)
    """
    trace = payload["run"]
    if not isinstance(trace, RunTrace):
        raise TypeError("evaluate_skill expects a RunTrace in payload['run']")
    m = run_metrics(trace)
    return {
        "task_id": m.task_id,
        "tdi": m.tdi,
        "delta_ace": m.delta_ace,
        "delta_mean_confidence": m.delta_mean_confidence,
        "winner_flip_rate": m.winner_flip_rate,
        "final_consensus_score": m.final_consensus_score,
        "n_rounds": len(m.per_round),
    }
