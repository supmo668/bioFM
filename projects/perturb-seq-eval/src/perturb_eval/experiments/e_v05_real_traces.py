"""Analyse v0.5.0 Modal-run JSONL traces for the paper's §4 tables.

Consumes two files written by ``scripts/modal/app_v05.py``:

  * ``trainer_runs.jsonl`` — one record per ``(dataset, task, backbone,
    N, R, seed)`` cell, with ``msd_topk`` as the held-out MSD.
  * ``lifecycle_runs.jsonl`` — one record per ``(dataset, task, seed)``
    full lifecycle run, with ``steps`` containing every agent proposal.

Emits ``summary.json`` with:

  * median MSD per config
  * best-config-per-task MSD
  * per-dataset medians (Adamson, Norman)
  * Architect choice entropy (backbone + hvg_count fields)
  * ``preregistered``: the five pre-registered gates H1-H5
    (``paper/PREREGISTRATION.md``), computed by
    :mod:`perturb_eval.experiments.preregistered`, with a PASS/FAIL/UNEVALUATED tally
  * ``preregistration``: the pre-registration pin copied from record 0
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
    summarise_choice_distribution,
)
from perturb_eval.experiments import preregistered as prereg
from perturb_eval.experiments.provenance import format_unparseable, read_jsonl_locating

logger = logging.getLogger(__name__)

ROLES: tuple[str, ...] = ("DataCurator", "Literature", "Architect", "Trainer", "Validator")


@dataclass(frozen=True)
class BestConfigPerTask:
    """Best (min-MSD) trainer configuration for a single task."""

    task: str
    best_msd: float
    best_config: dict[str, Any]
    n_configs_tried: int


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


def best_config_per_task(trainer_jsonl: Path) -> dict[str, BestConfigPerTask]:
    """Return each task's min-MSD trainer config across all seeds."""
    rows = _read_rows(trainer_jsonl)
    by_task: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        if not _finite(r.get("msd_topk")):
            continue
        if "task" not in r:
            continue
        by_task[r["task"]].append(r)
    out: dict[str, BestConfigPerTask] = {}
    for task, entries in by_task.items():
        # Minimum across all (backbone, N, R, seed).
        best = min(entries, key=lambda x: float(x["msd_topk"]))
        cfg = {
            k: best.get(k)
            for k in ("backbone", "N", "R", "seed", "dataset")
            if k in best
        }
        out[task] = BestConfigPerTask(
            task=task,
            best_msd=float(best["msd_topk"]),
            best_config=cfg,
            n_configs_tried=len(entries),
        )
    return out


def median_msd_per_config(trainer_jsonl: Path) -> list[dict]:
    """Median MSD per unique ``(dataset, backbone, N, R)``."""
    rows = _read_rows(trainer_jsonl)
    grouped: dict[tuple, list[float]] = defaultdict(list)
    for r in rows:
        if not _finite(r.get("msd_topk")):
            continue
        key = (
            r.get("dataset", ""),
            r.get("backbone", ""),
            int(r.get("N", -1)),
            int(r.get("R", -1)),
        )
        grouped[key].append(float(r["msd_topk"]))
    out = []
    for (dataset, backbone, N, R), vals in grouped.items():
        out.append(
            {
                "dataset": dataset,
                "backbone": backbone,
                "N": N,
                "R": R,
                "median_msd": statistics.median(vals),
                "n_seeds": len(vals),
            }
        )
    return out


def _task_key(row: dict) -> Any:
    """Trainer rows use ``task``; lifecycle rows use ``task_id``."""
    return row.get("task", row.get("task_id"))


def _check_task_sets(trainer_rows: list[dict], lifecycle_rows: list[dict]) -> tuple[set, set]:
    trainer_tasks = {_task_key(r) for r in trainer_rows}
    lifecycle_tasks = {_task_key(r) for r in lifecycle_rows}
    if trainer_tasks != lifecycle_tasks:
        only_t = sorted(map(str, trainer_tasks - lifecycle_tasks))
        only_l = sorted(map(str, lifecycle_tasks - trainer_tasks))
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
    """The ``preregistration`` record from record 0 (both headers must agree)."""
    t = (trainer_prov or {}).get("preregistration")
    lc = (lifecycle_prov or {}).get("preregistration")
    if t is not None and lc is not None and t != lc:
        raise ValueError(f"preregistration pin differs between headers: trainer={t!r}, "
                         f"lifecycle={lc!r}")
    return lc if lc is not None else t


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
    h_backbone: float | None,
    backbone_counts: dict[str, int],
    norman_strata: dict[str, str] | None,
) -> dict:
    """H1-H5 in the gate-result shape of :mod:`preregistered`, plus a tally."""
    arch = [s for t in llm_traces for s in t if s.get("agent_name") == "Architect"]
    table = prereg.per_task_table(lifecycle_rows)
    results = {
        "H1": prereg.h1_h2_stats(best_by_dataset.get("adamson_full", {}),
                                 prereg.H1_THRESHOLD, gate="H1"),
        "H2": prereg.h1_h2_stats(best_by_dataset.get("norman", {}), prereg.H2_THRESHOLD,
                                 gate="H2", strata=norman_strata),
        "H3": prereg.h3(h_backbone, pick_counts=backbone_counts,
                        n_llm_steps=sum("backbone" in s.get("proposal_content", {}) for s in arch),
                        n_distinct_model_ids=len({s.get("model_id") for s in arch
                                                  if s.get("model_id")})),
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
    ``summary["allow_partial_reason"]``). Diagnostic summaries carry a
    non-``ok`` ``status`` and null gate booleans.
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
    diagnostic = False
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

    # --- computation ------------------------------------------------------
    best_by_task = best_config_per_task(trainer_jsonl)
    best_by_dataset: dict[str, dict[str, float]] = defaultdict(dict)
    for task, bc in best_by_task.items():
        best_by_dataset[str(bc.best_config.get("dataset", "unknown"))][task] = bc.best_msd

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
    llm_traces = [
        [s for s in r.get("steps", []) if _step_source(s) == "llm"]
        for r in lifecycle_rows
    ]
    h_backbone = _entropy_or_none(llm_traces, "Architect", "backbone")
    h_hvg = _entropy_or_none(llm_traces, "Architect", "hvg_count")
    bb_dist = summarise_choice_distribution(llm_traces, agent="Architect", field="backbone")
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
        h_backbone=h_backbone, backbone_counts=bb_dist,
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
        "entropy_by_role": entropy_by_role,
        "gate_adamson_median_below_0_20": gate_adamson,
        "gate_norman_median_below_0_30": gate_norman,
        "gate_architect_entropy_above_0_5_nats": gate_entropy,
        "preregistered": {**gates, "tally": prereg.tally(gates)},
        "preregistration": _preregistration_pin(trainer_prov, lifecycle_prov),
        "best_config_per_task": {
            k: asdict(v) for k, v in best_by_task.items()
        },
    }


def main(
    trainer_jsonl: Path = Path("artifacts/v0.5.0/trainer_runs.jsonl"),
    lifecycle_jsonl: Path = Path("artifacts/v0.5.0/lifecycle_runs.jsonl"),
    out: Path = Path("artifacts/v0.5.0/summary.json"),
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


if __name__ == "__main__":  # pragma: no cover
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--trainer", type=Path, default=Path("artifacts/v0.5.0/trainer_runs.jsonl"))
    ap.add_argument("--lifecycle", type=Path, default=Path("artifacts/v0.5.0/lifecycle_runs.jsonl"))
    ap.add_argument("--out", type=Path, default=Path("artifacts/v0.5.0/summary.json"))
    ap.add_argument("--allow-fallback-for-diagnosis", action="store_true")
    ap.add_argument("--allow-partial", metavar="REASON", default=None,
                    help="non-empty reason; marks summary PARTIAL_DIAGNOSTIC_ONLY")
    args = ap.parse_args()
    s = main(
        args.trainer, args.lifecycle, args.out,
        allow_fallback_for_diagnosis=args.allow_fallback_for_diagnosis,
        allow_partial=args.allow_partial,
    )
    print(json.dumps(s, indent=2, default=str))
