"""Reading bytes, within bounds: can this file be decoded, and what is it?

Extracted from `chipsim.guards.record_content` at r2.27 (E-18). This is not guard POLICY — it makes
no decision about what is permitted. It answers one mechanical question, "what do these bytes say",
and it answers it under explicit ceilings, because a guard that OOMs produces no verdict at all,
which is the same false clean in a new costume.

Both halves of the record-content invariant consume it: the READ side asks whether a tracked file can
be decoded, and the DrugBank accession scan asks what a decodable file contains. Before this move the
ingest module imported three PRIVATE names from the guard to get at it, re-coupling exactly what the
E6-6 extraction had separated — so the names it needs are public here.

Every bound in this module was set by a measurement, not a guess, and the measurements are recorded
beside them: a 30 KiB dictionary-encoded parquet that expanded to 186.9 MiB as one string, a 206 KB
compressed dataset that reached 200 MB, and an h5ad whose `repr` elided all but six of ~41,000
identifiers.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


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


# --- Public names ------------------------------------------------------------------------------
# The guard and the ingest module both need these. They were private, and `ingest` imported them
# through the underscore anyway, which is the coupling this move exists to remove.

sha256_of = _sha256
decode_text = _decode_text
scan_chunks = _scan_chunks
is_readable = _is_readable
container_magic = _container_magic
