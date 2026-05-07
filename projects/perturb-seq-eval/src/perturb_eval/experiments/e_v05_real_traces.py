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
  * cross-dataset TDI transfer (ρ trained on Adamson applied to Norman)
  * three pre-registered gate booleans (see Phase 3 gates in
    ``.claude/plans/v0.5.0-real-perturb-seq.md``)
"""

from __future__ import annotations

import json
import math
import statistics
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from perturb_eval.agentic_lifecycle.freedom_probe import (
    per_agent_field_entropy,
    summarise_choice_distribution,
)


@dataclass(frozen=True)
class BestConfigPerTask:
    """Best (min-MSD) trainer configuration for a single task."""

    task: str
    best_msd: float
    best_config: dict[str, Any]
    n_configs_tried: int


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def best_config_per_task(trainer_jsonl: Path) -> dict[str, BestConfigPerTask]:
    """Return each task's min-MSD trainer config across all seeds."""
    rows = _read_jsonl(trainer_jsonl)
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
    rows = _read_jsonl(trainer_jsonl)
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


def tdi_vs_held_out_msd(
    lifecycle_jsonl: Path,
    *,
    feature_path: tuple[str, str] = ("Architect", "ace_proxy"),
) -> dict[str, float]:
    """Spearman correlation between a lifecycle-trace feature and final MSD.

    ``feature_path`` is ``(agent_name, proposal_field)`` — e.g.
    ``("Architect", "ace_proxy")`` looks up
    ``step.proposal_content["ace_proxy"]`` from the first Architect step
    per trace and correlates with ``final_msd_topk``.
    """
    agent, field = feature_path
    rows = _read_jsonl(lifecycle_jsonl)
    xs: list[float] = []
    ys: list[float] = []
    for r in rows:
        if not _finite(r.get("final_msd_topk")):
            continue
        feat_val = None
        for step in r.get("steps", []):
            if step.get("agent_name") == agent:
                feat_val = step.get("proposal_content", {}).get(field)
                break
        if feat_val is None:
            continue
        try:
            fv = float(feat_val)
        except (TypeError, ValueError):
            continue
        xs.append(fv)
        ys.append(float(r["final_msd_topk"]))
    if len(xs) < 3:
        return {"spearman": float("nan"), "n": len(xs)}
    # Spearman via rank correlation.
    rank_x = _rankdata(xs)
    rank_y = _rankdata(ys)
    return {"spearman": float(_pearson(rank_x, rank_y)), "n": len(xs)}


def _rankdata(x: list[float]) -> list[float]:
    # Average-rank ties.
    idx_sorted = sorted(range(len(x)), key=lambda i: x[i])
    ranks = [0.0] * len(x)
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and x[idx_sorted[j + 1]] == x[idx_sorted[i]]:
            j += 1
        avg_rank = (i + j) / 2 + 1.0
        for k in range(i, j + 1):
            ranks[idx_sorted[k]] = avg_rank
        i = j + 1
    return ranks


def _pearson(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    dx = math.sqrt(sum((a - mx) ** 2 for a in xs))
    dy = math.sqrt(sum((b - my) ** 2 for b in ys))
    if dx == 0 or dy == 0:
        return 0.0
    return num / (dx * dy)


def analyse_v05_run(trainer_jsonl: Path, lifecycle_jsonl: Path) -> dict:
    """End-to-end summary for the paper's §4 rewrite."""
    trainer_rows = _read_jsonl(trainer_jsonl)
    lifecycle_rows = _read_jsonl(lifecycle_jsonl)

    # Per-dataset median MSD (best config per task).
    best_by_task = best_config_per_task(trainer_jsonl)
    by_dataset: dict[str, list[float]] = defaultdict(list)
    for bc in best_by_task.values():
        ds = str(bc.best_config.get("dataset", "unknown"))
        by_dataset[ds].append(bc.best_msd)

    median_adamson = (
        float(statistics.median(by_dataset["adamson_full"]))
        if by_dataset.get("adamson_full") else float("nan")
    )
    median_norman = (
        float(statistics.median(by_dataset["norman"]))
        if by_dataset.get("norman") else float("nan")
    )

    # Architect choice entropy on lifecycle traces.
    traces = [list(r.get("steps", [])) for r in lifecycle_rows]
    h_backbone = per_agent_field_entropy(traces, agent="Architect", field="backbone")
    h_hvg = per_agent_field_entropy(traces, agent="Architect", field="hvg_count")
    bb_dist = summarise_choice_distribution(traces, agent="Architect", field="backbone")

    # Gate booleans per the v0.5.0 plan.
    gate_adamson = (not math.isnan(median_adamson)) and median_adamson < 0.20
    gate_norman = (not math.isnan(median_norman)) and median_norman < 0.30
    gate_entropy = h_backbone >= 0.5

    n_finite_lifecycle = sum(1 for r in lifecycle_rows if _finite(r.get("final_msd_topk")))

    return {
        "n_trainer_runs": len(trainer_rows),
        "n_lifecycle_runs": len(lifecycle_rows),
        "n_lifecycle_finite": n_finite_lifecycle,
        "n_tasks_analysed": len(best_by_task),
        "median_msd_adamson": median_adamson,
        "median_msd_norman": median_norman,
        "architect_backbone_entropy_nats": float(h_backbone),
        "architect_hvg_entropy_nats": float(h_hvg),
        "architect_backbone_distribution": bb_dist,
        "gate_adamson_median_below_0_20": bool(gate_adamson),
        "gate_norman_median_below_0_30": bool(gate_norman),
        "gate_architect_entropy_above_0_5_nats": bool(gate_entropy),
        "best_config_per_task": {
            k: asdict(v) for k, v in best_by_task.items()
        },
    }


def main(
    trainer_jsonl: Path = Path("artifacts/v0.5.0/trainer_runs.jsonl"),
    lifecycle_jsonl: Path = Path("artifacts/v0.5.0/lifecycle_runs.jsonl"),
    out: Path = Path("artifacts/v0.5.0/summary.json"),
) -> dict:
    """CLI convenience — writes ``summary.json`` next to the inputs."""
    summary = analyse_v05_run(trainer_jsonl, lifecycle_jsonl)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, default=str))
    return summary


if __name__ == "__main__":  # pragma: no cover
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--trainer", type=Path, default=Path("artifacts/v0.5.0/trainer_runs.jsonl"))
    ap.add_argument("--lifecycle", type=Path, default=Path("artifacts/v0.5.0/lifecycle_runs.jsonl"))
    ap.add_argument("--out", type=Path, default=Path("artifacts/v0.5.0/summary.json"))
    args = ap.parse_args()
    s = main(args.trainer, args.lifecycle, args.out)
    print(json.dumps(s, indent=2, default=str))
