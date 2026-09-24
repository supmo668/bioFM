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

from perturb_eval.backbones import BackboneTrainConfig
from perturb_eval.data.perturbations import resolve_target_indices
from perturb_eval.experiments.common import GridCellResult
from perturb_eval.experiments.e2_grid_fill import phi_identifier
from perturb_eval.experiments.heldout import build_view, fit_and_score, hvg_fields, select_for_task
from perturb_eval.types import Config


def load_adamson_combined(
    h5ad_paths: "list[Path | str]",
    *,
    n_top_hvg: int = 2000,
    max_cells_per_pert: int = 200,
) -> dict:
    """Load + concatenate multiple Adamson 10X subsets into one canonical dict.

    The scPerturb 10X001 (pilot), 10X005, and 10X010 subsets share the
    same schema but cover different TF perturbation sets. Each subset is
    loaded over its full gene vocabulary, re-indexed onto the vocabulary
    intersection, and concatenated. **No HVG cut happens here** (T8b, CTO
    #227): ranking genes over the concatenated matrix would let every
    held-out perturbation's cells vote on the features. ``n_top_hvg`` is
    recorded as ``ds["hvg_n_top"]`` and applied per held-out task on
    training cells only (:mod:`perturb_eval.experiments.heldout`).

    Targets resolve via :func:`resolve_target_indices` against the shared
    vocabulary (D1 tuples); a target gene absent from it raises
    ``ValueError`` — it is never silently skipped.
    """
    if not h5ad_paths:
        raise ValueError("need at least one h5ad path")

    per_file = [
        load_adamson_matrix(p, n_top_hvg=n_top_hvg, max_cells_per_pert=max_cells_per_pert)
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

    X = np.concatenate(Xs, axis=0)
    del Xs
    labels = np.concatenate(all_labels, axis=0).astype("U32")
    control_mask = np.concatenate(all_ctrl, axis=0)

    # Union of perturbations, first-appearance order across files.
    perturbations: list[str] = []
    for d in per_file:
        for pert in d["perturbations"]:
            if pert not in perturbations:
                perturbations.append(pert)
    gene_to_idx = {g: i for i, g in enumerate(shared_genes)}
    # Raises (listing every (label, gene)) on a target outside the shared vocab.
    target_gene_idx = resolve_target_indices(perturbations, gene_to_idx)
    unresolved = [pert for pert in perturbations if pert not in target_gene_idx]
    if unresolved:
        raise ValueError(
            f"Adamson perturbation label(s) {unresolved!r} are not controls under the "
            "Adamson convention but were not resolved to target genes"
        )

    return {
        "X": X,
        "labels": labels,
        "control_mask": control_mask,
        "target_gene_idx": target_gene_idx,
        "perturbations": tuple(perturbations),
        "gene_names": tuple(shared_genes),
        "hvg_n_top": int(n_top_hvg),
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
    """Load Adamson, log1p-normalise, downsample. Keeps the FULL gene vocabulary.

    The returned dictionary is the canonical input for every backbone on
    real data: ``{X, labels, control_mask, target_gene_idx, perturbations,
    gene_names, hvg_n_top}``. ``X`` is the raw log1p matrix (float32, all
    genes). **No HVG cut happens here** (T8b, CTO #227): ranking genes over
    all cells would include every held-out perturbation's cells. HVG is
    selected per held-out task on training cells only; ``n_top_hvg`` is
    only recorded as ``ds["hvg_n_top"]`` for that step.
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
    # log-FC prediction task). In place: no second full-size scratch copy.
    np.log1p(dense, out=dense)

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

    # Normalise perturbation labels and resolve targets against the full vocab.
    labels_norm = np.asarray([_normalise_pert_label(r) for r in labels_raw])
    control_mask = np.asarray([_is_control(r) for r in labels_raw])
    gene_to_idx = {str(g): i for i, g in enumerate(gene_names)}
    # Resolve on the NORMALISED gene-level labels: raw guide labels
    # ("DDIT3_pDS263") carry a '_'-joined plasmid suffix that '_'-parsing
    # would misread as a doublet. A target outside the vocab raises (A4) —
    # no random-gene substitute.
    perturbations: list[str] = []
    seen: set[str] = set()
    for raw_label, norm_label in zip(labels_raw, labels_norm):
        if _is_control(raw_label) or norm_label in seen:
            continue
        seen.add(str(norm_label))
        perturbations.append(str(norm_label))
    target_gene_idx = resolve_target_indices(perturbations, gene_to_idx)
    unresolved = [p for p in perturbations if p not in target_gene_idx]
    if unresolved:
        raise ValueError(
            f"Adamson perturbation label(s) {unresolved!r} are not controls under the "
            "Adamson convention but were not resolved to target genes"
        )

    # Controls get label "CTRL" in the uniform convention used by backbones.
    labels_final = np.where(control_mask, "CTRL", labels_norm).astype("U32")
    return {
        # float32: the full vocabulary is ~16x wider than the old 2 000-gene
        # cut; per-task views are cast to float64 (same values as before).
        "X": dense,
        "labels": labels_final,
        "control_mask": control_mask,
        "target_gene_idx": target_gene_idx,
        "perturbations": tuple(perturbations),
        "gene_names": tuple(str(g) for g in gene_names),
        "hvg_n_top": int(n_top_hvg),
    }


def train_grid_cell_adamson(
    phi: Config,
    task: str,
    seed: int,
    *,
    h5ad_path: Path | str,
    dataset_cache: dict | None = None,
    n_hvg: int | None = None,
) -> GridCellResult:
    """Train one (phi, task, seed) on real Adamson data.

    ``task`` is expected to be one of the normalised perturbation names
    from :func:`load_adamson_matrix`; it becomes the held-out perturbation
    for this grid cell. ``dataset_cache`` lets callers share the loaded raw
    dataset across calls (crucial — loading is ~6 s per call otherwise); it
    holds the full-vocabulary matrix only, never a feature selection.

    HVG (``n_hvg``, default ``ds["hvg_n_top"]``) is selected for THIS
    held-out task on training cells only (T8b); the result records
    ``hvg_n``, ``hvg_n_forced``, ``hvg_mode`` and the fitted ``n_params``.
    """
    t0 = time.perf_counter()
    ds = dataset_cache if dataset_cache is not None else load_adamson_matrix(h5ad_path)

    held = task
    sel = select_for_task(ds, held, n_hvg=n_hvg)
    view = build_view(ds, held, sel)
    out = fit_and_score(
        view,
        phi.backbone,
        BackboneTrainConfig(
            max_iter=20 + 40 * phi.n_rounds,
            learning_rate=1e-2,
            ridge_lambda=1.0,
            seed=seed,
        ),
    )
    return GridCellResult(
        phi_id=phi_identifier(phi),
        task=held,
        seed=seed,
        msd_topk=out["msd_topk"],
        wall_time_sec=time.perf_counter() - t0,
        backbone_name=out["backbone"],
        **hvg_fields(sel),
        n_params=out["n_params"],
    )
