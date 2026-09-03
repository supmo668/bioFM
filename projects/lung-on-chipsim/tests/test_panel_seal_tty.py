"""T7a's TTY gate — Global Constraint (4)'s first technical enforcement.

Global Constraint (4) reserves panel sealing to a human. Until this gate it had
**zero** technical force: it was a stated rule, and a headless agent session
could produce a perfectly valid live seal. `chipsim panel-seal` now refuses to
run without an interactive terminal on stdin.

*** THE LIMIT, STATED AT ITS HONEST SIZE AND NOT ONE STEP FURTHER ***

This gate converts an ACCIDENT into a DELIBERATE CIRCUMVENTION. That is the
whole claim.

It does NOT establish who ran the command, and it does not make the seal an
attestation. The digest remains unkeyed over public content, so it proves the
file is unmodified and never who ratified it. An agent that deliberately
allocates a pty defeats this guard completely, and doing so is neither difficult
nor exotic. Real signing with a human-held key is a v2 decision, deferred.

Any wording that describes this gate as *preventing* an agent from sealing, or
as evidence a human sealed, is an overclaim of exactly the kind the panel seal
already had to have corrected once.
"""

from __future__ import annotations

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
def sealed_fixture(tmp_path: Path) -> Path:
    """A ratified panel copied out of the committed fixtures.

    A COPY, never the live `configs/barrier_panel.yaml`: Global Constraint (4)
    forbids an agent running the seal against the real panel, and a test that
    did so would be the violation it exists to guard.
    """
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

    code = pipeline.main(["panel-seal", "--panel", str(sealed_fixture)])

    assert code == 0
    assert "ratified_panel_sha256" in sealed_fixture.read_text(encoding="utf-8")


def test_a_stdin_without_isatty_is_treated_as_no_tty(
    sealed_fixture: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Fail CLOSED on a stdin that cannot answer the question. A replaced or
    detached stdin lacking `isatty` must refuse, not sail through on an
    AttributeError swallowed somewhere."""
    monkeypatch.setattr(sys, "stdin", object())

    assert pipeline.main(["panel-seal", "--panel", str(sealed_fixture)]) != 0


def test_the_gate_does_not_claim_to_prove_who_sealed() -> None:
    """Honesty clause. The gate raises the cost of an accident; it does not
    authenticate anyone, and no wording may say otherwise."""
    text = Path(pipeline.__file__).read_text(encoding="utf-8").lower()

    for overclaim in (
        "proves a human",
        "proves that a human",
        "guarantees a human",
        "only a human can",
        "prevents an agent",
    ):
        assert overclaim not in text, f"pipeline.py overclaims the TTY gate: {overclaim!r}"
