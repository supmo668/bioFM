"""Norman 2019 real-data loader.

scPerturb repackages Norman's K562 Perturb-seq data (~100k cells, 100+
single and double CRISPRa perturbations) as an h5ad with
``obs.perturbation`` and ``var.gene_symbol``. Double knockdowns use the
``GENE_A+GENE_B`` delimiter.

The return shape matches :func:`perturb_eval.experiments.e2_adamson.load_adamson_matrix`
so every existing backbone/optimizer works unchanged.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

import numpy as np


_CONTROL_TOKENS = {"non-targeting", "nontargeting", "ctrl", "control", "NT"}


def _is_control_label(raw: str) -> bool:
    lower = raw.lower()
    return lower in {t.lower() for t in _CONTROL_TOKENS} or lower == "ntc"


def _parse_pert_label(raw: str) -> str:
    """Norman: singletons come as ``JUN``, doublets as ``JUN+FOS``.

    The loader preserves the full string for doublets (so the paper can
    report on epistasis) and returns the bare gene name for singletons.
    """
    return raw.strip()


def load_norman_matrix(
    h5ad_path: Union[Path, str],
    *,
    n_top_hvg: int = 2000,
    max_cells_per_pert: int = 400,
) -> dict:
    """Load Norman, log1p-normalise, HVG-filter, downsample.

    Returns the canonical dict keyed by
    ``{X, labels, control_mask, target_gene_idx, perturbations, gene_names}``.
    Double knockdowns live in ``labels`` as ``A+B`` but have no single
    ``target_gene_idx`` entry (there are two targets); they can still be
    used as held-out tasks by iterating over both gene indices upstream.
    """
    import anndata as ad

    adata = ad.read_h5ad(str(h5ad_path))

    # obs.perturbation is the harmonised scPerturb column.
    if "perturbation" not in adata.obs.columns:
        raise ValueError(
            f"expected 'perturbation' in obs.columns; got {list(adata.obs.columns)}"
        )

    labels_raw = adata.obs["perturbation"].astype(str).to_numpy()

    # Gene symbols.
    if "gene_symbol" in adata.var.columns:
        gene_names = np.asarray(adata.var["gene_symbol"].astype(str).to_numpy())
    else:
        gene_names = np.asarray(adata.var_names.astype(str).to_numpy())

    # Norman is ~100k cells × ~33k genes; the dense float32 matrix is
    # ~13 GB which OOMs typical 32 GB containers once HVG variance +
    # log1p scratch space stack up. We downsample rows on the SPARSE
    # matrix first, then dense-cast only the survivors.
    from scipy.sparse import issparse

    rng = np.random.default_rng(2026)
    keep_mask = np.zeros(adata.n_obs, dtype=bool)
    for p in np.unique(labels_raw):
        idx = np.where(labels_raw == p)[0]
        if len(idx) > max_cells_per_pert:
            idx = rng.choice(idx, size=max_cells_per_pert, replace=False)
        keep_mask[idx] = True

    sub = adata[keep_mask]
    labels_raw = labels_raw[keep_mask]

    raw_X = sub.X
    dense = (raw_X.toarray() if issparse(raw_X) else np.asarray(raw_X)).astype(np.float32)
    # Free original adata before log1p allocates scratch space.
    del adata, sub, raw_X
    dense = np.log1p(dense)

    # HVG cut on the already-downsampled matrix.
    n_top = min(n_top_hvg, dense.shape[1])
    gene_var = dense.var(axis=0)
    top_gene_idx = np.argsort(-gene_var)[:n_top]
    dense = dense[:, top_gene_idx]
    gene_names = gene_names[top_gene_idx]

    # Normalise + controls.
    control_mask = np.asarray([_is_control_label(r) for r in labels_raw])
    labels_norm = np.asarray([_parse_pert_label(r) for r in labels_raw])
    gene_to_idx = {str(g): i for i, g in enumerate(gene_names)}

    target_gene_idx: dict[str, int] = {}
    perturbations: list[str] = []
    for raw_label, norm_label in zip(labels_raw, labels_norm):
        if _is_control_label(raw_label) or norm_label in target_gene_idx:
            continue
        # Doublets: record the label but don't try to pick a single gene index.
        if "+" in norm_label:
            if norm_label not in perturbations:
                perturbations.append(norm_label)
            continue
        # Singleton: find the target gene in the HVG vocab.
        if norm_label in gene_to_idx:
            target_gene_idx[norm_label] = gene_to_idx[norm_label]
            perturbations.append(norm_label)
        else:
            # Target dropped by HVG filter — pick a deterministic fallback.
            target_gene_idx[norm_label] = int(rng.integers(0, len(gene_names)))
            perturbations.append(norm_label)

    labels_final = np.where(control_mask, "CTRL", labels_norm).astype("U64")

    return {
        "X": dense.astype(np.float64),
        "labels": labels_final,
        "control_mask": control_mask,
        "target_gene_idx": target_gene_idx,
        "perturbations": tuple(perturbations),
        "gene_names": tuple(str(g) for g in gene_names),
    }
