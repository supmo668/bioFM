"""Render the five supplement figures as PNG from cached Modal JSON.

Runs locally off the committed ``artifacts/modal_run/results/*.json`` and
writes PNG+PDF+HTML alongside the existing Modal-generated artifacts so
that markdown viewers (GitHub, VS Code preview) can render them inline.

PNG is the format reviewers and journal editors expect; PDF is retained
for the LaTeX compile.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


RESULTS = Path("artifacts/modal_run/results")
FIG_DIR = Path("artifacts/modal_run/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)


def _save(fig: go.Figure, name: str) -> None:
    """Write every format we need."""
    for ext, scale in (("png", 2), ("pdf", 1)):
        fig.write_image(str(FIG_DIR / f"{name}.{ext}"), scale=scale)
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
        title=f"Figure 1 — Metric overlap, Spearman ρ on n={e1['n_traces']} synthetic traces",
        xaxis_title="metric", yaxis_title="metric",
        template="simple_white", width=720, height=640,
    )
    _save(fig, "fig1_metric_heatmap")


def _traj_fig(path: Path, title: str, out: str) -> None:
    data = json.loads(path.read_text())["trajectories"]
    fig = go.Figure()
    for t in data:
        y = t["best_msd_per_iter"]
        fig.add_trace(go.Scatter(
            x=list(range(1, len(y) + 1)),
            y=y,
            mode="lines+markers",
            name=t["optimizer"],
        ))
    fig.update_layout(
        title=title,
        xaxis_title="iteration", yaxis_title="best MSD so far (↓ better)",
        template="simple_white", width=720, height=480,
        legend=dict(x=0.68, y=0.98, bgcolor="rgba(255,255,255,0.9)"),
    )
    _save(fig, out)


def fig2_e3_synthetic() -> None:
    _traj_fig(
        RESULTS / "e3_synthetic.json",
        "Figure 2 — E3 (synthetic shared-optimum): best MSD vs iteration",
        "fig2_e3_synthetic",
    )


def fig3_e3_adamson() -> None:
    _traj_fig(
        RESULTS / "e3_adamson.json",
        "Figure 3 — E3 (Adamson real data): best MSD vs iteration",
        "fig3_e3_adamson",
    )


def fig4_e3b_task_conditional() -> None:
    _traj_fig(
        RESULTS / "e3b_task_conditional.json",
        "Figure 4 — E3b (task-conditional synthetic): contextual GP dominates",
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
    fig = px.box(
        df, x="backbone_name", y="msd_topk", color="source",
        title="Figure 5 — Per-backbone held-out MSD across grids",
        labels={"backbone_name": "backbone", "msd_topk": "MSD on top-20 DEGs"},
        template="simple_white", points="outliers",
    )
    fig.update_layout(width=720, height=480)
    _save(fig, "fig5_backbone_msd")


def main() -> None:
    fig1_metric_heatmap()
    fig2_e3_synthetic()
    fig3_e3_adamson()
    fig4_e3b_task_conditional()
    fig5_backbone_msd()
    print(f"wrote {sum(1 for _ in FIG_DIR.iterdir())} files to {FIG_DIR.resolve()}")


if __name__ == "__main__":
    main()
