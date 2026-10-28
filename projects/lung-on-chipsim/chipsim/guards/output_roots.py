"""Record-bearing writers may only write into declared UNTRACKED roots — build-plan r2.20.

The invariant is *not written to a tracked path*, so the rule names where writing IS allowed.
r2.19 named the forbidden directory instead, and the §5 reviewers executed three bypasses of it:

  - `CONFIGS/` — on this project's own case-insensitive volume that IS `configs/`, and the
    name-bearing worksheet landed in the real tracked directory;
  - a symlinked `configs` directory, whose component `resolve()` erased before the check saw it;
  - check-one-object-write-another: the check resolved, the write used the literal path, and
    `os.replace` swapped a destination symlink for a real file inside the tracked directory.

It was also too broad, refusing every write under any `configs` ancestor — including the recovery
path the error message recommended. A deny-list can only enumerate the attacks someone thought of.

**WHICH HALF THIS ENFORCES (r2.21, E6-5).** This allow-list enforces the NAME half of the
principal's invariant: it stops a payload carrying a compound NAME beside a structure — or an
accession, name and structure on one row — from reaching a tracked path at all. It does not scan
content and makes no claim about accessions already in the tree; that is the repo-wide scan's half.
Stating the split is the point: a mechanism that implies it covers both is worse than one whose gap
is written down.

**Case (r2.20 says "case-insensitively"), and why this is NOT a lowercase comparison.** For an
ALLOW-list, case-insensitive string matching is the PERMISSIVE direction — the exact opposite of
the deny-list it replaces. `DATA/INTERIM` must be allowed when the filesystem says it IS the
declared directory, and refused when it is a different directory that merely spells alike. So
containment is decided by DIRECTORY IDENTITY (`os.path.samestat` on the nearest existing ancestor),
never by folding case in a string.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from chipsim.journal import source_root

#: Untracked roots a record-bearing payload may be written into, relative to the project root,
#: plus the test tmp root (r2.20). `data/raw/` is NOT here: it holds the pinned snapshot and is
#: DVC-tracked, so it is not an output destination.
DECLARED_OUTPUT_ROOTS = ("data/interim", "data/processed")

#: Functions whose payload can carry DrugBank record content. Each MUST route its destination
#: through `refuse_unless_declared_output_root`, and a registry test asserts both that they do and
#: that no other frame writer has quietly appeared (r2.20).
RECORD_BEARING_WRITERS = (
    "adjudication.write_adjudication_worksheet",
    "drugbank_snapshot.write_compounds",
)


class OutputRootError(RuntimeError):
    """A record-bearing writer was pointed at a destination outside the declared roots."""


class NoWorkTreeError(OutputRootError):
    """No git work tree could be established, so no record-bearing write is permitted.

    REFUSES rather than falling back to the package tree (approvals row 67). The guard's safe
    direction is refuse-when-unestablished — the same rule row 39 applied when unknown-format and
    unparseable became NOT compliant — and r2.34 forbids one function answering "where is the work
    tree" and "may I write here" with opposite safe directions. A non-editable wheel install has no
    legitimate record-bearing write to perform, so refusing costs nothing real; and E-07's complaint
    is that the roots ANCHOR to the installed package tree, which refusing satisfies.

    A subclass of `OutputRootError` so every existing caller still catches it, and separately named
    so "I cannot establish the tracked unit" is distinguishable from "that destination is outside
    the roots" — two different remedies.
    """


#: Names that ARE tracked inside the otherwise-untracked roots, because `.gitignore` re-includes
#: them (`!data/**/*.dvc`, `!data/**/.gitkeep`, `!data/processed/*.sha256`). The roots are
#: "untracked" BY DIRECTORY; the ignore file makes that false BY SUFFIX, and writing the
#: name-bearing worksheet to `data/processed/pgp_adjudication.sha256` was ACCEPTED — no symlink, no
#: env var, no race, just a filename in the directory where `.sha256` is this project's own sidecar
#: convention.
_TRACKED_BY_NEGATION = (".dvc", ".sha256")
_TRACKED_BY_NEGATION_NAMES = (".gitkeep",)


def _work_tree_root(start: Path) -> Path | None:
    """The git work-tree root at or above `start`, by PURE PATH WALK (approvals row 67).

    NO SUBPROCESS, and that is a constraint rather than a style preference. The 2026-09-02 decision
    rejected shelling out to git at runtime because a planted repository ran arbitrary commands
    three times in the gate, and `journal.source_root`'s docstring records that git state is no
    longer captured at all (CTO #44). A git-invoking anchor would reinstall that
    arbitrary-execution sink INSIDE the security guard that exists to stop record leakage.

    `.git` is accepted as a DIRECTORY or a FILE: it is a file in a linked worktree and in a
    submodule, and this project is developed in worktrees, so treating only the directory case as
    valid would make the guard refuse every write in the layout it is actually used in.

    Returns None when no work tree can be established; the caller refuses rather than guessing.
    """
    for candidate in (start, *start.parents):
        try:
            marker = candidate / ".git"
            if marker.is_dir() or marker.is_file():
                return candidate
        except OSError:
            continue
    return None


def declared_output_roots() -> tuple[Path, ...]:
    """The resolved untracked roots.

    The system temp directory is NOT a root. It used to be, via `tempfile.gettempdir()`, i.e.
    `$TMPDIR` — so pointing that at the project made the ENTIRE TRACKED TREE a declared output
    root, and writing accession+name+structure into `configs/` was accepted. A CI runner that
    clones into `$TMPDIR` hit it with no attacker involved. `journal.source_root()`'s own docstring
    refuses exactly this shape: "an audit trail whose default location can be redirected by an
    environment variable is one an operator cannot reason about."

    The temp root survives ONLY as a test-time grant, and only when it is nowhere near the
    project: under pytest, and refused outright if it contains (or is contained by) the project
    root, which is precisely the TMPDIR=<project> attack.
    """
    project = Path(source_root()).resolve()
    work_tree = _work_tree_root(project)
    if work_tree is None:
        raise NoWorkTreeError(
            f"no git work tree found at or above {project} — refusing every record-bearing write "
            "rather than falling back to the installed package tree (approvals row 67). The "
            "tracked unit IS the work tree; without it this guard cannot tell a tracked "
            "destination from an untracked one, and an unestablished answer is not permission."
        )

    roots = [(project / rel).resolve() for rel in DECLARED_OUTPUT_ROOTS]

    if os.environ.get("PYTEST_CURRENT_TEST"):
        try:
            tmp = Path(tempfile.gettempdir()).resolve()
        except OSError:
            return tuple(roots)
        # OVERLAP IS TESTED AGAINST THE WORK TREE, NOT THE PROJECT DIRECTORY (approvals row 67).
        # It used to compare against `project` (= the chipsim package's parent), so a temp root
        # pointed at a TRACKED SIBLING of the project — `workstreams/`, `docs/` — was neither an
        # ancestor nor a descendant of it and passed. Measured: PYTEST_CURRENT_TEST set plus
        # TMPDIR at a tracked sibling and the guard ACCEPTED a write there. The invariant is
        # "never a TRACKED path", and the tracked unit is the work tree.
        inside_work_tree = tmp == work_tree or work_tree in tmp.parents or tmp in work_tree.parents
        if not inside_work_tree:
            roots.append(tmp)
    return tuple(roots)


def _nearest_existing(path: Path) -> Path | None:
    for candidate in (path, *path.parents):
        try:
            if candidate.exists():
                return candidate
        except OSError:
            return None
    return None


def _is_within(candidate: Path, root: Path) -> bool:
    """Is `candidate` inside `root`, by DIRECTORY IDENTITY rather than by string comparison?

    The nearest existing ancestor is compared with `os.path.samestat`, which answers "the same
    directory" on any filesystem: it accepts `DATA/INTERIM` on a case-insensitive volume because
    it IS the declared directory, and rejects it on a case-sensitive one because it is not. A
    string comparison would have to choose between those, and either choice is wrong somewhere.
    """
    anchor = _nearest_existing(candidate)
    if anchor is None:
        return False
    try:
        root_stat = root.stat()
    except OSError:
        return False
    for node in (anchor, *anchor.parents):
        try:
            if os.path.samestat(node.stat(), root_stat):
                return True
        except OSError:
            continue
    return False


def refuse_unless_declared_output_root(out: Path) -> None:
    """Raise unless `out` is inside a declared untracked root (r2.20).

    Refuses a symlinked destination or any symlinked ANCESTOR: the check and the write must mean
    the same object, and `os.replace` replaces a link itself rather than following it.
    """
    literal = Path(out)

    if literal.is_symlink():
        raise OutputRootError(
            f"refusing to write record-bearing output to {out}: the destination is a symlink, and "
            "writing would replace the link itself rather than follow it."
        )
    for parent in literal.parents:
        if parent.is_symlink():
            raise OutputRootError(
                f"refusing to write record-bearing output to {out}: its ancestor {parent} is a "
                "symlink, so the path the check sees is not the path the write reaches."
            )

    try:
        stat = literal.lstat()
    except OSError:
        stat = None
    if stat is not None and stat.st_nlink > 1:
        # Symlinks were refused and HARD links were not: `os.link(configs/victim, data/interim/x)`
        # then a legitimate write overwrote the TRACKED file IN PLACE with the complete record.
        # No symlink anywhere, so every link check above missed it.
        raise OutputRootError(
            f"refusing to write record-bearing output to {out}: it is a hard link "
            f"({stat.st_nlink} names), so writing it would also write whatever else points at "
            "that inode — which may be a tracked file."
        )

    if literal.suffix in _TRACKED_BY_NEGATION or literal.name in _TRACKED_BY_NEGATION_NAMES:
        raise OutputRootError(
            f"refusing to write record-bearing output to {out}: `{literal.name}` is TRACKED even "
            "inside an untracked root, because .gitignore re-includes it "
            f"({', '.join((*_TRACKED_BY_NEGATION, *_TRACKED_BY_NEGATION_NAMES))}). The roots are "
            "untracked by DIRECTORY; this name is tracked by SUFFIX."
        )

    try:
        resolved = literal.resolve()
    except (OSError, RuntimeError) as exc:
        raise OutputRootError(f"refusing to write to {out}: unresolvable path ({exc}).") from exc

    roots = declared_output_roots()
    for root in roots:
        if _is_within(literal, root) and _is_within(resolved, root):
            return

    raise OutputRootError(
        f"refusing to write record-bearing output to {out}: it is not inside a declared untracked "
        f"root. Allowed: {', '.join(DECLARED_OUTPUT_ROOTS)} (plus the test tmp root). This payload "
        "can carry DrugBank record content — a name beside a structure key, or an accession, name "
        "and structure on one row — and the invariant is that such content is never written to a "
        "tracked path. Publish the human-facing file with export_tracked_adjudication() instead, "
        "which projects to the five tracked columns."
    )
