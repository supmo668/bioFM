"""§16 — APPROVE ON EXECUTE for ETL stages.

The principal's standing instruction is "every run should log / save the exact config, always
create new config copies for run, approve on execute". The first half was already built and
working; the second existed for `panel-seal` ONLY, so every stage that WRITES ARTIFACTS ran
unapproved. These bind the half that was added.

What the gate is worth is bounded and the bound is stated in the code: it converts an ACCIDENTAL
run into a DELIBERATE one and makes the difference visible in the journal. It does NOT identify who
approved, and nothing here asserts that it does.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from chipsim import pipeline


def _runs(project_root: Path) -> list[Path]:
    journal = project_root / "journal"
    if not journal.is_dir():
        return []
    return sorted(
        (d for d in journal.iterdir() if d.is_dir() and d.name != "invocations"),
        key=lambda d: d.name,
    )


@pytest.fixture
def snapshot_project(tmp_path, monkeypatch):
    """A project root with a `configs/` tree and the raw snapshot the stage verifies."""
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "env.yaml").write_text("paths:\n  raw: data/raw\n")
    monkeypatch.setenv("CHIPSIM_PROJECT_ROOT", str(tmp_path))
    monkeypatch.setattr(pipeline, "project_root", lambda: tmp_path)
    return tmp_path


def test_an_ETL_stage_with_no_tty_and_no_yes_is_REFUSED(snapshot_project, monkeypatch, capsys):
    """The default posture. A stage that writes artifacts must not run because nobody said no."""
    monkeypatch.setattr(pipeline, "_stdin_is_interactive", lambda: False)
    monkeypatch.setattr(pipeline, "_HANDLERS", dict(pipeline._HANDLERS))
    pipeline._HANDLERS["hash-verify"] = lambda ns: pytest.fail("the stage must not have run")

    code = pipeline.main(["hash-verify", "--dest", str(snapshot_project / "data")])

    assert code == 2
    assert "no approval was given" in capsys.readouterr().err


def test_a_DECLINED_run_still_records_the_configs_it_would_have_used(snapshot_project, monkeypatch):
    """A refusal that leaves no trace only prevents runs; it does not account for them.

    The run record is opened BEFORE the prompt on purpose — the same ordering `panel-seal` uses,
    for the same reason: a declined attempt is exactly what the trail exists to show.
    """
    monkeypatch.setattr(pipeline, "_stdin_is_interactive", lambda: False)
    monkeypatch.setattr(pipeline, "_HANDLERS", dict(pipeline._HANDLERS))
    pipeline._HANDLERS["hash-verify"] = lambda ns: pytest.fail("the stage must not have run")

    assert pipeline.main(["hash-verify", "--dest", str(snapshot_project / "data")]) == 2

    runs = _runs(snapshot_project)
    assert runs, "a declined run must still open a run record"
    declined = runs[-1]
    assert json.loads((declined / "outcome.json").read_text())["status"] == "declined"
    assert not (declined / "approval.json").exists(), "nothing approved it"
    assert (declined / "configs" / "env.yaml").exists(), (
        "the snapshot must be kept, so the record shows what the refused run would have used"
    )


def test_yes_approves_and_is_RECORDED_as_a_flag_not_as_a_human(snapshot_project, monkeypatch):
    """`--yes` is a RECORDED ESCAPE. The record must not let an unattended run read as an answered
    one — an unrecorded escape would be worse than no gate at all."""
    monkeypatch.setattr(pipeline, "_stdin_is_interactive", lambda: False)
    monkeypatch.setattr(pipeline, "_HANDLERS", dict(pipeline._HANDLERS))
    pipeline._HANDLERS["hash-verify"] = lambda ns: 0

    assert pipeline.main(["hash-verify", "--dest", str(snapshot_project / "data"), "--yes"]) == 0

    record = json.loads((_runs(snapshot_project)[-1] / "approval.json").read_text())
    assert record["mode"] == "flag"
    assert record["stdin_was_a_tty"] is False, (
        "the record must say no terminal was attached, so `flag` cannot be read as a human answer"
    )
    assert record["command"] == "hash-verify"


def test_an_interactive_answer_is_recorded_DISTINCTLY_from_the_flag(snapshot_project, monkeypatch):
    """The two approval modes must be distinguishable after the fact, or recording is pointless."""
    monkeypatch.setattr(pipeline, "_stdin_is_interactive", lambda: True)
    monkeypatch.setattr(pipeline, "_read_confirmation", lambda timeout: "run")
    monkeypatch.setattr(pipeline, "_HANDLERS", dict(pipeline._HANDLERS))
    pipeline._HANDLERS["hash-verify"] = lambda ns: 0

    assert pipeline.main(["hash-verify", "--dest", str(snapshot_project / "data")]) == 0

    record = json.loads((_runs(snapshot_project)[-1] / "approval.json").read_text())
    assert record["mode"] == "interactive"
    assert record["stdin_was_a_tty"] is True


def test_a_wrong_answer_at_the_prompt_DECLINES(snapshot_project, monkeypatch):
    """Anything that is not the word collapses to not-approved — including silence and a timeout,
    which `_read_confirmation` already flattens to the same value."""
    monkeypatch.setattr(pipeline, "_stdin_is_interactive", lambda: True)
    monkeypatch.setattr(pipeline, "_read_confirmation", lambda timeout: "yes")
    monkeypatch.setattr(pipeline, "_HANDLERS", dict(pipeline._HANDLERS))
    pipeline._HANDLERS["hash-verify"] = lambda ns: pytest.fail("the stage must not have run")

    assert pipeline.main(["hash-verify", "--dest", str(snapshot_project / "data")]) == 2
    assert json.loads((_runs(snapshot_project)[-1] / "outcome.json").read_text())["status"] == (
        "declined"
    )


# RETIRED 2026-10-22 (principal ruling): `test_the_READ_ONLY_reports_are_NOT_gated` asserted that
# `record-content-report` and `record-content-gate` run ungated. Both are E-21..E-23 commands and
# the union-minus-E-23 reconciliation deliberately did not bring them across (row 61: "do not open
# by repairing the register"). Every parameter of the test named an excluded command, so the test
# retires whole rather than being narrowed. The gating rule it protected is still covered for the
# commands that DO exist by the NON_ETL_SUBCOMMANDS cases above.
def test_t29_approved_by_is_recorded_VERBATIM(snapshot_project, monkeypatch):
    """Done-when 1. Stored exactly as given — never normalised into a known set, because the
    moment the field only accepts recognised values it starts to look like authentication."""
    monkeypatch.setattr(pipeline, "_stdin_is_interactive", lambda: False)
    monkeypatch.setattr(pipeline, "_HANDLERS", dict(pipeline._HANDLERS))
    pipeline._HANDLERS["hash-verify"] = lambda ns: 0

    assert (
        pipeline.main(
            [
                "hash-verify",
                "--dest",
                str(snapshot_project / "data"),
                "--yes",
                "--approved-by",
                "cto",
            ]
        )
        == 0
    )

    record = json.loads((_runs(snapshot_project)[-1] / "approval.json").read_text())
    assert record["approved_by"] == "cto"
    # Additive: the existing contract is untouched by the new field.
    assert record["mode"] == "flag"
    assert record["stdin_was_a_tty"] is False


def test_t29_omitting_the_flag_leaves_the_field_ABSENT_not_defaulted(snapshot_project, monkeypatch):
    """Done-when 2, and the point of the whole task.

    A default — empty string, "unknown", the agent's own address — would recreate exactly the
    ambiguity T29 exists to remove, because every run would then carry a value and none of them
    would mean anything. Absent is the only honest encoding of "nobody said".
    """
    monkeypatch.setattr(pipeline, "_stdin_is_interactive", lambda: False)
    monkeypatch.setattr(pipeline, "_HANDLERS", dict(pipeline._HANDLERS))
    pipeline._HANDLERS["hash-verify"] = lambda ns: 0

    assert pipeline.main(["hash-verify", "--dest", str(snapshot_project / "data"), "--yes"]) == 0

    record = json.loads((_runs(snapshot_project)[-1] / "approval.json").read_text())
    assert "approved_by" not in record, (
        "the key must be ABSENT when nobody supplied it — a defaulted value would make every run "
        "look attributed and none of them actually be"
    )


def test_t29_an_odd_string_is_preserved_rather_than_normalised(snapshot_project, monkeypatch):
    """Verbatim means verbatim. A value the code does not recognise must survive intact, or the
    field is quietly a controlled vocabulary pretending to be a free-text label."""
    monkeypatch.setattr(pipeline, "_stdin_is_interactive", lambda: False)
    monkeypatch.setattr(pipeline, "_HANDLERS", dict(pipeline._HANDLERS))
    pipeline._HANDLERS["hash-verify"] = lambda ns: 0
    odd = "  principal via CTO delegation (r2.38)  "

    assert (
        pipeline.main(
            [
                "hash-verify",
                "--dest",
                str(snapshot_project / "data"),
                "--yes",
                "--approved-by",
                odd,
            ]
        )
        == 0
    )

    record = json.loads((_runs(snapshot_project)[-1] / "approval.json").read_text())
    assert record["approved_by"] == odd, "the value was normalised; it must be stored as given"


def test_t29_is_NEVER_inferred_from_identity_or_from_mode(snapshot_project, monkeypatch):
    """The honesty clause, pinned.

    This file already states the gate "does NOT identify who approved". `approved_by` must not
    erode that: it is a label someone chose to attach, never a derivation. If it were ever filled
    in from `agent-identity` or from the absence of a TTY, an unattended run would start carrying
    an attribution nobody made — the exact false-clean shape this project keeps finding.
    """
    monkeypatch.setattr(pipeline, "_stdin_is_interactive", lambda: True)
    monkeypatch.setattr(pipeline, "_read_confirmation", lambda timeout: "run")
    monkeypatch.setattr(pipeline, "_HANDLERS", dict(pipeline._HANDLERS))
    pipeline._HANDLERS["hash-verify"] = lambda ns: 0

    assert pipeline.main(["hash-verify", "--dest", str(snapshot_project / "data")]) == 0

    record = json.loads((_runs(snapshot_project)[-1] / "approval.json").read_text())
    assert record["mode"] == "interactive"
    assert "approved_by" not in record, (
        "an interactive answer must not be attributed to anyone — the human at the terminal is "
        "unidentified and the record must keep saying so"
    )


def test_t29_the_flag_is_available_on_an_interactive_approval_too(snapshot_project, monkeypatch):
    """Not flag-only. Someone typing the confirmation on another party's instruction can still
    say so, and the two fields stay orthogonal: `mode` is HOW, `approved_by` is WHO."""
    monkeypatch.setattr(pipeline, "_stdin_is_interactive", lambda: True)
    monkeypatch.setattr(pipeline, "_read_confirmation", lambda timeout: "run")
    monkeypatch.setattr(pipeline, "_HANDLERS", dict(pipeline._HANDLERS))
    pipeline._HANDLERS["hash-verify"] = lambda ns: 0

    assert (
        pipeline.main(
            [
                "hash-verify",
                "--dest",
                str(snapshot_project / "data"),
                "--approved-by",
                "principal",
            ]
        )
        == 0
    )

    record = json.loads((_runs(snapshot_project)[-1] / "approval.json").read_text())
    assert record["mode"] == "interactive"
    assert record["approved_by"] == "principal"
