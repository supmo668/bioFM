"""The v0.6 sweep's testable pieces (build-plan T6; QG C14, C22, OWN-1).

``scripts/modal/app_v05.py`` imports ``modal`` at module top and so cannot be
imported by tests; everything it decides lives here instead:

* :func:`lifecycle_record` / :func:`iter_lifecycle_records` — the lifecycle
  loop body (``seed`` and ``dataset`` are passed to
  :func:`run_agentic_lifecycle`, which requires both);
* :func:`spend_guard` — the CTO #283 spend stop ($12, stop-and-report) and the
  $28 hard kill, used as the loops' ``should_stop``;
* :func:`derive_status` / :func:`provenance_entropies` — the ONE producer of
  the final provenance status and of its entropy figures (LLM-sourced steps
  only, via the analyser's own function);
* :func:`validate_version` / :func:`version_out_dir` — ``--version`` is a
  release tag and the output dir stays under ``/data``;
* :data:`LIFECYCLE_N_ROUNDS` — amendment 2 (A2-2): every lifecycle run is
  exactly three rounds, no early stop;
* :func:`llm_cache_start` / :func:`llm_cache_end` — amendment 2 (A2-8): the
  version-namespaced LLM cache, its entry count at start (must be 0) and the
  run's cache-hit count (must be 0); otherwise the run is a replay.
"""

from __future__ import annotations

import re
import time
from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import asdict
from pathlib import Path
from typing import Any, Literal

from perturb_eval.agentic_lifecycle.architect_dispatch import BackboneUnavailableError
from perturb_eval.agentic_lifecycle.loop import run_agentic_lifecycle
from perturb_eval.experiments.errors import classify, transient_error_fields
from perturb_eval.llm.openrouter_client import (
    PREREG_VERSION,
    count_cache_entries,
    versioned_cache_dir,
)

# A2-2: every pre-registered lifecycle run executes exactly this many rounds.
LIFECYCLE_N_ROUNDS = 3


def _require_three_rounds(max_rounds: int) -> None:
    if max_rounds != LIFECYCLE_N_ROUNDS:
        raise ValueError(
            f"max_rounds={max_rounds}: amendment 2 (A2-2) fixes every lifecycle run at "
            f"exactly {LIFECYCLE_N_ROUNDS} rounds (three rounds, no early stop)"
        )


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
    ``lifecycle_kwargs`` are forwarded to it; ``max_rounds`` is
    :data:`LIFECYCLE_N_ROUNDS` and any other value is refused (A2-2). The record is ``asdict(run)`` plus ``dataset``, ``seed``
    and ``wall_sec``; a run that carried a transient trainer failure has its
    ``error_fields`` flattened into the record (``error``, ``error_type``,
    ``error_class``, ``traceback``) so the analyser counts it as an error
    record (QG C4).
    """
    fn = run_fn or run_agentic_lifecycle
    lifecycle_kwargs.setdefault("max_rounds", LIFECYCLE_N_ROUNDS)
    _require_three_rounds(lifecycle_kwargs["max_rounds"])
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
        dataset=dataset_name,
        **lifecycle_kwargs,
    )
    rec = asdict(run)
    error_fields = rec.pop("error_fields", None) or {}
    # A2-5: the same eval-gene fields (indices, count, symbols when the loader
    # has gene names) as the trainer record for this task.
    if rec.get("eval_gene_idx"):
        from perturb_eval.experiments.heldout import eval_gene_fields

        rec.update(eval_gene_fields(ds, rec["eval_gene_idx"]))
    return (
        rec
        | dict(error_fields)
        | {
            "dataset": dataset_name,
            "seed": seed,
            "wall_sec": time.time() - t0,
        }
    )


def iter_lifecycle_records(
    *,
    datasets: Iterable[tuple[str, dict, Iterable[str]]],
    seeds: Iterable[int],
    pool: Any,
    max_rounds: int = LIFECYCLE_N_ROUNDS,
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
    _require_three_rounds(max_rounds)  # A2-2
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
                    rec = fn(
                        task=held,
                        dataset_name=dataset_name,
                        ds=ds,
                        seed=seed,
                        pool=pool,
                        max_rounds=max_rounds,
                    )
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


# ---------------------------------------------------------------------------
# Spend guard (CTO #283 condition 3; gate finding OWN-1)
# ---------------------------------------------------------------------------

SpendAction = Literal["spend_stop", "hard_kill"]


def spend_guard(cost_usd: float, *, stop_usd: float, kill_usd: float) -> SpendAction | None:
    """``None`` while ``cost_usd <= stop_usd``; ``"spend_stop"`` once it passes
    ``stop_usd`` (stop and report); ``"hard_kill"`` once it passes ``kill_usd``.
    Both boundaries are strict (``>``): spend exactly at a limit does not trip it.
    """
    if stop_usd > kill_usd:
        raise ValueError(f"spend stop ${stop_usd} is above the hard kill ${kill_usd}")
    if cost_usd > kill_usd:
        return "hard_kill"
    if cost_usd > stop_usd:
        return "spend_stop"
    return None


# ---------------------------------------------------------------------------
# Final status + entropies: one producer (QG C14)
# ---------------------------------------------------------------------------


def _steps(records: Iterable[Mapping[str, Any]]) -> Iterator[Mapping[str, Any]]:
    for rec in records:
        if not isinstance(rec, Mapping) or rec.get("record_type") == "provenance":
            continue
        for st in rec.get("steps") or ():
            if isinstance(st, Mapping):
                yield st


def derive_status(
    lifecycle_records: Iterable[Mapping[str, Any]],
    *,
    cost_usd: float,
    kill_usd: float,
    stop_reason: str | None = None,
    llm_cache_entries_at_start: int | None = None,
) -> str:
    """Final provenance ``status`` of a sweep that ran to its end or was stopped.

    ``"failed_fallback"`` if any lifecycle step is a fallback (C-KEY-2; beats
    everything else); else ``"partial"`` if the sweep was stopped
    (``stop_reason``, e.g. the $12 spend stop) or spent strictly more than
    ``kill_usd``; else, when the cache info is given
    (``llm_cache_entries_at_start``, amendment 2 A2-8), ``"replay"`` if the
    version-namespaced cache was non-empty at start or any LLM-sourced step was
    served from the cache (:func:`llm_cache_end`); else ``"ok"``. Without the
    cache info the replay check is skipped (the original signature). Transient
    per-cell error records do not change the status: the analyser refuses them
    on its own (CTO #245 Q1).
    """
    records = list(lifecycle_records)
    if any(st.get("source") == "fallback" for st in _steps(records)):
        return "failed_fallback"
    if stop_reason is not None or cost_usd > kill_usd:
        return "partial"
    if (
        llm_cache_entries_at_start is not None
        and llm_cache_end(records, entries_at_start=llm_cache_entries_at_start)["replay"]
    ):
        return "replay"
    return "ok"


def provenance_entropies(lifecycle_records: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """The provenance ``entropies`` block, computed by the analyser's own
    LLM-only function (:func:`e_v05_real_traces.architect_entropies`): ``None``
    (never ``0.0``) when no LLM-sourced Architect step carries the field."""
    from perturb_eval.experiments.e_v05_real_traces import architect_entropies

    rows = [
        r
        for r in lifecycle_records
        if isinstance(r, Mapping) and r.get("record_type") != "provenance"
    ]
    return architect_entropies(rows)


# ---------------------------------------------------------------------------
# LLM cache namespace (amendment 2, A2-8)
# ---------------------------------------------------------------------------


def llm_cache_start(cache_root: str | Path, prereg_version: str = PREREG_VERSION) -> dict[str, Any]:
    """Provenance block recorded at sweep start: the version, the namespace the
    client must use (``<cache_root>/<prereg_version>``) and its entry count,
    which for the pre-registered run must be 0 (recorded, not refused: a
    non-zero start makes the run a replay, see :func:`llm_cache_end`)."""
    ns = versioned_cache_dir(cache_root, prereg_version)
    return {
        "prereg_version": prereg_version,
        "llm_cache_namespace": str(ns),
        "llm_cache_entries_at_start": count_cache_entries(ns),
    }


def llm_cache_end(
    lifecycle_records: Iterable[Mapping[str, Any]], *, entries_at_start: int
) -> dict[str, Any]:
    """Provenance block recorded at sweep end: the number of LLM-sourced steps
    served from the cache (must be 0) and whether the run is a REPLAY (a
    non-empty namespace at start, or any cache hit), with the reasons."""
    hits = sum(
        1
        for st in _steps(lifecycle_records)
        if st.get("source") == "llm" and st.get("cache_hit") is True
    )
    reasons: list[str] = []
    if entries_at_start:
        reasons.append(f"LLM cache namespace held {entries_at_start} entries at start (must be 0)")
    if hits:
        reasons.append(f"{hits} LLM step(s) served from the cache (must be 0)")
    return {"llm_cache_hit_count": hits, "replay": bool(reasons), "replay_reasons": reasons}


# ---------------------------------------------------------------------------
# --version -> output dir (QG C22)
# ---------------------------------------------------------------------------

VERSION_RE = re.compile(r"^v\d+\.\d+\.\d+[A-Za-z0-9._-]*$")
DATA_ROOT = Path("/data")


# Amendment 4 (A4-1 / A4-2) pins for the pre-registered version: Haiku sampling and the
# spend carried in from the aborted run (1.3) plus the authorised dry runs (0.0548).
PREREGISTERED_VERSION = "v0.6.0"
PREREGISTERED_TEMPERATURE = 0.3
PREREGISTERED_PRIOR_SPEND_USD = 1.3548


def validate_pinned_run_params(version: str, *, temperature: float, prior_spend_usd: float) -> None:
    """Refuse a pre-registered run whose pinned parameters differ from amendment 4 (QG-4, QG-6)."""
    if version != PREREGISTERED_VERSION:
        return
    if abs(float(temperature) - PREREGISTERED_TEMPERATURE) > 1e-12:
        raise ValueError(
            f"A4-1 pins Haiku temperature at {PREREGISTERED_TEMPERATURE} for {version}; got {temperature}"
        )
    if float(prior_spend_usd) + 1e-9 < PREREGISTERED_PRIOR_SPEND_USD:
        raise ValueError(
            f"A4-2 carries in prior spend of at least ${PREREGISTERED_PRIOR_SPEND_USD} for {version}; "
            f"got {prior_spend_usd}"
        )


def validate_version(version: str) -> str:
    """Return ``version`` if it is a release tag (``v<maj>.<min>.<patch>[suffix]``,
    suffix ``[A-Za-z0-9._-]``); raise ``ValueError`` otherwise."""
    if not isinstance(version, str) or not VERSION_RE.fullmatch(version):
        raise ValueError(f"--version {version!r} must match {VERSION_RE.pattern} (e.g. v0.6.0)")
    return version


def version_out_dir(version: str, *, root: Path = DATA_ROOT) -> Path:
    """``<root>/<version>`` after :func:`validate_version`; refuses any result
    that does not resolve to a direct child of ``root``."""
    validate_version(version)
    base = Path(root).resolve()
    out = (base / version).resolve()
    if out.parent != base:
        raise ValueError(f"--version {version!r} resolves outside {base}: {out}")
    return out
