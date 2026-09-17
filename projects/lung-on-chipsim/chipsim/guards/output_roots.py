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


def declared_output_roots() -> tuple[Path, ...]:
    """The resolved roots, including the test tmp root."""
    project = Path(source_root())
    roots = [(project / rel).resolve() for rel in DECLARED_OUTPUT_ROOTS]
    roots.append(Path(tempfile.gettempdir()).resolve())
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
