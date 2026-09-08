"""A7 · realised analog-series structure, measured from SMILES.

P7 measured *how much* clustering costs: at series of five with `icc = 0.8` the
sign test falls from 0.95 to 0.46. That established the magnitude. It did not
establish the **realised** value for an actual compound roster, and the halt rule
(G3, r1.6) is evaluated on the realised value, never on the exchangeable
idealisation.

This module supplies the half of that input which is genuinely free: the
**series-size distribution**, computed locally from SMILES with the RDKit layer
R5 already needs, at zero Modal cost.

**What this module deliberately does NOT do, and why it matters.**

`icc` is **not derivable from structure.** Structure says which compounds are
analogs; `icc` says how correlated their `(y, f)` *contributions* are, and `f` is
a Boltz-2 prediction that does not exist until the batch has been spent. The A&D's
P7 remedy read *"series membership is computable locally from SMILES ... and P0 is
re-run on the measured `icc` and series-size distribution"* — which slides from a
quantity that IS free (membership) to one that is NOT (`icc`) inside a single
sentence. Treating `icc` as measured pre-spend would be the same defect this
programme keeps catching: a number carried across the boundary of the assumption
that produced it.

So `icc` is handled as a **sensitivity range**, not an input. `power_over_icc_range`
reports power across the plausible band, and the halt rule must hold across it
rather than at a convenient point.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

__all__ = [
    "SeriesStructure",
    "cluster_by_scaffold",
    "design_effect",
    "effective_n_unequal",
    "measure_series_structure",
    "murcko_scaffold",
    "power_over_icc_range",
]


def design_effect(sizes: Sequence[int], icc: float) -> float:
    """`1 + (m_A − 1)·icc`, the design effect for **unequal** cluster sizes.

    `m_A = Σmᵢ² / Σmᵢ` — the size-weighted mean, not the arithmetic mean.

    **This is not a refinement of `power.effective_n`; it is a correction of it.**
    That function takes a single `cluster_size` and so, applied to a real roster,
    is reached through the arithmetic mean. By Cauchy–Schwarz `m_A ≥ mean(m)` for
    every size vector, with equality **only** when all clusters are the same size.
    A real roster is never equal-sized, so the arithmetic mean **always**
    understates the design effect — optimistic, in the same direction as every
    other A7 error, and silently.

    Measured, one series of 12 among 28 singletons at `icc = 0.5`: the arithmetic
    mean reads `n_eff = 33.6`, the correct size-weighted `m_A` reads **15.1**. The
    optimistic form claims **2.2× more independent information than the roster
    holds** — and it is the form a reader reaches for by default.
    """
    if icc < 0.0 or icc > 1.0:
        raise ValueError(f"icc must lie in [0, 1]; got {icc}")
    total = sum(sizes)
    if total <= 0:
        raise ValueError("cannot compute a design effect over an empty roster")
    if any(m <= 0 for m in sizes):
        raise ValueError(f"cluster sizes must be positive; got {list(sizes)}")
    m_a = sum(m * m for m in sizes) / total
    return 1.0 + (m_a - 1.0) * icc


def effective_n_unequal(sizes: Sequence[int], icc: float) -> float:
    """`n / deff` for an unequal-sized roster."""
    return sum(sizes) / design_effect(sizes, icc)


def murcko_scaffold(smiles: str) -> str:
    """Bemis–Murcko scaffold as canonical SMILES.

    Raises on an unparseable SMILES rather than returning `""`. A molecule that
    silently becomes the empty scaffold would be pooled with every other failure
    into one enormous phantom series — a parse failure reported as the strongest
    possible clustering signal, in the optimistic-to-pessimistic direction but
    still a fabricated number.
    """
    from rdkit import Chem
    from rdkit.Chem.Scaffolds import MurckoScaffold

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"unparseable SMILES: {smiles!r}")
    scaffold = MurckoScaffold.GetScaffoldForMol(mol)
    return Chem.MolToSmiles(scaffold)


def cluster_by_scaffold(smiles: Iterable[str]) -> dict[str, list[int]]:
    """Group ligand indices by Bemis–Murcko scaffold.

    Acyclic molecules yield the empty scaffold `""`. They are **not** one series:
    having no ring system in common is not evidence of sharing one. Each is
    returned as its own singleton under a distinct key.
    """
    groups: dict[str, list[int]] = {}
    acyclic = 0
    for i, smi in enumerate(smiles):
        scaffold = murcko_scaffold(smi)
        if scaffold == "":
            key = f"<acyclic:{acyclic}>"
            acyclic += 1
        else:
            key = scaffold
        groups.setdefault(key, []).append(i)
    return groups


@dataclass(frozen=True)
class SeriesStructure:
    """Realised clustering of a compound roster. `icc` is deliberately absent."""

    n: int
    cluster_sizes: tuple[int, ...]
    n_clusters: int
    max_cluster: int
    singleton_fraction: float
    weighted_mean_size: float

    def effective_n(self, icc: float) -> float:
        return effective_n_unequal(self.cluster_sizes, icc)

    def design_effect(self, icc: float) -> float:
        return design_effect(self.cluster_sizes, icc)


def measure_series_structure(smiles: Sequence[str]) -> SeriesStructure:
    """Measure realised series structure from SMILES. No `icc`, by construction."""
    if len(smiles) == 0:
        raise ValueError("cannot measure series structure of an empty roster")
    groups = cluster_by_scaffold(smiles)
    sizes = tuple(sorted((len(v) for v in groups.values()), reverse=True))
    n = sum(sizes)
    counts = Counter(sizes)
    m_a = sum(m * m for m in sizes) / n
    return SeriesStructure(
        n=n,
        cluster_sizes=sizes,
        n_clusters=len(sizes),
        max_cluster=max(sizes),
        singleton_fraction=counts[1] / len(sizes),
        weighted_mean_size=m_a,
    )


def power_over_icc_range(
    structure: SeriesStructure,
    icc_grid: Sequence[float] = (0.0, 0.3, 0.5, 0.8),
) -> list[tuple[float, float, float]]:
    """`(icc, deff, n_eff)` across the sensitivity band.

    Returns a **range**, never a point estimate, because `icc` is not measurable
    before the batch is spent. The halt rule holds across this band or it does
    not hold.
    """
    return [(icc, structure.design_effect(icc), structure.effective_n(icc)) for icc in icc_grid]
