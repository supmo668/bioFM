"""The registry test `guards/output_roots.py` said existed and did not (approvals row 65).

The guard's own docstring claimed "a registry test asserts both that they do and that no other
frame writer has quietly appeared (r2.20)". No such test existed anywhere in the repository: a
quality gate measured ZERO references to `output_roots`, `OutputRootError`,
`DECLARED_OUTPUT_ROOTS` or `RECORD_BEARING_WRITERS` under `tests/`, and inserting `return` as the
first statement of `refuse_unless_declared_output_root` left the whole suite byte-identical to
baseline. 187 lines of guard over the project's top invariant, asserting nothing — and a registered
writer (`drugbank_snapshot.write_compounds`) that never called it, so
`chipsim write --out configs/x.parquet` wrote accession + name + InChI + InChIKey into the tracked
tree.

Two properties, because the claim had two halves:

1. **Every registered writer REFUSES a tracked destination.** Called per writer, so a failure names
   which one regressed rather than reporting "some writer".
2. **No frame writer has quietly appeared OUTSIDE the registry.** Discovered from the source by AST,
   not from a hand-kept list — a hand-kept list of hand-kept lists is how the original claim came to
   be false.

NO IDENTIFIER APPEARS IN THIS FILE. The payloads are shaped like records (the declared column
names) and filled with `FIXTURE`-prefixed values, because what is under test is the DESTINATION
check, not the content.
"""

from __future__ import annotations

import ast
import os
from pathlib import Path

import pandas as pd
import pytest

from chipsim.guards.output_roots import (
    DECLARED_OUTPUT_ROOTS,
    RECORD_BEARING_WRITERS,
    OutputRootError,
    declared_output_roots,
    refuse_unless_declared_output_root,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE = PROJECT_ROOT / "chipsim"

#: Trees whose frame writers can carry record content. `audit/` and `eval/` write derived
#: statistics, not records, and are excluded deliberately rather than by omission.
_RECORD_BEARING_TREES = ("harmonize", "ingest")

_FRAME_WRITE_METHODS = ("to_parquet", "to_csv", "to_feather", "to_json", "to_excel")


def _module_label(path: Path) -> str:
    """`module.function`, matching RECORD_BEARING_WRITERS' own convention.

    The registry writes `adjudication.write_adjudication_worksheet`, not
    `harmonize.adjudication.…`. A label that does not match the registry's spelling would report
    every writer as unregistered — a check that fails for the wrong reason is as useless as one
    that passes for the wrong reason.
    """
    return path.stem


def _frame_writers_in_source() -> set[str]:
    """Every module-level function that calls a DataFrame write method, found by AST.

    Derived from the source rather than listed, so a new writer cannot opt out by not being
    added to a constant — which is exactly how the registry's claim became false.
    """
    found: set[str] = set()
    files = [p for tree in _RECORD_BEARING_TREES for p in (PACKAGE / tree).glob("*.py")]
    assert files, f"no source files found under {_RECORD_BEARING_TREES} — discovery is broken"
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for inner in ast.walk(node):
                if (
                    isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Attribute)
                    and inner.func.attr in _FRAME_WRITE_METHODS
                ):
                    found.add(f"{_module_label(path)}.{node.name}")
                    break
    return found


def _record_shaped_frame() -> pd.DataFrame:
    from chipsim.ingest.drugbank_snapshot import PERSISTED_COMPOUND_COLUMNS

    return pd.DataFrame([{c: f"FIXTURE-{c}" for c in PERSISTED_COMPOUND_COLUMNS}])


def _call_writer(name: str, out: Path) -> None:
    """Invoke a registered writer by its registry name, with a record-shaped payload."""
    if name == "drugbank_snapshot.write_compounds":
        from chipsim.ingest.drugbank_snapshot import write_compounds

        write_compounds(_record_shaped_frame(), out)
        return
    if name == "adjudication.write_adjudication_worksheet":
        from chipsim.harmonize.adjudication import write_adjudication_worksheet

        labels = pd.Series(["unknown"], index=["FIXTURE-KEY-0"], name="adjudicated_label")
        labels.index.name = "canonical_inchikey"
        compounds = pd.DataFrame(
            {
                "canonical_inchikey": ["FIXTURE-KEY-0"],
                "name": ["FIXTURE-NAME-0"],
                "stereo_is_relative": [False],
            }
        )
        write_adjudication_worksheet(labels, compounds, out)
        return
    raise AssertionError(
        f"{name} is in RECORD_BEARING_WRITERS but this test does not know how to call it. "
        "Add it here — an unexercised registry entry is the defect this file exists to stop."
    )


def test_the_registry_is_not_empty():
    """Anti-vacuity. Every assertion below iterates the registry; an empty one asserts nothing."""
    assert RECORD_BEARING_WRITERS, "RECORD_BEARING_WRITERS is empty — every test here is vacuous"
    assert len(set(RECORD_BEARING_WRITERS)) == len(RECORD_BEARING_WRITERS), "duplicate entry"


@pytest.mark.parametrize("writer", RECORD_BEARING_WRITERS)
def test_every_registered_writer_refuses_a_tracked_destination(writer, tmp_path):
    """The registry's first claim: each named writer DOES route through the guard.

    `configs/` is the destination the measured incident used. Parametrized so a regression names
    the writer; a single loop would report only that one of them failed.
    """
    target = PROJECT_ROOT / "configs" / "FIXTURE_registry_probe.parquet"
    sidecar = target.with_suffix(".sha256")
    assert not target.exists(), "probe destination already exists — refusing to risk a real file"

    # CLEANS UP IN `finally`, because when the guard is BROKEN this test performs the very write
    # the guard exists to refuse — into the tracked tree. Measured: the first run of this file with
    # `write_compounds` un-wired left configs/FIXTURE_registry_probe.{parquet,sha256} behind, and
    # the pre-check above then refused to run at all. A test of a refusal must not depend on the
    # refusal working in order to leave the tree clean.
    try:
        with pytest.raises(OutputRootError):
            _call_writer(writer, target)
        assert not target.exists(), f"{writer} created {target} before refusing"
        assert not sidecar.exists(), f"{writer} wrote a sidecar before refusing"
    finally:
        for residue in (target, sidecar):
            residue.unlink(missing_ok=True)


@pytest.mark.parametrize("writer", RECORD_BEARING_WRITERS)
def test_every_registered_writer_accepts_a_declared_root(writer, tmp_path, monkeypatch):
    """The mirror. Without it, a writer that refuses EVERYTHING would pass the test above."""
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "registry-test")
    out = tmp_path / "FIXTURE_registry_probe.parquet"
    _call_writer(writer, out)
    assert out.exists(), f"{writer} refused a declared root: {out}"


def test_no_frame_writer_has_quietly_appeared_outside_the_registry():
    """The registry's second claim, and the half that cannot be kept by hand.

    Discovered by AST from the source. A new `to_parquet`/`to_csv` writer under a record-bearing
    tree must either route through the guard (and be registered) or be excluded here on purpose.
    """
    discovered = _frame_writers_in_source()
    assert discovered, "AST discovery found no frame writers at all — the walk is broken"
    unregistered = discovered - set(RECORD_BEARING_WRITERS) - _EXEMPT_WRITERS
    assert not unregistered, (
        f"frame writer(s) not in RECORD_BEARING_WRITERS and not exempt: {sorted(unregistered)}. "
        "Either route the destination through refuse_unless_declared_output_root and register it, "
        "or add it to _EXEMPT_WRITERS with the reason it cannot carry record content."
    )


#: Frame writers under a record-bearing tree that deliberately carry NO record content. Each is
#: listed with its reason, so an addition is a decision rather than an oversight.
_EXEMPT_WRITERS: frozenset[str] = frozenset(
    {
        # Projects to the five tracked columns and DROPS `name`, so it cannot pair a name with a
        # structure; its destination is additionally pinned by the never-clobber guard.
        "adjudication.export_tracked_adjudication",
        # Writes the verdict series + the generated flag. Keys only, no names.
        "adjudication.adjudicate_pgp_labels",
    }
)
# NOTE: `merge_report` is deliberately absent. It was in this list on first draft, written from
# assumption, and `test_the_exempt_list_is_itself_accounted_for` rejected it: that module writes
# MARKDOWN via `render_markdown` and calls no DataFrame writer at all, so it is not discovered and
# must not be exempted. The stale-exemption check caught a fabricated entry on its first run, which
# is the entire reason it exists.


def test_the_exempt_list_is_itself_accounted_for():
    """An exemption naming a function that no longer exists silently shrinks the check."""
    discovered = _frame_writers_in_source()
    stale = _EXEMPT_WRITERS - discovered
    assert not stale, (
        f"_EXEMPT_WRITERS names writer(s) that no longer exist: {sorted(stale)}. "
        "A stale exemption is a hole that looks like a decision."
    )


def test_the_declared_roots_are_relative_and_untracked_by_name():
    """The roots are the guard's whole allow-list; a tracked path among them voids everything."""
    assert DECLARED_OUTPUT_ROOTS, "no declared output roots — the guard would refuse everything"
    for rel in DECLARED_OUTPUT_ROOTS:
        assert not Path(rel).is_absolute(), f"{rel} is absolute; roots are project-relative"
        assert not str(rel).startswith(".."), f"{rel} escapes the project"
        assert str(rel).split("/")[0] == "data", (
            f"{rel} is not under data/ — configs/, docs/ and workstreams/ are TRACKED, and a "
            "tracked declared root would make the guard accept exactly what it exists to refuse"
        )


def test_a_destination_outside_every_declared_root_is_refused():
    """The guard's core predicate, called directly rather than through a writer."""
    with pytest.raises(OutputRootError):
        refuse_unless_declared_output_root(PROJECT_ROOT / "configs" / "FIXTURE_probe.csv")
    with pytest.raises(OutputRootError):
        refuse_unless_declared_output_root(PROJECT_ROOT / "FIXTURE_probe.csv")


def test_a_tracked_by_negation_name_is_refused_inside_a_declared_root(tmp_path, monkeypatch):
    """`.dvc`/`.sha256`/`.gitkeep` are tracked by this project's own .gitignore negations."""
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "registry-test")
    for name in ("probe.dvc", "probe.sha256", ".gitkeep"):
        with pytest.raises(OutputRootError):
            refuse_unless_declared_output_root(tmp_path / name)


def test_a_symlinked_destination_and_a_symlinked_ancestor_are_both_refused(tmp_path, monkeypatch):
    """The measured bypass: a symlinked `configs` whose resolve() erased it before the check."""
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "registry-test")
    link = tmp_path / "link.csv"
    link.symlink_to(tmp_path / "real.csv")
    with pytest.raises(OutputRootError):
        refuse_unless_declared_output_root(link)

    real_dir = tmp_path / "real_dir"
    real_dir.mkdir()
    linked_dir = tmp_path / "linked_dir"
    linked_dir.symlink_to(real_dir, target_is_directory=True)
    with pytest.raises(OutputRootError):
        refuse_unless_declared_output_root(linked_dir / "probe.csv")


def test_the_pytest_temp_grant_is_withdrawn_when_tmpdir_overlaps_the_project(monkeypatch):
    """TMPDIR=<project> made the entire tracked tree a declared root. It must not return."""
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "registry-test")
    monkeypatch.setenv("TMPDIR", str(PROJECT_ROOT))
    import tempfile as _tempfile

    _tempfile.tempdir = None  # clear the cached value so gettempdir() re-reads TMPDIR
    try:
        roots = declared_output_roots()
        assert PROJECT_ROOT.resolve() not in roots, (
            "the project root became a declared output root via TMPDIR — this is the measured "
            "incident, where writing accession+name+structure into configs/ was accepted"
        )
        with pytest.raises(OutputRootError):
            refuse_unless_declared_output_root(PROJECT_ROOT / "configs" / "FIXTURE_probe.csv")
    finally:
        _tempfile.tempdir = None
        os.environ.pop("TMPDIR", None)
