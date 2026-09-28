"""Apply DataCurator agent's QC recipe to the AnnData matrix.

Previously HVG was hardcoded in the grid; here the DataCurator proposal
drives the number of HVG kept. The HVG filter materialises so downstream
Trainer/Validator see exactly what the agent chose.

The mito-% threshold (``qc_mito_max``) is ONLY LOGGED (``execution_meta``):
the lifecycle dataset carries no per-cell mito fraction and no cell filter is
implemented here. QG-2 / A2-3: the loop records it per round with
``applied=False`` and a reason (``architect_dispatch.NOT_APPLIED_FIELDS``);
whether to implement the filter is an open ruling.

T8b (CTO #227): HVG is ranked on TRAINING cells only, through the single
helper :func:`perturb_eval.data.hvg.select_hvg_train_only`; the caller must
pass ``train_mask`` explicitly.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from perturb_eval.data import hvg as _hvg


def execute_data_curator(
    *,
    X: np.ndarray,
    labels: np.ndarray,
    proposal: dict,
    train_mask: np.ndarray,
    force_include: Iterable[int] = (),
) -> dict:
    """Top-N HVG ranked on ``X[train_mask]`` only, union ``force_include``.

    ``X``/``labels`` are ALL cells; the returned ``X``/``labels`` are the
    training rows restricted to the selected columns. ``top_gene_indices``
    are sorted column indices into ``X``.

    ``qc_mito_max`` / ``pct_mito_max`` is read and echoed in
    ``execution_meta["pct_mito_max"]`` but NO cell is filtered by it (QG-2).
    """
    # A2-3: the schema keys (``hvg_count`` / ``qc_mito_max``) are read first;
    # ``n_top_hvg`` / ``pct_mito_max`` are the legacy keys of the non-LLM pools.
    n_top_hvg = int(proposal.get("hvg_count", proposal.get("n_top_hvg", 500)))
    pct_mito_max = float(proposal.get("qc_mito_max", proposal.get("pct_mito_max", 15.0)))

    sel = _hvg.select_hvg_train_only(X, train_mask, n_top_hvg, force_include=force_include)
    rows = np.flatnonzero(np.asarray(train_mask, dtype=bool))
    # float64: real-data loaders return a float32 full-vocabulary matrix.
    X_out = np.asarray(X[np.ix_(rows, sel.indices)], dtype=np.float64)

    return {
        "X": X_out,
        "labels": labels[rows],
        "top_gene_indices": sel.indices,
        "hvg_selection": sel,
        "execution_meta": {
            "applied_hvg": int(X_out.shape[1]),
            "pct_mito_max": pct_mito_max,
            "hvg_n": sel.n_hvg,
            "hvg_n_forced": int(sel.n_forced),
            "hvg_mode": sel.mode,
        },
    }
