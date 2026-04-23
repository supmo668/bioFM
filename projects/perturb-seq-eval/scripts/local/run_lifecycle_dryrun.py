"""End-to-end agentic lifecycle on a tiny synthetic dataset.

CPU smoke test for the lifecycle package. Uses the MockAgentPool so no
network or LLM call is made. For the Adamson run, see
scripts/modal/app_lifecycle.py.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np

from perturb_eval.agentic_lifecycle.loop import MockAgentPool, run_agentic_lifecycle

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts" / "lifecycle_dryrun"
OUT.mkdir(parents=True, exist_ok=True)


def _toy_dataset(seed: int = 0) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, int]]:
    rng = np.random.default_rng(seed)
    X = rng.standard_normal((200, 40)) * 0.3 + 2.0
    labels = np.asarray(["CTRL"] * 50 + ["A"] * 50 + ["B"] * 50 + ["C"] * 50)
    X[50:100, 5] -= 2.0
    X[100:150, 10] -= 2.0
    X[150:200, 15] -= 2.0
    control_mask = labels == "CTRL"
    target_gene_idx = {"A": 5, "B": 10, "C": 15}
    return X, labels, control_mask, target_gene_idx


def main() -> None:
    X, labels, control_mask, target_gene_idx = _toy_dataset()
    pool = MockAgentPool(seed=0)
    runs: list[dict] = []
    t0 = time.perf_counter()
    for held in ("A", "B", "C"):
        run = run_agentic_lifecycle(
            task_id=f"hold_{held}",
            X=X, labels=labels, control_mask=control_mask,
            target_gene_idx=target_gene_idx, held_out=held,
            agent_pool=pool, max_rounds=3,
        )
        print(
            f"{held}: MSD={run.final_msd_topk:.4f}  rounds={run.n_rounds}  "
            f"backbone={run.backbone_used}"
        )
        runs.append(asdict(run))
    wall = time.perf_counter() - t0
    (OUT / "dryrun_runs.json").write_text(json.dumps(runs, indent=2, default=str))
    print(f"Wrote {len(runs)} runs → {OUT / 'dryrun_runs.json'}  (wall={wall:.2f}s)")


if __name__ == "__main__":
    main()
