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
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.modules.pop(name, None)
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
    import re

    for stale in ("OpenRouter", "rotating", "pending", "best-of"):
        assert stale not in desc, stale
    assert not re.search(r"\b54\b", desc)
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
    assert ("10.6084/m9.figshare.32086920.v5", "isNewVersionOf") in relations
    assert (
        "10.5281/zenodo.20060974",
        "isNewVersionOf",
    ) in relations  # latest v0.5.1 Zenodo version
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
    assert names == sorted([*bd.RUN_FILES, f"{bd.RUN_ID}.json", "SHA256SUMS", "BUILD_INFO"])
    import hashlib

    for line in (dst / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split("  ")
        assert hashlib.sha256((dst / name).read_bytes()).hexdigest() == digest
    rr = json.loads((ROOT / "paper" / "data" / "run_record_amendments.json").read_text())[
        "amendments"
    ][0]
    row = next(f for f in rr["files"] if f["path"].endswith(f"{bd.RUN_ID}.json"))
    assert (
        hashlib.sha256((dst / f"{bd.RUN_ID}.json").read_bytes()).hexdigest() == row["sha256_after"]
    )
    assert row["sha256_before"].startswith("323af965b631ce83")  # the superseded, published value


class _Resp:
    def __init__(self, body=None):
        self._body = body or {}
        self.status_code = 200

    def json(self):
        return self._body

    def raise_for_status(self):
        return None


def _submitter(monkeypatch, tmp_path, venue, state):
    sv = _load("scripts/publish/submit_to_venues.py", "sv_test")
    calls = []

    def record(method):
        def f(url, **kw):
            calls.append((method, url, kw))
            if method == "post" and url.endswith("/deposit/depositions"):
                return _Resp({"id": 1, "links": {"bucket": "https://bucket/B"}})
            if method == "put" and "/deposit/depositions/" in url:
                return _Resp({"metadata": {"prereserve_doi": {"doi": "10.5072/zenodo.1"}}})
            return _Resp({})

        return f

    for m in ("post", "put", "get", "delete"):
        monkeypatch.setattr(sv.requests, m, record(m))
    monkeypatch.setattr(sv, "_raise_on", lambda r: None)
    for env in ("ZENODO_TOKEN", "FIGSHARE_TOKEN"):
        monkeypatch.setenv(env, "test-token-not-a-placeholder")
    state_path = tmp_path / "state.json"
    state_path.write_text(json.dumps(state))
    cfg = sv.PublishConfig.load(ROOT / "publish.yml")
    cls = {"zenodo": sv.ZenodoSubmitter, "figshare": sv.FigshareSubmitter}[venue]
    return sv, cls(cfg, sv.State(state_path), dry_run=True), calls, state_path, cfg


def test_zenodo_submitter_refuses_a_published_deposit_without_any_request(tmp_path, monkeypatch):
    sv, sub, calls, state_path, _ = _submitter(
        monkeypatch, tmp_path, "zenodo", {"zenodo": {"deposit_id": 19748260, "published": True}}
    )
    import pytest

    with pytest.raises(sv.PublishedRecordError, match="already published"):
        sub.submit([])
    assert calls == []
    assert json.loads(state_path.read_text())["zenodo"] == {
        "deposit_id": 19748260,
        "published": True,
    }


def test_figshare_submitter_refuses_a_published_article_without_any_request(tmp_path, monkeypatch):
    sv, sub, calls, _, _ = _submitter(
        monkeypatch, tmp_path, "figshare", {"figshare": {"article_id": 32086920, "published": True}}
    )
    import pytest

    with pytest.raises(sv.PublishedRecordError, match="already published"):
        sub.submit([])
    assert calls == []


def test_zenodo_first_deposit_sends_the_publish_yml_metadata(tmp_path, monkeypatch):
    sv, sub, calls, state_path, cfg = _submitter(monkeypatch, tmp_path, "zenodo", {})
    sub.submit([])
    posts = [c for c in calls if c[0] == "post"]
    assert [c[1] for c in posts] == [
        f"{sub.base}/deposit/depositions"
    ]  # created; dry-run: no publish
    meta = next(c for c in calls if c[0] == "put")[2]["json"]["metadata"]
    assert meta["description"] == cfg.description
    assert meta["creators"][0]["name"] == "Mo, Mang-yin"
    assert meta["version"] == "0.6.0"
    assert not any(r["relation"] == "isIdenticalTo" for r in meta["related_identifiers"])
    st = json.loads(state_path.read_text())["zenodo"]
    assert st["deposit_id"] == 1 and "published" not in st


def test_zenodo_draft_resume_uploads_into_the_recorded_bucket(tmp_path, monkeypatch):
    sv, sub, calls, _, _ = _submitter(
        monkeypatch, tmp_path, "zenodo", {"zenodo": {"deposit_id": 5, "bucket": "https://bucket/B"}}
    )
    f = tmp_path / "x.txt"
    f.write_text("x")
    sub.submit([{"name": "x.txt", "path": f}])
    assert not any(c[0] == "post" and c[1].endswith("/deposit/depositions") for c in calls)
    assert any(c[0] == "put" and c[1] == "https://bucket/B/x.txt" for c in calls)


def test_main_reports_a_published_record_and_continues(tmp_path, monkeypatch):
    sv = _load("scripts/publish/submit_to_venues.py", "sv_main")
    src = (ROOT / "scripts" / "publish" / "submit_to_venues.py").read_text()
    assert "except (requests.HTTPError, PublishedRecordError)" in src


def test_files_paths_follow_the_build_step(tmp_path, monkeypatch):
    bd = _load("scripts/publish/build_deposit.py", "bd_paths")
    files = {f["name"]: f for f in _cfg()["files"]}
    assert Path(files["v060_run_artifacts.zip"]["path"]) == (
        bd.OUT / "v060_run_artifacts"
    ).relative_to(ROOT)
    assert Path(files["paper_build.log"]["path"]) == (bd.OUT / "paper_build.log").relative_to(ROOT)
    for f in files.values():
        if not f["path"].startswith("build/") and f["path"] != "paper/paper.pdf":
            assert (ROOT / f["path"]).exists(), f["path"]
    monkeypatch.setattr(bd.shutil, "which", lambda name: None)
    import pytest

    with pytest.raises(RuntimeError, match="tectonic not found"):
        bd.build_pdf(tmp_path)


def test_staged_run_matches_the_committed_artifacts_and_is_restaged_clean(tmp_path):
    import hashlib

    bd = _load("scripts/publish/build_deposit.py", "bd_stage")
    dst = bd.stage_run_artifacts(tmp_path)
    (dst / "stray.txt").write_text("x")
    dst = bd.stage_run_artifacts(tmp_path)
    assert not (dst / "stray.txt").exists()
    lines = (dst / "SHA256SUMS").read_text().splitlines()
    names = {line.split("  ")[1] for line in lines}
    assert names == set(bd.RUN_FILES) | {f"{bd.RUN_ID}.json"} and len(lines) == 5
    for name in bd.RUN_FILES:
        assert (
            hashlib.sha256((dst / name).read_bytes()).digest()
            == hashlib.sha256((ART / name).read_bytes()).digest()
        )
    assert "staged from git" in (dst / "BUILD_INFO").read_text()


def test_check_fails_on_a_hand_edit_and_write_mode_is_idempotent(tmp_path, monkeypatch, capsys):
    rd = _load("scripts/paper/render_publish_description.py", "rd_check")
    pub, cit = tmp_path / "publish.yml", tmp_path / "CITATION.cff"
    pub.write_text(
        (ROOT / "publish.yml")
        .read_text()
        .replace("Multi-agent group-generation", "Multi-agent GROUP-generation", 1)
    )
    cit.write_text((ROOT / "CITATION.cff").read_text())
    monkeypatch.setattr(rd, "PUBLISH", pub)
    monkeypatch.setattr(rd, "CITATION", cit)
    monkeypatch.setattr(sys, "argv", ["x", "--check"])
    assert rd.main() == 1 and "publish.yml" in capsys.readouterr().err
    monkeypatch.setattr(sys, "argv", ["x"])
    assert rd.main() == 0
    once = (pub.read_text(), cit.read_text())
    assert rd.main() == 0 and (pub.read_text(), cit.read_text()) == once
    monkeypatch.setattr(sys, "argv", ["x", "--check"])
    assert rd.main() == 0
    new, old = yaml.safe_load(pub.read_text()), yaml.safe_load((ROOT / "publish.yml").read_text())
    assert {k: v for k, v in new.items() if k != "description"} == {
        k: v for k, v in old.items() if k != "description"
    }
    desc_lines = pub.read_text().split("description: |\n", 1)[1].split("\n\n", 1)[0].splitlines()
    for line in desc_lines:
        assert not line.rstrip().endswith("-"), line  # no hyphen break inside the block scalar


def test_render_rules(tmp_path, monkeypatch):
    rd = _load("scripts/paper/render_publish_description.py", "rd_rules")
    gen = tmp_path / "gen.tex"
    gen.write_text(
        "\\newcommand{\\resA}{\\ensuremath{-0.12}}\n\\newcommand{\\resB}{\\textbf{3}}\n"
        "\\newcommand{\\resC}{1\\,234}\n\\newcommand{\\resD}{\\textemdash}\n"
    )
    paper = tmp_path / "p.tex"

    def run(body):
        paper.write_text(f"\\begin{{abstract}}\n{body}\n\\end{{abstract}}")
        return rd.render()

    monkeypatch.setattr(rd, "GEN", gen)
    monkeypatch.setattr(rd, "PAPER", paper)
    assert run("$\\Delta C$ and $\\rho=\\resA$ and $>\\resB$.") == "ΔC and ρ = −0.12 and > 3."
    assert run("a---b, 1--2, \\resC{} cells, \\resD.") == "a—b, 1–2, 1,234 cells, —."
    assert (
        run("x~\\citep{k}. % comment\nNext \\textsc{Adamson} sentence.")
        == "x. Next Adamson sentence."
    )
    import pytest

    with pytest.raises(ValueError):
        run("(\\citet{k}) 10\\%")
    with pytest.raises(KeyError):
        run("\\resZ")


def test_keywords_and_citation_version_are_true_of_the_work():
    tex = " ".join(
        (ROOT / "paper" / p).read_text().lower()
        for p in ("paper.tex", "sections/results.tex", "sections/experimental_setup.tex")
    )
    cit = yaml.safe_load((ROOT / "CITATION.cff").read_text())
    for kw in _cfg()["keywords"]:
        assert kw.lower() in tex, kw
    assert set(cit["keywords"]) >= set(_cfg()["keywords"]) - {"provenance"}
    assert str(cit["version"]) == _cfg()["version"] == "0.6.0"
    prereg = json.loads((ART / "provenance.json").read_text())["prereg_version"]
    assert prereg.startswith("v" + _cfg()["version"])
    notes = " ".join(r.get("notes", "") for r in cit.get("references", []))
    assert (
        "used as the" not in notes
    )  # no reference claims a tool role the v0.6.0 study does not use


def test_run_record_amendment_rr1_is_complete_and_true():
    """RR-1 (principal ruling 2026-10-08): the LLM key-storage record is gone from every run file,
    each file's before/after hash is recorded, the 'before' is what the repository held, and the
    paper prints the superseded manifest hash."""
    import hashlib
    import subprocess

    rr = json.loads((ROOT / "paper" / "data" / "run_record_amendments.json").read_text())[
        "amendments"
    ]
    assert [a["id"] for a in rr] == ["RR-1"] and rr[0]["date"] == "2026-10-08"
    paths = {f["path"] for f in rr[0]["files"]}
    run_files = {
        f"artifacts/v0.6.0/{n}"
        for n in ("provenance.json", "trainer_runs.jsonl", "lifecycle_runs.jsonl")
    }
    run_files |= {str(p.relative_to(ROOT)) for p in (ROOT / "configs" / "runs").glob("*.json")}
    assert paths == run_files
    for f in rr[0]["files"]:
        text = (ROOT / f["path"]).read_text()
        for value in (
            "llm_key_source",
            "syntropyhealth",
            "infisical",
            "cross_project",
            "home_project",
        ):
            assert value not in text, (f["path"], value)
        assert hashlib.sha256((ROOT / f["path"]).read_bytes()).hexdigest() == f["sha256_after"]
        before = subprocess.run(
            ["git", "show", f"{rr[0]['before_commit']}:projects/perturb-seq-eval/{f['path']}"],
            cwd=ROOT,
            capture_output=True,
            check=True,
        ).stdout
        assert hashlib.sha256(before).hexdigest() == f["sha256_before"], f["path"]
    import re

    for rel in ("paper.tex", "sections/results.tex", "sections/corrections.tex"):
        text = re.sub(r"(?<!\\\\)%.*", "", (ROOT / "paper" / rel).read_text())
        for mac in ("\\resManifestShaSuperseded", "\\resRROneDate", "\\resManifestSha"):
            assert mac in text, (rel, mac)
        assert "323af965" not in text and "70be925d" not in text, rel  # never hand-typed
    # CTO #585 cond. 3: RR-1's recorded hashes are frozen; a re-amendment is a new RR-n entry,
    # never an edit of RR-1 (canonical digest of every (path, before, after) row).
    rows = [(f["path"], f["sha256_before"], f["sha256_after"]) for f in rr[0]["files"]]
    assert hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest() == (
        "5118914e11fcfaab4a42234bca4d4efe1fbcd90cd63b2b9e16e49cf163248773"
    )
    assert "llm_key_source" not in (ART / "summary.json").read_text()  # shipped too
    for doc in ("README.md", "paper/README.md", "scripts/modal/app_v05.py"):
        assert "syntropyhealth" not in (ROOT / doc).read_text(), doc


def test_generator_refuses_a_manifest_that_does_not_match_the_amendment(tmp_path, monkeypatch):
    import shutil as _sh

    import pytest

    fv = _load("scripts/paper/fill_v060_numbers.py", "fv_rr")
    rr = json.loads((ROOT / "paper" / "data" / "run_record_amendments.json").read_text())
    (tmp_path / "paper" / "data").mkdir(parents=True)
    (tmp_path / "configs" / "runs").mkdir(parents=True)
    man = tmp_path / "configs" / "runs" / "20260929T035447Z-ce5f237.json"
    _sh.copy(ROOT / "configs" / "runs" / man.name, man)
    (tmp_path / "artifacts").symlink_to(ROOT / "artifacts")  # v0.5.0 record read via PROJECT_ROOT
    monkeypatch.setattr(fv, "PROJECT_ROOT", tmp_path)
    rec = tmp_path / "paper" / "data" / "run_record_amendments.json"

    def build():
        return fv.build(
            ART,
            ROOT / "paper/data/projection_v060.json",
            man,
            [],
            ROOT / "paper/data/land_v060.json",
            ROOT / "paper/data/amendments_v060.json",
            ROOT / "paper/data/v050_record.json",
        )

    rec.write_text(json.dumps(rr))
    try:
        m = build()
    except FileNotFoundError as exc:  # generator reads other inputs from PROJECT_ROOT: mirror them
        raise AssertionError(f"test fixture incomplete: {exc}") from exc
    assert m["ManifestShaSuperseded"] == "323af965b631ce83" and m["RROneFileCount"] == "6"
    bad = json.loads(json.dumps(rr))
    for f in bad["amendments"][0]["files"]:
        if f["path"].endswith(man.name):
            f["sha256_after"] = "0" * 64
    rec.write_text(json.dumps(bad))
    with pytest.raises(ValueError, match="RR-1 amendment record"):
        build()
    rec.write_text(json.dumps({"amendments": []}))
    with pytest.raises(ValueError, match="no RR-1"):
        build()


def test_build_main_refuses_uncommitted_inputs_before_staging(monkeypatch, capsys):
    import subprocess as sp

    bd = _load("scripts/publish/build_deposit.py", "bd_main")
    calls = []
    state = {"porcelain": " M configs/runs/20260929T035447Z-ce5f237.json\n", "render_rc": 0}

    def fake(args, **kw):
        calls.append(args)
        if "--porcelain" in args:
            return sp.CompletedProcess(args, 0, state["porcelain"], "")
        return sp.CompletedProcess(args, state["render_rc"], "", "")

    monkeypatch.setattr(bd.subprocess, "run", fake)
    staged = []
    monkeypatch.setattr(bd, "stage_run_artifacts", lambda *a, **k: staged.append(1) or Path("x"))
    monkeypatch.setattr(sys, "argv", ["build_deposit.py", "--skip-pdf"])
    assert bd.main() == 1 and staged == []
    assert "deposit inputs are not committed" in capsys.readouterr().err
    porcelain = next(c for c in calls if "--porcelain" in c)
    for path in (
        "paper",
        "scripts/paper",
        "artifacts/v0.6.0",
        "configs/runs",
        "publish.yml",
        "CITATION.cff",
        "docs",
        "artifacts/v0.5.0",
    ):
        assert path in porcelain, path
    state["porcelain"] = ""
    assert bd.main() == 0 and staged == [1]
    calls.clear()
    state["render_rc"] = 1
    assert bd.main() == 1 and not any("--porcelain" in c for c in calls)


def test_rr1_appendix_says_a_rerun_no_longer_records_the_field():
    """CTO #585 cond. 2: with the code retired, the appendix must not claim a re-run re-creates it."""
    import re

    text = re.sub(
        r"(?<!\\\\)%.*", "", (ROOT / "paper" / "sections" / "corrections.tex").read_text()
    )
    start = text.index("\\label{app:rr}")
    nxt = text.find("\\subsection", start)
    rr = " ".join(text[start : nxt if nxt != -1 else len(text)].split())
    for stale in ("re-creates", "re-create", "recreates", "still records"):
        assert stale not in rr, stale
    assert "no longer does" in rr and "does not record it" in rr
