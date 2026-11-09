"""The CLI route to both scaffold writers — the route the renames actually changed.

Why this file exists. `chipsim/pipeline.py` holds two function-local imports that bind the
scaffold path AND the writer for each command. Those two lines are the ones the 2026-11-08
rename touched, and measured before this file existed: **no test reached either of them.**
The suite was 911 green while a planted crossed-wiring defect in those exact lines produced
zero additional failures, because every other test calls the writers directly on their
modules and bypasses `pipeline.py`.

So the rename was green and UNVERIFIED on its only live call sites. "I cannot test it" is
not "it is fixed." The gap was backstopped only by `ty` going 25 -> 26 diagnostics, which
is detectable solely by someone comparing counts against a non-zero baseline.

Each test below asserts the command's CONTENT and its PATH, because either alone passes
under a crossed wiring: with the writer crossed but the path right, the content is wrong;
with the path crossed but the writer right, the content is right and the destination is not.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from chipsim import pipeline
from chipsim.transport._s6 import S6_FORBIDDEN_RELPATHS
from chipsim.transport.prior import (
    PRIOR_NAMES,
    PRIOR_SCAFFOLD_RELPATH,
    TransportPriorTemplateError,
)
from chipsim.transport.theta import (
    THETA_ROOT,
    THETA_SCAFFOLD_RELPATH,
    ThetaTemplateError,
)

#: Either writer may raise; both refusals carry the same 'human-owned' wording.
REFUSALS = (ThetaTemplateError, TransportPriorTemplateError)


def test_the_two_scaffold_commands_are_wired_to_their_own_handlers():
    """Dispatch-table wiring, asserted by identity rather than by behaviour."""
    assert pipeline._HANDLERS["theta-scaffold"] is pipeline._cmd_theta_scaffold
    assert pipeline._HANDLERS["transport-prior-scaffold"] is pipeline._cmd_transport_prior_scaffold


def test_theta_scaffold_cli_writes_theta_content(tmp_path: Path):
    out = tmp_path / "t.yaml"
    assert pipeline.main(["theta-scaffold", "--out", str(out)]) == 0
    doc = yaml.safe_load(out.read_text())
    # CONTENT: the theta root, not the prior's two entry names.
    assert THETA_ROOT in doc, f"theta-scaffold wrote {sorted(doc)} — the wrong writer ran"
    assert not any(name in doc for name in PRIOR_NAMES)


def test_transport_prior_scaffold_cli_writes_prior_content(tmp_path: Path):
    out = tmp_path / "p.yaml"
    assert pipeline.main(["transport-prior-scaffold", "--out", str(out)]) == 0
    doc = yaml.safe_load(out.read_text())
    assert tuple(doc) == PRIOR_NAMES, f"wrote {sorted(doc)} — the wrong writer ran"
    assert THETA_ROOT not in doc


def test_each_command_defaults_to_its_own_scaffold_path(tmp_path: Path, monkeypatch, capsys):
    """The PATH half. A crossed path constant leaves the content correct and the file wrong.

    `project_root` is patched so nothing is written into the tracked tree.
    """
    monkeypatch.setattr(pipeline, "project_root", lambda: tmp_path)
    assert pipeline.main(["theta-scaffold"]) == 0
    assert (tmp_path / THETA_SCAFFOLD_RELPATH).is_file()
    assert not (tmp_path / PRIOR_SCAFFOLD_RELPATH).exists()

    assert pipeline.main(["transport-prior-scaffold"]) == 0
    assert (tmp_path / PRIOR_SCAFFOLD_RELPATH).is_file()
    capsys.readouterr()


@pytest.mark.parametrize("command", ["theta-scaffold", "transport-prior-scaffold"])
@pytest.mark.parametrize("relpath", [p.as_posix() for p in S6_FORBIDDEN_RELPATHS])
def test_neither_command_can_create_an_s6_forbidden_path(command, relpath, tmp_path: Path):
    """The S6 absence guard, through the CLI, for BOTH writers.

    `prior.write_scaffold` had NO S6 refusal until 2026-11-08 while theta's had one, so
    `transport-prior-scaffold --out configs/theta_priors.yaml` created the human-owned file
    whose absence IS the enforcement of "no coding agent writes a biological number" —
    measured, 766 bytes, exit 0. The parametrisation is the point: the guard is asserted for
    every writer and every forbidden path, so a third writer cannot inherit the old asymmetry.
    """
    target = tmp_path / relpath
    with pytest.raises(REFUSALS) as excinfo:
        pipeline.main([command, "--out", str(target)])
    assert "human-owned" in str(excinfo.value)
    assert not target.exists(), f"{command} created {relpath}"


@pytest.mark.parametrize("command", ["theta-scaffold", "transport-prior-scaffold"])
def test_neither_command_is_fooled_by_a_miscased_forbidden_path(command, tmp_path: Path):
    """APFS is case-insensitive, so `configs/Theta_Priors.yaml` is the forbidden inode.

    A case-SENSITIVE comparison skipped the refusal on macOS and fired on a case-sensitive
    Linux CI — a guard whose verdict depends on the platform.
    """
    target = tmp_path / "configs" / "Theta_Priors.yaml"
    with pytest.raises(REFUSALS):
        pipeline.main([command, "--out", str(target)])
    assert not target.exists()
