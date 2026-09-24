"""CTO #250 evidence pass — measure, from the data, whether a label->gene alias is supported.

Read-only, CPU only. For each (dataset, label, candidate gene): cells labelled with the label vs control
cells, per-cell library-size normalised (1e4) + log1p, mean expression of the candidate gene in each group,
the delta, and the delta's rank among all genes (1 = most down-regulated). Also records the candidate's
Ensembl ID and cross-dataset Ensembl identity for renamed symbols, and each label's obs.nperts.
Candidates are hypotheses to be tested; nothing here asserts them.

    modal run scripts/modal/label_evidence.py
"""
from __future__ import annotations

import modal

app = modal.App("perturb-eval-label-evidence")
DATA_VOL = modal.Volume.from_name("perturb-eval-data")
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "h5py==3.16.0", "anndata==0.12.19", "pandas>=2.2,<3", "numpy>=1.26", "scipy>=1.11")

ADAMSON = ("Adamson2016_pilot.h5ad", "Adamson2016_10X005.h5ad", "Adamson2016_10X010.h5ad")
NORMAN = "NormanWeissman2019_filtered.h5ad"
# (label, candidate gene) — hypotheses under test.
ADAMSON_Q = (("PERK", "EIF2AK3"), ("IRE1", "ERN1"))
NORMAN_Q = (("C3orf72", "FOXL2NB"), ("C19orf26", "CBARP"), ("KIAA1804", None))
NORMAN_CTRL = {"non-targeting", "nontargeting", "ctrl", "control", "nt", "ntc"}
EXTRA_LABELS = ("3x", "Gal4-4(mod)")


def _lognorm(X):
    import numpy as np
    import scipy.sparse as sp

    X = X.tocsr().astype(np.float64) if sp.issparse(X) else np.asarray(X, dtype=np.float64)
    lib = np.asarray(X.sum(axis=1)).ravel()
    lib[lib == 0] = 1.0
    if sp.issparse(X):
        X = sp.diags(1e4 / lib) @ X
        X.data = np.log1p(X.data)
        return X
    return np.log1p(X * (1e4 / lib)[:, None])


def _means(X, mask):
    import numpy as np

    return np.asarray(X[mask].mean(axis=0)).ravel()


def _test(X, var_names, lab_mask, ctrl_mask, gene):
    import numpy as np

    mu_l, mu_c = _means(X, lab_mask), _means(X, ctrl_mask)
    delta = mu_l - mu_c
    order = np.argsort(delta, kind="stable")  # most negative first
    rank = {int(g): r + 1 for r, g in enumerate(order)}
    top = [(str(var_names[i]), round(float(delta[i]), 4)) for i in order[:5]]
    row = {"n_labelled_cells": int(lab_mask.sum()), "n_control_cells": int(ctrl_mask.sum()),
           "top5_most_down": top}
    if gene is not None:
        hit = np.flatnonzero(np.asarray(var_names) == gene)
        if hit.size:
            g = int(hit[0])
            row.update({"gene": gene, "in_vocab": True,
                        "mean_log_labelled": round(float(mu_l[g]), 4),
                        "mean_log_control": round(float(mu_c[g]), 4),
                        "delta": round(float(delta[g]), 4),
                        "delta_rank_among_genes": rank[g], "n_genes": int(len(var_names))})
        else:
            row.update({"gene": gene, "in_vocab": False})
    return row


@app.function(image=image, cpu=2.0, memory=16384, timeout=1800, volumes={"/data": DATA_VOL})
def evidence() -> dict:
    import anndata as ad
    import numpy as np

    out: dict = {"adamson": {}, "norman": {}, "ensembl": {}, "nperts": {}}
    ens_by_symbol: dict = {}
    for f in ADAMSON:
        a = ad.read_h5ad(f"/data/datasets/{f}")
        raw = a.obs["perturbation"].astype(str).to_numpy()
        norm = np.array([r.split("_")[0] for r in raw])
        ctrl = np.array([r == "*" or r.startswith("62(") for r in raw])
        X = _lognorm(a.X)
        vn = a.var_names.to_numpy()
        for s in ("C3orf72", "C19orf26", "KIAA1804", "EIF2AK3", "ERN1"):
            if s in a.var_names:
                ens_by_symbol.setdefault(s, {})[f] = str(a.var.loc[s, "ensembl_id"])
        for lab in (*[q[0] for q in ADAMSON_Q], *EXTRA_LABELS):
            m = norm == lab
            if m.any() and "nperts" in a.obs:
                out["nperts"].setdefault(lab, {})[f] = sorted({str(v) for v in a.obs.loc[m, "nperts"]})
        for lab, gene in ADAMSON_Q:
            m = norm == lab
            if m.any():
                out["adamson"].setdefault(lab, {})[f] = _test(X, vn, m, ctrl, gene)
        del a, X
    a = ad.read_h5ad(f"/data/datasets/{NORMAN}")
    pert = a.obs["perturbation"].astype(str).to_numpy()
    ctrl = np.array([p.lower() in NORMAN_CTRL for p in pert])
    X = _lognorm(a.X)
    vn = a.var_names.to_numpy()
    ens_col = "ensemble_id" if "ensemble_id" in a.var else "ensembl_id"
    for lab, gene in NORMAN_Q:
        m = pert == lab  # singleton cells only: the cleanest test
        out["norman"][lab] = _test(X, vn, m, ctrl, gene)
        if gene is not None and gene in a.var_names:
            out["norman"][lab]["ensembl_id"] = str(a.var.loc[gene, ens_col])
        out["nperts"].setdefault(lab, {})[NORMAN] = sorted({str(v) for v in a.obs.loc[m, "nperts"]}) if m.any() else []
    for old, new in (("C3orf72", "FOXL2NB"), ("C19orf26", "CBARP")):
        norman_id = str(a.var.loc[new, ens_col]) if new in a.var_names else None
        adamson_ids = ens_by_symbol.get(old, {})
        out["ensembl"][f"{old}->{new}"] = {"norman_" + new: norman_id, "adamson_" + old: adamson_ids,
                                           "identical": bool(norman_id) and set(adamson_ids.values()) == {norman_id}}
    out["ensembl"]["adamson_symbol_ids"] = ens_by_symbol
    return out


@app.local_entrypoint()
def main() -> None:
    import json

    print(json.dumps(evidence.remote(), indent=1))
