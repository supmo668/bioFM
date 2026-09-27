"""Per-held-out-task training on real data with train-only HVG (T8b, CTO #227).

The loaders return the FULL gene vocabulary (raw matrix only, never a feature
selection). For each held-out perturbation this module:

1. selects the task's 20 evaluation genes ONCE on the full post-QC gene axis
   (:func:`perturb_eval.data.hvg.top_deg_columns`, amendment 2 A2-5);
2. selects HVG with :func:`perturb_eval.data.hvg.select_hvg_train_only` over
   ``labels != held`` (controls stay in the training rows, as before), forcing
   in every perturbation's target columns and the task's evaluation genes;
3. slices all cells to those columns (float64) and remaps targets;
4. fits a backbone on the training rows and scores the held-out perturbation
   on its evaluation genes.

Amendment 2 A2-4: the trainer grid is backbone x R x seed (N removed);
:func:`trainer_grid` states the distinct-configuration count and the seeds.

:func:`iter_trainer_records` is the v0.5 trainer-sweep loop body moved out of
``scripts/modal/app_v05.py`` (which imports ``modal`` at module top and so
cannot be tested), used for both Adamson and Norman.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass

import numpy as np

from perturb_eval.agentic_lifecycle.architect_dispatch import BackboneUnavailableError
from perturb_eval.backbones import (
    _REGISTRY,
    BackboneTrainConfig,
    available_backbones,
    build_backbone,
    count_fitted_params,
    mean_squared_deviation,
)
from perturb_eval.data import hvg as _hvg
from perturb_eval.experiments.errors import classify, transient_error_fields

DEFAULT_N_HVG = 2000


@dataclass(frozen=True)
class HeldOutView:
    """All cells of ``ds`` restricted to one task's train-only HVG columns."""

    held: str
    X: np.ndarray
    labels: np.ndarray
    control_mask: np.ndarray
    train_mask: np.ndarray
    train_targets: dict[str, tuple[int, ...]]
    held_target: tuple[int, ...]
    hvg: _hvg.HVGSelection
    eval_genes: np.ndarray  # full-axis columns, rank order (A2-5)
    eval_cols: np.ndarray  # the same genes as columns of ``X``


def task_eval_genes(ds: dict, held: str) -> np.ndarray:
    """The task's 20 evaluation genes on the dataset's full gene axis (A2-5)."""
    return _hvg.top_deg_columns(ds["X"], ds["labels"], ds["control_mask"], held)


def select_for_task(
    ds: dict, held: str, *, n_hvg: int | None = None, eval_genes: np.ndarray | None = None
) -> _hvg.HVGSelection:
    """Train-only HVG for ``held``: ranking over ``ds["labels"] != held`` rows,
    union every target column and the task's evaluation genes (A2-5;
    computed with :func:`task_eval_genes` when ``eval_genes`` is ``None``)."""
    if held not in ds["target_gene_idx"]:
        raise ValueError(
            f"held-out task {held!r} not in perturbations {sorted(ds['target_gene_idx'])}"
        )
    n = int(n_hvg if n_hvg is not None else ds.get("hvg_n_top", DEFAULT_N_HVG))
    train_mask = ds["labels"] != held
    if not train_mask.any():
        raise ValueError("empty training mask — dataset may be misformed")
    if eval_genes is None:
        eval_genes = task_eval_genes(ds, held)
    forced = set(_hvg.all_target_columns(ds["target_gene_idx"]))
    forced.update(int(i) for i in eval_genes)
    # Attribute lookup at call time so a test spy on the module is honoured.
    return _hvg.select_hvg_train_only(ds["X"], train_mask, n, force_include=sorted(forced))


def build_view(
    ds: dict, held: str, sel: _hvg.HVGSelection, eval_genes: np.ndarray | None = None
) -> HeldOutView:
    """Slice ``ds`` to ``sel``. Raises ``ValueError`` if an evaluation gene is
    not in the selection (never scored on a narrower gene set)."""
    if eval_genes is None:
        eval_genes = task_eval_genes(ds, held)
    eval_genes = np.asarray(eval_genes, dtype=np.int64)
    old_to_new = {int(old): new for new, old in enumerate(sel.indices.tolist())}
    missing = [int(g) for g in eval_genes if int(g) not in old_to_new]
    if missing:
        raise ValueError(f"evaluation gene column(s) not in the HVG selection: {missing}")
    targets = _hvg.remap_targets(ds["target_gene_idx"], sel.indices)
    return HeldOutView(
        held=held,
        X=np.asarray(ds["X"][:, sel.indices], dtype=np.float64),
        labels=ds["labels"],
        control_mask=ds["control_mask"],
        train_mask=ds["labels"] != held,
        train_targets={p: t for p, t in targets.items() if p != held},
        held_target=targets[held],
        hvg=sel,
        eval_genes=eval_genes,
        eval_cols=np.asarray([old_to_new[int(g)] for g in eval_genes], dtype=np.int64),
    )


def fit_and_score(view: HeldOutView, backbone_name: str, cfg: BackboneTrainConfig) -> dict:
    """Fit on the view's training rows, score the held-out task. Returns
    ``{msd_topk, backbone, n_params}``."""
    if backbone_name in _REGISTRY and backbone_name not in available_backbones():
        raise BackboneUnavailableError(
            f"backbone {backbone_name!r} is known but unavailable in this environment "
            f"(available: {sorted(available_backbones())})"
        )
    if backbone_name not in available_backbones():
        raise ValueError(
            f"unknown backbone {backbone_name!r}; available: {sorted(available_backbones())}"
        )
    bb = build_backbone(backbone_name)
    tm = view.train_mask
    bb.fit(
        view.X[tm], view.labels[tm].tolist(), view.control_mask[tm], view.train_targets, cfg
    )
    n_genes = view.X.shape[1]
    pred = bb.predict_logfc(view.held, view.held_target, n_genes=n_genes)
    truth = np.mean(view.X[view.labels == view.held], axis=0) - np.mean(
        view.X[view.control_mask], axis=0
    )
    return {
        "msd_topk": float(mean_squared_deviation(pred, truth, view.eval_cols)),
        "backbone": bb.name,
        "n_params": count_fitted_params(bb),
    }


def hvg_fields(sel: _hvg.HVGSelection) -> dict:
    """Provenance fields for one task's HVG selection."""
    return {"hvg_n": sel.n_hvg, "hvg_n_forced": int(sel.n_forced), "hvg_mode": sel.mode}


def eval_gene_fields(ds: dict, eval_genes: np.ndarray) -> dict:
    """Record fields for one task's evaluation genes (A2-5): full-axis indices
    and, when the loader carries ``gene_names``, the symbols."""
    idx = [int(g) for g in eval_genes]
    out: dict = {"eval_gene_idx": idx, "n_eval_genes": len(idx)}
    names = ds.get("gene_names")
    if names is not None:
        out["eval_genes"] = [str(names[i]) for i in idx]
    return out


# A2-4: backbones whose fit ignores both ``seed`` and ``max_iter`` (so R): every
# (R, seed) cell of such a backbone is the same fit. Pinned empirically by
# tests/test_prereg_a2_trainer.py.
R_SEED_INVARIANT_BACKBONES: frozenset[str] = frozenset({"linear"})


def trainer_config(R: int, seed: int) -> BackboneTrainConfig:
    """The trainer configuration of one grid cell: R sets the iteration budget."""
    return BackboneTrainConfig(max_iter=20 + 40 * R, learning_rate=1e-2, ridge_lambda=1.0,
                               seed=seed)


def trainer_grid(
    *, backbones: Iterable[str], r_sweep: Iterable[int], seeds: Iterable[int]
) -> dict:
    """The trainer grid as run (A2-4), for provenance and the paper.

    Per task, ``n_records_per_task`` = backbones x R x seeds cells are run;
    ``n_distinct_per_task`` counts the distinct fits among them (a backbone in
    :data:`R_SEED_INVARIANT_BACKBONES` contributes one). The H1/H2 oracle is
    the minimum over these distinct configurations.
    """
    backbones, r_sweep, seeds = list(backbones), list(r_sweep), list(seeds)
    per_bb = {
        b: 1 if b in R_SEED_INVARIANT_BACKBONES else len(set(r_sweep)) * len(set(seeds))
        for b in backbones
    }
    return {
        "backbones": backbones,
        "r_sweep": r_sweep,
        "seeds": seeds,
        "n_records_per_task": len(backbones) * len(r_sweep) * len(seeds),
        "n_distinct_per_task": sum(per_bb.values()),
        "distinct_by_backbone": per_bb,
        "r_seed_invariant_backbones": sorted(R_SEED_INVARIANT_BACKBONES & set(backbones)),
    }


def iter_trainer_records(
    *,
    dataset_name: str,
    ds: dict,
    tasks: Iterable[str],
    backbones: Iterable[str],
    r_sweep: Iterable[int],
    seeds: Iterable[int],
    n_hvg: int | None = None,
    should_stop: Callable[[], bool] | None = None,
) -> Iterator[dict]:
    """Yield one trainer-sweep JSONL record per (backbone, task, R, seed) cell.

    N is not an axis (amendment 2 A2-4); see :func:`trainer_grid`.

    Loop order and record shape match the former inline loop in
    ``app_v05.py``. Per-cell exceptions follow the CTO #245 Q1 taxonomy
    (:mod:`perturb_eval.experiments.errors`): only a TRANSIENT exception
    becomes an ``error`` record (``msd_topk = inf``, ``error_type``,
    ``error_class``, ``traceback``) and the loop continues; every other
    exception — programming, :class:`BackboneUnavailableError`, or anything
    unclassified — propagates and aborts the run, as does a task absent from
    ``target_gene_idx``. The evaluation genes and the HVG are
    selected once per held-out task (cached) and each record carries
    ``hvg_n``, ``hvg_n_forced``, ``hvg_mode``, ``eval_gene_idx``,
    ``n_eval_genes``, ``eval_genes`` (when named) and (on success) ``n_params``.
    Stops as soon as ``should_stop()`` is true.
    """
    tasks, r_sweep, seeds = list(tasks), list(r_sweep), list(seeds)
    evals: dict[str, np.ndarray] = {}
    selections: dict[str, _hvg.HVGSelection] = {}
    view: HeldOutView | None = None
    for backbone_name in backbones:
        for held in tasks:
            if held not in ds["target_gene_idx"]:
                # Preflight (T22) guarantees every task resolves; reaching
                # here mid-run is a bug, never a silent skip.
                raise ValueError(
                    f"{dataset_name}: task {held!r} has no entry in target_gene_idx"
                )
            for R in r_sweep:
                for seed in seeds:
                    if should_stop is not None and should_stop():
                        return
                    t0 = time.time()
                    base = {
                        "dataset": dataset_name, "task": held, "backbone": backbone_name,
                        "R": R, "seed": seed,
                    }
                    try:
                        if held not in evals:
                            evals[held] = task_eval_genes(ds, held)
                        if held not in selections:
                            selections[held] = select_for_task(
                                ds, held, n_hvg=n_hvg, eval_genes=evals[held]
                            )
                        if view is None or view.held != held:
                            view = build_view(ds, held, selections[held], evals[held])
                        out = fit_and_score(view, backbone_name, trainer_config(R, seed))
                        rec = {
                            **base,
                            "msd_topk": out["msd_topk"],
                            "wall_sec": time.time() - t0,
                            **hvg_fields(selections[held]),
                            **eval_gene_fields(ds, evals[held]),
                            "n_params": out["n_params"],
                        }
                    except BackboneUnavailableError:
                        raise  # C-TORCH-2: never an error record
                    except Exception as e:
                        if classify(e) != "transient":
                            raise  # CTO #245 Q1: default is ABORT
                        rec = {
                            **base,
                            "msd_topk": float("inf"),
                            **transient_error_fields(e),
                            "wall_sec": time.time() - t0,
                        }
                        if held in selections:
                            rec.update(hvg_fields(selections[held]))
                        if held in evals:
                            rec.update(eval_gene_fields(ds, evals[held]))
                    yield rec
