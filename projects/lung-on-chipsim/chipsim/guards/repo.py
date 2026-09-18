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
"""

from __future__ import annotations

import os
import subprocess
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
from chipsim.guards.report import render_path  # noqa: F401
from chipsim.journal import source_root


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


def _tracked_entries(root: Path):
    """(mode, oid, path) for every tracked entry, refusing an unmerged index.

    ENUMERATED FROM `git ls-files -s` RATHER THAN FROM `checkout-index` (r2.32 constraint 1). That
    tool skips unmerged entries and still exits 0, so a listing derived from it could not tell "not
    tracked" from "silently not written" — which is exactly how staged mode came to report CLEAN
    over a file it never read. Here the STAGE is visible, so refusing a tree mid-merge is a property
    of the enumeration rather than of a downstream check.
    """
    run = _git(["ls-files", "-z", "-s"], cwd=root)
    if run.returncode != 0:
        raise ScanNotPerformed(
            f"git ls-files failed under {root}: {run.stderr.strip() or 'no diagnostic'}"
        )
    entries = []
    for record in filter(None, run.stdout.split("\0")):
        meta, rel = record.split("\t", 1)
        mode, oid, stage = meta.split()
        if stage != "0":
            raise ScanNotPerformed(
                f"{rel} is UNMERGED in the index (stage {stage}). A tree in the middle of a merge "
                f"is not one this report can speak for. Resolve the merge and re-run."
            )
        entries.append((mode, oid, rel))
    return entries


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
    """
    entries = [(mode, oid, rel) for mode, oid, rel in _tracked_entries(root) if mode != "160000"]
    into.mkdir(parents=True, exist_ok=True)
    if not entries:
        return into

    request = "".join(f"{oid}\n" for _mode, oid, _rel in entries).encode("ascii")
    # THE SAME ENVIRONMENT SANITISATION `_git` APPLIES — every `GIT_*` dropped and `core.fsmonitor`
    # neutralised — because this invocation reads repository content, and a planted config steering
    # it is exactly the channel `_git`'s docstring exists to close. Not routed through `_git`
    # itself because that decodes to text with surrogateescape, which is right for paths and wrong
    # for blob content: this must stay bytes (constraint 3).
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    run = subprocess.run(
        ["git", "-c", "core.fsmonitor=", "cat-file", "--batch"],
        cwd=root,
        input=request,
        capture_output=True,
        env=env,
        check=False,
    )
    if run.returncode != 0:
        raise ScanNotPerformed(
            f"could not read the staged blobs under {root}: "
            f"{run.stderr.decode('utf-8', 'replace').strip() or 'no diagnostic'}"
        )

    stream = run.stdout
    offset = 0
    written = 0
    for _mode, oid, rel in entries:
        newline = stream.find(b"\n", offset)
        if newline < 0:
            raise ScanNotPerformed(f"truncated blob stream while reading {rel}")
        header = stream[offset:newline].split()
        if len(header) != 3 or header[1] != b"blob":
            raise ScanNotPerformed(
                f"{rel}: expected a blob for {oid}, got {stream[offset:newline]!r}"
            )
        size = int(header[2])
        start = newline + 1
        payload = stream[start : start + size]
        if len(payload) != size:
            raise ScanNotPerformed(f"truncated blob for {rel}: {len(payload)} of {size} bytes")
        offset = start + size + 1  # trailing newline git appends after each object

        target = into / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        written += 1

    # CONSTRAINT 4: the count must keep meaning "files whose bytes were read". A mismatch is a
    # refusal, never a silent skip — the defect `checkout-index` had.
    if written != len(entries):
        raise ScanNotPerformed(
            f"materialised {written} of {len(entries)} tracked blobs under {root}"
        )
    return into


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
