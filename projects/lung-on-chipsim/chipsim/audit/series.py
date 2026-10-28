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

So `icc` is handled as a **sensitivity range**, not an input. `structure_over_icc_range`
reports `(icc, deff, n_eff)` across the plausible band — **it does not report power**;
see its docstring for why that distinction is load-bearing.

**Every number here is an UPPER bound on independent information.** Murcko
scaffolding detects only ring-system sharing, so it is *blind* to acyclic analog
series (a homologous fatty-acid or amino-acid series has no ring system and is
reported as fully independent). Blindness is not evidence of independence. Where
that blindness applies, `SeriesStructure.n_acyclic` is non-zero and `n_eff` is an
upper bound rather than an estimate — surfaced, never silent, because a roster of
transporter substrates (carnitine, choline, amino acids, polyamines) is exactly
the case where this fires and exactly the direction that greenlights an
underpowered study.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

__all__ = [
    "SeriesStructure",
    "StructureRow",
    "cluster_by_scaffold",
    "design_effect",
    "effective_n_unequal",
    "measure_series_structure",
    "murcko_scaffold",
    "structure_over_icc_range",
]


def _validated_sizes(sizes: Iterable[int]) -> tuple[int, ...]:
    """Materialise once, then validate. Order matters for both reasons.

    **Materialising first is a correctness fix, not tidiness.** `sizes` was
    iterated three times (`sum`, `any`, `sum`), so a one-shot iterable was
    exhausted after the first pass and `m_A` came out `0`, yielding
    `deff = 1 - icc` — **below 1**, which is mathematically impossible and claims
    *more* independent information than the roster holds. The natural call site,
    `design_effect((len(v) for v in cluster_by_scaffold(s).values()), icc)`, is
    exactly that shape.

    **Positivity is checked before emptiness** so `[-2, -3]` reports the
    positivity error rather than the misleading "empty roster".
    """
    if isinstance(sizes, (str, bytes)):
        raise TypeError(f"cluster sizes must be a sequence of ints, got {type(sizes).__name__}")
    materialised = tuple(sizes)
    for m in materialised:
        if isinstance(m, bool) or not isinstance(m, int):
            raise TypeError(f"cluster sizes must be integers; got {materialised!r}")
        if m <= 0:
            raise ValueError(f"cluster sizes must be positive; got {materialised!r}")
    if not materialised:
        raise ValueError("cannot compute a design effect over an empty roster")
    return materialised


def _validated_icc(icc: float) -> float:
    """`not 0.0 <= icc <= 1.0` — the form that rejects NaN.

    The previous `icc < 0.0 or icc > 1.0` let **NaN** through, because both
    comparisons are `False` for NaN. `deff` then became `nan`, `n_eff` became
    `nan`, and a halt rule written `if n_eff < required: halt` **never fires** —
    NaN silently authorises the spend. `power.simulate_clustered_ligand_set`
    already used the correct form, so the two halves of the same gate disagreed
    on their domain guard.
    """
    if not 0.0 <= icc <= 1.0:
        raise ValueError(f"icc must lie in [0, 1] and be non-NaN; got {icc!r}")
    return icc


def design_effect(sizes: Iterable[int], icc: float) -> float:
    """`1 + (m_A - 1)*icc`, the design effect for **unequal** cluster sizes.

    `m_A = sum(m_i^2) / sum(m_i)` — the size-weighted mean, not the arithmetic mean.

    **Relative to the arithmetic mean this is a correction, not a refinement.**
    `power.effective_n` takes a single scalar `cluster_size`, so applied to a real
    roster it is reached through the arithmetic mean. By Cauchy-Schwarz
    `m_A >= mean(m)` for every size vector, equality only when all clusters are
    identical — so *the arithmetic reading* always understates the discount.

    Measured, one series of 12 among 28 singletons at `icc = 0.5`: arithmetic mean
    reads `n_eff = 33.6`, size-weighted reads **15.1** — a **2.2x overstatement**
    of the independent information, on an entirely ordinary roster shape.

    **Scoped deliberately.** A reader who instead plugs the *largest* cluster into
    `power.effective_n` errs the other way (`6.15` for the same roster —
    over-conservative by 2.5x). "Always optimistic" is true of the arithmetic-mean
    reading, which is the one a reader reaches for by default; it is not a property
    of `power.effective_n` in the abstract. Stating it unscoped would itself be a
    number carried across the boundary of the assumption that produced it.
    """
    materialised = _validated_sizes(sizes)
    icc = _validated_icc(icc)
    total = sum(materialised)
    m_a = sum(m * m for m in materialised) / total
    deff = 1.0 + (m_a - 1.0) * icc
    if deff < 1.0:
        raise AssertionError(
            f"design effect {deff!r} < 1 for sizes={materialised!r}, icc={icc!r} — "
            "a design effect below 1 claims more independent information than the "
            "roster holds and is always a bug"
        )
    return deff


def effective_n_unequal(sizes: Iterable[int], icc: float) -> float:
    """`n / deff` for an unequal-sized roster."""
    materialised = _validated_sizes(sizes)
    return sum(materialised) / design_effect(materialised, icc)


def murcko_scaffold(smiles: str) -> str:
    """Bemis-Murcko scaffold as canonical SMILES.

    Raises on unparseable, empty, blank, or zero-atom input rather than returning
    `""`. **`Chem.MolFromSmiles("")` returns a valid EMPTY `Mol`, not `None`**, so
    a bare `mol is None` guard does not fire: an empty cell became `""`, which
    `cluster_by_scaffold` then classified as an independent acyclic singleton.
    Three blank trailing cells in a ChEMBL CSV export would inflate `n` by three.
    `"   "` and `"\\n"` *do* raise, so the gap was invisible to casual testing.
    Salt-only rows (`"[Na+].[Cl-]"`) hit the same path.
    """
    from rdkit import Chem
    from rdkit.Chem.Scaffolds import MurckoScaffold

    if not isinstance(smiles, str):
        raise TypeError(f"SMILES must be a string; got {type(smiles).__name__}")
    if not smiles.strip():
        raise ValueError(f"empty or blank SMILES: {smiles!r}")
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"unparseable SMILES: {smiles!r}")
    if mol.GetNumAtoms() == 0:
        raise ValueError(f"SMILES parsed to a zero-atom molecule: {smiles!r}")
    scaffold = MurckoScaffold.GetScaffoldForMol(mol)
    return Chem.MolToSmiles(scaffold)


def cluster_by_scaffold(smiles: Sequence[str]) -> dict[str, list[int]]:
    """Group ligand indices by Bemis-Murcko scaffold.

    Acyclic molecules yield the empty scaffold. They are **not** pooled into one
    series — having no ring system in common is not evidence of sharing one — so
    each gets a distinct `<acyclic:N>` key.

    **But nor are they evidence of independence, and that is the harder half.**
    Murcko is *blind* to acyclic analog series: six homologous fatty acids
    (C8-C13) are a textbook series and are reported here as six singletons.
    Blindness in the optimistic direction is the one that greenlights an
    underpowered study, and it lands precisely on transporter substrates —
    carnitine, choline, amino acids, polyamines. Callers must read
    `SeriesStructure.n_acyclic`; `measure_series_structure` surfaces it.
    """
    if isinstance(smiles, (str, bytes)):
        raise TypeError(
            f"expected a sequence of SMILES strings, got a bare {type(smiles).__name__} "
            "(a str is a Sequence[str] of its own characters)"
        )
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
    """Realised clustering of a compound roster. `icc` is deliberately absent.

    `singleton_cluster_fraction` is the fraction of **clusters** that are
    singletons; `singleton_compound_fraction` is the fraction of **compounds**
    sitting in one. They differ sharply — on `[12] + [1]*28` they are `0.966` and
    `0.70` — and the unqualified name `singleton_fraction` disclosed neither
    denominator while being the figure a reader would quote to argue a roster is
    diverse. Both are now named for their denominator.

    `n_acyclic` counts compounds with no ring system, for which Murcko detects no
    series. When it is non-zero, **`n_eff` is an upper bound, not an estimate.**
    """

    n: int
    cluster_sizes: tuple[int, ...]
    n_clusters: int
    max_cluster: int
    n_acyclic: int
    singleton_cluster_fraction: float
    singleton_compound_fraction: float
    weighted_mean_size: float

    @property
    def clustering_is_lower_bound(self) -> bool:
        """True when Murcko was blind to part of the roster, so `n_eff` is an upper bound."""
        return self.n_acyclic > 0

    def effective_n(self, icc: float) -> float:
        """Effective sample size. **Upper bound** when `clustering_is_lower_bound`."""
        return effective_n_unequal(self.cluster_sizes, icc)

    def design_effect(self, icc: float) -> float:
        """Design effect. **Lower bound** when `clustering_is_lower_bound`."""
        return design_effect(self.cluster_sizes, icc)


def measure_series_structure(smiles: Sequence[str]) -> SeriesStructure:
    """Measure realised series structure from SMILES. No `icc`, by construction."""
    if isinstance(smiles, (str, bytes)):
        raise TypeError(
            f"expected a sequence of SMILES strings, got a bare {type(smiles).__name__} "
            "(a str is a Sequence[str] of its own characters)"
        )
    if len(smiles) == 0:
        raise ValueError("cannot measure series structure of an empty roster")
    groups = cluster_by_scaffold(smiles)
    n_acyclic = sum(1 for k in groups if k.startswith("<acyclic:"))
    sizes = tuple(sorted((len(v) for v in groups.values()), reverse=True))
    n = sum(sizes)
    counts = Counter(sizes)
    m_a = sum(m * m for m in sizes) / n
    return SeriesStructure(
        n=n,
        cluster_sizes=sizes,
        n_clusters=len(sizes),
        max_cluster=max(sizes),
        n_acyclic=n_acyclic,
        singleton_cluster_fraction=counts[1] / len(sizes),
        singleton_compound_fraction=counts[1] / n,
        weighted_mean_size=m_a,
    )


@dataclass(frozen=True)
class StructureRow:
    """One row of the sensitivity band.

    `n_eff_is_upper_bound` is a field rather than a footnote so a caller cannot
    read `n_eff` without it being in the same object.
    """

    icc: float
    deff: float
    n_eff: float
    n_eff_is_upper_bound: bool


def structure_over_icc_range(
    structure: SeriesStructure,
    icc_grid: Sequence[float] = (0.0, 0.3, 0.5, 0.8),
) -> list[StructureRow]:
    """`(icc, deff, n_eff)` across the sensitivity band. **Returns no power.**

    Renamed from `power_over_icc_range`, which computed no power. The old name
    invited a caller wiring the halt rule to read slot 2 as a probability and
    compare `15.09` against a `0.8` threshold — always passing. The A&D requires
    the halt rule to be evaluated on **power** across this band; that power does
    not exist yet, because `power.clustered_sign_test_power` accepts only a scalar
    `cluster_size` (the arithmetic-mean form this module exists to correct) and
    `SeriesStructure` does not yet carry per-compound labels. **Naming this
    function for a quantity it does not compute was the same defect the A&D
    catalogues; renaming it is the honest half of the fix, and the missing
    label-aware power path is recorded as outstanding.**

    A grid of fewer than two points is rejected: the contract is that the halt
    rule *holds across the band*, and `all([])` is `True`, so an empty grid would
    satisfy it vacuously. A one-point grid is the point estimate the docstring
    forbids. That check lived only in the test suite; it belongs in the code.
    """
    grid = tuple(icc_grid)
    if len(grid) < 2:
        raise ValueError(
            f"icc_grid needs at least 2 points to be a sensitivity band; got {grid!r} — "
            "an empty grid satisfies 'holds across the band' vacuously and a "
            "single point is the estimate this function exists to refuse"
        )
    return [
        StructureRow(
            icc=icc,
            deff=structure.design_effect(icc),
            n_eff=structure.effective_n(icc),
            n_eff_is_upper_bound=structure.clustering_is_lower_bound,
        )
        for icc in grid
    ]
