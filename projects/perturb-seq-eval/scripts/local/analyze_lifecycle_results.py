"""Bootstrap 95 % CIs + summary stats on end-to-end agentic lifecycle runs.

Consumes ``artifacts/lifecycle/adamson_lifecycle_runs.json``; writes
``artifacts/modal_run/revision/revision_stats_lifecycle.json``.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
IN_PATH = ROOT / "artifacts" / "lifecycle" / "adamson_lifecycle_runs.json"
OUT_DIR = ROOT / "artifacts" / "modal_run" / "revision"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _bootstrap(
    values: np.ndarray,
    *,
    n_boot: int = 2000,
    alpha: float = 0.05,
    rng: np.random.Generator | None = None,
) -> tuple[float, float, float]:
    rng = rng or np.random.default_rng(2026)
    n = values.shape[0]
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    samples = np.empty(n_boot, dtype=np.float64)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        samples[i] = values[idx].mean()
    return (
        float(values.mean()),
        float(np.quantile(samples, alpha / 2)),
        float(np.quantile(samples, 1 - alpha / 2)),
    )


def main() -> None:
    if not IN_PATH.exists():
        raise SystemExit(f"lifecycle manifest missing: {IN_PATH}")
    runs = json.loads(IN_PATH.read_text())
    finite = [r for r in runs if np.isfinite(r.get("final_msd_topk", float("inf")))]
    failed = [r for r in runs if not np.isfinite(r.get("final_msd_topk", float("inf")))]

    per_task: dict[str, list[float]] = {}
    round_depth: list[int] = []
    backbone_counts: Counter[str] = Counter()
    for r in finite:
        per_task.setdefault(r["task_id"], []).append(r["final_msd_topk"])
        round_depth.append(int(r["n_rounds"]))
        backbone_counts[r["backbone_used"]] += 1

    all_msds = np.array([r["final_msd_topk"] for r in finite], dtype=np.float64)
    point, lo, hi = _bootstrap(all_msds)

    payload = {
        "n_runs_total": len(runs),
        "n_runs_finite": len(finite),
        "n_runs_failed": len(failed),
        "n_unique_tasks": len(per_task),
        "final_msd_mean_ci95": [point, lo, hi],
        "per_task_msd_mean": {t: float(np.mean(v)) for t, v in per_task.items()},
        "per_task_msd_n_runs": {t: len(v) for t, v in per_task.items()},
        "round_depth_distribution": dict(Counter(round_depth)),
        "backbone_usage": dict(backbone_counts),
    }
    out_path = OUT_DIR / "revision_stats_lifecycle.json"
    out_path.write_text(json.dumps(payload, indent=2, default=str))
    print(json.dumps(payload, indent=2, default=str))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
