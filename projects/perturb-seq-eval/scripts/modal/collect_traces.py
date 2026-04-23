"""Collect real CellForge round-0 traces for each Adamson perturbation.

Stub for MC3b in docs/REVIEWER_CRITIQUE.md / §7 Open Question #1 of
docs/SUPPLEMENT.md. The current supplement uses simulated probe
signatures on Adamson; this module closes that gap by harvesting the
round-0 trace from a live 5-agent orchestrator run per perturbation and
projecting it onto the 4-dim probe schema (ACE_norm, mean(c), CSD,
max(c)).

Not yet wired end-to-end. The skeleton below shows the intended call
surface so the supplement can reference it by name; the actual
orchestrator connection, LLM severity rater, and volume-commit paths
will land in a follow-up PR per INTERNAL_FOLLOWUP.md §3 D1.

Usage (once implemented)::

    modal run scripts/modal/collect_traces.py::collect_adamson_probes \\
        --openrouter-model nvidia/nemotron-3-super-120b-a12b:free

Expected output: ``/data/artifacts/probes.json`` keyed by perturbation
name, each value a 4-dim list. Consumed by ``run_e3_adamson``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

import numpy as np


# OSF / OpenRouter config is loaded from .env — see research/PUBLISHING_RUNBOOK.md.
ADAMSON_H5AD = "/data/adamson/Adamson2016_pilot.h5ad"
PROBE_OUT_PATH = "/data/artifacts/probes.json"


class OrchestratorClient(Protocol):
    """Minimal contract the collector needs from a CellForge-compatible
    5-agent orchestrator. Any binding (MassGen, CellForge, a local mock)
    that satisfies this Protocol plugs in."""

    def run_round_zero(
        self,
        task: str,
        *,
        perturbation: str,
        modality: str,
    ) -> dict: ...


def project_round_zero_to_probe(round0: dict) -> np.ndarray:
    """Turn a coordination-tracker round-0 snapshot into a 4-dim probe.

    Expected ``round0`` fields:
      - ``confidences`` : list[float] — per-agent confidence in [0, 1]
      - ``critique_severities`` : list[list[float]] — row-per-agent severity matrix
    """
    from perturb_eval.experiments.common import probe_signature_from_trace
    from perturb_eval.types import RoundTrace, RunTrace

    rt = RoundTrace(
        round_index=0,
        agent_names=tuple(round0.get("agent_names", ("A", "B", "C", "D", "E"))),
        confidences=tuple(round0["confidences"]),
        critique_severities=tuple(tuple(r) for r in round0["critique_severities"]),
        winner_index=int(round0.get("winner_index", 0)),
        consensus_score=float(round0.get("consensus_score", 0.5)),
    )
    run = RunTrace(task_id=round0.get("task_id", "adamson"), rounds=(rt,),
                   converged=False, backbone="live")
    return probe_signature_from_trace(run)


def collect_adamson_probes(
    client: OrchestratorClient,
    perturbations: list[str],
    *,
    out_path: str = PROBE_OUT_PATH,
) -> dict[str, list[float]]:
    """Iterate perturbations, harvest one round-0 trace each, project → probe.

    NOT YET IMPLEMENTED END-TO-END. This is the MC3b skeleton per
    docs/REVIEWER_CRITIQUE.md. Contributions welcome.
    """
    raise NotImplementedError(
        "MC3b — live-trace collection is the last open blocker before "
        "the ICLR-workshop submission bar. See docs/INTERNAL_FOLLOWUP.md §2."
    )
