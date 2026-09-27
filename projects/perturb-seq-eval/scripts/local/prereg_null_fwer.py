"""Null false-positive rates of the pre-registered H4 gate, computed THROUGH THE ESTIMATOR'S OWN CODE PATH.

CTO #269: the magnitude must come from permutation against the actual estimator (preregistered._rho: average-rank
Spearman), not from a normal approximation. Reproducible: fixed seed, no data needed.

1. Per-test null  P(rho_hat > 0.5)  at n = 20, 21, 41 — permutation of y against a fixed, tie-free x.
2. Gate FWER — Monte Carlo of the WHOLE pre-registered gate: two datasets (n=21 Adamson, n=20 Norman), per dataset the
   three quantities {ACE_norm, 1-dC, TDI_lifecycle = preregistered.tdi_lifecycle(ACE, 1-dC)} against a null MSD; the gate
   fires if ANY of the six rho_hat exceeds 0.5. The dependence between ACE and 1-dC is unknown, so both extremes are run:
   independent (upper) and identical ranks (lower); the true rate lies between them.
3. The pooled comparator: one quantity, one Spearman over n = 41.

Definitions (``--defs``):
  a1 (default) — the definitions in force at amendment 1 (0c2932a): ACE_norm and clipped 1-dC on [0, 1],
     TDI_lifecycle = preregistered.tdi_lifecycle (clipped to [0, 1]). Reproduces the published amendment-1 table.
  a2 — the AMENDMENT 2 definitions (principal rulings A2-10 (a), A2-11 (a); CTO #430): ACE := metrics.ace_d on
     [0, 1]; UNCLIPPED 1-dC on [0, 2]; TDI_lifecycle = 7/12 * ACE + 5/12 * (1-dC) with NO outer clip, range
     [0, 17/12]. Adds the third dependence arm A2-9 requires: REVERSED ranks (the negative-dependence extreme),
     so the reported range bounds the whole dependence family, not only its non-negative half. The a2 TDI is
     written out here, not imported, because the code change that implements it is a measurand fix that lands
     after the amendment lock; the formula is identical to the amended text.

    .venv/bin/python scripts/local/prereg_null_fwer.py [--defs a1|a2]
"""
from __future__ import annotations

import argparse
import json

import numpy as np

from perturb_eval.experiments.preregistered import rho, tdi_lifecycle

SEED, THRESH = 2026, 0.5
N_PERM, N_SIM = 200_000, 100_000
N_ADAMSON, N_NORMAN, N_POOLED = 21, 20, 41


def per_test_null(n: int, rng: np.random.Generator) -> float:
    x = np.arange(n, dtype=float)
    y = np.arange(n, dtype=float)
    hits = sum((rho(x, rng.permutation(y)) or -2.0) > THRESH for _ in range(N_PERM))
    return hits / N_PERM


A2_W_ACE, A2_W_DC = 7 / 12, 5 / 12


def tdi_lifecycle_a2(ace: float, one_minus_dc: float) -> float:
    """Amendment-2 TDI_lifecycle: unclipped weighted sum, range [0, 17/12]."""
    return A2_W_ACE * ace + A2_W_DC * one_minus_dc


def one_dataset_fires(n: int, rng: np.random.Generator, dependence: str, defs: str) -> bool:
    msd = rng.random(n)
    ace = rng.random(n)
    if defs == "a1":
        omdc = ace.copy() if dependence == "identical" else rng.random(n)
        tdi = np.array([tdi_lifecycle(a, b) for a, b in zip(ace, omdc)])
    else:  # a2: unclipped 1-dC on [0, 2]
        if dependence == "identical":
            omdc = 2.0 * ace            # same ranks as ACE
        elif dependence == "reversed":
            omdc = 2.0 * (1.0 - ace)    # opposite ranks to ACE
        else:
            omdc = 2.0 * rng.random(n)
        tdi = np.array([tdi_lifecycle_a2(a, b) for a, b in zip(ace, omdc)])
    return any((rho(q, msd) or -2.0) > THRESH for q in (ace, omdc, tdi))


def gate_fwer(rng: np.random.Generator, dependence: str, defs: str) -> float:
    fires = 0
    for _ in range(N_SIM):
        a = one_dataset_fires(N_ADAMSON, rng, dependence, defs)
        b = one_dataset_fires(N_NORMAN, rng, dependence, defs)
        fires += a or b
    return fires / N_SIM


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--defs", choices=("a1", "a2"), default="a1")
    defs = ap.parse_args().defs
    arms = ("independent", "identical") if defs == "a1" else ("independent", "identical", "reversed")
    rng = np.random.default_rng(SEED)
    out = {"defs": defs, "seed": SEED, "threshold": THRESH, "n_perm": N_PERM, "n_sim": N_SIM,
           "estimator": "perturb_eval.experiments.preregistered.rho (average-rank Spearman; alias _rho)",
           "per_test_null_P(rho>0.5)": {str(n): per_test_null(n, rng) for n in (N_NORMAN, N_ADAMSON, N_POOLED)},
           "gate_fwer_6_tests": {f"components_{arm}": gate_fwer(rng, arm, defs) for arm in arms}}
    p41 = out["per_test_null_P(rho>0.5)"][str(N_POOLED)]
    out["pooled_single_test_n41"] = p41
    hi = max(out["gate_fwer_6_tests"].values())
    out["gate_fwer_max_over_arms"] = hi
    out["ratio_gate_upper_to_pooled"] = (hi / p41) if p41 else None
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
