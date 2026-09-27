"""Analyse v0.6.0 (and legacy v0.5.0) Modal-run JSONL traces for the paper's §4 tables.

Consumes two files written by ``scripts/modal/app_v05.py``:

  * ``trainer_runs.jsonl`` — one record per ``(dataset, task, backbone,
    N, R, seed)`` cell, with ``msd_topk`` as the held-out MSD.
  * ``lifecycle_runs.jsonl`` — one record per ``(dataset, task, seed)``
    full lifecycle run, with ``steps`` containing every agent proposal.

Emits ``summary.json`` with:

  * median MSD per config
  * best-config-per-task MSD
  * per-dataset medians (Adamson, Norman)
  * Architect choice entropy (STATED backbone, A2-6, with the executed backbone
    alongside; hvg_count)
  * ``preregistered``: the five pre-registered gates H1-H5
    (``paper/PREREGISTRATION.md``), computed by
    :mod:`perturb_eval.experiments.preregistered`, with a PASS/FAIL/UNEVALUATED tally
  * ``preregistration``: the pre-registration pin copied from record 0

A task's identity is ``(dataset, task)`` (:func:`preregistered.task_key`): a
gene symbol can be a task in both Adamson and Norman (QG C5).

Gates are licensed only for a pinned, finished, clean run: a run whose record 0
carries no ``preregistration`` pin is summarised as ``status="UNPINNED"``, and
a legacy run without provenance as ``legacy_no_provenance`` — both diagnostic,
every gate ``pass=None`` (QG C10). Headers whose pins differ are refused.

CLI::

    python -m perturb_eval.experiments.e_v05_real_traces [ARTIFACTS_DIR]

reads ``ARTIFACTS_DIR/{trainer_runs,lifecycle_runs}.jsonl`` (default
``artifacts/v0.6.0``) and writes ``ARTIFACTS_DIR/summary.json``.
"""

from __future__ import annotations

import json
import logging
import math
import statistics
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from perturb_eval.agentic_lifecycle.freedom_probe import (
    choice_entropy,
    per_agent_field_entropy,
)
from perturb_eval.experiments import preregistered as prereg
from perturb_eval.experiments.preregistered import task_key
from perturb_eval.experiments.provenance import format_unparseable, read_jsonl_locating

logger = logging.getLogger(__name__)

DEFAULT_ARTIFACTS_DIR = Path("artifacts/v0.6.0")

ROLES: tuple[str, ...] = ("DataCurator", "Literature", "Architect", "Trainer", "Validator")


@dataclass(frozen=True)
class BestConfigPerTask:
    """Best (min-MSD) trainer configuration for a single ``(dataset, task)``.

    Amendment 2 (A2-4): a configuration is ``(backbone, R)`` -- N is not an
    axis -- and seeds are replicates. ``n_configs_tried`` counts the distinct
    ``(backbone, R)`` configurations actually run (with a finite MSD);
    ``n_records`` the finite records; ``seeds`` the seeds seen.
    """

    task: str
    best_msd: float
    best_config: dict[str, Any]
    n_configs_tried: int
    dataset: str | None = None
    n_records: int = 0
    seeds: tuple = ()


def _read_jsonl(path: Path) -> tuple[dict | None, list[dict]]:
    """Return ``(provenance, rows)``.

    If line 0 is ``{"record_type": "provenance", ...}`` it is returned
    separately and excluded from ``rows``; otherwise ``provenance`` is
    ``None`` (a legacy artifact). Any unparseable line is REFUSED
    (``ValueError`` naming file, line and byte offset) — CTO #245 Q2, no
    override.
    """
    rows, bad = read_jsonl_locating(path)
    if bad:
        raise ValueError(
            f"{len(bad)} unparseable JSONL line(s); analyser refuses: "
            + format_unparseable(path, bad)
        )
    if rows and isinstance(rows[0], dict) and rows[0].get("record_type") == "provenance":
        return rows[0], rows[1:]
    return None, rows


def _read_rows(path: Path) -> list[dict]:
    return _read_jsonl(path)[1]


def _finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def best_config_per_task(trainer_jsonl: Path) -> dict[tuple[str, str], BestConfigPerTask]:
    """Return each ``(dataset, task)``'s oracle: the min MSD over the distinct
    ``(backbone, R)`` configurations actually run, each seed a replicate
    (amendment 2, A2-4: N is not a configuration axis). Non-finite records are
    excluded."""
    rows = _read_rows(trainer_jsonl)
    by_task: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in rows:
        if not _finite(r.get("msd_topk")):
            continue
        if "task" not in r:
            continue
        by_task[task_key(r)].append(r)
    out: dict[tuple[str, str], BestConfigPerTask] = {}
    for (dataset, task), entries in by_task.items():
        # A2-4: min over the distinct (backbone, R) configurations, seeds as
        # replicates (the min over every finite replicate of every configuration).
        best = min(entries, key=lambda x: float(x["msd_topk"]))
        cfg = {
            k: best.get(k)
            for k in ("backbone", "R", "seed", "dataset")
            if k in best
        }
        seeds = sorted({e["seed"] for e in entries if e.get("seed") is not None}, key=str)
        out[(dataset, task)] = BestConfigPerTask(
            task=task,
            best_msd=float(best["msd_topk"]),
            best_config=cfg,
            n_configs_tried=len({(e.get("backbone"), e.get("R")) for e in entries}),
            dataset=dataset,
            n_records=len(entries),
            seeds=tuple(seeds),
        )
    return out


def median_msd_per_config(trainer_jsonl: Path) -> list[dict]:
    """Median MSD over seeds per unique ``(dataset, backbone, R)`` configuration
    (amendment 2, A2-4: N is not a configuration axis; seeds are replicates)."""
    rows = _read_rows(trainer_jsonl)
    grouped: dict[tuple, list[float]] = defaultdict(list)
    for r in rows:
        if not _finite(r.get("msd_topk")):
            continue
        key = (
            r.get("dataset", ""),
            r.get("backbone", ""),
            int(r.get("R", -1)),
        )
        grouped[key].append(float(r["msd_topk"]))
    out = []
    for (dataset, backbone, R), vals in grouped.items():
        out.append(
            {
                "dataset": dataset,
                "backbone": backbone,
                "R": R,
                "median_msd": statistics.median(vals),
                "n_seeds": len(vals),
            }
        )
    return out


def _fmt_key(key: tuple[str, str] | None) -> str:
    return "None" if key is None else f"{key[0]}:{key[1]}"


def _check_task_sets(trainer_rows: list[dict], lifecycle_rows: list[dict]) -> tuple[set, set]:
    """Both files must cover the same ``(dataset, task)`` set (QG C5)."""
    trainer_tasks = {task_key(r) for r in trainer_rows}
    lifecycle_tasks = {task_key(r) for r in lifecycle_rows}
    if trainer_tasks != lifecycle_tasks:
        only_t = sorted(map(_fmt_key, trainer_tasks - lifecycle_tasks))
        only_l = sorted(map(_fmt_key, lifecycle_tasks - trainer_tasks))
        raise ValueError(
            f"task sets differ: only-trainer={only_t}, only-lifecycle={only_l}"
        )
    return trainer_tasks, lifecycle_tasks


def _resolve_provenance(
    trainer_prov: dict | None,
    lifecycle_prov: dict | None,
    trainer_jsonl: Path,
    trainer_path: Path,
    lifecycle_path: Path,
    provenance_json: Path | None,
) -> dict | None:
    """Cross-check the two record-0 headers; return the effective provenance.

    The JSONL headers are written at run start (so typically carry no
    ``finished_at``); the finalised ``provenance.json`` next to the JSONLs
    (or the explicit ``provenance_json`` path) supplies ``status`` and
    ``finished_at`` when present, and must agree on ``run_id``/``git_sha``.
    Returns ``None`` for a legacy run (no headers at all).
    """
    if trainer_prov is None and lifecycle_prov is None:
        logger.warning(
            "legacy artifact without provenance record: %s, %s",
            trainer_path, lifecycle_path,
        )
        return None
    if trainer_prov is None or lifecycle_prov is None:
        raise ValueError(
            "provenance record present in only one file: "
            f"trainer={trainer_path} has={trainer_prov is not None}, "
            f"lifecycle={lifecycle_path} has={lifecycle_prov is not None}"
        )
    for key in ("run_id", "git_sha"):
        tv, lv = trainer_prov.get(key), lifecycle_prov.get(key)
        if tv is None or tv != lv:
            raise ValueError(
                f"provenance {key} mismatch: trainer {trainer_path} {key}={tv!r}, "
                f"lifecycle {lifecycle_path} {key}={lv!r}"
            )
    effective = dict(lifecycle_prov)
    final_path = provenance_json or (trainer_jsonl.parent / "provenance.json")
    if final_path.exists():
        final = json.loads(final_path.read_text())
        for key in ("run_id", "git_sha"):
            if final.get(key) != effective.get(key):
                raise ValueError(
                    f"provenance.json {final_path} {key}={final.get(key)!r} does not match "
                    f"JSONL headers {key}={effective.get(key)!r}"
                )
        effective.update(final)
    return effective


def _step_source(step: dict) -> str:
    src = step.get("source")
    return src if src in ("llm", "fallback", "mock") else "unknown"


def _entropy_or_none(traces: list[list[dict]], agent: str, field: str) -> float | None:
    if not any(s.get("agent_name") == agent and field in s.get("proposal_content", {})
               for t in traces for s in t):
        return None
    return float(per_agent_field_entropy(traces, agent=agent, field=field))


def llm_traces_of(lifecycle_rows: list[dict]) -> list[list[dict]]:
    """Per run, its LLM-sourced steps only (T16). Steps without a ``source``
    are UNKNOWN and never assumed to be LLM."""
    return [[s for s in r.get("steps", []) if _step_source(s) == "llm"]
            for r in lifecycle_rows]


def architect_entropies(lifecycle_rows: list[dict]) -> dict[str, Any]:
    """Architect backbone / hvg_count entropy (nats) and backbone distribution
    over LLM-sourced steps only; an entropy is ``None`` when no LLM-sourced
    Architect step carries the field. The one producer used by both this
    analyser and the sweep's provenance (QG C14).

    Amendment 2 (A2-6): the backbone entropy and distribution are those of the
    Architect's STATED backbone (``backbone_stated``; the H3 measurand, computed by
    :func:`preregistered.architect_backbone_stats`) -- a missing or off-menu stated
    value is never defaulted or counted. The EXECUTED backbone's distribution and
    entropy, and the stated != executed count, are reported alongside."""
    traces = llm_traces_of(lifecycle_rows)
    bb = prereg.architect_backbone_stats(s for t in traces for s in t)
    return {
        "architect_backbone_entropy_nats": bb["entropy_stated_nats"],
        "architect_hvg_entropy_nats": _entropy_or_none(traces, "Architect", "hvg_count"),
        "architect_backbone_distribution": bb["stated_counts"],
        "architect_backbone_executed_entropy_nats": bb["entropy_executed_nats"],
        "architect_backbone_executed_distribution": bb["executed_counts"],
        "architect_backbone_n_executed_ne_stated": bb["n_executed_ne_stated"],
    }


def _validate_partial_reason(allow_partial: str | None) -> str | None:
    """``allow_partial`` is a REASON string (CTO #245 Q1), never a bool."""
    if allow_partial is None:
        return None
    if not isinstance(allow_partial, str):
        raise TypeError(
            f"allow_partial must be a non-empty reason string or None, got "
            f"{type(allow_partial).__name__} {allow_partial!r}"
        )
    if not allow_partial.strip():
        raise ValueError("allow_partial reason must be non-empty (not blank/whitespace)")
    return allow_partial


def _is_error_record(row: dict) -> bool:
    return "error" in row or "error_class" in row


def _preregistration_pin(trainer_prov: dict | None, lifecycle_prov: dict | None) -> dict | None:
    """The ``preregistration`` record from record 0.

    Refuses (``ValueError``) when the two headers' pins differ — including one
    pinned and one not (QG C10). ``None`` means the run is UNPINNED.
    """
    t = (trainer_prov or {}).get("preregistration")
    lc = (lifecycle_prov or {}).get("preregistration")
    if t != lc:
        raise ValueError(f"preregistration pin differs between headers: trainer={t!r}, "
                         f"lifecycle={lc!r}")
    return lc or None


def _norman_strata(prov: dict | None) -> dict[str, str] | None:
    tasks = (prov or {}).get("tasks") or {}
    if "norman_singletons" not in tasks and "norman_doublets" not in tasks:
        return None
    strata = {t: "singleton" for t in tasks.get("norman_singletons") or []}
    strata.update({t: "doublet" for t in tasks.get("norman_doublets") or []})
    return strata


def preregistered_results(
    best_by_dataset: dict[str, dict[str, float]],
    lifecycle_rows: list[dict],
    llm_traces: list[list[dict]],
    *,
    norman_strata: dict[str, str] | None,
) -> dict:
    """H1-H5 in the gate-result shape of :mod:`preregistered`, plus a tally.

    H3 gates on the Architect's STATED backbone over LLM-sourced Architect steps;
    the executed backbone is reported alongside (amendment 2, A2-6)."""
    arch = [s for t in llm_traces for s in t if s.get("agent_name") == "Architect"]
    table = prereg.per_task_table(lifecycle_rows)
    results = {
        "H1": prereg.h1_h2_stats(best_by_dataset.get("adamson_full", {}),
                                 prereg.H1_THRESHOLD, gate="H1"),
        "H2": prereg.h1_h2_stats(best_by_dataset.get("norman", {}), prereg.H2_THRESHOLD,
                                 gate="H2", strata=norman_strata),
        "H3": prereg.h3_from_stats(
            prereg.architect_backbone_stats(arch),
            n_distinct_model_ids=len({s.get("model_id") for s in arch if s.get("model_id")})),
        "H4": prereg.h4(table),
        "H5": prereg.h5([r for r in table if r["dataset"] == "adamson_full"],
                        [r for r in table if r["dataset"] == "norman"]),
    }
    if norman_strata is None:
        results["H2"]["strata_reason"] = "no Norman task plan in provenance"
    return results


def analyse_v05_run(
    trainer_jsonl: Path,
    lifecycle_jsonl: Path,
    *,
    allow_fallback_for_diagnosis: bool = False,
    allow_partial: str | None = None,
    provenance_json: Path | None = None,
) -> dict:
    """End-to-end summary for the paper's §4 rewrite.

    Refuses (``ValueError``) before any computation when: the trainer and
    lifecycle task sets differ; the two provenance headers disagree on
    ``run_id``/``git_sha``; the run is ``failed``; the run used any
    fallback step or is ``failed_fallback`` (C-KEY-2, unless
    ``allow_fallback_for_diagnosis``); either JSONL has an unparseable line,
    or provenance recorded one (CTO #245 Q2, no override); or the run is
    partial/unfinished or has ANY error record (unless ``allow_partial`` — a
    non-empty REASON string, CTO #245 Q1, written to
    ``summary["allow_partial_reason"]``); or the two headers' pre-registration
    pins differ (QG C10). Diagnostic summaries carry a non-``ok`` ``status``
    and null gate booleans: besides the escape hatches above, a legacy run
    without provenance and an ``UNPINNED`` run (no pre-registration pin in
    record 0) are always diagnostic (QG C10).
    """
    partial_reason = _validate_partial_reason(allow_partial)
    trainer_prov, trainer_rows = _read_jsonl(trainer_jsonl)
    lifecycle_prov, lifecycle_rows = _read_jsonl(lifecycle_jsonl)

    # --- T15: hard-fail before any computation ---------------------------
    trainer_tasks, lifecycle_tasks = _check_task_sets(trainer_rows, lifecycle_rows)
    prov = _resolve_provenance(
        trainer_prov, lifecycle_prov, trainer_jsonl,
        trainer_jsonl, lifecycle_jsonl, provenance_json,
    )
    pin = _preregistration_pin(trainer_prov, lifecycle_prov)

    if prov is not None:
        recorded = prov.get("unparseable_lines") or {}
        located = [
            format_unparseable(name, entries)
            for name, entries in sorted(recorded.items()) if entries
        ]
        if located:
            raise ValueError(
                "provenance records unparseable JSONL line(s) seen at run time; "
                "analyser refuses: " + "; ".join(located)
            )

    all_steps = [s for r in lifecycle_rows for s in r.get("steps", [])]
    source_counts = {k: 0 for k in ("llm", "fallback", "mock", "unknown")}
    for st in all_steps:
        source_counts[_step_source(st)] += 1

    status = "ok" if prov is not None else "legacy_no_provenance"
    # QG C10: a legacy run (no provenance) is never licensed.
    diagnostic = prov is None
    used_partial_reason: str | None = None
    n_error_records = sum(1 for r in trainer_rows + lifecycle_rows if _is_error_record(r))
    prov_status = prov.get("status") if prov is not None else None
    if prov is not None and prov_status == "failed":
        raise ValueError(f"run FAILED: provenance status='failed' (run_id={prov.get('run_id')!r})")
    if source_counts["fallback"] or prov_status == "failed_fallback":
        msg = (
            f"run FAILED: {source_counts['fallback']} fallback steps "
            f"(provenance status={prov_status!r}); C-KEY-2 — analyser refuses "
            "to summarise a run with fallback rows"
        )
        if not allow_fallback_for_diagnosis:
            raise ValueError(msg)
        logger.warning("%s — computing DIAGNOSTIC-ONLY summary", msg)
        status, diagnostic = "FAILED_FALLBACK_DIAGNOSTIC_ONLY", True
    partial_msgs: list[str] = []
    if (status != "FAILED_FALLBACK_DIAGNOSTIC_ONLY" and prov is not None
            and (prov_status != "ok" or prov.get("finished_at") is None)):
        partial_msgs.append(
            f"run partial/unfinished: provenance status={prov_status!r}, "
            f"finished_at={prov.get('finished_at')!r}"
        )
    if n_error_records:
        partial_msgs.append(
            f"{n_error_records} error record(s) present (transient per-cell failures)"
        )
    if partial_msgs:
        msg = "; ".join(partial_msgs) + "; analyser refuses to summarise"
        if partial_reason is None:
            raise ValueError(msg + " (pass allow_partial=<reason> for a diagnostic read)")
        logger.warning("%s — computing DIAGNOSTIC-ONLY summary (reason: %s)", msg, partial_reason)
        used_partial_reason = partial_reason
        diagnostic = True
        if status != "FAILED_FALLBACK_DIAGNOSTIC_ONLY":
            status = "PARTIAL_DIAGNOSTIC_ONLY"
    if prov is not None and pin is None:
        # QG C10: the pre-registration is enforced at analysis time — a run
        # with no pin in record 0 is summarised but never licenses a gate.
        logger.warning("run has no preregistration pin in record 0 — DIAGNOSTIC-ONLY summary")
        diagnostic = True
        if status == "ok":
            status = "UNPINNED"

    # --- computation ------------------------------------------------------
    best_by_task = best_config_per_task(trainer_jsonl)
    best_by_dataset: dict[str, dict[str, float]] = defaultdict(dict)
    for (dataset, task), bc in best_by_task.items():
        best_by_dataset[dataset][task] = bc.best_msd

    median_adamson = (
        float(statistics.median(best_by_dataset["adamson_full"].values()))
        if best_by_dataset.get("adamson_full") else float("nan")
    )
    median_norman = (
        float(statistics.median(best_by_dataset["norman"].values()))
        if best_by_dataset.get("norman") else float("nan")
    )

    # T16: entropy/distribution figures use LLM-sourced steps only. Steps
    # without a ``source`` field are UNKNOWN and never assumed to be LLM.
    llm_traces = llm_traces_of(lifecycle_rows)
    arch_ent = architect_entropies(lifecycle_rows)
    h_backbone = arch_ent["architect_backbone_entropy_nats"]
    h_hvg = arch_ent["architect_hvg_entropy_nats"]
    bb_dist = arch_ent["architect_backbone_distribution"]
    entropy_by_role: dict[str, float | None] = {}
    for role in ROLES:
        proposals = [
            s.get("proposal_content", {}) for t in llm_traces for s in t
            if s.get("agent_name") == role
        ]
        # Entropy over whole proposals (canonical JSON) for this role.
        entropy_by_role[role] = float(choice_entropy(proposals)) if proposals else None

    # Pre-registered gates H1-H5 (paper/PREREGISTRATION.md).
    gates = preregistered_results(
        best_by_dataset, lifecycle_rows, llm_traces,
        norman_strata=_norman_strata(prov),
    )
    if diagnostic:
        # A diagnostic summary never licenses a gate.
        gates = {k: prereg.not_licensed(v, f"diagnostic summary (status={status}) "
                                           "never licenses a gate")
                 for k, v in gates.items()}
    gate_adamson = gates["H1"]["pass"]
    gate_norman = gates["H2"]["pass"]
    gate_entropy = gates["H3"]["pass"]

    n_finite_lifecycle = sum(1 for r in lifecycle_rows if _finite(r.get("final_msd_topk")))

    return {
        "status": status,
        "allow_partial_reason": used_partial_reason,
        "n_error_records": n_error_records,
        "run_id": prov.get("run_id") if prov is not None else None,
        "git_sha": prov.get("git_sha") if prov is not None else None,
        "n_trainer_runs": len(trainer_rows),
        "n_lifecycle_runs": len(lifecycle_rows),
        "n_lifecycle_finite": n_finite_lifecycle,
        "n_tasks_analysed": len(best_by_task),
        "n_tasks_trainer": len(trainer_tasks),
        "n_tasks_lifecycle": len(lifecycle_tasks),
        "n_lifecycle_runs_unique_tasks": len(lifecycle_tasks),
        "n_steps_llm": source_counts["llm"],
        "n_steps_fallback": source_counts["fallback"],
        "n_steps_mock": source_counts["mock"],
        "n_steps_unknown": source_counts["unknown"],
        "median_msd_adamson": median_adamson,
        "median_msd_norman": median_norman,
        "architect_backbone_entropy_nats": h_backbone,
        "architect_hvg_entropy_nats": h_hvg,
        "architect_backbone_distribution": bb_dist,
        "architect_backbone_executed_distribution":
            arch_ent["architect_backbone_executed_distribution"],
        "architect_backbone_executed_entropy_nats":
            arch_ent["architect_backbone_executed_entropy_nats"],
        "architect_backbone_n_executed_ne_stated":
            arch_ent["architect_backbone_n_executed_ne_stated"],
        "entropy_by_role": entropy_by_role,
        "gate_adamson_median_below_0_20": gate_adamson,
        "gate_norman_median_below_0_30": gate_norman,
        "gate_architect_entropy_above_0_5_nats": gate_entropy,
        "preregistered": {**gates, "tally": prereg.tally(gates)},
        "preregistration": pin,
        "best_config_per_task": {
            _fmt_key(k): asdict(v) for k, v in best_by_task.items()
        },
    }


def main(
    trainer_jsonl: Path = DEFAULT_ARTIFACTS_DIR / "trainer_runs.jsonl",
    lifecycle_jsonl: Path = DEFAULT_ARTIFACTS_DIR / "lifecycle_runs.jsonl",
    out: Path = DEFAULT_ARTIFACTS_DIR / "summary.json",
    *,
    allow_fallback_for_diagnosis: bool = False,
    allow_partial: str | None = None,
) -> dict:
    """CLI convenience — writes ``summary.json`` next to the inputs.

    ``summary.json`` is written only after ``analyse_v05_run`` returns; any
    refusal (``ValueError``) propagates and nothing is written. A partial
    summary carries ``status="PARTIAL_DIAGNOSTIC_ONLY"`` and
    ``allow_partial_reason`` into the written file.
    """
    summary = analyse_v05_run(
        trainer_jsonl,
        lifecycle_jsonl,
        allow_fallback_for_diagnosis=allow_fallback_for_diagnosis,
        allow_partial=allow_partial,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, default=str))
    return summary


def parse_cli(argv: list[str] | None = None) -> Any:
    """CLI arguments: an optional positional artifacts dir (default
    ``artifacts/v0.6.0``) supplies ``trainer_runs.jsonl``,
    ``lifecycle_runs.jsonl`` and ``summary.json``; ``--trainer``,
    ``--lifecycle`` and ``--out`` override each path."""
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("artifacts_dir", nargs="?", type=Path, default=DEFAULT_ARTIFACTS_DIR)
    ap.add_argument("--trainer", type=Path, default=None)
    ap.add_argument("--lifecycle", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--allow-fallback-for-diagnosis", action="store_true")
    ap.add_argument("--allow-partial", metavar="REASON", default=None,
                    help="non-empty reason; marks summary PARTIAL_DIAGNOSTIC_ONLY")
    args = ap.parse_args(argv)
    d = args.artifacts_dir
    args.trainer = args.trainer or d / "trainer_runs.jsonl"
    args.lifecycle = args.lifecycle or d / "lifecycle_runs.jsonl"
    args.out = args.out or d / "summary.json"
    return args


if __name__ == "__main__":  # pragma: no cover
    args = parse_cli()
    s = main(
        args.trainer, args.lifecycle, args.out,
        allow_fallback_for_diagnosis=args.allow_fallback_for_diagnosis,
        allow_partial=args.allow_partial,
    )
    print(json.dumps(s, indent=2, default=str))
