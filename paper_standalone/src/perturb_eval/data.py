"""Perturb-seq dataset protocol + lightweight loaders.

The goal is to let agents and predictors depend on a common interface without
forcing scanpy/anndata into the core package. Real loaders live behind
optional imports.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class PerturbSeqSplit:
    """A minimal training/eval split for perturb-seq tasks."""

    name: str
    n_cells: int
    n_genes: int
    n_perturbations: int
    perturbation_names: tuple[str, ...]
    path: Path | None = None  # where the AnnData lives, if any


class PerturbSeqDataset(Protocol):
    name: str

    def train(self) -> PerturbSeqSplit: ...
    def val(self) -> PerturbSeqSplit: ...
    def test(self) -> PerturbSeqSplit: ...


# ---------------------------------------------------------------------------
# Synthetic stub — used by tests and the end-to-end demo
# ---------------------------------------------------------------------------


@dataclass
class SyntheticPerturbSeq:
    """Deterministic in-memory stub. No I/O, no numpy in this file."""

    name: str = "synthetic"
    n_cells: int = 500
    n_genes: int = 50
    perturbations: tuple[str, ...] = (
        "GSK3B_KO", "TP53_KO", "CTNNB1_KO", "IL6_stim", "LPS_stim",
    )

    def train(self) -> PerturbSeqSplit:
        return self._split("train", frac=0.7)

    def val(self) -> PerturbSeqSplit:
        return self._split("val", frac=0.15)

    def test(self) -> PerturbSeqSplit:
        return self._split("test", frac=0.15)

    def _split(self, name: str, frac: float) -> PerturbSeqSplit:
        return PerturbSeqSplit(
            name=f"{self.name}:{name}",
            n_cells=int(self.n_cells * frac),
            n_genes=self.n_genes,
            n_perturbations=len(self.perturbations),
            perturbation_names=self.perturbations,
        )


# ---------------------------------------------------------------------------
# Real loaders — optional, lazily imported
# ---------------------------------------------------------------------------


def load_norman(path: Path | str) -> PerturbSeqDataset:  # pragma: no cover - needs scanpy
    """Load Norman et al. 2019 from a cached AnnData at ``path``.

    Fetch instructions: ``scripts/fetch_norman.py`` downloads GSE133344 and
    writes ``norman2019.h5ad`` into the given directory.
    """
    import anndata  # noqa: F401
    # Deferred; the real implementation builds a PerturbSeqDataset around scanpy.
    raise NotImplementedError(
        "Real Norman loader requires anndata + the h5ad file — see scripts/fetch_norman.py"
    )


def load_adamson(path: Path | str) -> PerturbSeqDataset:  # pragma: no cover
    """Load Adamson et al. 2016 (UPR) — lighter alternative to Norman."""
    raise NotImplementedError("Real Adamson loader — see scripts/fetch_adamson.py")
