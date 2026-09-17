"""E-17: the scan is DATA; rendering is presentation.

Before this, `_render_for_root` computed the verdict and formatted it in one pass, and the exit code
existed nowhere except inside the string it returned. That is not a style complaint — it is why
E-13b happened: no test could assert the exit code cheaply, so twelve mutants survived while every
defect test asserted on a validator's return value instead.
"""

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
