"""Read-only audit: per dataset file, how many perturbation labels (and cells) carry nperts > 1,
plus perturbation_type values. Decides whether "single-gene" tasks are single-gene. CPU only.

    modal run scripts/modal/audit_nperts.py
"""
from __future__ import annotations

import modal

app = modal.App("perturb-eval-audit-nperts")
DATA_VOL = modal.Volume.from_name("perturb-eval-data")
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "h5py==3.16.0", "anndata==0.12.19", "pandas>=2.2,<3", "numpy>=1.26")
FILES = ("Adamson2016_pilot.h5ad", "Adamson2016_10X005.h5ad", "Adamson2016_10X010.h5ad",
         "NormanWeissman2019_filtered.h5ad")


@app.function(image=image, cpu=1.0, memory=8192, timeout=900, volumes={"/data": DATA_VOL})
def audit() -> dict:
    import anndata as ad

    out = {}
    for f in FILES:
        obs = ad.read_h5ad(f"/data/datasets/{f}", backed="r").obs
        g = obs.groupby(obs["perturbation"].astype(str), observed=True)
        per = g["nperts"].agg(lambda s: sorted({str(v) for v in s}))
        multi = {k: v for k, v in per.items() if v != ["1"] and v != ["0"]}
        out[f] = {
            "n_labels": int(per.size),
            "nperts_value_counts_cells": {str(k): int(v) for k, v in obs["nperts"].astype(str).value_counts().items()},
            "perturbation_type": {str(k): int(v) for k, v in obs["perturbation_type"].astype(str).value_counts().items()},
            "n_labels_with_nperts_gt1": len(multi),
            "labels_with_nperts_gt1_sample": dict(list(sorted(multi.items()))[:40]),
            "all_labels": {k: {"nperts": v, "n_cells": int(n)} for (k, v), n in zip(sorted(per.items()), [int(g.size().loc[k]) for k in sorted(per.index)])},
        }
    return out


@app.local_entrypoint()
def main() -> None:
    import json

    print(json.dumps(audit.remote(), indent=1))
