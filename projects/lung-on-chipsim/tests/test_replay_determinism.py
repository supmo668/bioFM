"""The PoC form of the replay test — build-plan S12 (r2.7).

*** WHICH REPLAY TEST THIS IS. SAY IT, DO NOT ASSUME IT. ***

CONTEXT.md defines "the replay test" as TWO tests at two rungs, and they must
never be conflated:

  PoC form (v0+v1)  same config + same seed reproduces the same scores exactly.
  v3 form           re-run a kept diff from the journal + seed and reproduce the
                    trajectory exactly — a test OF THE AGENT EXPLORATION LOOP.

This file is the **PoC form**. The v3 form is **not applicable** to the PoC,
which runs no exploration loop and therefore produces no kept diff and no veto
state; its absence is not a defect and nothing here claims to close it.

*** WHAT "SCORES" MEANS HERE, STATED PLAINLY RATHER THAN GLOSSED ***

The PoC form is specified over *scores*. **This build has no scores.** There is
no model, no head and no scorer in the plan's M0 slice: `chipsim/heads/` and
`chipsim/uncertainty/` are empty, and no task in the build plan produces a
score. So the literal PoC form is **not yet executable**, and a test named for
scores that actually compared something else would be the exact defect S12 was
created to fix — a control that cannot fail for the reason it exists.

What this file therefore tests is the strongest true form available now: the
same config + the same seed reproduces the **persisted ETL artifact** byte for
byte. That is a real determinism control over the whole parse → canonicalize →
persist path, including the rdkit InChIKey computation and the parquet encoding
that everything downstream is sha256'd against.

Its limit, stated so no reader over-reads it: **the seed does not currently
influence any of this.** Nothing in the PoC's code path consumes a seed yet, so
these tests lock determinism and pin the seed's RECORDING, but they do not yet
demonstrate seed-SENSITIVITY. When a scorer lands, the PoC form must be
re-pointed at scores and this limit removed. Until then, describing the PoC
replay test as "closed" would be an overclaim.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import yaml

from chipsim.harmonize.ids import add_canonical_identity
from chipsim.ingest.drugbank_snapshot import load_compounds, write_compounds
from chipsim.journal import read_manifest, start_run

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = PROJECT_ROOT / "tests" / "fixtures" / "snapshot"


def _seeded_project(tmp_path: Path, seed: int) -> Path:
    """A project root whose config carries `seed`."""
    root = tmp_path / f"project-{seed}"
    (root / "configs").mkdir(parents=True)
    (root / "configs" / "env.yaml").write_text(
        yaml.safe_dump({"stage": "test", "seed": seed})
    )
    return root


def _run_once(project_root: Path, run_id: str) -> tuple[str, dict]:
    """One full run: open a journal record, compute, persist, digest the bytes.

    The artifact is written OUTSIDE the run directory. Run directories are
    immutable and atomically complete-or-absent (A&D §4.4a-ii, `start_run`), so
    dropping outputs into the audit record would both contradict that model and
    model the wrong pattern for whoever writes the next pipeline stage.
    """
    run_dir = start_run("chipsim write", project_root, run_id=run_id)
    frame = add_canonical_identity(load_compounds(SNAPSHOT_DIR, min_rows=0))
    out = project_root / f"{run_id}-compounds.parquet"
    write_compounds(frame, out)
    return hashlib.sha256(out.read_bytes()).hexdigest(), read_manifest(run_dir)


def test_same_config_and_seed_reproduce_byte_identical_output(tmp_path: Path) -> None:
    """The PoC form, at the scope that exists: two runs of ONE config and ONE
    seed produce a byte-identical artifact.

    Byte-identical, not merely equal-valued: everything downstream is sha256'd
    against these bytes, so a frame that compares equal while serializing
    differently still breaks every digest that quotes it.
    """
    project = _seeded_project(tmp_path, 20260903)

    first, first_manifest = _run_once(project, "run-a")
    second, second_manifest = _run_once(project, "run-b")

    assert first == second, (
        "two runs of the same config and seed produced different bytes — the "
        "PoC replay control has failed for the reason it exists"
    )
    # And both records agree on the seed that was in force.
    assert first_manifest["environment"]["seeds"]["resolved"] == 20260903
    assert second_manifest["environment"]["seeds"]["resolved"] == 20260903


def test_the_two_runs_are_separate_records_not_one_reused(tmp_path: Path) -> None:
    """Guards the test above from passing vacuously. If both halves resolved to
    the same run directory, it would be comparing a file with itself and could
    never fail."""
    project = _seeded_project(tmp_path, 7)

    _run_once(project, "run-a")
    _run_once(project, "run-b")

    records = sorted(p.name for p in (project / "journal").iterdir() if p.is_dir())
    assert records == ["run-a", "run-b"]


def test_the_determinism_control_can_actually_fail(tmp_path: Path) -> None:
    """A determinism assertion that cannot distinguish different inputs proves
    nothing. This shows the comparison has teeth: a genuinely different frame
    produces a different digest through the same persist path."""
    project = _seeded_project(tmp_path, 11)

    baseline, _ = _run_once(project, "run-a")

    start_run("chipsim write", project, run_id="run-mutated")
    frame = add_canonical_identity(load_compounds(SNAPSHOT_DIR, min_rows=0)).iloc[:-1]
    out = project / "run-mutated-compounds.parquet"
    write_compounds(frame, out)
    mutated = hashlib.sha256(out.read_bytes()).hexdigest()

    assert mutated != baseline, (
        "dropping a row did not change the digest — the comparison is not "
        "actually sensitive to the data and the control above is decorative"
    )


def test_the_seed_recorded_is_the_seed_the_config_carried(tmp_path: Path) -> None:
    """The record must pin the seed that was in force, per run. Without this the
    replay has a number it cannot trust."""
    for seed in (1, 2):
        project = _seeded_project(tmp_path, seed)
        _, manifest = _run_once(project, "only")
        assert manifest["environment"]["seeds"]["resolved"] == seed
        assert manifest["environment"]["seeds"]["source"] == "config:env.yaml"


def test_this_file_does_not_claim_to_close_the_v3_replay_test() -> None:
    """Honesty clause, in the same spirit as the journal's own. The v3 form is
    not applicable to the PoC; a docstring here drifting into claiming it would
    reintroduce the overclaim the plan explicitly forbids."""
    # Scoped to the module DOCSTRING, not the file text. Reading the whole file
    # makes this guard match its own list of forbidden phrases below and fail on
    # itself — the same self-reference that tripped the journal's honesty grep on
    # its own author. The docstring is where the claim would actually be made.
    lowered = (__doc__ or "").lower()

    for claim in ("closes the v3", "v3 form is delivered", "implements the v3"):
        assert claim not in lowered, f"this file claims the v3 replay form: {claim!r}"

    # It must keep saying, out loud, that scores do not exist yet.
    assert "this build has no scores" in lowered, (
        "the no-scores limit was removed from the module docstring; if scores "
        "now exist, re-point the PoC form at them rather than deleting the caveat"
    )
