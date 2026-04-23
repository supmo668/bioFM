"""Regenerate all five figures with CI bands + Wong colourblind-safe palette.

Consumes ``artifacts/modal_run/revision/revision_stats.json`` (output of
``bootstrap_and_analyze.py``) plus the cached E2 grid JSONLs.

Outputs PNG+PDF+HTML into ``artifacts/modal_run/figures/`` alongside the
v1 figures. Overwrites `fig[2-4]_*.png` with the CI-banded versions;
fig1 (Spearman heatmap) and fig5 (backbone MSD) are regenerated only to
apply the Wong palette consistently.

Closes mc9 (colourblind-safe) and supports MC1 (CIs visible on the
trajectory figures).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go


# Wong / Okabe-Ito palette — colourblind-safe.
WONG = {
    "random": "#999999",          # grey
    "cma_es": "#E69F00",           # orange
    "one_plus_lambda_es": "#E69F00",  # alias
    "contextual_gp": "#56B4E9",    # sky blue
    "linear": "#009E73",           # bluish green
    "mlp": "#F0E442",              # yellow
    "scgpt_small": "#0072B2",      # blue
    "synthetic": "#CC79A7",        # purple (for the box plot)
    "adamson": "#D55E00",          # vermillion
}


RESULTS = Path("artifacts/modal_run/results")
REVISION = Path("artifacts/modal_run/revision")
FIG_DIR = Path("artifacts/modal_run/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)


def _save(fig: go.Figure, name: str) -> None:
    fig.write_image(str(FIG_DIR / f"{name}.png"), scale=2)
    fig.write_image(str(FIG_DIR / f"{name}.pdf"))
    fig.write_html(str(FIG_DIR / f"{name}.html"))


def fig1_metric_heatmap() -> None:
    e1 = json.loads((RESULTS / "e1_overlap.json").read_text())
    rho = np.asarray(e1["spearman_matrix"])
    names = e1["feature_names"]
    fig = go.Figure(data=go.Heatmap(
        z=rho, x=names, y=names, colorscale="RdBu", zmid=0, zmin=-1, zmax=1,
        text=[[f"{v:.2f}" for v in row] for row in rho],
        texttemplate="%{text}", textfont={"size": 11},
        colorbar_title="Spearman ρ",
    ))
    fig.update_layout(
        title=(
            f"Figure 1 — Metric overlap, Spearman ρ on n={e1['n_traces']} synthetic traces"
        ),
        xaxis_title="metric", yaxis_title="metric",
        template="simple_white", width=720, height=640,
    )
    _save(fig, "fig1_metric_heatmap")


def _trajectory_fig_with_ci(
    regime_key: str,
    title: str,
    out: str,
) -> None:
    rev = json.loads((REVISION / "revision_stats.json").read_text())
    payload = rev[regime_key]
    n_iter = payload["n_iterations"]
    n_seeds = payload["n_seeds"]
    n_tasks = payload["n_tasks"]
    iters = list(range(1, n_iter + 1))
    fig = go.Figure()
    for opt, stats in payload["per_optimizer"].items():
        mean = stats["best_msd_per_iter_mean"]
        per_seed_final = np.asarray(stats["per_seed_final_msd"])
        # Band: iteration-wise CI approximated by the final-step CI width
        # scaled to each iter's mean. This is an approximation — the
        # authoritative per-iter CIs would need per-(iter, run) bootstrap,
        # which the revision script can easily emit if needed.
        ci_width = (stats["final_msd_ci95"][1] - stats["final_msd_ci95"][0]) / 2.0
        mean_arr = np.asarray(mean)
        upper = (mean_arr + ci_width).tolist()
        lower = (mean_arr - ci_width).tolist()
        color = WONG.get(opt, "#000000")
        # Upper bound (transparent, for fill)
        fig.add_trace(go.Scatter(
            x=iters + iters[::-1],
            y=upper + lower[::-1],
            fill="toself",
            fillcolor=f"rgba{(*_hex_to_rgb(color), 0.12)}",
            line=dict(color="rgba(0,0,0,0)"),
            hoverinfo="skip",
            showlegend=False,
            name=f"{opt} CI",
        ))
        fig.add_trace(go.Scatter(
            x=iters, y=mean,
            mode="lines+markers", name=opt,
            line=dict(color=color, width=2),
            marker=dict(size=5, color=color),
        ))
    fig.update_layout(
        title=f"{title}<br><sub>bands = ±½·CI95 of final-step bootstrap "
              f"(n_tasks={n_tasks}, n_seeds={n_seeds})</sub>",
        xaxis_title="iteration", yaxis_title="best MSD so far (↓ better)",
        template="simple_white", width=720, height=520,
        legend=dict(x=0.68, y=0.98, bgcolor="rgba(255,255,255,0.9)"),
    )
    _save(fig, out)


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def fig2_synthetic() -> None:
    _trajectory_fig_with_ci(
        "synthetic_shared_optimum",
        "Figure 2 — E3 (synthetic shared-optimum): best MSD vs iteration (CIs added)",
        "fig2_e3_synthetic",
    )


def fig3_adamson() -> None:
    _trajectory_fig_with_ci(
        "adamson_real",
        "Figure 3 — E3 (Adamson real data): best MSD vs iteration (CIs added)",
        "fig3_e3_adamson",
    )


def fig4_task_conditional() -> None:
    _trajectory_fig_with_ci(
        "task_conditional_synthetic",
        "Figure 4 — E3b (task-conditional synthetic): contextual GP dominates (CIs added)",
        "fig4_e3b_task_conditional",
    )


def fig5_backbone_msd() -> None:
    rows: list[dict] = []
    for src_name, path in (
        ("synthetic", RESULTS / "e2_grid_synthetic.jsonl"),
        ("adamson", RESULTS / "e2_grid_adamson.jsonl"),
    ):
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                row["source"] = src_name
                rows.append(row)
    df = pd.DataFrame(rows)
    fig = go.Figure()
    for src in ["synthetic", "adamson"]:
        sub = df[df["source"] == src]
        for bb in sorted(sub["backbone_name"].unique()):
            vals = sub.loc[sub["backbone_name"] == bb, "msd_topk"].values
            fig.add_trace(go.Box(
                y=vals.tolist(),
                x=[bb] * len(vals),
                name=src,
                marker_color=WONG.get(src, "#000000"),
                boxpoints="outliers",
                offsetgroup=src,
                legendgroup=src,
                showlegend=bb == "linear",
            ))
    fig.update_layout(
        title="Figure 5 — Per-backbone held-out MSD across grids (Wong palette)",
        xaxis_title="backbone", yaxis_title="MSD on top-20 DEGs",
        template="simple_white", width=720, height=480, boxmode="group",
    )
    _save(fig, "fig5_backbone_msd")


def main() -> None:
    fig1_metric_heatmap()
    fig2_synthetic()
    fig3_adamson()
    fig4_task_conditional()
    fig5_backbone_msd()
    print(f"Wrote {sum(1 for _ in FIG_DIR.iterdir())} files into {FIG_DIR.resolve()}")


if __name__ == "__main__":
    main()
