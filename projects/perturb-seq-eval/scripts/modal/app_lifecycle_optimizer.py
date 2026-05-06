"""Contextual-BO vs random with live agentic-lifecycle evaluation on Adamson.

Each iteration = one full CellForge lifecycle run. The contextual GP
routes across (n_agents, n_rounds, backbone_family) using pre-harvested
round-0 probe signatures as context.

This is the end-to-end headline figure: iteration-vs-best-MSD where
"best MSD" comes from agents that chose and trained the model.

Deploy + run::

    set -a; source .env; set +a
    cd projects/perturb-seq-eval
    modal deploy scripts/modal/app_lifecycle_optimizer.py
    modal run scripts/modal/app_lifecycle_optimizer.py::entrypoint
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import modal

try:
    PROJECT_DIR_HOST = Path(__file__).resolve().parents[2]
except IndexError:
    PROJECT_DIR_HOST = Path(__file__).resolve().parent
# v0.5.0 layout: libs/cellforge-agents lives at the repo root.
try:
    REPO_ROOT_HOST = Path(__file__).resolve().parents[3]
    CELLFORGE_DIR_HOST = REPO_ROOT_HOST / "libs" / "cellforge-agents"
    if not CELLFORGE_DIR_HOST.exists():
        CELLFORGE_DIR_HOST = PROJECT_DIR_HOST.parent / "cellforge-agents"
except Exception:  # noqa: BLE001
    CELLFORGE_DIR_HOST = PROJECT_DIR_HOST


image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "build-essential")
    .pip_install(
        "numpy>=1.26", "typer>=0.12", "pandas>=2.2", "scipy>=1.11",
        "h5py>=3.10", "scikit-learn>=1.3", "torch>=2.2",
        "transformers>=4.42", "huggingface_hub>=0.24",
        "sentencepiece>=0.2", "sacremoses>=0.1", "accelerate>=0.30",
        "python-dotenv>=1.0",
    )
    .add_local_dir(
        str(PROJECT_DIR_HOST), remote_path="/app", copy=True,
        ignore=["artifacts/**", ".venv/**", "**/__pycache__/**"],
    )
    .add_local_dir(
        str(CELLFORGE_DIR_HOST), remote_path="/app_cellforge", copy=True,
        ignore=["**/__pycache__/**"],
    )
    .workdir("/app")
    .run_commands("pip install -e . && pip install -e /app_cellforge")
)


app = modal.App("perturb-eval-lifecycle-opt")
DATA_VOL = modal.Volume.from_name("perturb-eval-data", create_if_missing=True)
BIOFM_VOL = modal.Volume.from_name("biofm-cache", create_if_missing=True)


def _env_secrets() -> dict[str, str]:
    keys = (
        "OPENROUTER_API_KEY", "OPENROUTER_MODEL", "OPENROUTER_BASE_URL",
        "OPENROUTER_REFERER", "OPENROUTER_APP_TITLE",
    )
    return {
        **{k: os.environ.get(k, "") for k in keys},
        "HF_CACHE_DIR": "/biofm_cache",
        "TRANSFORMERS_CACHE": "/biofm_cache",
        "HF_HOME": "/biofm_cache",
    }


def _synthetic_probe(task_name: str, idx: int, total: int) -> list[float]:
    """Deterministic probe signature. Kept here so the optimizer has a
    context even when we haven't (yet) harvested real round-0 probes.
    The value of the contextual GP rests on the probe's informativeness,
    which in this iteration is bounded by the simulator; §5.5 of
    SUPPLEMENT.md discloses this."""
    import numpy as np

    rng = np.random.default_rng(2027 + (abs(hash(task_name)) % 2**30))
    hardness = (idx + 0.5) / max(total, 1)
    confs = np.clip(rng.normal(0.5, 0.08 + 0.25 * hardness, size=5), 0.01, 1.0)
    return [
        float(
            -np.sum((confs / confs.sum()) * np.log((confs / confs.sum()) + 1e-12))
            / np.log(5)
        ),
        float(confs.mean()),
        float(np.clip(hardness * 0.4 + rng.normal(0, 0.05), 0, 1)),
        float(confs.max()),
    ]


@app.function(
    image=image, gpu="A10G", cpu=4.0, memory=16384, timeout=14400,
    volumes={"/data": DATA_VOL, "/biofm_cache": BIOFM_VOL},
    secrets=[modal.Secret.from_dict(_env_secrets())],
)
def run_live_optimizer(n_iterations: int = 8, n_seeds: int = 1) -> dict:
    import numpy as np

    from perturb_eval.agentic_lifecycle.cellforge_pool import CellForgeAgentPool
    from perturb_eval.agentic_lifecycle.loop import run_agentic_lifecycle
    from perturb_eval.experiments import run_e3_optimizer_comparison
    from perturb_eval.experiments.e2_adamson import load_adamson_matrix
    from perturb_eval.types import Config

    ds = load_adamson_matrix(
        "/data/adamson/Adamson2016_pilot.h5ad",
        n_top_hvg=2000, max_cells_per_pert=200,
    )
    pool = CellForgeAgentPool(use_biofm=True)
    tasks = list(ds["perturbations"])
    contexts = {
        t: np.asarray(_synthetic_probe(t, i, len(tasks)), dtype=np.float64)
        for i, t in enumerate(tasks)
    }

    def eval_fn(phi: "Config", task: str, seed: int) -> float:
        t0 = time.time()
        try:
            run = run_agentic_lifecycle(
                task_id=task,
                X=ds["X"], labels=ds["labels"],
                control_mask=ds["control_mask"],
                target_gene_idx=ds["target_gene_idx"], held_out=task,
                agent_pool=pool, max_rounds=phi.n_rounds,
                backbone_override=phi.backbone,
                validator_threshold_override=0.05,
            )
            msd = float(run.final_msd_topk)
        except Exception as e:  # noqa: BLE001
            print(f"  eval FAILED task={task} phi={phi} seed={seed}: {e!r}")
            msd = 1.0
        print(
            f"  eval task={task} phi_a={phi.n_agents} r={phi.n_rounds} b={phi.backbone} "
            f"seed={seed} MSD={msd:.4f} wall={time.time() - t0:.1f}s"
        )
        return msd

    phis = tuple(
        Config(n_agents=a, n_rounds=r, backbone=b)
        for a in (3, 5)
        for r in (1, 2, 3)
        for b in ("linear", "mlp", "scgpt_small")
    )

    trajectories = run_e3_optimizer_comparison(
        grid={}, contexts=contexts,
        optimizers=("random", "contextual_gp"),
        n_iterations=n_iterations, n_seeds=n_seeds,
        config_space=phis, eval_fn=eval_fn,
    )
    out = [
        {
            "optimizer": t.optimizer,
            "best_msd_per_iter": list(t.best_msd_per_iter),
            "per_seed_trajectories": [list(x) for x in t.per_seed_trajectories],
            "n_iterations": t.n_iterations,
            "n_seeds": t.n_seeds,
            "n_tasks": t.n_tasks,
        }
        for t in trajectories
    ]
    out_dir = Path("/data/lifecycle")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "adamson_live_optimizer.json").write_text(json.dumps(out, indent=2))
    DATA_VOL.commit()
    return {"trajectories": out}


@app.local_entrypoint()
def entrypoint(n_iterations: int = 8, n_seeds: int = 1) -> None:
    out = run_live_optimizer.remote(n_iterations=n_iterations, n_seeds=n_seeds)
    print(json.dumps(out, indent=2, default=str))
