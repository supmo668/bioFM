"""In-process preflight for the v0.6 sweep (build-plan T22; C-KEY-1, C-TORCH-1/2).

:func:`preflight` runs every check the sweep depends on and raises ONE
:class:`PreflightError` listing ALL failures, before any trainer, lifecycle or
LLM work. There is no skip path: a missing ``OPENROUTER_API_KEY`` refuses the
whole run (CTO #235), it does not produce a trainer-only run.

Checks:

* C-KEY-1 — ``OPENROUTER_API_KEY`` present (presence only; the value is
  never logged, and is scrubbed from any error text) and a pool probe returns
  a usable model id.
* C-TORCH-1 — every backbone in ``kwargs["backbones"]`` is in
  :func:`available_backbones`, so the C-TORCH-2 raise is dead code in a
  healthy run.
* the output directory is empty (record 0 of each JSONL is this run's
  provenance).
* datasets load — the loaders passed in call the fetch path with
  ``trust_unpinned=False``; a fetch/digest error is a failure, not bypassed.
* the task plan builds — :func:`build_task_lists` asserts the stratum counts
  (T11); its error is reported here.
* every planned task resolves to target columns in its dataset
  (:func:`resolve_target_indices` against the dataset's gene vocabulary AND an
  entry in ``target_gene_idx``) — the sweep never skips a task.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Union

from perturb_eval.backbones import available_backbones
from perturb_eval.data.perturbations import resolve_target_indices
from perturb_eval.experiments.v05_tasks import TaskPlan

logger = logging.getLogger(__name__)

KEY_NAME = "OPENROUTER_API_KEY"

# Which dataset each TaskPlan pool is held out from (names as in app_v05).
TASK_POOL_DATASET: dict[str, str] = {
    "adamson": "adamson_full",
    "norman_singletons": "norman",
    "norman_doublets": "norman",
}

DatasetSource = Union[Mapping[str, Any], Callable[[], Mapping[str, Any]]]
PlanSource = Union[TaskPlan, Callable[[Mapping[str, Mapping[str, Any]]], TaskPlan]]
ProbeFn = Callable[[Mapping[str, str]], "str | None"]


class PreflightError(RuntimeError):
    """Every preflight failure, listed; raised before any GPU/model work."""

    def __init__(self, failures: list[str]) -> None:
        self.failures = list(failures)
        body = "\n".join(f"  - {f}" for f in self.failures)
        super().__init__(f"v0.6 preflight failed ({len(self.failures)} failure(s)):\n{body}")


@dataclass(frozen=True)
class PreflightReport:
    ok: bool
    task_plan: TaskPlan
    datasets: dict[str, Mapping[str, Any]]
    probe_model_id: str
    backbones: tuple[str, ...]
    checks: tuple[str, ...] = field(default_factory=tuple)


def openrouter_probe(env: Mapping[str, str]) -> str | None:
    """Default pool probe: ONE minimal chat through :class:`OpenRouterClient`.

    Uses a fresh temporary cache so a cached reply cannot fake a live pool.
    Returns the serving model id, or ``None`` when no model in the pool
    answers. Never called in tests (they inject a stub).
    """
    import tempfile

    import requests

    from perturb_eval.llm.openrouter_client import (
        DEFAULT_POOL,
        OpenRouterClient,
        OpenRouterError,
    )

    with tempfile.TemporaryDirectory(prefix="v06-preflight-") as tmp:
        client = OpenRouterClient(
            api_key=env[KEY_NAME], cache_dir=Path(tmp), pool=DEFAULT_POOL
        )
        try:
            res = client.chat_json(
                role="Validator",
                task_id="__preflight__",
                round_index=0,
                prompt='Reply with exactly this JSON object: {"ok": true}',
                seed=0,
            )
        except (OpenRouterError, requests.RequestException) as exc:
            logger.warning("preflight probe: no usable model (%s)", type(exc).__name__)
            return None
    return res.model_id or None


def _scrub(text: str, secret: str) -> str:
    return text.replace(secret, "<redacted>") if secret else text


def _describe(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {exc}"


def preflight(
    *,
    kwargs: Mapping[str, Any],
    datasets_spec_or_loaded: Mapping[str, DatasetSource],
    task_plan: PlanSource,
    env: Mapping[str, str],
    out_dir: Path | None = None,
    probe_fn: ProbeFn | None = None,
) -> PreflightReport:
    """Run every sweep precondition; raise one :class:`PreflightError` listing all failures.

    Parameters
    ----------
    kwargs
        The resolved ``run_v05_sweep`` kwargs (``backbones``, ``doublet_delim``).
    datasets_spec_or_loaded
        ``{dataset name: loaded ds dict | zero-arg loader}``. Loaders run here
        (they must fetch with ``trust_unpinned=False``); any exception is a
        reported failure.
    task_plan
        A :class:`TaskPlan`, or a callable ``(loaded datasets) -> TaskPlan``
        (normally wrapping :func:`build_task_lists`, whose stratum-count
        assertion is reused, not duplicated).
    env
        Environment mapping; only the PRESENCE of ``OPENROUTER_API_KEY`` is
        checked here, and the value is only handed to ``probe_fn``.
    out_dir
        ``/data/<version>/``; must be absent or empty.
    probe_fn
        ``env -> model_id | None``; defaults to :func:`openrouter_probe`.
    """
    failures: list[str] = []
    checks: list[str] = []
    secret = env.get(KEY_NAME) or ""

    # ---- C-KEY-1: key presence + pool probe --------------------------------
    probe_model_id = ""
    if not bool(env.get(KEY_NAME)):
        failures.append(
            f"C-KEY-1: {KEY_NAME} is not set (presence check); the lifecycle phase "
            "cannot run and a trainer-only run is not permitted (CTO #235)"
        )
    else:
        probe = probe_fn if probe_fn is not None else openrouter_probe
        try:
            got = probe(env)
        except Exception as exc:  # noqa: BLE001 — reported as a failure, never bypassed
            failures.append(
                f"C-KEY-1: OpenRouter pool probe raised: {_scrub(_describe(exc), secret)}"
            )
        else:
            if not got:
                failures.append("C-KEY-1: OpenRouter pool probe returned no usable model")
            else:
                probe_model_id = str(got)
                checks.append(f"pool probe ok ({probe_model_id})")

    # ---- C-TORCH-1: every sweep backbone is available ----------------------
    backbones = tuple(kwargs.get("backbones", ()))
    available = available_backbones()
    missing_bb = [b for b in backbones if b not in available]
    if not backbones:
        failures.append("C-TORCH-1: kwargs['backbones'] is empty")
    elif missing_bb:
        failures.append(
            f"C-TORCH-1: backbone(s) {missing_bb} not in available_backbones() "
            f"{sorted(available)} (scgpt_small needs torch importable)"
        )
    else:
        checks.append(f"backbones available: {list(backbones)}")

    # ---- output dir empty --------------------------------------------------
    if out_dir is not None:
        out = Path(out_dir)
        if out.exists() and (not out.is_dir() or any(out.iterdir())):
            entries = sorted(p.name for p in out.iterdir()) if out.is_dir() else [out.name]
            failures.append(
                f"output dir {out} is not empty ({entries}); use a new --version "
                "or move the old files aside"
            )
        else:
            checks.append(f"output dir empty: {out}")

    # ---- datasets (fetch with trust_unpinned=False happens in the loaders) --
    loaded: dict[str, Mapping[str, Any]] = {}
    for name, src in datasets_spec_or_loaded.items():
        if callable(src):
            try:
                loaded[name] = src()
            except Exception as exc:  # noqa: BLE001 — reported as a failure, never bypassed
                failures.append(f"dataset {name!r} failed to fetch/load: {_describe(exc)}")
                continue
        else:
            loaded[name] = src
        checks.append(f"dataset loaded: {name}")

    # ---- task plan (stratum counts asserted by build_task_lists) -----------
    plan: TaskPlan | None = None
    if isinstance(task_plan, TaskPlan):
        plan = task_plan
    elif len(loaded) != len(datasets_spec_or_loaded):
        failures.append("task plan not built: a dataset failed to load (see above)")
    else:
        try:
            plan = task_plan(loaded)
        except Exception as exc:  # noqa: BLE001 — reported as a failure, never bypassed
            failures.append(f"task plan build failed: {_describe(exc)}")

    # ---- every task resolves in its dataset --------------------------------
    if plan is not None:
        delim = str(kwargs.get("doublet_delim", "_"))
        for pool_name, ds_name in TASK_POOL_DATASET.items():
            tasks = tuple(getattr(plan, pool_name))
            if not tasks:
                continue
            ds = loaded.get(ds_name)
            if ds is None:
                if ds_name in datasets_spec_or_loaded:
                    continue  # its load failure is already listed
                failures.append(
                    f"task plan has {len(tasks)} {pool_name} task(s) but dataset "
                    f"{ds_name!r} is not in the sweep"
                )
                continue
            failures.extend(_unresolved_tasks(ds_name, pool_name, tasks, ds, delim))
        if not plan.all_tasks:
            failures.append("task plan is empty")

    if failures:
        raise PreflightError([_scrub(f, secret) for f in failures])

    assert plan is not None
    for c in checks:
        logger.info("preflight ok: %s", c)
    return PreflightReport(
        ok=True,
        task_plan=plan,
        datasets=loaded,
        probe_model_id=probe_model_id,
        backbones=backbones,
        checks=tuple(checks),
    )


def _unresolved_tasks(
    ds_name: str,
    pool_name: str,
    tasks: tuple[str, ...],
    ds: Mapping[str, Any],
    delim: str,
) -> list[str]:
    """One failure line per task that does not resolve to target columns in ``ds``."""
    out: list[str] = []
    tgi = ds.get("target_gene_idx", {})
    genes = ds.get("gene_names")
    gene_to_idx = {str(g): i for i, g in enumerate(genes)} if genes is not None else None
    for task in tasks:
        if gene_to_idx is not None:
            try:
                resolved = resolve_target_indices([task], gene_to_idx, delim=delim)
            except ValueError as exc:
                out.append(f"{ds_name}/{pool_name}: task {task!r} does not resolve: {exc}")
                continue
            if task not in resolved:
                out.append(
                    f"{ds_name}/{pool_name}: task {task!r} is a control label, not a target"
                )
                continue
        if task not in tgi:
            out.append(
                f"{ds_name}/{pool_name}: task {task!r} has no entry in the dataset's "
                "target_gene_idx (the trainer and lifecycle would have nothing to hold out)"
            )
    return out


__all__ = [
    "KEY_NAME",
    "PreflightError",
    "PreflightReport",
    "TASK_POOL_DATASET",
    "openrouter_probe",
    "preflight",
]
