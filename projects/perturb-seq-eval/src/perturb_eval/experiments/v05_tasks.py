"""Deterministic v0.5 task-list construction (build-plan T2).

Pure function over plain data (labels + per-label scores), so it is testable
without AnnData or Modal and independent of ``PYTHONHASHSEED`` and of dict
insertion order: every mapping is iterated in ``sorted()`` key order, every
label pool is sorted before sampling, and Norman strata come from
:func:`deterministic_stratum` (CRC32), never the built-in salted ``hash``.

Controls are not filtered here: exactly as in ``scripts/modal/app_v05.py``
before this refactor, control labels are excluded upstream by the loaders
(Adamson scores are keyed by ``target_gene_idx``; Norman ``perturbations``
omits controls).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from perturb_eval.data.perturbations import is_doublet
from perturb_eval.data.subsample import deterministic_stratum, stratified_subsample

_NORMAN_SINGLETON_STRATA = 3
_NORMAN_DOUBLET_STRATA = 2


@dataclass(frozen=True)
class TaskPlan:
    """Resolved held-out task lists plus the provenance needed to audit them.

    ``strata`` keys are namespaced ``"<pool>:<label>"`` (pool one of
    ``adamson`` / ``norman_singletons`` / ``norman_doublets``) so a gene that
    appears in both datasets cannot overwrite its other stratum.
    """

    adamson: tuple[str, ...]
    norman_singletons: tuple[str, ...]
    norman_doublets: tuple[str, ...]
    strata: dict[str, int] = field(default_factory=dict)
    eligible_counts: dict[str, int] = field(default_factory=dict)

    @property
    def all_tasks(self) -> tuple[str, ...]:
        return self.adamson + self.norman_singletons + self.norman_doublets

    def to_dict(self) -> dict[str, Any]:
        return {
            "adamson": list(self.adamson),
            "norman_singletons": list(self.norman_singletons),
            "norman_doublets": list(self.norman_doublets),
            "strata": {k: int(self.strata[k]) for k in sorted(self.strata)},
            "eligible_counts": {
                k: int(self.eligible_counts[k]) for k in sorted(self.eligible_counts)
            },
        }


def _pool_adamson(
    adamson_summary: Mapping[str, Mapping[str, float]],
) -> list[tuple[str, float]]:
    pooled: dict[str, float] = {}
    for subset in sorted(adamson_summary):
        scores = adamson_summary[subset]
        for label in sorted(scores):
            if label in pooled:
                raise ValueError(
                    f"Adamson label {label!r} appears in more than one subset "
                    f"(second: {subset!r}); pooled stratification is ambiguous"
                )
            pooled[label] = float(scores[label])
    return sorted(pooled.items())


def build_task_lists(
    adamson_summary: Mapping[str, Mapping[str, float]],
    norman_labels: Sequence[str],
    *,
    norman_n_singletons: int,
    norman_n_doublets: int,
    adamson_n_per_bin: int,
    adamson_n_bins: int,
    seed: int,
    doublet_delim: str = "_",
) -> TaskPlan:
    """Build the Adamson + Norman held-out task lists deterministically.

    Parameters
    ----------
    adamson_summary
        ``{subset name: {perturbation label: mean |logFC| of its target}}``.
        Labels are pooled across subsets and binned into ``adamson_n_bins``
        quantile bins of score; ``adamson_n_per_bin`` are drawn per bin and
        the draw is topped up to exactly ``adamson_n_per_bin * adamson_n_bins``
        (uneven bins). A pool of exactly that size is kept whole.

    Raises
    ------
    AssertionError
        (T11 / C-RG-2) if any pool is smaller than its requested count, so
        the resolved lists can never be silently short. The message gives
        requested vs got and every eligible-pool size.
    norman_labels
        Non-control Norman perturbation labels (singletons and doublets).
    """
    strata: dict[str, int] = {}

    # ---- Adamson: quantile bins over mean |logFC| ----
    pooled = _pool_adamson(adamson_summary)
    tfs = np.array([lbl for lbl, _ in pooled], dtype=object)
    strengths = np.array([s for _, s in pooled], dtype=float)
    adamson_n = adamson_n_per_bin * adamson_n_bins
    if len(tfs) > adamson_n:
        bin_edges = np.quantile(strengths, np.linspace(0, 1, adamson_n_bins + 1))
        # digitize returns bin ids in [1..n_bins]; clamp to [0..n_bins-1].
        bin_ids = np.clip(
            np.digitize(strengths, bin_edges[1:-1]), 0, adamson_n_bins - 1
        )
        for lbl, b in zip(tfs, bin_ids):
            strata[f"adamson:{lbl}"] = int(b)
        adamson = tuple(
            str(x)
            for x in stratified_subsample(
                tfs,
                bin_ids,
                n_per_stratum=adamson_n_per_bin,
                seed=seed,
                n_total=adamson_n,
            )
        )
    else:
        adamson = tuple(str(x) for x in tfs)

    # ---- Norman: singleton / doublet split, CRC32 strata ----
    unique_labels = sorted(set(norman_labels))
    singletons = [p for p in unique_labels if not is_doublet(p, doublet_delim)]
    doublets = [p for p in unique_labels if is_doublet(p, doublet_delim)]

    def _draw(pool: list[str], k: int, n: int, name: str) -> tuple[str, ...]:
        if not pool or n <= 0:
            return ()
        pool_strata = [deterministic_stratum(p, k) for p in pool]
        for p, s in zip(pool, pool_strata):
            strata[f"{name}:{p}"] = s
        chosen = stratified_subsample(
            np.array(pool, dtype=object),
            np.array(pool_strata),
            n_per_stratum=max(1, n // k),
            seed=seed,
            n_total=n,
        )
        return tuple(str(x) for x in chosen)

    chosen_singletons = _draw(
        singletons, _NORMAN_SINGLETON_STRATA, norman_n_singletons, "norman_singletons"
    )
    chosen_doublets = _draw(
        doublets, _NORMAN_DOUBLET_STRATA, norman_n_doublets, "norman_doublets"
    )

    _check_counts(
        [
            ("adamson", "adamson", adamson_n, len(adamson), len(tfs)),
            ("norman singletons", "singletons", norman_n_singletons,
             len(chosen_singletons), len(singletons)),
            ("norman doublets", "doublets", norman_n_doublets,
             len(chosen_doublets), len(doublets)),
        ],
        doublet_delim,
    )

    return TaskPlan(
        adamson=adamson,
        norman_singletons=chosen_singletons,
        norman_doublets=chosen_doublets,
        strata=strata,
        eligible_counts={
            "adamson": len(tfs),
            "norman_singletons": len(singletons),
            "norman_doublets": len(doublets),
        },
    )


def _check_counts(
    rows: Sequence[tuple[str, str, int, int, int]], doublet_delim: str
) -> None:
    """Raise ``AssertionError`` if any pool resolved short of its request.

    An explicit ``raise`` (not ``assert``) so ``python -O`` cannot strip it.
    With exact fill this fires only when a pool is genuinely too small.
    """
    short = [r for r in rows if r[3] != r[2]]
    if not short:
        return
    pools = "; ".join(f"eligible {tag}: {pool}" for _, tag, _, _, pool in rows)
    what = "; ".join(f"{name}: requested {req}, got {got}" for name, _, req, got, _ in short)
    raise AssertionError(
        f"task-list stratum count mismatch — {what} ({pools}; "
        f"doublet_delim={doublet_delim!r})"
    )
