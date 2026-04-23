"""Preflight probe: one shallow round, return a 4-d signature.

The probe is the cheapest possible look at a task. It runs the agents in a
"shallow" configuration — which the caller picks — and returns just enough
information for the Bayesian recommender to propose a full configuration.

This module is framework-agnostic: it takes a ``RoundTrace`` (however the
caller produced it — real orchestrator, mock, or stored log) and returns a
``ProbeSignature``.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from perturb_eval.metrics import ace_norm, critique_severity_dispersion
from perturb_eval.types import RoundTrace


@dataclass(frozen=True)
class ProbeSignature:
    """The 4-d summary the recommender consumes."""

    ace_norm: float      # softmax-confidence entropy, normalised to [0,1]
    mean_conf: float     # average agent confidence
    max_conf: float      # max single-agent confidence
    csd: float           # critique severity dispersion

    def as_vector(self) -> tuple[float, float, float, float]:
        return (self.ace_norm, self.mean_conf, self.max_conf, self.csd)


def signature_from_round(rt: RoundTrace) -> ProbeSignature:
    """Compute the probe signature from a single RoundTrace."""
    confs = rt.confidences
    arr = list(confs)
    mean_c = sum(arr) / len(arr) if arr else 0.0
    max_c = max(arr) if arr else 0.0
    return ProbeSignature(
        ace_norm=ace_norm(confs),
        mean_conf=mean_c,
        max_conf=max_c,
        csd=critique_severity_dispersion(rt.critique_severities),
    )


def preflight(
    run_shallow_round: Callable[[], RoundTrace],
) -> ProbeSignature:
    """Execute a shallow one-round probe and return its signature.

    ``run_shallow_round`` is a user-supplied callable that performs the probe —
    typically a one-round invocation of the CellForge orchestrator with a
    reduced tool-call budget per agent. Keeping it as a callable avoids
    coupling this module to any particular orchestrator implementation.
    """
    rt = run_shallow_round()
    if rt.round_index != 0:
        raise ValueError("preflight expects a round 0 trace")
    return signature_from_round(rt)
