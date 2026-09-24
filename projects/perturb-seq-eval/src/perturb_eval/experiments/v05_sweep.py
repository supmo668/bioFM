"""One v0.5 lifecycle-sweep iteration as a testable function (build-plan T6).

Moved verbatim from the lifecycle loop in ``scripts/modal/app_v05.py`` (which
imports ``modal`` at module top and so cannot be imported by tests), with one
change: ``seed`` is now passed to :func:`run_agentic_lifecycle`, which requires
it (T5), instead of only being written into the record.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import asdict
from typing import Any

from perturb_eval.agentic_lifecycle.loop import run_agentic_lifecycle


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
