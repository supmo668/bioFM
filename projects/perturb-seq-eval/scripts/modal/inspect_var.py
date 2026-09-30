"""Read-only: list gene-metadata columns (adata.var) of the four datasets, and look up the labels the
fail-closed resolver refused, so the label->gene mapping can be ruled on evidence. CPU only, no writes.

    modal run scripts/modal/inspect_var.py
"""
from __future__ import annotations

import modal

app = modal.App("perturb-eval-inspect-var")
DATA_VOL = modal.Volume.from_name("perturb-eval-data")
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "h5py==3.16.0", "anndata==0.12.19", "pandas>=2.2,<3", "numpy>=1.26")
FILES = ("Adamson2016_pilot.h5ad", "Adamson2016_10X005.h5ad", "Adamson2016_10X010.h5ad",
         "NormanWeissman2019_filtered.h5ad")
QUERY = ("PERK", "IRE1", "EIF2AK3", "ERN1", "C3orf72", "FOXL2NB", "KIAA1804", "MAP3K21", "C19orf26", "CBARP")


@app.function(image=image, cpu=1.0, memory=8192, timeout=900, volumes={"/data": DATA_VOL})
def inspect() -> dict:
    import anndata as ad

    out = {}
    for f in FILES:
        a = ad.read_h5ad(f"/data/datasets/{f}", backed="r")
        var = a.var
        cols = {c: [str(x) for x in var[c].head(3).tolist()] for c in var.columns}
        idx = [str(x) for x in var.index[:3]]
        hits = {}
        for q in QUERY:
            m = var.index.astype(str) == q
            row = {"in_index": bool(m.any())}
            for c in var.columns:
                s = var[c].astype(str)
                if (s == q).any():
                    row[f"in_{c}"] = True
            hits[q] = row
        obs_cols = [c for c in a.obs.columns if "pert" in c.lower() or "guide" in c.lower() or "target" in c.lower()]
        out[f] = {"n_vars": int(a.n_vars), "var_index_head": idx, "var_columns": cols,
                  "query": hits, "obs_pert_columns": obs_cols}
        a.file.close()
    return out


@app.local_entrypoint()
def main() -> None:
    import json

    print(json.dumps(inspect.remote(), indent=1))
