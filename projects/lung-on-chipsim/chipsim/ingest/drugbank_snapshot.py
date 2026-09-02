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
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
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

    Never writes outside `dest`, and leaves `dest` untouched when it raises BEFORE publishing; a failure
    during the publish loop can leave `dest` partly replaced, which verify_snapshot
    detects (the manifest and the files will disagree): every
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
            "fetched_utc": datetime.now(UTC).isoformat(timespec="seconds"),
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

    # H6: the manifest is written by the same process it certifies, so on its own
    # it proves only internal consistency — a wholly fabricated snapshot with a
    # matching manifest passes. Cross-check its commit against provenance.yaml,
    # which is HUMAN-written at T2 and is the independent claim about what was
    # pinned. Two artifacts from different authors must agree, or the manifest is
    # certifying itself.
    provenance_path = dest / "provenance.yaml"
    if provenance_path.is_file():
        import yaml

        provenance = yaml.safe_load(provenance_path.read_text()) or {}
        pinned = str(provenance.get("source_commit") or "").strip()
        certified = str(manifest.get("source_commit") or "").strip()
        if pinned and certified and pinned != certified:
            raise SnapshotFetchError(
                f"{MANIFEST_NAME} certifies commit {certified[:12]}… but "
                f"provenance.yaml pins {pinned[:12]}…. The snapshot on disk is not "
                "the one the human pinned at T2. The manifest cannot vouch for this "
                "— it was written by the process that fetched the files."
            )

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


#: What may legitimately be git-tracked under data/raw/: DVC pointers, directory
#: anchors, the integrity manifest, and T1/T2's human provenance artifacts.
VENDORING_ALLOWED_SUFFIXES = (".dvc",)
VENDORING_ALLOWED_NAMES = frozenset({".gitkeep", MANIFEST_NAME, "provenance.yaml", "PROVENANCE.md"})


def vendored_offenders(tracked_paths) -> list[str]:
    """Paths under data/raw/ that constitute REDISTRIBUTED payload.

    ChipSim never redistributes DrugBank. This is the single definition of that
    rule; T11's positive test and its falsification both call it, so a widened
    allow-list breaks the falsification too. (Previously the rule was restated
    inline in both tests, which made the falsification a closed tautology that
    imported no production code.)

    Deliberately NOT a `*.tsv` glob: per CTO ruling E-5 the DVC store holds the
    snapshot as EXTENSIONLESS md5 blobs, which a suffix glob would never catch.
    """
    offenders = []
    for path in tracked_paths:
        name = Path(path).name
        if path.endswith(VENDORING_ALLOWED_SUFFIXES) or name in VENDORING_ALLOWED_NAMES:
            continue
        offenders.append(path)
    return offenders


# --------------------------------------------------------------------------- #
# T5 · parse the compound table
# --------------------------------------------------------------------------- #

#: Row-count floor for the real snapshot. DrugBank 4.2 carries several thousand
#: compounds; anything under this means the parse silently produced a near-empty
#: frame. The floor is what makes T5's done-condition non-vacuous (defect 9) — a
#: column-only assertion passes trivially on an empty frame.
MIN_COMPOUND_ROWS = 1000

#: Columns T5 emits, in declared order (T5a persists in this order).
COMPOUND_COLUMNS = (
    "drugbank_id",
    "name",
    "type",
    "groups",
    "atc_codes",
    "inchi",
    "inchikey",
)

#: The upstream TSVs pipe-join multi-valued cells.
_LIST_SEP = "|"


def _split_list_cell(value: object) -> list[str]:
    """Pipe-joined string -> list[str]. Empty/NA -> []."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    text = str(value).strip()
    if not text:
        return []
    return [part.strip() for part in text.split(_LIST_SEP) if part.strip()]


def load_compounds(raw_dir: Path, min_rows: int = MIN_COMPOUND_ROWS) -> pd.DataFrame:
    """`raw_dir` contains drugbank.tsv, drugbank-slim.tsv, proteins.tsv at its TOP LEVEL.

    Columns: drugbank_id, name, type, groups (list[str]),
    atc_codes (list[str]), inchi, inchikey.
    Drops rows with no InChIKey. Does not canonicalise — that is T5b / harmonize/ids.py.

    `min_rows` is the non-vacuity floor (defect 9). It defaults to the real
    snapshot's floor; tests parsing a small fixture pass `min_rows=0` explicitly,
    so lowering it is always a visible act at the call site rather than a silent
    default.
    """
    path = Path(raw_dir) / "drugbank.tsv"
    if not path.is_file():
        raise FileNotFoundError(
            f"{path} not found. The snapshot is fetched by T4a "
            "(`python -m chipsim.ingest.drugbank_snapshot --dest ... --commit ...`)."
        )

    frame = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, na_values=[""])

    missing = [c for c in COMPOUND_COLUMNS if c not in frame.columns]
    if missing:
        raise ValueError(f"{path} is missing expected column(s): {missing}")

    frame = frame.loc[:, list(COMPOUND_COLUMNS)].copy()

    # Drop rows with no InChIKey: without a structure key there is nothing to
    # join on downstream, and T5b cannot canonicalise them.
    frame = frame[frame["inchikey"].notna() & (frame["inchikey"].str.strip() != "")]

    for column in ("groups", "atc_codes"):
        frame[column] = frame[column].map(_split_list_cell)

    frame = frame.reset_index(drop=True)

    if len(frame) < min_rows:
        raise ValueError(
            f"parsed only {len(frame)} compound rows from {path}, below the floor of "
            f"{min_rows}. An almost-empty frame passes every column assertion, so the "
            "floor is what makes this check non-vacuous (defect 9)."
        )
    return frame


# --------------------------------------------------------------------------- #
# T6 · parse the protein-edge table
# --------------------------------------------------------------------------- #

#: The four edge categories the upstream table uses. T6 asserts EQUALITY against
#: this set, not a subset (defect 9): a subset check passes on a frame that lost
#: three of the four categories to a bad filter.
EDGE_CATEGORIES = frozenset({"target", "enzyme", "transporter", "carrier"})

#: Only human edges are in scope.
HUMAN_ORGANISM = "Homo sapiens"

EDGE_COLUMNS = ("drugbank_id", "uniprot_id", "category", "organism")

#: Row-count floor for human protein edges on the real snapshot.
MIN_EDGE_ROWS = 1000


def load_protein_edges(
    raw_dir: Path,
    min_rows: int = MIN_EDGE_ROWS,
    require_all_categories: bool = True,
) -> pd.DataFrame:
    """Columns: drugbank_id, uniprot_id, category, organism.

    `category` is one of target, enzyme, transporter, carrier.
    Filters to organism == 'Homo sapiens'.

    `min_rows` and `require_all_categories` are the non-vacuity guards; tests that
    deliberately exercise a degenerate table lower them explicitly at the call site.
    """
    path = Path(raw_dir) / "proteins.tsv"
    if not path.is_file():
        raise FileNotFoundError(
            f"{path} not found. The snapshot is fetched by T4a "
            "(`python -m chipsim.ingest.drugbank_snapshot --dest ... --commit ...`)."
        )

    frame = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, na_values=[""])

    missing = [c for c in EDGE_COLUMNS if c not in frame.columns]
    if missing:
        raise ValueError(f"{path} is missing expected column(s): {missing}")

    frame = frame.loc[:, list(EDGE_COLUMNS)].copy()

    unknown = set(frame["category"].dropna().unique()) - EDGE_CATEGORIES
    if unknown:
        raise ValueError(
            f"{path} carries unexpected edge category/categories {sorted(unknown)}; "
            f"expected a subset of {sorted(EDGE_CATEGORIES)}"
        )

    frame = frame[frame["organism"] == HUMAN_ORGANISM].reset_index(drop=True)

    # The floor mirrors load_compounds. Without it an organism-label drift
    # ("Human" vs "Homo sapiens") silently yields ZERO edges, every compound then
    # labels 'unknown', and that is indistinguishable from a real absence of
    # evidence. An almost-empty frame passes every column assertion.
    if len(frame) < min_rows:
        raise ValueError(
            f"parsed only {len(frame)} human protein edges from {path}, below the floor "
            f"of {min_rows}. Check the organism filter: values must read exactly "
            f"{HUMAN_ORGANISM!r}."
        )

    # EQUALITY, asserted here rather than only in tests (defect 9). Restricting it
    # to the test suite means it runs only against a hand-built fixture and can
    # never fail on real data — a snapshot that lost three of four categories to a
    # bad filter would sail through.
    if require_all_categories:
        observed = set(frame["category"].dropna().unique())
        if observed != set(EDGE_CATEGORIES):
            raise ValueError(
                f"{path} yielded categories {sorted(observed)} after the "
                f"{HUMAN_ORGANISM!r} filter; expected exactly "
                f"{sorted(EDGE_CATEGORIES)}. A missing category means a filter "
                "dropped edges the pipeline depends on."
            )
    return frame


# --------------------------------------------------------------------------- #
# T5a · persist the compound frame
# --------------------------------------------------------------------------- #

#: Persisted column order. `canonical_inchikey` (T5b) leads because the frame is
#: sorted on it and every downstream task indexes on it.
PERSISTED_COMPOUND_COLUMNS = (
    "canonical_inchikey",
    "drugbank_id",
    "name",
    "type",
    "groups",
    "atc_codes",
    "inchi",
    "inchikey",
)

#: Parquet format version pinned so the bytes are reproducible across pyarrow
#: releases; compression off for the same reason.
_PARQUET_VERSION = "2.6"


def write_compounds(df: pd.DataFrame, out: Path) -> None:
    """Declared column order and dtypes, sorted by canonical_inchikey.

    pyarrow, version='2.6', compression=None.
    """
    missing = [c for c in PERSISTED_COMPOUND_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"cannot persist: frame is missing {missing}. "
            "Run add_canonical_identity() (T5b) before write_compounds() (T5a)."
        )

    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)

    frame = (
        df.loc[:, list(PERSISTED_COMPOUND_COLUMNS)]
        .sort_values("canonical_inchikey", kind="mergesort")
        .reset_index(drop=True)
    )

    frame.to_parquet(out, engine="pyarrow", version=_PARQUET_VERSION, compression=None, index=False)

    write_digest_sidecar(out)


def write_digest_sidecar(target: Path) -> str:
    """Write the digest sidecar beside a processed artifact and return the digest.

    NOTE the sidecar REPLACES the suffix — `drugbank_compounds.parquet` yields
    `drugbank_compounds.sha256`, not `...parquet.sha256`. That is what build-plan
    T5a specifies and what `.gitignore` tracks, so it is deliberate; the cost is
    that two artifacts sharing a stem would collide. `read_digest_sidecar` verifies
    the recorded filename to make such a collision visible instead of silent.

    The sidecar is git-tracked while the artifact itself is not: it is what lets a
    reviewer verify the artifact without it being redistributed.
    """
    target = Path(target)
    digest = _sha256(target)
    sidecar = target.with_suffix(".sha256")
    sidecar.write_text(f"{digest}  {target.name}\n")
    return digest


def read_digest_sidecar(target: Path) -> str:
    """Parse the digest out of the sidecar, verifying it describes THIS file.

    The sidecar body records the filename, so a stem collision (`x.parquet` and
    `x.csv` both writing `x.sha256`) is detectable here rather than silently
    handing back another artifact's digest.
    """
    target = Path(target)
    sidecar = target.with_suffix(".sha256")
    if not sidecar.is_file():
        raise FileNotFoundError(f"digest sidecar missing: {sidecar}")

    parts = sidecar.read_text().split()
    if len(parts) >= 2 and parts[1] != target.name:
        raise ValueError(
            f"{sidecar} records a digest for {parts[1]!r}, not {target.name!r}. "
            "Two artifacts sharing a stem have collided on one sidecar."
        )
    return parts[0]


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
