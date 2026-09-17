"""Record-bearing writers refuse a destination outside the declared untracked roots — r2.20.

The invariant is *not written to a tracked path*, so the rule names where writing IS allowed.
r2.19 guarded the NAME `configs/` and the §5 reviewers executed three bypasses of it: `CONFIGS/`
(which on a case-insensitive volume landed the name-bearing worksheet in the REAL `configs/`), a
symlinked `configs` directory that `resolve()` erased, and check-one-object-write-another where
`os.replace` swapped a destination symlink for a real file inside the tracked directory. It was
also too broad, refusing every write under any `configs` ancestor including the recovery path.

Two writers carry record content and must both go through ONE helper:
  - `write_adjudication_worksheet` — `name` beside `canonical_inchikey`;
  - `write_compounds` — accession, name, InChI and InChIKey ON ONE ROW, the complete record.
`chipsim write --out` inherits the refusal through the second; it gets no second check, because
two checks drift and the second becomes the one people trust.

NOTE ON CASE (r2.20 says "case-insensitively"): for an ALLOW-list, case-insensitive matching is the
PERMISSIVE direction — the opposite of the deny-list it replaces. `DATA/INTERIM` must be allowed
when it IS the declared directory (a case-insensitive volume) and refused when it is a different
directory that merely spells alike. So identity is decided by the filesystem (same directory),
never by lowercasing a string.
"""

from __future__ import annotations

import ast
import os
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from chipsim.guards.output_roots import (
    RECORD_BEARING_WRITERS,
    OutputRootError,
    declared_output_roots,
    refuse_unless_declared_output_root,
)
from chipsim.ingest.drugbank_snapshot import COMPOUND_COLUMNS, write_compounds

PROJECT_ROOT = Path(__file__).resolve().parent.parent
KEY = "FIXTURECMPDAAA-FIXTUREKEY-N"


def _labels_and_compounds():
    labels = pd.Series(["yes"], index=[KEY])
    labels.index.name = "canonical_inchikey"
    compounds = pd.DataFrame(
        {"canonical_inchikey": [KEY], "name": ["FIXTURE-NAME"], "stereo_is_relative": [False]}
    )
    return labels, compounds


def _compound_frame():
    return pd.DataFrame({column: ["x"] for column in COMPOUND_COLUMNS}).assign(
        canonical_inchikey=[KEY], stereo_is_relative=[False]
    )


# --- the helper itself -------------------------------------------------------------------


def test_the_declared_roots_are_exactly_what_the_clause_names():
    roots = declared_output_roots()
    assert (PROJECT_ROOT / "data" / "interim").resolve() in roots
    assert (PROJECT_ROOT / "data" / "processed").resolve() in roots
    assert Path(tempfile.gettempdir()).resolve() in roots
    assert len(roots) == 3, "a fourth root is a policy change, not a detail"


@pytest.mark.parametrize(
    "rel",
    [
        "configs/pgp_adjudication.csv",
        "pgp_adjudication.csv",
        "docs/leak.csv",
        "tests/fixtures/leak.csv",
        "data/raw/drugbank/leak.parquet",
    ],
    ids=["configs", "project-root", "docs", "fixtures", "data-raw"],
)
def test_every_tracked_destination_is_refused(rel):
    """r2.19 protected ONE directory name. Measured at §5: the name-bearing worksheet wrote
    cleanly to the project root, docs/, tests/fixtures/ and workstreams/ — all tracked."""
    with pytest.raises(OutputRootError, match="data/interim"):
        refuse_unless_declared_output_root(PROJECT_ROOT / rel)


@pytest.mark.parametrize("rel", ["data/interim/w.csv", "data/processed/c.parquet"])
def test_the_declared_roots_are_allowed(rel):
    refuse_unless_declared_output_root(PROJECT_ROOT / rel)


def test_a_relative_escape_out_of_a_declared_root_is_refused():
    """Containment on the RESOLVED path: `data/interim/../../configs/x` is not in a declared root
    however it is spelled."""
    with pytest.raises(OutputRootError):
        refuse_unless_declared_output_root(
            PROJECT_ROOT / "data" / "interim" / ".." / ".." / "configs" / "x.csv"
        )


@pytest.mark.parametrize(
    "rel",
    ["configs/sub/deep/w.csv", "workstreams/lung-on-chipsim/w.csv"],
    ids=["nested-under-configs", "workstreams"],
)
def test_the_refusal_covers_anything_under_a_tracked_directory(rel):
    """Not just a tracked directory's immediate children: a `parent.name` implementation passed
    every r2.19 test because each fixture put the file directly in `configs/`."""
    with pytest.raises(OutputRootError):
        refuse_unless_declared_output_root(PROJECT_ROOT / rel)


def test_a_bare_filename_written_from_inside_a_tracked_directory_is_refused(monkeypatch):
    """The cwd-relative case: the path's STRING contains no tracked directory at all, so only
    resolution catches it. Under r2.19 this was the one shape that separated a resolving
    implementation from a substring one."""
    monkeypatch.chdir(PROJECT_ROOT / "configs")
    with pytest.raises(OutputRootError):
        refuse_unless_declared_output_root(Path("w.csv"))


def test_a_symlink_loop_raises_the_guards_own_error(tmp_path):
    """A RuntimeError from `resolve()` would escape every `except OutputRootError`, including the
    CLI's, producing the traceback the CLI exists to prevent."""
    os.symlink(tmp_path / "b", tmp_path / "a")
    os.symlink(tmp_path / "a", tmp_path / "b")
    with pytest.raises(OutputRootError):
        refuse_unless_declared_output_root(tmp_path / "a" / "w.csv")


def test_the_test_tmp_root_is_allowed(tmp_path):
    refuse_unless_declared_output_root(tmp_path / "w.csv")


def test_a_symlinked_destination_is_refused(tmp_path):
    """Check and write must mean the SAME object: `os.replace` replaces the link itself, so a
    destination symlink pointing into a tracked directory was the §5 bypass."""
    target = tmp_path / "w.csv"
    os.symlink(PROJECT_ROOT / "configs" / "stolen.csv", target)
    with pytest.raises(OutputRootError, match="symlink"):
        refuse_unless_declared_output_root(target)


def test_a_symlinked_ANCESTOR_is_refused(tmp_path):
    """The ancestor case is the one `resolve()` alone hides: a link named like a declared root,
    pointing anywhere."""
    (tmp_path / "real").mkdir()
    os.symlink(tmp_path / "real", tmp_path / "interim")
    with pytest.raises(OutputRootError, match="symlink"):
        refuse_unless_declared_output_root(tmp_path / "interim" / "w.csv")


def test_containment_is_by_directory_identity_not_by_substring(tmp_path):
    """`data/interim_backup/` merely starts with a declared root's name."""
    with pytest.raises(OutputRootError):
        refuse_unless_declared_output_root(PROJECT_ROOT / "data" / "interim_backup" / "w.csv")


def test_a_case_variant_is_judged_by_identity_not_by_lowercasing():
    """For an ALLOW-list, case-insensitive string matching is the PERMISSIVE direction. `DATA/
    INTERIM` may pass only because the filesystem says it IS `data/interim`, never because the
    letters match once folded."""
    candidate = PROJECT_ROOT / "DATA" / "INTERIM" / "w.csv"
    same_directory = (PROJECT_ROOT / "DATA" / "INTERIM").exists() and os.path.samefile(
        PROJECT_ROOT / "DATA" / "INTERIM", PROJECT_ROOT / "data" / "interim"
    )
    if same_directory:
        refuse_unless_declared_output_root(candidate)
    else:
        with pytest.raises(OutputRootError):
            refuse_unless_declared_output_root(candidate)


# --- both writers actually call it -------------------------------------------------------


def test_the_worksheet_writer_refuses_a_tracked_destination(tmp_path):
    labels, compounds = _labels_and_compounds()
    from chipsim.harmonize.adjudication import write_adjudication_worksheet

    target = PROJECT_ROOT / "configs" / "pgp_adjudication.csv"
    with pytest.raises(Exception, match="data/interim"):
        write_adjudication_worksheet(labels, compounds, target)
    assert not target.exists()


def test_the_compound_writer_refuses_a_tracked_destination():
    """The WORST payload in the project — accession, name, InChI and InChIKey on one row — and
    until r2.20 it validated its columns and never its destination."""
    target = PROJECT_ROOT / "configs" / "drugbank_compounds.parquet"
    with pytest.raises(Exception, match="data/interim"):
        write_compounds(_compound_frame(), target)
    assert not target.exists()


def test_the_compound_writer_still_writes_to_a_declared_root(tmp_path):
    out = tmp_path / "drugbank_compounds.parquet"
    write_compounds(_compound_frame(), out)
    assert out.is_file()


def test_the_cli_inherits_the_refusal_without_a_second_check(tmp_path, capsys):
    """ "The CLI does NOT get a second check of its own, because two checks drift and the second
    becomes the one people trust." So the CLI must refuse *through* the writer."""
    from chipsim import pipeline

    source = inspect_source(pipeline._cmd_write)
    assert "refuse_unless_declared_output_root" not in source, (
        "the CLI must inherit the refusal from write_compounds, not re-implement it"
    )


def inspect_source(function) -> str:
    import inspect

    return inspect.getsource(function)


# --- the registry: a new writer cannot silently opt out ------------------------------------


def _functions_that_write(module_path: Path) -> set[str]:
    """Every function in a module that calls `to_csv` / `to_parquet` on something."""
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    writers: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for inner in ast.walk(node):
            if (
                isinstance(inner, ast.Call)
                and isinstance(inner.func, ast.Attribute)
                and inner.func.attr in {"to_csv", "to_parquet"}
            ):
                writers.add(f"{module_path.stem}.{node.name}")
    return writers


def test_every_function_that_writes_a_frame_is_classified():
    """The registry pattern that caught the unregistered fixture file: a new writer must be
    DECLARED either as record-bearing (and therefore calling the helper) or as not, so it cannot
    silently opt out of the check."""
    found: set[str] = set()
    for path in sorted((PROJECT_ROOT / "chipsim").rglob("*.py")):
        found |= _functions_that_write(path)

    declared = set(RECORD_BEARING_WRITERS) | set(NOT_RECORD_BEARING)
    assert found, "anti-vacuity: the AST scan must find the writers that exist"
    assert found <= declared, (
        f"undeclared frame writer(s): {sorted(found - declared)}. Declare each as record-bearing "
        "(and route it through refuse_unless_declared_output_root) or as not record-bearing."
    )


#: Frame writers whose payload cannot carry DrugBank record content, each with the reason.
NOT_RECORD_BEARING = {
    # The worksheet's five-column projection: no `name`, by construction (r2.17/G-15).
    "adjudication.export_tracked_adjudication",
    # Verdicts + the generated stereo flag, keyed by canonical InChIKey. No name, no accession.
    "adjudication.adjudicate_pgp_labels",
    # Merge-report members, identified by canonical InChIKey only (the id/name association goes to
    # the untracked run journal, never to the report).
    "merge_report.write_merge_report",
    # Not a writer at all: stringifies a parquet IN MEMORY so the record-content scan can read it.
    # It touches no path. Declared rather than excluded from the scan, because a scan that knows
    # about "the ones that do not really count" stops being a registry.
    "drugbank_snapshot._parquet_chunks",
}


def test_both_record_bearing_writers_are_registered():
    assert set(RECORD_BEARING_WRITERS) == {
        "adjudication.write_adjudication_worksheet",
        "drugbank_snapshot.write_compounds",
    }
