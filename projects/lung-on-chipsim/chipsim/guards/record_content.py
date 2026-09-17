"""The record-content guard: what a tracked file may be, and what may excuse it.

Extracted from `chipsim.ingest.drugbank_snapshot` at r2.25 (E6-6). That module is about ingesting a
pinned compound snapshot; this one is about a question with nothing to do with DrugBank — CAN THIS
REPOSITORY'S TRACKED FILES BE READ, who owns them, and which of them are declared. The two had grown
together until the guard was 1200 lines of a 2000-line ingest module.

WHAT THE GUARD KNOWS: containers and their magic, decodability, repository topology, project
ownership, the declaration surface, and the report a human reads.

WHAT IT DOES NOT KNOW, AND MUST NOT: anything about DrugBank. The extraction's one non-mechanical
seam (named in the r2.25 clause) was `undecodable_unallowed` reaching into the DrugBank exclusions.
That is not one question but TWO, and conflating them would be a defect:

  * `readability_waived(root, rel)` — "this file's readability is not this gate's business."
    Dispatch payloads are waived by ruling (#122 §3) and never scanned either way, so reporting them
    would be unactionable noise. It deliberately does NOT cover the exclusion LEDGER: the ledger's
    content IS still read, so its readability is exactly what this check is for.
  * `content_exempt(rel)` — "this path is ALREADY exempt by the content mechanism", so a declaration
    on top would exempt it twice and make it invisible to both halves of the guard. This one DOES
    cover the ledger.

Both default to refusing nothing, so a caller who forgets to pass them gets a NOISIER gate rather
than a quieter one — the only safe direction for a default in a mechanism whose failure mode is a
false clean.
"""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import yaml

from chipsim.journal import source_root


def nothing_is_waived(root: Path, rel: str) -> bool:
    """Default readability waiver: nothing is waived. Fail-closed."""
    return False


def nothing_is_content_exempt(rel: str) -> bool:
    """Default content-exemption predicate: nothing is exempt. Fail-closed."""
    return False


@dataclass(frozen=True)
class ContentPolicy:
    """What the OWNING project waives, injected rather than imported.

    The guard must not know about DrugBank. Both defaults refuse nothing, so a caller who forgets
    to pass a policy gets a noisier gate rather than a quieter one — the only safe direction for a
    default in a mechanism whose failure mode is a false clean.
    """

    #: "This file's readability is not this gate's business." Dispatch payloads are waived by
    #: ruling (#122 §3). NOT the exclusion ledger: its content IS read, so its readability is
    #: exactly what the check is for.
    readability_waived: Callable[[Path, str], bool] = nothing_is_waived
    #: "This path is ALREADY exempt by the content mechanism", so declaring it too would exempt it
    #: twice and make it invisible to both halves of the guard. This one DOES cover the ledger.
    content_exempt: Callable[[str], bool] = nothing_is_content_exempt


DEFAULT_POLICY = ContentPolicy()


#: Any file in a dispatches/ directory, whatever its suffix. The waiver pattern above is `.md`-only
#: by design; THIS one is the never-declarable class. A non-.md payload is exactly what E6-4 keeps
#: failing here, so matching on the waiver's pattern would have exempted the one file the rule is
#: for — `leak.pdf` walked straight through it.
_DISPATCH_DIRECTORY_RE = re.compile(r"^\.claude/usr/(?:[^/]+/)+dispatches/[^/]+$")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


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
        with target.open("rb") as handle:
            head = handle.read(8)
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


def marker_backed_owners(paths) -> frozenset[str]:
    """Projects proved to exist by a TRACKED MARKER alone, independent of any declaration.

    This is the set used to answer "may this path be declared HERE?" — deliberately the WIDER of
    the two, because for the placement rule widening is the safe direction. Answering placement
    with the narrowed set made the registry police itself: delisting a project turned its artifacts
    into "unowned" paths, and unowned paths may legally be declared at the repo root, so one edit to
    one file cleared another team's artifacts with no defect reported.

    The marker is evidence the registry does not control, which is what breaks that circle.
    """
    tracked = set(paths)
    found: set[str] = set()
    for prefix, index, marker in _OWNERSHIP_PREFIXES:
        head = prefix.rstrip("/")
        if index == 0:
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


def recognised_owners(
    root: Path, paths, surface: DeclarationSurface | None = None
) -> frozenset[str]:
    """The projects that DEMONSTRABLY exist.

    TWO independent conditions, and an owner needs BOTH (r2.24 E-11):

    * a tracked MARKER, so the directory alone cannot mint an owner — the attacker's own file had
      to create the directory, which makes its existence worth nothing as evidence; and
    * a place in the DECLARED registry at the repo root, once that registry exists.

    The registry NARROWS, never widens. A marker alone does not mint an owner and neither does a
    declaration alone, so minting one means editing a tracked declaration file AND adding a marker —
    both reviewable. Until the registry exists the marker stands alone, and it is a MITIGATION, not
    proof: it is addable by anyone who adds a `pyproject.toml`, and the report says so.
    """
    found = marker_backed_owners(paths)
    declared = (DeclarationSurface.require(root) if surface is None else surface).registry
    return found if declared is None else found & declared


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


class RecordContentScanError(RuntimeError):
    """The scan could not be PERFORMED — a different answer from "the scan found nothing".

    E-08 was that the report scanned the wrong tree and printed a clean result. The first fix moved
    the root selection and left every other way of getting the root wrong still ending in
    "0 (failing this gate: 0)" and exit 0. Four reviewers reproduced that composite, so "I could not
    determine what to scan" is now an exception with its own exit code rather than an empty list.

    This is E-06's ruling applied to the READ side: a missing declared root fails loudly naming the
    root, because one message for both states sends a legitimate operator looking for the wrong bug.
    """


#: WHERE declarations live. Per-project data following the ingest module's `DRUGBANK_ID_LEDGER`
#: precedent of pointing at `configs/` rather than inlining (r2.21 E6-1) — the precedent stands even
#: though the ledger itself stayed behind in that module at the E6-6 extraction — plus a repo-root
#: surface
#: for paths no project owns (r2.23 E-05). The guard reads the UNION of the two.
#:
#: The placement rule is the whole point of E6-1 and is ENFORCED below, not merely documented: the
#: project file may declare only what THIS project owns, and the repo-root file only what NOBODY
#: owns. 24 paths belonging to other teams were once declared inside this module's source, so
#: another team adding a figure turned this module's gate red and the repair landed in a file they
#: neither own nor can judge.
PROJECT_DECLARATION_FILE = f"projects/{THIS_PROJECT}/configs/record_content_declarations.yaml"
REPO_DECLARATION_FILE = "config/record_content_declarations.yaml"

#: Declaration files are short lists of claims. The bound is what stops an alias-expansion or
#: oversized document from making the gate permanently un-runnable, which is the one denial this
#: mechanism is exposed to.
_MAX_DECLARATION_BYTES = 1 << 20

#: A content pin is exactly 64 lowercase hex characters. Anything else cannot match a sha256 and
#: would sit in the data looking like coverage.
_SHA256_RE = re.compile(r"[0-9a-f]{64}")

#: `why` is required. A declaration is a CLAIM, and "none of these is a DrugBank artifact" in a
#: comment is the thing E6-1 contrasts a checkable claim against.
_DECLARATION_KEYS = frozenset({"path", "sha256", "derived_from", "why"})


def _container_magic(target: Path) -> str | None:
    """ "parquet" / "HDF5" when the file IS a structured container, by MAGIC rather than by suffix.

    A suffix filter is name-based dispatch — the anti-pattern this module condemns for parquet 170
    lines above — and a container named `blob.dat` walks straight through it.
    """
    try:
        with target.open("rb") as handle:
            head = handle.read(8)
    except OSError:
        return None
    if head.startswith(_PARQUET_MAGIC):
        return "parquet"
    if head.startswith(_HDF5_MAGIC):
        return "HDF5"
    return None


def _declaration_document(root: Path, rel: str) -> dict:
    """Parse one declaration file. ABSENT is legitimate and means "nothing declared here"."""
    target = Path(root) / rel
    if not target.is_file():
        return {}
    size = target.stat().st_size
    if size > _MAX_DECLARATION_BYTES:
        # Bounded like every other reader in this guard. `yaml.safe_load` is safe against arbitrary
        # object construction but not against alias expansion or a huge document, and a declaration
        # file nobody can parse is the gate held permanently un-runnable.
        raise RecordContentScanError(
            f"{rel} is {size} bytes, above the {_MAX_DECLARATION_BYTES}-byte bound for declaration "
            f"data. A declaration file is a short list of claims; this is something else."
        )
    try:
        doc = yaml.safe_load(target.read_text(encoding="utf-8"))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        # ValueError covers UnicodeDecodeError, which read_text raises and which is NOT an OSError.
        # One non-UTF-8 byte in a declaration file produced a traceback out of the CLI — exit 1 and
        # no report — from the one command whose contract is that it must never fail silently.
        raise RecordContentScanError(
            f"{rel} could not be read as YAML ({exc}), so the gate cannot tell what is declared. "
            f"Refusing to report: an unreadable declaration file is not an empty one."
        ) from exc
    if doc is None:
        return {}
    if not isinstance(doc, dict):
        raise RecordContentScanError(f"{rel} must be a mapping, got {type(doc).__name__}.")
    # Quoted in the data because tests/test_scaffold.py forbids a bare numeric value anywhere under
    # configs/ — biological numbers are human-owned, and a scanner cannot tell a schema version from
    # a parameter. Checked here so the field is load-bearing: reading a future schema as if it were
    # this one is how a declaration comes to mean something other than what it says.
    version = doc.get("version")
    # `str(version) != "1"` accepted YAML 1.1 integer spellings — 0x1 and 01 both stringify to
    # something a reader would not call version 1. The data files quote it, so require the string.
    if version != "1":
        raise RecordContentScanError(
            f'{rel}: unsupported declaration schema version {version!r} (this gate reads "1"). '
            f"Refusing to interpret it as the schema it is not."
        )
    return doc


def _declaration_entries(root: Path) -> list[tuple[str, dict, str]]:
    """(declared path, entry, which surface declared it), with the SHAPE checked.

    A structurally broken entry raises rather than being skipped: the gate cannot evaluate what it
    cannot parse, and "could not evaluate" must never arrive at the same answer as "nothing to
    declare". That is exit 3, not exit 2 and certainly not a pass.
    """
    return _entries_from(
        {
            PROJECT_DECLARATION_FILE: _declaration_document(root, PROJECT_DECLARATION_FILE),
            REPO_DECLARATION_FILE: _declaration_document(root, REPO_DECLARATION_FILE),
        }
    )


def _entries_from(docs: dict[str, dict]) -> list[tuple[str, dict, str]]:
    """The shape checks, over documents that have already been parsed."""
    entries: list[tuple[str, dict, str]] = []
    seen: dict[str, str] = {}
    for rel, surface in (
        (PROJECT_DECLARATION_FILE, "project"),
        (REPO_DECLARATION_FILE, "repo-root"),
    ):
        doc = docs[rel]
        declared_list = doc.get("declarations") or []
        if not isinstance(declared_list, list):
            raise RecordContentScanError(
                f"{rel}: `declarations` must be a list, got {type(declared_list).__name__}."
            )
        for raw in declared_list:
            if not isinstance(raw, dict):
                raise RecordContentScanError(f"{rel}: every declaration must be a mapping.")
            unknown = set(raw) - _DECLARATION_KEYS
            if unknown:
                raise RecordContentScanError(
                    f"{rel}: unknown declaration key(s) {sorted(map(repr, unknown))}. A key the "
                    f"gate does not "
                    f"understand may be the one a reader believed was doing the work."
                )
            path = raw.get("path")
            if not isinstance(path, str) or not path:
                raise RecordContentScanError(f"{rel}: every declaration needs a `path`.")
            # TYPE before truthiness. `bool(12345)`, `bool(True)` and `bool({"a": 1})` are all
            # true, so a mistyped field passed the exactly-one-claim check below and then crashed on
            # a string operation — a traceback out of the CLI, which tells an operator nothing about
            # which file or which entry to repair. Same defect as the §7 CLI traceback.
            for field, expected in (("sha256", str), ("derived_from", str), ("why", str)):
                value = raw.get(field)
                if value is not None and not isinstance(value, expected):
                    raise RecordContentScanError(
                        f"{rel}: `{path}` has `{field}` of type {type(value).__name__}; it must be "
                        f"a string. YAML supplies whatever was written, and a mistyped field is a "
                        f"claim nobody can evaluate."
                    )
            digest = raw.get("sha256")
            if digest is not None and not _SHA256_RE.fullmatch(digest):
                raise RecordContentScanError(
                    f"{rel}: `{path}` has a `sha256` that is not 64 lowercase hex characters "
                    f"({digest!r}). A pin that cannot match anything would clear nothing while "
                    f"looking like coverage."
                )
            # PRESENCE, not truthiness: `sha256: null` alongside `derived_from` is two claims,
            # and testing bool() silently resolved it to the second one.
            if ("sha256" in raw) == ("derived_from" in raw):
                raise RecordContentScanError(
                    f"{rel}: `{path}` must carry exactly one of `sha256` (pin the content) or "
                    f"`derived_from` (name a tracked source). Neither is a bare path declaration, "
                    f"which is what E6-3 forbids; both at once is a claim nobody can adjudicate."
                )
            if not raw.get("why"):
                raise RecordContentScanError(
                    f"{rel}: `{path}` needs a `why`. A declaration is a claim, and an unexplained "
                    f"one is the comment E6-1 contrasts a checkable claim against."
                )
            if path in seen:
                raise RecordContentScanError(
                    f"`{path}` is declared twice ({seen[path]} and {surface}); which claim governs "
                    f"is not something the gate may pick."
                )
            seen[path] = surface
            entries.append((path, raw, surface))
    return entries


def _under_an_ownership_prefix(rel: str) -> bool:
    """Is this path inside a directory that BELONGS to somebody, registry or no registry?

    `path_owner` answers "which RECOGNISED project owns this", returning None both for a path nobody
    owns and for a path under an UNREGISTERED project name. Those are different facts, and
    conflating them let `projects/ghost-lib/payload.bin` be declared at the repo-root surface
    precisely BECAUSE the registry refused to recognise `ghost-lib`: registering the name made the
    declaration illegal, and not registering it made it legal.
    """
    parts = Path(rel).parts
    return bool(parts) and any(
        parts[0] == prefix.rstrip("/") for prefix, _i, _m in _OWNERSHIP_PREFIXES
    )


def declaration_defects(
    root: Path,
    paths,
    policy: ContentPolicy = DEFAULT_POLICY,
    surface: DeclarationSurface | None = None,
) -> list[tuple[str, str]]:
    """(declared path, what is wrong with the claim) for every entry that does NOT hold.

    These always fail this gate. Both declaration files are OURS — the project file by ownership,
    the repo-root file because an unowned path belongs to nobody — so a defect in either is ours to
    repair, and there is no other gate for it to fall to (E-03).
    """
    tracked = set(paths)
    # TWO owner sets, answering two different questions (DES-1). Placement asks "may this be
    # declared here?" and is judged against the MARKER-BACKED set, which the registry cannot shrink;
    # failure scoping asks "whose gate does this fail?" and uses the narrowed set elsewhere. Using
    # the narrowed set for BOTH let a delisting legalise declaring another team's artifacts.
    placement_owners = marker_backed_owners(paths)
    read = DeclarationSurface.require(root) if surface is None else surface
    defects: list[tuple[str, str]] = []

    for path, entry, where in read.entries:
        owner = path_owner(path, placement_owners)
        if where == "project" and owner != THIS_PROJECT:
            remedy = (
                "Another team's artifact declared here inherits this module's failure mode and "
                "repair path, in a file they neither own nor can judge."
                if owner
                else "An unowned path is declared at the repo-root surface instead (E-05)."
            )
            defects.append(
                (
                    path,
                    f"declared in this project's file, but {owner or 'nobody'} owns it. {remedy}",
                )
            )
        if where == "repo-root" and _under_an_ownership_prefix(path):
            defects.append(
                (
                    path,
                    (
                        f"declared in the repo-root surface, but `{Path(path).parts[0]}/` is an "
                        f"OWNERSHIP PREFIX — the path belongs to a project whether or not that "
                        f"project is in the registry. The repo-root surface is for paths that "
                        f"belong to nobody; delisting an owner must not turn its subtree into one."
                    ),
                )
            )
        if where == "repo-root" and owner is not None:
            defects.append(
                (
                    path,
                    (
                        f"declared in the repo-root surface, but {owner} owns it. The repo-root "
                        f"surface is for paths NOBODY owns; an owned path is declared by its owner."
                    ),
                )
            )
        if path not in tracked:
            defects.append(
                (
                    path,
                    (
                        "declared but not tracked — the file was deleted or renamed and the entry "
                        "stayed behind. A declaration nobody checks reads as coverage and clears "
                        "nothing."
                    ),
                )
            )
            continue

        if _DISPATCH_DIRECTORY_RE.match(path):
            defects.append(
                (
                    path,
                    (
                        "declared, but dispatch payloads are the DOUBLE-EXEMPT path class E6-4 "
                        "closed: `path_owner` returning None for them is what keeps a non-.md "
                        "payload failing here. A declaration on top would make it fail nowhere."
                    ),
                )
            )

        if policy.content_exempt(path):
            defects.append(
                (
                    path,
                    (
                        "declared AND content-excluded. A path may never be exempted twice by two "
                        "different mechanisms: the content scan already skips it, so a declaration "
                        "on top makes it invisible to both halves of the guard — the "
                        "double-exemption shape E6-4 closed for dispatch payloads."
                    ),
                )
            )

        target = Path(root) / path
        if target.is_file():
            head = _container_magic(target)
            if head:
                defects.append(
                    (
                        path,
                        (
                            f"declared, but it is a readable {head} container. A structured container is "
                            f"ALWAYS read, never declared (E6-2) — checked by magic, not by suffix."
                        ),
                    )
                )
                continue

        if target.is_file() and _is_readable(target):
            defects.append(
                (
                    path,
                    (
                        "declared, but the scan CAN read it. A declaration says a file cannot be read; "
                        "declaring a readable file exempts nothing and hides everything."
                    ),
                )
            )
            continue

        if entry.get("sha256"):
            if not target.is_file():
                defects.append((path, "declared with a sha256 but absent from disk."))
                continue
            # The module's own streaming helper, not read_bytes(): every other reader in this
            # guard is bounded, and a declared file is by construction a binary — a pinned PDF or a
            # rendered video is exactly the large-file case.
            actual = _sha256(target)
            if actual != entry["sha256"]:
                defects.append(
                    (
                        path,
                        (
                            f"STALE declaration: pinned {entry['sha256'][:12]}…, file is {actual[:12]}…. "
                            f"Every declared file is a build output, so a path-keyed declaration would have "
                            f"gone on matching this path forever (E6-3)."
                        ),
                    )
                )
            continue

        if not target.is_file():
            defects.append(
                (
                    path,
                    (
                        "claims a tracked source, but the declared file itself is absent from disk, "
                        "so nothing about it has been looked at. `sha256` refuses this case and the "
                        "two forms must agree."
                    ),
                )
            )
            continue

        # WHAT THIS VERIFIES, exactly: that the named source is tracked, readable, owned by the
        # same project, and not itself declared. It does NOT verify that the declared file derives
        # from it — naming an unrelated same-owner file satisfies the check. The derivation is a
        # human claim, and `why` is where it is made; the gate narrows who may make it and keeps the
        # source in scope, which is less than the prose used to imply.
        source = entry["derived_from"]
        if source in {p for p, _e, _s in read.entries}:
            defects.append(
                (
                    path,
                    (
                        f"claims to be derived from `{source}`, which is ITSELF declared. An "
                        f"exemption may not rest on a file this same report may be calling a "
                        f"broken claim in the same run."
                    ),
                )
            )
            continue
        if path_owner(source, placement_owners) != owner:
            defects.append(
                (
                    path,
                    (
                        f"claims to be derived from `{source}`, which belongs to a different owner "
                        f"({path_owner(source, placement_owners) or 'nobody'} vs "
                        f"{owner or 'nobody'}). Any tracked readable file would otherwise satisfy "
                        f"the claim, which puts it back in review — the position `sha256` exists to "
                        f"escape."
                    ),
                )
            )
            continue
        if source not in tracked:
            defects.append(
                (
                    path,
                    (
                        f"claims to be derived from `{source}`, which is not tracked. The claim is only "
                        f"self-maintaining while the source it names is in scope."
                    ),
                )
            )
            continue
        source_target = Path(root) / source
        if not source_target.is_file() or not _is_readable(source_target):
            defects.append(
                (
                    path,
                    (
                        f"claims to be derived from `{source}`, which the scan cannot read — so the source "
                        f"is not in scope and the claim rests on something nobody has checked either."
                    ),
                )
            )
    return defects


@dataclass(frozen=True)
class DeclarationSurface:
    """Everything the declaration data says, read ONCE and then immutable (r2.25 E-14).

    The cheap complaint was nineteen parses per report and a pinned artifact hashed three times. The
    real one: nothing was snapshotted, so an edit landing mid-report produced A SINGLE REPORT THAT
    DISAGREED WITH ITSELF — rows marked FAILS HERE under an owner whose own footer said it fails
    nobody, with an exit code that depended on interleaving. Reading once makes that impossible
    rather than unlikely.

    `structural_error` is E-13. A declaration file that cannot be parsed is NOT "could not scan at
    all": the scan works, only the exemption data is unreadable. So nothing is declared — the
    fail-closed direction, more files fail and never fewer — the listing is still rendered, and the
    reason travels WITH the surface, to be reported beside the listing instead of replacing it.
    """

    entries: tuple[tuple[str, dict, str], ...] = ()
    registry: frozenset[str] | None = None
    structural_error: str | None = None

    @classmethod
    def require(cls, root: Path) -> DeclarationSurface:
        """RAISES on MALFORMED declaration data. For a caller asking one rule a direct question.

        It tolerates an ABSENT file — that rule belongs to the report, which is the surface an
        operator reads, and has always been checked there rather than in the validator.
        """
        docs = {
            rel: _declaration_document(root, rel)
            for rel in (PROJECT_DECLARATION_FILE, REPO_DECLARATION_FILE)
        }
        return cls(
            entries=tuple(_entries_from(docs)),
            registry=_registry_from(docs[REPO_DECLARATION_FILE]),
            structural_error=None,
        )

    @classmethod
    def read(cls, root: Path) -> DeclarationSurface:
        """NEVER raises; carries the reason instead, so the listing can still be rendered (E-13).

        Used only by the report. Nothing is declared when the data is broken — the fail-closed
        direction, more files fail and never fewer.
        """
        try:
            refuse_an_absent_declaration_surface(root)
            return cls.require(root)
        except RecordContentScanError as exc:
            return cls(entries=(), registry=None, structural_error=str(exc))


def valid_declarations(
    root: Path,
    paths,
    policy: ContentPolicy = DEFAULT_POLICY,
    surface: DeclarationSurface | None = None,
) -> frozenset[str]:
    """The declared paths whose claim actually HOLDS. Only these clear a file."""
    read = DeclarationSurface.require(root) if surface is None else surface
    broken = {path for path, _ in declaration_defects(root, paths, policy, read)}
    return frozenset(path for path, _, _ in read.entries if path not in broken)


def declared_owner_registry(root: Path) -> frozenset[str] | None:
    """The owner names the repo-root surface declares, or None when no registry exists yet."""
    return _registry_from(_declaration_document(root, REPO_DECLARATION_FILE))


def _registry_from(doc: dict) -> frozenset[str] | None:
    owners = doc.get("owners")
    if owners is None:
        return None
    if not isinstance(owners, list) or not all(isinstance(o, str) and o for o in owners):
        raise RecordContentScanError(
            f"{REPO_DECLARATION_FILE}: `owners` must be a list of project names."
        )
    return frozenset(owners)


def assert_no_container_is_declared(root: Path) -> None:
    """Raise when a DECLARED path is a readable structured container (r2.21 E6-2).

    Checked by MAGIC, not by suffix: a suffix filter is name-based dispatch, the anti-pattern this
    module condemns for parquet 170 lines above, and a container named `blob.dat` walked straight
    through it. Reads the declaration DATA — before r2.24 it read a constant that was permanently
    empty, so it could not have failed.
    """
    containers = []
    for rel, _entry, _surface in _declaration_entries(root):
        target = Path(root) / rel
        if not target.is_file():
            continue
        if _container_magic(target):
            containers.append(rel)
    assert containers == [], (
        f"declared readable container(s): {containers}. A structured container is ALWAYS read, "
        "never declared (r2.21 E6-2) — only rendered artifacts may be declared."
    )


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


#: A tracked count below this is not a repository this report can speak for — it is a listing that
#: went wrong. Crude on purpose, and the WEAKER half of the pair: the witness below proves the
#: listing is of THIS tree, while the floor catches a listing of the right tree that came back
#: truncated, which the witness cannot see. The suite's own anti-vacuity test has used the same
#: floor since it was written (r2.24 E-08b).
_MINIMUM_PLAUSIBLE_TRACKED = 100


def _refuse_a_scan_that_cannot_see_itself(root: Path, paths: list[str]) -> None:
    """The listing must be a listing of THIS tree, and a plausible one. Fatal — exit 3.

    Kills together: a root that is some unrelated enclosing repository (a dotfiles `$HOME`, a
    wrapper monorepo), a root whose index was read from elsewhere, and a listing emptied or
    truncated by any means. The suite has asserted exactly this about ITSELF since it was written;
    the command could not, which is why every wrong root read as clean.

    A path that is tracked but ABSENT FROM DISK is deliberately NOT refused here — see
    `unresolvable_tracked`. Making that fatal (as I first shipped it) makes the report unrunnable in
    a legitimate sparse or partial checkout, and a control nobody can run is not a control
    (r2.24 E-10).
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
    if len(paths) < _MINIMUM_PLAUSIBLE_TRACKED:
        raise RecordContentScanError(
            f"only {len(paths)} tracked path(s) under {root}, which is below the floor of "
            f"{_MINIMUM_PLAUSIBLE_TRACKED}: this is a listing that went wrong, not a repository "
            f"with nothing in it. Refusing to report."
        )


def refuse_an_absent_declaration_surface(root: Path) -> None:
    """Both declaration files must EXIST, parse, and declare a schema this gate reads.

    An absent file used to read as an empty one, which silently reverted the owner registry to the
    pre-r2.24 marker-only mitigation — with the same exit code as a healthy run. This module already
    says "an unreadable declaration file is not an empty one"; an ABSENT one is not either.

    Without this, "the surface exists" is precisely what "declared" was before the surface was
    built: a state the code can describe and cannot verify. `declarations: []` is a claim somebody
    made on purpose and the gate checked; a missing file is a scan that could not be performed.
    """
    for rel in (PROJECT_DECLARATION_FILE, REPO_DECLARATION_FILE):
        if not (Path(root) / rel).is_file():
            raise RecordContentScanError(
                f"the declaration surface {rel} is ABSENT. An empty `declarations: []` is a claim "
                f"made on purpose; a missing file is a scan that could not be performed. Refusing "
                f"to report."
            )
        # Existence only. The PARSE happens once, in DeclarationSurface.require, rather than here
        # and again there — the surface is supposed to be read once (E-14).


def unresolvable_tracked(root: Path, paths) -> list[str]:
    """Tracked paths that are not present on disk, so the scan cannot read them.

    Sparse checkout, `skip-worktree`, or a partial clone that never fetched the blob. THE PAYLOAD IS
    STILL IN THE REPOSITORY — which is the thing the invariant protects — while the worktree simply
    does not have it, so `undecodable_unallowed` walked straight past it with
    `if not target.is_file(): continue` and the report said nothing at all.

    Counted and reported ALWAYS; scoping the count would repeat E-08. The FAILURE is scoped by
    ownership, which is E6-1b exactly (r2.24 E-10).
    """
    return sorted(rel for rel in paths if not (Path(root) / rel).is_file())


def render_undeclared_report(policy: ContentPolicy = DEFAULT_POLICY) -> tuple[str, int]:
    """The report a HUMAN reads, and the exit code this project's gate would produce.

    "Listing that reaches no one is functionally a silent skip" (CTO, §6 boundary) — a report only
    ever asserted on inside tests is the declare-and-skip problem wearing a different coat.

    It takes NO argument. The defect was a caller passing the wrong root, and a `root=None`
    parameter removes the caller's obligation to choose without removing its ability to choose
    wrongly. Narrowed scans are `_render_for_root`, whose underscore says that a narrowed scan is
    not a supported product behaviour.
    """
    return _render_for_root(repo_root(), policy)


def _render_for_root(root: Path, policy: ContentPolicy = DEFAULT_POLICY) -> tuple[str, int]:
    root = Path(root).resolve()
    paths, submodules = _tracked_listing(root)
    _refuse_a_scan_that_cannot_see_itself(root, paths)

    # ONE read, threaded through everything below (r2.25 E-14). Before this the two YAML files were
    # parsed nineteen times per report and nothing was snapshotted, so an edit landing mid-report
    # produced a report that disagreed with itself.
    surface = DeclarationSurface.read(root)
    report = undeclared_report(root, paths, policy, surface)
    failing = set(failing_undeclared(root, paths, policy, surface))

    # Tracked but absent from disk. Listed always; failing only where we own it, or where nobody
    # does — the same predicate failing_undeclared uses, because "unowned fails here" is
    # load-bearing for E6-4 and a missing file is no different in that respect.
    recognised = recognised_owners(root, paths, surface)
    missing = [(rel, path_owner(rel, recognised)) for rel in unresolvable_tracked(root, paths)]
    failing |= {rel for rel, owner in missing if owner is None or owner == THIS_PROJECT}

    # A declaration whose claim does not hold fails this gate outright. Both surfaces are ours —
    # the project file by ownership, the repo-root file because an unowned path belongs to nobody —
    # so there is no other gate for a broken claim to fall to (E-03).
    entries = surface.entries
    defects = declaration_defects(root, paths, policy, surface)
    # Kept in `failing` so a broken claim marks its row, but COUNTED separately below: mixing two
    # categories into one number made the summary wrong exactly where a reader checks it first.
    failing |= {path for path, _ in defects}
    undecodable_failing = {rel for rel, _owner in report if rel in failing} | {
        rel for rel, _owner in missing if rel in failing
    }

    # The root and the denominator go on the header, printed unconditionally. Naming the root only
    # in the all-clear branch left the harder falsehood undetectable: a wrong-but-nonempty root
    # prints a plausible list with no root stated anywhere, and a count with no base reads the same
    # whether 4,000 files were scanned or none. The PACKAGE is named too: which tree gets audited
    # follows the copy of chipsim that was imported, so two worktrees of one repo can each report
    # on the other's tree without a word.
    lines = [
        (
            f"undeclared undecodable files: {len(report)} "
            f"(failing this gate: {len(undecodable_failing)}) "
            f"— scanned {len(paths)} tracked files under {root}, "
            f"{len(missing)} not present on disk"
        ),
        (
            # The failure this clause is about is a mechanism that is easy to MISS because nothing
            # exercises it: the removal half shipped and the READ half did not, and the scoping kept
            # the suite green without it. An empty declaration set is the correct state today, and
            # it has to be a NUMBER rather than something implied by silence.
            f"  declarations read: {len(entries)} "
            f"({sum(1 for _, _, s in entries if s == 'project')} from {PROJECT_DECLARATION_FILE}, "
            f"{sum(1 for _, _, s in entries if s == 'repo-root')} from {REPO_DECLARATION_FILE}), "
            f"{len(defects)} whose claim does not hold"
        ),
        f"  (scan run from package {Path(__file__).resolve()})",
    ]
    if surface.structural_error:
        lines.append(
            "  DECLARATION DATA COULD NOT BE READ, so NOTHING IS DECLARED — every undecodable file "
            "is reported below as if it had never been declared, which is the fail-closed "
            "direction: more files fail, never fewer. This is exit 2, not exit 3: the scan worked, "
            "only the exemption data is unreadable."
        )
        lines.append(f"    {surface.structural_error}")
    for rel, owner in report:
        mark = "FAILS HERE" if rel in failing else "listed"
        lines.append(f"  {render_path(rel)}  owner={owner or '<unowned>'}  [{mark}]")
    if not report:
        lines.append("  (none)")
    if defects:
        lines.append("  DECLARATIONS WHOSE CLAIM DOES NOT HOLD — these clear nothing:")
        for path, why in defects:
            lines.append(f"    {render_path(path)}  [FAILS HERE]  {why}")
    if missing:
        lines.append(
            "  tracked but NOT PRESENT ON DISK, so the scan could not read them (sparse or partial "
            "checkout). The payload is still in the repository:"
        )
        for rel, owner in missing:
            mark = "FAILS HERE" if rel in failing else "listed"
            lines.append(f"    {render_path(rel)}  owner={owner or '<unowned>'}  [{mark}]")
    if submodules:
        lines.append(
            f"  {len(submodules)} submodule(s) NOT scanned (another repository, not files here): "
            f"{', '.join(render_path(rel) for rel in submodules)}"
        )
    # E-03, stated where it is read rather than only in the plan: `owner=` names who SHOULD care,
    # not who is enforcing. Saying "listed" to a human 23 times, with an owner beside it, reads as
    # "filed with the team who will fix it" — and no other project implements this check.
    if surface.registry is None:
        lines.append(
            f"  owner registry: MARKER-BACKED ONLY — no `owners` list in {REPO_DECLARATION_FILE}. "
            "A tracked marker is louder than `mkdir` but is addable by anyone who adds a "
            "pyproject.toml, so this is a MITIGATION, not proof (E-11)."
        )
    else:
        lines.append(
            f"  owner registry: DECLARED in {REPO_DECLARATION_FILE}, intersected with the tracked "
            "marker — an owner needs both, so neither a declaration nor a file alone mints one."
        )
    lines.append(
        "  exit 2 when a file owned by this project, or owned by none, is undeclared. Files listed "
        "against another project fail NO gate today: no other project implements this check, so "
        "`owner=` names who should care, not who is enforcing (E-03)."
    )
    return "\n".join(lines), (2 if failing or surface.structural_error else 0)


def undeclared_report(
    root: Path,
    paths,
    policy: ContentPolicy = DEFAULT_POLICY,
    surface: DeclarationSurface | None = None,
) -> list[tuple[str, str | None]]:
    """(path, owning project) for every undeclared undecodable file, repo-wide (r2.22, E6-1b).

    The LISTING is never scoped — "listing is what may never be skipped; failing is what is
    scoped" — so another team's artifacts stay visible and countable here even though they do not
    fail this gate.
    """
    # The registry is built from the SAME listing the report is rendered from, so an owner cannot
    # be recognised on the strength of a file that this scan never saw.
    read = DeclarationSurface.require(root) if surface is None else surface
    recognised = recognised_owners(root, paths, read)
    return sorted(
        (rel, path_owner(rel, recognised))
        for rel in undecodable_unallowed(root, paths, policy, read)
    )


def failing_undeclared(
    root: Path,
    paths,
    policy: ContentPolicy = DEFAULT_POLICY,
    surface: DeclarationSurface | None = None,
) -> list[str]:
    """The subset of the report that fails THIS project's gate: files this project owns, plus
    every file no project owns.

    Measured before this scoping existed: of 24 declared paths, 0 belonged to this project, and
    removing them as E6-1 required made this module's live test fail on 24 files owned by two
    other teams — inverting the coupling instead of removing it.
    """
    return [
        rel
        for rel, owner in undeclared_report(root, paths, policy, surface)
        if owner is None or owner == THIS_PROJECT
    ]


def undecodable_unallowed(
    root: Path,
    paths,
    policy: ContentPolicy = DEFAULT_POLICY,
    surface: DeclarationSurface | None = None,
) -> list[str]:
    """Tracked paths the scan cannot read AND whose declaration does not hold (r2.24 E-02).

    A skipped file is an UNCHECKED file: "no hits" from a file the scan never read is the
    false-clean this project keeps rediscovering. Reporting them is what makes the scan's silence
    mean something.

    Dispatch payloads are skipped — they are waived by ruling (#122 §3) and never scanned either
    way, so reporting them would be unactionable noise. The LEDGER pair is NOT skipped: its content
    IS still read (`ledger_tuple_hits`), so its readability is exactly what this check is for. The
    exclusions exist for accession CONTENT, not for readability.
    """
    declared = valid_declarations(root, paths, policy, surface)
    unreadable: list[str] = []
    for rel in paths:
        if policy.readability_waived(root, rel):
            continue
        if rel in declared:
            continue
        target = Path(root) / rel
        if not target.is_file():
            # Not silent any more: unresolvable_tracked() counts these and the report gives them
            # their own section. Skipping HERE is right — there is nothing to read — but the skip
            # was the whole defect for as long as nothing said it had happened (r2.24 E-10).
            continue
        if not _is_readable(target):
            unreadable.append(rel)
    return sorted(unreadable)
