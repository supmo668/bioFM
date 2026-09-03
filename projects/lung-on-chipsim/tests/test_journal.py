"""Run-journal tests — build-plan S12, A&D §4.4a.

One test per done-condition, plus the honesty-clause grep. These run entirely in
`tmp_path`: the journal is created under a temporary project root, never under the
real `journal/`, so the suite cannot pollute a real run history.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest
import yaml

from chipsim.journal import (
    JournalError,
    ManifestVerificationError,
    finish_run,
    read_manifest,
    read_outcome,
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
    # Re-READ from disk. Asserting against `snapshot_text` — captured before the
    # edit — is tautologically true and cannot fail whatever the implementation does.
    assert "EDITED" not in (run_dir / "configs" / "env.yaml").read_text()


# --- done-condition 3 ------------------------------------------------------


def test_reusing_a_run_id_raises_rather_than_overwriting(fake_project: Path) -> None:
    run_dir = start_run("chipsim parse", fake_project, run_id="fixed-id")
    marker = run_dir / "marker.txt"
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
    # ALLOWLIST, not a blocklist. A blocklist of four names passes any digest
    # field called something else — verified: adding `record_sha256` survived the
    # blocklist form. An invocation record is an audit trail, never the
    # attestation, so its shape is closed rather than merely filtered.
    assert set(record) == {"record_type", "command", "start", "argv", "environment"}, (
        f"unexpected invocation record shape: {sorted(record)}. The record is "
        "closed by design — a new field must be justified, not merely not-forbidden."
    )

    # And nothing digest-shaped anywhere in the structure, including nested.
    def _walk(node, path=""):
        if isinstance(node, dict):
            for k, v in node.items():
                # Digest tokens with boundaries, so PYTHONHASHSEED — a seed env
                # var, legitimately recorded — is not mistaken for a digest.
                assert not re.search(
                    r"(?:^|_)(?:sha\d*|digest|signature|checksum)(?:$|_)|\bhash\b",
                    str(k),
                    re.IGNORECASE,
                ), (
                    f"invocation record carries a digest-shaped key at {path}.{k}. "
                    "A digest here would read as an attestation of the seal, and "
                    "it would not be one."
                )
                _walk(v, f"{path}.{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                _walk(v, f"{path}[{i}]")

    _walk(record)


# --- the dirty tree is RECORDED, never hidden or refused -------------------


def test_manifest_records_environment_by_value(fake_project: Path) -> None:
    run_dir = start_run("chipsim parse", fake_project)
    m = read_manifest(run_dir)

    assert m["record_type"] == "run"
    assert m["argv"]
    # git state is deliberately NOT recorded — see the module docstring.
    assert "git" not in m, (
        "git state was removed from the run record (CTO ruling #44): capturing it "
        "meant running `git status` in a directory arriving from workflow config, "
        "and `git status` executes core.fsmonitor. Its reappearance would restore "
        "that sink."
    )
    # B3 — BY VALUE, not key presence. Key-presence assertions are why four
    # separate mutants of the environment block left the suite fully green: a
    # manifest recording None for every package, or a constant platform, satisfies
    # `pkg in m["packages"]` exactly as well as the truth does. The whole reason
    # pyarrow and rdkit are ==-pinned is so the record can show two runs were the
    # same computation, and a record of `None` shows nothing.
    import os as _os
    import platform as _platform
    import sys as _sys
    from importlib.metadata import version as _version

    # sys.version, not platform.python_version(): the manifest records the FULL
    # build string, which distinguishes two 3.11.15 builds from different
    # compilers — a real source of numeric difference in wheels.
    assert m["python"] == _sys.version, (
        f"recorded python {m['python']!r} != running {_sys.version!r}"
    )
    assert m["platform"] == _platform.platform(), (
        f"recorded platform {m['platform']!r} != running {_platform.platform()!r}"
    )

    for pkg in ("pyarrow", "rdkit", "pandas", "numpy", "PyYAML"):
        assert pkg in m["packages"], f"{pkg} is output-determining and must be recorded"
        assert m["packages"][pkg] == _version(pkg), (
            f"recorded {pkg}=={m['packages'][pkg]!r} but the installed version is "
            f"{_version(pkg)!r}. A version recorded as None or stale cannot show "
            "that two runs were the same computation."
        )

    # argv by value, not merely truthy — with argv[0] trimmed to its basename.
    #
    # RESOLVED (principal ruling, 2026-09-03), superseding the note that stood
    # here. Two corrections to what this comment used to say:
    #   1. The premise was WRONG. `journal/**` is gitignored and only `.gitkeep`
    #      is tracked, so no absolute path ever reached git. The exposure is at
    #      PUBLICATION time — records shipped alongside results — not commit time.
    #   2. The trade it asserted was false. Dropping argv[0] does not weaken the
    #      record's account of what ran: `python`, `platform` and `packages`
    #      identify the interpreter more precisely than its path does. So the
    #      absolute path was pure disclosure and the basename is kept.
    # argv[1:] stays verbatim; those are the run's real inputs.
    expected_argv = [_os.path.basename(_sys.argv[0]), *_sys.argv[1:]] if _sys.argv else []
    assert m["argv"] == expected_argv, f"recorded argv {m['argv']!r} != expected {expected_argv!r}"

    # Config digests by value against the snapshot bytes on disk.
    import hashlib as _hashlib

    assert m["configs"], "a project with configs/ must record them"
    for name, digest in m["configs"].items():
        actual = _hashlib.sha256((run_dir / "configs" / name).read_bytes()).hexdigest()
        assert digest == actual, f"recorded digest for {name} does not match the snapshot"

    assert "environment" in m


# --- B3: the git/environment block is asserted BY VALUE ---------------------
#
# The tests above assert KEY PRESENCE. Key presence is satisfied by a field that
# is always wrong, so four separate mutants of `_git_state`/`_environment` left
# the suite fully green — including `dirty_files -> []`, which HIDES A DIRTY TREE,
# the one posture A&D §4.4a states in bold ("a dirty tree is recorded, never
# hidden or refused"). A record whose git block is never checked against a known
# repository is decoration.
#
# The four mutants these tests exist to kill, each a one-line lie the old suite
# accepted:
#
#   M1  dirty_files -> []          hides a dirty tree              (A&D §4.4a bold)
#   M2  dirty -> False             hides the dirty FLAG
#   M3  commit -> None             drops the identity of the code that ran
#   M4  project_root_override      hides that the audit trail was diverted
#         -> None
#
# Asserted against a repository built here, whose state is known exactly, rather
# than against the repository the suite happens to be running in.


def _run_git(repo: Path, *args: str) -> str:
    """git, for BUILDING the fixture. Deliberately not the module's own probe —
    a test that used `_git_state` to compute its own expected value would pass
    against every one of the four mutants."""
    import subprocess

    out = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True)
    return out.stdout.strip()


def test_environment_records_the_journal_relocation_by_value(
    fake_project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Kills M4 (`project_root_override -> None`).

    The override relocates the audit trail. A record that does not say where it
    was meant to live cannot show the trail was diverted — which is the whole
    reason the field exists.
    """
    monkeypatch.setenv("CHIPSIM_PROJECT_ROOT", str(fake_project))
    run_dir = start_run("chipsim parse", fake_project)
    env = read_manifest(run_dir)["environment"]

    assert env["project_root_override"] == str(fake_project), (
        "the relocation must be recorded by value; None here would mean a "
        "diverted trail is indistinguishable from a default one"
    )

    monkeypatch.delenv("CHIPSIM_PROJECT_ROOT")
    run_dir2 = start_run("chipsim parse", fake_project, run_id="no-override")
    env2 = read_manifest(run_dir2)["environment"]
    assert env2["project_root_override"] is None, (
        "and absence must be recorded as absence, so the two cases differ"
    )


def test_environment_records_seed_vars_by_value(
    fake_project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A seed that is set must appear with its VALUE; one that is not must appear
    as None rather than be omitted — "not set" and "we forgot to look" must not
    be the same record."""
    from chipsim.journal import SEED_ENV_VARS

    name = SEED_ENV_VARS[0]
    monkeypatch.setenv(name, "424242")
    run_dir = start_run("chipsim parse", fake_project)
    seeds = read_manifest(run_dir)["environment"]["seeds"]

    # The raw env capture moved under `seeds["env"]` when seed RESOLUTION landed
    # (S12 r2.7); the by-value / absence-is-recorded rule this test exists for is
    # unchanged and still applies to the raw map.
    assert seeds["env"][name] == "424242"
    for other in SEED_ENV_VARS:
        assert other in seeds["env"], f"{other} must be recorded even when unset"

    # And the resolution itself is present, naming which source won.
    assert seeds["resolved"] == 424242
    assert seeds["source"] == "env:CHIPSIM_SEED"


# --- honesty clause --------------------------------------------------------


def test_no_wording_claims_the_journal_authenticates_anyone() -> None:
    """A&D §4.4a honesty clause. The digest detects modification; it does not
    prove authorship. This is a grep-level test because the conflation it guards
    against has recurred."""
    import re

    pkg = Path(__file__).resolve().parent.parent / "chipsim"
    # Scope: every file where a human might read such a claim. journal.py alone
    # left pipeline.py's `panel-seal` --help text — the string an operator reads at
    # the moment of sealing — ungoverned, which is where the last overclaim of this
    # class survived two rounds of "reframe complete".
    sources = [
        pkg / "journal.py",
        pkg / "pipeline.py",
        pkg / "harmonize" / "pgp_label.py",
    ]

    forbidden = [
        r"proves? (?:the |that )?(?:a )?human",
        r"authenticat(?:e|es|ing|ion)\b(?!\w)",
        r"proves? who",
        r"attests? that a human",
        r"establish(?:es)? who",
        r"identif(?:y|ies) who",
        r"who[- ]ran",
        # TTY-gate paraphrases. The gate checks that stdin is a terminal; it does
        # not establish a human is present, and a pty defeats it. These forms all
        # slipped a literal-string blocklist in test_panel_seal_tty.py, which is
        # why the negative check was consolidated here — this guard has the
        # negation window and the anti-vacuity check.
        r"ensures? (?:a|the) human",
        r"impossible for an agent",
        r"prevents? an agent",
        r"guarantees? (?:a )?human",
        r"requires? a human to be present",
    ]
    inspected = 0
    for source in sources:
        # Collapse newlines so a claim wrapped across two lines cannot slip the
        # adjacency the patterns require.
        raw = source.read_text()
        text = re.sub(r"\s+", " ", raw.lower())
        for pattern in forbidden:
            for match in re.finditer(pattern, text):
                inspected += 1
                # The negation must appear BEFORE the claim, within the same
                # sentence. The previous form searched the whole line, so
                # "authenticates the operator who wrote it, no question" passed —
                # the guard against the overclaim was itself bypassable by using
                # the word "no" AFTER the claim. Verified: that exact sentence
                # survived the old check and fails this one.
                sentence_start = max(text.rfind(". ", 0, match.start()) + 1, 0)
                window = text[max(sentence_start, match.start() - 160) : match.start()]
                assert re.search(
                    r"\b(?:not|never|cannot|no|nothing|neither)\b",
                    window,
                ), (
                    f"{source.name} appears to claim the journal or seal "
                    f"authenticates someone: …{text[max(0, match.start() - 90) : match.start() + 60]}…"
                )

    # The loop must not pass by matching nothing. If the honest disclaimers are
    # ever deleted wholesale, `inspected == 0` and this test would otherwise go
    # quietly green on a module that says nothing at all about the limitation.
    assert inspected > 0, (
        "no honesty-clause language found in any scanned source — the disclaimers "
        "that state the digest does not prove authorship appear to have been removed"
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


# --- QG regressions: findings from the S12 review --------------------------


def test_an_outcome_cannot_be_written_twice(fake_project: Path) -> None:
    """QG-1 (CRITICAL). A crashed run must not be restampable as a success.
    Done-condition 5 was only half-implemented: the crash path left no outcome,
    but nothing stopped a later write from creating one."""
    run_dir = start_run("chipsim parse", fake_project)
    finish_run(run_dir, status="crashed", detail="boom")

    with pytest.raises(JournalError, match="already has an outcome"):
        finish_run(run_dir, status="ok", detail="totally fine")

    assert read_outcome(run_dir)["status"] == "crashed"


def test_tampering_with_a_config_snapshot_is_detected_on_read(
    fake_project: Path,
) -> None:
    """QG-2. The configs digest map was decorative — nothing re-hashed the
    snapshot at read time, so the snapshot was silently editable."""
    run_dir = start_run("chipsim parse", fake_project)
    (run_dir / "configs" / "env.yaml").write_text(yaml.safe_dump({"stage": "TAMPERED"}))

    with pytest.raises(ManifestVerificationError, match="does not match the manifest"):
        read_manifest(run_dir)


def test_adding_a_file_to_the_snapshot_is_detected(fake_project: Path) -> None:
    """QG-2, other direction: an unrecorded extra file is also tampering."""
    run_dir = start_run("chipsim parse", fake_project)
    (run_dir / "configs" / "smuggled.yaml").write_text("x: 1\n")

    with pytest.raises(ManifestVerificationError, match="unrecorded file"):
        read_manifest(run_dir)


def test_a_relocated_record_does_not_verify(fake_project: Path) -> None:
    """QG-5. The digest covers the manifest's CONTENTS, not the record's
    IDENTITY, so a whole record could be copied to another id and still verify."""
    import shutil

    run_dir = start_run("chipsim parse", fake_project, run_id="real")
    impostor = run_dir.parent / "impostor"
    shutil.copytree(run_dir, impostor)

    read_manifest(run_dir)  # the original still verifies
    with pytest.raises(ManifestVerificationError, match="copied or relocated"):
        read_manifest(impostor)


def test_yml_and_nested_configs_are_snapshotted(fake_project: Path) -> None:
    """QG-7. `*.yaml` at one level missed `.yml` and subdirectories, so a config
    the run read could be absent from the record indistinguishably from one that
    never existed."""
    (fake_project / "configs" / "other.yml").write_text("a: 1\n")
    nested = fake_project / "configs" / "panels"
    nested.mkdir()
    (nested / "lung.yaml").write_text("b: 2\n")

    run_dir = start_run("chipsim parse", fake_project)
    recorded = set(read_manifest(run_dir)["configs"])

    assert recorded == {"env.yaml", "barrier_panel.yaml", "other.yml", "panels/lung.yaml"}
    assert (run_dir / "configs" / "panels" / "lung.yaml").read_text() == "b: 2\n"


def test_a_tampered_outcome_is_detected(fake_project: Path) -> None:
    """QG-8. The outcome sits outside the manifest digest, so it carries its own."""
    run_dir = start_run("chipsim parse", fake_project)
    finish_run(run_dir, status="crashed", detail="boom")

    path = run_dir / "outcome.json"
    doc = json.loads(path.read_text())
    doc["status"] = "ok"
    path.write_text(json.dumps(doc))

    with pytest.raises(ManifestVerificationError, match="was modified"):
        read_outcome(run_dir)


def test_an_unfinished_run_reads_as_none_never_as_success(fake_project: Path) -> None:
    run_dir = start_run("chipsim parse", fake_project)
    assert read_outcome(run_dir) is None


def test_a_traversing_run_id_is_rejected(fake_project: Path) -> None:
    """QG-11. `..` in a run id escaped journal/ entirely."""
    for bad in ("../escape", "a/b", "..", ""):
        with pytest.raises(JournalError, match="invalid run id"):
            start_run("chipsim parse", fake_project, run_id=bad)
    assert not (fake_project / "escape").exists()


def test_a_failed_start_leaves_no_partial_run_directory(
    fake_project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """QG-4. A crash mid-snapshot used to leave a manifest-less directory that
    made every reader raise and permanently burned its run id."""
    import chipsim.journal as journal_mod

    monkeypatch.setattr(
        journal_mod, "_package_versions", lambda: (_ for _ in ()).throw(OSError("nope"))
    )
    with pytest.raises(OSError, match="nope"):
        start_run("chipsim parse", fake_project, run_id="doomed")

    journal = fake_project / "journal"
    assert not (journal / "doomed").exists()
    assert list(journal.iterdir()) == [], "no staging directory may be left behind"


def test_the_project_root_override_is_recorded(
    fake_project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """QG-3. The override relocates the audit trail, so a record that does not
    say it was set cannot show the trail was diverted."""
    monkeypatch.setenv("CHIPSIM_PROJECT_ROOT", str(fake_project))
    run_dir = start_run("chipsim parse", fake_project)
    env = read_manifest(run_dir)["environment"]
    assert env["project_root_override"] == str(fake_project)


def test_invocation_records_never_overwrite_each_other(fake_project: Path) -> None:
    """QG-10. `write_text` would replace a prior audit record."""
    for _ in range(4):
        record_invocation("panel-seal", fake_project, argv=["chipsim", "panel-seal"])
    records = list((fake_project / "journal" / "invocations").glob("*.json"))
    assert len(records) == 4


def test_panel_seal_fails_closed_when_it_cannot_be_journalled(
    fake_project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """QG-3. Everywhere else the journal is best-effort, but a seal written with
    no record of the attempt is exactly what the trail exists to make visible."""
    from chipsim import pipeline

    monkeypatch.setenv("CHIPSIM_PROJECT_ROOT", str(fake_project))
    sealed: list[str] = []
    monkeypatch.setitem(pipeline._HANDLERS, "panel-seal", lambda ns: sealed.append("x"))
    monkeypatch.setattr(
        pipeline, "record_invocation", lambda *a, **k: (_ for _ in ()).throw(OSError("ro"))
    )

    assert pipeline.main(["panel-seal", "--panel", "x.yaml"]) == 2
    assert sealed == [], "the seal must not run when its invocation cannot be recorded"


def test_an_unrecordable_etl_run_leaves_a_durable_marker(
    fake_project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """QG-4. stderr is routinely discarded under n8n/cron, so 'ran without a
    record' must be visible somewhere durable."""
    from chipsim import pipeline

    monkeypatch.setenv("CHIPSIM_PROJECT_ROOT", str(fake_project))
    monkeypatch.setitem(pipeline._HANDLERS, "hash-verify", lambda ns: 0)
    monkeypatch.setattr(
        pipeline, "start_run", lambda *a, **k: (_ for _ in ()).throw(OSError("nope"))
    )

    assert pipeline.main(["hash-verify", "--dest", str(fake_project)]) == 0
    markers = list((fake_project / "journal").glob("UNRECORDED-*.json"))
    assert len(markers) == 1
    assert "nope" in json.loads(markers[0].read_text())["error"]


def test_a_handler_exiting_zero_is_not_recorded_as_a_crash(
    fake_project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """QG-9. sys.exit(0) was caught by `except BaseException` and journalled as a
    crash while the process exited 0 — the record contradicted the run."""
    from chipsim import pipeline

    monkeypatch.setenv("CHIPSIM_PROJECT_ROOT", str(fake_project))

    def _exit_ok(ns):
        raise SystemExit(0)

    monkeypatch.setitem(pipeline._HANDLERS, "hash-verify", _exit_ok)

    with pytest.raises(SystemExit):
        pipeline.main(["hash-verify", "--dest", str(fake_project)])

    runs = [d for d in (fake_project / "journal").iterdir() if d.name != "invocations"]
    assert read_outcome(runs[0])["status"] == "ok"


def test_a_handler_returning_none_is_recorded_as_success(
    fake_project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """QG-9, other direction: None meant `code == 0` was False → 'failed', while
    the process exited 0."""
    from chipsim import pipeline

    monkeypatch.setenv("CHIPSIM_PROJECT_ROOT", str(fake_project))
    monkeypatch.setitem(pipeline._HANDLERS, "hash-verify", lambda ns: None)

    assert pipeline.main(["hash-verify", "--dest", str(fake_project)]) == 0
    runs = [d for d in (fake_project / "journal").iterdir() if d.name != "invocations"]
    assert read_outcome(runs[0])["status"] == "ok"


# --- B1: the outcome<->manifest binding is UNCONDITIONAL --------------------
#
# Done-condition 5: a crashed run cannot read as success. The binding check was
# written `if bound and manifest_path.is_file()`, which is not a weaker check but
# no check — it hands the forger two one-step opt-outs. The outcome digest is
# unkeyed, so recomputing it after either edit is free.


def _forge_outcome_into(run_dir: Path, donor: Path, *, drop_binding: bool) -> None:
    """Copy a successful run's outcome into `run_dir`, repaired to pass every
    check that came before the binding check."""
    from chipsim.journal import outcome_digest

    o = json.loads((donor / "outcome.json").read_text())
    o["run_id"] = run_dir.name  # defeats the location check
    if drop_binding:
        o.pop("manifest_sha256", None)
    o.pop("outcome_sha256", None)
    o["outcome_sha256"] = outcome_digest(o)  # unkeyed: recomputed for free
    (run_dir / "outcome.json").write_text(json.dumps(o))


def test_a_crashed_run_cannot_read_as_success_via_a_copied_outcome(
    fake_project: Path,
) -> None:
    good = start_run("good", fake_project, run_id="good")
    finish_run(good, status="ok")
    crashed = start_run("crashed", fake_project, run_id="crashed")

    _forge_outcome_into(crashed, good, drop_binding=False)

    with pytest.raises(ManifestVerificationError):
        read_outcome(crashed)


def test_deleting_the_manifest_does_not_skip_the_binding_check(
    fake_project: Path,
) -> None:
    """The bypass: the check only ran `if manifest_path.is_file()`, so removing
    the manifest opted straight out of it. A verification that can be skipped by
    deleting the thing it verifies is not a verification."""
    good = start_run("good", fake_project, run_id="good")
    finish_run(good, status="ok")
    crashed = start_run("crashed", fake_project, run_id="crashed")

    _forge_outcome_into(crashed, good, drop_binding=False)
    (crashed / "manifest.json").unlink()

    with pytest.raises(ManifestVerificationError):
        read_outcome(crashed)


def test_dropping_manifest_sha256_does_not_skip_the_binding_check(
    fake_project: Path,
) -> None:
    """The other bypass: the check only ran `if bound`, so an outcome that simply
    omits the field was accepted."""
    good = start_run("good", fake_project, run_id="good")
    finish_run(good, status="ok")
    crashed = start_run("crashed", fake_project, run_id="crashed")

    _forge_outcome_into(crashed, good, drop_binding=True)

    with pytest.raises(ManifestVerificationError):
        read_outcome(crashed)


def test_an_honest_outcome_still_reads_back(fake_project: Path) -> None:
    """The binding must reject forgeries without rejecting the real thing."""
    run_dir = start_run("real", fake_project, run_id="real")
    finish_run(run_dir, status="ok")
    assert read_outcome(run_dir)["status"] == "ok"


# --- B2: the state probe never executes the inspected repo's config ---------


def test_the_project_root_override_must_be_an_existing_absolute_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Fails CLOSED. A silent fallback would write the audit trail into the source
    tree while the operator believes it was diverted."""
    from chipsim import pipeline

    monkeypatch.setenv("CHIPSIM_PROJECT_ROOT", "relative/path")
    with pytest.raises(JournalError):
        pipeline.project_root()

    monkeypatch.setenv("CHIPSIM_PROJECT_ROOT", str(tmp_path / "nope"))
    with pytest.raises(JournalError):
        pipeline.project_root()

    monkeypatch.setenv("CHIPSIM_PROJECT_ROOT", str(tmp_path))
    assert pipeline.project_root() == tmp_path.resolve()


def test_source_root_is_not_overridable(monkeypatch: pytest.MonkeyPatch) -> None:
    from chipsim.journal import source_root

    before = source_root()
    monkeypatch.setenv("CHIPSIM_PROJECT_ROOT", "/tmp")
    assert source_root() == before, (
        "source_root selects the tree git is read from and must never be "
        "steerable by the environment"
    )


# --- B1: config symlink escape (principal ruling, 2026-09-03) --------------


def test_a_config_symlinked_outside_the_project_is_refused_loudly(
    fake_project: Path, tmp_path: Path
) -> None:
    """B1. `shutil.copy2` follows symlinks, so a config symlinked at a target
    outside the project had its CONTENT copied into the record and hashed into
    the manifest — exfiltrating whatever the link pointed at.

    The refusal must be LOUD. Silently skipping the file is the worse bug: the
    record would then claim a complete snapshot it does not have, which is
    exactly the indistinguishability this module exists to prevent.
    """
    outside = tmp_path.parent / "outside-secret.yaml"
    outside.write_text("private_key: SHOULD-NEVER-BE-COPIED\n")
    (fake_project / "configs" / "leak.yaml").symlink_to(outside)

    with pytest.raises(JournalError) as excinfo:
        start_run("chipsim parse", fake_project)

    message = str(excinfo.value)
    assert "leak.yaml" in message
    # The refusal names the escape; it does not leak the secret's contents.
    assert "SHOULD-NEVER-BE-COPIED" not in message


def test_a_refused_symlink_config_leaves_no_record_at_all(
    fake_project: Path, tmp_path: Path
) -> None:
    """B1. Fail loudly means fail COMPLETELY — no partial record survives, so
    there is never a run directory claiming a snapshot that omitted a config."""
    outside = tmp_path.parent / "outside-secret2.yaml"
    outside.write_text("secret: 1\n")
    (fake_project / "configs" / "leak.yaml").symlink_to(outside)

    with pytest.raises(JournalError):
        start_run("chipsim parse", fake_project, run_id="run-refused")

    journal = fake_project / "journal"
    assert not (journal / "run-refused").exists()
    # and no staging leftovers
    assert list(journal.glob(".staging-*")) == []


def test_a_symlink_resolving_back_inside_the_project_is_still_snapshotted(
    fake_project: Path,
) -> None:
    """B1 must gate on the RESOLVED path escaping the root, not on being a
    symlink. An in-project symlink is legitimate and its content is genuinely
    part of the project, so refusing it would be a false positive."""
    real = fake_project / "configs" / "real.yaml"
    real.write_text("inside: true\n")
    (fake_project / "configs" / "alias.yaml").symlink_to(real)

    run_dir = start_run("chipsim parse", fake_project)
    recorded = read_manifest(run_dir)["configs"]

    assert "alias.yaml" in recorded
    assert (run_dir / "configs" / "alias.yaml").read_text() == "inside: true\n"


def test_a_config_directory_symlinked_outside_the_project_is_refused(
    fake_project: Path, tmp_path: Path
) -> None:
    """B1. The escape works through a linked DIRECTORY too, since rglob walks
    into it — the per-file resolved-path check must catch that as well."""
    outside_dir = tmp_path.parent / "outside-configs"
    outside_dir.mkdir(exist_ok=True)
    (outside_dir / "secret.yaml").write_text("token: nope\n")
    (fake_project / "configs" / "linked").symlink_to(outside_dir)

    with pytest.raises(JournalError):
        start_run("chipsim parse", fake_project)


def test_an_in_project_symlinked_directory_is_walked_not_silently_skipped(
    fake_project: Path,
) -> None:
    """B1, second half. `rglob` does not recurse into symlinked directories, so
    configs beneath an in-project linked dir were absent from the snapshot while
    an ordinary `open()` in the run still read them — a silent skip. The walk now
    follows them."""
    real_dir = fake_project / "configs" / "panels"
    real_dir.mkdir()
    (real_dir / "lung.yaml").write_text("b: 2\n")
    (fake_project / "configs" / "linked").symlink_to(real_dir)

    recorded = set(read_manifest(start_run("chipsim parse", fake_project))["configs"])

    assert "linked/lung.yaml" in recorded, "linked dir was silently skipped"
    assert "panels/lung.yaml" in recorded


def test_a_symlink_cycle_in_configs_terminates(fake_project: Path) -> None:
    """Following linked dirs introduces the possibility of a cycle; the walk
    must terminate rather than recurse until the stack blows."""
    nested = fake_project / "configs" / "nested"
    nested.mkdir()
    (nested / "a.yaml").write_text("a: 1\n")
    (nested / "loop").symlink_to(fake_project / "configs")

    recorded = set(read_manifest(start_run("chipsim parse", fake_project))["configs"])
    assert "nested/a.yaml" in recorded


# --- B2: argv[0] disclosure (principal ruling, 2026-09-03) -----------------


def test_argv0_is_recorded_as_a_basename_not_an_absolute_path(
    fake_project: Path,
) -> None:
    """B2. argv[0] arrives as an absolute interpreter/script path, which
    discloses the operator's directory layout (home dir, usernames, checkout
    location) in a record published with results. python/platform/packages
    already identify the interpreter, so the absolute path adds no replay value
    — it is pure disclosure."""
    run_dir = start_run(
        "chipsim parse",
        fake_project,
        argv=["/Users/someone/private/checkouts/bio/.venv/bin/chipsim", "parse"],
    )
    argv = read_manifest(run_dir)["argv"]

    assert argv[0] == "chipsim"
    assert "/Users/someone" not in argv[0]


def test_argv_tail_is_recorded_verbatim(fake_project: Path) -> None:
    """B2 trims argv[0] ONLY. The arguments are the run's actual inputs — pathes
    among them are replay-relevant and must survive untouched."""
    run_dir = start_run(
        "chipsim parse",
        fake_project,
        argv=["/opt/venv/bin/chipsim", "parse", "--config", "/data/in/env.yaml", "-v"],
    )
    argv = read_manifest(run_dir)["argv"]

    assert argv == ["chipsim", "parse", "--config", "/data/in/env.yaml", "-v"]


def test_invocation_records_also_trim_argv0(fake_project: Path) -> None:
    """B2 applies to `panel-seal` invocation records too — same disclosure, same
    publication path."""
    record_invocation(
        "chipsim panel-seal",
        fake_project,
        argv=["/Users/someone/.venv/bin/chipsim", "panel-seal"],
    )
    records = sorted((fake_project / "journal" / "invocations").glob("*.json"))
    assert records, "no invocation record written"
    argv = json.loads(records[-1].read_text())["argv"]
    assert argv[0] == "chipsim"


def test_an_empty_argv_is_recorded_without_raising(fake_project: Path) -> None:
    """Trimming must not assume argv is non-empty; an embedded interpreter can
    present an empty argv and the run must still record."""
    run_dir = start_run("chipsim parse", fake_project, argv=[])
    assert read_manifest(run_dir)["argv"] == []


# --- B3/S12: seed capture (principal ruling, 2026-09-03) -------------------


def test_the_seed_is_resolved_from_the_run_config_and_recorded(
    fake_project: Path,
) -> None:
    """S12 r2.7. Previously `environment.seeds` held only env vars, so the map
    was populated only if an operator happened to export one — no replay claim
    was supportable. The seed now resolves from the run config."""
    (fake_project / "configs" / "env.yaml").write_text(
        yaml.safe_dump({"stage": "test", "seed": 20260903})
    )

    manifest = read_manifest(start_run("chipsim parse", fake_project))
    seeds = manifest["environment"]["seeds"]

    assert seeds["resolved"] == 20260903
    assert seeds["source"] == "config:env.yaml"


def test_an_absent_seed_is_recorded_as_absent_not_omitted(
    fake_project: Path,
) -> None:
    """'Unset' and 'unrecorded' must not look the same at replay — the same rule
    the env-var seeds already follow."""
    seeds = read_manifest(start_run("chipsim parse", fake_project))["environment"]["seeds"]

    assert "resolved" in seeds, "an absent seed must still be recorded, as absent"
    assert seeds["resolved"] is None
    assert seeds["source"] == "unset"


def test_the_env_var_seed_overrides_the_config_seed_and_the_record_says_so(
    fake_project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """CHIPSIM_SEED is the operator's override. The record must name which one
    actually took effect, or a replay cannot tell which value was in force."""
    (fake_project / "configs" / "env.yaml").write_text(
        yaml.safe_dump({"stage": "test", "seed": 111})
    )
    monkeypatch.setenv("CHIPSIM_SEED", "222")

    seeds = read_manifest(start_run("chipsim parse", fake_project))["environment"]["seeds"]

    assert seeds["resolved"] == 222
    assert seeds["source"] == "env:CHIPSIM_SEED"


def test_the_raw_seed_env_vars_are_still_recorded_alongside_the_resolution(
    fake_project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Adding the resolution must not drop the raw capture — PYTHONHASHSEED and
    SOURCE_DATE_EPOCH still move results and are still part of the record."""
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    seeds = read_manifest(start_run("chipsim parse", fake_project))["environment"]["seeds"]

    assert seeds["env"]["PYTHONHASHSEED"] == "0"
    assert "SOURCE_DATE_EPOCH" in seeds["env"]


def test_a_non_integer_config_seed_is_refused_rather_than_recorded_as_junk(
    fake_project: Path,
) -> None:
    """A seed that is not an integer cannot seed anything. Recording it anyway
    would put a value in the record that no replay can use, while the record
    claims a seed was in force."""
    (fake_project / "configs" / "env.yaml").write_text(
        yaml.safe_dump({"stage": "test", "seed": "not-a-number"})
    )

    with pytest.raises(JournalError, match="seed"):
        start_run("chipsim parse", fake_project)


def test_an_unparseable_config_refuses_rather_than_claiming_the_seed_is_unset(
    fake_project: Path,
) -> None:
    """Self-review finding. A malformed `configs/env.yaml` that plainly carries
    `seed: 42` previously produced `source: "unset"` — a POSITIVE FALSE
    STATEMENT in the record, worse than recording nothing and the same class of
    silent dishonesty as a snapshot claiming completeness it lacks."""
    (fake_project / "configs" / "env.yaml").write_text("seed: 42\n  bad: [unclosed\n")

    with pytest.raises(JournalError, match="seed"):
        start_run("chipsim parse", fake_project)


def test_the_snapshot_copies_the_path_that_was_verified(fake_project: Path) -> None:
    """Self-review finding (TOCTOU). The escape check resolves the config, and
    the copy must use THAT resolved path — checking one path and copying another
    re-follows the link and leaves a window to repoint it in between."""
    real = fake_project / "configs" / "real.yaml"
    real.write_text("inside: true\n")
    (fake_project / "configs" / "alias.yaml").symlink_to(real)

    run_dir = start_run("chipsim parse", fake_project)

    assert (run_dir / "configs" / "alias.yaml").read_text() == "inside: true\n"


def test_an_argv0_ending_in_a_separator_still_records_a_name(
    fake_project: Path,
) -> None:
    """Self-review finding. `os.path.basename` returns "" for a path ending in a
    separator, which would replace the record of what ran with nothing — worse
    than the disclosure it was trimming."""
    run_dir = start_run("chipsim parse", fake_project, argv=["/opt/venv/bin/", "parse"])
    assert read_manifest(run_dir)["argv"][0] != ""


def test_an_underscored_seed_string_is_refused(fake_project: Path) -> None:
    """Self-review finding. `int("1_0")` is 10 in Python, so a config reading
    `seed: "1_0"` would be recorded as 10 — a recorded seed that differs from the
    one a human reads is precisely the trust this record carries."""
    (fake_project / "configs" / "env.yaml").write_text(
        yaml.safe_dump({"stage": "test", "seed": "1_0"})
    )
    with pytest.raises(JournalError, match="decimal integer"):
        start_run("chipsim parse", fake_project)


def test_a_symlink_diamond_is_refused_rather_than_enumerated(
    fake_project: Path,
) -> None:
    """Self-review finding. Per-branch cycle detection stops a directory being
    its own ancestor but NOT a diamond: N nested dirs each linking twice to the
    level above enumerate 2^N distinct acyclic paths. Measured at 12 levels:
    8,178 files in 5 seconds. Refused loudly, never truncated."""
    configs = fake_project / "configs"
    prev = configs
    for i in range(14):
        level = configs / f"l{i}"
        level.mkdir()
        (level / "a.yaml").write_text("a: 1\n")
        (level / "x").symlink_to(prev)
        (level / "y").symlink_to(prev)
        prev = level

    with pytest.raises(JournalError, match="Refusing rather than truncating"):
        start_run("chipsim parse", fake_project)


def test_an_ordinary_nested_config_tree_is_well_within_the_bound(
    fake_project: Path,
) -> None:
    """The bound must not fire on anything real, or it becomes the defect."""
    configs = fake_project / "configs"
    for i in range(8):
        nested = configs / f"group{i}" / "sub"
        nested.mkdir(parents=True)
        (nested / f"c{i}.yaml").write_text(f"i: {i}\n")

    recorded = read_manifest(start_run("chipsim parse", fake_project))["configs"]
    assert len([k for k in recorded if k.startswith("group")]) == 8


def test_a_boolean_seed_is_refused(fake_project: Path) -> None:
    """The bool guard had ZERO coverage — deleting `isinstance(value, bool) or`
    left all tests green while `seed: true` recorded as `resolved: 1`. Same class
    as the `1_0` -> 10 defect: a recorded seed differing from what a human reads.
    YAML `true`/`yes` both parse to bool."""
    (fake_project / "configs" / "env.yaml").write_text(
        yaml.safe_dump({"stage": "test", "seed": True})
    )
    with pytest.raises(JournalError, match="cannot seed anything"):
        start_run("chipsim parse", fake_project)


def test_a_float_seed_is_refused(fake_project: Path) -> None:
    """The non-int/str branch was likewise uncovered."""
    (fake_project / "configs" / "env.yaml").write_text(
        yaml.safe_dump({"stage": "test", "seed": 1.5})
    )
    with pytest.raises(JournalError, match="cannot seed anything"):
        start_run("chipsim parse", fake_project)


def test_a_seed_in_env_yml_is_not_recorded_as_unset(fake_project: Path) -> None:
    """`_config_sources` accepts `.yml` and snapshots it, so a seed there was
    recorded as `source: "unset"` while the record's OWN config copy carried the
    seed — a positive false statement by a different route."""
    (fake_project / "configs" / "env.yaml").unlink()
    (fake_project / "configs" / "env.yml").write_text(
        yaml.safe_dump({"stage": "test", "seed": 999})
    )

    seeds = read_manifest(start_run("chipsim parse", fake_project))["environment"]["seeds"]
    assert seeds["resolved"] == 999, "a seed in env.yml read as unset"


def test_an_exported_but_empty_seed_reads_as_unset(
    fake_project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`export CHIPSIM_SEED=$SEED` with SEED unset is an ordinary shell accident.
    Treating "" as a present-but-invalid seed hard-failed every run and bricked
    panel-seal outright."""
    monkeypatch.setenv("CHIPSIM_SEED", "")

    seeds = read_manifest(start_run("chipsim parse", fake_project))["environment"]["seeds"]
    assert seeds["source"] == "unset"


def test_a_non_integer_env_seed_is_refused(
    fake_project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Only the config refusal path was covered; the env path was not."""
    monkeypatch.setenv("CHIPSIM_SEED", "not-a-number")
    with pytest.raises(JournalError, match="CHIPSIM_SEED"):
        start_run("chipsim parse", fake_project)


def test_a_hard_linked_config_is_refused(fake_project: Path, tmp_path: Path) -> None:
    """B1, third route. `Path.resolve()` has nothing to resolve for a hard link:
    a second directory entry for an OUTSIDE inode reports its own in-configs/
    path and passes every path check. `ln` (no -s) reached the same exfiltration
    the symlink guard closes, with identical preconditions."""
    outside = tmp_path.parent / "hardlink-secret.yaml"
    outside.write_text("api_key: TOPSECRET\n")
    os.link(outside, fake_project / "configs" / "leak.yaml")

    with pytest.raises(JournalError, match="hard link"):
        start_run("chipsim parse", fake_project)


def test_a_broken_symlink_config_is_not_silently_skipped(
    fake_project: Path,
) -> None:
    """`is_dir()` and `is_file()` both follow the link and both return False, so
    a dangling `*.yaml` fell off the end of the loop with no branch — a silent
    skip inside a walk whose whole premise is that nothing is passed over
    quietly."""
    (fake_project / "configs" / "dangling.yaml").symlink_to(
        fake_project / "configs" / "nonexistent.yaml"
    )

    with pytest.raises(JournalError, match="dangling.yaml"):
        start_run("chipsim parse", fake_project)


def test_a_file_planted_under_a_symlinked_snapshot_dir_is_detected(
    fake_project: Path, tmp_path: Path
) -> None:
    """The read path used `rglob`, which does not descend into symlinked dirs —
    the exact bug fixed on the write path, not carried across. Files planted
    under a linked directory inside the snapshot were invisible to the
    extra-file check and the tampered record verified CLEAN."""
    run_dir = start_run("chipsim parse", fake_project)
    planted = tmp_path.parent / "planted-configs"
    planted.mkdir(exist_ok=True)
    (planted / "extra.yaml").write_text("injected: true\n")
    (run_dir / "configs" / "more").symlink_to(planted)

    with pytest.raises(ManifestVerificationError):
        read_manifest(run_dir)


def test_the_manifest_declares_its_record_schema(fake_project: Path) -> None:
    """r2.7 changed `environment.seeds` from a flat map to {resolved, source,
    env}. Both shapes verify clean against their own digest, so without a
    declared schema an old record and a new one are indistinguishable except by
    probing for a key — the same 'must not look alike' rule the seeds follow."""
    from chipsim.journal import RECORD_SCHEMA

    manifest = read_manifest(start_run("chipsim parse", fake_project))
    assert manifest["record_schema"] == RECORD_SCHEMA
    # and it is covered by the digest, not bolted on outside it
    assert "record_schema" in {k for k in manifest if k != "manifest_sha256"}
