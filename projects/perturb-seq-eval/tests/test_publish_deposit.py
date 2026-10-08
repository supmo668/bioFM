"""Deposit metadata is a claim about the work (CTO #577): it is generated from, or tested
against, the manuscript and the run's evidence."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "v0.6.0"
HAIKU = "claude-haiku-4-5-20251001"
SONNET = "claude-sonnet-5-5"


def _load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # dataclasses resolve their module by name
    spec.loader.exec_module(mod)
    return mod


def _cfg() -> dict:
    return yaml.safe_load((ROOT / "publish.yml").read_text())


def test_descriptions_are_a_fresh_render_of_the_abstract():
    r = subprocess.run(
        [sys.executable, "scripts/paper/render_publish_description.py", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    rd = _load("scripts/paper/render_publish_description.py", "rpd")
    text = rd.render()
    assert " ".join(_cfg()["description"].split()) == text
    cit = yaml.safe_load((ROOT / "CITATION.cff").read_text())
    assert " ".join(cit["abstract"].split()) == text


def test_method_sentence_matches_the_run_evidence():
    """The roster sentence is bound to provenance: pinned Haiku/Sonnet roster, Validator on
    Sonnet, four proposer roles on Haiku, no served-model mismatch, no fallback step."""
    desc = " ".join(_cfg()["description"].split())
    assert (
        "pinned roster of Anthropic Claude models (Haiku 4.5 for the four proposer roles, "
        "Sonnet 5.5 for the Validator) whose served model is recorded and asserted per call" in desc
    )
    for stale in ("OpenRouter", "rotating", "54", "pending", "best-of"):
        assert stale not in desc, stale
    p = json.loads((ART / "provenance.json").read_text())
    s = json.loads((ART / "summary.json").read_text())
    assert set(p["llm_pool"]) == {HAIKU, SONNET}
    served = {}
    for c in p["llm_call_log"]:
        served.setdefault(c["role"], set()).add(c["served_model"])
    assert served == {
        "DataCurator": {HAIKU},
        "Literature": {HAIKU},
        "Architect": {HAIKU},
        "Trainer": {HAIKU},
        "Validator": {SONNET},
    }
    assert p["llm_report"]["served_mismatch_count"] == 0
    assert all(c["served_model"] == c["requested_model"] for c in p["llm_call_log"])
    assert s["n_steps_fallback"] == 0


def test_gate_sentence_matches_the_summary():
    desc = " ".join(_cfg()["description"].split())
    pr = json.loads((ART / "summary.json").read_text())["preregistered"]
    assert pr["H5"]["pass"] is False and "H5 fails" in desc
    assert f"{pr['tally']['PASS']} of {pr['tally']['out_of']} gates pass" in desc


def test_creators_use_the_ruled_name_everywhere():
    assert [c["name"] for c in _cfg()["creators"]] == ["Mo, Mang-yin"]
    assert _cfg()["creators"][0]["orcid"] == "0009-0009-5233-3142"
    cit = yaml.safe_load((ROOT / "CITATION.cff").read_text())
    assert (
        cit["authors"][0]["given-names"] == "Mang-yin" and cit["authors"][0]["family-names"] == "Mo"
    )
    for rel in ("publish.yml", "CITATION.cff", "paper/paper.tex"):
        assert "Mangyin" not in (ROOT / rel).read_text(), rel
    assert "Mang-yin Mo" in (ROOT / "paper" / "paper.tex").read_text()


def test_related_identifiers_assert_a_new_version_not_identity():
    rel = _cfg()["venues"]["zenodo"]["related_identifiers"]
    relations = {(r["identifier"], r["relation"]) for r in rel}
    assert not any(r["relation"] == "isIdenticalTo" for r in rel)
    assert ("10.6084/m9.figshare.32086920", "isNewVersionOf") in relations
    assert (
        "10.5281/zenodo.20060974",
        "isNewVersionOf",
    ) in relations  # latest v0.5.1 Zenodo version
    assert ("https://github.com/supmo668/bioFM", "isSupplementedBy") in relations
    cit = (ROOT / "CITATION.cff").read_text()
    assert "10.5281/zenodo.20060974" in cit  # the version the new deposit supersedes is on record


def test_files_block_ships_the_v060_run_and_marks_v050_superseded():
    files = {f["name"]: f for f in _cfg()["files"]}
    assert files["paper.pdf"]["path"] == "paper/paper.pdf"
    assert files["paper_build.log"]["path"] == "build/deposit/paper_build.log"
    assert files["v060_run_artifacts.zip"]["path"] == "build/deposit/v060_run_artifacts"
    assert files["v050_run_artifacts.zip"]["description"].startswith("SUPERSEDED")
    for f in files.values():
        assert "pending" not in f["description"].lower(), f["name"]


def test_stage_run_artifacts_copies_the_run_with_checksums(tmp_path):
    bd = _load("scripts/publish/build_deposit.py", "bd")
    dst = bd.stage_run_artifacts(tmp_path)
    names = sorted(p.name for p in dst.iterdir())
    assert names == sorted([*bd.RUN_FILES, f"{bd.RUN_ID}.json", "SHA256SUMS"])
    import hashlib

    for line in (dst / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split("  ")
        assert hashlib.sha256((dst / name).read_bytes()).hexdigest() == digest
    manifest = hashlib.sha256((dst / f"{bd.RUN_ID}.json").read_bytes()).hexdigest()
    assert manifest.startswith("323af965b631ce83")


def test_zenodo_submitter_refuses_a_published_deposit(tmp_path, monkeypatch):
    sv = _load("scripts/publish/submit_to_venues.py", "sv")
    state_path = tmp_path / "state.json"
    state_path.write_text(json.dumps({"zenodo": {"deposit_id": 19748260, "published": True}}))
    monkeypatch.setenv("ZENODO_TOKEN", "test-token-not-a-placeholder")
    cfg = sv.PublishConfig.load(ROOT / "publish.yml")
    state = sv.State(state_path)
    try:
        sub = sv.ZenodoSubmitter(cfg, state, dry_run=True)
    except TypeError:
        sub = sv.ZenodoSubmitter(cfg, state)
    import pytest

    with pytest.raises(RuntimeError, match="already published"):
        sub.submit([])
