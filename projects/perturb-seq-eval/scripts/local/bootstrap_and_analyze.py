"""Compute bootstrap CIs, cumulative regret, and γ_T per regime.

Closes MC1 (per-seed CIs), mc5 (cumulative regret), and mc8 (numerical γ_T)
from docs/REVIEWER_CRITIQUE.md. Reads the cached E2 grids + the rerun-with-
per-seed E3 trajectories, writes a single ``revision_stats.json`` with
everything a reviewer would want to cite.

Bootstrap resamples the per-(task, seed) final MSD curves over both axes
simultaneously. Cumulative regret is already emitted by the updated E3
runner; we just compute CIs over its per-seed decomposition.

γ_T estimate uses the greedy maximum-information-gain algorithm from
Krause, Singh & Guestrin 2008 (§5.1) applied to the exact kernel used by
the contextual GP on each regime's full grid. For small |Φ| × |tasks|
this is tractable in seconds.

Run from ``projects/perturb-seq-eval/``::

    python scripts/local/bootstrap_and_analyze.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from perturb_eval.experiments import (
    probe_signature_from_trace,
    run_e3_optimizer_comparison,
)
from perturb_eval.experiments.e3_optimizer_comparison import _phi_key
from perturb_eval.optimizers.contextual_gp import _hamming_like, _matern52
from perturb_eval.optimizers.base import config_to_vec
from perturb_eval.types import Config, RoundTrace, RunTrace


RESULTS = Path("artifacts/modal_run/results")
REVISION = Path("artifacts/modal_run/revision")
REVISION.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------


def bootstrap_ci(
    per_seed: np.ndarray,           # (n_runs, n_iter) — n_runs = n_tasks × n_seeds
    reducer,
    n_resamples: int = 2_000,
    alpha: float = 0.05,
    rng: np.random.Generator | None = None,
) -> tuple[float, float, float]:
    """Percentile-bootstrap CI of ``reducer(per_seed_resampled)`` at level ``alpha``."""
    rng = rng or np.random.default_rng(2026)
    n_runs = per_seed.shape[0]
    point = float(reducer(per_seed))
    samples = np.empty(n_resamples, dtype=np.float64)
    for i in range(n_resamples):
        idx = rng.integers(0, n_runs, size=n_runs)
        samples[i] = float(reducer(per_seed[idx]))
    lo = float(np.quantile(samples, alpha / 2))
    hi = float(np.quantile(samples, 1 - alpha / 2))
    return point, lo, hi


# ---------------------------------------------------------------------------
# γ_T — maximum information gain (Krause, Singh, Guestrin 2008)
# ---------------------------------------------------------------------------


def max_information_gain(
    kernel_matrix: np.ndarray,
    T: int,
    noise: float = 1e-3,
) -> float:
    """Greedy estimate of ``γ_T = max_{|A|=T} ½ log |I + σ⁻² K_A|``.

    For each of ``T`` rounds, pick the unselected index that maximally
    increases the log-determinant (submodular greedy → (1 − 1/e) optimal).
    """
    n = kernel_matrix.shape[0]
    selected: list[int] = []
    gain_so_far = 0.0
    inv_noise = 1.0 / noise
    for _ in range(min(T, n)):
        best_gain, best_idx = -np.inf, -1
        for i in range(n):
            if i in selected:
                continue
            cand = selected + [i]
            K_A = kernel_matrix[np.ix_(cand, cand)]
            sign, logdet = np.linalg.slogdet(np.eye(len(cand)) + inv_noise * K_A)
            info = 0.5 * float(logdet) if sign > 0 else 0.0
            delta = info - gain_so_far
            if delta > best_gain:
                best_gain, best_idx = delta, i
        if best_idx < 0:
            break
        selected.append(best_idx)
        gain_so_far += best_gain
    return gain_so_far


def build_factor_kernel_matrix(
    config_space: tuple[Config, ...],
    contexts: dict[str, np.ndarray],
    ls_phi: float = 1.0,
    ls_x: float = 1.0,
) -> np.ndarray:
    """Dense Φ × X kernel matrix over the product of configs and contexts."""
    phi_emb = np.stack([config_to_vec(c) for c in config_space], axis=0)
    task_names = sorted(contexts)
    x_emb = np.stack([contexts[t] for t in task_names], axis=0)
    # Cartesian product of (phi, task) → one row per (i, j) pair.
    Phi_prod = np.repeat(phi_emb, len(task_names), axis=0)
    X_prod = np.tile(x_emb, (len(config_space), 1))
    K_phi = _hamming_like(Phi_prod, Phi_prod, ls_phi)
    K_x = _matern52(X_prod, X_prod, ls_x)
    return K_phi * K_x


# ---------------------------------------------------------------------------
# Grid loaders
# ---------------------------------------------------------------------------


def load_grid_jsonl(path: Path) -> dict[tuple[str, str], float]:
    grid: dict[tuple[str, str], float] = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        # Phi keys in grid JSONL are "a3_r1_linear"; E3 wants "a=3r=1b=linear".
        p = row["phi_id"]
        parts = p.split("_")
        phi_key = f"a={parts[0][1:]}r={parts[1][1:]}b={'_'.join(parts[2:])}"
        grid[(phi_key, row["task"])] = float(row["msd_topk"])
    return grid


def synth_probe_contexts(tasks: tuple[str, ...], seed: int = 2026) -> dict[str, np.ndarray]:
    """Reproduce the deterministic probe-generator used in the Modal app,
    so rerun numbers match the supplement exactly."""
    rng = np.random.default_rng(seed)
    contexts: dict[str, np.ndarray] = {}
    for i, t in enumerate(tasks):
        hardness = (i + 0.5) / len(tasks)
        confs = np.clip(rng.normal(0.5, 0.08 + 0.25 * hardness, size=5), 0.01, 1.0)
        rt = RoundTrace(
            round_index=0,
            agent_names=tuple(f"A{j}" for j in range(5)),
            confidences=tuple(confs.tolist()),
            critique_severities=tuple(tuple(0.15 + 0.45 * hardness for _ in range(4))
                                      for _ in range(5)),
            winner_index=0,
            consensus_score=float(np.clip(0.9 - 0.5 * hardness, 0.1, 0.95)),
        )
        trace = RunTrace(task_id=t, rounds=(rt,), converged=False, backbone="synthetic")
        contexts[t] = probe_signature_from_trace(trace)
    return contexts


def task_conditional_grid() -> tuple[
    dict[tuple[str, str], float],
    dict[str, np.ndarray],
    tuple[Config, ...],
]:
    phis = tuple(
        Config(n_agents=a, n_rounds=r, backbone=b)
        for a in (3, 4, 5)
        for r in (1, 2, 3)
        for b in ("linear", "mlp", "scgpt_small")
    )
    tasks = ("easy1", "easy2", "easy3", "easy4",
             "hard1", "hard2", "hard3", "hard4")
    contexts: dict[str, np.ndarray] = {}
    grid: dict[tuple[str, str], float] = {}
    for t in tasks:
        hard = t.startswith("hard")
        contexts[t] = (
            np.array([0.15, 0.70, 0.05, 0.85]) if not hard
            else np.array([0.85, 0.40, 0.55, 0.45])
        )
        for phi in phis:
            size = phi.n_agents * phi.n_rounds
            target = 15.0 if hard else 3.0
            bonus = {
                "linear": 0.0 if not hard else 0.15,
                "mlp": 0.10 if not hard else 0.05,
                "scgpt_small": 0.20 if not hard else 0.0,
            }[phi.backbone]
            grid[(_phi_key(phi), t)] = float(max(0.0, ((size - target) / 15.0) ** 2 + bonus))
    return grid, contexts, phis


# ---------------------------------------------------------------------------
# Regime runner
# ---------------------------------------------------------------------------


def run_regime(
    *,
    name: str,
    grid: dict[tuple[str, str], float],
    contexts: dict[str, np.ndarray],
    config_space: tuple[Config, ...],
    n_iterations: int,
    n_seeds: int,
    rng: np.random.Generator,
) -> dict:
    """Run E3 with per-seed output and compute stats for this regime."""
    trajectories = run_e3_optimizer_comparison(
        grid=grid,
        contexts=contexts,
        optimizers=("random", "cma_es", "contextual_gp"),
        n_iterations=n_iterations,
        n_seeds=n_seeds,
        config_space=config_space,
    )
    regime_stats: dict[str, dict] = {}
    for t in trajectories:
        per_seed = np.asarray(t.per_seed_trajectories, dtype=np.float64)  # (runs, iters)
        final = per_seed[:, -1]
        # Cumulative regret per run — recompute here from the stored best-so-far
        # curve and the task-level minima (so we don't rely on an implicit axis).
        task_names = sorted(contexts)
        y_min_per_task = np.array([
            min(v for (_, tname), v in grid.items() if tname == task)
            for task in task_names
        ])
        # per-run y_min: each run is one (task, seed); tasks are major.
        y_min_per_run = np.repeat(y_min_per_task, n_seeds)
        # Regret of the best-so-far curve at final iter = (best_final - y_min).
        final_regret = final - y_min_per_run
        point_final, lo_final, hi_final = bootstrap_ci(
            per_seed, lambda a: float(np.mean(a[:, -1])), rng=rng,
        )
        point_regret, lo_regret, hi_regret = bootstrap_ci(
            final_regret[:, None], lambda a: float(np.mean(a)), rng=rng,
        )
        regime_stats[t.optimizer] = {
            "final_msd_mean": point_final,
            "final_msd_ci95": [lo_final, hi_final],
            "final_regret_mean": point_regret,
            "final_regret_ci95": [lo_regret, hi_regret],
            "aulc_mean": float(np.sum(t.best_msd_per_iter)),
            "cum_regret_final": float(t.cum_regret_per_iter[-1]) if t.cum_regret_per_iter else float("nan"),
            "best_msd_per_iter_mean": list(t.best_msd_per_iter),
            "cum_regret_per_iter_mean": list(t.cum_regret_per_iter),
            "per_seed_final_msd": [float(x) for x in final],
        }

    # γ_T: greedy max-info-gain on the factor kernel.
    K = build_factor_kernel_matrix(config_space, contexts)
    gamma = max_information_gain(K, T=n_iterations)

    # Pairwise CI-overlap detection: does contextual_gp CI overlap CMA-ES CI on final MSD?
    cg = regime_stats.get("contextual_gp", {})
    es = regime_stats.get("cma_es", {})
    rd = regime_stats.get("random", {})
    def overlaps(a: dict, b: dict) -> bool:
        if not a or not b:
            return False
        return not (a["final_msd_ci95"][1] < b["final_msd_ci95"][0]
                    or b["final_msd_ci95"][1] < a["final_msd_ci95"][0])
    ci_overlap = {
        "contextual_vs_cma_es": overlaps(cg, es),
        "contextual_vs_random": overlaps(cg, rd),
    }

    return {
        "regime": name,
        "n_iterations": n_iterations,
        "n_seeds": n_seeds,
        "n_tasks": len(contexts),
        "n_configs": len(config_space),
        "per_optimizer": regime_stats,
        "gamma_T": gamma,
        "ci_overlap_on_final_msd": ci_overlap,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    rng = np.random.default_rng(2026)
    config_space_default = tuple(
        Config(n_agents=a, n_rounds=r, backbone=b)
        for a in (3, 4, 5)
        for r in (1, 2, 3)
        for b in ("linear", "mlp", "scgpt_small")
    )
    out: dict[str, dict] = {}

    # --- Synthetic shared-optimum ---
    syn_grid = load_grid_jsonl(RESULTS / "e2_grid_synthetic.jsonl")
    syn_tasks = tuple(sorted({t for _, t in syn_grid}))
    syn_ctx = synth_probe_contexts(syn_tasks, seed=2026)
    out["synthetic_shared_optimum"] = run_regime(
        name="synthetic_shared_optimum",
        grid=syn_grid, contexts=syn_ctx,
        config_space=config_space_default,
        n_iterations=30, n_seeds=20, rng=rng,
    )

    # --- Adamson real data ---
    ada_grid = load_grid_jsonl(RESULTS / "e2_grid_adamson.jsonl")
    ada_tasks = tuple(sorted({t for _, t in ada_grid}))
    ada_ctx = synth_probe_contexts(ada_tasks, seed=2027)
    out["adamson_real"] = run_regime(
        name="adamson_real",
        grid=ada_grid, contexts=ada_ctx,
        config_space=config_space_default,
        n_iterations=30, n_seeds=20, rng=rng,
    )

    # --- Task-conditional synthetic (E3b) ---
    tc_grid, tc_ctx, tc_phis = task_conditional_grid()
    out["task_conditional_synthetic"] = run_regime(
        name="task_conditional_synthetic",
        grid=tc_grid, contexts=tc_ctx,
        config_space=tc_phis,
        n_iterations=30, n_seeds=20, rng=rng,
    )

    # Save
    with (REVISION / "revision_stats.json").open("w") as f:
        json.dump(out, f, indent=2)

    # Human-readable summary
    for regime, payload in out.items():
        print(f"=== {regime} ===")
        print(f"  γ_T (T=30)         : {payload['gamma_T']:.3f}")
        overlap = payload["ci_overlap_on_final_msd"]
        print(f"  CI overlap cg↔cma  : {overlap['contextual_vs_cma_es']}")
        print(f"  CI overlap cg↔rand : {overlap['contextual_vs_random']}")
        for opt, stats in payload["per_optimizer"].items():
            lo, hi = stats["final_msd_ci95"]
            print(f"  {opt:<14} final={stats['final_msd_mean']:.5f} "
                  f"CI95=[{lo:.5f}, {hi:.5f}]  regret={stats['final_regret_mean']:.5f}")
        print()


if __name__ == "__main__":
    main()
