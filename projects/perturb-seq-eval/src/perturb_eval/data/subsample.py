"""Deterministic stratified subsampler.

Given a flat array of candidate labels and a parallel array of strata,
return a sorted subset with at most ``n_per_stratum`` entries per stratum,
chosen reproducibly from ``seed``.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def mean_abs_logfc_per_target(
    X: NDArray,
    labels: NDArray,
    control_mask: NDArray,
    target_gene_idx: dict[str, int],
) -> dict[str, float]:
    """Compute mean |logFC| of each target's own gene across cells.

    Uses the per-perturbation mean minus the control mean on the target
    gene's column. Log-space is already applied in the loaders, so this
    is a mean |Δlog1p| — a faithful perturbation-strength stratifier.
    """
    ctrl_mean = X[control_mask].mean(axis=0)
    out: dict[str, float] = {}
    for pert, idx in target_gene_idx.items():
        mask_p = labels == pert
        if not mask_p.any():
            continue
        pert_mean = X[mask_p].mean(axis=0)
        out[pert] = float(abs(pert_mean[idx] - ctrl_mean[idx]))
    return out


def stratified_subsample(
    labels: NDArray,
    strata: NDArray,
    *,
    n_per_stratum: int,
    seed: int,
) -> NDArray:
    """Return a sorted array of labels stratified by ``strata``.

    Parameters
    ----------
    labels
        1-D array of candidate identifiers (strings or objects).
    strata
        1-D array parallel to ``labels`` assigning each candidate to a
        stratum (any hashable value).
    n_per_stratum
        Maximum number of candidates drawn per stratum. If a stratum has
        fewer members, all are kept.
    seed
        RNG seed — same seed yields the same output across calls.

    Returns
    -------
    NDArray
        Sorted subset of ``labels``.

    Raises
    ------
    ValueError
        If ``labels`` and ``strata`` have different shapes.
    """
    labels = np.asarray(labels)
    strata = np.asarray(strata)
    if labels.shape != strata.shape:
        raise ValueError(
            f"labels shape {labels.shape} != strata shape {strata.shape}"
        )
    if n_per_stratum <= 0:
        raise ValueError(f"n_per_stratum must be positive, got {n_per_stratum}")

    rng = np.random.default_rng(seed)
    keep: list = []
    for s in np.unique(strata):
        idx = np.where(strata == s)[0]
        if len(idx) <= n_per_stratum:
            keep.extend(labels[idx].tolist())
            continue
        choice = rng.choice(idx, size=n_per_stratum, replace=False)
        keep.extend(labels[choice].tolist())

    out = np.array(sorted(keep), dtype=labels.dtype)
    return out
