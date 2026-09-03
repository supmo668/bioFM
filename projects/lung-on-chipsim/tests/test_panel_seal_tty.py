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

import io
import json
import os
import sys
from pathlib import Path

import pytest

from chipsim import pipeline


class _FakeStdin:
    """A stdin that can claim to be a terminal and can answer the E-4 prompt.

    `answer` defaults to "" — NOT to the confirmation. The default used to be
    `"seal\n"`, so a bare `_FakeStdin(tty=True)` silently consented on behalf of
    an absent human. In a module whose entire thesis is failing closed, a test
    double whose default is CONSENT is the wrong polarity: every future test that
    forgets the argument gets a pass through the gate rather than a refusal, and
    a fixture that grants what it is supposed to withhold cannot demonstrate the
    withholding. Tests that want to clear the gate now say so explicitly.
    """

    def __init__(self, tty: bool, answer: str = "") -> None:
        self._tty = tty
        self._answer = answer

    def isatty(self) -> bool:
        return self._tty

    def readline(self) -> str:
        return self._answer


@pytest.fixture(autouse=True)
def _never_journal_into_the_real_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """AUTOUSE. The redirect must not be something a test can decline.

    It was opt-in, carried by the `sealed_fixture` fixture. Three tests in this
    file used a module-level `_sealed_fixture()` helper instead, did not get the
    redirect, and wrote 86 agent-authored `panel-seal` records into the real
    `projects/lung-on-chipsim/journal/invocations/` — the audit trail that is
    Global Constraint (4)'s only mechanical support. A genuine violation differs
    from those entries by an argv path.

    `test_the_fixture_redirects_the_journal_away_from_the_real_tree` asserted the
    redirect was in place, but it could only see the tests that had asked for it;
    the ones that opted out were invisible to it by construction. So the guard is
    autouse now: not because the helper was wrong to exist, but because a
    protection you have to remember to request is one that will eventually not be
    requested, and nothing in the suite could tell you it had happened.
    """
    monkeypatch.setenv("CHIPSIM_PROJECT_ROOT", str(tmp_path))


def _tree_snapshot(root: Path) -> dict[str, bytes]:
    """Every file under `root` EXCEPT the journal, by relative path, with contents.

    Compared against a single file's bytes, this catches three things a byte
    check cannot: a seal that writes and then RESTORES the original bytes, a
    sidecar written alongside the panel, and a temp file left behind. Verified by
    review: a `panel-seal` that sealed, copied the sealed result to
    `panel.sealed.leak`, and restored the original bytes passed every test in
    this file. "The panel's final bytes are unchanged" and "refusing to seal
    wrote nothing" are different claims, and only the first was being made.

    `journal/` is excluded because a refused attempt DOES write there, on
    purpose — the record of an abandoned seal is the thing the trail exists to
    preserve. Excluding it here is not a blind spot: `_journal_records` below
    asserts on it directly, so the two halves of "what may change" are each
    checked, rather than one of them being quietly waived.
    """
    return {
        str(path.relative_to(root)): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and "journal" not in path.relative_to(root).parts
    }


def _journal_records(root: Path) -> list[str]:
    """The invocation records under `root`, by name."""
    invocations = root / "journal" / "invocations"
    return sorted(p.name for p in invocations.glob("*.json")) if invocations.is_dir() else []


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
    """The gate must be a gate, not a wall: the command proceeds when BOTH gates
    are cleared. Otherwise the test above would pass against a command that never
    works.

    "With a TTY" was the old wording and it was false: this stdin also types the
    confirmation, so the test clears two gates and names one. It matters because
    the test then fails for reasons unrelated to the TTY — deleting `.strip()`
    from the comparison breaks THIS test, which reads as a TTY regression.
    """
    monkeypatch.setattr(sys, "stdin", _FakeStdin(tty=True, answer="seal\n"))

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


# --- E-4: the confirmation read -------------------------------------------


def test_confirmation_refusal_writes_nothing(sealed_fixture, monkeypatch, capsys):
    """A TTY proves a terminal is attached, never that anyone is at it.

    A pty allocated by a wrapper satisfies isatty() with nobody present, so the
    read is what makes the act deliberate. On refusal NOTHING under the project
    root may change — see `_tree_snapshot` for why the panel's own bytes are not
    a sufficient check.
    """
    from chipsim import pipeline

    before = _tree_snapshot(sealed_fixture.parent)
    journal_before = _journal_records(sealed_fixture.parent)

    monkeypatch.setattr(pipeline, "_stdin_is_interactive", lambda: True)
    monkeypatch.setattr("sys.stdin", io.StringIO("no thanks\n"))

    rc = pipeline.main(["panel-seal", "--panel", str(sealed_fixture)])

    assert rc == 2, "a refused confirmation must exit non-zero"
    assert _tree_snapshot(sealed_fixture.parent) == before, (
        "refusing to seal must write nothing outside the journal"
    )
    # ...and the refusal IS journalled. The stderr message says so, so this
    # asserts the message is true rather than merely well-intentioned: an
    # abandoned seal attempt that left no trace would make the command's own
    # account of itself false.
    assert len(_journal_records(sealed_fixture.parent)) == len(journal_before) + 1, (
        "the refused attempt left no record, contradicting what the refusal prints"
    )
    # WHICH gate refused. Both gates return 2, so without this the test passes
    # when the TTY gate refuses first — verified by review: deleting the
    # `_stdin_is_interactive` patch above left this test green while never
    # reaching the confirmation read it is named for.
    assert "confirmation not given" in capsys.readouterr().err


def test_confirmation_accepted_seals(sealed_fixture, monkeypatch):
    """Positive control — the gate must not block the sanctioned path."""
    import yaml

    from chipsim import pipeline
    from chipsim.harmonize.pgp_label import panel_digest

    before = sealed_fixture.read_text(encoding="utf-8")
    monkeypatch.setattr(pipeline, "_stdin_is_interactive", lambda: True)
    monkeypatch.setattr("sys.stdin", io.StringIO("seal\n"))

    rc = pipeline.main(["panel-seal", "--panel", str(sealed_fixture)])
    after = sealed_fixture.read_text(encoding="utf-8")

    assert rc == 0
    # NOT `"ratified_panel_sha256" in after`. The committed fixture already
    # carries that key, so the substring check was satisfied by an untouched
    # file: a `panel-seal` that read the existing digest, printed it and returned
    # 0 without calling `seal_panel` at all passed this test. That is a verbatim
    # regression of a defect the sibling TTY test's own comment records as
    # already fixed once — which is why the corrected form is written out here
    # rather than assumed to be inherited.
    assert after != before, "panel-seal exited 0 without rewriting the digest"
    doc = yaml.safe_load(after)
    assert doc["ratified_panel_sha256"] == panel_digest(doc, sealed_fixture)


def test_the_confirmation_is_case_insensitive(sealed_fixture, monkeypatch):
    """`SEAL` typed by a human with caps lock on must work.

    The comparison lowercases, and nothing tested it — dropping `.lower()` was a
    silent survivor. Low stakes on its own, but the failure mode is a human who
    typed the right word being told they did not confirm.
    """
    from chipsim import pipeline

    before = sealed_fixture.read_text(encoding="utf-8")
    monkeypatch.setattr(pipeline, "_stdin_is_interactive", lambda: True)
    monkeypatch.setattr("sys.stdin", io.StringIO("  SEAL  \n"))

    assert pipeline.main(["panel-seal", "--panel", str(sealed_fixture)]) == 0
    assert sealed_fixture.read_text(encoding="utf-8") != before


def test_empty_stdin_is_a_refusal_not_a_seal(sealed_fixture, monkeypatch, capsys):
    """EOF on stdin — a closed pipe, a killed parent — must refuse.

    Reading '' and treating it as consent is the fail-open form of this gate.
    """
    from chipsim import pipeline

    before = _tree_snapshot(sealed_fixture.parent)
    monkeypatch.setattr(pipeline, "_stdin_is_interactive", lambda: True)
    monkeypatch.setattr("sys.stdin", io.StringIO(""))

    assert pipeline.main(["panel-seal", "--panel", str(sealed_fixture)]) == 2
    assert _tree_snapshot(sealed_fixture.parent) == before
    assert "confirmation not given" in capsys.readouterr().err


@pytest.mark.parametrize("boom", [KeyboardInterrupt, OSError])
def test_an_interrupted_or_failed_read_is_a_refusal(sealed_fixture, monkeypatch, boom):
    """Ctrl-C at the prompt must not seal.

    The read's exception handler returns "" and that was never tested: mutating
    it to return "seal" survived the whole suite. Someone pressing Ctrl-C is
    withdrawing consent in the most explicit way available to them, and it was
    one character away from meaning the opposite.
    """
    from chipsim import pipeline

    class _Exploding:
        def isatty(self) -> bool:
            return True

        def readline(self) -> str:
            raise boom

    before = _tree_snapshot(sealed_fixture.parent)
    monkeypatch.setattr(pipeline, "_stdin_is_interactive", lambda: True)
    monkeypatch.setattr(sys, "stdin", _Exploding())

    assert pipeline.main(["panel-seal", "--panel", str(sealed_fixture)]) == 2
    assert _tree_snapshot(sealed_fixture.parent) == before


# --- E-4 hardening: the prompt, the timeout, and the refusal's honesty --------


def test_the_prompt_goes_to_stderr_so_a_redirect_cannot_swallow_it(
    sealed_fixture: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """`panel-seal > log.txt` must still show the human the question.

    On stdout the prompt lands in the redirect file while the command sits
    waiting on a read the operator cannot see they owe it. That presents as a
    hang — and a hang is the thing someone "fixes" by piping `yes seal` into it,
    which is precisely the deliberate circumvention the gate is here to make
    someone choose rather than stumble into.
    """
    monkeypatch.setattr(sys, "stdin", _FakeStdin(tty=True, answer="no\n"))

    pipeline.main(["panel-seal", "--panel", str(sealed_fixture)])

    captured = capsys.readouterr()
    assert "Type 'seal' to continue" in captured.err
    assert "Type 'seal' to continue" not in captured.out


def test_the_refusal_does_not_claim_nothing_was_written(
    sealed_fixture: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """An abandoned seal attempt IS recorded. The message must not deny it.

    The refusal used to end "Nothing was written." — false, because the
    invocation is journalled before the handler is reached, deliberately: an
    abandoned attempt is exactly what the trail exists to show. The message must
    say what did not change (the panel) without denying what did (the record).
    """
    monkeypatch.setattr(sys, "stdin", _FakeStdin(tty=True, answer="no\n"))
    before = sealed_fixture.read_text(encoding="utf-8")

    code = pipeline.main(["panel-seal", "--panel", str(sealed_fixture)])

    assert code == 2
    assert sealed_fixture.read_text(encoding="utf-8") == before
    err = capsys.readouterr().err
    assert "Nothing was written" not in err, "the refusal denies the journal record it just created"
    assert "panel was NOT modified" in err
    assert "journal" in err.lower()


def test_confirmation_times_out_rather_than_waiting_forever() -> None:
    """No answer is not consent — and it must not be an indefinite wait either.

    A bare `readline()` on a real fd blocks until something arrives. An
    unattended invocation with a pty and nobody at it (a CI step, a wrapper that
    left stdin open) then hangs indefinitely instead of refusing. The timeout is
    what turns that into a clean fail-closed refusal.
    """
    read_fd, write_fd = os.pipe()
    try:
        with os.fdopen(read_fd, "r") as empty_stdin:
            real_stdin = sys.stdin
            sys.stdin = empty_stdin  # type: ignore[assignment]
            try:
                # Nothing is ever written to the write end.
                answer = pipeline._read_confirmation(0.05)
            finally:
                sys.stdin = real_stdin
    finally:
        os.close(write_fd)

    assert answer == "", "a timed-out prompt must read as not-confirmed"


def test_a_stdin_with_no_fileno_is_read_not_refused() -> None:
    """Fail-closed belongs on the timeout, NOT on unpollable stdin.

    `select` cannot poll an in-memory buffer, and raises three different
    exception types for the three ways it can fail to (ValueError, OSError,
    TypeError). Refusing in that case would reject every non-fd stdin to guard
    against a kernel block that cannot happen to an object with no fd — and
    missing TypeError specifically crashed the command with a traceback at the
    exact moment a human was being asked to confirm.
    """
    for fake in (io.StringIO("seal\n"), _FakeStdin(tty=True, answer="seal\n")):
        real_stdin = sys.stdin
        sys.stdin = fake  # type: ignore[assignment]
        try:
            assert pipeline._read_confirmation(30.0).strip() == "seal", (
                f"{type(fake).__name__} stdin was refused instead of read"
            )
        finally:
            sys.stdin = real_stdin


def test_no_source_claims_that_deleting_the_seal_line_bypasses_the_check() -> None:
    """A stale caveat that understates a protection is still a false statement.

    `load_ratified_panel` refuses a ratified panel carrying no seal, so deleting
    the line is a refusal, not a bypass. The claim was true when written and
    survived the fix that falsified it. Pinned because the next reader has no way
    to tell which half of a self-contradicting module to believe.
    """
    root = Path(__file__).resolve().parents[1] / "chipsim"
    # An EXACT match with no exemption clause. The first draft of this test
    # excused any file also containing "used to end", so the retraction could
    # shelter a re-added claim in the same file — the same loose-matcher bug this
    # suite caught once already. The retraction now paraphrases instead of
    # quoting, which lets the search stay literal and unconditional.
    offenders = [
        path
        for path in root.rglob("*.py")
        if "bypasses the check" in path.read_text(encoding="utf-8")
    ]
    assert not offenders, f"stale seal-bypass claim in: {[str(p) for p in offenders]}"
