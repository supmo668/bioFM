"""Data-curator tool belt: AnnData-like QC and loading.

The real implementation would wrap ``scanpy`` / ``anndata`` / ``cellxgene-census``.
Here we stub out the return shapes so the pipeline can be exercised.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QCReport:
    n_cells: int
    n_genes: int
    pct_mito_max: float
    pct_ribo_max: float
    hvgs: int
    doublet_rate: float
    dataset_id: str


class OmicsTool:
    name = "omics.qc"

    # ---- data fetch ------------------------------------------------------
    def fetch(self, modality: str, perturbation: str) -> str:
        """Pretend to resolve a perturbation × modality pair to a GEO/CellxGene ID."""
        # Real implementation: query cellxgene-census / GEO.
        return f"CXG::{modality}::{perturbation}"

    # ---- qc --------------------------------------------------------------
    def qc(self, dataset_id: str) -> QCReport:
        """Compute standard single-cell QC metrics (stub)."""
        return QCReport(
            n_cells=48_000,
            n_genes=22_000,
            pct_mito_max=12.0,
            pct_ribo_max=35.0,
            hvgs=3_000,
            doublet_rate=0.04,
            dataset_id=dataset_id,
        )
