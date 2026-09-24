"""Per-held-out-task training on real data with train-only HVG (T8b, CTO #227).

The loaders return the FULL gene vocabulary (raw matrix only, never a feature
selection). For each held-out perturbation this module:

1. selects HVG with :func:`perturb_eval.data.hvg.select_hvg_train_only` over
   ``labels != held`` (controls stay in the training rows, as before), forcing
   in every perturbation's target columns;
2. slices all cells to those columns (float64) and remaps targets;
3. fits a backbone on the training rows and scores the held-out perturbation
   on its top-20 DEGs (unchanged, CTO out-of-scope item).

:func:`iter_trainer_records` is the v0.5 trainer-sweep loop body moved out of
``scripts/modal/app_v05.py`` (which imports ``modal`` at module top and so
cannot be tested), used for both Adamson and Norman.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass

import numpy as np

from perturb_eval.backbones import (
    BackboneTrainConfig,
    available_backbones,
    build_backbone,
    count_fitted_params,
    mean_squared_deviation,
)
from perturb_eval.data import hvg as _hvg

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


def select_for_task(ds: dict, held: str, *, n_hvg: int | None = None) -> _hvg.HVGSelection:
    """Train-only HVG for ``held``: ranking over ``ds["labels"] != held`` rows."""
    if held not in ds["target_gene_idx"]:
        raise ValueError(
            f"held-out task {held!r} not in perturbations {sorted(ds['target_gene_idx'])}"
        )
    n = int(n_hvg if n_hvg is not None else ds.get("hvg_n_top", DEFAULT_N_HVG))
    train_mask = ds["labels"] != held
    if not train_mask.any():
        raise ValueError("empty training mask — dataset may be misformed")
    # Attribute lookup at call time so a test spy on the module is honoured.
    return _hvg.select_hvg_train_only(
        ds["X"], train_mask, n, force_include=_hvg.all_target_columns(ds["target_gene_idx"])
    )


def build_view(ds: dict, held: str, sel: _hvg.HVGSelection) -> HeldOutView:
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
    )


def fit_and_score(view: HeldOutView, backbone_name: str, cfg: BackboneTrainConfig) -> dict:
    """Fit on the view's training rows, score the held-out task. Returns
    ``{msd_topk, backbone, n_params}``."""
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
    top_k = np.argsort(-np.abs(truth))[:20]
    return {
        "msd_topk": float(mean_squared_deviation(pred, truth, top_k)),
        "backbone": bb.name,
        "n_params": count_fitted_params(bb),
    }


def hvg_fields(sel: _hvg.HVGSelection) -> dict:
    """Provenance fields for one task's HVG selection."""
    return {"hvg_n": sel.n_hvg, "hvg_n_forced": int(sel.n_forced), "hvg_mode": sel.mode}


def iter_trainer_records(
    *,
    dataset_name: str,
    ds: dict,
    tasks: Iterable[str],
    backbones: Iterable[str],
    n_sweep: Iterable[int],
    r_sweep: Iterable[int],
    seeds: Iterable[int],
    n_hvg: int | None = None,
    should_stop: Callable[[], bool] | None = None,
) -> Iterator[dict]:
    """Yield one trainer-sweep JSONL record per (backbone, task, N, R, seed) cell.

    Loop order and record shape match the former inline loop in
    ``app_v05.py``; per-cell exceptions become ``error`` records. HVG is
    selected once per held-out task (cached) and each record carries
    ``hvg_n``, ``hvg_n_forced``, ``hvg_mode`` and (on success) ``n_params``.
    Stops as soon as ``should_stop()`` is true.
    """
    tasks, n_sweep, r_sweep, seeds = list(tasks), list(n_sweep), list(r_sweep), list(seeds)
    selections: dict[str, _hvg.HVGSelection] = {}
    view: HeldOutView | None = None
    for backbone_name in backbones:
        for held in tasks:
            if held not in ds["target_gene_idx"]:
                continue
            for N in n_sweep:
                for R in r_sweep:
                    for seed in seeds:
                        if should_stop is not None and should_stop():
                            return
                        t0 = time.time()
                        base = {
                            "dataset": dataset_name, "task": held, "backbone": backbone_name,
                            "N": N, "R": R, "seed": seed,
                        }
                        try:
                            if held not in selections:
                                selections[held] = select_for_task(ds, held, n_hvg=n_hvg)
                            if view is None or view.held != held:
                                view = build_view(ds, held, selections[held])
                            out = fit_and_score(
                                view,
                                backbone_name,
                                BackboneTrainConfig(
                                    max_iter=20 + 40 * R,
                                    learning_rate=1e-2,
                                    ridge_lambda=1.0,
                                    seed=seed,
                                ),
                            )
                            rec = {
                                **base,
                                "msd_topk": out["msd_topk"],
                                "wall_sec": time.time() - t0,
                                **hvg_fields(selections[held]),
                                "n_params": out["n_params"],
                            }
                        except Exception as e:  # noqa: BLE001 — recorded, as before
                            rec = {
                                **base,
                                "msd_topk": float("inf"),
                                "error": f"{type(e).__name__}: {e}",
                                "wall_sec": time.time() - t0,
                            }
                            if held in selections:
                                rec.update(hvg_fields(selections[held]))
                        yield rec
