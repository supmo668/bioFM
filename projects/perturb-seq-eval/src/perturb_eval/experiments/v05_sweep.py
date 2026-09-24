"""One v0.5 lifecycle-sweep iteration as a testable function (build-plan T6).

Moved verbatim from the lifecycle loop in ``scripts/modal/app_v05.py`` (which
imports ``modal`` at module top and so cannot be imported by tests), with one
change: ``seed`` is now passed to :func:`run_agentic_lifecycle`, which requires
it (T5), instead of only being written into the record.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable, Iterator
from dataclasses import asdict
from typing import Any

from perturb_eval.agentic_lifecycle.architect_dispatch import BackboneUnavailableError
from perturb_eval.agentic_lifecycle.loop import run_agentic_lifecycle
from perturb_eval.experiments.errors import classify, transient_error_fields


def lifecycle_record(
    *,
    task: str,
    dataset_name: str,
    ds: dict,
    seed: int,
    pool: Any,
    run_fn: Callable[..., Any] | None = None,
    **lifecycle_kwargs: Any,
) -> dict:
    """Run one agentic lifecycle for ``task`` on ``ds`` and return its JSONL record.

    ``run_fn`` defaults to :func:`run_agentic_lifecycle` (injectable for tests).
    ``lifecycle_kwargs`` are forwarded to it; ``max_rounds`` defaults to 3 as in
    the v0.5 sweep. The record is ``asdict(run)`` plus ``dataset``, ``seed``
    and ``wall_sec``.
    """
    fn = run_fn or run_agentic_lifecycle
    lifecycle_kwargs.setdefault("max_rounds", 3)
    t0 = time.time()
    run = fn(
        task_id=task,
        X=ds["X"],
        labels=ds["labels"],
        control_mask=ds["control_mask"],
        target_gene_idx=ds["target_gene_idx"],
        held_out=task,
        agent_pool=pool,
        seed=seed,
        **lifecycle_kwargs,
    )
    return asdict(run) | {
        "dataset": dataset_name,
        "seed": seed,
        "wall_sec": time.time() - t0,
    }


def iter_lifecycle_records(
    *,
    datasets: Iterable[tuple[str, dict, Iterable[str]]],
    seeds: Iterable[int],
    pool: Any,
    max_rounds: int = 3,
    should_stop: Callable[[], bool] | None = None,
    record_fn: Callable[..., dict] | None = None,
) -> Iterator[dict]:
    """Yield one lifecycle-sweep JSONL record per ``(dataset, task, seed)``.

    The v0.6 lifecycle loop moved out of ``scripts/modal/app_v05.py`` so the
    CTO #245 Q1 taxonomy is testable: a TRANSIENT exception becomes an error
    record (``final_msd_topk = inf``, ``error_type``, ``error_class``,
    ``traceback``) and the loop continues; anything else — programming,
    :class:`BackboneUnavailableError` (C-TORCH-2), unclassified — propagates.
    A task absent from ``target_gene_idx`` raises (preflight guarantees it
    resolves; never a skip). Stops as soon as ``should_stop()`` is true.
    ``record_fn`` defaults to :func:`lifecycle_record` (injectable for tests).
    """
    fn = record_fn or lifecycle_record
    seeds = list(seeds)
    for dataset_name, ds, tasks in datasets:
        for held in tasks:
            if held not in ds["target_gene_idx"]:
                raise RuntimeError(
                    f"{dataset_name}: task {held!r} not in target_gene_idx mid-run "
                    "(preflight should have refused this run)"
                )
            for seed in seeds:
                if should_stop is not None and should_stop():
                    return
                t0 = time.time()
                try:
                    rec = fn(task=held, dataset_name=dataset_name, ds=ds, seed=seed,
                             pool=pool, max_rounds=max_rounds)
                except BackboneUnavailableError:
                    raise  # C-TORCH-2: never a per-record error / silent gap
                except Exception as e:
                    if classify(e) != "transient":
                        raise  # CTO #245 Q1: default is ABORT
                    rec = {
                        "dataset": dataset_name,
                        "task_id": held,
                        "seed": seed,
                        **transient_error_fields(e),
                        "final_msd_topk": float("inf"),
                        "n_rounds": 0,
                        "wall_sec": time.time() - t0,
                        "steps": [],
                    }
                yield rec


def run_guarded(
    records: Iterable[dict],
    *,
    sink: Callable[[dict], None],
    on_abort: Callable[[BaseException], None],
) -> int:
    """Drain ``records`` into ``sink``; on any exception call ``on_abort(exc)``
    (which finalises provenance as ``failed``) and re-raise. Returns the count."""
    n = 0
    try:
        for rec in records:
            sink(rec)
            n += 1
    except Exception as exc:
        on_abort(exc)
        raise
    return n
