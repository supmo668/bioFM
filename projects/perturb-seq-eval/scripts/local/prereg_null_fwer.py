"""Null false-positive rates of the pre-registered H4 gate, computed THROUGH THE ESTIMATOR'S OWN CODE PATH.

CTO #269: the magnitude must come from permutation against the actual estimator (preregistered._rho: average-rank
Spearman), not from a normal approximation. Reproducible: fixed seed, no data needed.

1. Per-test null  P(rho_hat > 0.5)  at n = 20, 21, 41 — permutation of y against a fixed, tie-free x.
2. Gate FWER — Monte Carlo of the WHOLE pre-registered gate: two datasets (n=21 Adamson, n=20 Norman), per dataset the
   three quantities {ACE_norm, 1-dC, TDI_lifecycle = preregistered.tdi_lifecycle(ACE, 1-dC)} against a null MSD; the gate
   fires if ANY of the six rho_hat exceeds 0.5. The dependence between ACE and 1-dC is unknown, so both extremes are run:
   independent (upper) and identical ranks (lower); the true rate lies between them.
3. The pooled comparator: one quantity, one Spearman over n = 41.

    .venv/bin/python scripts/local/prereg_null_fwer.py
"""
from __future__ import annotations

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


def one_dataset_fires(n: int, rng: np.random.Generator, dependence: str) -> bool:
    msd = rng.random(n)
    ace = rng.random(n)
    omdc = ace.copy() if dependence == "identical" else rng.random(n)
    tdi = np.array([tdi_lifecycle(a, b) for a, b in zip(ace, omdc)])
    return any((rho(q, msd) or -2.0) > THRESH for q in (ace, omdc, tdi))


def gate_fwer(rng: np.random.Generator, dependence: str) -> float:
    fires = 0
    for _ in range(N_SIM):
        a = one_dataset_fires(N_ADAMSON, rng, dependence)
        b = one_dataset_fires(N_NORMAN, rng, dependence)
        fires += a or b
    return fires / N_SIM


def main() -> None:
    rng = np.random.default_rng(SEED)
    out = {"seed": SEED, "threshold": THRESH, "n_perm": N_PERM, "n_sim": N_SIM,
           "estimator": "perturb_eval.experiments.preregistered.rho (average-rank Spearman; alias _rho)",
           "per_test_null_P(rho>0.5)": {str(n): per_test_null(n, rng) for n in (N_NORMAN, N_ADAMSON, N_POOLED)},
           "gate_fwer_6_tests": {"components_independent": gate_fwer(rng, "independent"),
                                 "components_identical_ranks": gate_fwer(rng, "identical")}}
    p41 = out["per_test_null_P(rho>0.5)"][str(N_POOLED)]
    out["pooled_single_test_n41"] = p41
    hi = out["gate_fwer_6_tests"]["components_independent"]
    out["ratio_gate_upper_to_pooled"] = (hi / p41) if p41 else None
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
