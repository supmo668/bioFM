"""Figure 6 — live agentic lifecycle MSDs per Adamson task.

Two panels (same figure):
  * iteration-vs-best-MSD from ``adamson_live_optimizer.json`` if present
    (produced by ``app_lifecycle_optimizer.py``);
  * per-task boxplot of ``adamson_lifecycle_runs.json`` MSDs otherwise.

Writes PNG + PDF + HTML into ``artifacts/modal_run/figures/``.
"""

from __future__ import annotations

import json
from pathlib import Path

import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parents[2]
LIFECYCLE_DIR = ROOT / "artifacts" / "lifecycle"
FIG_DIR = ROOT / "artifacts" / "modal_run" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

WONG = {"random": "#999999", "contextual_gp": "#56B4E9", "cma_es": "#E69F00"}
TASK_COLOR = "#0072B2"


def _save(fig: go.Figure, name: str) -> None:
    fig.write_image(str(FIG_DIR / f"{name}.png"), scale=2)
    fig.write_image(str(FIG_DIR / f"{name}.pdf"))
    fig.write_html(str(FIG_DIR / f"{name}.html"))


def _render_optimizer_trajectories(path: Path) -> None:
    data = json.loads(path.read_text())
    fig = go.Figure()
    for traj in data:
        y = traj["best_msd_per_iter"]
        fig.add_trace(
            go.Scatter(
                x=list(range(1, len(y) + 1)), y=y,
                mode="lines+markers", name=traj["optimizer"],
                line=dict(color=WONG.get(traj["optimizer"], "#000000"), width=2),
                marker=dict(size=6),
            )
        )
    fig.update_layout(
        title=(
            "Figure 6 — Live agentic lifecycle: best MSD vs iteration<br>"
            "<sub>Each iteration = one full 5-agent CellForge run on a real "
            "Adamson perturbation with BioFM-grounded tools (BioGPT + Geneformer)</sub>"
        ),
        xaxis_title="iteration", yaxis_title="best MSD so far (↓ better)",
        template="simple_white", width=720, height=520,
    )
    _save(fig, "fig6_lifecycle_optimizer")


def _render_per_task_box(path: Path) -> None:
    runs = json.loads(path.read_text())
    by_task: dict[str, list[float]] = {}
    for r in runs:
        msd = r.get("final_msd_topk")
        if msd is None or not (msd < float("inf")):
            continue
        by_task.setdefault(r["task_id"], []).append(float(msd))
    fig = go.Figure()
    for task, vals in sorted(by_task.items()):
        fig.add_trace(
            go.Box(y=vals, name=task, marker_color=TASK_COLOR, boxpoints="all",
                   jitter=0.3, pointpos=0)
        )
    fig.update_layout(
        title=(
            "Figure 6 — End-to-end agentic lifecycle MSD per Adamson task<br>"
            "<sub>Each point = one full 5-agent multi-round CellForge run "
            "with real model fitting</sub>"
        ),
        xaxis_title="held-out perturbation",
        yaxis_title="final MSD on top-20 DEGs (↓ better)",
        template="simple_white", width=820, height=520, showlegend=False,
    )
    _save(fig, "fig6_lifecycle_optimizer")


def main() -> None:
    optimizer_path = LIFECYCLE_DIR / "adamson_live_optimizer.json"
    runs_path = LIFECYCLE_DIR / "adamson_lifecycle_runs.json"
    if optimizer_path.exists():
        print(f"rendering optimizer trajectories from {optimizer_path}")
        _render_optimizer_trajectories(optimizer_path)
    elif runs_path.exists():
        print(f"rendering per-task box from {runs_path}")
        _render_per_task_box(runs_path)
    else:
        raise SystemExit(
            "No lifecycle results found. Run app_lifecycle.py or "
            "app_lifecycle_optimizer.py first."
        )
    print(f"wrote PNG/PDF/HTML → {FIG_DIR}")


if __name__ == "__main__":
    main()
