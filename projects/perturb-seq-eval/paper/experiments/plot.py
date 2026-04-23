"""Generate all figures for the paper from the CSVs simulate.py writes.

Output goes to paper/figures/ as PNG (for quick inspection) and PDF (for the
LaTeX includegraphics). Figures are intentionally small and print-safe —
single-column NeurIPS-ish.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")  # no interactive backend needed
import matplotlib.pyplot as plt  # noqa: E402


HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
FIG = HERE.parent / "figures"


def _load(name: str) -> list[dict[str, str]]:
    p = OUT / name
    if not p.exists():
        raise FileNotFoundError(p)
    with p.open() as fh:
        return list(csv.DictReader(fh))


def _save(fig: plt.Figure, name: str) -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"{name}.{ext}", bbox_inches="tight", dpi=150)
    plt.close(fig)


def fig1_tdi_vs_difficulty() -> None:
    rows = _load("e1_metric_validation.csv")
    d = np.array([float(r["difficulty"]) for r in rows])
    tdi = np.array([float(r["tdi"]) for r in rows])
    ace = np.array([float(r["ace_norm_final"]) for r in rows])
    lack = np.array([1.0 - max(0.0, min(1.0, float(r["delta_c"]))) for r in rows])

    fig, axes = plt.subplots(1, 3, figsize=(9.5, 2.8), sharey=False)
    for ax, y, label in zip(
        axes,
        [tdi, ace, lack],
        ["TDI (default)", "ACE$_{\\mathrm{norm}}$ (final round)",
         "Lack of convergence $1-\\Delta C$"],
        strict=True,
    ):
        ax.scatter(d, y, s=6, alpha=0.55, color="#2b6cb0")
        ax.set_xlabel("Ground-truth difficulty $d$")
        ax.set_ylabel(label)
        ax.set_xlim(0, 1)
        ax.grid(alpha=0.3, linestyle=":")
    fig.tight_layout()
    _save(fig, "fig1_metric_vs_difficulty")


def fig2_calibration_gain() -> None:
    rows = _load("e1b_tdi_calibration.csv")
    r = rows[0]
    default_sp = float(r["default_spearman_test"])
    calib_sp = float(r["calibrated_spearman_test"])

    abl = _load("e5_tdi_ablation.csv")
    names = [x["feature"].replace("_", " ") for x in abl]
    sp = [float(x["spearman"]) for x in abl]

    fig, axes = plt.subplots(1, 2, figsize=(9.5, 2.9))
    axes[0].bar(
        ["Default\ncoefficients", "Calibrated\n(ridge fit)"],
        [default_sp, calib_sp],
        color=["#a0aec0", "#2b6cb0"],
    )
    axes[0].set_ylabel("Test-set Spearman $\\rho(\\mathrm{TDI}, d)$")
    axes[0].set_ylim(-0.1, 1.0)
    axes[0].axhline(0.0, color="k", linewidth=0.5)
    axes[0].grid(axis="y", alpha=0.3, linestyle=":")
    for i, v in enumerate([default_sp, calib_sp]):
        axes[0].text(i, v + 0.02, f"{v:.2f}", ha="center", va="bottom", fontsize=9)

    order = np.argsort(sp)
    axes[1].barh(
        [names[i] for i in order],
        [sp[i] for i in order],
        color=["#e53e3e" if sp[i] < 0.2 else "#2b6cb0" for i in order],
    )
    axes[1].set_xlabel("Spearman $\\rho$ with difficulty $d$")
    axes[1].set_xlim(0, 1.0)
    axes[1].grid(axis="x", alpha=0.3, linestyle=":")
    fig.tight_layout()
    _save(fig, "fig2_calibration_and_ablation")


def fig3_pareto() -> None:
    rows = _load("e3_pareto.csv")
    b = np.array([float(r["budget"]) for r in rows])
    for key, label, colour, marker in [
        ("uniform_mean_auroc", "Uniform (largest under budget)", "#dd6b20", "s"),
        ("minimal_mean_auroc", "Minimal (always smallest)", "#a0aec0", "^"),
        ("adaptive_mean_auroc", "Adaptive (Bayesian probe)", "#2b6cb0", "o"),
    ]:
        y = np.array([float(r[key]) for r in rows])
        plt.plot(b, y, marker=marker, linewidth=1.2, label=label, color=colour,
                 markersize=4)
    plt.xlabel("Compute budget (FLOPs proxy)")
    plt.ylabel("Mean held-out AUROC")
    plt.grid(alpha=0.3, linestyle=":")
    plt.legend(fontsize=9, loc="lower right")
    fig = plt.gcf()
    fig.set_size_inches(5.8, 3.0)
    fig.tight_layout()
    _save(fig, "fig3_pareto")


def fig4_agent_scaling() -> None:
    rows = _load("e4_agent_scaling.csv")
    tiers = ["easy", "medium", "hard"]
    colours = {"easy": "#38a169", "medium": "#d69e2e", "hard": "#c53030"}
    for t in tiers:
        sub = [r for r in rows if r["tier"] == t]
        sub.sort(key=lambda r: int(r["n_agents"]))
        n = np.array([int(r["n_agents"]) for r in sub])
        mu = np.array([float(r["mean_auroc"]) for r in sub])
        sem = np.array([float(r["sem_auroc"]) for r in sub])
        plt.errorbar(n, mu, yerr=sem, marker="o", capsize=3, linewidth=1.2,
                     label=f"{t}", color=colours[t])
    plt.xlabel("Number of task agents $N$")
    plt.ylabel("Mean held-out AUROC (rounds $R=2$)")
    plt.grid(alpha=0.3, linestyle=":")
    plt.legend(title="Difficulty tier", fontsize=9)
    fig = plt.gcf()
    fig.set_size_inches(5.8, 3.2)
    fig.tight_layout()
    _save(fig, "fig4_agent_scaling")


def fig5_probe_to_difficulty() -> None:
    rows = _load("e1_metric_validation.csv")
    d = np.array([float(r["difficulty"]) for r in rows])
    X = np.array([
        [float(r["probe_ace"]), float(r["probe_meanC"]),
         float(r["probe_maxC"]), float(r["probe_csd"])]
        for r in rows
    ])
    # Refit ridge on all data for plotting a smooth predicted-vs-actual line.
    lam = 0.05
    A = X.T @ X + lam * np.eye(X.shape[1])
    w = np.linalg.solve(A, X.T @ d)
    pred = X @ w

    fig, ax = plt.subplots(1, 1, figsize=(4.8, 3.2))
    ax.scatter(d, pred, s=7, alpha=0.55, color="#2b6cb0")
    xx = np.linspace(0, 1, 30)
    ax.plot(xx, xx, "k--", linewidth=0.7, label="$y = x$")
    ax.set_xlabel("Ground-truth difficulty $d$")
    ax.set_ylabel("Probe$\\to d$ ridge prediction")
    ax.set_xlim(0, 1)
    ax.set_ylim(min(pred.min(), 0) - 0.05, max(pred.max(), 1) + 0.05)
    ax.grid(alpha=0.3, linestyle=":")
    ax.legend(fontsize=9, loc="lower right")
    fig.tight_layout()
    _save(fig, "fig5_probe_to_difficulty")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.parse_args()
    fig1_tdi_vs_difficulty()
    fig2_calibration_gain()
    fig3_pareto()
    fig4_agent_scaling()
    fig5_probe_to_difficulty()
    print("wrote figures into", FIG)


if __name__ == "__main__":
    main()
