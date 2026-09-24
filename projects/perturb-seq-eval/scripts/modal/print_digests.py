"""T20 — print size, SHA-256 and MD5 of the four pinned datasets on the Modal volume.

CPU-only, no GPU, no network: reads the files already on ``perturb-eval-data:/datasets``.
MD5 is emitted so the copies can be cross-checked against Zenodo's published checksums
before the SHA-256 digests are pinned in ``perturb_eval.data.download.DATASETS`` (T21).

    modal run scripts/modal/print_digests.py
"""
from __future__ import annotations

import modal

app = modal.App("perturb-eval-print-digests")
DATA_VOL = modal.Volume.from_name("perturb-eval-data")
FILES = (
    "Adamson2016_pilot.h5ad",
    "Adamson2016_10X005.h5ad",
    "Adamson2016_10X010.h5ad",
    "NormanWeissman2019_filtered.h5ad",
)


@app.function(cpu=1.0, memory=1024, timeout=900, volumes={"/data": DATA_VOL})
def digests() -> list[dict]:
    import hashlib
    from pathlib import Path

    out = []
    for name in FILES:
        p = Path("/data/datasets") / name
        sha, md5, n = hashlib.sha256(), hashlib.md5(), 0
        with p.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                sha.update(chunk)
                md5.update(chunk)
                n += len(chunk)
        out.append({"file": name, "bytes": n, "sha256": sha.hexdigest(), "md5": md5.hexdigest()})
    return out


@app.local_entrypoint()
def main() -> None:
    import json

    for row in digests.remote():
        print(json.dumps(row))
