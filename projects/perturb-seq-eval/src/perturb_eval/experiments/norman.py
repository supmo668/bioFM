"""Norman 2019 real-data loader.

scPerturb repackages Norman's K562 Perturb-seq data (~100k cells, 100+
single and double CRISPRa perturbations) as an h5ad with
``obs.perturbation`` and ``var.gene_symbol``. Double knockdowns are
``_``-joined (``GENE_A_GENE_B``, e.g. ``CBL_UBASH3A``); singletons are bare
symbols. Targets resolve via :func:`perturb_eval.data.label_contract.resolve_with_contract`
(D1: singletons -> 1-tuple, doublets -> 2-tuple); a target gene missing from
the gene vocabulary raises ``ValueError`` — no substitute is ever chosen.

The loader keeps the FULL gene vocabulary (T8b, CTO #227): HVG is selected
per held-out task on training cells only (:mod:`perturb_eval.experiments.heldout`).

The return shape matches :func:`perturb_eval.experiments.e2_adamson.load_adamson_matrix`
so every existing backbone/optimizer works unchanged.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

import numpy as np

from perturb_eval.data.label_contract import (
    NORMAN_CONTRACT,
    LabelContract,
    resolve_with_contract,
)
from perturb_eval.data.perturbations import is_doublet


_CONTROL_TOKENS = {"non-targeting", "nontargeting", "ctrl", "control", "NT"}


def _is_control_label(raw: str) -> bool:
    lower = raw.lower()
    return lower in {t.lower() for t in _CONTROL_TOKENS} or lower == "ntc"


def _parse_pert_label(raw: str) -> str:
    """Norman: singletons come as ``JUN``, doublets as ``JUN_FOS``.

    The loader preserves the full string for doublets (so the paper can
    report on epistasis) and returns the bare gene name for singletons.
    """
    return raw.strip()


def load_norman_matrix(
    h5ad_path: Union[Path, str],
    *,
    n_top_hvg: int = 2000,
    max_cells_per_pert: int = 400,
    doublet_delim: str = "_",
    contract: LabelContract = NORMAN_CONTRACT,
) -> dict:
    """Load Norman, downsample, log1p-normalise. Keeps the FULL gene vocabulary.

    Returns the canonical dict keyed by
    ``{X, labels, control_mask, target_gene_idx, perturbations, gene_names}``.
    ``target_gene_idx`` maps every non-control perturbation to a tuple of
    target column indices (D1): singletons -> ``(i,)``, doublets (labels
    joined by ``doublet_delim``, e.g. ``A_B``) -> ``(i_A, i_B)``. Raises
    ``ValueError`` listing every ``(label, gene)`` whose gene is absent from
    the gene vocabulary; there is no random-gene fallback.

    ``X`` is the raw log1p matrix over all genes (float32). **No HVG cut**
    happens here: ranking over all cells would include every held-out
    perturbation's cells. ``n_top_hvg`` is recorded as ``ds["hvg_n_top"]``
    and applied per held-out task on training cells only.

    ``contract`` (CTO #250/#251): structural controls (whole label) join
    ``control_mask``; excluded labels (whole label) lose their cells and are
    listed in ``ds["labels_excluded"]``; aliases apply PER TUPLE COMPONENT
    (``A_B`` -> ``apply(A)``, ``apply(B)``) while the task label stays the
    original string. ``ds["label_contract"]`` is ``contract.to_provenance()``.
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
    # ~13 GB which OOMs typical 32 GB containers once log1p scratch space
    # stacks up. We downsample rows on the SPARSE matrix first, then
    # dense-cast only the survivors, and log1p in place.
    from scipy.sparse import issparse

    rng = np.random.default_rng(2026)
    keep_mask = np.zeros(adata.n_obs, dtype=bool)
    labels_excluded: list[dict[str, str]] = []
    for p in np.unique(labels_raw):
        norm = _parse_pert_label(str(p))
        if not _is_control_label(str(p)) and contract.is_excluded(norm):
            entry = {"label": norm, "reason": contract.excluded[norm]}
            if entry not in labels_excluded:
                labels_excluded.append(entry)
            continue
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
    np.log1p(dense, out=dense)

    # Normalise + controls.
    labels_norm = np.asarray([_parse_pert_label(r) for r in labels_raw])
    control_mask = np.asarray(
        [_is_control_label(r) or contract.is_control(n) for r, n in zip(labels_raw, labels_norm)],
        dtype=bool,
    )
    gene_to_idx = {str(g): i for i, g in enumerate(gene_names)}

    # Unique non-control labels in first-appearance order.
    perturbations: list[str] = []
    seen: set[str] = set()
    for is_ctrl, norm_label in zip(control_mask, labels_norm):
        if is_ctrl or norm_label in seen:
            continue
        seen.add(norm_label)
        perturbations.append(str(norm_label))
    for p in perturbations:
        is_doublet(p, doublet_delim)  # raises on empty parts / >2 genes

    # D1: tuples of target columns, aliased per component; raises on any
    # target (after the contract) outside the vocab.
    target_gene_idx = resolve_with_contract(
        perturbations, gene_to_idx, contract, delim=doublet_delim
    )
    unresolved = [p for p in perturbations if p not in target_gene_idx]
    if unresolved:
        # resolve_target_indices skips labels its (broader) control rule
        # matches; the Norman loader did not classify these as controls.
        raise ValueError(
            f"Norman perturbation label(s) {unresolved!r} are not controls under the "
            "Norman convention but were not resolved to target genes"
        )

    labels_final = np.where(control_mask, "CTRL", labels_norm).astype("U64")

    return {
        # float32 over the full vocabulary; per-task views are cast to float64.
        "X": dense,
        "labels": labels_final,
        "control_mask": control_mask,
        "target_gene_idx": target_gene_idx,
        "perturbations": tuple(perturbations),
        "gene_names": tuple(str(g) for g in gene_names),
        "hvg_n_top": int(n_top_hvg),
        "labels_excluded": labels_excluded,
        "label_contract": contract.to_provenance(),
    }
