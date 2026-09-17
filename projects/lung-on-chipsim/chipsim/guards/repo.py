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
    run = _git(["ls-files", "-z", "-s"], cwd=root)
    if run.returncode != 0:
        raise ScanNotPerformed(
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


# --- Public names ------------------------------------------------------------------------------
# Only the names something OUTSIDE this module actually reads. `tracked_listing` and
# `MINIMUM_PLAUSIBLE_TRACKED` were minted in the E-18 split and read by nobody: an alias with no
# reader is an inert mechanism that reads as a supported API, which is the same defect E-19 and
# CODE-4 were about, one layer down. `record_content` imports the underscore names directly because
# it is the module this one was split OUT of, not an outside consumer.

run_git = _git
toplevel_of = _toplevel_of
tracked_paths = _tracked_paths_for_report
