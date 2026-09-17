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
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import requests
import yaml

from chipsim.guards.output_roots import refuse_unless_declared_output_root
from chipsim.journal import source_root

#: The three files slice 1 consumes. `mapping.tsv.gz` and `pubchem-mapping.tsv`
#: are consumed by no task here and arrive with the ChEMBL plan (minor note D).
SNAPSHOT_FILES = ("drugbank.tsv", "drugbank-slim.tsv", "proteins.tsv")

#: r2.11 — one DVC pointer per snapshot file, beside the TSV it describes. A single
#: directory pointer over data/raw/drugbank/ is unsatisfiable while provenance.yaml,
#: PROVENANCE.md and SHA256SUMS.json are git-tracked inside it (dvc/output.py:670).
#: DERIVED, not restated: the three test tables that guard the pointers import this,
#: so a fourth snapshot file cannot silently escape them (QG-10).
DVC_POINTERS = tuple(f"data/raw/drugbank/{name}.dvc" for name in SNAPSHOT_FILES)

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
VENDORING_ALLOWED_NAMES = frozenset(
    {
        ".gitkeep",
        MANIFEST_NAME,
        "provenance.yaml",
        "PROVENANCE.md",
        # Added 2026-09-14: the CTO's extended source-provenance file, landed on
        # trunk under data/raw/. It is provenance ABOUT the payload, exactly like
        # provenance.yaml, and carries no redistributed content — so allowing it
        # widens the allow-list by a metadata file rather than by a data class.
        "sources.yaml",
    }
)

#: A real DVC pointer is a few lines of YAML. Anything larger under a `.dvc` name is
#: payload wearing the allowed suffix — a suffix allow-list on its own would let a
#: renamed `drugbank.tsv` through (QG-9).
POINTER_MAX_BYTES = 4096

_MD5_RE = re.compile(r"^[0-9a-f]{32}$")


def pointer_defects(doc, *, expected_path: str, file: Path | None = None) -> list[str]:
    """Why a parsed `.dvc` document does NOT describe `expected_path` — `[]` when it does.

    The single definition of "is a pointer" (QG-13). T4's integration test and
    T11's unit tests both call it, and its falsification rows live beside them;
    an inline `doc["outs"][0]["md5"]` check had no negative case and failed a
    malformed pointer with a bare IndexError/KeyError instead of a diagnosis.

    Structural checks always run: `outs[0]` exists, `md5` is a 32-hex digest,
    `size` is a positive integer, `path` names the expected file. With `file`,
    the pointer is BOUND to that file: its size and md5 must match what is on disk
    (QG-4) — three copies of one pointer satisfy every structural check.
    """
    outs = doc.get("outs") if isinstance(doc, dict) else None
    if not isinstance(outs, list) or not outs or not isinstance(outs[0], dict):
        return ["outs: missing or empty — not a DVC pointer"]
    out = outs[0]
    defects: list[str] = []

    md5 = out.get("md5")
    if not isinstance(md5, str) or not _MD5_RE.fullmatch(md5):
        defects.append(f"md5: {md5!r} is not a 32-hex digest")
    size = out.get("size")
    if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
        defects.append(f"size: {size!r} is not a positive integer")
    path = out.get("path")
    if path != expected_path:
        defects.append(f"path: {path!r} does not name the expected file {expected_path!r}")

    if file is not None:
        if not file.is_file():
            defects.append(f"file: {file} is absent")
        else:
            actual_size = file.stat().st_size
            if isinstance(size, int) and not isinstance(size, bool) and size != actual_size:
                defects.append(f"size: pointer says {size}, file on disk is {actual_size}")
            actual_md5 = hashlib.md5(file.read_bytes()).hexdigest()
            if md5 != actual_md5:
                defects.append(f"md5: pointer says {md5}, file on disk is {actual_md5}")
    return defects


def _is_pointer_shaped(path: Path) -> bool:
    """A `.dvc` file that is small, parses as YAML, and passes `pointer_defects`
    for the file its name implies. Nothing else earns the allowed suffix."""
    if not path.is_file() or path.stat().st_size > POINTER_MAX_BYTES:
        return False
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError):
        return False
    return pointer_defects(doc, expected_path=path.name.removesuffix(".dvc")) == []


def vendored_offenders(tracked_paths, *, root: Path | None = None) -> list[str]:
    """Paths under data/raw/ that constitute REDISTRIBUTED payload.

    ChipSim never redistributes DrugBank. This is the single definition of that
    rule; T11's positive test and its falsification both call it, so a widened
    allow-list breaks the falsification too. (Previously the rule was restated
    inline in both tests, which made the falsification a closed tautology that
    imported no production code.)

    Deliberately NOT a `*.tsv` glob: per CTO ruling E-5 the DVC store holds the
    snapshot as EXTENSIONLESS md5 blobs, which a suffix glob would never catch.

    With `root`, a `.dvc` path is allowed only if the file there is pointer-shaped
    (`_is_pointer_shaped`) — the suffix alone no longer admits it (QG-9). Without
    `root` the rule is name-only, for callers that have paths but no tree.
    """
    offenders = []
    for path in tracked_paths:
        name = Path(path).name
        if name in VENDORING_ALLOWED_NAMES:
            continue
        if path.endswith(VENDORING_ALLOWED_SUFFIXES) and (
            root is None or _is_pointer_shaped(Path(root) / path)
        ):
            continue
        offenders.append(path)
    return offenders


#: A REAL DrugBank accession. The synthetic range DB9nnnn (DB90001…) that the
#: test fixtures use is excluded by the lookahead, so fixtures never match.
REAL_ACCESSION_RE = re.compile(r"\bDB(?!9\d{4}\b)\d{5}\b")

#: Every path below is relative to the REPOSITORY root, because the scan walks the whole
#: repository (CTO #122 §5). The keys used to be project-relative; under a repo-root walk
#: those would silently stop matching and the scan would report clean for the wrong reason.

#: The sanctioned exclusion LEDGER (#120 §4): it may carry real accessions — a study that
#: cannot name what it excluded cannot report its exclusions — but NOT an accession
#: associated with a structure (see `ledger_tuple_hits`).
DRUGBANK_ID_LEDGER = frozenset(
    {
        # The CLOSED unparseable-InChI roster: principal's ruling 2026-09-14,
        # "exclude these, recorded by ID".
        "projects/lung-on-chipsim/configs/unparseable_compounds.yaml",
        # Its tests cite the same eight IDs — the roster is closed and the tests
        # pin that it raises on an unlisted failure and on a listed compound that
        # parses again, which cannot be written without naming the members.
        "projects/lung-on-chipsim/tests/test_unparseable_exclusions.py",
    }
)

#: Single FILES excluded by ruling. Named files, never patterns over a directory.
#:
#: EMPTY, deliberately. The approval log was excluded here until the CTO reversed that
#: ruling (2026-09-16): a log row may be corrected IN PLACE when the correction is disclosed
#: in the row. Once that is the rule, an exclusion means the guard takes a row's "corrected"
#: claim on trust — a check that cannot see what it certifies. The log was scanned clean
#: before the exclusion was removed, so the change could not turn a green suite red.
DRUGBANK_ID_EXCLUDED_FILES: frozenset[str] = frozenset()

#: Dispatch payloads at any depth under .claude/usr/ (#122 §3): coordination records.
#: Redacting a sent message falsifies the audit trail of the rulings it carries.
#: (r2.21 E6-4) `.md` ONLY. #122 §3 waives dispatch payloads because redacting a sent MESSAGE
#: falsifies the audit trail of the rulings it carries — reasoning that covers a message, not
#: arbitrary bytes that happen to sit in the directory. Proven at §6: a tracked
#: `dispatches/leak.pdf` carrying a real accession was DOUBLE-exempt (undecodable AND waived) with
#: the whole suite green.
_DISPATCH_PAYLOAD_RE = re.compile(r"^\.claude/usr/(?:[^/]+/)+dispatches/[^/]+\.md$")

#: Union kept for callers that only need membership of the named files.
DRUGBANK_ID_EXCEPTIONS = DRUGBANK_ID_LEDGER | DRUGBANK_ID_EXCLUDED_FILES


def _is_dispatch_message(root: Path, rel: str) -> bool:
    """Is this dispatch payload an actual MESSAGE — i.e. does it decode as text?

    #122 §3 waives dispatch payloads because redacting a sent MESSAGE falsifies the audit trail of
    the rulings it carries. That reasoning is about text a human wrote and sent. A binary blob is
    not a message whatever it is named, and deciding messagehood by FILENAME meant the same payload
    that fails as `leak.pdf` was DOUBLE-exempt as `leak.md` — waived from the accession scan and
    skipped by the undecodable report, listed nowhere. Two reviewers executed it independently.

    This module's own doctrine, two functions away: "dispatch on the MAGIC, not on the name".
    """
    if not _DISPATCH_PAYLOAD_RE.match(rel):
        return False
    target = Path(root) / rel
    if not target.is_file():
        return True  # nothing to read; the path shape is all we have
    try:
        return _decode_text(target.read_bytes()) is not None
    except OSError:
        return False


def is_accession_excluded(rel: str) -> bool:
    """True when a repo-relative path is in the ruled exclusion set — and nothing else is:
    the ledger pair, the named excluded files, and dispatch payloads."""
    rel = str(rel)
    return rel in DRUGBANK_ID_EXCEPTIONS or bool(_DISPATCH_PAYLOAD_RE.match(rel))


#: Tracked files the scan CANNOT decode as text and which are DECLARED, by exact path, to be
#: artifacts rather than record carriers (CTO ruling, QG §5 E-3). Declared individually, never by
#: suffix or directory: a suffix rule waves through the next binary nobody looked at, which is the
#: silent-skip this list exists to end. A new undecodable tracked file FAILS the guard until
#: someone reads it and adds it here.
#:
#: Files THIS PROJECT declares unreadable — RENDERED ARTIFACTS ONLY (r2.21 E6-2): a readable
#: structured container is always read, never declared. EMPTY today, and that is the correct state:
#: this project owns no undecodable tracked file.
#:
#: The 23 paths that used to sit here belonged to `perturb-seq-eval` and `paper_standalone`, and
#: declaring another team's artifacts inside this module assigned them this module's failure mode
#: and repair path (r2.21 E6-1) — a decision that looked like bookkeeping while it assigned
#: ownership. They are now LISTED by `undeclared_report` with their owner named, and fail their
#: owner's gate rather than this one (r2.22 E6-1b). They are NOT re-declared here on those teams'
#: behalf.
RENDERED_ARTIFACT_DECLARATIONS: frozenset[str] = frozenset()


#: HDF5's signature. `h5ad` is HDF5, and AnnData's `obs`/`var` carry names and identifiers — the
#: same argument that made parquet's footer readable (r2.21 E6-2). A readable structured container
#: is ALWAYS read; only RENDERED artifacts (figures, typeset PDFs) may be declared.
_HDF5_MAGIC = b"\x89HDF\r\n\x1a\n"

#: Per-dataset ceiling. `_MAX_SCAN_BYTES` bounds the file ON DISK; a compressed dataset expands
#: far beyond it (206 KB -> 200 MB measured, 950x), and the parquet path is already batched.
_MAX_DATASET_BYTES = 64 * 1024 * 1024


class _UnreadableContainer(RuntimeError):
    """A structured container could not be fully read — REPORTABLE, never clean."""


class MissingContainerReader(RuntimeError):
    """No reader is installed for a structured container.

    Distinct from `_UnreadableContainer` so it can PROPAGATE: E6-2 says a container is always read,
    so "no reader" must stop the scan loudly rather than become "undecodable — declare it", which
    is the one answer a container may not receive. Distinct from a bare RuntimeError because h5py
    raises those for some malformed files, and those ARE reportable.
    """


#: Indirected so a test can remove the reader and assert the guard fails LOUDLY rather than
#: reporting "undecodable — declare it", which for a container is the one answer E6-2 forbids.
try:  # pragma: no cover - import guard
    import h5py as _HDF5_READER
except ImportError:  # pragma: no cover
    _HDF5_READER = None

#: Bytes a parquet file starts and ends with. Dispatch on the MAGIC, not on the name (QG §6):
#: `UP.PARQUET`, `.pq` and an extensionless blob are all real parquet, and a suffix test sent each
#: of them down the "cannot be decoded — declare it" path, whose remedy would have made a fully
#: readable record carrier permanently invisible. This repo already closed one case-sensitivity
#: bypass (84ce8e0); the same shape came back here.
_PARQUET_MAGIC = b"PAR1"

#: Rows per batch when scanning a parquet. Bounded deliberately: a 30 KiB dictionary-encoded file
#: expanded to 186.9 MiB as one string (6,317x, 592 MiB peak RSS), measured — and a guard that
#: OOMs produces no verdict at all, which is the same false-clean in a new costume.
_PARQUET_BATCH_ROWS = 10_000

#: Above this, a file is REPORTED as unscannable rather than read. A reported refusal is
#: actionable; an OOM mid-scan is not.
_MAX_SCAN_BYTES = 256 * 1024 * 1024

#: Verdict cache keyed by (path, mtime_ns, size): both callers walk the whole tracked tree, so an
#: uncached parquet was parsed and stringified TWICE per suite run.
_READABILITY_CACHE: dict[tuple[str, int, int], bool] = {}


def _decode_text(data: bytes) -> str | None:
    """Decode bytes that are TEXT in some encoding, or None when they are genuinely not text.

    UTF-16 and latin-1 documents carrying a real accession were classified "undecodable" and the
    only remedy offered was the allow-list — which would have made a PLAIN-TEXT accession carrier
    permanently invisible (measured on both encodings). UTF-16 in particular is a routine artifact
    of Windows-authored files.

    latin-1 decodes ANY byte sequence, so it cannot be the last resort unconditionally: a NUL byte
    or a low printable ratio means binary, and binary must stay REPORTABLE rather than become a
    string of mojibake that scans clean.
    """
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        try:
            return data.decode("utf-16")
        except UnicodeDecodeError:
            return None
    for encoding in ("utf-8", "utf-8-sig"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    if b"\x00" in data:
        return None
    try:
        text = data.decode("latin-1")
    except UnicodeDecodeError:  # pragma: no cover - latin-1 decodes every byte
        return None
    printable = sum(ch.isprintable() or ch in "\r\n\t" for ch in text)
    return text if text and printable / len(text) >= 0.9 else None


def _parquet_chunks(target: Path):
    """Every scannable part of a parquet: the FOOTER METADATA first, then the rows in batches.

    The metadata is not decoration. A table whose schema metadata carried
    {"drugbank_id": <real>, "name": <coined title>, "inchi": ...} scanned as ",harmless\n0,1\n" —
    the complete record present in the file, absent from the scanned text, and reported by NEITHER
    half of the guard, so its own tests certified the file clean. `pq.write_table(..., metadata=)`
    is ordinary, and DuckDB/Spark/Polars stamp metadata by default.

    Rows are yielded per batch rather than as one string, and list/array cells are stringified
    explicitly: numpy's repr ELIDES above 1000 elements, so an accession at position 1500 of a
    `groups` list vanished — and `write_compounds` persists `groups` and `atc_codes` as list
    columns, so that is this project's own shape.
    """
    import pyarrow.parquet as pq

    schema = pq.read_schema(target)
    meta_parts: list[str] = [str(schema)]
    for holder in (schema.metadata, *(field.metadata for field in schema)):
        for key, value in (holder or {}).items():
            meta_parts.append(f"{key.decode('latin-1')}={value.decode('latin-1')}")
    yield "\n".join(meta_parts)

    def _cell(value):
        """Stringify a cell by VALUE.

        Iterating a dict yields KEYS, so a top-level struct column scanned as
        `[accession,name,inchi]` while the record sat in the file's bytes — the §6 pattern in the
        one nested shape that was still eliding.
        """
        if isinstance(value, (str, bytes)) or not hasattr(value, "__len__"):
            return value
        if isinstance(value, dict):
            return "{" + ",".join(f"{k}={_cell(v)}" for k, v in value.items()) + "}"
        return "[" + ",".join(str(_cell(item)) for item in value) + "]"

    for batch in pq.ParquetFile(target).iter_batches(batch_size=_PARQUET_BATCH_ROWS):
        frame = batch.to_pandas()
        yield frame.map(_cell).to_csv(index=True)


def _hdf5_chunks(target: Path):
    """Every string dataset and every attribute in an HDF5/h5ad container.

    Numeric arrays are skipped deliberately: a 14.7M-element expression matrix cannot carry a
    compound name, and reading it would make the repo-wide scan unusable. Names and identifiers
    live in string datasets (`obs`, `var`) and in attributes — the HDF5 analogue of the parquet
    footer that carried a whole record invisibly at §6.
    """
    if _HDF5_READER is None:
        raise MissingContainerReader(
            f"{target} is an HDF5 container and no reader is installed (h5py). A container is "
            "ALWAYS read, never declared unread (r2.21 E6-2), so this fails loudly rather than "
            "inviting a declaration. Install the dev dependencies."
        )

    parts: list[str] = []
    datasets_seen = 0

    def _stringify(values) -> str:
        """Every element, never `repr(array)`.

        numpy's repr SUMMARISES above 1,000 elements, so the repo's own 34.6 MB container scanned
        to 4,270 characters with three elision markers: under 0.5% of its string content examined
        while reporting clean. `_parquet_chunks` fixed exactly this one clause earlier; the HDF5
        reader reintroduced it.
        """
        flat = getattr(values, "ravel", lambda: values)()
        return "\n".join(str(item) for item in flat)

    def visit(name, node):
        nonlocal datasets_seen
        parts.append(name)
        for key, value in getattr(node, "attrs", {}).items():
            parts.append(f"{key}={value!r}")

        dtype = getattr(node, "dtype", None)
        if dtype is None:
            return
        datasets_seen += 1

        # Compound/structured dtypes (`kind == "V"`) are the on-disk shape of every HDF5 table and
        # of legacy AnnData obs/var recarrays. Skipping them meant a dataset holding the whole
        # record scanned to seven characters.
        readable = dtype.kind in {"O", "S", "U", "V"}
        if not readable:
            return

        nbytes = getattr(node, "nbytes", 0) or 0
        if nbytes > _MAX_DATASET_BYTES:
            # Bounded like the parquet path: a 206 KB compressed dataset materialised 200 MB
            # (950x). A guard that OOMs gives no verdict at all.
            raise _UnreadableContainer(
                f"{name} is {nbytes} bytes uncompressed, above the scan bound"
            )
        try:
            values = node[()]
        except Exception as exc:
            # An unreadable dataset used to be annotated `<unreadable>` and the file still counted
            # as READ and scanned CLEAN. "A skipped file is an unchecked file" applies inside a
            # container too — this is the hdf5plugin-missing case, measured.
            raise _UnreadableContainer(f"{name} could not be read: {exc}") from exc
        parts.append(_stringify(values))

    with _HDF5_READER.File(target, "r") as handle:
        for key, value in handle.attrs.items():
            parts.append(f"{key}={value!r}")
        for name in handle:
            # `visititems` skips soft and external LINKS, so a container whose only members were
            # links produced an empty chunk and passed as "read".
            raw = handle.get(name, getlink=True)
            if isinstance(raw, (_HDF5_READER.SoftLink, _HDF5_READER.ExternalLink)):
                raise _UnreadableContainer(f"{name} is a link this scan does not follow")
        handle.visititems(visit)

    text = "\n".join(parts)
    if not text.strip():
        raise _UnreadableContainer("the container yielded no scannable content")
    yield text


def _scan_chunks(target: Path):
    """Chunks of scannable text for one file, or None when nothing can be read from it.

    None means REPORTABLE — `undecodable_unallowed` turns it into a failure unless the path is
    declared. It never means "clean".
    """
    try:
        size = target.stat().st_size
    except OSError:
        return None
    if size > _MAX_SCAN_BYTES:
        return None

    try:
        head = target.open("rb").read(8)
    except OSError:
        return None

    if head.startswith(_HDF5_MAGIC):
        try:
            return list(_hdf5_chunks(target))
        except MissingContainerReader:
            raise
        except _UnreadableContainer:
            # Partially-read IS unread: reported, never clean. E6-2 forbids answering this with a
            # declaration, and `test_no_readable_structured_container_is_declared` enforces that,
            # so the file stays visible until someone makes it readable.
            return None
        except MemoryError:
            raise
        except Exception:  # noqa: BLE001 - unreadable container: REPORTABLE, never clean
            return None

    if head.startswith(_PARQUET_MAGIC):
        try:
            return list(_parquet_chunks(target))
        except MemoryError:
            # NOT swallowed with everything else: an exhausted scan must never be remediable by
            # declaring the file, which is what the generic "undecodable" message invites.
            raise
        except ImportError:
            raise
        except Exception:  # noqa: BLE001 - an unreadable parquet is REPORTABLE, never clean
            return None

    try:
        data = target.read_bytes()
    except OSError:
        return None
    text = _decode_text(data)
    return None if text is None else [text]


def _is_readable(target: Path) -> bool:
    try:
        stat = target.stat()
        key = (str(target), stat.st_mtime_ns, stat.st_size)
    except OSError:
        return False
    if key not in _READABILITY_CACHE:
        _READABILITY_CACHE[key] = _scan_chunks(target) is not None
    return _READABILITY_CACHE[key]


#: This module's project, DERIVED. A bare literal bound to nothing meant that renaming the
#: project directory turned every path this project owns into "somebody else's": failing_undeclared
#: returns [] and THE GATE GOES GREEN — fail-open, reached by a rename nobody would think of as a
#: guard change.
THIS_PROJECT = Path(source_root()).name

#: Which project OWNS a repo-relative path (r2.22, E6-1b). Explicit, because the alternative is a
#: default, and a default here would silently make somebody else responsible for a failure they
#: cannot see. Order matters: the first matching prefix wins.
#:
#: A path matching NOTHING is UNOWNED BY DEFINITION, never "somebody else's" — and unowned FAILS
#: this gate. That rule is LOAD-BEARING FOR E6-4: `.claude/usr/**/dispatches/` belongs to no
#: project, so a non-.md dispatch payload keeps failing here. Without it, scoping would have made
#: `dispatches/leak.pdf` listed and unfailable ANYWHERE — re-opening the hole E6-4 closed one
#: clause above, in the same revision that closed it.
#: The WHOLE map (r2.22 calls it "an explicit map"). `workstreams/` used to be a hardcoded branch
#: below, outside the constant whose docstring calls itself the source of truth, so a reader
#: auditing the map saw two thirds of the rule.
#: (prefix, owner segment index, the tracked file that PROVES the owner exists). The marker is
#: what stops an owner being minted by mkdir: `libs/ghost-lib/payload.bin` used to report
#: `owner=ghost-lib [listed]` and exit 0, so a payload parked under a name nobody owns failed the
#: only gate that exists. The docstring below already condemned exactly this at depth 1
#: (`projects/README.pdf` -> owner "README.pdf"); this is that hole one segment deeper.
_OWNERSHIP_PREFIXES = (
    ("projects/", 1, "pyproject.toml"),  # projects/<owner>/...
    ("libs/", 1, "pyproject.toml"),  # libs/<owner>/...
    ("workstreams/", 1, "plan/build-plan.md"),  # workstreams/<owner>/...
    ("paper_standalone/", 0, "README.md"),  # the directory IS the project
)


def recognised_owners(paths) -> frozenset[str]:
    """The projects that DEMONSTRABLY exist, read from the tracked listing itself.

    An owner is recognised only when the repository tracks its marker. Creating the directory
    cannot mint one, because the attacker's file already had to create the directory — existence of
    the directory is therefore worth nothing as evidence.
    """
    tracked = set(paths)
    found: set[str] = set()
    for prefix, index, marker in _OWNERSHIP_PREFIXES:
        head = prefix.rstrip("/")
        if index == 0:
            # NOT "any path under it": the payload's own path would then prove its owner exists,
            # which is the self-certification the marker is here to prevent.
            if f"{head}/{marker}" in tracked:
                found.add(head)
            continue
        for rel in tracked:
            parts = Path(rel).parts
            if (
                len(parts) > index
                and parts[0] == head
                and f"{head}/{parts[index]}/{marker}" in tracked
            ):
                found.add(parts[index])
    return frozenset(found)


def path_owner(rel: str, recognised: frozenset[str]) -> str | None:
    """The project owning a repo-relative path, or None when no project owns it.

    An owner must own a SUBTREE. `projects/README.pdf` used to return "README.pdf" — an invented
    project — so a stray file directly under `projects/` failed NOBODY's gate: listed under a
    fabricated owner, skipped by the accession scan as unreadable, live test green. That is the
    double-exempt hole E6-4 closed, re-opened one function below the comment calling
    unowned-fails-here LOAD-BEARING FOR E6-4. `projects/../configs/x` returned ".." the same way.

    `recognised` is REQUIRED, not defaulted: an optional registry would let any future caller opt
    back into invented owners by omitting it, which is the same shape as the `root=None` parameter
    this revision removed one function below.

    Unowned is the SAFE answer here (it fails this gate), so every doubtful shape returns None.
    """
    parts = Path(rel).parts
    if not parts or ".." in parts or Path(rel).is_absolute():
        return None
    for prefix, index, _marker in _OWNERSHIP_PREFIXES:
        head = prefix.rstrip("/")
        if parts[0] != head:
            continue
        if index == 0:
            return head if head in recognised else None
        # An owner owns a subtree: there must be a segment AFTER the owner segment.
        if len(parts) > index + 1:
            # ...and the owner must EXIST. An unrecognised name is unowned, which fails here,
            # rather than somebody else's problem, which fails nowhere (E-03).
            return parts[index] if parts[index] in recognised else None
        return None
    return None


def assert_no_container_is_declared(root: Path) -> None:
    """Raise when a DECLARED path is a readable structured container (r2.21 E6-2).

    Checked by MAGIC, not by suffix: a suffix filter is name-based dispatch, the anti-pattern this
    module condemns for parquet 170 lines above, and a container named `blob.dat` walked straight
    through it.
    """
    containers = []
    for rel in sorted(RENDERED_ARTIFACT_DECLARATIONS):
        target = Path(root) / rel
        if not target.is_file():
            continue
        try:
            head = target.open("rb").read(8)
        except OSError:
            continue
        if head.startswith((_HDF5_MAGIC, _PARQUET_MAGIC)):
            containers.append(rel)
    assert containers == [], (
        f"declared readable container(s): {containers}. A structured container is ALWAYS read, "
        "never declared (r2.21 E6-2) — only rendered artifacts may be declared."
    )


class RecordContentScanError(RuntimeError):
    """The scan could not be PERFORMED — a different answer from "the scan found nothing".

    E-08 was that the report scanned the wrong tree and printed a clean result. The first fix moved
    the root selection and left every other way of getting the root wrong still ending in
    "0 (failing this gate: 0)" and exit 0. Four reviewers reproduced that composite, so "I could not
    determine what to scan" is now an exception with its own exit code rather than an empty list.

    This is E-06's ruling applied to the READ side: a missing declared root fails loudly naming the
    root, because one message for both states sends a legitimate operator looking for the wrong bug.
    """


def _git(args: list[str], *, cwd: Path) -> subprocess.CompletedProcess:
    """Run git so that NOTHING outside `cwd` can steer it.

    Two channels, both demonstrated against the previous version of this module:

    * `GIT_DIR` / `GIT_INDEX_FILE` / `GIT_CONFIG_COUNT` and friends override `cwd` outright, so the
      report listed a DIFFERENT repository's index while printing the root we believed we scanned —
      more misleading than the bug being fixed. Every `GIT_*` name is dropped rather than a curated
      list: new ones are added by git, not by us, and a curated list is what goes stale.
    * `core.fsmonitor` is a repo-local config value git EXECUTES. A planted one in an ancestor
      repository ran as the invoking user during `record-content-report`. The CTO's B2 ruling
      (#44) already requires both that the path be validated as the expected repository and that
      the invocation not honour config from a tree we do not trust; `-c core.fsmonitor=` is the
      second half, and `repo_root()`'s witness check below is the first.
    """
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(
        ["git", "-c", "core.fsmonitor=", *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        # A tracked path need not be valid UTF-8. Strict decoding turned that into a traceback
        # instead of a report, which is a loss of the listing rather than a false clean, but still
        # a way for one filename to silence the whole mechanism.
        errors="surrogateescape",
        check=False,
    )


def _toplevel_of(directory: Path) -> Path | None:
    """The working-tree root git itself reports for `directory`, or None if it is not a checkout."""
    run = _git(["rev-parse", "--show-toplevel"], cwd=directory)
    if run.returncode != 0 or not run.stdout.strip():
        return None
    return Path(run.stdout.strip()).resolve()


def render_path(rel: str) -> str:
    """A tracked path as it may safely be PRINTED.

    `git ls-files -z` emits names unquoted, and newline and ESC are legal in paths. A reviewer
    forged a complete clean report out of one filename: a leading `ESC[2J ESC[H` cleared the
    terminal and the rest of the name drew a fake header and a fake all-clear, with three
    payload-bearing files still listed underneath where no human would ever see them. A newline
    alone splits one real entry into two innocuous-looking rows.

    With no CI consumer of the exit code, THE PRINTED LISTING IS THE CONTROL, so it must not be
    writable by whoever can add a file.
    """
    if rel.isprintable():
        return rel
    return rel.encode("unicode_escape").decode("ascii") + "  [name contains control characters]"


def repo_root() -> Path:
    """The REPOSITORY root — the working tree holding this package (r2.23 E-08).

    Derived by walking up from `source_root()`, never from the cwd or an environment variable: the
    same ambient-state family that produced the $TMPDIR allow-list, the cwd-sensitive receipt
    verification, the cwd-derived monitor identity and the quality-config resolution.

    A worktree's `.git` is a FILE rather than a directory, so the marker is tested for EXISTENCE,
    not `is_dir` — `is_dir()` here is a one-character change that silently reinstates the
    project-root scan in every worktree, which is where this repo's work actually happens.

    The marker alone is not trusted. git is asked to resolve the candidate, so a stray or broken
    `.git` (an aborted `git init`, a copied worktree stub, a submodule conversion — this repo DOES
    use submodules) raises instead of collapsing the scan back to the project root, which is E-08
    verbatim. Nothing is returned on a guess: no repository found is an error, never a fallback to
    `source_root()`, because that fallback IS the narrow root the finding is about.
    """
    start = Path(source_root()).resolve()
    for candidate in (start, *start.parents):
        marker = candidate / ".git"
        if not marker.exists():
            continue
        top = _toplevel_of(candidate)
        if top is None:
            raise RecordContentScanError(
                f"{marker} exists but git cannot open a repository there, so the tree to scan "
                f"cannot be determined. Refusing to report: an unscannable tree must never render "
                f"as a clean one. Repair or remove that marker."
            )
        return top
    raise RecordContentScanError(
        f"no git repository at or above {start}, so there is no tracked-file list to scan. "
        f"Refusing to report a clean result over a tree that was never read (r2.23 E-08). This "
        f"command reports on a CHECKOUT; it cannot speak for an installed copy of the package."
    )


def _tracked_listing(root: Path) -> tuple[list[str], list[str]]:
    """(files, submodule gitlinks) under `root`, or an exception. NEVER an empty list standing in
    for a failure.

    The test-side twin of this function has used `check=True` from the day it was written, beneath
    a test titled "a scan over the wrong or an empty list reports clean". The human-facing copy
    used `check=False` and returned `[]`. That is the E-08 lesson — true of the function as the
    tests call it, false of the command a human runs — one function below the fix for it.

    Both halves come from ONE `git ls-files`, so the files reported and the submodules disclosed as
    unscanned can never be drawn from two different readings of the repository.
    """
    root = Path(root).resolve()
    top = _toplevel_of(root)
    if top is None:
        raise RecordContentScanError(
            f"{root} is not a git checkout, so no tracked-file list could be read. An empty list "
            f"is not an all-clear."
        )
    if top != root:
        raise RecordContentScanError(
            f"asked to scan {root}, but git resolves that directory to the working tree {top}. "
            f"Refusing to report: the tree scanned and the tree named must be the same one."
        )
    run = _git(["ls-files", "-z", "-s"], cwd=root)
    if run.returncode != 0:
        raise RecordContentScanError(
            f"git ls-files failed under {root}: {run.stderr.strip() or 'no diagnostic'}"
        )
    paths: list[str] = []
    gitlinks: list[str] = []
    for record in filter(None, run.stdout.split("\0")):
        meta, rel = record.split("\t", 1)
        (gitlinks if meta.split()[0] == "160000" else paths).append(rel)
    return paths, sorted(gitlinks)


def _tracked_paths_for_report(root: Path) -> list[str]:
    """The files half of the listing. Named for what it used to get wrong."""
    return _tracked_listing(root)[0]


def _refuse_a_scan_that_cannot_see_itself(root: Path, paths: list[str]) -> None:
    """The listing must contain THIS module's own tracked file, and every path must resolve.

    One assertion instead of one per failure mode. It kills, together: a root that is some
    unrelated enclosing repository (a dotfiles `$HOME`, a wrapper monorepo), a root whose index was
    read from elsewhere, a listing emptied by any means, and a checkout too sparse to answer the
    question. The suite has asserted exactly this about ITSELF since it was written; the command
    could not, which is why every wrong root read as clean.
    """
    here = Path(__file__).resolve()
    try:
        witness = here.relative_to(root).as_posix()
    except ValueError:
        raise RecordContentScanError(
            f"{root} does not contain this package ({here}), so it is not the repository this "
            f"report can speak for."
        ) from None
    if witness not in set(paths):
        raise RecordContentScanError(
            f"the listing for {root} does not contain this module's own file ({witness}), so it "
            f"is not a listing of the tree this package lives in. Refusing to report."
        )
    unresolvable = [rel for rel in paths if not (root / rel).is_file()]
    if unresolvable:
        raise RecordContentScanError(
            f"{len(unresolvable)} tracked path(s) under {root} do not resolve to a file, so they "
            f"would be skipped unread (e.g. {unresolvable[:3]}). A partially-materialised checkout "
            f"cannot produce an all-clear."
        )


def render_undeclared_report() -> tuple[str, int]:
    """The report a HUMAN reads, and the exit code this project's gate would produce.

    "Listing that reaches no one is functionally a silent skip" (CTO, §6 boundary) — a report only
    ever asserted on inside tests is the declare-and-skip problem wearing a different coat.

    It takes NO argument. The defect was a caller passing the wrong root, and a `root=None`
    parameter removes the caller's obligation to choose without removing its ability to choose
    wrongly. Narrowed scans are `_render_for_root`, whose underscore says that a narrowed scan is
    not a supported product behaviour.
    """
    return _render_for_root(repo_root())


def _render_for_root(root: Path) -> tuple[str, int]:
    root = Path(root).resolve()
    paths, submodules = _tracked_listing(root)
    _refuse_a_scan_that_cannot_see_itself(root, paths)
    report = undeclared_report(root, paths)
    failing = set(failing_undeclared(root, paths))

    # The root and the denominator go on the header, printed unconditionally. Naming the root only
    # in the all-clear branch left the harder falsehood undetectable: a wrong-but-nonempty root
    # prints a plausible list with no root stated anywhere, and a count with no base reads the same
    # whether 4,000 files were scanned or none. The PACKAGE is named too: which tree gets audited
    # follows the copy of chipsim that was imported, so two worktrees of one repo can each report
    # on the other's tree without a word.
    lines = [
        (
            f"undeclared undecodable files: {len(report)} (failing this gate: {len(failing)}) "
            f"— scanned {len(paths)} tracked files under {root}"
        ),
        f"  (scan run from package {Path(__file__).resolve()})",
    ]
    for rel, owner in report:
        mark = "FAILS HERE" if rel in failing else "listed"
        lines.append(f"  {render_path(rel)}  owner={owner or '<unowned>'}  [{mark}]")
    if not report:
        lines.append("  (none)")
    if submodules:
        lines.append(
            f"  {len(submodules)} submodule(s) NOT scanned (another repository, not files here): "
            f"{', '.join(render_path(rel) for rel in submodules)}"
        )
    # E-03, stated where it is read rather than only in the plan: `owner=` names who SHOULD care,
    # not who is enforcing. Saying "listed" to a human 23 times, with an owner beside it, reads as
    # "filed with the team who will fix it" — and no other project implements this check.
    lines.append(
        "  exit 2 when a file owned by this project, or owned by none, is undeclared. Files listed "
        "against another project fail NO gate today: no other project implements this check, so "
        "`owner=` names who should care, not who is enforcing (E-03)."
    )
    return "\n".join(lines), (2 if failing else 0)


def undeclared_report(root: Path, paths) -> list[tuple[str, str | None]]:
    """(path, owning project) for every undeclared undecodable file, repo-wide (r2.22, E6-1b).

    The LISTING is never scoped — "listing is what may never be skipped; failing is what is
    scoped" — so another team's artifacts stay visible and countable here even though they do not
    fail this gate.
    """
    # The registry is built from the SAME listing the report is rendered from, so an owner cannot
    # be recognised on the strength of a file that this scan never saw.
    recognised = recognised_owners(paths)
    return sorted((rel, path_owner(rel, recognised)) for rel in undecodable_unallowed(root, paths))


def failing_undeclared(root: Path, paths) -> list[str]:
    """The subset of the report that fails THIS project's gate: files this project owns, plus
    every file no project owns.

    Measured before this scoping existed: of 24 declared paths, 0 belonged to this project, and
    removing them as E6-1 required made this module's live test fail on 24 files owned by two
    other teams — inverting the coupling instead of removing it.
    """
    return [
        rel
        for rel, owner in undeclared_report(root, paths)
        if owner is None or owner == THIS_PROJECT
    ]


def undecodable_unallowed(root: Path, paths) -> list[str]:
    """Tracked paths the scan cannot read AND which are not declared in `RENDERED_ARTIFACT_DECLARATIONS`.

    A skipped file is an UNCHECKED file: "no hits" from a file the scan never read is the
    false-clean this project keeps rediscovering. Reporting them is what makes the scan's silence
    mean something.

    Dispatch payloads are skipped — they are waived by ruling (#122 §3) and never scanned either
    way, so reporting them would be unactionable noise. The LEDGER pair is NOT skipped: its content
    IS still read (`ledger_tuple_hits`), so its readability is exactly what this check is for. The
    exclusions exist for accession CONTENT, not for readability.
    """
    unreadable: list[str] = []
    for rel in paths:
        if _is_dispatch_message(root, rel) or rel in DRUGBANK_ID_EXCLUDED_FILES:
            continue
        if rel in RENDERED_ARTIFACT_DECLARATIONS:
            continue
        target = Path(root) / rel
        if not target.is_file():
            continue
        if not _is_readable(target):
            unreadable.append(rel)
    return sorted(unreadable)


def real_accession_hits(root: Path, paths) -> list[tuple[str, str]]:
    """(path, first real accession) for every tracked file outside the ruled exclusions that
    carries a real DrugBank ID. `root` is the REPOSITORY root and `paths` are repo-relative
    (CTO #122 §5); the old project-rooted scan never saw `workstreams/` or `.claude/`.

    Parquet is scanned as frame batches PLUS its footer metadata. A file that cannot be read at all
    is skipped HERE and reported by `undecodable_unallowed`, which fails unless the file is
    declared — so a skip is always visible somewhere (QG §5 E-3).

    `RENDERED_ARTIFACT_DECLARATIONS` is deliberately NOT consulted here: it declares that a file cannot be READ,
    never that its content is exempt. A declared path whose bytes turn out to be readable text is
    still scanned and still reported.

    **WHICH HALF THIS ENFORCES (r2.21, E6-5).** This scan enforces the ACCESSION half of the
    principal's invariant. A structure paired with a NAME and no accession is invisible to it BY
    DESIGN, not by oversight: names are an unbounded vocabulary and there is no detector for them.
    The name half is enforced elsewhere — by the r2.20 writer allow-list, which stops a
    name-bearing payload reaching a tracked path in the first place. Neither mechanism claims the
    other's coverage, because an overclaim about what a guard sees is worse than the gap it hides.
    """
    hits: list[tuple[str, str]] = []
    for rel in paths:
        if is_accession_excluded(rel):
            continue
        target = Path(root) / rel
        if not target.is_file():
            continue
        chunks = _scan_chunks(target)
        if chunks is None:
            continue
        for chunk in chunks:
            found = REAL_ACCESSION_RE.search(chunk)
            if found:
                hits.append((rel, found.group(0)))
                break
    return hits


#: A structure identifier: a full InChI, or an InChIKey. A key beside an accession is as
#: much an association as the full string — it identifies the same molecule.
_STRUCTURE_RE = re.compile(r"InChI=1S?/\S+|\b[A-Z]{14}-[A-Z]{10}-[A-Z]\b")

#: How far apart, in lines, an accession and a structure may sit and still be one
#: association. Two lines each way: a comment that names an accession on one line and gives
#: "its full string" on the next is the case this exists for.
_TUPLE_WINDOW = 2


def accession_structure_tuples(
    text: str, window: int = _TUPLE_WINDOW
) -> list[tuple[int, str, str]]:
    """(1-based line of the accession, accession, structure) for every real accession that
    sits within `window` lines of a structure identifier.

    This is the ASSOCIATION half of the record-content invariant (CTO #120 §1): an accession
    alone is identification, a structure alone is a public identifier, and the two together
    are DrugBank's row. A plain "no structure in this file" rule would be wrong — a file can
    legitimately hold a structure that belongs to no accession.
    """
    lines = text.splitlines()
    structures = [
        (i, m.group(0)) for i, line in enumerate(lines) for m in _STRUCTURE_RE.finditer(line)
    ]
    found: list[tuple[int, str, str]] = []
    seen: set[tuple[int, str]] = set()
    for i, line in enumerate(lines):
        for match in REAL_ACCESSION_RE.finditer(line):
            near = [s for j, s in structures if abs(j - i) <= window]
            if near and (i, match.group(0)) not in seen:
                seen.add((i, match.group(0)))
                found.append((i + 1, match.group(0), near[0]))
    return found


def ledger_tuple_hits(root: Path) -> list[tuple[str, int, str]]:
    """(repo-relative path, line, accession) for every accession/structure association in
    the sanctioned exclusion ledger (#120 §4: keep the accessions, drop the structures)."""
    hits: list[tuple[str, int, str]] = []
    for rel in sorted(DRUGBANK_ID_LEDGER):
        target = Path(root) / rel
        if not target.is_file():
            continue
        for line, accession, _ in accession_structure_tuples(target.read_text(encoding="utf-8")):
            hits.append((rel, line, accession))
    return hits


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
#:
#: *** PLAN DEVIATION, flagged for re-sign. ***
#: build-plan.md:450 and every fixture say `Homo sapiens`. The audited 2015
#: snapshot this study PINS says `Human` — 16,299 rows, and zero saying
#: `Homo sapiens`. So the loader as specified returns an empty frame on the only
#: data the study is allowed to use.
#:
#: Both labels are accepted, rather than swapping one for the other, because the
#: fixtures are legitimately `Homo sapiens` and silently preferring either
#: vocabulary would leave the next reader unable to tell which the code trusts.
#: The floor guard below caught this exactly as its author predicted in the
#: comment naming this precise drift — the guard worked; the fixture was wrong.
HUMAN_ORGANISM_LABELS = frozenset({"Homo sapiens", "Human"})

#: The canonical label, retained for messages and for callers that assert on one
#: spelling. NOT the filter — see above.
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

    observed = sorted(frame["organism"].dropna().unique())
    frame = frame[frame["organism"].isin(HUMAN_ORGANISM_LABELS)].reset_index(drop=True)

    # The floor mirrors load_compounds. Without it an organism-label drift
    # ("Human" vs "Homo sapiens") silently yields ZERO edges, every compound then
    # labels 'unknown', and that is indistinguishable from a real absence of
    # evidence. An almost-empty frame passes every column assertion.
    if len(frame) < min_rows:
        raise ValueError(
            f"parsed only {len(frame)} human protein edges from {path}, below the floor "
            f"of {min_rows}. The filter accepts {sorted(HUMAN_ORGANISM_LABELS)!r}; the "
            f"file's organism column actually contains {observed[:8]!r}"
            f"{' ...' if len(observed) > 8 else ''}. "
            "Naming the OBSERVED values rather than only the expected one: the first "
            "time this fired, the message sent the reader looking for a filter bug "
            "when the answer was a vocabulary difference visible in one column."
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
#: sorted on it and every downstream task indexes on it. `stereo_is_relative`
#: (CTO #122 §0) follows it: `write_compounds` persists ONLY these columns, so a flag
#: absent from this tuple would be silently dropped here and never reach the
#: T10/T13/T15 joins or the T18 roster that must honour it.
PERSISTED_COMPOUND_COLUMNS = (
    "canonical_inchikey",
    "stereo_is_relative",
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
    # r2.20: the WORST payload in the project — accession, name, InChI and InChIKey on ONE
    # ROW, the complete record. Until r2.20 this validated its columns and never its
    # destination, and `chipsim write --out <any path>` reached it with no validation at all;
    # writing into configs/ was measured at §5. The CLI inherits this refusal rather than
    # adding its own, because two checks drift and the second becomes the one people trust.
    refuse_unless_declared_output_root(out)

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
    """Deprecated entrypoint — delegates to the journalled pipeline.

    This module used to run `fetch_snapshot` directly, which meant
    `python -m chipsim.ingest.drugbank_snapshot` executed an ETL stage with **no
    run journal at all**: no config snapshot, no resolved package versions, no git
    state, and not even an UNRECORDED marker. An unjournalled fetch is
    indistinguishable on disk from a journalled one, which defeats S12's whole
    purpose — the A&D replay test cannot be run against an artifact whose inputs
    were never recorded.

    The docstring also claimed this was "Named in the T16 workflow export"; it was
    not. Every node in `orchestration/n8n/etl_drugbank.json` names
    `python -m chipsim.pipeline <stage>`, so the workflow already used the
    journalled path and this was a bypass with no remaining caller.

    Kept as a delegating shim rather than deleted so an operator with the old
    command in their shell history gets a journalled run instead of a silent
    bypass.
    """
    import argparse

    from chipsim.pipeline import main as pipeline_main

    ap = argparse.ArgumentParser(prog="python -m chipsim.ingest.drugbank_snapshot")
    ap.add_argument("--dest", required=True, type=Path)
    ap.add_argument(
        "--commit",
        required=True,
        help="40-hex source_commit from data/raw/drugbank/provenance.yaml (pinned by H in T2)",
    )
    ns = ap.parse_args(argv)
    print(
        "note: delegating to `python -m chipsim.pipeline fetch` so the run is journalled",
        file=sys.stderr,
    )
    return pipeline_main(["fetch", "--dest", str(ns.dest), "--commit", ns.commit])


if __name__ == "__main__":
    raise SystemExit(_main())
