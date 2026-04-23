"""End-to-end agentic perturb-seq lifecycle on Adamson 2016 pilot.

Deploy + run::

    set -a; source .env; set +a
    cd projects/perturb-seq-eval
    modal deploy scripts/modal/app_lifecycle.py
    modal run scripts/modal/app_lifecycle.py::entrypoint --n-seeds 3 --max-rounds 3

Produces ``/data/lifecycle/adamson_lifecycle_runs.json`` on the shared
Modal volume ``perturb-eval-data``. Download with::

    modal volume get perturb-eval-data /lifecycle/adamson_lifecycle_runs.json \\
        ./artifacts/lifecycle/adamson_lifecycle_runs.json --force
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict
from pathlib import Path

import modal

try:
    PROJECT_DIR_HOST = Path(__file__).resolve().parents[2]
except IndexError:
    PROJECT_DIR_HOST = Path(__file__).resolve().parent
try:
    CELLFORGE_DIR_HOST = PROJECT_DIR_HOST.parent / "cellforge-agents"
except Exception:  # noqa: BLE001
    CELLFORGE_DIR_HOST = PROJECT_DIR_HOST


image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "build-essential")
    .pip_install(
        "numpy>=1.26", "typer>=0.12", "pandas>=2.2", "pyarrow>=16",
        "scipy>=1.11", "h5py>=3.10", "scikit-learn>=1.3",
        "torch>=2.2", "transformers>=4.42", "huggingface_hub>=0.24",
        "sentencepiece>=0.2", "sacremoses>=0.1", "accelerate>=0.30",
        "python-dotenv>=1.0",
    )
    .add_local_dir(
        str(PROJECT_DIR_HOST), remote_path="/app", copy=True,
        ignore=["artifacts/**", ".venv/**", ".pytest_cache/**",
                ".ruff_cache/**", "**/__pycache__/**"],
    )
    .add_local_dir(
        str(CELLFORGE_DIR_HOST), remote_path="/app_cellforge", copy=True,
        ignore=["**/__pycache__/**", ".venv/**", ".pytest_cache/**"],
    )
    .workdir("/app")
    .run_commands("pip install -e . && pip install -e /app_cellforge")
)


app = modal.App("perturb-eval-lifecycle")
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


@app.function(
    image=image, gpu="A10G", cpu=4.0, memory=16384, timeout=10800,
    volumes={"/data": DATA_VOL, "/biofm_cache": BIOFM_VOL},
    secrets=[modal.Secret.from_dict(_env_secrets())],
)
def run_lifecycle_adamson(
    n_seeds: int = 3,
    max_rounds: int = 3,
    use_biofm: bool = True,
    validator_threshold: float = 0.05,
    backbones: tuple[str, ...] = ("linear", "mlp", "scgpt_small"),
) -> dict:
    """Run the end-to-end agentic lifecycle on each Adamson perturbation.

    Iterates over every ``(backbone, perturbation, seed)`` triple so the
    §5.5 headline number is an average over the full backbone axis, not
    just the Architect's deterministic pick. The Validator threshold is
    tightened (default 0.05 MSD) so the multi-round refinement path
    actually triggers on most tasks.
    """
    from perturb_eval.agentic_lifecycle.cellforge_pool import CellForgeAgentPool
    from perturb_eval.agentic_lifecycle.loop import run_agentic_lifecycle
    from perturb_eval.experiments.e2_adamson import load_adamson_matrix

    ds = load_adamson_matrix(
        "/data/adamson/Adamson2016_pilot.h5ad",
        n_top_hvg=2000, max_cells_per_pert=200,
    )
    pool = CellForgeAgentPool(use_biofm=use_biofm)

    out_dir = Path("/data/lifecycle")
    out_dir.mkdir(parents=True, exist_ok=True)

    runs: list[dict] = []
    for backbone in backbones:
        for pert in ds["perturbations"]:
            for seed in range(2026, 2026 + n_seeds):
                print(f"=== {pert} seed={seed} bb={backbone} ===")
                t0 = time.time()
                try:
                    run = run_agentic_lifecycle(
                        task_id=pert,
                        X=ds["X"], labels=ds["labels"],
                        control_mask=ds["control_mask"],
                        target_gene_idx=ds["target_gene_idx"], held_out=pert,
                        agent_pool=pool,
                        max_rounds=max_rounds,
                        backbone_override=backbone,
                        validator_threshold_override=validator_threshold,
                    )
                    rec = asdict(run) | {
                        "seed": seed,
                        "wall_sec": time.time() - t0,
                        "backbone_forced": backbone,
                    }
                    print(
                        f"  MSD={rec['final_msd_topk']:.4f}  rounds={rec['n_rounds']}"
                    )
                except Exception as e:  # noqa: BLE001
                    rec = {
                        "task_id": pert, "seed": seed,
                        "wall_sec": time.time() - t0,
                        "error": f"{type(e).__name__}: {e}",
                        "final_msd_topk": float("inf"),
                        "n_rounds": 0, "n_agents": 5,
                        "backbone_used": backbone, "backbone_forced": backbone,
                        "steps": [],
                    }
                    print(f"  FAILED: {rec['error']}")
                runs.append(rec)

    manifest = out_dir / "adamson_lifecycle_runs.json"
    manifest.write_text(json.dumps(runs, indent=2))
    DATA_VOL.commit()
    print(f"wrote {len(runs)} runs → {manifest}")
    return {"n_runs": len(runs), "path": str(manifest)}


@app.local_entrypoint()
def entrypoint(
    n_seeds: int = 3,
    max_rounds: int = 3,
    use_biofm: bool = True,
    validator_threshold: float = 0.05,
) -> None:
    out = run_lifecycle_adamson.remote(
        n_seeds=n_seeds,
        max_rounds=max_rounds,
        use_biofm=use_biofm,
        validator_threshold=validator_threshold,
    )
    print(json.dumps(out, indent=2, default=str))
