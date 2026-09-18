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


@pytest.mark.parametrize("command", ["record-content-report", "record-content-gate"])
def test_the_READ_ONLY_reports_are_NOT_gated(command, snapshot_project, monkeypatch):
    """A gate in front of the quality-gate commands is how a control gets switched off.

    These read and report; they write no artifact. If approving them were required, every gated
    boundary in this project would need a terminal — so the first person in a hurry would remove
    the gate entirely, and that is a worse outcome than not gating a read.
    """
    monkeypatch.setattr(pipeline, "_stdin_is_interactive", lambda: False)
    monkeypatch.setattr(pipeline, "_HANDLERS", dict(pipeline._HANDLERS))
    ran = {}
    pipeline._HANDLERS[command] = lambda ns: ran.setdefault("yes", True) and 0

    pipeline.main([command])

    assert ran.get("yes"), f"{command} must not require approval"
