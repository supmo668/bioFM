"""Deterministic stratified subsampler.

Given a flat array of candidate labels and a parallel array of strata,
return a sorted subset with at most ``n_per_stratum`` entries per stratum,
chosen reproducibly from ``seed``.
"""

from __future__ import annotations

import zlib
from collections.abc import Mapping, Sequence

import numpy as np
from numpy.typing import NDArray


def deterministic_stratum(label: str, k: int) -> int:
    """Map ``label`` to a stratum in ``[0, k)`` independent of process state.

    Uses CRC32 of the UTF-8 bytes rather than the built-in string hash,
    which is salted per interpreter (``PYTHONHASHSEED``) and therefore
    not reproducible across runs.

    Raises
    ------
    ValueError
        If ``k < 1``.
    """
    if k < 1:
        raise ValueError(f"k must be >= 1, got {k}")
    return zlib.crc32(label.encode("utf-8")) % k


def mean_abs_logfc_per_target(
    X: NDArray,
    labels: NDArray,
    control_mask: NDArray,
    target_gene_idx: Mapping[str, int | Sequence[int]],
) -> dict[str, float]:
    """Compute mean |logFC| of each target's own gene(s) across cells.

    Uses the per-perturbation mean minus the control mean on the target
    gene's column. Log-space is already applied in the loaders, so this
    is a mean |Δlog1p| — a faithful perturbation-strength stratifier.

    A target may be an ``int`` column or a tuple of columns (D1
    multi-target: a doublet is a 2-tuple). For a tuple the score is the
    arithmetic mean over its columns of ``|pert_mean[c] - ctrl_mean[c]|``;
    a 1-tuple ``(i,)`` yields exactly the same float as the int ``i``.
    """
    # float64 accumulation: loaders now return float32 full-vocabulary X.
    ctrl_mean = X[control_mask].mean(axis=0, dtype=np.float64)
    out: dict[str, float] = {}
    for pert, idx in target_gene_idx.items():
        mask_p = labels == pert
        if not mask_p.any():
            continue
        pert_mean = X[mask_p].mean(axis=0, dtype=np.float64)
        cols = (idx,) if isinstance(idx, (int, np.integer)) else tuple(idx)
        if not cols:
            raise ValueError(f"target {pert!r} has an empty tuple of target columns")
        diffs = [float(abs(pert_mean[c] - ctrl_mean[c])) for c in cols]
        out[pert] = sum(diffs) / len(diffs)
    return out


def stratified_subsample(
    labels: NDArray,
    strata: NDArray,
    *,
    n_per_stratum: int,
    seed: int,
    n_total: int | None = None,
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
    n_total
        Optional exact total (T11). After the per-stratum draw, the result
        is topped up deterministically (seeded permutation of the sorted
        remaining labels) or trimmed (sorted prefix) to exactly
        ``min(n_total, len(labels))``. ``None`` keeps the legacy
        per-stratum-only behaviour, whose output it leaves unchanged.

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

    if n_total is not None:
        if n_total < 0:
            raise ValueError(f"n_total must be non-negative, got {n_total}")
        target = min(n_total, len(labels))
        keep = sorted(keep)
        if len(keep) > target:
            keep = keep[:target]
        elif len(keep) < target:
            chosen = set(keep)
            remaining = sorted(x for x in labels.tolist() if x not in chosen)
            order = rng.permutation(len(remaining))
            keep.extend(remaining[i] for i in order[: target - len(keep)])

    out = np.array(sorted(keep), dtype=labels.dtype)
    return out
