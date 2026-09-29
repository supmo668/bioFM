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
* C-KEY-SOURCE — ``kwargs["llm_key_source"]`` (parsed on the host from
  ``OPENROUTER_KEY_SOURCE``) is present: provenance records WHERE the credential
  came from (principal directive 2026-09-24).
* C-PREREG — ``kwargs["preregistration"]`` (the committed, clean
  pre-registration pin) is present; ``kwargs["preregistration_error"]`` says
  why not (CTO #265).
* C-DESIGN (QG C12) — a PRE-REGISTERED version (:data:`PREREGISTERED_VERSIONS`)
  runs the pre-registered design only: ``max_tasks_override``,
  ``include_norman=False`` and ``include_adamson=False`` are refused.
* the output directory is empty (record 0 of each JSONL is this run's
  provenance).
* datasets load — the loaders passed in call the fetch path with
  ``trust_unpinned=False``; a fetch/digest error is a failure, not bypassed.
* the task plan builds — :func:`build_task_lists` asserts the stratum counts
  (T11); its error is reported here.
* every planned task resolves to target columns in its dataset
  (:func:`resolve_target_indices` against the dataset's gene vocabulary AND an
  entry in ``target_gene_idx``) — the sweep never skips a task. The gene
  lookup applies the dataset's ``label_contract`` aliases per component
  (CTO #250); a task that the contract EXCLUDED is a failure.

The report carries each dataset's ``label_contract`` provenance and every
``labels_excluded`` entry tagged with its dataset, for the provenance record.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Union

from perturb_eval.backbones import available_backbones
from perturb_eval.data.label_contract import gene_label_from_provenance
from perturb_eval.data.perturbations import resolve_target_indices
from perturb_eval.experiments.v05_tasks import TaskPlan

logger = logging.getLogger(__name__)

KEY_NAME = "OPENROUTER_API_KEY"

# Versions whose design is fixed by paper/PREREGISTRATION.md (QG C12).
PREREGISTERED_VERSIONS: frozenset[str] = frozenset({"v0.6.0"})
PREREGISTERED_DESIGN = (
    "41 = 21 + 15 + 5 tasks (21 Adamson = 3 |logFC| bins x 7, 15 Norman singletons, "
    "5 Norman doublets), both datasets"
)

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
    # CTO #467: every roster model probed; {model_id: {live, verdict, probed_at}}.
    roster_liveness: dict[str, dict[str, Any]] = field(default_factory=dict)
    # CTO #250: {dataset: label_contract provenance} and
    # ({"dataset", "label", "reason"}, ...) for provenance.tasks_excluded.
    label_contracts: dict[str, Mapping[str, Any]] = field(default_factory=dict)
    labels_excluded: tuple[dict[str, Any], ...] = field(default_factory=tuple)


PROBE_PROMPT = (
    "Reply with ONLY this JSON object and nothing else: "
    '{"confidence": 0.5, "dynamic_threshold_msd": 0.1}'
)


def openrouter_probe_all(env: Mapping[str, str]) -> dict[str, dict[str, Any]]:
    """Probe EVERY roster model with the Validator JSON schema (CTO #467).

    One direct call per model (no failover, fresh temporary cache so a cached
    reply cannot fake a live model). A model is live only when it answers a
    JSON object that ``parse_proposal("Validator", ...)`` accepts (A2-1, A3-3).
    Returns ``{model_id: {"live", "verdict", "probed_at"}}``. Never prints the key.
    """
    import datetime as _dt
    import tempfile

    import requests
    from pydantic import ValidationError

    from perturb_eval.agentic_lifecycle.proposal_schema import parse_proposal
    from perturb_eval.llm.openrouter_client import DEFAULT_POOL, OpenRouterClient

    table: dict[str, dict[str, Any]] = {}
    with tempfile.TemporaryDirectory(prefix="v06-preflight-") as tmp:
        client = OpenRouterClient(api_key=env[KEY_NAME], cache_dir=Path(tmp), pool=DEFAULT_POOL)
        for m in DEFAULT_POOL.models:
            probed_at = _dt.datetime.now(_dt.timezone.utc).isoformat()
            try:
                live, verdict, parsed = client.probe_model(m.model_id, PROBE_PROMPT)
            except requests.RequestException as exc:
                live, verdict, parsed = False, f"transport {type(exc).__name__}", None
            if live:
                try:
                    parse_proposal("Validator", parsed)
                except ValidationError:
                    live, verdict = False, "JSON answered but Validator schema failed"
            table[m.model_id] = {"live": bool(live), "verdict": verdict, "probed_at": probed_at}
    return table


def openrouter_probe(env: Mapping[str, str]) -> str | None:
    """Legacy single-model probe: the first live model of :func:`openrouter_probe_all`."""
    live = [k for k, v in openrouter_probe_all(env).items() if v["live"]]
    return live[0] if live else None


def _check_roster_liveness(got: Any, pool: Any) -> tuple[str, dict[str, dict[str, Any]], list[str]]:
    """CTO #467: the probe must cover EVERY roster model; every role needs >= 2
    live preferred models; returns (probe_model_id, normalised table, failures)."""
    import datetime as _dt

    from perturb_eval.llm.openrouter_client import DEFAULT_POOL

    pool = pool if pool is not None else DEFAULT_POOL
    expected = [m.model_id for m in pool.models]
    failures: list[str] = []
    if isinstance(got, str):  # legacy single-id probe
        now = _dt.datetime.now(_dt.timezone.utc).isoformat()
        got = {got: {"live": True, "verdict": "legacy single probe", "probed_at": now}}
    if not isinstance(got, Mapping):
        got = {}
    table: dict[str, dict[str, Any]] = {}
    for mid in expected:
        e = got.get(mid)
        if isinstance(e, Mapping):
            table[mid] = {
                "live": bool(e.get("live")),
                "verdict": str(e.get("verdict", "")),
                "probed_at": str(e.get("probed_at", "")),
            }
    unprobed = [mid for mid in expected if mid not in table]
    if unprobed:
        failures.append(
            f"C-KEY-1: preflight probed {len(table)} of {len(expected)} roster models; "
            f"unprobed: {unprobed} (every roster model must be probed, CTO #467)"
        )
    live = {mid for mid, e in table.items() if e["live"]}
    if not live:
        failures.append("C-KEY-1: OpenRouter pool probe returned no usable model")
    for role, prefs in pool.role_preferences.items():
        n = sum(1 for mid in prefs if mid in live)
        if n < 2:
            failures.append(
                f"C-KEY-1: role {role} has {n} live preferred model(s) (< 2): "
                f"{[(mid, table.get(mid, {}).get('verdict', 'unprobed')) for mid in prefs]}"
            )
    probe_model_id = ""
    if live:
        order = list(pool.role_preferences.get("Validator", ())) + expected
        probe_model_id = next(mid for mid in order if mid in live)
    return probe_model_id, table, failures


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
    pool: Any = None,
) -> PreflightReport:
    """Run every sweep precondition; raise one :class:`PreflightError` listing all failures.

    Parameters
    ----------
    kwargs
        The resolved ``run_v05_sweep`` kwargs (``backbones``, ``doublet_delim``,
        ``llm_key_source``, ``preregistration``, ``preregistration_error``).
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
    liveness: dict[str, dict[str, Any]] = {}
    if not bool(env.get(KEY_NAME)):
        failures.append(
            f"C-KEY-1: {KEY_NAME} is not set (presence check); the lifecycle phase "
            "cannot run and a trainer-only run is not permitted (CTO #235)"
        )
    else:
        probe = probe_fn if probe_fn is not None else openrouter_probe_all
        try:
            got = probe(env)
        except Exception as exc:  # noqa: BLE001 — reported as a failure, never bypassed
            failures.append(
                f"C-KEY-1: OpenRouter pool probe raised: {_scrub(_describe(exc), secret)}"
            )
        else:
            probe_model_id, liveness, probe_failures = _check_roster_liveness(got, pool)
            failures.extend(probe_failures)
            if probe_model_id:
                n_live = sum(1 for e in liveness.values() if e["live"])
                checks.append(
                    f"pool probe ok ({probe_model_id}; {n_live}/{len(liveness)} roster models live)"
                )

    # ---- C-KEY-SOURCE / C-PREREG: principal directive + CTO #265 ----------
    key_source = kwargs.get("llm_key_source")
    if not isinstance(key_source, Mapping) or not key_source:
        failures.append(
            "C-KEY-SOURCE: OPENROUTER_KEY_SOURCE not set; provenance must record where "
            "the credential came from (principal directive 2026-09-24)"
        )
    else:
        checks.append(
            f"key source recorded: {key_source.get('store')}:{key_source.get('project_slug')}"
            f":{key_source.get('env')}"
        )
    prereg = kwargs.get("preregistration")
    if not isinstance(prereg, Mapping) or not prereg:
        reason = kwargs.get("preregistration_error") or "no pre-registration record"
        failures.append(
            f"C-PREREG: pre-registration not committed/clean ({reason}) — a hypothesis "
            "fixed after the sweep is not a pre-registration (CTO #265)"
        )
    else:
        checks.append(f"pre-registration pinned: {prereg.get('path')} @ {prereg.get('commit')}")

    # ---- C-DESIGN (QG C12): a pre-registered version runs the full design ----
    version = kwargs.get("version")
    if version in PREREGISTERED_VERSIONS:
        shrink = [
            f"{k}={kwargs.get(k)!r}"
            for k, bad in (
                ("max_tasks_override", kwargs.get("max_tasks_override") is not None),
                ("include_norman", kwargs.get("include_norman", True) is False),
                ("include_adamson", kwargs.get("include_adamson", True) is False),
            )
            if bad
        ]
        if shrink:
            failures.append(
                f"C-DESIGN: version {version!r} is pre-registered; its design is "
                f"{PREREGISTERED_DESIGN}. Refusing {', '.join(shrink)} — a smaller run "
                "must use a non-pre-registered --version (e.g. v0.6.0-smoke)"
            )
        else:
            checks.append(f"pre-registered design unshrunk for {version}")

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
    label_contracts = {
        name: ds["label_contract"] for name, ds in loaded.items() if "label_contract" in ds
    }
    # CTO #253: raw_labels / n_cells (when the loader records them) pass through.
    labels_excluded = tuple(
        {**dict(e), "dataset": name, "label": str(e["label"]), "reason": str(e["reason"])}
        for name, ds in loaded.items()
        for e in ds.get("labels_excluded", ())
    )
    for c in checks:
        logger.info("preflight ok: %s", c)
    return PreflightReport(
        ok=True,
        task_plan=plan,
        datasets=loaded,
        probe_model_id=probe_model_id,
        backbones=backbones,
        checks=tuple(checks),
        roster_liveness=liveness,
        label_contracts=label_contracts,
        labels_excluded=labels_excluded,
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
    contract = ds.get("label_contract")
    excluded = {str(e["label"]): str(e["reason"]) for e in ds.get("labels_excluded", ())}
    for task in tasks:
        if task in excluded:
            out.append(
                f"{ds_name}/{pool_name}: task {task!r} is excluded by the label contract "
                f"({excluded[task]}); it must never be drawn"
            )
            continue
        if gene_to_idx is not None:
            try:
                gene_task = (
                    gene_label_from_provenance(task, contract, delim)
                    if contract is not None
                    else task
                )
                resolved = resolve_target_indices([gene_task], gene_to_idx, delim=delim)
            except ValueError as exc:
                out.append(f"{ds_name}/{pool_name}: task {task!r} does not resolve: {exc}")
                continue
            if gene_task not in resolved:
                out.append(f"{ds_name}/{pool_name}: task {task!r} is a control label, not a target")
                continue
        if task not in tgi:
            out.append(
                f"{ds_name}/{pool_name}: task {task!r} has no entry in the dataset's "
                "target_gene_idx (the trainer and lifecycle would have nothing to hold out)"
            )
    return out


__all__ = [
    "KEY_NAME",
    "PREREGISTERED_DESIGN",
    "PREREGISTERED_VERSIONS",
    "PreflightError",
    "PreflightReport",
    "TASK_POOL_DATASET",
    "openrouter_probe",
    "preflight",
]
