"""Fetch and parse the pinned public DrugBank 4.2 snapshot (dhimmel/drugbank).

The snapshot is a frozen, provenance-stamped copy of DrugBank 4.2 downloaded
2015-03-19, archived at doi:10.5281/zenodo.45579 and redistributed as derived
TSVs under CC BY-NC 4.0.

**ChipSim never redistributes DrugBank.** Files land under ``data/raw/``, which is
git-ignored and DVC-tracked. Only compound identity and drug->transporter/carrier
edges are taken from it — **never affinities**.

Populated by T3 (fetch). T5/T5a/T6 extend this module.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import requests

#: The three files slice 1 consumes. `mapping.tsv.gz` and `pubchem-mapping.tsv`
#: are consumed by no task here and arrive with the ChEMBL plan (minor note D).
SNAPSHOT_FILES = ("drugbank.tsv", "drugbank-slim.tsv", "proteins.tsv")

#: Upstream repo layout puts these under `data/`. They are written FLAT into
#: `dest`, with no nested `data/` level — T5/T6 expect them at the top level of
#: `raw_dir` (defect 7).
_REPO_SUBDIR = "data"
_RAW_BASE = "https://raw.githubusercontent.com"
_REPO = "dhimmel/drugbank"

_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

#: Name of the git-tracked (NOT DVC-tracked) integrity manifest.
MANIFEST_NAME = "SHA256SUMS.json"


class SnapshotFetchError(RuntimeError):
    """A snapshot file could not be retrieved or failed integrity checking."""


def _validate_commit(commit: str) -> str:
    """Reject anything that is not a full 40-hex commit SHA.

    A mutable branch head is not acceptable here: the whole point of the pin is
    that the snapshot cannot change under a 'frozen 2015 snapshot' claim
    (defect 17). Both the wrong-length and the right-length-wrong-alphabet cases
    are rejected — T3's done-condition tests both (defect 32).
    """
    if not isinstance(commit, str) or not _COMMIT_RE.match(commit):
        raise ValueError(
            f"commit must match ^[0-9a-f]{{40}}$ (a full, lowercase git SHA); got {commit!r}. "
            "Fetching by branch or short SHA is forbidden — the snapshot pin is what makes "
            "the provenance claim verifiable."
        )
    return commit


def snapshot_url(commit: str, basename: str) -> str:
    """URL of one snapshot file at a pinned commit."""
    return f"{_RAW_BASE}/{_REPO}/{commit}/{_REPO_SUBDIR}/{basename}"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _download(url: str, target: Path) -> None:
    resp = requests.get(url, stream=True, timeout=60)
    if resp.status_code != 200:
        raise SnapshotFetchError(f"GET {url} returned HTTP {resp.status_code}")
    with target.open("wb") as fh:
        for chunk in resp.iter_content(chunk_size=1 << 20):
            if chunk:
                fh.write(chunk)


def fetch_snapshot(dest: Path, commit: str) -> dict[str, str]:
    """Download SNAPSHOT_FILES from raw.githubusercontent at `commit`.

    Each file is written to ``dest/<basename>`` — FLAT, no nested ``data/`` level
    (defect 7). Returns ``{basename: sha256}``.

    Also writes ``dest/SHA256SUMS.json`` (git-tracked, NOT DVC)::

        {"source_commit": <40-hex>, "fetched_utc": <iso8601>,
         "files": {<basename>: <sha256>}}

    Raises ``ValueError`` unless `commit` matches ``^[0-9a-f]{40}$``.

    Never writes outside `dest`, and leaves `dest` untouched when it raises: every
    file is downloaded into a temporary directory first and only moved into place
    once all three have arrived. A half-fetched snapshot that still carried a
    manifest would be indistinguishable from a complete one.
    """
    _validate_commit(commit)
    dest = Path(dest)

    with tempfile.TemporaryDirectory(prefix="chipsim-snapshot-") as tmp:
        staging = Path(tmp)
        digests: dict[str, str] = {}
        for basename in SNAPSHOT_FILES:
            target = staging / basename
            _download(snapshot_url(commit, basename), target)
            digests[basename] = _sha256(target)

        manifest = {
            "source_commit": commit,
            "fetched_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "files": dict(digests),
        }
        (staging / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

        # Everything succeeded — publish atomically-ish into dest.
        dest.mkdir(parents=True, exist_ok=True)
        for name in (*SNAPSHOT_FILES, MANIFEST_NAME):
            shutil.move(str(staging / name), str(dest / name))

    return digests


def verify_snapshot(dest: Path) -> dict[str, str]:
    """Recompute each file's sha256 and check it against ``SHA256SUMS.json``.

    Returns the recomputed digests. Raises ``SnapshotFetchError`` on any mismatch,
    missing file, or missing manifest — this is what makes a post-fetch mutation
    detectable (defect 2).
    """
    dest = Path(dest)
    manifest_path = dest / MANIFEST_NAME
    if not manifest_path.is_file():
        raise SnapshotFetchError(
            f"no {MANIFEST_NAME} in {dest} — snapshot provenance is unverifiable"
        )
    manifest = json.loads(manifest_path.read_text())
    recorded = manifest.get("files", {})

    recomputed: dict[str, str] = {}
    problems = []
    for basename in SNAPSHOT_FILES:
        path = dest / basename
        if not path.is_file():
            problems.append(f"{basename}: missing from {dest}")
            continue
        recomputed[basename] = _sha256(path)
        if basename not in recorded:
            problems.append(f"{basename}: absent from {MANIFEST_NAME}")
        elif recomputed[basename] != recorded[basename]:
            problems.append(
                f"{basename}: sha256 mismatch — manifest {recorded[basename]}, on disk {recomputed[basename]}"
            )
    if problems:
        raise SnapshotFetchError("snapshot integrity check failed:\n  " + "\n  ".join(problems))
    return recomputed


def _main(argv=None) -> int:
    """CLI entrypoint — T4a runs this. Named in the T16 workflow export."""
    import argparse

    ap = argparse.ArgumentParser(prog="python -m chipsim.ingest.drugbank_snapshot")
    ap.add_argument("--dest", required=True, type=Path)
    ap.add_argument(
        "--commit",
        required=True,
        help="40-hex source_commit from data/raw/drugbank/provenance.yaml (pinned by H in T2)",
    )
    ns = ap.parse_args(argv)
    digests = fetch_snapshot(ns.dest, ns.commit)
    for name, digest in sorted(digests.items()):
        print(f"{digest}  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
