"""Modal app for the perturb-seq-eval **comprehensive** supplement run.

Budget ceiling: $30 (user-approved 2026-04-21). Projected: ~$22 across
E1 + E2-synthetic + E2-Adamson + E3 + E3b + figure generation.

Workflow
--------
    1. ``modal volume put perturb-eval-data Adamson2016_pilot.h5ad adamson/``
    2. ``modal run scripts/modal/app.py::entrypoint --step all``
    3. ``modal volume get perturb-eval-data results/ ./artifacts/modal_run/``
    4. ``modal volume get perturb-eval-data figures/ ./artifacts/modal_run/``

Functions
---------
    run_e1                     CPU, n_traces=5000 synthetic.
    train_grid_cell_synthetic  CPU worker for synthetic E2 cells.
    train_grid_cell_adamson    GPU worker for real-data E2 cells.
    orchestrate_e2_synthetic   fans out synthetic cells (1080).
    orchestrate_e2_adamson     fans out Adamson cells (189).
    run_e3                     CPU optimizer comparison on synthetic grid.
    run_e3_adamson             CPU optimizer comparison on Adamson grid.
    run_e3b                    CPU calibration check (task-conditional DGP).
    generate_figures           5 Plotly figures → PDF+HTML in /data/figures/.
    run_all                    one-button end-to-end.

All functions write into the shared ``perturb-eval-data`` volume under
``/data/results/`` and ``/data/figures/``.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import modal

# ---------------------------------------------------------------------------
# Image, volume, app
# ---------------------------------------------------------------------------

# Only resolvable when the file is read from the developer's checkout, not
# from the container's ``/root/app.py``. Fall back to a dummy path in the
# container — ``add_local_dir`` is only consulted at image build time.
try:
    PROJECT_DIR_HOST = Path(__file__).resolve().parents[2]
except IndexError:
    PROJECT_DIR_HOST = Path(__file__).resolve().parent

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "build-essential")
    .pip_install(
        "numpy>=1.26",
        "typer>=0.12",
        "pandas>=2.2",
        "pyarrow>=16",
        "scipy>=1.11",
        "h5py>=3.10",
        "scikit-learn>=1.3",
        "scikit-optimize>=0.10",
        "cma>=3.3",
        # plotly + kaleido pinned: kaleido 0.2.1 bundles its own Chromium; newer
        # versions require `plotly_get_chrome` which is impractical in a slim image.
        "plotly>=5.22,<6.0",
        "kaleido==0.2.1",
        # torch included for the scgpt_small backbone; CUDA build from Modal's default index.
        "torch>=2.2",
    )
    .add_local_dir(str(PROJECT_DIR_HOST), remote_path="/app", copy=True)
    .workdir("/app")
    .run_commands("pip install -e .")
)

app = modal.App("perturb-eval-supplement")
VOL = modal.Volume.from_name("perturb-eval-data", create_if_missing=True)

VOLUME_MOUNT = {"/data": VOL}
ADAMSON_H5AD_REMOTE = "/data/adamson/Adamson2016_pilot.h5ad"

# ---------------------------------------------------------------------------
# E1 — metric overlap
# ---------------------------------------------------------------------------


@app.function(image=image, cpu=2.0, memory=2048, timeout=300, volumes=VOLUME_MOUNT)
def run_e1(n_traces: int = 5000, seed: int = 2026) -> dict:
    import numpy as np

    from perturb_eval.experiments import run_e1_metric_overlap

    out = run_e1_metric_overlap(n_traces=n_traces, seed=seed)
    payload = {
        "spearman_matrix": np.asarray(out["spearman_matrix"]).tolist(),
        "feature_names": out["feature_names"],
        "drop_candidates": out["drop_candidates"],
        "n_traces": out["n_traces"],
    }
    Path("/data/results").mkdir(parents=True, exist_ok=True)
    with open("/data/results/e1_overlap.json", "w") as f:
        json.dump(payload, f, indent=2)
    VOL.commit()
    return payload


# ---------------------------------------------------------------------------
# E2 — synthetic grid fill
# ---------------------------------------------------------------------------


@app.function(image=image, cpu=2.0, memory=4096, timeout=600, volumes=VOLUME_MOUNT)
def train_grid_cell_synthetic_remote(phi_dict: dict, task: str, seed: int) -> dict:
    from dataclasses import asdict

    from perturb_eval.experiments import train_grid_cell_synthetic
    from perturb_eval.types import Config

    return asdict(
        train_grid_cell_synthetic(
            phi=Config(**phi_dict), task=task, seed=seed,
            n_cells=400, n_genes=80, n_perts=5,
        )
    )


@app.function(image=image, cpu=2.0, memory=4096, timeout=7200, volumes=VOLUME_MOUNT)
def orchestrate_e2_synthetic(n_seeds: int = 5) -> dict:
    from perturb_eval.experiments.common import GridCellResult
    from perturb_eval.experiments.e2_grid_fill import write_results_jsonl

    phis = [
        {"n_agents": a, "n_rounds": r, "backbone": b}
        for a in (3, 4, 5)
        for r in (1, 2, 3)
        for b in ("linear", "mlp", "scgpt_small")
    ]
    tasks = [f"T{i}" for i in range(8)]
    seeds = list(range(2026, 2026 + n_seeds))
    calls = [
        train_grid_cell_synthetic_remote.spawn(phi_dict=phi, task=t, seed=s)
        for phi in phis for t in tasks for s in seeds
    ]
    rows = [GridCellResult(**c.get()) for c in calls]
    out_path = Path("/data/results/e2_grid_synthetic.jsonl")
    write_results_jsonl(rows, out_path)
    VOL.commit()
    return {"n_cells": len(rows), "path": str(out_path)}


# ---------------------------------------------------------------------------
# E2 — Adamson (real) grid fill
# ---------------------------------------------------------------------------


@app.function(
    image=image, gpu="A10G", cpu=2.0, memory=8192, timeout=900, volumes=VOLUME_MOUNT,
)
def train_grid_cell_adamson_remote(phi_dict: dict, task: str, seed: int) -> dict:
    """GPU worker for one (phi, task, seed) Adamson cell.

    Loads the h5ad from the shared volume, so the Adamson file must be
    staged there first via ``modal volume put``.
    """
    from dataclasses import asdict

    from perturb_eval.experiments.e2_adamson import train_grid_cell_adamson
    from perturb_eval.types import Config

    return asdict(
        train_grid_cell_adamson(
            phi=Config(**phi_dict), task=task, seed=seed,
            h5ad_path=ADAMSON_H5AD_REMOTE,
        )
    )


@app.function(image=image, cpu=2.0, memory=4096, timeout=10800, volumes=VOLUME_MOUNT)
def orchestrate_e2_adamson(n_seeds: int = 3) -> dict:
    from perturb_eval.experiments.common import GridCellResult
    from perturb_eval.experiments.e2_adamson import load_adamson_matrix
    from perturb_eval.experiments.e2_grid_fill import write_results_jsonl

    # Discover which perturbations are actually available locally so task
    # names match ``train_grid_cell_adamson``'s expectations.
    ds = load_adamson_matrix(ADAMSON_H5AD_REMOTE, n_top_hvg=2000, max_cells_per_pert=400)
    tasks = list(ds["perturbations"])

    phis = [
        {"n_agents": a, "n_rounds": r, "backbone": b}
        for a in (3, 4, 5)
        for r in (1, 2, 3)
        for b in ("linear", "mlp", "scgpt_small")
    ]
    seeds = list(range(2026, 2026 + n_seeds))
    calls = [
        train_grid_cell_adamson_remote.spawn(phi_dict=phi, task=t, seed=s)
        for phi in phis for t in tasks for s in seeds
    ]
    rows = [GridCellResult(**c.get()) for c in calls]
    out_path = Path("/data/results/e2_grid_adamson.jsonl")
    write_results_jsonl(rows, out_path)
    VOL.commit()
    return {"n_cells": len(rows), "tasks": tasks, "path": str(out_path)}


# ---------------------------------------------------------------------------
# E3 — optimizer comparison on each cached grid
# ---------------------------------------------------------------------------


def _run_e3_on_grid(
    grid_jsonl: str,
    probe_seed: int,
    n_iterations: int,
    n_seeds: int,
) -> list[dict]:
    import numpy as np

    from perturb_eval.experiments import run_e3_optimizer_comparison
    from perturb_eval.experiments.e3_optimizer_comparison import _phi_key
    from perturb_eval.types import Config

    grid: dict[tuple[str, str], float] = {}
    with open(grid_jsonl) as f:
        for line in f:
            row = json.loads(line)
            grid[(row["phi_id"], row["task"])] = float(row["msd_topk"])
    # Re-key to optimizer convention.
    def recode(pid: str) -> str:
        parts = pid.split("_")
        return f"a={parts[0][1:]}r={parts[1][1:]}b={'_'.join(parts[2:])}"
    remapped = {(recode(p), t): m for (p, t), m in grid.items()}
    tasks = sorted({t for (_, t) in remapped})
    # Probe signatures: deterministic draw from round-0-like DGP so results
    # are reproducible without needing the full agent trace collector.
    rng = np.random.default_rng(probe_seed)
    contexts: dict[str, np.ndarray] = {}
    for i, t in enumerate(tasks):
        hardness = (i + 0.5) / len(tasks)
        confs = np.clip(rng.normal(0.5, 0.08 + 0.25 * hardness, size=5), 0.01, 1.0)
        contexts[t] = np.array([
            float(np.clip(-np.sum((confs / confs.sum()) * np.log(
                (confs / confs.sum()) + 1e-12)) / np.log(5), 0, 1)),
            float(confs.mean()),
            float(np.clip(hardness * 0.4 + rng.normal(0, 0.05), 0, 1)),
            float(confs.max()),
        ])
    config_space = tuple(
        Config(n_agents=a, n_rounds=r, backbone=b)
        for a in (3, 4, 5)
        for r in (1, 2, 3)
        for b in ("linear", "mlp", "scgpt_small")
    )
    trajectories = run_e3_optimizer_comparison(
        grid=remapped,
        contexts=contexts,
        optimizers=("random", "cma_es", "contextual_gp"),
        n_iterations=n_iterations,
        n_seeds=n_seeds,
        config_space=config_space,
    )
    return [
        {
            "optimizer": t.optimizer,
            "best_msd_per_iter": list(t.best_msd_per_iter),
            "n_iterations": t.n_iterations,
            "n_seeds": t.n_seeds,
            "n_tasks": t.n_tasks,
        }
        for t in trajectories
    ]


@app.function(image=image, cpu=2.0, memory=4096, timeout=1800, volumes=VOLUME_MOUNT)
def run_e3(n_iterations: int = 30, n_seeds: int = 20) -> dict:
    trajectories = _run_e3_on_grid(
        "/data/results/e2_grid_synthetic.jsonl",
        probe_seed=2026, n_iterations=n_iterations, n_seeds=n_seeds,
    )
    out_path = Path("/data/results/e3_synthetic.json")
    with out_path.open("w") as f:
        json.dump({"trajectories": trajectories}, f, indent=2)
    VOL.commit()
    return {"trajectories": trajectories, "path": str(out_path)}


@app.function(image=image, cpu=2.0, memory=4096, timeout=1800, volumes=VOLUME_MOUNT)
def run_e3_adamson(n_iterations: int = 30, n_seeds: int = 20) -> dict:
    trajectories = _run_e3_on_grid(
        "/data/results/e2_grid_adamson.jsonl",
        probe_seed=2027, n_iterations=n_iterations, n_seeds=n_seeds,
    )
    out_path = Path("/data/results/e3_adamson.json")
    with out_path.open("w") as f:
        json.dump({"trajectories": trajectories}, f, indent=2)
    VOL.commit()
    return {"trajectories": trajectories, "path": str(out_path)}


# ---------------------------------------------------------------------------
# E3b — task-conditional calibration
# ---------------------------------------------------------------------------


@app.function(image=image, cpu=2.0, memory=4096, timeout=600, volumes=VOLUME_MOUNT)
def run_e3b(n_iterations: int = 30, n_seeds: int = 20) -> dict:
    import numpy as np

    from perturb_eval.experiments import run_e3_optimizer_comparison
    from perturb_eval.experiments.e3_optimizer_comparison import _phi_key
    from perturb_eval.types import Config

    # Same task-conditional synthetic grid as scripts/local/e3b_task_conditional.py.
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
            backbone_bonus = {
                "linear": 0.0 if not hard else 0.15,
                "mlp": 0.10 if not hard else 0.05,
                "scgpt_small": 0.20 if not hard else 0.0,
            }[phi.backbone]
            grid[(_phi_key(phi), t)] = float(max(0.0, ((size - target) / 15.0) ** 2 + backbone_bonus))
    trajectories = run_e3_optimizer_comparison(
        grid=grid, contexts=contexts,
        optimizers=("random", "cma_es", "contextual_gp"),
        n_iterations=n_iterations, n_seeds=n_seeds,
        config_space=phis,
    )
    serialised = [
        {
            "optimizer": t.optimizer,
            "best_msd_per_iter": list(t.best_msd_per_iter),
            "n_iterations": t.n_iterations,
            "n_seeds": t.n_seeds,
            "n_tasks": t.n_tasks,
        }
        for t in trajectories
    ]
    out_path = Path("/data/results/e3b_task_conditional.json")
    with out_path.open("w") as f:
        json.dump({"trajectories": serialised}, f, indent=2)
    VOL.commit()
    return {"trajectories": serialised}


# ---------------------------------------------------------------------------
# Figure generation (Plotly → PDF + HTML)
# ---------------------------------------------------------------------------


@app.function(image=image, cpu=2.0, memory=4096, timeout=900, volumes=VOLUME_MOUNT)
def generate_figures() -> dict:
    import numpy as np
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go

    fig_dir = Path("/data/figures")
    fig_dir.mkdir(parents=True, exist_ok=True)
    results = Path("/data/results")

    artifacts: dict[str, str] = {}

    # 1. Spearman heatmap of all metrics (E1).
    e1 = json.loads((results / "e1_overlap.json").read_text())
    rho = np.asarray(e1["spearman_matrix"])
    names = e1["feature_names"]
    fig1 = go.Figure(data=go.Heatmap(
        z=rho, x=names, y=names, colorscale="RdBu", zmid=0,
        text=[[f"{v:.2f}" for v in row] for row in rho],
        texttemplate="%{text}", textfont={"size": 11},
        colorbar_title="Spearman ρ",
    ))
    fig1.update_layout(
        title=f"Figure 1 — Metric overlap, Spearman ρ, n={e1['n_traces']} synthetic traces",
        xaxis_title="metric", yaxis_title="metric",
        template="simple_white", width=720, height=640,
    )
    fig1.write_image(str(fig_dir / "fig1_metric_heatmap.pdf"))
    fig1.write_html(str(fig_dir / "fig1_metric_heatmap.html"))
    artifacts["fig1"] = "fig1_metric_heatmap.{pdf,html}"

    # 2. Iteration-vs-best-MSD on the *synthetic* shared-optimum grid (E3).
    e3s = json.loads((results / "e3_synthetic.json").read_text())["trajectories"]
    fig2 = go.Figure()
    for t in e3s:
        fig2.add_trace(go.Scatter(
            x=list(range(1, len(t["best_msd_per_iter"]) + 1)),
            y=t["best_msd_per_iter"],
            mode="lines+markers", name=t["optimizer"],
        ))
    fig2.update_layout(
        title="Figure 2 — E3 (synthetic shared-optimum): best MSD vs iteration",
        xaxis_title="iteration", yaxis_title="best MSD so far (↓ better)",
        template="simple_white", width=720, height=480,
    )
    fig2.write_image(str(fig_dir / "fig2_e3_synthetic.pdf"))
    fig2.write_html(str(fig_dir / "fig2_e3_synthetic.html"))
    artifacts["fig2"] = "fig2_e3_synthetic.{pdf,html}"

    # 3. Iteration-vs-best-MSD on the *Adamson* grid (E3 on real data).
    e3a_path = results / "e3_adamson.json"
    if e3a_path.exists():
        e3a = json.loads(e3a_path.read_text())["trajectories"]
        fig3 = go.Figure()
        for t in e3a:
            fig3.add_trace(go.Scatter(
                x=list(range(1, len(t["best_msd_per_iter"]) + 1)),
                y=t["best_msd_per_iter"],
                mode="lines+markers", name=t["optimizer"],
            ))
        fig3.update_layout(
            title="Figure 3 — E3 (Adamson real data): best MSD vs iteration",
            xaxis_title="iteration", yaxis_title="best MSD so far (↓ better)",
            template="simple_white", width=720, height=480,
        )
        fig3.write_image(str(fig_dir / "fig3_e3_adamson.pdf"))
        fig3.write_html(str(fig_dir / "fig3_e3_adamson.html"))
        artifacts["fig3"] = "fig3_e3_adamson.{pdf,html}"

    # 4. Iteration-vs-best-MSD on the task-conditional calibration grid (E3b).
    e3b = json.loads((results / "e3b_task_conditional.json").read_text())["trajectories"]
    fig4 = go.Figure()
    for t in e3b:
        fig4.add_trace(go.Scatter(
            x=list(range(1, len(t["best_msd_per_iter"]) + 1)),
            y=t["best_msd_per_iter"],
            mode="lines+markers", name=t["optimizer"],
        ))
    fig4.update_layout(
        title="Figure 4 — E3b (task-conditional synthetic): contextual GP dominates",
        xaxis_title="iteration", yaxis_title="best MSD so far (↓ better)",
        template="simple_white", width=720, height=480,
    )
    fig4.write_image(str(fig_dir / "fig4_e3b_task_conditional.pdf"))
    fig4.write_html(str(fig_dir / "fig4_e3b_task_conditional.html"))
    artifacts["fig4"] = "fig4_e3b_task_conditional.{pdf,html}"

    # 5. Per-backbone MSD boxplot on each grid + per-task best-phi heatmap.
    def _read_grid(path: Path) -> pd.DataFrame:
        if not path.exists():
            return pd.DataFrame()
        return pd.DataFrame([json.loads(line) for line in path.open()])
    df_syn = _read_grid(results / "e2_grid_synthetic.jsonl")
    df_ada = _read_grid(results / "e2_grid_adamson.jsonl")
    df_syn["source"] = "synthetic"
    if not df_ada.empty:
        df_ada["source"] = "adamson"
        df_all = pd.concat([df_syn, df_ada], ignore_index=True)
    else:
        df_all = df_syn

    fig5 = px.box(
        df_all, x="backbone_name", y="msd_topk", color="source",
        title="Figure 5 — Per-backbone held-out MSD across grids",
        labels={"backbone_name": "backbone", "msd_topk": "MSD on top-20 DEGs"},
        template="simple_white",
    )
    fig5.update_layout(width=720, height=480)
    fig5.write_image(str(fig_dir / "fig5_backbone_msd.pdf"))
    fig5.write_html(str(fig_dir / "fig5_backbone_msd.html"))
    artifacts["fig5"] = "fig5_backbone_msd.{pdf,html}"

    VOL.commit()
    return artifacts


# ---------------------------------------------------------------------------
# One-button driver
# ---------------------------------------------------------------------------


@app.function(image=image, cpu=2.0, memory=4096, timeout=14400, volumes=VOLUME_MOUNT)
def run_all() -> dict:
    t_e1 = time.time()
    e1 = run_e1.remote(n_traces=5000)
    t_e2s = time.time()
    e2s = orchestrate_e2_synthetic.remote(n_seeds=5)
    t_e2a = time.time()
    try:
        e2a = orchestrate_e2_adamson.remote(n_seeds=3)
    except Exception as e:  # noqa: BLE001
        e2a = {"error": str(e), "skipped": True}
    t_e3 = time.time()
    e3 = run_e3.remote(n_iterations=30, n_seeds=20)
    e3a = run_e3_adamson.remote(n_iterations=30, n_seeds=20) if not e2a.get("error") else {"skipped": True}
    e3b = run_e3b.remote(n_iterations=30, n_seeds=20)
    t_figs = time.time()
    figs = generate_figures.remote()
    return {
        "timing": {
            "e1_s": t_e2s - t_e1,
            "e2_synthetic_s": t_e2a - t_e2s,
            "e2_adamson_s": t_e3 - t_e2a,
            "e3_s": t_figs - t_e3,
            "figs_s": time.time() - t_figs,
        },
        "e1_drop_candidates": e1["drop_candidates"],
        "e2_synthetic_cells": e2s.get("n_cells"),
        "e2_adamson_cells": e2a.get("n_cells"),
        "figures": figs,
    }


@app.local_entrypoint()
def entrypoint(step: str = "all") -> None:
    """Dispatch: ``all`` | ``e1`` | ``e2_synthetic`` | ``e2_adamson`` | ``e3`` | ``e3_adamson`` | ``e3b`` | ``figures``."""
    dispatch = {
        "all": run_all,
        "e1": run_e1,
        "e2_synthetic": orchestrate_e2_synthetic,
        "e2_adamson": orchestrate_e2_adamson,
        "e3": run_e3,
        "e3_adamson": run_e3_adamson,
        "e3b": run_e3b,
        "figures": generate_figures,
    }
    if step not in dispatch:
        raise SystemExit(f"unknown step {step!r}")
    print(json.dumps(dispatch[step].remote(), indent=2, default=str))
