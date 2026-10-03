"""Highly-variable-gene selection on TRAINING cells only (T8b, CTO #227).

Ranking genes by variance over every cell — held-out perturbation included —
lets the held-out cells choose the model's input features (a leak). This is the
one function every training path (Adamson grid cell, the v0.5 trainer sweep
for Adamson + Norman, the agentic lifecycle) calls, once per held-out task.

Consequence (CTO condition 4): the feature space differs per held-out task, so
a cross-task median is a median over models with differing inputs.

``force_include`` is for target-gene columns: a target's identity comes from
the perturbation *label*, not from held-out expression, so forcing it in is not
a leak.

Amendment 2, A2-5: the 20 evaluation genes (convention 2) are ranked ONCE per
task on the dataset's full post-QC gene axis (:func:`top_deg_columns`), shared
by the trainer and lifecycle paths, and force-included like the targets. That
widens feature availability, not label exposure: the ranking already used the
held-out cells under the declared CPA/GEARS convention.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np

HVG_MODE = "train_only"

# Column block for the variance pass: bounds the float64 scratch copy to
# (n_train_cells x _CHUNK) instead of copying the whole training matrix.
_CHUNK = 2048

# Convention 2: MSD is scored on the top-20 DEGs.
N_EVAL_DEGS = 20


@dataclass(frozen=True)
class HVGSelection:
    """Result of :func:`select_hvg_train_only`.

    ``indices`` are sorted, unique column indices into the full gene vocabulary.
    ``n_by_variance`` columns come from the variance ranking; ``n_forced`` are
    the ``force_include`` columns that the ranking did not already pick, so
    ``len(indices) == n_by_variance + n_forced``.
    """

    indices: np.ndarray
    n_by_variance: int
    n_forced: int
    gene_var: np.ndarray
    mode: str = HVG_MODE

    @property
    def n_hvg(self) -> int:
        return len(self.indices)


def train_gene_variance(X: np.ndarray, train_mask: np.ndarray) -> np.ndarray:
    """Per-gene variance over the rows ``train_mask`` selects, in float64."""
    mask = np.asarray(train_mask, dtype=bool)
    if mask.shape != (X.shape[0],):
        raise ValueError(f"train_mask shape {mask.shape} != ({X.shape[0]},)")
    if not mask.any():
        raise ValueError("train_mask selects no cells")
    out = np.empty(X.shape[1], dtype=np.float64)
    for a in range(0, X.shape[1], _CHUNK):
        b = min(a + _CHUNK, X.shape[1])
        out[a:b] = np.asarray(X[mask, a:b], dtype=np.float64).var(axis=0)
    return out


def select_hvg_train_only(
    X: np.ndarray,
    train_mask: np.ndarray,
    n: int,
    *,
    force_include: Iterable[int] = (),
) -> HVGSelection:
    """Top-``n`` genes by variance over ``X[train_mask]`` only, union ``force_include``.

    Ties break stably (lower column index first). Held-out rows never enter the
    variance, so the selection cannot depend on held-out expression.
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    gene_var = train_gene_variance(X, train_mask)
    n_var = min(int(n), X.shape[1])
    top = np.argsort(-gene_var, kind="stable")[:n_var]
    forced = {int(i) for i in force_include}
    bad = [i for i in forced if not 0 <= i < X.shape[1]]
    if bad:
        raise ValueError(f"force_include indices out of range [0, {X.shape[1]}): {sorted(bad)}")
    top_set = {int(i) for i in top}
    added = forced - top_set
    indices = np.asarray(sorted(top_set | added), dtype=np.int64)
    return HVGSelection(
        indices=indices, n_by_variance=n_var, n_forced=len(added), gene_var=gene_var
    )


def _column_mean(X: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Per-gene float64 mean over the rows ``mask`` selects, in column blocks."""
    out = np.empty(X.shape[1], dtype=np.float64)
    for a in range(0, X.shape[1], _CHUNK):
        b = min(a + _CHUNK, X.shape[1])
        out[a:b] = np.asarray(X[mask, a:b], dtype=np.float64).mean(axis=0)
    return out


def top_deg_columns(
    X: np.ndarray,
    labels: np.ndarray,
    control_mask: np.ndarray,
    held: str,
    k: int = N_EVAL_DEGS,
) -> np.ndarray:
    """The ``k`` evaluation genes for ``held`` on the FULL gene axis of ``X`` (A2-5).

    Ranking is convention 2: largest ``|mean(X[held cells]) - mean(X[controls])|``,
    ties broken stably (lower column index first). Returns full-axis column
    indices in rank order. The one selector both paths call, once per task.
    """
    labels = np.asarray(labels)
    held_mask = labels == held
    ctrl = np.asarray(control_mask, dtype=bool)
    if not held_mask.any():
        raise ValueError(f"held-out perturbation {held!r} has no cells")
    if not ctrl.any():
        raise ValueError("control_mask selects no cells")
    truth = _column_mean(X, held_mask) - _column_mean(X, ctrl)
    return np.argsort(-np.abs(truth), kind="stable")[: int(k)].astype(np.int64)


def remap_targets(
    target_gene_idx: dict[str, int | tuple[int, ...]], indices: np.ndarray
) -> dict[str, tuple[int, ...]]:
    """Re-express every target (as a tuple) in the selected column space.

    Raises ``ValueError`` if any target column is not in ``indices`` — callers
    force targets in, so this only fires on a caller bug. No fallback (A4).
    """
    old_to_new = {int(old): new for new, old in enumerate(np.asarray(indices).tolist())}
    out: dict[str, tuple[int, ...]] = {}
    missing: list[tuple[str, int]] = []
    for p, t in target_gene_idx.items():
        cols = _as_cols(t)
        miss = [(p, c) for c in cols if c not in old_to_new]
        if miss:
            missing.extend(miss)
            continue
        out[p] = tuple(old_to_new[c] for c in cols)
    if missing:
        raise ValueError(f"target column(s) not in the HVG selection: {missing}")
    return out


def all_target_columns(target_gene_idx: dict[str, int | tuple[int, ...]]) -> list[int]:
    """Every target column of every perturbation (training + held-out)."""
    cols: set[int] = set()
    for t in target_gene_idx.values():
        cols.update(_as_cols(t))
    return sorted(cols)


def _as_cols(t: int | tuple[int, ...]) -> tuple[int, ...]:
    return tuple(int(i) for i in t) if isinstance(t, (tuple, list)) else (int(t),)
