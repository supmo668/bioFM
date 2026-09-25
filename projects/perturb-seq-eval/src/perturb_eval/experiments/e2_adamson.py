"""Adamson 2016 real-data variant of the E2 grid-cell trainer.

Reads the Adamson pilot .h5ad directly (h5py, no scanpy), normalises
counts → log1p, applies a leave-one-perturbation-out split, trains the
selected backbone, and returns an :class:`GridCellResult` against real
held-out MSD on top-K DEGs.

See docs/SUPPLEMENT_DESIGN.md §4 E2 (Adamson variant).
"""

from __future__ import annotations

import re
import time
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np

from perturb_eval.backbones import BackboneTrainConfig
from perturb_eval.data.label_contract import (
    ADAMSON_CONTRACT,
    LabelContract,
    is_adamson_control,
    resolve_with_contract,
    strip_adamson_plasmid,
)
from perturb_eval.experiments.common import GridCellResult
from perturb_eval.experiments.e2_grid_fill import phi_identifier
from perturb_eval.experiments.heldout import build_view, fit_and_score, hvg_fields, select_for_task
from perturb_eval.types import Config


def load_adamson_combined(
    h5ad_paths: "list[Path | str]",
    *,
    n_top_hvg: int = 2000,
    max_cells_per_pert: int = 200,
    contract: LabelContract = ADAMSON_CONTRACT,
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

    Targets resolve via :func:`resolve_with_contract` against the shared
    vocabulary (D1 tuples); a target gene absent from it raises
    ``ValueError`` — it is never silently skipped. ``contract`` (CTO #250) is
    applied by every per-file load; ``labels_excluded`` is the union across
    files (first-appearance order) and ``label_contract`` its provenance.
    """
    if not h5ad_paths:
        raise ValueError("need at least one h5ad path")

    per_file = [
        load_adamson_matrix(
            p, n_top_hvg=n_top_hvg, max_cells_per_pert=max_cells_per_pert, contract=contract
        )
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
    labels_excluded = _merge_exclusions(e for d in per_file for e in d["labels_excluded"])
    guides_per_gene: dict[str, list[str]] = {}
    for d in per_file:
        for gene, plasmids in d["guides_per_gene"].items():
            guides_per_gene[gene] = sorted(set(guides_per_gene.get(gene, [])) | set(plasmids))
    gene_to_idx = {g: i for i, g in enumerate(shared_genes)}
    # Raises (listing every (label, gene)) on a target outside the shared vocab.
    target_gene_idx = resolve_with_contract(perturbations, gene_to_idx, contract)
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
        "labels_excluded": labels_excluded,
        "guides_per_gene": {g: guides_per_gene[g] for g in sorted(guides_per_gene)},
        "label_contract": contract.to_provenance(),
    }


# ---------------------------------------------------------------------------
# Structural construct parser (CTO #253 a-f)
# ---------------------------------------------------------------------------

MULTI_GENE_REASON = "multi-gene construct; unsupported by D1"
MISSING_LABEL = "nan"
MISSING_ANNOTATION_REASON = "missing perturbation annotation (raw label 'nan')"

_ONLY_MARKER = "_only"
_COMPONENT_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9.\-]*")
# Control constructs ('*', '62(' / '63(' prefixes, 'neg_ctrl', contract
# structural controls) are classified by label_contract.is_adamson_control (QG C16).

ConstructKind = Literal["gene", "multi_gene", "control"]


@dataclass(frozen=True)
class AdamsonConstruct:
    """One raw Adamson ``obs.perturbation`` label, parsed structurally.

    ``components`` are the gene tokens AS WRITTEN (plasmid suffix and ``_only``
    marker removed); ``kind`` is ``"gene"`` for exactly one component,
    ``"multi_gene"`` for more, ``"control"`` for a control construct.
    """

    raw: str
    components: tuple[str, ...]
    kind: ConstructKind
    plasmid: str | None

    @property
    def gene(self) -> str:
        if self.kind != "gene":
            raise ValueError(f"construct {self.raw!r} is {self.kind}, not a single gene")
        return self.components[0]


def parse_adamson_construct(
    raw: str, contract: LabelContract = ADAMSON_CONTRACT
) -> AdamsonConstruct:
    """Parse a raw Adamson label; raise ``ValueError`` naming it if unparseable.

    Strip the plasmid suffix ``_p[A-Z]+[0-9]+(-[0-9]+)?``, then a trailing
    ``_only`` marker; the remainder split on ``_`` is the component tuple.
    Controls: ``'*'``, a ``62(``/``63(`` prefix, label text containing
    ``neg_ctrl``, or a remainder listed in ``contract.structural_controls``
    (``Gal4-4(mod)``). Nothing is guessed: a non-control label without a
    plasmid suffix, an empty/odd component, or a stray ``only`` token raises.
    """
    if not isinstance(raw, str) or not raw or raw != raw.strip():
        raise ValueError(f"unparseable Adamson raw label {raw!r}: empty or padded")
    if raw == "*":
        return AdamsonConstruct(raw=raw, components=("*",), kind="control", plasmid=None)
    rem, plasmid = strip_adamson_plasmid(raw)
    if is_adamson_control(raw, contract):
        return AdamsonConstruct(raw=raw, components=tuple(rem.split("_")), kind="control",
                                plasmid=plasmid)
    if plasmid is None:
        raise ValueError(f"unparseable Adamson raw label {raw!r}: no plasmid suffix "
                         "and not a control construct")
    if rem.endswith(_ONLY_MARKER):
        rem = rem[: -len(_ONLY_MARKER)]
    components = tuple(rem.split("_"))
    bad = [c for c in components if c == "only" or not _COMPONENT_RE.fullmatch(c)]
    if bad:
        raise ValueError(f"unparseable Adamson raw label {raw!r}: component(s) {bad!r}")
    kind: ConstructKind = "gene" if len(components) == 1 else "multi_gene"
    return AdamsonConstruct(raw=raw, components=components, kind=kind, plasmid=plasmid)


def _merge_exclusions(entries: Iterable[Mapping]) -> list[dict]:
    """Merge ``{label, reason, raw_labels, n_cells}`` entries by (label, reason)."""
    merged: dict[tuple[str, str], dict] = {}
    for e in entries:
        key = (str(e["label"]), str(e["reason"]))
        cur = merged.setdefault(key, {"label": key[0], "reason": key[1],
                                      "raw_labels": [], "n_cells": 0})
        cur["raw_labels"] = sorted(set(cur["raw_labels"]) | set(e["raw_labels"]))
        cur["n_cells"] += int(e["n_cells"])
    return list(merged.values())


def eligible_adamson_genes(
    raw_labels_by_subset: Mapping[str, Iterable[str]],
    contract: LabelContract = ADAMSON_CONTRACT,
) -> list[str]:
    """Sorted single-gene task labels the loaders would keep, from raw labels only.

    Skips ``'nan'``, controls, multi-gene constructs and contract exclusions.
    Vocabulary membership (and hence resolvability) needs the matrices and is
    NOT checked here; neither is the |logFC| bin membership.
    """
    genes: set[str] = set()
    for subset in sorted(raw_labels_by_subset):
        for raw in raw_labels_by_subset[subset]:
            if raw == MISSING_LABEL:
                continue
            c = parse_adamson_construct(raw, contract)
            if c.kind == "gene" and not contract.is_excluded(c.gene):
                genes.add(c.gene)
    return sorted(genes)


def load_adamson_matrix(
    h5ad_path: Path | str,
    *,
    n_top_hvg: int = 2000,
    max_cells_per_pert: int = 400,
    contract: LabelContract = ADAMSON_CONTRACT,
) -> dict:
    """Load Adamson, log1p-normalise, downsample. Keeps the FULL gene vocabulary.

    The returned dictionary is the canonical input for every backbone on
    real data: ``{X, labels, control_mask, target_gene_idx, perturbations,
    gene_names, hvg_n_top}``. ``X`` is the raw log1p matrix (float32, all
    genes). **No HVG cut happens here** (T8b, CTO #227): ranking genes over
    all cells would include every held-out perturbation's cells. HVG is
    selected per held-out task on training cells only; ``n_top_hvg`` is
    only recorded as ``ds["hvg_n_top"]`` for that step.

    Raw labels are parsed by :func:`parse_adamson_construct` (CTO #253): a
    single-gene construct's task label is its one component (several plasmids
    of one gene pool into one task; ``ds["guides_per_gene"]`` =
    ``{gene: [plasmid, ...]}``); controls join ``control_mask``; multi-gene
    constructs are excluded (``MULTI_GENE_REASON``, raw label recorded);
    missing annotations (h5ad code -1 / ``'nan'``) are excluded
    (``MISSING_ANNOTATION_REASON``). ``contract`` excludes or aliases parsed
    gene labels. Every ``ds["labels_excluded"]`` entry is ``{"label",
    "reason", "raw_labels", "n_cells"}`` (cells before downsampling).
    ``ds["label_contract"]`` is ``contract.to_provenance()``. Anything still
    unresolvable raises.
    """
    import h5py

    with h5py.File(str(h5ad_path), "r") as f:
        # Perturbation column stored as a h5ad categorical group.
        pert_group = f["obs/perturbation"]
        codes = pert_group["codes"][()]  # type: ignore[index]
        cats_raw = pert_group["categories"][()]  # type: ignore[index]
        cats = [c.decode() if isinstance(c, bytes) else c for c in cats_raw]
        # Code -1 is a MISSING annotation; indexing cats[-1] would silently
        # relabel those cells as the last category.
        labels_raw = np.asarray([cats[c] if c >= 0 else MISSING_LABEL for c in codes])

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

    # Classify every raw label structurally (CTO #253), then downsample per
    # raw label; excluded labels keep no cells and are reported with counts.
    rng = np.random.default_rng(2026)
    keep_mask = np.zeros(dense.shape[0], dtype=bool)
    exclusions: list[dict] = []
    constructs: dict[str, AdamsonConstruct] = {}
    for p in np.unique(labels_raw):
        raw = str(p)
        idx = np.where(labels_raw == p)[0]
        reason_label: tuple[str, str] | None = None
        if raw == MISSING_LABEL:
            reason_label = (MISSING_ANNOTATION_REASON, MISSING_LABEL)
        else:
            c = parse_adamson_construct(raw, contract)
            if c.kind == "multi_gene":
                reason_label = (MULTI_GENE_REASON, raw)
            elif c.kind == "gene" and contract.is_excluded(c.gene):
                reason_label = (contract.excluded[c.gene], c.gene)
            else:
                constructs[raw] = c
        if reason_label is not None:
            exclusions.append({"label": reason_label[1], "reason": reason_label[0],
                               "raw_labels": [raw], "n_cells": int(len(idx))})
            continue
        if len(idx) > max_cells_per_pert:
            idx = rng.choice(idx, size=max_cells_per_pert, replace=False)
        keep_mask[idx] = True
    labels_excluded = _merge_exclusions(exclusions)
    dense = dense[keep_mask]
    labels_raw = labels_raw[keep_mask]

    control_mask = np.asarray(
        [constructs[str(r)].kind == "control" for r in labels_raw], dtype=bool
    )
    labels_norm = np.asarray(
        [c.gene if c.kind == "gene" else "CTRL"
         for c in (constructs[str(r)] for r in labels_raw)]
    )
    guides: dict[str, set[str]] = {}
    for c in constructs.values():
        if c.kind == "gene":
            guides.setdefault(c.gene, set()).add(str(c.plasmid))
    gene_to_idx = {str(g): i for i, g in enumerate(gene_names)}
    # Resolve the parsed single-gene task labels: raw guide labels carry a
    # '_'-joined plasmid suffix that '_'-parsing would misread as a doublet.
    # A target outside the vocab raises (A4) — no random-gene substitute.
    perturbations: list[str] = []
    seen: set[str] = set()
    for is_ctrl, norm_label in zip(control_mask, labels_norm):
        if is_ctrl or norm_label in seen:
            continue
        seen.add(str(norm_label))
        perturbations.append(str(norm_label))
    target_gene_idx = resolve_with_contract(perturbations, gene_to_idx, contract)
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
        "labels_excluded": labels_excluded,
        "guides_per_gene": {g: sorted(guides[g]) for g in sorted(guides)},
        "label_contract": contract.to_provenance(),
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
