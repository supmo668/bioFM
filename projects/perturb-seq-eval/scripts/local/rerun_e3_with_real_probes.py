"""Rerun E3-Adamson with live probes + bootstrap CIs + γ_T.

Reads ``artifacts/real_probes/adamson_probes.json`` (baseline) and, if
present, ``artifacts/real_probes/adamson_probes_biofm.json`` (BioFM-grounded),
reruns the three optimizers against the cached Adamson MSD grid, and
writes:

    artifacts/modal_run/revision/revision_stats_real_probes.json         (baseline)
    artifacts/modal_run/revision/revision_stats_real_probes_biofm.json   (BioFM)

Both payloads carry per-optimizer final-MSD CIs, cumulative-regret CIs,
γ_T, and CI-overlap flags so the supplement can report whether the
real-data claim survives.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from perturb_eval.experiments import run_e3_optimizer_comparison  # noqa: E402
from perturb_eval.experiments.e3_optimizer_comparison import _phi_key  # noqa: E402
from perturb_eval.optimizers.base import config_to_vec  # noqa: E402
from perturb_eval.optimizers.contextual_gp import _hamming_like, _matern52  # noqa: E402
from perturb_eval.types import Config  # noqa: E402


RESULTS = ROOT / "artifacts" / "modal_run" / "results"
REVISION = ROOT / "artifacts" / "modal_run" / "revision"
PROBES = ROOT / "artifacts" / "real_probes"
REVISION.mkdir(parents=True, exist_ok=True)


def load_grid(path: Path) -> dict[tuple[str, str], float]:
    grid: dict[tuple[str, str], float] = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        parts = row["phi_id"].split("_")
        key = f"a={parts[0][1:]}r={parts[1][1:]}b={'_'.join(parts[2:])}"
        grid[(key, row["task"])] = float(row["msd_topk"])
    return grid


def max_information_gain(K: np.ndarray, T: int, noise: float = 1e-3) -> float:
    selected: list[int] = []
    info = 0.0
    inv = 1.0 / noise
    for _ in range(min(T, K.shape[0])):
        best_gain, best_idx = -np.inf, -1
        for i in range(K.shape[0]):
            if i in selected:
                continue
            cand = selected + [i]
            KA = K[np.ix_(cand, cand)]
            sign, logdet = np.linalg.slogdet(np.eye(len(cand)) + inv * KA)
            v = 0.5 * float(logdet) if sign > 0 else 0.0
            d = v - info
            if d > best_gain:
                best_gain, best_idx = d, i
        if best_idx < 0:
            break
        selected.append(best_idx)
        info += best_gain
    return info


def bootstrap(values: np.ndarray, n_boot: int = 2000, alpha: float = 0.05,
              rng: np.random.Generator | None = None) -> tuple[float, float, float]:
    rng = rng or np.random.default_rng(2026)
    n = values.shape[0]
    point = float(values.mean())
    samples = np.empty(n_boot, dtype=np.float64)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        samples[i] = values[idx].mean()
    return point, float(np.quantile(samples, alpha / 2)), float(np.quantile(samples, 1 - alpha / 2))


def run_with_probes(
    label: str,
    probes_path: Path,
    grid: dict[tuple[str, str], float],
    config_space: tuple[Config, ...],
    n_iter: int,
    n_seeds: int,
) -> dict:
    print(f"--- {label} ({probes_path.name}) ---")
    if not probes_path.exists():
        print(f"  skipped: {probes_path} not found")
        return {"status": "missing"}
    raw = json.loads(probes_path.read_text())
    contexts = {task: np.asarray(vec, dtype=np.float64) for task, vec in raw.items()}
    tasks = sorted(contexts)
    trajectories = run_e3_optimizer_comparison(
        grid=grid,
        contexts=contexts,
        optimizers=("random", "cma_es", "contextual_gp"),
        n_iterations=n_iter,
        n_seeds=n_seeds,
        config_space=config_space,
    )

    rng = np.random.default_rng(2026)
    task_min = {
        task: min(v for (_, t_), v in grid.items() if t_ == task)
        for task in tasks
    }
    y_min_per_run = np.repeat(
        np.array([task_min[t] for t in tasks]), n_seeds,
    )

    per_opt: dict[str, dict] = {}
    for t in trajectories:
        per_seed = np.asarray(t.per_seed_trajectories, dtype=np.float64)
        final = per_seed[:, -1]
        point_final, lo_final, hi_final = bootstrap(final, rng=rng)
        regret = final - y_min_per_run
        point_regret, lo_regret, hi_regret = bootstrap(regret, rng=rng)
        per_opt[t.optimizer] = {
            "final_msd_mean": point_final,
            "final_msd_ci95": [lo_final, hi_final],
            "final_regret_mean": point_regret,
            "final_regret_ci95": [lo_regret, hi_regret],
            "best_msd_per_iter_mean": list(t.best_msd_per_iter),
            "cum_regret_per_iter_mean": list(t.cum_regret_per_iter),
            "per_seed_final_msd": [float(x) for x in final],
        }

    # γ_T on the factor kernel
    phi_emb = np.stack([config_to_vec(c) for c in config_space], axis=0)
    x_emb = np.stack([contexts[t] for t in tasks], axis=0)
    Phi_prod = np.repeat(phi_emb, len(tasks), axis=0)
    X_prod = np.tile(x_emb, (len(config_space), 1))
    K = _hamming_like(Phi_prod, Phi_prod, 1.0) * _matern52(X_prod, X_prod, 1.0)
    gamma = max_information_gain(K, T=n_iter)

    def overlap(a: dict, b: dict) -> bool:
        return not (a["final_msd_ci95"][1] < b["final_msd_ci95"][0]
                    or b["final_msd_ci95"][1] < a["final_msd_ci95"][0])
    cg = per_opt.get("contextual_gp", {})
    es = per_opt.get("cma_es", {})
    rd = per_opt.get("random", {})
    overlaps = {
        "contextual_vs_cma_es": overlap(cg, es) if cg and es else None,
        "contextual_vs_random": overlap(cg, rd) if cg and rd else None,
    }
    payload = {
        "regime": label,
        "probes_path": str(probes_path),
        "contexts": {k: v.tolist() for k, v in contexts.items()},
        "n_iterations": n_iter,
        "n_seeds": n_seeds,
        "n_tasks": len(tasks),
        "per_optimizer": per_opt,
        "gamma_T": gamma,
        "ci_overlap_on_final_msd": overlaps,
    }
    for opt, s in per_opt.items():
        lo, hi = s["final_msd_ci95"]
        print(f"  {opt:<14} final={s['final_msd_mean']:.5f} CI95=[{lo:.5f},{hi:.5f}] "
              f"regret={s['final_regret_mean']:.5f}")
    print(f"  γ_T={gamma:.2f}  overlaps: {overlaps}")
    return payload


def main() -> int:
    grid = load_grid(RESULTS / "e2_grid_adamson.jsonl")
    config_space = tuple(
        Config(n_agents=a, n_rounds=r, backbone=b)
        for a in (3, 4, 5)
        for r in (1, 2, 3)
        for b in ("linear", "mlp", "scgpt_small")
    )

    out_baseline = run_with_probes(
        "adamson_real_probes_baseline",
        PROBES / "adamson_probes.json",
        grid, config_space, n_iter=30, n_seeds=20,
    )
    (REVISION / "revision_stats_real_probes.json").write_text(
        json.dumps(out_baseline, indent=2)
    )

    out_biofm = run_with_probes(
        "adamson_real_probes_biofm",
        PROBES / "adamson_probes_biofm.json",
        grid, config_space, n_iter=30, n_seeds=20,
    )
    if out_biofm.get("status") != "missing":
        (REVISION / "revision_stats_real_probes_biofm.json").write_text(
            json.dumps(out_biofm, indent=2)
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
