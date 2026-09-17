"""E-17: the scan is DATA; rendering is presentation.

Before this, `_render_for_root` computed the verdict and formatted it in one pass, and the exit code
existed nowhere except inside the string it returned. That is not a style complaint — it is why
E-13b happened: no test could assert the exit code cheaply, so twelve mutants survived while every
defect test asserted on a validator's return value instead.
"""

from pathlib import Path

import pytest
import yaml

from chipsim.guards.record_content import (
    ContentPolicy,
    RecordContentScan,
    ScanContext,
    nothing_is_content_exempt,
    nothing_is_waived,
    render_scan,
    scan_record_content,
)

NOTHING_WAIVED = ContentPolicy(
    readability_waived=nothing_is_waived, content_exempt=nothing_is_content_exempt
)


def _surface(tmp_path, owners=None):
    import chipsim.guards.record_content as rc

    proj = tmp_path / "projects" / rc.THIS_PROJECT
    (proj / "configs").mkdir(parents=True, exist_ok=True)
    (tmp_path / "config").mkdir(parents=True, exist_ok=True)
    (proj / "pyproject.toml").write_text("[project]\n")
    (tmp_path / rc.PROJECT_DECLARATION_FILE).write_text(
        yaml.safe_dump({"version": "1", "declarations": []})
    )
    repo_doc = {"version": "1", "declarations": []}
    if owners is not None:
        repo_doc["owners"] = owners
    (tmp_path / rc.REPO_DECLARATION_FILE).write_text(yaml.safe_dump(repo_doc))
    return [
        rc.PROJECT_DECLARATION_FILE,
        rc.REPO_DECLARATION_FILE,
        f"projects/{rc.THIS_PROJECT}/pyproject.toml",
    ]


def _surface_of(root):
    """The surface a caller must now pass explicitly.

    `require` rather than `read`, because that is what the deleted `surface=None` fallback built —
    so every existing test keeps the behaviour it was written against, and the argument is visible.
    """
    import chipsim.guards.record_content as _rc

    return _rc.DeclarationSurface.require(root)


def _write(tmp_path, rel, data: bytes):
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def test_the_exit_code_is_assertable_without_parsing_a_string(tmp_path, monkeypatch):
    """THE binding requirement of E-17. Everything else here follows from it."""
    import chipsim.guards.record_content as rc

    rel = "docs/payload.bin"
    _write(tmp_path, rel, b"\x00\xff\x80\x81 OPAQUE")
    listing = _surface(tmp_path) + [rel]
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    scan = scan_record_content(ScanContext.build(tmp_path, NOTHING_WAIVED))
    assert scan.exit_code == 2
    assert isinstance(scan, RecordContentScan)


def test_a_scan_context_cannot_resolve_itself(tmp_path):
    """What makes state ambient is not aggregation but IMPLICIT RESOLUTION. A context required
    everywhere and resolvable nowhere is the OPPOSITE of ambient state — so there is no default, no
    `None`, and no module-level instance to fall back to. Sixth defect in that family."""
    import inspect

    import chipsim.guards.record_content as rc

    for parameter in inspect.signature(ScanContext).parameters.values():
        assert parameter.default is inspect.Parameter.empty, (
            f"ScanContext.{parameter.name} has a default — a context that can resolve itself is "
            "exactly the ambient state this clause exists to prevent"
        )
    assert not hasattr(rc, "CURRENT_CONTEXT"), "no module-level instance"
    assert not hasattr(rc, "current_context"), "and no resolver"

    signature = inspect.signature(scan_record_content)
    assert list(signature.parameters) == ["context"], (
        "the scan takes the context and nothing else, so nothing can be omitted"
    )
    assert signature.parameters["context"].default is inspect.Parameter.empty


def test_rows_are_typed_and_carry_their_disposition(tmp_path, monkeypatch):
    """A reader should not have to reconstruct "what fails" by grepping four sections of prose."""
    import chipsim.guards.record_content as rc

    mine = f"projects/{rc.THIS_PROJECT}/docs/mine.bin"
    theirs = "projects/perturb-seq-eval/paper/theirs.pdf"
    for rel in (mine, theirs):
        _write(tmp_path, rel, b"\x00\xff\x80\x81 OPAQUE")
    _write(tmp_path, "projects/perturb-seq-eval/pyproject.toml", b"[project]\n")
    listing = _surface(tmp_path, owners=[rc.THIS_PROJECT, "perturb-seq-eval"]) + [
        mine,
        theirs,
        "projects/perturb-seq-eval/pyproject.toml",
    ]
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    scan = scan_record_content(ScanContext.build(tmp_path, NOTHING_WAIVED))
    by_path = {row.path: row for row in scan.rows}

    assert by_path[mine].disposition == "FAILS HERE"
    assert by_path[mine].owner == rc.THIS_PROJECT
    assert by_path[mine].category == "undecodable"
    assert by_path[theirs].disposition == "listed", "another project's file fails no gate today"
    assert by_path[theirs].owner == "perturb-seq-eval"


def test_rendering_is_derived_from_the_scan_and_changes_no_verdict(tmp_path, monkeypatch):
    """Presentation may reorder, group or drop; it may not decide. The exit code the renderer
    reports must be the one the scan computed."""
    import chipsim.guards.record_content as rc

    rel = "docs/payload.bin"
    _write(tmp_path, rel, b"\x00\xff\x80\x81 OPAQUE")
    listing = _surface(tmp_path) + [rel]
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    scan = scan_record_content(ScanContext.build(tmp_path, NOTHING_WAIVED))
    text, code = render_scan(scan)
    assert code == scan.exit_code
    assert rel in text


def test_the_shipped_command_still_renders_what_the_scan_says(tmp_path, monkeypatch, capsys):
    """The command remains the artifact a human reads, and it is now a thin call over the data."""
    import chipsim.guards.record_content as rc
    from chipsim import pipeline
    from chipsim.ingest.drugbank_snapshot import DRUGBANK_CONTENT_POLICY

    rel = "docs/payload.bin"
    _write(tmp_path, rel, b"\x00\xff\x80\x81 OPAQUE")
    listing = _surface(tmp_path) + [rel]
    monkeypatch.setattr(rc, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    code = pipeline.main(["record-content-report"])
    printed = capsys.readouterr().out
    scan = scan_record_content(ScanContext.build(tmp_path, DRUGBANK_CONTENT_POLICY))
    assert code == scan.exit_code
    assert rel in printed


def test_a_structural_error_is_a_field_not_a_paragraph(tmp_path, monkeypatch):
    """E-20 said the header must carry it. E-17 goes one step further: a CONSUMER should not have to
    read the header at all."""
    import chipsim.guards.record_content as rc

    listing = _surface(tmp_path)
    (tmp_path / rc.PROJECT_DECLARATION_FILE).write_text("declarations: [\n  - path: x\n")
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    scan = scan_record_content(ScanContext.build(tmp_path, NOTHING_WAIVED))
    assert scan.structural_error is not None
    assert scan.exit_code == 2
    assert rc.PROJECT_DECLARATION_FILE in scan.structural_error


def test_the_live_repository_scans_clean_as_DATA():
    """The live tree, through the data path rather than the text."""
    import chipsim.guards.record_content as rc
    from chipsim.ingest.drugbank_snapshot import DRUGBANK_CONTENT_POLICY

    scan = scan_record_content(ScanContext.build(rc.repo_root(), DRUGBANK_CONTENT_POLICY))
    assert scan.exit_code == 0
    assert scan.tracked_count > 100
    assert scan.structural_error is None
    assert [row for row in scan.rows if row.disposition == "FAILS HERE"] == []
    assert len([row for row in scan.rows if row.disposition == "listed"]) >= 20


def test_no_public_callable_resolves_a_declaration_surface_for_itself():
    """DESIGN-1. E-17's sixth named defect — "a declaration surface from a `None` default" — SURVIVED
    INSIDE THE FIX FOR IT, in seven public functions one layer below `ScanContext`.

    It was not cosmetic. The fallback built the surface with `require` (RAISES) while
    `ScanContext.build` uses `read` (carries `structural_error`), so ONE broken declaration file gave
    exit 2 through the scan and exit 3 through the direct API — E-13's ruling holding on one path and
    inverted on the other, decided by whether a caller remembered an optional argument.

    The test that was supposed to cover this inspected `ScanContext` alone, and a signature check on
    one class cannot see six functions. This walks the module.
    """
    import inspect

    import chipsim.guards.record_content as rc

    offenders = []
    for name, obj in vars(rc).items():
        if name.startswith("__") or not callable(obj):
            continue
        if getattr(obj, "__module__", None) != rc.__name__:
            continue
        try:
            signature = inspect.signature(obj)
        except (TypeError, ValueError):  # pragma: no cover - builtins
            continue
        for parameter in signature.parameters.values():
            annotation = str(parameter.annotation)
            if (
                "DeclarationSurface" in annotation
                and parameter.default is not inspect.Parameter.empty
            ):
                offenders.append(f"{name}({parameter.name}={parameter.default!r})")
    assert offenders == [], (
        f"these resolve a declaration surface for themselves: {offenders} — a context that can find "
        "itself is the ambient state this clause exists to prevent, and the fallback disagreed with "
        "ScanContext.build about whether a broken file raises"
    )


def test_a_broken_declaration_file_reads_UNREADABLE_not_zero(tmp_path, monkeypatch):
    """DESIGN-5. E-20 fixed the first header line and left the second reading "0 whose claim does not
    hold" — at the moment no claim could be evaluated at all. A count of zero and a count that could
    not be taken must not print the same glyph."""
    import chipsim.guards.record_content as rc

    listing = _surface(tmp_path)
    (tmp_path / rc.PROJECT_DECLARATION_FILE).write_text("declarations: [\n  - path: x\n")
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    scan = scan_record_content(ScanContext.build(tmp_path, NOTHING_WAIVED))
    text, code = render_scan(scan)
    second = text.splitlines()[1]
    assert "UNREADABLE" in second, second
    assert "0 whose claim does not hold" not in text
    assert code == 2


# --- r2.27 §11 code review ---------------------------------------------------------------------


def test_a_hand_built_context_cannot_skip_the_anti_vacuity_refusal(tmp_path, monkeypatch):
    """CODE-1, and it was a false clean through a PUBLIC API.

    The witness and the tracked-count floor ran inside `ScanContext.build` only, so
    `ScanContext(root=real_root, paths=(), ...)` — constructible by anyone, no underscore in sight —
    produced exit 0 naming the CORRECT root over an empty listing. That is E-08 verbatim, reachable
    where previously the only door was `_render_for_root`, which always checked.
    """
    import chipsim.guards.record_content as rc

    listing = _surface(tmp_path)
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))

    # Record the refusal rather than fight it: the property is that it runs on EVERY construction,
    # not only on the ones `build` made.
    seen: list[tuple] = []
    monkeypatch.setattr(
        rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: seen.append(tuple(paths))
    )
    surface = rc.DeclarationSurface.read(tmp_path)

    ScanContext(root=tmp_path, paths=(), submodules=(), policy=NOTHING_WAIVED, surface=surface)
    assert seen == [()], (
        "a hand-built context skipped the anti-vacuity refusal — exit 0 over an empty listing, "
        "naming the correct root, through a public API"
    )

    seen.clear()
    ScanContext.build(tmp_path, NOTHING_WAIVED)
    assert seen and seen[0], "and build still runs it, with the real listing"


def test_a_scan_cannot_disagree_with_its_own_exit_code(tmp_path, monkeypatch):
    """CODE-14. `render_scan` returns `exit_code` verbatim and recomputes nothing — which is right,
    and which meant nothing noticed when the two disagreed. A hand-built scan with a FAILS HERE row
    and exit_code=0 rendered the row and returned 0."""
    import chipsim.guards.record_content as rc

    with pytest.raises(rc.RecordContentScanError, match="internally inconsistent"):
        RecordContentScan(
            root=tmp_path,
            package=tmp_path / "pkg.py",
            tracked_count=500,
            failing_count=1,
            rows=(rc.ScanRow("x.bin", None, "undecodable", "FAILS HERE"),),
            declaration_counts=(0, 0, 0),
            defect_count=0,
            submodules=(),
            registry_state="declared",
            structural_error=None,
            exit_code=0,
        )


def test_a_row_in_an_unknown_category_is_still_printed(tmp_path):
    """CODE-5. The renderer partitioned rows by three literal strings with no catch-all, so a row in
    any other category vanished from every section of the text while still driving the exit code.
    "A listing that reaches no one is functionally a silent skip" is this module's own standard."""
    import chipsim.guards.record_content as rc

    scan = RecordContentScan(
        root=tmp_path,
        package=tmp_path / "pkg.py",
        tracked_count=500,
        failing_count=1,
        rows=(rc.ScanRow("b/new-kind.bin", None, "some-future-category", "FAILS HERE"),),
        declaration_counts=(0, 0, 0),
        defect_count=0,
        submodules=(),
        registry_state="declared",
        structural_error=None,
        exit_code=2,
    )
    text, code = render_scan(scan)
    assert code == 2
    assert "b/new-kind.bin" in text, "a FAILS HERE row was invisible to the reader"
    assert "UNRECOGNISED CATEGORY" in text


def test_an_unreadable_registry_is_not_reported_as_marker_backed(tmp_path, monkeypatch):
    """CODE-9. `registry_declared: bool` flattened three states into two, so a repository whose
    registry could not be PARSED printed "no `owners` list in <file>" — false, the file has one —
    beside a claim that the marker mitigation was in force, when every owner had been narrowed
    away."""
    import chipsim.guards.record_content as rc

    listing = _surface(tmp_path, owners=[rc.THIS_PROJECT])
    (tmp_path / rc.REPO_DECLARATION_FILE).write_text("owners: [\n")
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    scan = scan_record_content(ScanContext.build(tmp_path, NOTHING_WAIVED))
    text, _code = render_scan(scan)
    assert scan.registry_state == "unreadable"
    assert "owner registry: UNREADABLE" in text
    assert "MARKER-BACKED ONLY" not in text, "the mitigation was NOT in force"


def test_the_structural_error_cannot_break_the_reports_indentation(tmp_path, monkeypatch):
    """CODE-11. The message is multi-line PyYAML output echoing a tracked file's own text, and its
    continuation lines landed at column 0 — so attacker-chosen printable content appeared as
    free-standing report lines. Every path goes through `render_path` for exactly this reason."""
    import chipsim.guards.record_content as rc

    listing = _surface(tmp_path)
    (tmp_path / rc.PROJECT_DECLARATION_FILE).write_text("declarations: [ unclosed\n")
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    scan = scan_record_content(ScanContext.build(tmp_path, NOTHING_WAIVED))
    text, _code = render_scan(scan)
    body = text.splitlines()[1:]
    assert body, "no body lines means this `all()` proves nothing about indentation"
    assert all(line.startswith("  ") or line == "" for line in body), (
        "a line landed at column 0 and reads as a report line of its own:\n"
        + "\n".join(line for line in body if not line.startswith("  "))
    )


# --- r2.27 §11 test review: the mutants that survived ------------------------------------------


def test_no_constructor_on_the_scan_path_acquires_a_default(tmp_path):
    """MUT-24 and MUT-25. `ScanContext` itself is default-free and the existing test checks that —
    but it never looked at `ScanContext.build`, which is documented as "the only constructor a caller
    needs", nor at `_render_for_root`, which is what the shipped non-pytest entry point calls.

    Both survived the whole suite with defaults added. A shape check that inspects one class cannot
    see the constructors around it.
    """
    import inspect

    import chipsim.guards.record_content as rc

    for label, fn in (
        ("ScanContext.build", ScanContext.build),
        ("_render_for_root", rc._render_for_root),
        ("scan_record_content", scan_record_content),
        ("render_scan", render_scan),
    ):
        for parameter in inspect.signature(fn).parameters.values():
            assert parameter.default is inspect.Parameter.empty, (
                f"{label}({parameter.name}=...) acquired a default — a scan that can resolve any "
                "part of itself is the ambient state this clause forbids"
            )


def test_the_scan_root_cannot_come_from_the_environment(tmp_path, tmp_path_factory, monkeypatch):
    """MUT-5c, and it walks straight around the shape check. An implementation that keeps
    `ScanContext` default-free and `scan_record_content(context)` mandatory, and then resolves the
    ROOT from `$CHIPSIM_SCAN_ROOT` inside `_render_for_root`, reinstates the sixth member of the
    family the clause enumerates ("a tmp root from $TMPDIR") without tripping a signature check.

    MY FIRST VERSION OF THIS TEST DID NOT KILL THE MUTANT. It asserted on the EXIT CODE while
    patching `_tracked_listing` to return the same listing whatever root it was handed — so the
    decoy scan reported the same 2 (every path missing on disk, unowned, failing) and the two roots
    were indistinguishable through the number I was reading. The listing is root-aware here, and the
    assertion is on WHICH ROOT THE REPORT NAMES, which is the thing the defect actually changes.
    """
    import chipsim.guards.record_content as rc

    rel = "docs/payload.bin"
    _write(tmp_path, rel, b"\x00\xff\x80\x81 OPAQUE")
    handed = _surface(tmp_path) + [rel]

    decoy = tmp_path_factory.mktemp("decoy")
    decoy_listing = _surface(decoy)

    listings = {tmp_path.resolve(): handed, decoy.resolve(): decoy_listing}
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listings[Path(root).resolve()], []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    monkeypatch.setenv("CHIPSIM_SCAN_ROOT", str(decoy))
    monkeypatch.setenv("TMPDIR", str(decoy))
    monkeypatch.setenv("CHIPSIM_PROJECT_ROOT", str(decoy))
    monkeypatch.chdir(decoy)

    text, code = rc._render_for_root(tmp_path, NOTHING_WAIVED)
    assert str(tmp_path) in text, "the report must name the root it was HANDED"
    assert str(decoy) not in text, (
        "the scan answered about a root nobody passed it — the root was resolved from the "
        "environment, which is the ambient state this clause forbids"
    )
    assert code == 2, "and it is the handed root's verdict, not the decoy's clean one"

    scan = scan_record_content(ScanContext.build(tmp_path, NOTHING_WAIVED))
    assert scan.root == tmp_path.resolve()


def test_a_missing_path_is_categorised_missing_not_undecodable(tmp_path, monkeypatch):
    """MUT-8. Building the missing-on-disk rows with `category="undecodable"` survived 219/219 —
    and the two text tests that appear to cover the section pass while the SECTION IS GONE, because
    `"not present on disk" in printed` is satisfied by the unconditional header fragment
    "N not present on disk" even when N is zero."""
    import chipsim.guards.record_content as rc

    ghost = "docs/ghost_payload.bin"  # in the listing, never written
    live = "docs/payload.bin"
    _write(tmp_path, live, b"\x00\xff\x80\x81 OPAQUE")
    listing = _surface(tmp_path) + [ghost, live]
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    scan = scan_record_content(ScanContext.build(tmp_path, NOTHING_WAIVED))
    by_path = {row.path: row for row in scan.rows}
    assert by_path[ghost].category == "missing-on-disk"
    assert by_path[live].category == "undecodable"

    text, _code = render_scan(scan)
    assert "tracked but NOT PRESENT ON DISK" in text, "the SECTION, not the header fragment"
    assert ", 1 not present on disk" in text.splitlines()[0]


def test_the_tracked_count_is_the_listing_length_exactly(tmp_path, monkeypatch):
    """MUT-15. `len(paths) + 1` survived: the only live assertion was a floor (`> 100`), and this is
    the very number the E-08 finding is about — "scanned N tracked files under ROOT"."""
    import chipsim.guards.record_content as rc

    listing = _surface(tmp_path)
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    scan = scan_record_content(ScanContext.build(tmp_path, NOTHING_WAIVED))
    assert scan.tracked_count == len(listing)
    text, _code = render_scan(scan)
    assert f"scanned {len(listing)} tracked files under {tmp_path}" in text


def test_the_registry_state_is_pinned_in_every_direction(tmp_path, monkeypatch):
    """MUT-16. A hardcoded registry state survived 219/219, so the report's E-11 disclosure was
    unpinned BOTH ways: it could claim the marker-only mitigation while a registry was declared
    (understating the control) or the reverse (overstating it)."""
    import chipsim.guards.record_content as rc

    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    listing = _surface(tmp_path, owners=[rc.THIS_PROJECT])
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    declared = scan_record_content(ScanContext.build(tmp_path, NOTHING_WAIVED))
    assert declared.registry_state == "declared"
    assert "owner registry: DECLARED" in render_scan(declared)[0]

    listing = _surface(tmp_path)  # no `owners:` key at all
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    absent = scan_record_content(ScanContext.build(tmp_path, NOTHING_WAIVED))
    assert absent.registry_state == "marker-backed-only"
    assert "MARKER-BACKED ONLY" in render_scan(absent)[0]


def test_a_broken_declaration_row_carries_its_reason_as_a_FIELD(tmp_path, monkeypatch):
    """MUT-21 was killed only through the rendered string — which is the coupling E-17 exists to
    remove. `detail` is data; assert it as data."""
    import chipsim.guards.record_content as rc

    gone = f"projects/{rc.THIS_PROJECT}/docs/gone.bin"
    listing = _surface(tmp_path, owners=[rc.THIS_PROJECT])
    import yaml as _yaml

    (tmp_path / rc.PROJECT_DECLARATION_FILE).write_text(
        _yaml.safe_dump(
            {
                "version": "1",
                "declarations": [{"path": gone, "sha256": "a" * 64, "why": "long gone"}],
            }
        )
    )
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    scan = scan_record_content(ScanContext.build(tmp_path, NOTHING_WAIVED))
    broken = [row for row in scan.rows if row.category == "broken-declaration"]
    assert broken, "the declaration is broken and should have produced a row"
    assert all(row.detail for row in broken)
    assert "not tracked" in broken[0].detail
    assert all(row.disposition == "FAILS HERE" for row in broken)
