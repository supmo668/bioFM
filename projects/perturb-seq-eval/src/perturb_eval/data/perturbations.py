"""Perturbation label parsing and target-column resolution (T7; A4 / D1).

Norman 2019 (scPerturb bundle) joins double knockdowns with ``_``
(``CBL_UBASH3A``); singletons are bare symbols (``BAK1``). Under the D1
multi-target contract every perturbation maps to a *tuple* of target column
indices — singletons are 1-tuples, doublets 2-tuples.

:func:`resolve_target_indices` never substitutes: a target gene absent from
the vocabulary is an error, reported for every ``(label, gene)`` pair at once.

Labels must already be gene-level. Raw Adamson guide labels
(``DDIT3_pDS263``, control ``62(mod)_pBA581``) carry a ``_``-joined plasmid
suffix and are NOT doublets — parse them first (``e2_adamson.parse_adamson_construct``).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

def is_control(label: str) -> bool:
    """True iff ``label`` is a control under the Norman OR the Adamson predicate.

    Delegates to the per-dataset predicates owned by
    :mod:`perturb_eval.data.label_contract` (QG C16); both loaders relabel
    controls to ``"CTRL"``, which the Norman ``ctrl`` token covers. Imported
    lazily: ``label_contract`` imports this module.
    """
    from perturb_eval.data.label_contract import is_adamson_control, is_norman_control

    return is_norman_control(label) or is_adamson_control(label)


def parse_perturbation(label: str, delim: str = "_") -> tuple[str, ...]:
    """Split ``label`` on ``delim`` into stripped gene symbols.

    ``"CBL_UBASH3A"`` -> ``("CBL", "UBASH3A")``; ``"BAK1"`` -> ``("BAK1",)``.
    Raises ``ValueError`` if the label or any part is empty (``""``, ``"A__B"``).
    """
    if not delim:
        raise ValueError("delim must be a non-empty string")
    parts = tuple(p.strip() for p in label.split(delim))
    if any(not p for p in parts):
        raise ValueError(
            f"perturbation label {label!r} has an empty part when split on {delim!r}: {parts!r}"
        )
    return parts


def is_doublet(label: str, delim: str = "_") -> bool:
    """True for a two-gene label, False for a singleton; raises for >=3 parts."""
    parts = parse_perturbation(label, delim)
    if len(parts) > 2:
        raise ValueError(
            f"perturbation label {label!r} has {len(parts)} parts when split on {delim!r}; "
            "Norman 2019 has no triplet (or higher-order) perturbations — "
            "check the delimiter or the label source"
        )
    return len(parts) == 2


def resolve_target_indices(
    perturbations: Iterable[str],
    gene_to_idx: Mapping[str, int],
    *,
    delim: str = "_",
) -> dict[str, tuple[int, ...]]:
    """Map each non-control perturbation to its target column indices (label order).

    Controls (:func:`is_control`) are omitted from the result. Every gene of
    every other label must be in ``gene_to_idx``; otherwise a single
    ``ValueError`` lists each missing ``(label, gene)`` pair. No fallback index
    is ever substituted.
    """
    out: dict[str, tuple[int, ...]] = {}
    missing: list[tuple[str, str]] = []
    for label in perturbations:
        if is_control(label):
            continue
        genes = parse_perturbation(label, delim)
        miss = [(label, g) for g in genes if g not in gene_to_idx]
        if miss:
            missing.extend(miss)
            continue
        out[label] = tuple(int(gene_to_idx[g]) for g in genes)
    if missing:
        pairs = ", ".join(repr(m) for m in missing)
        raise ValueError(
            f"{len(missing)} perturbation target gene(s) absent from the gene vocabulary "
            f"(len(gene_to_idx)={len(gene_to_idx)}); refusing to substitute. "
            f"Missing (label, gene): {pairs}"
        )
    return out
