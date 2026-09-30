"""Read-only: reproduce the pre-fix h5py decode (``cats[code]``) of obs/perturbation and report, per file,
how many cells carry code -1 (missing annotation) and which real category ``cats[-1]`` silently absorbed them.
CPU only, no writes.

    modal run scripts/modal/audit_missing_codes.py
"""
from __future__ import annotations

import modal

app = modal.App("perturb-eval-audit-missing-codes")
DATA_VOL = modal.Volume.from_name("perturb-eval-data")
image = modal.Image.debian_slim(python_version="3.11").pip_install("h5py==3.16.0", "numpy>=1.26")
FILES = ("Adamson2016_pilot.h5ad", "Adamson2016_10X005.h5ad", "Adamson2016_10X010.h5ad",
         "NormanWeissman2019_filtered.h5ad")


@app.function(image=image, cpu=1.0, memory=4096, timeout=600, volumes={"/data": DATA_VOL})
def audit() -> dict:
    import h5py

    out = {}
    for f in FILES:
        with h5py.File(f"/data/datasets/{f}", "r") as h:
            g = h["obs/perturbation"]
            codes = g["codes"][()]
            cats = [c.decode() if isinstance(c, bytes) else c for c in g["categories"][()]]
        last = cats[-1]
        n_missing = int((codes == -1).sum())
        n_last_true = int((codes == len(cats) - 1).sum())
        out[f] = {"n_cells": int(codes.size), "n_code_minus1": n_missing, "last_category": last,
                  "last_category_true_cells": n_last_true,
                  "last_category_prefix_decode_cells": n_last_true + n_missing}
    return out


@app.local_entrypoint()
def main() -> None:
    import json

    print(json.dumps(audit.remote(), indent=1))
