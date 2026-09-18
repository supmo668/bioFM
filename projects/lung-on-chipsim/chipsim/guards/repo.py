"""Repository topology: where the repository is, and what it tracks.

Extracted from `chipsim.guards.record_content` at r2.27 (E-18). Nothing here decides what is
PERMITTED — that is the guard's question. This module answers the one it has to ask first, and every
answer in it was a false-clean at some point:

  * `repo_root` walks up from the package rather than from the cwd, because the report once ran at
    the PROJECT root and printed "0 — every tracked file was read" while 23 tracked files elsewhere
    had never been read (r2.23 E-08). A worktree's `.git` is a FILE, so the marker is tested for
    EXISTENCE, not `is_dir` — `is_dir` there silently reinstates the narrow scan in every worktree.
  * `_git` drops every `GIT_*` variable and disables `core.fsmonitor`, because the environment could
    point the listing at a different repository while the report printed the correct root, and
    because `core.fsmonitor` is configuration the SCANNED repository supplies and git EXECUTES.
  * `_tracked_listing` RAISES rather than returning an empty list: "I could not list the files" must
    never arrive at the same answer as "there are no files".
  * `render_path` escapes unprintable names, because one filename could draw a complete fake clean
    report over the real one.
  * `materialise_blobs` reads BLOB BYTES rather than the working-tree rendering of the index, and
    trusts nothing about what comes back: not that two tracked names are two files (a
    case-insensitive volume made them one and the record in the discarded blob was never scanned),
    not that the bytes are the object requested (`refs/replace/*` substitutes content under the
    requested oid), and not that the repository fits in memory (a guard that OOMs gives no verdict,
    which is a false clean in a new costume).
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import tempfile
import threading
from pathlib import Path

from chipsim.guards.errors import (  # noqa: F401
    DeclarationDataUnusable,
    GuardInvariantViolated,
    RecordContentScanError,
    ScanNotPerformed,
)

# The exception vocabulary is a LEAF (r2.29): it lived here under a rule that was false on the
# facts — this module raises it 5 times against record_content's 24 — and the real reason was
# cycle avoidance. Re-exported so existing importers keep working.
# `render_path` moved to `report` with the rest of presentation; re-exported because callers
# reach it here and ruff deletes what it cannot see a use for.
from chipsim.guards.report import render_path
from chipsim.journal import source_root


def _git_argv(args: list[str]) -> list[str]:
    """The hardened argv EVERY git invocation in this module uses. ONE definition, deliberately.

    `materialise_blobs` cannot call `_git` — that decodes to text, which is right for paths and
    wrong for blob content — and so it grew its OWN copy of the hardening, in the same change whose
    entire point was that two definitions of one thing drift. A security review named the
    consequence before it happened: a future flag added to `_git` would silently not apply to the
    call that reads repository CONTENT. The bytes/text difference is the only thing that stays
    local now.

    `--no-replace-objects` because `refs/replace/*` re-points an OID at different content and
    `cat-file` honours it, echoing the REQUESTED oid in its header — so the substitution is
    invisible to any check short of hashing the payload (which `materialise_blobs` now also does).
    It has to be an argv flag: the env sanitiser below drops `GIT_NO_REPLACE_OBJECTS` along with
    every other `GIT_*`, so the environment is not a place this can be closed from.
    """
    return ["git", "--no-replace-objects", "-c", "core.fsmonitor=", *args]


def _git_env() -> dict[str, str]:
    """The environment with every `GIT_*` name dropped — see `_git` for why all of them."""
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


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
    return subprocess.run(
        _git_argv(args),
        cwd=cwd,
        env=_git_env(),
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


def _tracked_entries(root: Path) -> list[tuple[str, str, str]]:
    """(mode, oid, path) for every tracked entry, refusing an unmerged index or a non-toplevel root.

    ENUMERATED FROM `git ls-files -s` RATHER THAN FROM `checkout-index` (r2.32 constraint 1). That
    tool skips unmerged entries and still exits 0, so a listing derived from it could not tell "not
    tracked" from "silently not written" — which is exactly how staged mode came to report CLEAN
    over a file it never read. Here the STAGE is visible, so refusing a tree mid-merge is a property
    of the enumeration rather than of a downstream check.
    """
    root = Path(root).resolve()
    top = _toplevel_of(root)
    if top is None:
        raise ScanNotPerformed(
            f"{root} is not a git checkout, so no tracked-file list could be read. An empty list "
            f"is not an all-clear."
        )
    if top != root:
        raise ScanNotPerformed(
            f"asked to scan {root}, but git resolves that directory to the working tree {top}. "
            f"Refusing to report: the tree scanned and the tree named must be the same one."
        )
    run = _git(["ls-files", "-z", "-s"], cwd=root)
    if run.returncode != 0:
        raise ScanNotPerformed(
            f"git ls-files failed under {root}: {run.stderr.strip() or 'no diagnostic'}"
        )
    entries = []
    for record in filter(None, run.stdout.split("\0")):
        # A shape git does not produce today must still arrive as a REFUSAL. Unpacking it raised
        # `ValueError` straight past every caller's `except RecordContentScanError` — the same
        # traceback-instead-of-a-report failure `_git`'s docstring names two functions above.
        try:
            meta, rel = record.split("\t", 1)
            mode, oid, stage = meta.split()
        except ValueError as exc:
            raise ScanNotPerformed(
                f"could not parse a `git ls-files -s` record under {root}: "
                f"{render_path(repr(record))} ({exc})"
            ) from exc
        if stage != "0":
            raise ScanNotPerformed(
                f"{rel} is UNMERGED in the index (stage {stage}). A tree in the middle of a merge "
                f"is not one this report can speak for. Resolve the merge and re-run."
            )
        entries.append((mode, oid, rel))
    return entries


def _object_hasher(root: Path):
    """A constructor for the hash git names objects with in THIS repository, or a refusal.

    Read rather than assumed: a sha256 repository names blobs with 64 hex digits, and a verifier
    hard-coded to sha1 there would reject every object and call it tampering.

    A CONSTRUCTOR rather than a one-shot function, so the payload can be fed through in chunks and
    never has to exist in memory whole. Neither hash is used here for collision resistance: the
    question is only "does this repository call these bytes by this name", and the repository's own
    answer is the one being checked.
    """
    run = _git(["rev-parse", "--show-object-format"], cwd=root)
    fmt = run.stdout.strip() if run.returncode == 0 else ""
    if fmt == "sha1":
        return lambda: hashlib.sha1(usedforsecurity=False)
    if fmt == "sha256":
        return lambda: hashlib.sha256(usedforsecurity=False)
    raise ScanNotPerformed(
        f"{root} reports object format {fmt!r}, which this reader cannot verify blobs against. "
        f"Refusing rather than reading bytes it cannot check."
    )


def _feed_oids(pipe, request: bytes) -> None:
    """Write the request while the main thread drains stdout, so neither waits on the other.

    An `OSError` here means the reader closed the pipe first — it refused something and is already
    raising. Its exception is the one that describes the problem; this one would replace a precise
    diagnosis with `EPIPE`.
    """
    try:
        pipe.write(request)
        pipe.close()
    except OSError:
        pass


def materialise_blobs(root: Path, into: Path) -> Path:
    """Write every tracked entry's BLOB BYTES into `into`, and return it.

    NOT `checkout-index`: that materialises the working-tree RENDERING of the index, applying `eol`
    and `filter` conversions, so the bytes it produces are not the bytes a commit carries. Measured
    from COMMITTED configuration alone — `* text eol=crlf` turns `line one\n` into `line one\r\n`,
    a different sha256 — and with a filter driver, content in the blob can be absent from the
    materialised copy entirely, which passes a commit that carries it.

    `cat-file --batch` is a BYTE STREAM with a `<oid> <type> <size>` header; the size is
    authoritative and nothing is decoded here (r2.32 constraint 3).

    A SYMLINK'S BLOB IS ITS TARGET STRING, so it is written as ordinary content and the staged path
    needs no link-aware reader (constraint 2).

    THREE THINGS THIS FUNCTION NO LONGER TAKES ON TRUST, each of which was a way for the gate to
    report clean over bytes it never read:

    * THE FILESYSTEM'S IDEA OF A DISTINCT NAME. Two tracked paths differing only in case, or only
      in Unicode normalisation, are ONE file on APFS and on NTFS. Reproduced: an index holding
      `Data.csv` (carrying the record) and `data.csv` (a decoy) materialised as a single file
      holding the decoy, and the counter below said 2 of 2. The filesystem's own equivalence is
      what conflates them, so `exists()` — which asks the filesystem — is what detects them.
    * THE BYTES BEING THE ONES ASKED FOR. `refs/replace/*` re-points an OID at other content and
      the response header echoes the REQUESTED oid, so only hashing the payload can tell. The
      argv closes the channel and the hash checks that it stayed closed.
    * THE TREE FITTING IN MEMORY. `capture_output` held every tracked blob at once — measured at
      ~240 MiB on this repository against 25 MiB for the tool it replaced — while `decoding` sets
      three explicit ceilings on the argument that a guard which OOMs produces no verdict, and no
      verdict is a false clean in a new costume. The stream is consumed one blob at a time.
    """
    entries = [(mode, oid, rel) for mode, oid, rel in _tracked_entries(root) if mode != "160000"]
    into.mkdir(parents=True, exist_ok=True)
    if any(into.iterdir()):
        raise GuardInvariantViolated(
            f"{render_path(str(into))} is not empty. The staged tree must start empty or the "
            f"collision refusal below cannot tell a second write from a pre-existing file."
        )
    if not entries:
        return into

    new_hasher = _object_hasher(root)
    request = "".join(f"{oid}\n" for _mode, oid, _rel in entries).encode("ascii")

    with tempfile.TemporaryFile() as diagnostics:
        proc = subprocess.Popen(
            _git_argv(["cat-file", "--batch"]),
            cwd=root,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=diagnostics,
            env=_git_env(),
        )
        feeder = threading.Thread(target=_feed_oids, args=(proc.stdin, request), daemon=True)
        feeder.start()
        try:
            _consume_blobs(proc.stdout, entries, into, new_hasher)
            if proc.stdout.read(1):
                raise ScanNotPerformed(
                    f"git returned more object records than the {len(entries)} requested under "
                    f"{root}. Refusing a stream this reader does not understand."
                )
        finally:
            proc.stdout.close()
            feeder.join(timeout=5)
            if proc.poll() is None:
                proc.kill()
            proc.wait()
        if proc.returncode != 0:
            diagnostics.seek(0)
            detail = diagnostics.read().decode("utf-8", "replace").strip()
            raise ScanNotPerformed(
                f"could not read the staged blobs under {root}: {detail or 'no diagnostic'}"
            )

    # CONSTRAINT 4: the count must keep meaning "files whose bytes were read". This asks the
    # FILESYSTEM how many files exist rather than counting the writes we just made — a counter
    # incremented once per loop iteration could only ever equal the number of iterations, which is
    # why the previous version of this check passed over the collision above while a blob was
    # being lost. Two tracked paths that are one file are visible here and nowhere else.
    materialised = sum(1 for path in into.rglob("*") if path.is_file())
    if materialised != len(entries):
        raise ScanNotPerformed(
            f"materialised {materialised} files for {len(entries)} tracked blobs under {root}"
        )
    return into


#: Blob payloads move through the hasher and the file handle in slices of this size, so the peak
#: cost of the reader is a constant rather than the largest file anyone has committed. Measured:
#: holding each payload whole cost 94.7 MiB on this repository against a 34.5 MiB largest blob,
#: because the hash input was a second copy of it.
_BLOB_CHUNK_BYTES = 1 << 20


def _consume_blobs(stream, entries, into: Path, new_hasher) -> None:
    """Read one `cat-file --batch` record per entry and write its payload. Refuses, never skips."""
    written: dict[str, str] = {}
    into_resolved = into.resolve()
    for _mode, oid, rel in entries:
        header = stream.readline()
        if not header.endswith(b"\n"):
            raise ScanNotPerformed(f"truncated blob stream while reading {render_path(rel)}")
        fields = header.rstrip(b"\n").split()
        if len(fields) != 3 or fields[1] != b"blob":
            raise ScanNotPerformed(
                f"{render_path(rel)}: expected a blob for {oid}, got {header.rstrip()!r}"
            )
        if fields[0] != oid.encode("ascii"):
            raise ScanNotPerformed(
                f"{render_path(rel)}: asked for {oid}, got a record for "
                f"{fields[0].decode('ascii', 'replace')}. The stream and the listing have "
                f"diverged, so no row in this report can be trusted."
            )
        try:
            size = int(fields[2])
        except ValueError as exc:
            raise ScanNotPerformed(
                f"{render_path(rel)}: unreadable object size in {header.rstrip()!r}"
            ) from exc

        target = into / rel
        # NOTHING IS WRITTEN OUTSIDE THE STAGED TREE. git validates index paths and rejected every
        # `..` entry two reviews could construct, so this has no demonstrated bypass today — which
        # is exactly why it is written down rather than left implicit. The tool this replaced
        # enforced path safety in C, and dropping to plain writes moved the whole class onto a
        # git-side invariant, in the component whose CVE history is that invariant failing.
        if not target.resolve().is_relative_to(into_resolved):
            raise ScanNotPerformed(
                f"{render_path(rel)} resolves outside the staged tree. Refusing to write it: a "
                f"tracked path may not name a destination the scan does not own."
            )
        # ASK THE FILESYSTEM, not `resolve()`: on a case-insensitive or normalisation-insensitive
        # volume `Path.resolve()` returns the spelling it was given, so it reports two distinct
        # paths for the one file that is about to be overwritten. `exists()` consults the same
        # equivalence that causes the collision. Checked BEFORE the file is opened, because
        # opening for write is itself the destructive act.
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            collides = target.exists() or target.is_symlink()
        except OSError as exc:
            raise ScanNotPerformed(
                f"could not prepare the staged path for {render_path(rel)}: {exc}"
            ) from exc
        if collides:
            clash = written.get(str(target).casefold(), "an earlier entry")
            raise ScanNotPerformed(
                f"{render_path(rel)} and {render_path(clash)} are DISTINCT tracked paths that "
                f"this filesystem treats as one file. Writing the second would discard the "
                f"first, and the scan would report clean over bytes it never read."
            )

        digest = new_hasher()
        digest.update(b"blob %d\0" % size)
        remaining = size
        try:
            with target.open("wb") as sink:
                while remaining:
                    chunk = stream.read(min(remaining, _BLOB_CHUNK_BYTES))
                    if not chunk:
                        raise ScanNotPerformed(
                            f"truncated blob for {render_path(rel)}: "
                            f"{size - remaining} of {size} bytes"
                        )
                    digest.update(chunk)
                    sink.write(chunk)
                    remaining -= len(chunk)
        except OSError as exc:
            # The tool this replaced turned an unwritable name into `ScanNotPerformed` with a
            # diagnostic; letting `OSError` past here loses the report entirely, because no caller
            # catches it. Measured: a tracked path whose bytes are not valid UTF-8 is refused by
            # APFS with Errno 92, and the gate died with a traceback and exit 1.
            raise ScanNotPerformed(
                f"could not write the staged blob for {render_path(rel)}: {exc}"
            ) from exc

        if stream.read(1) != b"\n":
            raise ScanNotPerformed(
                f"{render_path(rel)}: the object record is not framed as git frames it"
            )

        # THE PAYLOAD IS THE OBJECT IT WAS ASKED FOR — not merely labelled as it. This is the only
        # check that sees through `refs/replace/*`, whose response header carries the REQUESTED
        # oid, and it is also what makes the positional walk above an assertion rather than an
        # assumption: a record consumed at the wrong offset does not hash to the right name.
        actual = digest.hexdigest()
        if actual != oid:
            raise ScanNotPerformed(
                f"{render_path(rel)}: the bytes returned for {oid} name the object {actual}. "
                f"Refusing to scan content this repository does not agree it stores."
            )
        written[str(target).casefold()] = rel


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
            raise ScanNotPerformed(
                f"{marker} exists but git cannot open a repository there, so the tree to scan "
                f"cannot be determined. Refusing to report: an unscannable tree must never render "
                f"as a clean one. Repair or remove that marker."
            )
        return top
    raise ScanNotPerformed(
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
    # DERIVED FROM `_tracked_entries`, which is the ONE enumeration and the ONE unmerged refusal.
    #
    # The r2.32 blob reader needed mode/OID/stage, so `_tracked_entries` was added — and this
    # function briefly kept its own `ls-files` call, its own stage parsing and its own copy of the
    # refusal. Two definitions of "what is tracked here", able to drift, introduced by a fix for a
    # different defect, in a module whose recent history is entirely about two halves disagreeing
    # about what exists. Nothing had drifted yet; that is not the point.
    #
    # The de-duplication that used to live here is gone with it: a tree with stages is REFUSED
    # before anything could be duplicated, so a `seen` set guarding against repeated records would
    # be dead machinery reading as a live guard.
    #
    # The TOPLEVEL WITNESS went the same way, and in the same direction: it used to live here, so
    # `materialise_blobs` — which calls the enumeration directly — inherited nothing from it, and
    # was saved only by this function running afterwards. An invariant one call site away from the
    # thing it protects is an invariant waiting for a second call site.
    paths: list[str] = []
    gitlinks: list[str] = []
    for mode, _oid, rel in _tracked_entries(root):
        (gitlinks if mode == "160000" else paths).append(rel)
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


# --- Public names ------------------------------------------------------------------------------
# Only the names something OUTSIDE this module actually reads. `tracked_listing` and
# `MINIMUM_PLAUSIBLE_TRACKED` were minted in the E-18 split and read by nobody: an alias with no
# reader is an inert mechanism that reads as a supported API, which is the same defect E-19 and
# CODE-4 were about, one layer down. `record_content` imports the underscore names directly because
# it is the module this one was split OUT of, not an outside consumer.

run_git = _git
toplevel_of = _toplevel_of
tracked_paths = _tracked_paths_for_report
