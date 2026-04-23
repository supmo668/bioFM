"""E1 — metric overlap characterisation.

Generate synthetic multi-round traces via a lightweight DGP, compute every
current and new metric, and report pairwise Spearman rank correlation.
Metrics whose Spearman with their historical counterpart is ≥ 0.95 and
that add < 0.02 held-out signal go into ``drop_candidates`` — the
pre-registered decision rule from docs/SUPPLEMENT_DESIGN.md §1.3.
"""

from __future__ import annotations

import numpy as np

from perturb_eval.metrics import (
    ace_d,
    ace_norm,
    critique_severity_dispersion,
    critique_severity_star,
    round_metrics,
    tdi,
    tdi2,
    winner_flip_rate,
    delta_mean_confidence,
)
from perturb_eval.types import RoundTrace, RunTrace


_FEATURES = ("ace_h", "ace_d", "csd", "csd_star", "delta_c", "wfr", "tdi", "tdi2")
_OVERLAP_PAIRS = (("ace_h", "ace_d"), ("csd", "csd_star"), ("tdi", "tdi2"))


def _synthetic_trace(rng: np.random.Generator, difficulty: float) -> RunTrace:
    """Tiny DGP whose difficulty parameter drives confidence dispersion and
    severity patterns. Returns a 3-round, 5-agent trace."""
    rounds: list[RoundTrace] = []
    n_agents = 5
    winner = int(rng.integers(0, n_agents))
    for r in range(3):
        # Hard tasks → flatter confidences, more winner flips, more severity.
        base = np.clip(rng.normal(0.6, 0.1 + 0.2 * difficulty, size=n_agents), 0.01, 1.0)
        sev_rows = np.clip(
            rng.normal(0.2 + 0.4 * difficulty, 0.15, size=(n_agents, n_agents - 1)),
            0.0,
            1.0,
        )
        # Inject a "lone severe critic" for high-difficulty tasks.
        if difficulty > 0.6 and r == 0:
            sev_rows[0, 0] = 1.0
        if difficulty > 0.5 and rng.random() < 0.5:
            winner = int(rng.integers(0, n_agents))
        rounds.append(
            RoundTrace(
                round_index=r,
                agent_names=tuple(f"A{i}" for i in range(n_agents)),
                confidences=tuple(base.tolist()),
                critique_severities=tuple(tuple(row) for row in sev_rows),
                winner_index=winner,
                consensus_score=float(np.clip(0.9 - 0.5 * difficulty + rng.normal(0, 0.05), 0, 1)),
            )
        )
    return RunTrace(task_id="synth", rounds=tuple(rounds), converged=False, backbone="linear")


def _rank(x: np.ndarray) -> np.ndarray:
    """Dense ranks (ties → average rank); no scipy dependency."""
    order = np.argsort(x)
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(len(x), dtype=np.float64)
    return ranks


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    ra = _rank(a)
    rb = _rank(b)
    ra = ra - ra.mean()
    rb = rb - rb.mean()
    denom = float(np.sqrt((ra * ra).sum() * (rb * rb).sum()))
    if denom < 1e-12:
        return 0.0
    return float((ra * rb).sum() / denom)


def run_e1_metric_overlap(n_traces: int = 1000, seed: int = 2026) -> dict:
    """Run E1. Returns a dict with the Spearman matrix + drop decisions."""
    rng = np.random.default_rng(seed)
    feats: dict[str, list[float]] = {f: [] for f in _FEATURES}
    difficulties: list[float] = []
    for _ in range(n_traces):
        d = float(rng.uniform(0.0, 1.0))
        difficulties.append(d)
        trace = _synthetic_trace(rng, difficulty=d)
        per_round = tuple(round_metrics(r) for r in trace.rounds)
        last_rt = trace.rounds[-1]
        feats["ace_h"].append(ace_norm(last_rt.confidences))
        feats["ace_d"].append(ace_d(last_rt.confidences))
        feats["csd"].append(critique_severity_dispersion(last_rt.critique_severities))
        feats["csd_star"].append(critique_severity_star(last_rt.critique_severities))
        feats["delta_c"].append(delta_mean_confidence(per_round))
        feats["wfr"].append(winner_flip_rate(per_round))
        feats["tdi"].append(tdi(per_round))
        feats["tdi2"].append(
            tdi2(
                per_round,
                interaction_coeffs={"ace_norm_x_lack_conv": 0.2, "csd_x_wfr": 0.1},
            )
        )

    arrays = {f: np.asarray(v, dtype=np.float64) for f, v in feats.items()}
    n_feat = len(_FEATURES)
    rho = np.eye(n_feat)
    for i, a in enumerate(_FEATURES):
        for j, b in enumerate(_FEATURES):
            if i < j:
                rho[i, j] = _spearman(arrays[a], arrays[b])
                rho[j, i] = rho[i, j]

    # Drop-rule: Spearman(new, old) ≥ 0.95 → drop the new metric.
    drop: list[str] = []
    index = {name: i for i, name in enumerate(_FEATURES)}
    for old, new in _OVERLAP_PAIRS:
        if abs(rho[index[old], index[new]]) >= 0.95:
            drop.append(new)

    return {
        "spearman_matrix": rho,
        "feature_names": list(_FEATURES),
        "drop_candidates": drop,
        "n_traces": n_traces,
    }
