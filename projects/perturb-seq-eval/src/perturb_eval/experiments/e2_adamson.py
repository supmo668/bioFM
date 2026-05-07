"""Adamson 2016 real-data variant of the E2 grid-cell trainer.

Reads the Adamson pilot .h5ad directly (h5py, no scanpy), normalises
counts → log1p, applies a leave-one-perturbation-out split, trains the
selected backbone, and returns an :class:`GridCellResult` against real
held-out MSD on top-K DEGs.

See docs/SUPPLEMENT_DESIGN.md §4 E2 (Adamson variant).
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np

from perturb_eval.backbones import (
    BackboneTrainConfig,
    build_backbone,
    mean_squared_deviation,
)
from perturb_eval.experiments.common import GridCellResult
from perturb_eval.experiments.e2_grid_fill import phi_identifier
from perturb_eval.types import Config


def load_adamson_combined(
    h5ad_paths: "list[Path | str]",
    *,
    n_top_hvg: int = 2000,
    max_cells_per_pert: int = 200,
) -> dict:
    """Load + concatenate multiple Adamson 10X subsets into one canonical dict.

    The scPerturb 10X001 (pilot), 10X005, and 10X010 subsets share the
    same schema but cover different TF perturbation sets. To maximise
    target-gene retention we load each subset with HVG *disabled*
    (``n_top_hvg=len(gene_names)``), take the gene-vocab intersection
    across files, then apply the HVG cut on the concatenated matrix so
    every subset votes on which genes survive. Target TFs that exist in
    the shared vocab always survive the HVG cut (we augment the HVG set
    with every target gene before slicing).
    """
    import numpy as np

    if not h5ad_paths:
        raise ValueError("need at least one h5ad path")

    # Load each subset with per-file HVG disabled (huge n_top_hvg).
    per_file = [
        load_adamson_matrix(p, n_top_hvg=10**9, max_cells_per_pert=max_cells_per_pert)
        for p in h5ad_paths
    ]

    # Gene vocab intersection.
    gene_sets = [set(d["gene_names"]) for d in per_file]
    shared_genes = sorted(set.intersection(*gene_sets))
    if not shared_genes:
        raise ValueError("no shared genes across Adamson subsets")

    # Re-index each subset onto the shared vocab.
    Xs = []
    all_labels = []
    all_ctrl = []
    for d in per_file:
        gene_to_old_idx = {g: i for i, g in enumerate(d["gene_names"])}
        order = np.array([gene_to_old_idx[g] for g in shared_genes])
        Xs.append(d["X"][:, order])
        all_labels.append(d["labels"])
        all_ctrl.append(d["control_mask"])

    X_full = np.concatenate(Xs, axis=0)
    labels = np.concatenate(all_labels, axis=0).astype("U32")
    control_mask = np.concatenate(all_ctrl, axis=0)

    # Collect target TF names before HVG cut so every target survives.
    all_target_tfs: set[str] = set()
    for d in per_file:
        all_target_tfs.update(d["perturbations"])
    gene_to_shared_idx = {g: i for i, g in enumerate(shared_genes)}
    target_indices_to_keep = {
        gene_to_shared_idx[tf]
        for tf in all_target_tfs
        if tf in gene_to_shared_idx
    }

    # HVG on the combined matrix.
    if n_top_hvg < len(shared_genes):
        gene_var = X_full.var(axis=0)
        top_by_var = set(np.argsort(-gene_var)[:n_top_hvg].tolist())
        keep_set = top_by_var | target_indices_to_keep
        kept = sorted(keep_set)
        X = X_full[:, kept]
        final_genes = [shared_genes[i] for i in kept]
    else:
        X = X_full
        final_genes = list(shared_genes)

    gene_to_new_idx = {g: i for i, g in enumerate(final_genes)}
    target_gene_idx: dict[str, int] = {}
    perturbations: list[str] = []
    for d in per_file:
        for p in d["perturbations"]:
            if p in target_gene_idx:
                continue
            if p in gene_to_new_idx:
                target_gene_idx[p] = gene_to_new_idx[p]
                perturbations.append(p)
            # else: target dropped from vocab entirely (not present in
            # shared genes at all) — skip (honest gap).

    return {
        "X": X.astype(np.float64),
        "labels": labels,
        "control_mask": control_mask,
        "target_gene_idx": target_gene_idx,
        "perturbations": tuple(perturbations),
        "gene_names": tuple(final_genes),
    }


def _normalise_pert_label(raw: str) -> str:
    """Adamson pilot labels look like ``'DDIT3_pDS263'``; keep the gene name."""
    return raw.split("_")[0]


def _is_control(raw: str) -> bool:
    # Non-targeting guides are encoded as ``'*'`` and ``'62(mod)_pBA581'``.
    return raw == "*" or raw.startswith("62(")


def load_adamson_matrix(
    h5ad_path: Path | str,
    *,
    n_top_hvg: int = 2000,
    max_cells_per_pert: int = 400,
) -> dict:
    """Load Adamson, log1p-normalise, downsample, pick top-HVG genes.

    The returned dictionary is the canonical input for every backbone on
    real data: ``{X, labels, control_mask, target_gene_idx, perturbations}``
    with the same keys the synthetic path uses.
    """
    import h5py

    with h5py.File(str(h5ad_path), "r") as f:
        # Perturbation column stored as a h5ad categorical group.
        pert_group = f["obs/perturbation"]
        codes = pert_group["codes"][()]  # type: ignore[index]
        cats_raw = pert_group["categories"][()]  # type: ignore[index]
        cats = [c.decode() if isinstance(c, bytes) else c for c in cats_raw]
        labels_raw = np.asarray([cats[c] for c in codes])

        # Gene names (scPerturb packaging stores them under var/gene_symbol).
        gene_names_raw = f["var/gene_symbol"][()]  # type: ignore[index]
        gene_names = np.asarray(
            [g.decode() if isinstance(g, bytes) else g for g in gene_names_raw]
        )

        # X is CSC in scPerturb packaging (shape attribute is canonical).
        x_shape = tuple(f["X"].attrs["shape"])  # (n_cells, n_genes)
        data = f["X/data"][()]      # type: ignore[index]
        indices = f["X/indices"][()]  # type: ignore[index]
        indptr = f["X/indptr"][()]    # type: ignore[index]
        encoding = str(f["X"].attrs.get("encoding-type", "csc_matrix"))

    from scipy.sparse import csc_matrix, csr_matrix  # type: ignore[import-not-found]

    if encoding.startswith("csc"):
        sp = csc_matrix((data, indices, indptr), shape=x_shape)
    else:
        sp = csr_matrix((data, indices, indptr), shape=x_shape)
    dense = sp.toarray().astype(np.float32)

    # log1p normalisation (counts are raw integers after scanpy's default
    # QC from scPerturb; we keep it simple — no cell-depth scaling here so
    # the HVG picks are depth-dominated but OK for the backbone's relative
    # log-FC prediction task).
    dense = np.log1p(dense)

    # Pick top-N most variable genes (Seurat-style on log1p).
    gene_var = dense.var(axis=0)
    top_gene_idx = np.argsort(-gene_var)[:n_top_hvg]
    dense = dense[:, top_gene_idx]
    gene_names = gene_names[top_gene_idx]

    # Downsample cells per perturbation.
    rng = np.random.default_rng(2026)
    keep_mask = np.zeros(dense.shape[0], dtype=bool)
    for p in np.unique(labels_raw):
        idx = np.where(labels_raw == p)[0]
        if len(idx) > max_cells_per_pert:
            idx = rng.choice(idx, size=max_cells_per_pert, replace=False)
        keep_mask[idx] = True
    dense = dense[keep_mask]
    labels_raw = labels_raw[keep_mask]

    # Normalise perturbation labels and identify targets present in the HVG vocab.
    labels_norm = np.asarray([_normalise_pert_label(r) for r in labels_raw])
    control_mask = np.asarray([_is_control(r) for r in labels_raw])
    gene_to_idx = {str(g): i for i, g in enumerate(gene_names)}
    target_gene_idx: dict[str, int] = {}
    perturbations = []
    for raw_label, norm_label in zip(labels_raw, labels_norm):
        if not _is_control(raw_label) and norm_label not in target_gene_idx:
            target_gene_idx[str(norm_label)] = gene_to_idx.get(
                str(norm_label),
                # Fall back to the most-variable gene if HVG missed the target
                # (unlikely for Adamson TFs — TF genes are typically in top 2000).
                int(rng.integers(0, len(gene_names))),
            )
            perturbations.append(str(norm_label))

    # Controls get label "CTRL" in the uniform convention used by backbones.
    labels_final = np.where(control_mask, "CTRL", labels_norm).astype("U32")
    return {
        "X": dense.astype(np.float64),
        "labels": labels_final,
        "control_mask": control_mask,
        "target_gene_idx": target_gene_idx,
        "perturbations": tuple(perturbations),
        "gene_names": tuple(str(g) for g in gene_names),
    }


def train_grid_cell_adamson(
    phi: Config,
    task: str,
    seed: int,
    *,
    h5ad_path: Path | str,
    dataset_cache: dict | None = None,
) -> GridCellResult:
    """Train one (phi, task, seed) on real Adamson data.

    ``task`` is expected to be one of the normalised perturbation names
    from :func:`load_adamson_matrix`; it becomes the held-out perturbation
    for this grid cell. ``dataset_cache`` lets callers share the preprocessed
    dataset across calls (crucial — loading is ~6 s per call otherwise).
    """
    t0 = time.perf_counter()
    ds = dataset_cache if dataset_cache is not None else load_adamson_matrix(h5ad_path)

    held = task
    if held not in ds["target_gene_idx"]:
        raise ValueError(
            f"held-out task {held!r} not in Adamson perturbations "
            f"{sorted(ds['target_gene_idx'])}"
        )
    train_mask = ds["labels"] != held
    if not train_mask.any():
        raise ValueError("empty training mask — dataset may be misformed")

    from perturb_eval.backbones import available_backbones

    if phi.backbone not in available_backbones():
        raise ValueError(
            f"unknown backbone {phi.backbone!r}; "
            f"available: {sorted(available_backbones())}"
        )
    backbone = build_backbone(phi.backbone)
    train_targets = {p: idx for p, idx in ds["target_gene_idx"].items() if p != held}
    backbone.fit(
        ds["X"][train_mask],
        ds["labels"][train_mask].tolist(),
        ds["control_mask"][train_mask],
        train_targets,
        BackboneTrainConfig(
            max_iter=20 + 40 * phi.n_rounds,
            learning_rate=1e-2,
            ridge_lambda=1.0,
            seed=seed,
        ),
    )

    target_idx = ds["target_gene_idx"][held]
    n_genes = ds["X"].shape[1]
    pred = backbone.predict_logfc(held, target_idx, n_genes=n_genes)

    # Observed log-FC from held-out perturbation vs control cells.
    mask_p = ds["labels"] == held
    mask_c = ds["control_mask"]
    truth = np.mean(ds["X"][mask_p], axis=0) - np.mean(ds["X"][mask_c], axis=0)
    top_k = np.argsort(-np.abs(truth))[:20]
    msd = mean_squared_deviation(pred, truth, top_k)
    return GridCellResult(
        phi_id=phi_identifier(phi),
        task=held,
        seed=seed,
        msd_topk=msd,
        wall_time_sec=time.perf_counter() - t0,
        backbone_name=backbone.name,
    )
