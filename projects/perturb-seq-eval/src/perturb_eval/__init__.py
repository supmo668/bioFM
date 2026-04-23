"""Agentic evaluation + Bayesian HP tuning for CellForge-style perturb-seq design."""

from perturb_eval.bayesian import BayesianRecommender, Recommendation
from perturb_eval.metrics import (
    ace,
    critique_severity_dispersion,
    delta_ace,
    delta_mean_confidence,
    round_metrics,
    run_metrics,
    tdi,
    winner_flip_rate,
)
from perturb_eval.probe import ProbeSignature, preflight
from perturb_eval.types import Config, RoundTrace, RunMetrics, RunTrace

__all__ = [
    "BayesianRecommender",
    "Config",
    "ProbeSignature",
    "Recommendation",
    "RoundTrace",
    "RunMetrics",
    "RunTrace",
    "ace",
    "critique_severity_dispersion",
    "delta_ace",
    "delta_mean_confidence",
    "preflight",
    "round_metrics",
    "run_metrics",
    "tdi",
    "winner_flip_rate",
]
