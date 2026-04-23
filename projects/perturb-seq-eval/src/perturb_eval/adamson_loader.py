"""Loader for the real Adamson 2016 Perturb-seq h5ad.

We use only ``h5py`` (part of the scientific Python stack) — no scanpy or
anndata dependency — because all we need is the perturbation labels and
basic QC metrics; we do not do any single-cell preprocessing here.

Dataset source: Zenodo record 13350497 (scPerturb curated repackaging of
GSE90546). Fetch with ``scripts/fetch_adamson.py``.

Adamson, B. et al. *A Multiplexed Single-Cell CRISPR Screening Platform
Enables Systematic Dissection of the Unfolded Protein Response.* Cell 167,
1867–1882 (2016). doi:10.1016/j.cell.2016.11.048
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from perturb_eval.data import PerturbSeqSplit


@dataclass(frozen=True)
class AdamsonQC:
    n_cells: int
    n_genes: int
    perturbation_names: tuple[str, ...]
    perturbation_counts: tuple[int, ...]
    median_ncounts: float
    median_ngenes: int
    median_pct_mito: float
    cell_line: str


def load_adamson_h5ad(path: Path | str) -> AdamsonQC:
    """Read the real Adamson 2016 h5ad and return a QC summary.

    Returns a frozen ``AdamsonQC`` record. The raw h5ad is not kept in
    memory; only the lightweight obs/var metadata is inspected.
    """
    import h5py

    with h5py.File(str(path), "r") as f:
        obs = f["obs"]
        var = f["var"]

        # Use obs row count as the authoritative n_cells — X may be stored
        # in either CSR or CSC depending on the source, so indptr axis is
        # ambiguous. obs columns all have length n_cells.
        n_cells = int(f["obs/ncounts"].shape[0])
        n_genes = int(var["gene_symbol"].shape[0])

        pert_cats_raw = obs["perturbation/categories"][:]
        pert_codes = obs["perturbation/codes"][:]
        pert_names = tuple(
            (c.decode() if isinstance(c, bytes) else str(c)) for c in pert_cats_raw
        )
        pert_counts = tuple(int((pert_codes == i).sum()) for i in range(len(pert_names)))

        ncounts = f["obs/ncounts"][:]
        ngenes = f["obs/ngenes"][:]
        pct_mito = f["obs/percent_mito"][:]

        cell_line_raw = obs["cell_line/categories"][:]
        cell_line = (cell_line_raw[0].decode() if isinstance(cell_line_raw[0], bytes)
                     else str(cell_line_raw[0]))

    import statistics

    return AdamsonQC(
        n_cells=n_cells,
        n_genes=n_genes,
        perturbation_names=pert_names,
        perturbation_counts=pert_counts,
        median_ncounts=float(statistics.median(ncounts)),
        median_ngenes=int(statistics.median(ngenes)),
        median_pct_mito=float(statistics.median(pct_mito)),
        cell_line=cell_line,
    )


def adamson_to_split(qc: AdamsonQC, *, split: str = "train",
                     fraction: float = 1.0) -> PerturbSeqSplit:
    """Wrap the QC summary as a PerturbSeqSplit-compatible record."""
    return PerturbSeqSplit(
        name=f"Adamson2016:{split}",
        n_cells=int(qc.n_cells * fraction),
        n_genes=qc.n_genes,
        n_perturbations=len(qc.perturbation_names),
        perturbation_names=qc.perturbation_names,
    )


def perturbation_as_task_name(raw_pert: str) -> str:
    """Turn 'DDIT3_pDS263' or 'CREB1_pDS269' into a human task name.

    Guide barcodes ('pDS263', 'pBA581', etc.) are stripped; control
    perturbations (starting with '*' or the wildtype barcode '62(mod)')
    are mapped to 'control'.
    """
    if not raw_pert or raw_pert.startswith("*") or raw_pert.startswith("62("):
        return "control"
    # Take the leading gene symbol before the underscore.
    return raw_pert.split("_", 1)[0].upper() + " knockdown"
