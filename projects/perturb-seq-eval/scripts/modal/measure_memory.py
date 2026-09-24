"""Pre-spend resource check (CTO #245): measure, don't estimate, the loader footprint.

Loads Adamson (combined) and Norman exactly as ``app_v05.run_v05_sweep`` does — pinned fetch
(``trust_unpinned=False``), the sweep's ``n_top_hvg`` / ``max_cells_per_pert`` — then runs one
train-only HVG pass per dataset, and reports peak RSS against the sweep function's 32 GiB limit.
CPU only, no GPU, no LLM calls.

    modal run scripts/modal/measure_memory.py
"""
from __future__ import annotations

from pathlib import Path

import modal

PROJECT_DIR_HOST = Path(__file__).resolve().parents[2]
SWEEP_MEMORY_MIB = 32768  # must match app_v05's @app.function(memory=...)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "numpy>=1.26", "pandas>=2.2", "scipy>=1.11", "h5py==3.16.0", "anndata==0.12.19",
        "scikit-learn>=1.3", "pydantic>=2.0", "requests>=2.31",
    )
    .add_local_dir(
        str(PROJECT_DIR_HOST), remote_path="/app", copy=True,
        ignore=["artifacts/**", ".venv/**", ".pytest_cache/**", ".ruff_cache/**", "**/__pycache__/**"],
    )
    .workdir("/app")
    .env({"PYTHONPATH": "/app/src"})
)
app = modal.App("perturb-eval-measure-memory")
DATA_VOL = modal.Volume.from_name("perturb-eval-data")


@app.function(image=image, cpu=4.0, memory=SWEEP_MEMORY_MIB, timeout=1800, volumes={"/data": DATA_VOL})
def measure(n_top_hvg: int = 2000, max_cells_per_pert: int = 200) -> dict:
    import resource
    import time

    import numpy as np

    from perturb_eval.data.download import fetch_adamson_all, fetch_norman
    from perturb_eval.data.hvg import select_hvg_train_only
    from perturb_eval.experiments.e2_adamson import load_adamson_combined
    from perturb_eval.experiments.norman import load_norman_matrix

    def peak_gib() -> float:
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024**2  # KiB on Linux

    out: dict = {"limit_gib": SWEEP_MEMORY_MIB / 1024, "n_top_hvg": n_top_hvg,
                 "max_cells_per_pert": max_cells_per_pert}
    data_dir = Path("/data/datasets")
    for name, load in (
        ("adamson_full", lambda: load_adamson_combined(
            [p for _, p in sorted(fetch_adamson_all(dest_dir=data_dir, trust_unpinned=False).items())],
            n_top_hvg=n_top_hvg, max_cells_per_pert=max_cells_per_pert)),
        ("norman", lambda: load_norman_matrix(
            fetch_norman(dest_dir=data_dir, trust_unpinned=False),
            n_top_hvg=n_top_hvg, max_cells_per_pert=max_cells_per_pert)),
    ):
        t0 = time.time()
        ds = load()
        X, labels = ds["X"], np.asarray(ds["labels"])
        held = next(l for l in sorted(set(labels.tolist())) if l != "CTRL")
        sel = select_hvg_train_only(X, labels != held, n_top_hvg)
        idx = getattr(sel, "indices", sel)
        out[name] = {
            "shape": list(X.shape), "dtype": str(X.dtype),
            "matrix_gib": round(X.nbytes / 1024**3, 3),
            "n_hvg_selected": int(len(idx)),
            "load_plus_hvg_sec": round(time.time() - t0, 1),
            "peak_rss_gib_after": round(peak_gib(), 3),
        }
        del ds, X
    out["peak_rss_gib"] = round(peak_gib(), 3)
    out["headroom_gib"] = round(out["limit_gib"] - out["peak_rss_gib"], 3)
    return out


@app.local_entrypoint()
def main() -> None:
    import json

    print(json.dumps(measure.remote(), indent=2))
