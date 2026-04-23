"""Apply DataCurator agent's QC recipe to the AnnData matrix.

Previously HVG was hardcoded in the grid; here the DataCurator proposal
drives the number of HVG kept and the mito-% threshold is logged for
reporting. The filter materialises so downstream Trainer/Validator see
exactly what the agent chose.
"""

from __future__ import annotations

import numpy as np


def execute_data_curator(
    *,
    X: np.ndarray,
    labels: np.ndarray,
    proposal: dict,
) -> dict:
    """Apply Seurat-style top-N HVG selection. Returns filtered X + meta."""
    n_top_hvg = int(proposal.get("n_top_hvg", 500))
    pct_mito_max = float(proposal.get("pct_mito_max", 15.0))

    if X.shape[1] <= n_top_hvg:
        X_out = X
        top_idx = np.arange(X.shape[1])
    else:
        gene_var = X.var(axis=0)
        top_idx = np.argsort(-gene_var)[:n_top_hvg]
        X_out = X[:, top_idx]

    return {
        "X": X_out,
        "labels": labels,
        "top_gene_indices": top_idx,
        "execution_meta": {
            "applied_hvg": int(X_out.shape[1]),
            "pct_mito_max": pct_mito_max,
        },
    }
