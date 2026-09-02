"""Run-journal tests — build-plan S12, A&D §4.4a.

One test per done-condition, plus the honesty-clause grep. These run entirely in
`tmp_path`: the journal is created under a temporary project root, never under the
real `journal/`, so the suite cannot pollute a real run history.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from chipsim.journal import (
    JournalError,
    ManifestVerificationError,
    finish_run,
    read_manifest,
    record_invocation,
    start_run,
)


@pytest.fixture
def fake_project(tmp_path: Path) -> Path:
    """A minimal project root: configs/ with two YAMLs, and nothing else."""
    configs = tmp_path / "configs"
    configs.mkdir()
    (configs / "env.yaml").write_text(yaml.safe_dump({"stage": "test"}))
    (configs / "barrier_panel.yaml").write_text(
        yaml.safe_dump({"ratified": False, "panel": [{"symbol": "ABCB1"}]})
    )
    return tmp_path


# --- done-condition 1 ------------------------------------------------------


def test_run_snapshots_every_config_and_digests_match(fake_project: Path) -> None:
    run_dir = start_run("chipsim parse", fake_project)
    manifest = read_manifest(run_dir)

    snapped = {p.name for p in (run_dir / "configs").glob("*.yaml")}
    assert snapped == {"env.yaml", "barrier_panel.yaml"}

    assert set(manifest["configs"]) == snapped
    for name, digest in manifest["configs"].items():
        import hashlib

        actual = hashlib.sha256((run_dir / "configs" / name).read_bytes()).hexdigest()
        assert actual == digest, f"snapshot digest mismatch for {name}"


# --- done-condition 2 ------------------------------------------------------


def test_editing_a_config_after_the_run_does_not_change_the_snapshot(
    fake_project: Path,
) -> None:
    run_dir = start_run("chipsim parse", fake_project)
    before = read_manifest(run_dir)["configs"]["env.yaml"]
    snapshot_text = (run_dir / "configs" / "env.yaml").read_text()

    (fake_project / "configs" / "env.yaml").write_text(yaml.safe_dump({"stage": "EDITED"}))

    after = read_manifest(run_dir)["configs"]["env.yaml"]
    assert after == before
    assert (run_dir / "configs" / "env.yaml").read_text() == snapshot_text
    assert "EDITED" not in snapshot_text


# --- done-condition 3 ------------------------------------------------------


def test_reusing_a_run_id_raises_rather_than_overwriting(fake_project: Path) -> None:
    run_dir = start_run("chipsim parse", fake_project, run_id="fixed-id")
    marker = (run_dir / "marker.txt")
    marker.write_text("original")

    with pytest.raises(JournalError, match="already exists"):
        start_run("chipsim parse", fake_project, run_id="fixed-id")

    assert marker.read_text() == "original"


# --- done-condition 4 ------------------------------------------------------


def test_tampered_manifest_fails_read_manifest(fake_project: Path) -> None:
    run_dir = start_run("chipsim parse", fake_project)
    path = run_dir / "manifest.json"
    doc = json.loads(path.read_text())
    doc["argv"] = ["chipsim", "something-else"]
    path.write_text(json.dumps(doc))

    with pytest.raises(ManifestVerificationError):
        read_manifest(run_dir)


def test_manifest_without_a_digest_is_refused(fake_project: Path) -> None:
    """Never load unverified — absence of a digest is not consent."""
    run_dir = start_run("chipsim parse", fake_project)
    path = run_dir / "manifest.json"
    doc = json.loads(path.read_text())
    doc.pop("manifest_sha256")
    path.write_text(json.dumps(doc))

    with pytest.raises(ManifestVerificationError, match="no manifest_sha256"):
        read_manifest(run_dir)


# --- done-condition 5 ------------------------------------------------------


def test_a_crashed_run_leaves_no_outcome_and_cannot_read_as_success(
    fake_project: Path,
) -> None:
    run_dir = start_run("chipsim parse", fake_project)
    # crash: finish_run never called
    assert not (run_dir / "outcome.json").exists()

    finished = start_run("chipsim parse", fake_project, run_id="finished")
    finish_run(finished, status="ok")
    assert json.loads((finished / "outcome.json").read_text())["status"] == "ok"


def test_outcome_is_written_last(fake_project: Path) -> None:
    """The manifest must already exist when the outcome lands, so an outcome can
    never be the only record of a run."""
    run_dir = start_run("chipsim parse", fake_project)
    assert (run_dir / "manifest.json").exists()
    finish_run(run_dir, status="failed", detail="boom")
    outcome = json.loads((run_dir / "outcome.json").read_text())
    assert outcome["status"] == "failed"
    assert outcome["detail"] == "boom"


# --- done-condition 6 ------------------------------------------------------


def test_panel_seal_invocation_record_carries_no_digest(fake_project: Path) -> None:
    rec_path = record_invocation(
        "panel-seal", fake_project, argv=["chipsim", "panel-seal", "--panel", "x.yaml"]
    )
    record = json.loads(rec_path.read_text())

    assert record["record_type"] == "invocation"
    assert record["argv"] == ["chipsim", "panel-seal", "--panel", "x.yaml"]
    assert "start" in record and record["environment"] is not None
    for forbidden in ("manifest_sha256", "configs", "digest", "sha256"):
        assert forbidden not in record, (
            f"an invocation record must carry no digest field; found {forbidden!r}. "
            "The record is an audit trail, never the attestation."
        )


# --- the dirty tree is RECORDED, never hidden or refused -------------------


def test_manifest_records_git_state_and_environment(fake_project: Path) -> None:
    run_dir = start_run("chipsim parse", fake_project)
    m = read_manifest(run_dir)

    assert m["record_type"] == "run"
    assert m["argv"]
    assert "git" in m and "commit" in m["git"] and "dirty" in m["git"]
    assert isinstance(m["git"]["dirty_files"], list)
    assert m["python"] and m["platform"]
    for pkg in ("pyarrow", "rdkit", "pandas", "numpy", "PyYAML"):
        assert pkg in m["packages"], f"{pkg} is output-determining and must be recorded"
    assert "environment" in m


# --- honesty clause --------------------------------------------------------


def test_no_wording_claims_the_journal_authenticates_anyone() -> None:
    """A&D §4.4a honesty clause. The digest detects modification; it does not
    prove authorship. This is a grep-level test because the conflation it guards
    against has recurred."""
    import re

    source = Path(__file__).resolve().parent.parent / "chipsim" / "journal.py"
    text = source.read_text().lower()

    forbidden = [
        r"proves? (?:the |that )?(?:a )?human",
        r"authenticat(?:e|es|ing|ion)\b(?!\w)",
        r"proves? who",
        r"attests? that a human",
    ]
    for pattern in forbidden:
        for match in re.finditer(pattern, text):
            line = text[: match.start()].count("\n") + 1
            snippet = text.splitlines()[line - 1].strip()
            # A negated statement ("does NOT prove a human ran it") is the point.
            assert re.search(r"\bnot\b|\bnever\b|\bcannot\b|\bno\b", snippet), (
                f"{source.name}:{line} appears to claim the journal authenticates "
                f"someone: {snippet!r}"
            )


# --- pipeline wiring (S12's second file) -----------------------------------


def test_etl_stage_opens_a_run_and_writes_the_outcome_last(
    fake_project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from chipsim import pipeline

    monkeypatch.setenv("CHIPSIM_PROJECT_ROOT", str(fake_project))
    monkeypatch.setitem(pipeline._HANDLERS, "hash-verify", lambda ns: 0)

    assert pipeline.main(["hash-verify", "--dest", str(fake_project)]) == 0

    runs = [d for d in (fake_project / "journal").iterdir() if d.name != "invocations"]
    assert len(runs) == 1
    manifest = read_manifest(runs[0])
    assert manifest["command"] == "hash-verify"
    assert manifest["configs"], "the stage must snapshot configs before running"
    assert json.loads((runs[0] / "outcome.json").read_text())["status"] == "ok"


def test_a_crashing_stage_is_recorded_and_never_reads_as_success(
    fake_project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from chipsim import pipeline

    monkeypatch.setenv("CHIPSIM_PROJECT_ROOT", str(fake_project))

    def _boom(ns):
        raise RuntimeError("boom")

    monkeypatch.setitem(pipeline._HANDLERS, "hash-verify", _boom)

    with pytest.raises(RuntimeError, match="boom"):
        pipeline.main(["hash-verify", "--dest", str(fake_project)])

    runs = [d for d in (fake_project / "journal").iterdir() if d.name != "invocations"]
    outcome = json.loads((runs[0] / "outcome.json").read_text())
    assert outcome["status"] == "crashed"
    assert outcome["status"] != "ok"


def test_panel_seal_is_journalled_as_an_invocation_not_a_run(
    fake_project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Global Constraint (4) has no technical force; recording the invocation is
    what makes a violation detectable."""
    from chipsim import pipeline

    monkeypatch.setenv("CHIPSIM_PROJECT_ROOT", str(fake_project))
    monkeypatch.setitem(pipeline._HANDLERS, "panel-seal", lambda ns: 0)

    assert pipeline.main(["panel-seal", "--panel", "x.yaml"]) == 0

    journal = fake_project / "journal"
    assert [d.name for d in journal.iterdir()] == ["invocations"], (
        "panel-seal must be journalled as an invocation, never as a run"
    )
    records = list((journal / "invocations").glob("*.json"))
    assert len(records) == 1
    record = json.loads(records[0].read_text())
    assert record["record_type"] == "invocation"
    assert "manifest_sha256" not in record
