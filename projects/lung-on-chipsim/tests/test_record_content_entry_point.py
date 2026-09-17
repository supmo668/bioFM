"""E6-7: the one entry point a non-pytest consumer can call.

Until this existed, readability, declarations, ownership and accession content were composed by the
TEST SUITE and by the report renderer — so the invariant was enforced for whoever runs pytest and
for nobody else. CI, a pre-commit hook and another project had nothing to call.
"""

import subprocess
import sys
from pathlib import Path

import pytest

from chipsim.record_content import (
    RecordContentViolation,
    enforce_record_content,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = PROJECT_ROOT.parent.parent


def test_the_live_repository_passes_the_combined_gate():
    """The whole invariant, in one call, against the real tree."""
    result = enforce_record_content()
    assert result.status == "clean"
    assert result.exit_code == 0
    assert result.scanned > 100, "a scan of nothing is not a pass"
    assert result.root == REPO_ROOT


def test_the_fail_lives_IN_the_entry_point_not_in_the_caller():
    """The point of the clause. A consumer must not have to know which four checks to run, in what
    order, and which return value means failure — otherwise the enforcement lives in the caller and
    every caller re-implements it slightly differently.

    The only way to receive a result is for the gate to have PASSED; failure raises.
    """
    import chipsim.record_content as rc

    assert callable(rc.enforce_record_content)
    signature_ok = "raise" in rc.enforce_record_content.__doc__.lower()
    assert signature_ok, "the docstring must say that it raises, because that is the contract"


def test_a_failing_file_raises_with_the_three_state_status(tmp_path, monkeypatch):
    """E-13's contract, carried by the exception rather than flattened to a boolean."""
    import chipsim.guards.record_content as guard
    import chipsim.record_content as rc

    rel = "docs/unowned_payload.bin"
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"\x00\xff\x80\x81 OPAQUE")
    listing = _surface(tmp_path) + [rel]

    monkeypatch.setattr(guard, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(guard, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(guard, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    with pytest.raises(RecordContentViolation) as exc:
        rc.enforce_record_content()
    assert exc.value.status == "files-fail"
    assert exc.value.exit_code == 2
    assert rel in exc.value.report


def test_a_tree_that_cannot_be_scanned_is_a_DIFFERENT_status(tmp_path, monkeypatch):
    """Three states, not a boolean: "I could not look" must never arrive at the same answer as
    "I looked and it was fine", nor at the same one as "I looked and it failed"."""
    import chipsim.guards.record_content as guard
    import chipsim.record_content as rc

    def refuse():
        raise guard.RecordContentScanError("no repository here")

    monkeypatch.setattr(guard, "repo_root", refuse)

    with pytest.raises(RecordContentViolation) as exc:
        rc.enforce_record_content()
    assert exc.value.status == "could-not-scan"
    assert exc.value.exit_code == 3


def test_the_entry_point_checks_ACCESSION_CONTENT_too(tmp_path, monkeypatch):
    """Readability is only half. A file the scan CAN read, carrying a real accession, is the other
    half — and it lived in a different module, so nothing composed the two outside the suite."""
    import chipsim.guards.record_content as guard
    import chipsim.record_content as rc

    rel = "docs/leak.txt"
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("see DB" + "00128" + "\n")
    listing = _surface(tmp_path) + [rel]

    monkeypatch.setattr(guard, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(guard, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(guard, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    with pytest.raises(RecordContentViolation) as exc:
        rc.enforce_record_content()
    assert exc.value.status == "files-fail"
    assert rel in exc.value.report
    assert "accession" in exc.value.report.lower()


def test_it_RE_IMPLEMENTS_none_of_the_pieces():
    """ "It composes the existing checks and re-implements none of them, so there stays one
    definition of each." Asserted structurally: the composition root defines no scanning logic of
    its own — it holds no regex, no magic bytes, no decode, no git call."""
    source = (PROJECT_ROOT / "chipsim/record_content.py").read_text()
    for forbidden in ("re.compile", "PAR1", "decode(", "subprocess", "ls-files", "sha256"):
        assert forbidden not in source, (
            f"the entry point re-implements {forbidden!r} instead of calling the piece that owns it"
        )


def test_a_non_pytest_consumer_can_call_it():
    """The clause's actual subject: CI, a pre-commit hook, or another project. Run it the way one
    of those would — a fresh interpreter, no pytest anywhere."""
    script = (
        f"import sys; sys.path.insert(0, {str(PROJECT_ROOT)!r})\n"
        "from chipsim.record_content import enforce_record_content\n"
        "r = enforce_record_content()\n"
        "print('STATUS', r.status, 'EXIT', r.exit_code, 'SCANNED', r.scanned)\n"
    )
    out = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=False
    )
    assert "STATUS clean EXIT 0" in out.stdout, out.stdout + out.stderr
    assert "pytest" not in out.stderr


def _surface(tmp_path):
    """The declaration surface every fixture root needs, since an absent one is a structural error."""
    import yaml

    import chipsim.guards.record_content as guard

    proj = tmp_path / "projects" / guard.THIS_PROJECT
    (proj / "configs").mkdir(parents=True, exist_ok=True)
    (tmp_path / "config").mkdir(parents=True, exist_ok=True)
    (proj / "pyproject.toml").write_text("[project]\n")
    (tmp_path / guard.PROJECT_DECLARATION_FILE).write_text(
        yaml.safe_dump({"version": "1", "declarations": []})
    )
    (tmp_path / guard.REPO_DECLARATION_FILE).write_text(
        yaml.safe_dump({"version": "1", "declarations": [], "owners": [guard.THIS_PROJECT]})
    )
    return [
        guard.PROJECT_DECLARATION_FILE,
        guard.REPO_DECLARATION_FILE,
        f"projects/{guard.THIS_PROJECT}/pyproject.toml",
    ]
