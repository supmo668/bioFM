"""Simulation study for the ACE/TDI/Bayesian-recommender paper.

Generates synthetic 5-agent run traces over a controlled task-difficulty
manifold, then runs the proposed metrics + Bayesian recommender end-to-end
and writes CSV summaries under paper/experiments/out/ that the plotting and
table-generation scripts consume.

All randomness is seeded. The DGP and its parameters are declared at the top
so reviewers can inspect the assumptions in one place.
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# Make the perturb_eval package importable without a full install.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from perturb_eval.bayesian import BayesianRecommender  # noqa: E402
from perturb_eval.calibration import fit_tdi_coefficients  # noqa: E402
from perturb_eval.metrics import (  # noqa: E402
    delta_ace,
    delta_mean_confidence,
    round_metrics,
    tdi,
    winner_flip_rate,
)
from perturb_eval.probe import ProbeSignature, signature_from_round  # noqa: E402
from perturb_eval.types import Config, RoundTrace, RunTrace  # noqa: E402

# ---------------------------------------------------------------------------
# DGP parameters — declared up-front so reviewers can audit assumptions.
# ---------------------------------------------------------------------------

DGP = dict(
    # Agent skill baselines per agent role (varies across tasks).
    skill_base_mean=0.55,
    skill_base_std=0.08,
    # Difficulty couples to (a) rate at which confidences rise, (b) critique
    # severity, (c) probability of a dominant specialist.
    convergence_rate_easy=0.15,
    convergence_rate_hard=-0.02,
    noise_std_confidence=0.05,
    noise_std_severity=0.08,
    severity_floor=0.0,
    severity_ceil=1.0,
    # Validation AUROC model (for extrinsic experiments).
    auroc_scale=8.0,
    backbone_factor={"scGPT": 1.0, "scPRINT-2": 1.3},
    # Config space enumerated in the paper.
    config_space=tuple(
        Config(n_agents=a, n_rounds=r, backbone=b)
        for a in (3, 5)
        for r in (1, 2, 3)
        for b in ("scGPT", "scPRINT-2")
    ),
)

AGENT_NAMES_5 = ("DataCurator", "Literature", "Architect", "Trainer", "Validator")


# ---------------------------------------------------------------------------
# Synthetic DGP
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Task:
    """A single synthetic task with a known ground-truth difficulty."""

    task_id: str
    difficulty: float      # d ∈ [0, 1]; 0 = easy, 1 = hard
    specialist_idx: int    # which agent (if any) is the natural lead


def sample_task(rng: np.random.Generator, task_id: str) -> Task:
    d = float(rng.uniform(0.0, 1.0))
    # Probability that a clear specialist exists scales inversely with d.
    has_specialist = rng.uniform() < (1.0 - d * 0.8)
    specialist = int(rng.integers(0, 5)) if has_specialist else -1
    return Task(task_id=task_id, difficulty=d, specialist_idx=specialist)


def simulate_run(
    task: Task,
    n_agents: int,
    n_rounds: int,
    rng: np.random.Generator,
    agent_names: tuple[str, ...] = AGENT_NAMES_5,
) -> RunTrace:
    """Simulate one run of the orchestrator on a given task.

    ``n_agents`` is allowed to be < or > len(agent_names); we generate generic
    names ``A0..A{n-1}`` if we need to exceed 5.
    """
    if n_agents > len(agent_names):
        names = tuple(f"Agent{i}" for i in range(n_agents))
    else:
        names = agent_names[:n_agents]

    d = task.difficulty
    rate_mean = (1 - d) * DGP["convergence_rate_easy"] + d * DGP["convergence_rate_hard"]

    # Per-agent baseline skill + per-agent convergence rate, sampled per task.
    skills = rng.normal(DGP["skill_base_mean"], DGP["skill_base_std"], size=n_agents)
    rates = rng.normal(rate_mean, 0.03, size=n_agents)

    # Optional specialist boost.
    if 0 <= task.specialist_idx < n_agents:
        skills[task.specialist_idx] += 0.10 * (1 - d)

    # Per-agent critique strictness.
    strictness = np.clip(rng.normal(0.1 + 0.35 * d, 0.1, size=n_agents), 0.0, 1.0)

    rounds: list[RoundTrace] = []
    for r in range(n_rounds):
        # Confidences rise with r at rate that depends on d.
        noise = rng.normal(0, DGP["noise_std_confidence"], size=n_agents)
        raw_conf = skills + rates * r + noise
        # Hard tasks inject extra flatness — pull everyone toward the mean.
        if d > 0.5:
            flat_pull = 0.5 * (d - 0.5) * 2  # 0 at d=0.5, 1 at d=1.0
            raw_conf = (1 - flat_pull) * raw_conf + flat_pull * np.mean(raw_conf)
        conf = np.clip(raw_conf, 0.0, 1.0)

        # Critique severity: low-confidence targets attract more severity.
        # S[i,j] = strictness_i + (1 - conf_j) * coupling + noise
        sev_noise = rng.normal(0, DGP["noise_std_severity"], size=(n_agents, n_agents))
        base = strictness[:, None] + (1.0 - conf[None, :]) * (0.6 * d + 0.1) + sev_noise
        sev = np.clip(base, DGP["severity_floor"], DGP["severity_ceil"])
        # Project onto the (n_agents × n_agents-1) off-diagonal row-form.
        rows: list[tuple[float, ...]] = []
        for i in range(n_agents):
            row = [float(sev[i, j]) for j in range(n_agents) if j != i]
            rows.append(tuple(row))

        # Winner: confidence minus mean severity received.
        mean_rec = np.zeros(n_agents)
        for j in range(n_agents):
            vals = [sev[i, j] for i in range(n_agents) if i != j]
            mean_rec[j] = float(np.mean(vals)) if vals else 0.0
        scores = conf - mean_rec
        winner = int(np.argmax(scores))
        consensus = float(scores[winner])

        rounds.append(
            RoundTrace(
                round_index=r,
                agent_names=names,
                confidences=tuple(float(c) for c in conf),
                critique_severities=tuple(rows),
                winner_index=winner,
                consensus_score=consensus,
            )
        )

    return RunTrace(task_id=task.task_id, rounds=tuple(rounds),
                    converged=rounds[-1].consensus_score > 0.5,
                    backbone="scGPT")


# ---------------------------------------------------------------------------
# Validation AUROC model — how well the team's output predicts held-out response.
# ---------------------------------------------------------------------------

def simulate_auroc(
    difficulty: float,
    n_agents: int,
    n_rounds: int,
    backbone: str,
    rng: np.random.Generator,
) -> float:
    """Simulate downstream validation AUROC.

    Easier tasks saturate AUROC at ~1.0 with small compute; harder tasks plateau
    at 0.5 regardless of compute. The functional form is a saturating
    exponential in ``n_agents × n_rounds × backbone_factor``.
    """
    b = DGP["backbone_factor"].get(backbone, 1.0)
    saturation = 1.0 - math.exp(-(n_agents * n_rounds * b) / DGP["auroc_scale"])
    max_attainable = 0.5 + (0.5 - 0.5 * difficulty)
    auroc = 0.5 + (max_attainable - 0.5) * saturation
    return float(np.clip(auroc + rng.normal(0, 0.01), 0.0, 1.0))


# ---------------------------------------------------------------------------
# Experiment runners
# ---------------------------------------------------------------------------

def run_experiment_1_metric_validation(
    rng: np.random.Generator,
    n_tasks: int,
    out_dir: Path,
) -> None:
    """E1: Do our metrics rank task difficulty?"""
    rows: list[dict[str, float]] = []
    for i in range(n_tasks):
        task = sample_task(rng, task_id=f"t{i}")
        trace = simulate_run(task, n_agents=5, n_rounds=3, rng=rng)
        per_round = tuple(round_metrics(r) for r in trace.rounds)
        rows.append({
            "task_id": task.task_id,
            "difficulty": task.difficulty,
            "ace_norm_final": per_round[-1].ace_norm,
            "csd_final": per_round[-1].csd,
            "mean_conf_final": per_round[-1].mean_confidence,
            "delta_ace": delta_ace(per_round),
            "delta_c": delta_mean_confidence(per_round),
            "wfr": winner_flip_rate(per_round),
            "consensus_final": per_round[-1].consensus_score,
            "tdi": tdi(per_round),
            "probe_ace": per_round[0].ace_norm,
            "probe_meanC": per_round[0].mean_confidence,
            "probe_maxC": per_round[0].max_confidence,
            "probe_csd": per_round[0].csd,
        })
    _write_csv(out_dir / "e1_metric_validation.csv", rows)


def run_experiment_2_probe_to_tdi(
    rng: np.random.Generator,
    n_tasks: int,
    out_dir: Path,
) -> None:
    """E2: Does a round-0 probe predict post-hoc TDI?

    We reuse the E1 table but additionally fit a held-out regressor probe→TDI.
    This is just an analysis step on E1 data; the CSV we emit contains the
    split indicator and the fitted prediction.
    """
    rows = _read_csv(out_dir / "e1_metric_validation.csv")
    if not rows:
        return
    n = len(rows)
    test_mask = np.zeros(n, dtype=bool)
    test_idx = rng.choice(n, size=max(1, n // 5), replace=False)
    test_mask[test_idx] = True

    X = np.array([[float(r["probe_ace"]), float(r["probe_meanC"]),
                   float(r["probe_maxC"]), float(r["probe_csd"])] for r in rows])
    y = np.array([float(r["tdi"]) for r in rows])

    # Ridge regression with λ=0.05.
    Xtr, ytr = X[~test_mask], y[~test_mask]
    lam = 0.05
    A = Xtr.T @ Xtr + lam * np.eye(Xtr.shape[1])
    b = Xtr.T @ ytr
    w = np.linalg.solve(A, b)
    y_pred = X @ w

    # R² on the test split.
    ss_res = float(np.sum((y[test_mask] - y_pred[test_mask]) ** 2))
    ss_tot = float(np.sum((y[test_mask] - y[test_mask].mean()) ** 2))
    r2_test = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    out_rows = []
    for i, r in enumerate(rows):
        out_rows.append({
            **r,
            "split": "test" if test_mask[i] else "train",
            "tdi_pred": float(y_pred[i]),
        })
    _write_csv(out_dir / "e2_probe_to_tdi.csv", out_rows)

    meta = out_dir / "e2_probe_to_tdi_meta.csv"
    _write_csv(meta, [{"r2_test": r2_test, "coef_ace": float(w[0]),
                       "coef_meanC": float(w[1]), "coef_maxC": float(w[2]),
                       "coef_csd": float(w[3]), "n_test": int(test_mask.sum())}])


def run_experiment_3_pareto(
    rng: np.random.Generator,
    n_tasks: int,
    out_dir: Path,
) -> None:
    """E3: Pareto frontier — uniform vs. minimal vs. Bayesian-adaptive policy."""
    configs = DGP["config_space"]
    # Step 1: on a calibration half, record the minimal config that reaches a
    # 95% fraction of the full-team AUROC on each task. That becomes the
    # "observed optimal" φ* used by the Bayesian recommender.
    tasks = [sample_task(rng, task_id=f"t{i}") for i in range(n_tasks)]
    cal_idx = rng.choice(n_tasks, size=n_tasks // 2, replace=False)
    cal_mask = np.zeros(n_tasks, dtype=bool)
    cal_mask[cal_idx] = True

    probes: list[ProbeSignature] = []
    optimal: list[Config] = []
    for i, t in enumerate(tasks):
        if not cal_mask[i]:
            continue
        # Probe = round 0 of a shallow (3 agents, 1 round) run.
        probe_trace = simulate_run(t, n_agents=3, n_rounds=1, rng=rng)
        sig = signature_from_round(probe_trace.rounds[0])
        # Ground truth: record AUROC for every config, find the smallest that
        # reaches ≥ 95% of the best.
        aurocs = {
            c: simulate_auroc(t.difficulty, c.n_agents, c.n_rounds, c.backbone, rng)
            for c in configs
        }
        best = max(aurocs.values())
        target = 0.95 * best
        feasible = [c for c, a in aurocs.items() if a >= target]
        feasible.sort(key=lambda c: c.flops_proxy())
        phi_star = feasible[0] if feasible else max(configs, key=lambda c: aurocs[c])
        probes.append(sig)
        optimal.append(phi_star)

    recommender = BayesianRecommender(config_space=configs).fit(list(zip(probes, optimal, strict=True)))

    # Step 2: on the held-out half, score each policy under a range of budgets.
    max_budget = max(c.flops_proxy() for c in configs)
    min_budget = min(c.flops_proxy() for c in configs)
    budgets = list(range(min_budget, max_budget + 1))
    rows: list[dict[str, float]] = []
    for b_budget in budgets:
        u_sum, m_sum, a_sum = 0.0, 0.0, 0.0
        u_flops, m_flops, a_flops = 0, 0, 0
        n_eval = 0
        # Uniform: largest config under budget
        uniform_cfg = max(
            (c for c in configs if c.flops_proxy() <= b_budget),
            key=lambda c: c.flops_proxy(),
            default=configs[0],
        )
        # Minimal: smallest config always
        minimal_cfg = min(configs, key=lambda c: c.flops_proxy())

        for i, t in enumerate(tasks):
            if cal_mask[i]:
                continue
            probe_trace = simulate_run(t, n_agents=3, n_rounds=1, rng=rng)
            sig = signature_from_round(probe_trace.rounds[0])
            rec = recommender.recommend(sig, budget=b_budget)
            adaptive_cfg = rec.config

            u_sum += simulate_auroc(t.difficulty, uniform_cfg.n_agents, uniform_cfg.n_rounds, uniform_cfg.backbone, rng)
            m_sum += simulate_auroc(t.difficulty, minimal_cfg.n_agents, minimal_cfg.n_rounds, minimal_cfg.backbone, rng)
            a_sum += simulate_auroc(t.difficulty, adaptive_cfg.n_agents, adaptive_cfg.n_rounds, adaptive_cfg.backbone, rng)
            u_flops += uniform_cfg.flops_proxy()
            m_flops += minimal_cfg.flops_proxy()
            a_flops += adaptive_cfg.flops_proxy()
            n_eval += 1

        rows.append({
            "budget": b_budget,
            "uniform_mean_auroc": u_sum / max(1, n_eval),
            "minimal_mean_auroc": m_sum / max(1, n_eval),
            "adaptive_mean_auroc": a_sum / max(1, n_eval),
            "uniform_mean_flops": u_flops / max(1, n_eval),
            "minimal_mean_flops": m_flops / max(1, n_eval),
            "adaptive_mean_flops": a_flops / max(1, n_eval),
        })
    _write_csv(out_dir / "e3_pareto.csv", rows)


def run_experiment_4_agent_scaling(
    rng: np.random.Generator,
    n_tasks_per_setting: int,
    out_dir: Path,
) -> None:
    """E4: How does mean AUROC scale with the number of task agents?"""
    agent_counts = (2, 3, 4, 5, 6, 8, 10)
    rounds_fixed = 2
    tiers = (("easy", 0.1, 0.3), ("medium", 0.4, 0.6), ("hard", 0.7, 0.9))

    rows: list[dict[str, float]] = []
    for tier_name, lo, hi in tiers:
        for n in agent_counts:
            aurocs = []
            for i in range(n_tasks_per_setting):
                d = float(rng.uniform(lo, hi))
                task = Task(task_id=f"{tier_name}_{n}_{i}", difficulty=d, specialist_idx=-1)
                a = simulate_auroc(d, n, rounds_fixed, "scGPT", rng)
                aurocs.append(a)
                # Also simulate the actual run so per-round dynamics exist; we
                # don't use the trace here but it validates the DGP shape.
                _ = simulate_run(task, n_agents=n, n_rounds=rounds_fixed, rng=rng)
            arr = np.asarray(aurocs)
            rows.append({
                "tier": tier_name,
                "n_agents": n,
                "mean_auroc": float(arr.mean()),
                "sem_auroc": float(arr.std(ddof=1) / math.sqrt(len(arr))) if len(arr) > 1 else 0.0,
                "flops": n * rounds_fixed,
            })
    _write_csv(out_dir / "e4_agent_scaling.csv", rows)


def run_experiment_1b_tdi_calibration(
    rng: np.random.Generator,
    out_dir: Path,
) -> None:
    """E1b: Calibrate TDI coefficients on a train split and report test-set fit.

    The default coefficients are chosen heuristically and (as E1 shows) don't
    weight the strongest empirical signal enough. This experiment quantifies
    how much a data-driven fit improves TDI's agreement with the ground-truth
    difficulty label — the paper's main practical argument for the calibration
    harness.
    """
    rows = _read_csv(out_dir / "e1_metric_validation.csv")
    if not rows:
        return
    X = np.array([
        [float(r["ace_norm_final"]),
         float(r["csd_final"]),
         1.0 - max(0.0, min(1.0, float(r["delta_c"]))),
         float(r["wfr"])]
        for r in rows
    ])
    d = np.array([float(r["difficulty"]) for r in rows])
    n = X.shape[0]
    idx = rng.permutation(n)
    cut = int(0.8 * n)
    tr = idx[:cut]
    te = idx[cut:]

    # Default coefficients (from metrics.DEFAULT_TDI_COEFFS).
    default_w = np.array([0.35, 0.25, 0.25, 0.15])
    default_pred = X @ default_w
    # Ridge-fit coefficients on the training split.
    lam = 0.1
    A = X[tr].T @ X[tr] + lam * np.eye(X.shape[1])
    b = X[tr].T @ d[tr]
    w_fit = np.linalg.solve(A, b)
    w_fit = np.clip(w_fit, 0.0, None)
    if w_fit.sum() > 0:
        w_fit = w_fit / w_fit.sum()
    fit_pred = X @ w_fit

    # Metrics on the test split.
    out = {
        "default_r2_test": _r2(default_pred[te], d[te]),
        "default_spearman_test": _spearman(default_pred[te], d[te]),
        "calibrated_r2_test": _r2(fit_pred[te], d[te]),
        "calibrated_spearman_test": _spearman(fit_pred[te], d[te]),
        "calibrated_alpha": float(w_fit[0]),
        "calibrated_beta": float(w_fit[1]),
        "calibrated_gamma": float(w_fit[2]),
        "calibrated_delta": float(w_fit[3]),
        "n_train": int(len(tr)),
        "n_test": int(len(te)),
    }
    _write_csv(out_dir / "e1b_tdi_calibration.csv", [out])


def run_experiment_2b_probe_to_difficulty(
    rng: np.random.Generator,
    out_dir: Path,
) -> None:
    """E2b: Regress the round-0 probe signature directly against difficulty.

    E2 shows probe→TDI is weak because TDI depends on round-over-round signals
    the probe doesn't see. But the probe might predict the *latent* difficulty
    directly — that's what actually matters for the recommender.
    """
    rows = _read_csv(out_dir / "e1_metric_validation.csv")
    if not rows:
        return
    X = np.array([
        [float(r["probe_ace"]), float(r["probe_meanC"]),
         float(r["probe_maxC"]), float(r["probe_csd"])]
        for r in rows
    ])
    d = np.array([float(r["difficulty"]) for r in rows])
    n = X.shape[0]
    idx = rng.permutation(n)
    cut = int(0.8 * n)
    tr, te = idx[:cut], idx[cut:]
    lam = 0.05
    A = X[tr].T @ X[tr] + lam * np.eye(X.shape[1])
    b = X[tr].T @ d[tr]
    w = np.linalg.solve(A, b)
    pred = X @ w

    out = {
        "probe_to_d_r2_test": _r2(pred[te], d[te]),
        "probe_to_d_spearman_test": _spearman(pred[te], d[te]),
        "w_ace": float(w[0]), "w_meanC": float(w[1]),
        "w_maxC": float(w[2]), "w_csd": float(w[3]),
        "n_train": int(len(tr)), "n_test": int(len(te)),
    }
    _write_csv(out_dir / "e2b_probe_to_difficulty.csv", [out])


def run_experiment_5_tdi_ablation(
    rng: np.random.Generator,
    out_dir: Path,
) -> None:
    """E5: Which of (α, β, γ, δ) does the heavy lifting in TDI?"""
    e1_rows = _read_csv(out_dir / "e1_metric_validation.csv")
    if not e1_rows:
        return
    # Build (run_trace_features, label) style data. We already computed the
    # relevant features in E1; regress difficulty against single-feature TDIs.
    d = np.array([float(r["difficulty"]) for r in e1_rows])
    feats = {
        "ace_norm": np.array([float(r["ace_norm_final"]) for r in e1_rows]),
        "csd": np.array([float(r["csd_final"]) for r in e1_rows]),
        "lack_of_convergence": np.array(
            [1.0 - max(0.0, min(1.0, float(r["delta_c"]))) for r in e1_rows]
        ),
        "wfr": np.array([float(r["wfr"]) for r in e1_rows]),
    }
    rows: list[dict[str, float]] = []
    for name, x in feats.items():
        # Univariate linear regression against d.
        xm = x.mean(); dm = d.mean()
        num = float(np.sum((x - xm) * (d - dm)))
        den = float(np.sum((x - xm) ** 2))
        slope = num / den if den > 0 else 0.0
        intercept = dm - slope * xm
        pred = slope * x + intercept
        ss_res = float(np.sum((d - pred) ** 2))
        ss_tot = float(np.sum((d - dm) ** 2))
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
        # Also the Spearman rank correlation of the raw feature with d.
        rho = _spearman(x, d)
        rows.append({"feature": name, "r2": r2, "spearman": rho, "slope": slope})

    # Full TDI correlation for comparison.
    tdi_vals = np.array([float(r["tdi"]) for r in e1_rows])
    rows.append({
        "feature": "TDI_full",
        "r2": _r2(tdi_vals, d),
        "spearman": _spearman(tdi_vals, d),
        "slope": float("nan"),
    })
    _write_csv(out_dir / "e5_tdi_ablation.csv", rows)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    keys = list(rows[0].keys())
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open() as fh:
        return list(csv.DictReader(fh))


def _spearman(x: np.ndarray, y: np.ndarray) -> float:
    """Pearson on rank-transformed values — equivalent to Spearman ρ."""
    xr = np.argsort(np.argsort(x))
    yr = np.argsort(np.argsort(y))
    return _pearson(xr.astype(float), yr.astype(float))


def _pearson(x: np.ndarray, y: np.ndarray) -> float:
    xm = x - x.mean()
    ym = y - y.mean()
    denom = math.sqrt(float(np.sum(xm * xm) * np.sum(ym * ym)))
    return float(np.sum(xm * ym) / denom) if denom > 0 else 0.0


def _r2(pred: np.ndarray, target: np.ndarray) -> float:
    ss_res = float(np.sum((target - pred) ** 2))
    ss_tot = float(np.sum((target - target.mean()) ** 2))
    return 1 - ss_res / ss_tot if ss_tot > 0 else 0.0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--n-tasks", type=int, default=300)
    ap.add_argument("--n-pareto-tasks", type=int, default=200)
    ap.add_argument("--n-tasks-per-setting", type=int, default=50)
    ap.add_argument("--out", type=Path,
                    default=Path(__file__).resolve().parent / "out")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(args.seed)

    print("[E1] metric validation —", args.n_tasks, "tasks")
    run_experiment_1_metric_validation(rng, args.n_tasks, args.out)
    print("[E1b] calibrated TDI")
    run_experiment_1b_tdi_calibration(rng, args.out)
    print("[E2] probe → TDI regression")
    run_experiment_2_probe_to_tdi(rng, args.n_tasks, args.out)
    print("[E2b] probe → difficulty direct")
    run_experiment_2b_probe_to_difficulty(rng, args.out)
    print("[E3] Pareto frontier —", args.n_pareto_tasks, "tasks")
    run_experiment_3_pareto(rng, args.n_pareto_tasks, args.out)
    print("[E4] agent-count scaling —", args.n_tasks_per_setting, "tasks/setting")
    run_experiment_4_agent_scaling(rng, args.n_tasks_per_setting, args.out)
    print("[E5] TDI single-feature ablation")
    run_experiment_5_tdi_ablation(rng, args.out)
    print("Wrote CSVs into", args.out)


if __name__ == "__main__":
    main()
