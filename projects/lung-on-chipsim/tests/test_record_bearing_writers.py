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

import argparse
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
    # No match=: "data/interim" is the allow-list constant the generic message always enumerates,
    # so it is satisfied by any refusal at all. The message contract is asserted once, by
    # test_the_refusal_names_the_destination_and_the_remedy, and nowhere else.
    with pytest.raises(OutputRootError):
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
    # NOT match="symlink": pytest names tmp_path after the test, so this test's OWN directory
    # contains the word and the assertion passed with the destination check DELETED — verbatim the
    # trap the r2.19 test I deleted had documented, reintroduced by my own migration. Assert the
    # sentence only this branch can produce, and prove the generic refusal is NOT what fired.
    plain = tmp_path / "x"
    plain.mkdir()
    target = plain / "w.csv"
    os.symlink(PROJECT_ROOT / "configs" / "stolen.csv", target)
    with pytest.raises(OutputRootError) as exc:
        refuse_unless_declared_output_root(target)
    message = str(exc.value)
    assert "the destination is a symlink" in message
    assert "not inside a declared untracked root" not in message


def test_a_symlinked_ANCESTOR_is_refused(tmp_path):
    """The ancestor case is the one `resolve()` alone hides: a link named like a declared root,
    pointing anywhere."""
    # NOT match="symlink". pytest names tmp_path after the test function, so this test's own
    # directory contains the word: a reviewer left the branch raising, deleted "symlink" from its
    # message, and the file stayed green. The sibling test above documents this exact trap in a
    # comment and avoids it; this one walked into it one function later.
    (tmp_path / "real").mkdir()
    os.symlink(tmp_path / "real", tmp_path / "interim")
    with pytest.raises(OutputRootError) as exc:
        refuse_unless_declared_output_root(tmp_path / "interim" / "w.csv")
    message = str(exc.value).replace(str(tmp_path), "<tmp>")
    assert "is a symlink" in message
    assert "the path the check sees is not the path the write reaches" in message
    assert "not inside a declared untracked root" not in message, (
        "the generic refusal fired, so the ancestor branch is not what this test exercised"
    )


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
    # OutputRootError, not Exception: a bare Exception is satisfied by anything raised BEFORE the
    # guard is ever reached, so the test would pass while the destination went unchecked.
    with pytest.raises(OutputRootError):
        write_adjudication_worksheet(labels, compounds, target)
    assert not target.exists()


def test_a_refused_write_does_not_create_the_tracked_directory_first(tmp_path, monkeypatch):
    """The migration dropped `assert not target.parent.exists()`. Both refusal tests aim at
    directories that already exist, so an `mkdir` before the guard is invisible to them."""
    from chipsim.harmonize.adjudication import write_adjudication_worksheet

    root = _tracked_like(tmp_path, monkeypatch)
    target = root / "docs" / "new" / "deep" / "w.csv"
    labels, compounds = _labels_and_compounds()
    with pytest.raises(OutputRootError):
        write_adjudication_worksheet(labels, compounds, target)
    assert not (root / "docs").exists(), "a refused write must not create the tree first"


def test_the_refusal_names_the_destination_and_the_remedy(tmp_path, monkeypatch):
    """`match="data/interim"` is satisfied by the constant the message enumerates, so a message
    reduced to "refusing. Allowed: ..." passed — losing both the destination and the recovery
    path the deleted r2.19 test had pinned."""
    root = _tracked_like(tmp_path, monkeypatch)
    target = root / "configs" / "pgp_adjudication.csv"
    with pytest.raises(OutputRootError) as exc:
        refuse_unless_declared_output_root(target)
    message = str(exc.value)
    assert str(target) in message, "the message must name what was refused"
    assert "export_tracked_adjudication" in message, "and how to publish legitimately"


def test_containment_consults_directory_identity_not_string_case(tmp_path, monkeypatch):
    """A casefolded-string implementation — the PERMISSIVE direction the module forbids — survives
    on a case-insensitive volume, because the case test computes its expectation from the same rule
    the implementation uses. Pin that `samestat` is actually consulted."""

    root = _tracked_like(tmp_path, monkeypatch)
    ok = root / "data" / "interim" / "w.csv"
    refuse_unless_declared_output_root(ok)

    monkeypatch.setattr(os.path, "samestat", lambda a, b: False)
    with pytest.raises(OutputRootError):
        refuse_unless_declared_output_root(ok)


def test_the_cli_reports_a_refused_destination_as_a_message_not_a_traceback(
    tmp_path, monkeypatch, capsys
):
    """My own test asserted in PROSE that the CLI has an `except OutputRootError` clause — which
    did not exist. `chipsim write --out <tracked path>` exited with a raw traceback, journalled as
    "crashed": the failure mode the sibling command's docstring promises to abolish."""
    import chipsim.ingest.drugbank_snapshot as ds
    from chipsim import pipeline
    from chipsim.harmonize import ids

    root = _tracked_like(tmp_path, monkeypatch)
    monkeypatch.setenv("CHIPSIM_PROJECT_ROOT", str(tmp_path))
    out = root / "configs" / "drugbank_compounds.parquet"

    # Reach the WRITE: the command loads the snapshot first, and the refusal is what is under test.
    frame = _compound_frame()
    monkeypatch.setattr(ds, "load_compounds", lambda *a, **k: frame)
    monkeypatch.setattr(ids, "add_canonical_identity_excluding", lambda *a, **k: (frame, []))
    monkeypatch.setattr(ids, "load_preregistered_exclusions", lambda *a, **k: set())

    code = pipeline._cmd_write(
        argparse.Namespace(raw_dir=tmp_path, out=out, exclusions=tmp_path / "x.yaml")
    )
    captured = capsys.readouterr()
    assert code == 2
    assert "Traceback" not in captured.err
    assert "ERROR" in captured.err
    assert not out.exists()


def test_the_compound_writer_refuses_a_tracked_destination():
    """The WORST payload in the project — accession, name, InChI and InChIKey on one row — and
    until r2.20 it validated its columns and never its destination."""
    target = PROJECT_ROOT / "configs" / "drugbank_compounds.parquet"
    # OutputRootError, not Exception — see the worksheet twin above.
    with pytest.raises(OutputRootError):
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


#: The serialization surface actually reachable here. `to_csv`/`to_parquet` alone let a writer
#: opt out silently: `pq.write_table`, `to_feather`, `to_hdf` and a bare `open(..., "w")` all
#: survived the registry — and the CLI persisting the complete record via `pq.write_table` with no
#: destination check survived the FULL SUITE.
_SERIALISING_CALLS = frozenset(
    {
        "to_csv",
        "to_parquet",
        "to_feather",
        "to_hdf",
        "to_pickle",
        "to_excel",
        "to_json",
        "to_sql",
        "to_string",
        "write_table",
        "write_dataset",
        "write_feather",
        "save",
        "savez",
        "write_text",
        "write_bytes",
        "dump",
    }
)


def _functions_that_write(module_path: Path) -> set[str]:
    """Every function in a module that serialises something."""
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    writers: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for inner in ast.walk(node):
            if (
                isinstance(inner, ast.Call)
                and isinstance(inner.func, ast.Attribute)
                and inner.func.attr in _SERIALISING_CALLS
            ):
                writers.add(f"{module_path.stem}.{node.name}")
            # A WRITE MODE, however the file was opened. `open(p, "w")` is an `ast.Name` call and
            # `p.open("wb")` is an `ast.Attribute` call, and matching only the first let the reader
            # that materialises EVERY TRACKED BLOB leave this registry silently — not by being new,
            # but by changing how it writes. `Path.open` is the same act as `open`; the detector
            # has to agree.
            # The MODE SITS IN A DIFFERENT SLOT in the two spellings: `open(path, "w")` carries it
            # at args[1] because args[0] is the path, while `path.open("wb")` carries it at
            # args[0] because the path is the receiver. Looking only at args[1:] finds nothing in
            # the attribute form — which is how the first attempt at this fix still saw zero
            # writers in the module it was written for.
            is_open_call = isinstance(inner, ast.Call) and (
                (isinstance(inner.func, ast.Name) and inner.func.id == "open")
                or (isinstance(inner.func, ast.Attribute) and inner.func.attr == "open")
            )
            mode_args = []
            if is_open_call:
                positional = (
                    inner.args[1:] if isinstance(inner.func, ast.Name) else list(inner.args)
                )
                mode_args = [*positional, *(kw.value for kw in inner.keywords)]
            opens_for_write = is_open_call and any(
                isinstance(arg, ast.Constant)
                and isinstance(arg.value, str)
                and ("w" in arg.value or "a" in arg.value or "+" in arg.value)
                for arg in mode_args
            )
            if opens_for_write:
                writers.add(f"{module_path.stem}.{node.name}")
    return writers


def test_the_writer_detector_sees_more_than_two_pandas_methods(tmp_path):
    """Anti-vacuity for the SCANNER, not just for its result: a planted writer using each API must
    be found. `pq.write_table` in the CLI — persisting accession + name + InChI + InChIKey to any
    path with no destination check — survived the full suite before this."""
    module = tmp_path / "planted.py"
    module.write_text(
        "import pyarrow.parquet as pq\n"
        "def a(frame, out):\n    pq.write_table(frame, out)\n"
        "def b(frame, out):\n    frame.to_feather(out)\n"
        "def c(frame, out):\n    frame.to_hdf(out, key='x')\n"
        "def d(frame, out):\n    open(out, 'w').write(frame.to_string())\n"
        "def e(frame, out):\n    return frame.sum()\n"
    )
    found = _functions_that_write(module)
    assert found == {"planted.a", "planted.b", "planted.c", "planted.d"}


def test_no_declared_writer_is_a_phantom():
    """`merge_report.write_merge_report` was declared and DOES NOT EXIST. Because the assertion was
    `found <= declared`, a stale declaration passed silently — while the real writer in that module
    (`main`, via write_text) stayed invisible. The incident this guard's docstrings cite is a merge
    report that carried 89 real accessions."""
    found: set[str] = set()
    for path in sorted((PROJECT_ROOT / "chipsim").rglob("*.py")):
        found |= _functions_that_write(path)
    declared = (
        set(RECORD_BEARING_WRITERS) | set(NOT_RECORD_BEARING) | set(RECORD_BEARING_PENDING_RULING)
    )
    assert declared <= found, f"declared writer(s) that do not exist: {sorted(declared - found)}"


def test_every_function_that_writes_a_frame_is_classified():
    """The registry pattern that caught the unregistered fixture file: a new writer must be
    DECLARED either as record-bearing (and therefore calling the helper) or as not, so it cannot
    silently opt out of the check."""
    found: set[str] = set()
    for path in sorted((PROJECT_ROOT / "chipsim").rglob("*.py")):
        found |= _functions_that_write(path)

    declared = (
        set(RECORD_BEARING_WRITERS) | set(NOT_RECORD_BEARING) | set(RECORD_BEARING_PENDING_RULING)
    )
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
    # Not a writer at all: stringifies a parquet IN MEMORY so the record-content scan can read it.
    # It touches no path. Declared rather than excluded from the scan, because a scan that knows
    # about "the ones that do not really count" stops being a registry.
    "decoding._parquet_chunks",
    # A hex digest of a file. No compound data of any kind.
    "drugbank_snapshot.write_digest_sidecar",
    # Run metadata and config snapshots into the git-ignored journal; no compound rows.
    "journal.start_run",
    "pipeline._journal_best_effort",
    # HOW a run was approved — command, mode, whether a tty was attached, timestamp, argv — written
    # beside the config snapshot in the same git-ignored journal. Same class as the two above: run
    # metadata, no compound rows. Caught by this registry the moment it existed, which is the
    # property the registry is for.
    "pipeline._write_approval_record",
    # The ratified barrier panel (protein identifiers + ratifier attribution), T7a's human
    # artifact. It legitimately writes configs/barrier_panel.yaml and carries no DrugBank content.
    "pgp_label.seal_panel",
}

#: Writers whose payload CAN carry record content but whose legitimate destination is NOT a
#: declared untracked root, so r2.20's helper cannot be applied to them as written. Escalated to
#: the CTO; recorded here so the registry states the gap instead of hiding it behind a
#: comfortable classification.
#:
#: These were INVISIBLE to the registry until the detector was widened beyond to_csv/to_parquet —
#: which is exactly the "a new writer cannot silently opt out" property r2.20 asks for, working.
RECORD_BEARING_PENDING_RULING = {
    # Writes the raw DrugBank tables to `--dest`, unvalidated: the most record-bearing payload in
    # the project. Its legitimate home is data/raw/ (DVC-tracked, git-ignored), not a declared root.
    "drugbank_snapshot.fetch_snapshot",
    # The function that ACTUALLY WRITES the bytes `fetch_snapshot` is registered for: it streams
    # each remote snapshot file to disk through `target.open("wb")`. Invisible to this registry
    # until the detector above learned that spelling — the same blind spot, and the same
    # entry-point-vs-writer split, as `repo._consume_blobs` below, but PRE-EXISTING and nobody's
    # recent change. It carries the raw DrugBank tables, so it inherits `fetch_snapshot`'s
    # classification exactly: record-bearing, destination not a declared root.
    "drugbank_snapshot._download",
    # Writes merge_report.json/.md to an operator-chosen --out. Today it identifies members by
    # canonical InChIKey only and sends the id/name association to the git-ignored journal — but
    # "a tracked merge report came to carry 89 real accessions" is the incident this guard's own
    # docstrings cite, and the destination is unguarded.
    "merge_report.main",
    # Writes EVERY TRACKED BLOB into a TemporaryDirectory so the commit gate can read the bytes a
    # commit would carry (r2.32). Its payload is, by construction, the most record-bearing thing in
    # the repository — so "not record bearing" would be the comfortable classification this list
    # exists to refuse — but its destination is a temp tree outside the repository, not a declared
    # root, so `refuse_unless_declared_output_root` cannot be applied to it as written.
    #
    # The security review named the residual: that tree contains exactly the content the gate exists
    # to keep out of the repository, and it survives an abnormal exit. Escalated with the reader
    # change rather than filed as settled.
    #
    # REGISTERED UNDER THE FUNCTION THAT ACTUALLY WRITES, not the public entry point
    # (`repo.materialise_blobs`) that calls it. When the write moved into this helper and changed
    # from `write_bytes` to a file handle, the detector above stopped seeing it at all and the
    # entry named here became a phantom — the registry was silently describing a writer that no
    # longer existed while missing the one that did.
    "repo._consume_blobs",
}


def test_both_record_bearing_writers_are_registered():
    assert set(RECORD_BEARING_WRITERS) == {
        "adjudication.write_adjudication_worksheet",
        "drugbank_snapshot.write_compounds",
    }


# --- §7: the four EXECUTED bypasses of this very allow-list ----------------------------------


def _tracked_like(tmp_path: Path, monkeypatch) -> Path:
    """A fake project root inside tmp_path, with the declared roots present.

    The refusal tests must NOT aim at the real tracked tree: under a guard regression the suite
    itself planted a name-bearing worksheet in `configs/` and left it there, poisoning a later run.
    A red test must never be able to commit the violation it is testing for.
    """
    import chipsim.guards.output_roots as guard

    root = tmp_path / "fake_project"
    (root / "data" / "interim").mkdir(parents=True)
    (root / "data" / "processed").mkdir(parents=True)
    (root / "configs").mkdir()
    monkeypatch.setattr(guard, "source_root", lambda: root)
    return root


def test_the_temp_sibling_cannot_be_redirected_into_a_tracked_path(tmp_path, monkeypatch):
    """§7 EXECUTED BYPASS. The guard validates `out`; the writer then wrote `out.name + '.tmp'`,
    and `to_csv` FOLLOWS a symlink. Pre-placing that sibling as a link into `configs/` meant a
    perfectly legitimate, fully-allowed call wrote the name-bearing worksheet into the tracked
    directory — check-one-object-write-another, the r2.20 docstring's own bypass #3, moved one
    filename over."""
    from chipsim.harmonize.adjudication import write_adjudication_worksheet

    root = _tracked_like(tmp_path, monkeypatch)
    victim = root / "configs" / "stolen_via_tmp.csv"
    out = root / "data" / "interim" / "pgp_adjudication.csv"
    os.symlink(victim, out.with_name(out.name + ".tmp"))

    labels, compounds = _labels_and_compounds()
    write_adjudication_worksheet(labels, compounds, out)

    assert not victim.exists(), "the tracked path must not be written through the temp sibling"
    assert out.is_file() and "name" in pd.read_csv(out, dtype=str).columns


def test_a_hardlinked_destination_is_refused(tmp_path, monkeypatch):
    """§7 EXECUTED BYPASS. Only symlinks were refused. `os.link(configs/victim, data/interim/x)`
    then `write_compounds(...)` overwrote the TRACKED file in place with accession + name + InChI +
    InChIKey on one row — no symlink anywhere."""
    root = _tracked_like(tmp_path, monkeypatch)
    victim = root / "configs" / "victim_tracked.csv"
    victim.write_text("original tracked content\n")
    hard = root / "data" / "interim" / "hard.parquet"
    os.link(victim, hard)

    with pytest.raises(OutputRootError, match="hard link"):
        refuse_unless_declared_output_root(hard)
    assert victim.read_text() == "original tracked content\n"


def test_the_declared_tmp_root_cannot_be_redirected_by_an_environment_variable(
    tmp_path, monkeypatch
):
    """§7 EXECUTED BYPASS. The third declared root came from `tempfile.gettempdir()`, i.e. $TMPDIR.
    Point it at the project and THE WHOLE TRACKED TREE becomes a declared output root — writing
    accession+name+structure into `configs/` was ACCEPTED. CI runners routinely set TMPDIR inside
    the workspace.

    `journal.source_root()`'s own docstring refuses exactly this ("a location that can be
    redirected by an environment variable is one an operator cannot reason about"), and the CTO had
    flagged this family of defect an hour before I wrote it.
    """
    root = _tracked_like(tmp_path, monkeypatch)
    monkeypatch.setenv("TMPDIR", str(root))

    with pytest.raises(OutputRootError):
        refuse_unless_declared_output_root(root / "configs" / "leak_via_tmpdir.csv")


def test_a_tracked_by_negation_filename_inside_a_declared_root_is_refused(tmp_path, monkeypatch):
    """§7 EXECUTED BYPASS. The roots are "untracked" BY DIRECTORY, but .gitignore re-includes
    `!data/**/*.dvc`, `!data/**/.gitkeep` and `!data/processed/*.sha256` — so those names ARE
    tracked inside the allowed directories. Writing the name-bearing worksheet to
    `data/processed/pgp_adjudication.sha256` was accepted: no symlink, no env var, no race, just a
    filename in the directory where `.sha256` is this project's own sidecar convention."""
    # NOT match="tracked": the word comes from this test's own tmp directory name. A reviewer
    # replaced this branch's entire .gitignore explanation with "nope." and the file stayed green —
    # the message that makes the refusal actionable could be deleted unnoticed.
    root = _tracked_like(tmp_path, monkeypatch)
    for rel in ("data/processed/x.sha256", "data/interim/x.dvc", "data/interim/.gitkeep"):
        with pytest.raises(OutputRootError) as exc:
            refuse_unless_declared_output_root(root / rel)
        message = str(exc.value).replace(str(tmp_path), "<tmp>")
        assert ".gitignore re-includes it" in message
        assert "untracked by DIRECTORY" in message
        assert Path(rel).name in message, "the refusal must name the file the operator chose"

    # The ordinary names in the same directories stay allowed.
    refuse_unless_declared_output_root(root / "data" / "processed" / "x.parquet")
    refuse_unless_declared_output_root(root / "data" / "interim" / "x.csv")
