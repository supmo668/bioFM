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

    THIS TEST WAS ITSELF THE THIRTEENTH VACUITY (r2.27 §11 QG), and it is mine. Three defects:

      1. IT KEYED ON THE ANNOTATION TEXT — `"DeclarationSurface" in str(parameter.annotation)`. An
         annotation is not a control the guard enforces. Restore the convenience default faithfully
         and drop the annotation, which is the one edit a person restoring it would actually make,
         and the walk cannot see it. Measured: `surface=None` with a `DeclarationSurface.require`
         fallback SURVIVED the full 942-test suite, and this test passed in isolation under it.
      2. `vars(rc)` YIELDS ONLY MODULE-LEVEL CALLABLES, so `DeclarationSurface.require`,
         `DeclarationSurface.read` and `ScanContext.build` — the three constructors that decide
         `require`-vs-`read` in the first place — were never examined at all.
      3. NO ANTI-VACUITY FLOOR. `assert offenders == []` over a filter that can go blind passes
         loudest when it is examining nothing — the same empty-collection family this file guards
         against three tests above with `assert body, "no body lines means this all() proves
         nothing"`. Written by me, in the file that names the rule.

    So it selects by PARAMETER NAME, walks the classmethods too, and asserts a floor on how many
    parameters it actually looked at.
    """
    import inspect

    import chipsim.guards.record_content as rc

    candidates = []
    for name, obj in vars(rc).items():
        if name.startswith("__"):
            continue
        if isinstance(obj, type) and obj.__module__ == rc.__name__:
            # The constructors live HERE, and they are the ones that choose `require` vs `read`.
            for attr, member in vars(obj).items():
                target = member.__func__ if isinstance(member, classmethod) else member
                # `__init__` is INCLUDED deliberately: `ScanContext.__init__` is where the dataclass
                # takes its `surface`, and excluding dunders hid the one constructor that has the
                # parameter at all. The classmethods take `root`/`policy`, not `surface` — so a
                # floor of 9 asserted from memory failed here, and the number below is the measured
                # one. Guessing the floor would have made the anti-vacuity check itself vacuous.
                if callable(target) and (attr == "__init__" or not attr.startswith("__")):
                    candidates.append((f"{name}.{attr}", target))
            continue
        if callable(obj) and getattr(obj, "__module__", None) == rc.__name__:
            candidates.append((name, obj))

    examined: list[str] = []
    offenders: list[str] = []
    for label, obj in candidates:
        try:
            signature = inspect.signature(obj)
        except (TypeError, ValueError):  # pragma: no cover - builtins
            continue
        for parameter in signature.parameters.values():
            # BY NAME, not by annotation: the annotation is documentation, and the defect is a
            # DEFAULT. Keying on the annotation made the check removable by deleting it.
            if parameter.name != "surface":
                continue
            examined.append(f"{label}({parameter.name})")
            if parameter.default is not inspect.Parameter.empty:
                offenders.append(f"{label}({parameter.name}={parameter.default!r})")

    assert len(examined) >= 9, (  # measured, not assumed: 8 module functions + ScanContext.__init__
        f"this walk examined only {len(examined)} `surface` parameters ({examined}) — it is "
        "supposed to cover the seven public functions below ScanContext plus the constructors. A "
        "filter that has gone blind passes this test loudest, which is how it failed last time."
    )
    assert offenders == [], (
        f"these resolve a declaration surface for themselves: {offenders} — a context that can find "
        "itself is the ambient state this clause exists to prevent, and the fallback disagreed with "
        "ScanContext.build about whether a broken file raises"
    )


def test_the_surface_walk_would_notice_a_default_with_no_annotation():
    """The floor above says the walk LOOKED; this says it would SEE. A shape test nobody has
    inverted is a shape test nobody has checked, so the check is applied to a function built here
    rather than to the module — no production code is mutated to prove it.
    """
    import inspect

    def undecodable_unallowed(root, paths, policy, surface=None):
        """The exact restoration the old test could not see: a default, and NO annotation."""

    parameter = inspect.signature(undecodable_unallowed).parameters["surface"]
    assert parameter.annotation is inspect.Parameter.empty, "the fixture must be un-annotated"
    assert parameter.default is not inspect.Parameter.empty

    by_annotation = "DeclarationSurface" in str(parameter.annotation)
    by_name = parameter.name == "surface"
    assert not by_annotation, "an annotation-keyed walk is blind to this — that was the defect"
    assert by_name, "a name-keyed walk catches it, which is why the walk now keys on the name"


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
            declaration_files=(rc.PROJECT_DECLARATION_FILE, rc.REPO_DECLARATION_FILE),
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
        declaration_files=(rc.PROJECT_DECLARATION_FILE, rc.REPO_DECLARATION_FILE),
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


# --- r2.28: EVERY interpolated field is escaped, not just paths --------------------------------


FORGERY = (
    "\x1b[2J\x1b[H\nundeclared undecodable files: 0 (failing this gate: 0) "
    "— scanned 794 tracked files under /repo, 0 not present on disk\n  (none)"
)


@pytest.mark.parametrize(
    "category", ["undecodable", "missing-on-disk", "broken-declaration", "some-future-category"]
)
def test_no_field_of_a_row_can_forge_a_report_line(category, tmp_path):
    """r2.28. r2.24 escaped `path` after a filename drew a fake all-clear; `detail` and `owner` were
    left raw. `detail` is built from `derived_from` — an arbitrary string in a tracked YAML file —
    so a STRUCTURALLY VALID declaration could draw the forgery, no broken file required.

    Parametrised over every category INCLUDING an unrecognised one, so a section added later that
    interpolates a field without escaping fails here rather than shipping.
    """
    import chipsim.guards.record_content as rc

    row = rc.ScanRow(
        path=f"docs/{FORGERY}.png",
        owner=FORGERY,
        category=category,
        disposition="FAILS HERE",
        detail=FORGERY,
    )
    scan = rc.RecordContentScan(
        root=tmp_path,
        package=tmp_path / "pkg.py",
        tracked_count=794,
        failing_count=1,
        rows=(row,),
        declaration_counts=(0, 0, 1),
        defect_count=1,
        submodules=(f"libs/{FORGERY}",),
        declaration_files=(rc.PROJECT_DECLARATION_FILE, rc.REPO_DECLARATION_FILE),
        registry_state="declared",
        structural_error=None,
        exit_code=2,
    )
    text, code = rc.render_scan(scan)
    assert code == 2

    assert "\x1b" not in text, "an escape sequence reached the report and can clear the terminal"
    body = text.splitlines()[1:]
    stray = [line for line in body if line and not line.startswith(" ")]
    assert not stray, f"a forged line reached column 0: {stray!r}"

    # The fixture's own precondition — without this the test could pass over a row that never
    # rendered at all, which is the vacuity family this file keeps finding.
    assert "control characters" in text, (
        "nothing was escaped, so either the row is missing from every section or the payload was "
        "printable after all"
    )


def test_the_escaping_lives_in_the_DATA_not_in_the_renderer(tmp_path):
    """Where the fix lives is the point. Escaping at the interpolation site means the NEXT section
    someone adds reintroduces the hole; escaping at construction means no renderer can."""
    import chipsim.guards.record_content as rc

    row = rc.ScanRow("docs/x.png", FORGERY, "undecodable", "listed", FORGERY)
    assert "\x1b" not in row.owner, "owner is still raw in the data"
    assert "\x1b" not in row.detail, "detail is still raw in the data"
    assert "\n" not in row.detail, "a multi-line detail can still split into report rows"


def test_a_row_disposition_outside_the_two_values_is_refused(tmp_path):
    """`disposition` is one bit spelled as two strings, and the scan's failing-count MATCHES on it.
    A typo would silently stop a row counting as failing while it still printed."""
    import chipsim.guards.record_content as rc

    with pytest.raises(rc.RecordContentScanError, match="neither"):
        rc.ScanRow("docs/x.png", None, "undecodable", "FAILS-HERE")


@pytest.mark.parametrize("broken", ["project", "repo-root"])
def test_the_UNREADABLE_disclosure_does_not_name_the_healthy_file(broken, tmp_path, monkeypatch):
    """r2.28 §11 QG. `registry_state == "unreadable"` is derived from `structural_error`, which is
    set by EITHER declaration file — but the banner hardcoded the repo-root path. With only the
    PROJECT file broken, one report named the project file in its structural-error section and the
    repo-root file in its registry banner, and the banner is the half an operator acts on.

    The existing test happened to corrupt the repo-root file, so it never saw this.
    """
    import chipsim.guards.record_content as rc

    listing = _surface(tmp_path, owners=[rc.THIS_PROJECT])
    target = rc.PROJECT_DECLARATION_FILE if broken == "project" else rc.REPO_DECLARATION_FILE
    healthy = rc.REPO_DECLARATION_FILE if broken == "project" else rc.PROJECT_DECLARATION_FILE
    (tmp_path / target).write_text("declarations: [ unclosed\n")
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    scan = scan_record_content(ScanContext.build(tmp_path, NOTHING_WAIVED))
    assert scan.registry_state == "unreadable"
    text, _code = render_scan(scan)

    banner = [line for line in text.splitlines() if "owner registry: UNREADABLE" in line]
    assert banner, "the disclosure is missing entirely"
    assert healthy not in banner[0], (
        f"the banner names {healthy}, which parsed fine — the operator is sent to repair the "
        f"wrong file while {target} is the one that failed"
    )
    assert target in text, "the report must still name the file that actually failed"


def test_an_EMPTY_owners_list_narrows_to_nothing_and_is_not_an_absent_registry(
    tmp_path, monkeypatch
):
    """The code here is CORRECT and nothing bound it — a test gap, not a defect, and worth saying
    so precisely rather than claiming a fix.

    `if owners is None: return None` distinguishes "no registry yet" from "a registry naming
    nobody". The mutant `if not owners:` collapses them and SURVIVED the full suite: with
    `owners: []`, current code yields `frozenset()` so every path is unowned and unowned FAILS
    here (fail-closed); the mutant yields `None`, so the marker-backed set comes back, other
    projects' paths acquire owners, and under E-03 they fail nobody's gate. One-line data edit, no
    code change, gate goes quiet.

    The existing registry test covers "owners present" and "no `owners:` key" — never the empty
    list, which is the only input that separates the two readings.
    """
    import chipsim.guards.record_content as rc

    theirs = "projects/perturb-seq-eval/theirs.bin"
    _write(tmp_path, theirs, b"\x00\xff\x80\x81 OPAQUE")
    listing = _surface(tmp_path, owners=[]) + [
        "projects/perturb-seq-eval/pyproject.toml",
        theirs,
    ]
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    assert rc.declared_owner_registry(tmp_path) == frozenset(), (
        "an empty `owners:` list is a registry naming NOBODY, not an absent registry"
    )

    scan = scan_record_content(ScanContext.build(tmp_path, NOTHING_WAIVED))
    assert scan.registry_state == "declared", "the registry EXISTS; it is simply empty"

    row = next(r for r in scan.rows if r.path == theirs)
    assert row.owner is None, "the registry narrowed every owner away, so this path is unowned"
    assert row.disposition == "FAILS HERE", "and unowned fails HERE — the fail-closed direction"
    assert scan.exit_code == 2


# --- §12: the surface must be bound to the root it was READ FROM ------------------------------


def test_a_surface_cannot_be_used_against_a_root_it_was_not_read_from(tmp_path_factory):
    """S11-11 / r2.29 signatures-first. `DeclarationSurface.read(root)` DISCARDS `root`, and eight
    public functions then take `root` and `surface` as SEPARATE arguments — so a caller can pass a
    surface read from tree A together with tree B and receive A's verdicts, silently.

    Every verdict in the memo is a snapshot of filesystem reads (`is_file`, `_sha256`,
    `_is_readable`) under a root the key does not mention. E-14's whole thesis is that disagreement
    must be IMPOSSIBLE rather than unlikely, and the frozen object is missing the one field that
    says what it was frozen FROM.

    Unreachable through `ScanContext.build` today — which is why it is a latent hazard rather than a
    live bug, and why the fix is to make the pair unrepresentable rather than to add a check.
    """
    import chipsim.guards.record_content as rc

    a = tmp_path_factory.mktemp("tree_a")
    b = tmp_path_factory.mktemp("tree_b")
    for root in (a, b):
        (root / rc.PROJECT_DECLARATION_FILE).parent.mkdir(parents=True, exist_ok=True)
        (root / rc.REPO_DECLARATION_FILE).parent.mkdir(parents=True, exist_ok=True)
        (root / rc.PROJECT_DECLARATION_FILE).write_text('version: "1"\ndeclarations: []\n')
        (root / rc.REPO_DECLARATION_FILE).write_text('version: "1"\ndeclarations: []\n')

    surface = rc.DeclarationSurface.read(a)
    assert getattr(surface, "root", None) is not None, (
        "the surface does not record which tree it was read from, so nothing can detect a "
        "mismatched (root, surface) pair"
    )
    assert Path(surface.root).resolve() == a.resolve()


def test_a_declaration_surface_cannot_be_constructed_without_saying_what_it_read(tmp_path):
    """S11-8, closed in §12. `DeclarationSurface()` was publicly constructible on all-defaults and
    landed on `registry=None` -> MARKER-BACKED-ONLY: the WIDENING direction, where more paths
    acquire an owner and under E-03 an owned path fails nobody's gate. A real root plus a real
    listing plus a defaulted surface reported MARKER-BACKED ONLY over a repository whose registry
    exists and narrows, and the anti-vacuity refusal never saw it because it validates root and
    paths, not the surface.

    `ScanContext` got `__post_init__` because "the only sanctioned constructor has to be enforced by
    the TYPE rather than by convention". That argument was not carried one class over — and when I
    bound the root in §12 I reintroduced the default myself, to satisfy dataclass field ordering.
    """
    import chipsim.guards.record_content as rc

    with pytest.raises(TypeError):
        rc.DeclarationSurface()

    with pytest.raises(TypeError):
        rc.DeclarationSurface(root=tmp_path)


def test_a_surface_reporting_it_could_not_parse_may_not_also_carry_entries(tmp_path):
    """The stateable invariant: a structural error means NOTHING was read. Carrying entries beside
    one is a surface claiming to have parsed the file it is reporting it could not parse."""
    import chipsim.guards.record_content as rc

    with pytest.raises(rc.RecordContentScanError, match="must declare nothing"):
        rc.DeclarationSurface(
            root=tmp_path,
            entries=(("docs/x.bin", {"path": "docs/x.bin"}, "project"),),
            registry=None,
            structural_error="could not be read as YAML",
        )

    with pytest.raises(rc.RecordContentScanError, match="must declare nothing"):
        rc.DeclarationSurface(
            root=tmp_path,
            entries=(),
            registry=frozenset({"x"}),
            structural_error="could not be read as YAML",
        )


# --- §12.2: whose fault is it? the taxonomy, and the handler that used to get it wrong ----------


def test_a_guard_bug_is_not_reported_as_the_repositorys_declaration_data(tmp_path):
    """r2.29's deciding evidence, and it is worse than the clause states.

    `DeclarationSurface.read` existed to turn declaration problems into a rendered report, and it
    caught the BASE class. MEASURED before the split: a guard bug raised inside `require()` was
    swallowed, became `structural_error`, and was reported as "the declaration data could not be
    parsed" — exit 2, naming a file that parsed perfectly well. A programming error in the guard
    arrived as an accusation against the tree it was scanning.

    `GuardInvariantViolated` is therefore NOT catchable by that handler. It still lands in exit 3
    (there is no fourth state, r2.28) but it says whose fault it is.
    """
    import chipsim.guards.record_content as rc
    from chipsim.guards.errors import DeclarationDataUnusable, GuardInvariantViolated

    for rel in (rc.PROJECT_DECLARATION_FILE, rc.REPO_DECLARATION_FILE):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text('version: "1"\ndeclarations: []\n')

    def boom(_docs):
        raise GuardInvariantViolated("INTERNAL: the guard's own invariant")

    real = rc._entries_from
    rc._entries_from = boom
    try:
        with pytest.raises(GuardInvariantViolated):
            rc.DeclarationSurface.read(tmp_path)
    finally:
        rc._entries_from = real

    # THE OTHER DIRECTION, or this test would pass against "catch nothing": a genuine declaration
    # problem must STILL be converted, because rendering the listing beside the reason is E-13.
    def data_problem(_docs):
        raise DeclarationDataUnusable("the YAML is malformed")

    rc._entries_from = data_problem
    try:
        surface = rc.DeclarationSurface.read(tmp_path)
    finally:
        rc._entries_from = real
    assert surface.structural_error is not None
    assert surface.entries == () and surface.registry is None


def test_each_failure_names_whose_fault_it_is():
    """The taxonomy as a shape check: three classes, one base, and the guard's own defect is not a
    subclass of either caller-facing one — otherwise a handler for those would swallow it again.
    """
    from chipsim.guards import errors

    assert issubclass(errors.ScanNotPerformed, errors.RecordContentScanError)
    assert issubclass(errors.DeclarationDataUnusable, errors.RecordContentScanError)
    assert issubclass(errors.GuardInvariantViolated, errors.RecordContentScanError)

    assert not issubclass(errors.GuardInvariantViolated, errors.DeclarationDataUnusable)
    assert not issubclass(errors.GuardInvariantViolated, errors.ScanNotPerformed)
    assert not issubclass(errors.DeclarationDataUnusable, errors.ScanNotPerformed)
    assert not issubclass(errors.ScanNotPerformed, errors.DeclarationDataUnusable)


def test_the_errors_module_is_a_leaf():
    """It is imported by `repo`, `decoding` and `record_content`, so whichever of them owned it
    became a dependency of the others — which is why the old placement rule ("the exception belongs
    with the layer that RAISES it") was really cycle avoidance wearing a principle's clothes. A leaf
    that imports from the package would reintroduce the cycle it exists to prevent."""
    import ast
    from pathlib import Path as _Path

    from chipsim.guards import errors

    tree = ast.parse(_Path(errors.__file__).read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")

    assert not [m for m in imported if m.startswith("chipsim")], (
        f"errors.py imports from the package: {sorted(imported)} — it is no longer a leaf"
    )


def test_the_invariants_raise_the_guards_own_error_not_a_repository_one():
    """Every `__post_init__` invariant is unreachable unless this module has a bug, so none of them
    may raise a class that blames the repository."""
    import chipsim.guards.record_content as rc
    from chipsim.guards.errors import GuardInvariantViolated

    with pytest.raises(GuardInvariantViolated):
        rc.ScanRow("docs/x.png", None, "undecodable", "FAILS-HERE")

    with pytest.raises(GuardInvariantViolated):
        rc.RecordContentScan(
            root=Path("/r"),
            package=Path("/r/p.py"),
            tracked_count=5,
            failing_count=0,
            rows=(rc.ScanRow("x.bin", None, "undecodable", "FAILS HERE"),),
            declaration_counts=(0, 0, 0),
            defect_count=0,
            submodules=(),
            declaration_files=(rc.PROJECT_DECLARATION_FILE, rc.REPO_DECLARATION_FILE),
            registry_state="declared",
            structural_error=None,
            exit_code=0,
        )


# --- §12.4: "the renderer decides nothing" is now a CHECK, not a claim -------------------------


def test_the_report_module_cannot_read_anything():
    """This is the whole reason the extraction was worth doing.

    "The renderer decides nothing" was a property a reviewer had to verify BY READING, and it had
    already been broken twice while the words stayed true: the exit code was recomputed in the
    renderer for a while, and as late as r2.27 §11 the header's failing-count was still being
    re-derived from a NARROWER partition than the exit code — so a scan with one broken declaration
    printed "failing this gate: 0" beside exit 2.

    A module that cannot open a file cannot decide anything about one. So the property is asserted
    against the IMPORT LIST: `errors` (a leaf) plus the standard library, and nothing that reaches
    the filesystem, git or YAML.
    """
    import ast
    from pathlib import Path as _Path

    from chipsim.guards import report

    tree = ast.parse(_Path(report.__file__).read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
    imported.discard("__future__")

    forbidden = {"subprocess", "yaml", "os", "shutil", "io", "tempfile", "socket", "requests"}
    assert not (imported & forbidden), (
        f"the report module imports {sorted(imported & forbidden)} — it can reach outside the scan "
        "it was handed, and 'the renderer decides nothing' is back to being a claim"
    )

    package_imports = {m for m in imported if m == "chipsim"}
    assert package_imports <= {"chipsim"}, sorted(package_imports)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("chipsim"):
            assert node.module == "chipsim.guards.errors", (
                f"report imports {node.module}; it may only depend on the errors leaf, or the "
                "dependency stops pointing one way"
            )

    # And it must not call the builtins that read, even without an import.
    calls = {
        n.func.id
        for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
    }
    assert "open" not in calls, "the report module calls open()"


def test_the_renderer_returns_the_scans_exit_code_and_counts_verbatim(tmp_path):
    """The behavioural half of the same property, because an import list cannot see arithmetic.

    Both numbers the header reports are FIELDS now, and this asserts the renderer prints them rather
    than recomputing them: a scan whose fields are deliberately inconsistent with a naive recount
    cannot be constructed (the invariant refuses it), so the check is that the printed values equal
    the field values for a scan that CAN exist.
    """
    import chipsim.guards.record_content as rc

    scan = rc.RecordContentScan(
        root=tmp_path,
        package=tmp_path / "pkg.py",
        tracked_count=777,
        failing_count=1,
        rows=(rc.ScanRow("docs/x.bin", None, "undecodable", "FAILS HERE"),),
        declaration_counts=(3, 2, 0),
        defect_count=0,
        submodules=(),
        declaration_files=("a/project.yaml", "b/repo.yaml"),
        registry_state="declared",
        structural_error=None,
        exit_code=2,
    )
    text, code = rc.render_scan(scan)
    header = text.splitlines()[0]

    assert code == scan.exit_code
    assert f"(failing this gate: {scan.failing_count}" in header
    assert f"scanned {scan.tracked_count} tracked files" in header
    # the declaration FILES come from the scan too, so the renderer no longer resolves them
    assert "3 from a/project.yaml" in text
    assert "2 from b/repo.yaml" in text
