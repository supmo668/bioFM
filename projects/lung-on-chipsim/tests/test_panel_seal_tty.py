"""T7a's TTY gate — Global Constraint (4)'s first technical enforcement.

Global Constraint (4) reserves panel sealing to a human. Until this gate it had
**zero** technical force: it was a stated rule, and a headless agent session
could produce a perfectly valid live seal. `chipsim panel-seal` now refuses to
run without an interactive terminal on stdin.

*** THE LIMIT, STATED AT ITS HONEST SIZE AND NOT ONE STEP FURTHER ***

This gate converts an ACCIDENT into a DELIBERATE CIRCUMVENTION. That is the
whole claim.

It does NOT establish who ran the command, and it does not make the seal an
attestation. The digest remains unkeyed over public content, so it DETECTS a
later edit and never says who ratified it — it does not establish the file is
unmodified, since anything able to write the panel can recompute the digest. An agent that deliberately
allocates a pty defeats this guard completely, and doing so is neither difficult
nor exotic. Real signing with a human-held key is a v2 decision, deferred.

Any wording that describes this gate as *preventing* an agent from sealing, or
as evidence a human sealed, is an overclaim of exactly the kind the panel seal
already had to have corrected once.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

from chipsim import pipeline


class _FakeStdin:
    def __init__(self, tty: bool) -> None:
        self._tty = tty

    def isatty(self) -> bool:
        return self._tty


@pytest.fixture
def sealed_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A ratified panel copied out of the committed fixtures.

    A COPY, never the live `configs/barrier_panel.yaml`: Global Constraint (4)
    forbids an agent running the seal against the real panel, and a test that
    did so would be the violation it exists to guard.

    `CHIPSIM_PROJECT_ROOT` is redirected for the same reason, one level down.
    `pipeline.main` journals every `panel-seal` INVOCATION, and without this the
    tests wrote agent-authored `panel-seal` records into the real
    `projects/lung-on-chipsim/journal/invocations/` — polluting the very audit
    trail that is Constraint (4)'s mechanical support, with entries a genuine
    violation differs from only by an argv path. The original fixture reasoned
    carefully about not touching the live panel and missed the journal side of
    the same constraint.
    """
    monkeypatch.setenv("CHIPSIM_PROJECT_ROOT", str(tmp_path))
    source = Path(__file__).resolve().parent / "fixtures" / "barrier_panel_ratified.yaml"
    target = tmp_path / "barrier_panel.yaml"
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    return target


def test_panel_seal_refuses_without_a_tty(
    sealed_fixture: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    """No TTY on stdin → non-zero exit. This is the enforcement itself."""
    monkeypatch.setattr(sys, "stdin", _FakeStdin(tty=False))

    code = pipeline.main(["panel-seal", "--panel", str(sealed_fixture)])

    assert code != 0, "panel-seal ran without an interactive terminal"
    assert "terminal" in capsys.readouterr().err.lower()


def test_panel_seal_writes_nothing_when_it_refuses(
    sealed_fixture: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """'Exit non-zero' is not enough on its own — it must write NOTHING. A
    refusal that still stamped a digest would hand back the seal it declined to
    grant."""
    before = sealed_fixture.read_text(encoding="utf-8")
    monkeypatch.setattr(sys, "stdin", _FakeStdin(tty=False))

    pipeline.main(["panel-seal", "--panel", str(sealed_fixture)])

    assert sealed_fixture.read_text(encoding="utf-8") == before, (
        "panel-seal modified the panel while refusing to run"
    )


def test_panel_seal_proceeds_past_the_gate_with_a_tty(
    sealed_fixture: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The gate must be a gate, not a wall: with a TTY the command proceeds.
    Otherwise the test above would pass against a command that never works."""
    monkeypatch.setattr(sys, "stdin", _FakeStdin(tty=True))

    before = sealed_fixture.read_text(encoding="utf-8")
    code = pipeline.main(["panel-seal", "--panel", str(sealed_fixture)])
    after = sealed_fixture.read_text(encoding="utf-8")

    assert code == 0
    # Assert the seal was RECOMPUTED, not merely that the word is present — the
    # committed fixture already carries a `ratified_panel_sha256`, so the bare
    # substring check passed against a `seal_panel` that did nothing.
    assert after != before, "panel-seal exited 0 without rewriting the digest"
    import yaml

    from chipsim.harmonize.pgp_label import panel_digest

    doc = yaml.safe_load(after)
    assert doc["ratified_panel_sha256"] == panel_digest(doc, sealed_fixture)


def test_a_stdin_without_isatty_is_treated_as_no_tty(
    sealed_fixture: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Fail CLOSED on a stdin that cannot answer the question. A replaced or
    detached stdin lacking `isatty` must refuse, not sail through on an
    AttributeError swallowed somewhere."""
    monkeypatch.setattr(sys, "stdin", object())

    assert pipeline.main(["panel-seal", "--panel", str(sealed_fixture)]) != 0


def test_the_gate_states_its_limit_positively(sealed_fixture: Path) -> None:
    """POSITIVE assertion, replacing a blocklist that was tuned to pass.

    The blocklist form was theatre: a one-word paraphrase ("ensures a human is
    present", "impossible for an agent to seal headlessly") slipped all five
    literals and the suite stayed green. Its list was also chosen so the NEGATED
    forms already in `pipeline.py` would not match — i.e. tuned to pass rather
    than to detect.

    The negative check now lives where it is already done properly:
    `test_no_wording_claims_the_journal_authenticates_anyone` in
    `test_journal.py` scans `pipeline.py` with regexes, a preceding-negation
    window, and an anti-vacuity `inspected > 0` guard. This test asserts the
    complement — that the sanctioned limit is actually STATED, so deleting the
    caveat fails rather than passing quietly.
    """
    text = Path(pipeline.__file__).read_text(encoding="utf-8")

    assert "deliberate circumvention" in text, (
        "the TTY gate's stated limit was removed from pipeline.py"
    )
    assert "does NOT establish who is running the command" in text, (
        "the refusal message no longer disclaims authorship"
    )


def test_a_refused_headless_seal_is_still_journalled_as_an_invocation(
    sealed_fixture: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`record_invocation` runs BEFORE the gate, deliberately: a refused attempt
    is exactly what the Constraint (4) trail should show. Moving the gate ahead
    of the journalling would look like a tidy-up and would make headless seal
    ATTEMPTS invisible, with nothing failing."""
    monkeypatch.setattr(sys, "stdin", _FakeStdin(tty=False))

    assert pipeline.main(["panel-seal", "--panel", str(sealed_fixture)]) != 0

    records = list((tmp_path / "journal" / "invocations").glob("*panel-seal.json"))
    assert len(records) == 1, "a refused headless seal left no invocation record"
    assert json.loads(records[0].read_text())["record_type"] == "invocation"


def test_the_fixture_redirects_the_journal_away_from_the_real_tree(
    sealed_fixture: Path, tmp_path: Path
) -> None:
    """Guards the fixture's redirect directly, without re-invoking pytest.

    An earlier version of this guard shelled out to pytest on this very file,
    which re-ran itself — infinite recursion. Asserting on the redirect itself
    is both correct and terminating.
    """
    assert os.environ["CHIPSIM_PROJECT_ROOT"] == str(tmp_path)
    assert Path(pipeline.project_root()) == tmp_path, (
        "panel-seal would journal into the REAL project tree — Constraint (4)'s "
        "audit trail must not carry test-authored entries"
    )
