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
import os
from pathlib import Path


def link_bytes(path: Path) -> bytes | None:
    """A symlink's OWN bytes: the target path, which is exactly what git stores as its blob.

    `open()` follows the link, so every reader here would otherwise be reading the TARGET —
    content the index does not carry, and for a dangling link, nothing at all (§12.8).

    WORKTREE MODE ONLY, NOW — and the distinction is worth stating because the r2.32 ruling expected
    this to disappear entirely. In STAGED mode it does: `materialise_blobs` writes a symlink's blob
    as ordinary content, so the staged path never meets a link and needs no link-aware reader, which
    a test asserts. In WORKTREE mode the scan meets a real symlink on disk, and removing this was
    measured to report a dangling link as UNREADABLE — a wrong reason that then invites a
    declaration. So it is scoped rather than deleted, and the deviation was reported with the
    measurement rather than half-performed in silence.
    """
    if not path.is_symlink():
        return None
    return os.readlink(path).encode("utf-8", "surrogateescape")


def entry_exists(path: Path) -> bool:
    """Is there an ENTRY here — a regular file OR a symlink, dangling or not?

    `Path.is_file()` follows the link, so a dangling tracked symlink answered False and was skipped
    by the accession scan, skipped by the readability check, and reported as "tracked but not
    present on disk" — three wrong answers to a question about an entry that is genuinely there and
    that a commit genuinely carries (§12.8).
    """
    return path.is_symlink() or path.is_file()


def _sha256(path: Path) -> str:
    own = link_bytes(path)
    if own is not None:
        # The digest of a symlink is the digest of its TARGET STRING. Hashing the target would pin
        # a file that is not in the index, and would raise outright on a dangling link.
        return hashlib.sha256(own).hexdigest()
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

#: AGGREGATE ceiling across ONE container, and the reason it exists (r2.28 §11 QG): the per-dataset
#: bound was applied N times with no cap on N, and `_scan_chunks` did `list(...)` over the chunk
#: generator, so every batch was held at once. `_PARQUET_BATCH_ROWS` therefore bounded the pandas
#: conversion peak and NOTHING ELSE — measured, a 4,140-byte parquet yielded 11 chunks totalling
#: 20,588,497 bytes, ~4,974x the on-disk size, held simultaneously. Exceeding this is a REPORTED
#: refusal, not a crash: a guard that OOMs produces no verdict at all, which is a false clean in a
#: new costume.
_MAX_CONTAINER_BYTES = 192 * 1024 * 1024

#: How many elements of a variable-length dataset to materialise at a time. `node.nbytes` is
#: `size * dtype.itemsize`, and `np.dtype("O").itemsize` is 8 — a POINTER width — so a vlen-string
#: dataset reports 8 bytes per element however long the strings are. Measured: 1,000 x 1 KiB
#: strings report 8,000 bytes and materialise 1,024,000, a 128x understatement, so the 64 MiB
#: ceiling admitted ~8.6 GB. Those are exactly the datasets (h5ad obs/var) this reader exists to
#: read, so the bound has to be taken on MATERIALISED bytes, in slices, rather than on `nbytes`.
_VLEN_SLICE_ELEMENTS = 4096


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

#: Verdict cache: both callers walk the whole tracked tree, so an uncached parquet was parsed and
#: stringified TWICE per suite run.
#:
#: KEYED ON MORE THAN (path, mtime, size) — that triple kept a STALE verdict across a same-size
#: rewrite that preserves mtime, which is not exotic: `cp -p`, `tar -x`, `rsync -t`, a `git
#: checkout` of a same-size blob, or any `os.utime` all produce it. The dangerous direction is a
#: stale UNREADABLE, because a file that has since become readable would be cleared and then
#: skipped, so its content is never scanned.
#:
#: WHAT ACTUALLY CARRIES THAT IS `st_ctime_ns`, and the rest is DEFENCE IN DEPTH — stated that way
#: because the stronger version was measured and did not hold. `st_ctime_ns` moves on any inode
#: change and `os.utime` cannot set it, so on a modern filesystem it alone separates every case I
#: could construct: neutralising `st_dev`, `st_ino`, `st_mtime_ns` or `st_size` individually
#: changes no reachable outcome. They earn their place only where `ctime` granularity is COARSE
#: (HFS+, exFAT, some NFS/SMB mounts), where two rewrites can land inside one granule.
#:
#: The earlier comment here claimed `st_ino`/`st_dev` "distinguish a replaced file from an edited
#: one". They would, if `st_ctime_ns` did not already — so the claim was true of the mechanism and
#: false about what it contributes, which is the kind of sentence this module keeps having to
#: correct (§12.12).
_READABILITY_CACHE: dict[tuple[str, int, int, int, int, int], bool] = {}


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

    def nbytes_of(node) -> int:
        return int(getattr(node, "nbytes", 0) or 0)

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

        # BYTE-WIDTH INTEGER DATASETS ARE READ AS BYTES (§12.9). They were skipped with every other
        # numeric dtype, under a comment reasoning that "a 14.7M-element expression matrix cannot
        # carry a compound name" — true of expression matrices, false of uint8. Measured: a record
        # written as `np.frombuffer(record.encode(), dtype=np.uint8)` was invisible while
        # `_is_readable` returned True, so the container was certified as FULLY READ and needed no
        # declaration. A claim about one dataset SHAPE was justifying a rule about all dtypes.
        #
        # Deliberately NOT every numeric dtype: a matrix of doubles genuinely cannot carry text, and
        # reading one would cost the bound this module exists to keep. A buffer of encoded text is
        # one byte wide, and that is what is read.
        byte_buffer = dtype.kind in {"u", "i"} and dtype.itemsize == 1
        if not readable and not byte_buffer:
            return

        if byte_buffer:
            if nbytes_of(node) > _MAX_DATASET_BYTES:
                raise _UnreadableContainer(
                    f"{name} is {nbytes_of(node)} bytes of byte-width data, above the scan bound"
                )
            try:
                raw = bytes(memoryview(node[()]).cast("B"))
            except Exception as exc:
                raise _UnreadableContainer(f"{name} could not be read: {exc}") from exc
            text = _decode_text(raw)
            if text is not None:
                parts.append(text)
            return

        nbytes = getattr(node, "nbytes", 0) or 0
        if dtype.kind == "O":
            # `nbytes` is a POINTER count here, not a byte count — see _VLEN_SLICE_ELEMENTS. Read
            # in slices and bound what actually materialises.
            parts.append(_read_vlen_in_slices(name, node))
            return
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

    def _read_vlen_in_slices(name, node) -> str:
        """Materialise a variable-length dataset a slice at a time, against a real byte budget."""
        try:
            count = int(getattr(node, "shape", (0,))[0]) if getattr(node, "shape", ()) else 0
        except (TypeError, IndexError):
            count = 0
        if count == 0:
            try:
                return _stringify(node[()])
            except Exception as exc:
                raise _UnreadableContainer(f"{name} could not be read: {exc}") from exc

        pieces: list[str] = []
        used = 0
        for start in range(0, count, _VLEN_SLICE_ELEMENTS):
            try:
                block = node[start : start + _VLEN_SLICE_ELEMENTS]
            except Exception as exc:
                raise _UnreadableContainer(f"{name} could not be read: {exc}") from exc
            text = _stringify(block)
            used += len(text)
            if used > _MAX_DATASET_BYTES:
                raise _UnreadableContainer(
                    f"{name} materialises more than {_MAX_DATASET_BYTES} bytes of "
                    f"variable-length data, above the scan bound"
                )
            pieces.append(text)
        return "\n".join(pieces)

    def refuse_links(group, prefix: str, seen: set) -> None:
        """Refuse a link ANYWHERE in the graph, not only among the root group's members.

        The original loop was `for name in handle:`, which iterates the ROOT GROUP ONLY, while
        `visititems` silently skips links at every depth. The identical external link was therefore
        refused at the top level and invisible one group down — measured:

            link at TOP level    -> chunks=None      readable=False
            link NESTED in /uns  -> chunks=['uns']   readable=True

        The second case is a FALSE CLEAN: the container counted as READ, was never listed as
        undecodable, and yielded no accession hits, while part of its graph was never visited. The
        comment this replaces stated that exact hazard and then guarded one level (r2.27 §11 QG).

        `seen` holds object ids: HDF5 permits cyclic HARD links, so a naive walk can recurse
        forever on a container an attacker chooses.
        """
        for key in group:
            path = f"{prefix}{key}"
            raw = group.get(key, getlink=True)
            if isinstance(raw, (_HDF5_READER.SoftLink, _HDF5_READER.ExternalLink)):
                raise _UnreadableContainer(f"{path} is a link this scan does not follow")
            try:
                child = group[key]
            except (KeyError, OSError) as exc:
                # A dangling link resolves to nothing. Unreadable, not absent: the same direction
                # as every other refusal here.
                raise _UnreadableContainer(f"{path} could not be resolved: {exc}") from exc
            if isinstance(child, _HDF5_READER.Group):
                marker = child.id.__hash__()
                if marker in seen:
                    continue
                seen.add(marker)
                refuse_links(child, f"{path}/", seen)

    with _HDF5_READER.File(target, "r") as handle:
        for key, value in handle.attrs.items():
            parts.append(f"{key}={value!r}")
        refuse_links(handle, "", set())
        handle.visititems(visit)
        # The file must stay open while the parts are yielded, so they are produced inside the
        # `with` and handed on below rather than being read lazily from a closed handle.

    # YIELDED INCREMENTALLY (§12.12). This used to accumulate every dataset and every attribute
    # into `parts` and yield ONCE, so `_collect_bounded` — which meters chunk by chunk — saw a
    # single chunk and could only raise AFTER the whole expansion was already resident, twice over
    # because of the join. Measured by a reviewer: a 3.4 MB container drove 1,574 MB peak RSS,
    # ~455x its size on disk, growing linearly in dataset count with no cap on the count.
    #
    # `datasets_seen` was incremented and never read: the "per-dataset bound applied N times with
    # no cap on N" that `_MAX_CONTAINER_BYTES` says it fixed had been fixed on the PARQUET path
    # only. A guard that OOMs produces no verdict at all.
    if not any(part.strip() for part in parts):
        raise _UnreadableContainer("the container yielded no scannable content")
    yield from parts


def _collect_bounded(chunks, what: str) -> list[str]:
    """Consume a chunk generator against an AGGREGATE byte budget.

    The `list(...)` this replaces was not gratuitous — it forces errors at CALL time so
    `_scan_chunks` can classify them, which a lazy generator would defer to the consumer. But it
    also held every batch at once, so `_PARQUET_BATCH_ROWS` bounded the per-batch conversion peak
    and nothing else. Keeping the eager consumption and adding a running total gets both: errors
    still surface where they can be classified, and the total is bounded.

    Exceeding the budget is `_UnreadableContainer` — REPORTED, never clean, and never answerable
    with a declaration (E6-2). A guard that OOMs gives no verdict at all.
    """
    collected: list[str] = []
    used = 0
    for chunk in chunks:
        used += len(chunk)
        if used > _MAX_CONTAINER_BYTES:
            raise _UnreadableContainer(
                f"{what} expands beyond {_MAX_CONTAINER_BYTES} bytes of scannable text, above the "
                f"container bound"
            )
        collected.append(chunk)
    return collected


def _scan_chunks(target: Path):
    """Chunks of scannable text for one file, or None when nothing can be read from it.

    None means REPORTABLE — `undecodable_unallowed` turns it into a failure unless the path is
    declared. It never means "clean".
    """
    own = link_bytes(target)
    if own is not None:
        # A SYMLINK IS NOT ITS TARGET. Its bytes are the target path, and those are what a commit
        # carries — so those are what the scan reads (§12.8). Following it meant an accession in a
        # link target was committed and never seen, and a dangling link read as "unreadable",
        # which is a wrong reason that invites a declaration.
        text = _decode_text(own)
        return None if text is None else [text]

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
            return _collect_bounded(_hdf5_chunks(target), "the HDF5 container")
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
            return _collect_bounded(_parquet_chunks(target), "the parquet")
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
        # `lstat`, NOT `stat`: `stat` FOLLOWS a symlink, so a dangling one raised OSError and the
        # link was reported unreadable — a wrong reason that invites a declaration. The cache key
        # should describe the ENTRY, which is what the index holds, not whatever it points at.
        # Identical to `stat` for a regular file (§12.8).
        stat = target.lstat()
        key = (
            str(target),
            stat.st_dev,
            stat.st_ino,
            stat.st_mtime_ns,
            stat.st_ctime_ns,
            stat.st_size,
        )
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
# The two `ingest` actually reads. It imported them through the underscore before the E-18 move,
# which is the coupling the move exists to remove.
#
# `decode_text`, `is_readable` and `container_magic` were exported beside them and read by nobody.
# The comment here used to say "the guard and the ingest module both need these", which was true of
# two of the five — prose asserting a property nothing checks (rule 13). The guard imports the
# underscore names directly: it is the module this one was split out of, not an outside consumer.

sha256_of = _sha256
scan_chunks = _scan_chunks
