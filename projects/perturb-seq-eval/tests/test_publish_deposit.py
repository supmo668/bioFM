"""Deposit metadata is a claim about the work (CTO #577): it is generated from, or tested
against, the manuscript and the run's evidence."""

from __future__ import annotations

import importlib.util
import json
import re
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
    """The roster sentence is bound to provenance: pinned Haiku/Sonnet roster, the validating
    role on Sonnet, the four proposing roles on Haiku, no served-model mismatch, no fallback
    step. The abstract names the roles by what they do, since it does not define their names."""
    desc = " ".join(_cfg()["description"].split())
    assert (
        "pinned roster of Anthropic Claude models (Haiku 4.5 for the four roles that propose, "
        "Sonnet 5.5 for the role that validates) whose served model is recorded and asserted "
        "per call" in desc
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
    # HACA-119: the description carries the generator's own sentence, so a rename there reaches it
    fv = _load("scripts/paper/fill_v060_numbers.py", "fv_gate_sentence")
    outcomes = {g: pr[g]["pass"] for g in fv.HYPOTHESIS_NAMES}
    assert pr["H5"]["pass"] is False
    assert fv.gate_summary(outcomes, pr["tally"]["out_of"]) in desc


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
    assert ("10.6084/m9.figshare.32086920.v8", "isNewVersionOf") in relations
    # Single Zenodo parent: the published 0.6.2 version that 0.6.3 revises (approvals row 45,
    # 2026-11-25); the concept DOI in the notes carries the rest of the chain (CTO #639).
    zen = [r for r in rel if r["relation"] == "isNewVersionOf" and "zenodo" in r["identifier"]]
    assert [r["identifier"] for r in zen] == ["10.5281/zenodo.24518637"]
    cit = (ROOT / "CITATION.cff").read_text()
    assert "10.5281/zenodo.24518637" in cit  # the version the new deposit supersedes is on record
    assert "v5 = v0.5.1" not in cit  # Figshare v5 matches Zenodo v0.5.2 by checksum, not v0.5.1
    changelog = (ROOT / "CHANGELOG.md").read_text()
    assert "Known gap: 0.5.1 and 0.5.2 are not documented here" in changelog
    assert (
        "10.5281/zenodo.20074427" in changelog and "No release note is reconstructed" in changelog
    )
    assert "10.5281/zenodo.24518637" in changelog  # the 0.6.2 record the new deposit revises


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


# Fake venues for the submitter tests. A small stateful "world" tracks the files each draft holds
# (inherited ones until deleted, uploads once made), so the exact-file-set checks are exercised.
ZEN_BASE = "https://zenodo.org/api"
FIG_BASE = "https://api.figshare.com/v2"
NEW_ZEN = 24600555  # the new-version draft id Zenodo would return (newer than 24518637)
ZBUCKET = f"{ZEN_BASE}/files/new-draft-bucket"


def _world():
    return {
        "zen_inherited": {"f1": "paper.pdf", "f2": "supplement.zip"},
        "zen": {},
        "fig_inherited": {11: "paper.pdf", 12: "supplement.zip"},
        "fig": {},
        "fig_authors": [{"full_name": "Mang-yin Mo"}],
    }


def _revision_routes(public_versions=(8,), world=None, draft=None):
    w = world if world is not None else _world()
    pub = list(public_versions)

    def public(url, kw):
        v = pub.pop(0) if len(pub) > 1 else pub[0]
        return {"version": v, "files": [{"name": "paper.pdf", "supplied_md5": "old"}]}

    def zen_draft(url, kw):
        d = {
            "id": NEW_ZEN,
            "conceptrecid": "19716140",
            "state": "unsubmitted",
            "submitted": False,
            "links": {"bucket": ZBUCKET},
            "files": [{"id": i} for i in w["zen_inherited"]],
        }
        d.update(draft or {})
        return d

    def zen_files(url, kw):
        held = [{"id": i, "filename": n, "checksum": "old"} for i, n in w["zen_inherited"].items()]
        return held + [{"id": n, "filename": n, "checksum": m} for n, m in w["zen"].items()]

    def zen_delete(url, kw):
        w["zen_inherited"].pop(url.rsplit("/", 1)[-1], None)
        return {}

    def zen_upload(url, kw):
        import hashlib

        w["zen"][url.rsplit("/", 1)[-1]] = hashlib.md5(kw.get("data", b"")).hexdigest()
        return {}

    def fig_files(url, kw):
        return [{"id": i} for i in w["fig_inherited"]]

    def fig_delete(url, kw):
        w["fig_inherited"].pop(int(url.rsplit("/", 1)[-1]), None)
        return {}

    def fig_article(url, kw):
        held = [
            {"name": n, "supplied_md5": "old", "status": "available"}
            for n in w["fig_inherited"].values()
        ]
        for n, m in w["fig"].items():
            entry = {
                "name": n,
                "supplied_md5": m,
                "status": w.get("fig_status", {}).get(n, "available"),
            }
            if entry["status"] == "__missing__":
                del entry["status"]  # the API left the key out
            held.append(entry)
        return {"files": held, "authors": w["fig_authors"]}

    return {
        ("post", "/deposit/depositions/24518637/actions/newversion"): {
            "links": {"latest_draft": f"{ZEN_BASE}/deposit/depositions/{NEW_ZEN}"}
        },
        ("get", f"/deposit/depositions/{NEW_ZEN}"): zen_draft,
        ("get", f"/deposit/depositions/{NEW_ZEN}/files"): zen_files,
        ("delete", f"/deposit/depositions/{NEW_ZEN}/files/f1"): zen_delete,
        ("delete", f"/deposit/depositions/{NEW_ZEN}/files/f2"): zen_delete,
        ("put", "/files/new-draft-bucket/paper.pdf"): zen_upload,
        ("put", f"/deposit/depositions/{NEW_ZEN}"): {
            "metadata": {"prereserve_doi": {"doi": f"10.5281/zenodo.{NEW_ZEN}"}}
        },
        ("post", f"/deposit/depositions/{NEW_ZEN}/actions/publish"): {
            "doi": f"10.5281/zenodo.{NEW_ZEN}"
        },
        ("get", f"{FIG_BASE}/articles/32086920"): public,
        ("get", "/account/articles/32086920/files"): fig_files,
        ("delete", "/account/articles/32086920/files/11"): fig_delete,
        ("delete", "/account/articles/32086920/files/12"): fig_delete,
        ("get", "/account/articles/32086920"): fig_article,
        "_world": w,
    }


def _fake(calls, routes):
    def record(method):
        def f(url, **kw):
            calls.append((method, url, kw))
            # longest matching suffix wins, so ".../555/files" beats ".../555"
            hits = [
                (s, b)
                for key, b in routes.items()
                if key != "_world"
                for (m, s) in [key]
                if m == method and url.endswith(s)
            ]
            if hits:
                body = max(hits, key=lambda h: len(h[0]))[1]
                return _Resp(body(url, kw) if callable(body) else body)
            if method == "post" and url.endswith("/deposit/depositions"):
                return _Resp({"id": 1, "links": {"bucket": f"{ZEN_BASE}/files/plain"}})
            if method == "put" and "/deposit/depositions/" in url:
                return _Resp({"metadata": {"prereserve_doi": {"doi": "10.5072/zenodo.1"}}})
            if method == "post" and url.endswith("/account/articles"):
                return _Resp({"location": f"{FIG_BASE}/account/articles/777"})
            if method == "post" and url.endswith("/reserve_doi"):
                return _Resp({"doi": "10.6084/m9.figshare.777"})
            if method == "post" and url.endswith("/actions/publish"):
                return _Resp({"doi": "10.5281/zenodo.1"})
            return _Resp({})

        return f

    return record


def _submitter(monkeypatch, tmp_path, venue, state, dry_run=True, vcfg_patch=None, routes=None):
    """A submitter over a faked venue. vcfg_patch {key: value|None} edits venues.<venue>
    (None removes the key, e.g. revision_of, to exercise the plain create path)."""
    sv = _load("scripts/publish/submit_to_venues.py", "sv_test")
    calls = []
    routes = routes if routes is not None else _revision_routes()
    record = _fake(calls, routes)
    for m in ("post", "put", "get", "delete"):
        monkeypatch.setattr(sv.requests, m, record(m))
    monkeypatch.setattr(sv, "_raise_on", lambda r: None)
    for env in ("ZENODO_TOKEN", "FIGSHARE_TOKEN", "OSF_TOKEN"):
        monkeypatch.setenv(env, "test-token-not-a-placeholder")
    state_path = tmp_path / "state.json"
    state_path.write_text(json.dumps(state))
    cfg = sv.PublishConfig.load(ROOT / "publish.yml")
    for k, v in (vcfg_patch or {}).items():
        if v is None:
            cfg.venues[venue].pop(k, None)
        else:
            cfg.venues[venue][k] = v
    cls = {"zenodo": sv.ZenodoSubmitter, "figshare": sv.FigshareSubmitter, "osf": sv.OSFSubmitter}[
        venue
    ]
    sub = cls(cfg, sv.State(state_path), dry_run=dry_run)
    if venue == "figshare":
        world = routes.get("_world") or {"fig": {}}

        def upload(art_id, f):
            calls.append(("upload", art_id, f))
            world["fig"][f["name"]] = f["md5"]

        monkeypatch.setattr(sub, "_upload_file", upload)
    return sv, sub, calls, state_path, cfg


PLAIN = {"revision_of": None}  # the generic create path (no revision configured)
# A revision that a completed dry run prepared (the state the publish go starts from).
ZSTATE = {
    "zenodo": {
        "deposit_id": NEW_ZEN,
        "bucket": ZBUCKET,
        "revision_of": 24518637,
        "inherited_files_removed": True,
        "prepared": True,
    }
}
FSTATE = {
    "figshare": {
        "article_id": 32086920,
        "revision_of": 32086920,
        "doi": "10.6084/m9.figshare.32086920",
        "public_baseline": [8, [["paper.pdf", "old"]]],
        "inherited_files_removed": True,
        "prepared": True,
    }
}


def _prepared_world():
    w = _world()
    w["zen_inherited"], w["fig_inherited"] = {}, {}
    return w


# ---- guards: published/superseded records refused, except EXACTLY the two named revisions ----


def test_only_two_named_revisions_are_permitted():
    sv = _load("scripts/publish/submit_to_venues.py", "sv_allowed")
    assert sv.ALLOWED_REVISIONS == {"zenodo": 24518637, "figshare": 32086920}
    assert sv.ZENODO_CONCEPT == 19716140 and sv.FIGSHARE_BASE_VERSION == 8
    cfg = yaml.safe_load((ROOT / "publish.yml").read_text())["venues"]
    assert cfg["zenodo"]["revision_of"] == 24518637
    assert cfg["figshare"]["revision_of"] == 32086920
    assert "revision_of" not in cfg["osf"]
    rel = {r["identifier"] for r in cfg["zenodo"]["related_identifiers"]}
    assert f"10.6084/m9.figshare.32086920.v{sv.FIGSHARE_BASE_VERSION}" in rel


def test_published_or_superseded_records_are_refused_before_any_request(tmp_path, monkeypatch):
    import pytest

    cases = (
        ("zenodo", {"zenodo": {"deposit_id": 19748260, "published": True}}, None),
        ("zenodo", {"zenodo": {"deposit_id": 24518637}}, None),  # the target itself, as a draft
        ("zenodo", {"zenodo": {"deposit_id": "24518637", "revision_of": 24518637}}, None),  # str
        ("zenodo", {"zenodo": {"deposit_id": 20060974}}, PLAIN),
        ("zenodo", {"zenodo": {"deposit_id": 23411021, "bucket": "x"}}, None),  # mixing
        ("zenodo", {}, {"revision_of": 20060974}),  # any other revision target
        ("zenodo", {}, {"revision_of": 24430429}),  # 0.6.1, the previous target: refused now
        ("zenodo", {"zenodo": {"deposit_id": 24430429, "revision_of": 24430429}}, None),
        ("zenodo", {}, {"revision_of": 24518637.0}),  # not an int
        ("figshare", {"figshare": {"article_id": 32086920, "published": True}}, None),
        ("figshare", {"figshare": {"article_id": 32086920}}, None),  # hand-seeded, no revision_of
        ("figshare", {"figshare": {"article_id": 32086920}}, PLAIN),  # no revision configured
        ("figshare", {"figshare": {"article_id": "32086920"}}, PLAIN),  # str id, no revision
        ("figshare", {"figshare": {"article_id": 34562538}}, None),  # standalone draft: mixing
        ("figshare", {}, {"revision_of": 99}),
        ("figshare", {}, {"revision_of": 32086920.0}),
    )
    for venue, state, patch in cases:
        sv, sub, calls, state_path, _ = _submitter(
            monkeypatch, tmp_path, venue, state, vcfg_patch=patch
        )
        with pytest.raises(sv.PublishedRecordError):
            sub.submit([])
        assert calls == [], (venue, state, patch, calls)
        assert json.loads(state_path.read_text()) == state


def test_zenodo_revision_dry_run_touches_24518637_only_via_newversion(tmp_path, monkeypatch):
    routes = _revision_routes()
    sv, sub, calls, state_path, cfg = _submitter(monkeypatch, tmp_path, "zenodo", {}, routes=routes)
    f = tmp_path / "paper.pdf"
    f.write_bytes(b"v060")
    sub.submit([{"name": "paper.pdf", "path": f, "md5": "m"}])
    on_target = [(m, u) for m, u, _ in calls if "24518637" in u]
    assert on_target == [("post", f"{ZEN_BASE}/deposit/depositions/24518637/actions/newversion")]
    deletes = [u for m, u, _ in calls if m == "delete"]
    assert deletes == [
        f"{ZEN_BASE}/deposit/depositions/{NEW_ZEN}/files/f1",
        f"{ZEN_BASE}/deposit/depositions/{NEW_ZEN}/files/f2",
    ]
    assert ("put", f"{ZBUCKET}/paper.pdf") in [(m, u) for m, u, _ in calls]
    meta = next(kw for m, u, kw in calls if m == "put" and u.endswith(f"/{NEW_ZEN}"))["json"][
        "metadata"
    ]
    assert meta["version"] == "0.6.3" and "standalone" not in meta["notes"]
    notes = " ".join(meta["notes"].split())
    assert notes.startswith("0.6.3 is the next version of this record")
    assert "10.5281/zenodo.19716140" in notes
    # 0.6.3 revises the wording of 0.6.2 and says what 0.6.2 already carries, so that a reader
    # of the record does not take the sixth amendment or its disclosure for new in 0.6.3.
    assert "It revises the wording of version 0.6.2" in notes
    assert "Version 0.6.2 already carries the sixth amendment" in notes
    assert "tag v0.6.0-a6" in notes and "previous round's held-out error" in notes
    assert "none of that is changed in this version" in notes
    assert "named by what they claim" in notes and "defined where they are first used" in notes
    assert "versions up to 0.6.2 credited to 'Xiangru Chen and others'" in notes
    assert "No hypothesis, threshold, estimator, run or outcome changed" in notes
    # No ticket, ledger row, draft id or commit is cited in a public record, and the notes do
    # not call the pre-registration untouched (the sixth amendment stands, from 0.6.2).
    for false_claim in ("untouched", "HACA-", "2792a52d", "24519260", "c42ac57", "approvals row"):
        assert false_claim not in notes, false_claim
    zen_parents = [
        r["identifier"]
        for r in meta["related_identifiers"]
        if r["relation"] == "isNewVersionOf" and "zenodo" in r["identifier"]
    ]
    assert zen_parents == ["10.5281/zenodo.24518637"]
    assert not any(m == "post" and u.endswith("/actions/publish") for m, u, _ in calls)  # dry run
    st = json.loads(state_path.read_text())["zenodo"]
    assert st == {
        "deposit_id": NEW_ZEN,
        "bucket": ZBUCKET,
        "revision_of": 24518637,
        "inherited_files_removed": True,
        "doi": f"10.5281/zenodo.{NEW_ZEN}",
        "prepared": True,
    }


def test_zenodo_newversion_response_is_validated_before_any_delete(tmp_path, monkeypatch):
    import pytest

    bad_drafts = (
        {"state": "done", "submitted": True},  # not an open draft
        {"conceptrecid": "999"},  # another concept
        {"id": 23500556},  # id differs from the latest_draft URL
        {"links": {"bucket": "https://evil.example/files/x"}},  # bucket off the API host
        {"id": 20060974},  # a superseded id
    )
    for bad in bad_drafts:
        routes = _revision_routes(draft=bad)
        if bad.get("id"):
            routes[("get", f"/deposit/depositions/{bad['id']}")] = routes[
                ("get", f"/deposit/depositions/{NEW_ZEN}")
            ]
        sv, sub, calls, _, _ = _submitter(monkeypatch, tmp_path, "zenodo", {}, routes=routes)
        with pytest.raises(sv.PublishedRecordError):
            sub.submit([])
        assert not any(m in ("delete", "put") for m, _, _ in calls), bad
    # A self-consistent draft whose id is not newer than the record being revised (and is in
    # no superseded list) is refused by the id-order check alone.
    older = 24500555
    assert older < sv.ALLOWED_REVISIONS["zenodo"] and older not in sv.SUPERSEDED_RECORDS["zenodo"]
    routes = _revision_routes(draft={"id": older})
    routes[("post", "/deposit/depositions/24518637/actions/newversion")] = {
        "links": {"latest_draft": f"{ZEN_BASE}/deposit/depositions/{older}"}
    }
    routes[("get", f"/deposit/depositions/{older}")] = routes[
        ("get", f"/deposit/depositions/{NEW_ZEN}")
    ]
    sv, sub, calls, _, _ = _submitter(monkeypatch, tmp_path, "zenodo", {}, routes=routes)
    with pytest.raises(sv.PublishedRecordError):
        sub.submit([])
    assert not any(m in ("delete", "put") for m, _, _ in calls)
    routes = _revision_routes()
    routes[("post", "/deposit/depositions/24518637/actions/newversion")] = {
        "links": {"latest_draft": "https://evil.example/api/deposit/depositions/555"}
    }
    sv, sub, calls, _, _ = _submitter(monkeypatch, tmp_path, "zenodo", {}, routes=routes)
    with pytest.raises(sv.PublishedRecordError, match="unexpected draft URL"):
        sub.submit([])
    assert not any("evil.example" in u for _, u, _ in calls)  # the token never goes there


def test_zenodo_revision_publish_publishes_only_the_prepared_new_version(tmp_path, monkeypatch):
    routes = _revision_routes(world=_prepared_world())
    sv, sub, calls, state_path, _ = _submitter(
        monkeypatch, tmp_path, "zenodo", ZSTATE, dry_run=False, routes=routes
    )
    sub.submit([])
    assert not any("24518637" in u for _, u, _ in calls)
    assert any(m == "post" and u.endswith(f"/{NEW_ZEN}/actions/publish") for m, u, _ in calls)
    assert json.loads(state_path.read_text())["zenodo"]["published"] is True


def test_publish_needs_a_completed_dry_run_and_the_removal_done(tmp_path, monkeypatch):
    import pytest

    for venue, state in (("zenodo", ZSTATE), ("figshare", FSTATE)):
        for drop in ("prepared", "inherited_files_removed"):
            st = json.loads(json.dumps(state))
            st[venue].pop(drop)
            routes = _revision_routes(world=_prepared_world())
            sv, sub, calls, _, _ = _submitter(
                monkeypatch, tmp_path, venue, st, dry_run=False, routes=routes
            )
            with pytest.raises(sv.DraftRequiredError):
                sub.submit([])
            assert not any(m == "post" and u.endswith("publish") for m, u, _ in calls), (
                venue,
                drop,
            )


def test_interrupted_removal_is_finished_by_the_next_dry_run(tmp_path, monkeypatch):
    world = _world()  # inherited files still present
    st = {
        "zenodo": {
            k: v
            for k, v in ZSTATE["zenodo"].items()
            if k not in ("prepared", "inherited_files_removed")
        }
    }
    sv, sub, calls, state_path, _ = _submitter(
        monkeypatch, tmp_path, "zenodo", st, routes=_revision_routes(world=world)
    )
    sub.submit([])
    assert world["zen_inherited"] == {}
    assert json.loads(state_path.read_text())["zenodo"]["inherited_files_removed"] is True
    fst = {
        "figshare": {
            k: v
            for k, v in FSTATE["figshare"].items()
            if k not in ("prepared", "inherited_files_removed")
        }
    }
    world = _world()
    sv, sub, calls, state_path, _ = _submitter(
        monkeypatch, tmp_path, "figshare", fst, routes=_revision_routes(world=world)
    )
    sub.submit([])
    assert world["fig_inherited"] == {}


def test_leftover_or_missing_files_block_the_publish(tmp_path, monkeypatch):
    import pytest

    f = tmp_path / "paper.pdf"
    f.write_bytes(b"v060")
    entry = {"name": "paper.pdf", "path": f, "md5": "m"}
    world = _prepared_world()
    world["zen"] = {"paper.pdf": "m", "leftover.zip": "x"}
    sv, sub, calls, _, _ = _submitter(
        monkeypatch, tmp_path, "zenodo", ZSTATE, dry_run=False, routes=_revision_routes(world=world)
    )
    with pytest.raises(sv.DraftMismatchError, match="not the release's files"):
        sub.submit([entry])
    assert not any(m == "post" and u.endswith("/actions/publish") for m, u, _ in calls)
    world = _prepared_world()
    sv, sub, calls, _, _ = _submitter(
        monkeypatch,
        tmp_path,
        "figshare",
        FSTATE,
        dry_run=False,
        routes=_revision_routes(world=world),
    )
    monkeypatch.setattr(sub, "_upload_file", lambda a, f: None)  # an upload that silently failed
    with pytest.raises(sv.DraftMismatchError, match="not the release's files"):
        sub.submit([entry])
    assert not any(m == "post" and u.endswith("/publish") for m, u, _ in calls)


def test_zenodo_resume_rereads_the_bucket_and_refuses_a_changed_one(tmp_path, monkeypatch):
    import pytest

    st = json.loads(json.dumps(ZSTATE))
    st["zenodo"]["bucket"] = "https://evil.example/files/x"
    sv, sub, calls, _, _ = _submitter(
        monkeypatch, tmp_path, "zenodo", st, routes=_revision_routes(world=_prepared_world())
    )
    with pytest.raises(sv.DraftMismatchError, match="bucket"):
        sub.submit([])
    assert not any("evil.example" in u for _, u, _ in calls)


def test_figshare_revision_dry_run_prepares_the_next_version_unpublished(tmp_path, monkeypatch):
    routes = _revision_routes()
    sv, sub, calls, state_path, cfg = _submitter(
        monkeypatch, tmp_path, "figshare", {}, routes=routes
    )
    f = tmp_path / "paper.pdf"
    f.write_bytes(b"v060")
    sub.submit([{"name": "paper.pdf", "path": f, "md5": "m", "size": 4}])
    writes = [(m, u) for m, u, _ in calls if m in ("put", "delete", "post")]
    assert writes == [
        ("put", f"{FIG_BASE}/account/articles/32086920"),
        ("delete", f"{FIG_BASE}/account/articles/32086920/files/11"),
        ("delete", f"{FIG_BASE}/account/articles/32086920/files/12"),
    ]  # no create, no reserve_doi, no publish; uploads go through _upload_file
    assert [c[1] for c in calls if c[0] == "upload"] == [32086920]
    payload = next(kw for m, u, kw in calls if m == "put")["json"]
    assert "authors" not in payload and payload["description"] == cfg.description
    assert payload["references"] == cfg.venues["figshare"]["references"]
    public = [u for m, u, _ in calls if m == "get" and u == f"{FIG_BASE}/articles/32086920"]
    assert len(public) >= 4  # baseline, after the metadata PUT, after the removal, at the end
    first_delete = next(i for i, c in enumerate(calls) if c[0] == "delete")
    assert any(c[1] == f"{FIG_BASE}/articles/32086920" for c in calls[1:first_delete])
    st = json.loads(state_path.read_text())["figshare"]
    assert st == {
        "article_id": 32086920,
        "revision_of": 32086920,
        "doi": "10.6084/m9.figshare.32086920",
        "public_baseline": [8, [["paper.pdf", "old"]]],
        "inherited_files_removed": True,
        "prepared": True,
    }


def test_figshare_revision_refuses_a_later_base_and_stops_on_public_change(tmp_path, monkeypatch):
    import pytest

    sv, sub, calls, _, _ = _submitter(
        monkeypatch, tmp_path, "figshare", {}, routes=_revision_routes(public_versions=(9,))
    )
    with pytest.raises(sv.PublishedRecordError, match="starts only from v8"):
        sub.submit([])
    assert calls and all(m == "get" for m, _, _ in calls)
    # The public view changes after the metadata PUT: stop BEFORE deleting any file.
    sv, sub, calls, _, _ = _submitter(
        monkeypatch, tmp_path, "figshare", {}, routes=_revision_routes(public_versions=(8, 9))
    )
    with pytest.raises(sv.PublishedRecordError, match="PUBLIC version changed"):
        sub.submit([])
    assert not any(m == "delete" for m, _, _ in calls)
    # On a publish run, the public view is re-checked against the recorded baseline first.
    sv, sub, calls, _, _ = _submitter(
        monkeypatch,
        tmp_path,
        "figshare",
        FSTATE,
        dry_run=False,
        routes=_revision_routes(public_versions=(9,), world=_prepared_world()),
    )
    with pytest.raises(sv.PublishedRecordError, match="PUBLIC version changed"):
        sub.submit([])
    assert not any(m in ("put", "post", "delete") for m, _, _ in calls)


def test_figshare_revision_refuses_the_v5_base_with_gets_only(tmp_path, monkeypatch):
    """v5 is the v0.5.x public version: 0.6.3 starts only from v8 (0.6.2)."""
    import pytest

    sv, sub, calls, state_path, _ = _submitter(
        monkeypatch, tmp_path, "figshare", {}, routes=_revision_routes(public_versions=(5,))
    )
    with pytest.raises(sv.PublishedRecordError, match="starts only from v8"):
        sub.submit([])
    assert calls and all(m == "get" for m, _, _ in calls)
    assert json.loads(state_path.read_text()) == {}


def test_figshare_revision_refuses_the_previous_base_v7_with_gets_only(tmp_path, monkeypatch):
    """v7 was the base of the 0.6.2 revision: with 0.6.2 public as v8, a v7 public view is not
    a base 0.6.3 may start from."""
    import pytest

    sv, sub, calls, state_path, _ = _submitter(
        monkeypatch, tmp_path, "figshare", {}, routes=_revision_routes(public_versions=(7,))
    )
    with pytest.raises(sv.PublishedRecordError, match="starts only from v8"):
        sub.submit([])
    assert calls and all(m == "get" for m, _, _ in calls)
    assert json.loads(state_path.read_text()) == {}


def test_state_revision_of_must_be_a_real_integer(tmp_path, monkeypatch):
    """SEC-2: a recorded revision_of of 24518637.0 or True never satisfies the revision check."""
    import pytest

    for bad in (24518637.0, True, "24518637"):
        state = {"zenodo": {**ZSTATE["zenodo"], "revision_of": bad}}
        sv, sub, calls, state_path, _ = _submitter(
            monkeypatch, tmp_path, "zenodo", state, dry_run=False
        )
        with pytest.raises(sv.PublishedRecordError, match="not an integer id"):
            sub.submit([])
        assert calls == [], (bad, calls)
        assert json.loads(state_path.read_text()) == state
    for bad in (32086920.0, True, "32086920"):
        state = {"figshare": {**FSTATE["figshare"], "revision_of": bad}}
        sv, sub, calls, state_path, _ = _submitter(
            monkeypatch, tmp_path, "figshare", state, dry_run=False
        )
        with pytest.raises(sv.PublishedRecordError, match="not an integer id"):
            sub.submit([])
        assert calls == [], (bad, calls)
        assert json.loads(state_path.read_text()) == state


def test_figshare_publish_run_refuses_any_author_but_the_expected_one(tmp_path, monkeypatch):
    """CTO #643 gate 2, enforced: the publish run refuses unless the revised article has exactly
    publish.yml's expected Figshare author, and never adds authors itself."""
    import pytest

    expected = yaml.safe_load((ROOT / "publish.yml").read_text())["venues"]["figshare"][
        "expected_author"
    ]
    assert expected == "Mang-yin Mo"
    for authors, ok in (
        ([{"full_name": expected}], True),
        ([{"full_name": "Mangyin Mo"}], False),  # profile not renamed
        ([{"full_name": expected}, {"full_name": "Mo, Mang-yin"}], False),  # duplicate
        ([], False),
    ):
        world = _prepared_world()
        world["fig_authors"] = authors
        sv, sub, calls, state_path, _ = _submitter(
            monkeypatch,
            tmp_path,
            "figshare",
            FSTATE,
            dry_run=False,
            routes=_revision_routes(world=world),
        )
        if ok:
            sub.submit([])
            assert any(m == "post" and u.endswith("/32086920/publish") for m, u, _ in calls)
            assert json.loads(state_path.read_text())["figshare"]["published"] is True
        else:
            with pytest.raises(sv.DraftMismatchError, match="expected_author"):
                sub.submit([])
            assert not any(m == "post" and u.endswith("/publish") for m, u, _ in calls)
        assert not any(isinstance(c[1], str) and c[1].endswith("/authors") for c in calls)
        assert not any(c[0] == "delete" for c in calls)


def test_plain_create_path_still_creates_when_no_revision_is_configured(tmp_path, monkeypatch):
    sv, sub, calls, _, _ = _submitter(monkeypatch, tmp_path, "zenodo", {}, vcfg_patch=PLAIN)
    sub.submit([])
    assert [u for m, u, _ in calls if m == "post"] == [f"{ZEN_BASE}/deposit/depositions"]
    sv, sub, calls, _, _ = _submitter(monkeypatch, tmp_path, "figshare", {}, vcfg_patch=PLAIN)
    sub.submit([])
    assert any(m == "post" and u == f"{FIG_BASE}/account/articles" for m, u, _ in calls)


def test_publish_run_without_a_recorded_draft_writes_nothing(tmp_path, monkeypatch):
    import pytest

    for venue in ("zenodo", "figshare"):
        sv, sub, calls, _, _ = _submitter(monkeypatch, tmp_path, venue, {}, dry_run=False)
        with pytest.raises(sv.DraftRequiredError):
            sub.submit([])
        assert not [c for c in calls if c[0] in ("post", "put", "delete")], venue


def test_resume_refuses_changed_files_and_refreshes_figshare_metadata(tmp_path, monkeypatch):
    import pytest

    f = tmp_path / "paper.pdf"
    f.write_bytes(b"v060")
    entry = {"name": "paper.pdf", "path": f, "md5": "new", "size": 4}
    world = _prepared_world()
    world["zen"] = {"paper.pdf": "old"}
    sv, sub, calls, _, _ = _submitter(
        monkeypatch, tmp_path, "zenodo", ZSTATE, routes=_revision_routes(world=world)
    )
    with pytest.raises(sv.DraftMismatchError):
        sub.submit([entry])
    assert not any(m == "put" and u.startswith(ZBUCKET) for m, u, _ in calls)
    world = _prepared_world()
    world["zen"] = {"paper.pdf": "new"}
    sv, sub, calls, _, _ = _submitter(
        monkeypatch, tmp_path, "zenodo", ZSTATE, routes=_revision_routes(world=world)
    )
    sub.submit([entry])
    assert not any(m == "put" and u == f"{ZBUCKET}/paper.pdf" for m, u, _ in calls)
    world = _prepared_world()
    world["fig"] = {"paper.pdf": "old"}
    sv, sub, calls, _, cfg = _submitter(
        monkeypatch, tmp_path, "figshare", FSTATE, routes=_revision_routes(world=world)
    )
    with pytest.raises(sv.DraftMismatchError):
        sub.submit([entry])
    refresh = [kw for m, u, kw in calls if m == "put" and u.endswith("/account/articles/32086920")]
    assert refresh and refresh[0]["json"]["description"] == cfg.description
    assert "authors" not in refresh[0]["json"]
    assert not any(m == "delete" for m, _, _ in calls)  # a resume never re-removes files


def _run_main(monkeypatch, tmp_path, argv, state=None, routes=None, yml=None, calls=None):
    """Run the real main() with the network stubbed: publish.yml (or ``yml``) copied to a config
    dir that is NOT the working directory, so the state file must be anchored to the config, not
    to cwd. A byte copy of the tracked v0.6.0 lineage record is seeded beside it."""
    sv = _load("scripts/publish/submit_to_venues.py", "sv_main_run")
    cfgdir, cwd = tmp_path / "proj", tmp_path / "elsewhere"
    cfgdir.mkdir()
    cwd.mkdir()
    (cfgdir / "publish.yml").write_text(
        yml if yml is not None else (ROOT / "publish.yml").read_text()
    )
    (cfgdir / "publish.state.v060.json").write_bytes(
        (ROOT / "publish.state.v060.json").read_bytes()
    )
    if state is not None:
        (cfgdir / "publish.state.v063.json").write_text(json.dumps(state))
    legacy = '{"zenodo": {"deposit_id": 19748260, "published": true}}'
    (cfgdir / "publish.state.json").write_text(legacy)
    env = tmp_path / ".env"
    env.write_text("")
    calls = [] if calls is None else calls
    routes = routes if routes is not None else _revision_routes()
    record = _fake(calls, routes)
    for m in ("post", "put", "get", "delete"):
        monkeypatch.setattr(sv.requests, m, record(m))
    monkeypatch.setattr(sv, "_raise_on", lambda r: None)
    monkeypatch.setattr(sv, "prepare_files", lambda cfg, workdir: [])
    for tok in ("ZENODO_TOKEN", "FIGSHARE_TOKEN", "OSF_TOKEN"):
        monkeypatch.setenv(tok, "test-token-not-a-placeholder")
    monkeypatch.chdir(cwd)
    monkeypatch.setattr(
        sys, "argv", ["sv", *argv, "--config", str(cfgdir / "publish.yml"), "--env", str(env)]
    )
    rc = sv.main()
    return rc, calls, cfgdir, cwd, legacy


def test_main_dry_run_prepares_both_revisions_in_the_config_anchored_state(tmp_path, monkeypatch):
    """main() resolves the release's state next to publish.yml (not cwd), passes --dry-run through
    (nothing published), prepares exactly the two revisions, and never writes the v0.5 state."""
    rc, calls, cfgdir, cwd, legacy = _run_main(monkeypatch, tmp_path, ["all", "--dry-run"])
    assert rc == 0
    st = json.loads((cfgdir / "publish.state.v063.json").read_text())
    assert st["zenodo"]["deposit_id"] == NEW_ZEN and st["zenodo"]["revision_of"] == 24518637
    assert st["zenodo"]["prepared"] is True and st["figshare"]["prepared"] is True
    assert st["figshare"]["article_id"] == 32086920 and st["figshare"]["revision_of"] == 32086920
    assert "published" not in st["zenodo"] and "published" not in st["figshare"]
    assert not (cwd / "publish.state.v063.json").exists()
    assert (cfgdir / "publish.state.json").read_text() == legacy
    lineage = (ROOT / "publish.state.v060.json").read_bytes()
    assert (cfgdir / "publish.state.v060.json").read_bytes() == lineage  # never written
    posts = [u for m, u, _ in calls if m == "post"]
    assert not any(u.endswith("/actions/publish") or u.endswith("/publish") for u in posts), posts
    assert not any(
        u.endswith("/deposit/depositions") or u.endswith("/account/articles") for u in posts
    )


def test_main_publish_without_a_recorded_draft_creates_nothing(tmp_path, monkeypatch):
    rc, calls, cfgdir, _, _ = _run_main(monkeypatch, tmp_path, ["all"])
    assert rc == 1
    assert not [c for c in calls if c[0] in ("post", "put", "delete")], calls
    assert not (cfgdir / "publish.state.v063.json").exists()


def test_main_publishes_only_the_recorded_revisions(tmp_path, monkeypatch):
    state = {**ZSTATE, **FSTATE}
    routes = _revision_routes(world=_prepared_world())
    rc, calls, cfgdir, _, _ = _run_main(monkeypatch, tmp_path, ["all"], state=state, routes=routes)
    assert rc == 0
    posts = [u for m, u, _ in calls if m == "post"]
    assert not any("newversion" in u for u in posts)
    assert any(u.endswith(f"/deposit/depositions/{NEW_ZEN}/actions/publish") for u in posts)
    assert any(u.endswith("/account/articles/32086920/publish") for u in posts)
    assert not any(m == "delete" for m, _, _ in calls)
    st = json.loads((cfgdir / "publish.state.v063.json").read_text())
    assert st["zenodo"]["published"] is True and st["figshare"]["published"] is True
    lineage = (ROOT / "publish.state.v060.json").read_bytes()
    assert (cfgdir / "publish.state.v060.json").read_bytes() == lineage  # never written


def test_main_reports_a_mismatched_state_and_continues(tmp_path, monkeypatch):
    seeded = {"figshare": {"article_id": 34562538}}  # the discarded standalone draft
    rc, calls, _, _, _ = _run_main(monkeypatch, tmp_path, ["all", "--dry-run"], state=seeded)
    assert rc == 1  # figshare refused ...
    assert not any("34562538" in c[1] or "32086920" in c[1] for c in calls), calls
    assert any(c[1].endswith("/24518637/actions/newversion") for c in calls)  # ... zenodo still ran


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
    src = (ROOT / "publish.yml").read_text()
    edited = src.replace("group-generation", "GROUP-generation", 1)
    assert edited != src  # the hand edit must land, or the --check below proves nothing
    pub.write_text(edited)
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
    # the exploratory macro family is read from its own generated file (Amendment 6)
    gen_expl = tmp_path / "gen_expl.tex"
    gen_expl.write_text(
        "\\newcommand{\\explNeg}{\\ensuremath{-0.207}}\n\\newcommand{\\explPos}{0.003}\n"
    )
    paper = tmp_path / "p.tex"

    def run(body):
        paper.write_text(f"\\begin{{abstract}}\n{body}\n\\end{{abstract}}")
        return rd.render()

    monkeypatch.setattr(rd, "GEN", gen)
    monkeypatch.setattr(rd, "GEN_EXPLORATORY", gen_expl)
    monkeypatch.setattr(rd, "PAPER", paper)
    assert set(rd.macros()) == {"resA", "resB", "resC", "resD", "explNeg", "explPos"}
    assert (
        run("($\\rho=\\explPos$ on Adamson and $\\explNeg$ on Norman, \\explNeg{} again)")
        == "(\u03c1 = 0.003 on Adamson and \u22120.207 on Norman, \u22120.207 again)"
    )
    assert run("$\\Delta C$ and $\\rho=\\resA$ and $>\\resB$.") == "ΔC and ρ = −0.12 and > 3."
    assert run("a---b, 1--2, \\resC{} cells, \\resD.") == "a—b, 1–2, 1,234 cells, —."
    assert (
        run("x~\\citep{k}. % comment\nNext \\textsc{Adamson} sentence.")
        == "x. Next Adamson sentence."
    )
    import pytest

    # a textual citation renders from the explicit CITET map and from nowhere else: the mapped
    # key gives its plain-text form, and an unmapped key stops the render
    assert rd.CITET == {"lee2026catts": "Lee and colleagues (2026)"}
    assert (
        run("the \\textsc{CATTS} method of \\citet{lee2026catts}; we ask~\\citep{k}.")
        == "the CATTS method of Lee and colleagues (2026); we ask."
    )
    with pytest.raises(ValueError, match="CITET"):
        run("as \\citet{k} show")
    with pytest.raises(ValueError):
        run("(\\citet{k}) 10\\%")
    with pytest.raises(KeyError):
        run("\\resZ")
    with pytest.raises(KeyError, match="explZ"):
        run("$\\explZ$")  # an exploratory macro the generated file does not define
    gen_expl.write_text("")  # the family comes from GEN_EXPLORATORY and nowhere else
    with pytest.raises(KeyError, match="explNeg"):
        run("\\explNeg")


def test_keywords_and_citation_version_are_true_of_the_work():
    tex = " ".join(
        (ROOT / "paper" / p).read_text().lower()
        for p in ("paper.tex", "sections/results.tex", "sections/experimental_setup.tex")
    )
    cit = yaml.safe_load((ROOT / "CITATION.cff").read_text())
    for kw in _cfg()["keywords"]:
        assert kw.lower() in tex, kw
    assert set(cit["keywords"]) >= set(_cfg()["keywords"]) - {"provenance"}
    # 0.6.3 is the self-contained rewrite of the manuscript, a deposit of the unchanged v0.6.0 run
    # (approvals row 45, 2026-11-25: relabel and dry run only). CITATION.cff names the released
    # work: 0.6.2 (published 2026-11-25 on the go of row 43) until the 0.6.3 deposit is
    # published, 0.6.3 and its DOI after that (publish.yml sequence step 5).
    sv = _load("scripts/publish/submit_to_venues.py", "sv_citation")
    state_path = sv.resolve_state_path(None, sv.PublishConfig.load(ROOT / "publish.yml"))
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    ids = {i["value"]: i.get("description", "") for i in cit["identifiers"]}
    changelog = (ROOT / "CHANGELOG.md").read_text()
    version = _cfg()["version"]
    head = [ln for ln in changelog.splitlines() if ln.startswith(f"## [{version}]")]
    assert len(head) == 1, head
    if state.get("zenodo", {}).get("published"):
        # Both venues are published before CITATION names the release (sequence step 5).
        assert state.get("figshare", {}).get("published") is True
        assert str(cit["version"]) == version
        # The DOIs are parsed identifiers, not text that a comment could supply.
        zenodo_doi = state["zenodo"]["doi"]
        figshare_doi = f"{state['figshare']['doi']}.v{sv.FIGSHARE_BASE_VERSION + 1}"
        assert zenodo_doi in ids and figshare_doi in ids
        assert "latest published release" in ids[zenodo_doi]
        # Only this release's record calls itself the latest; the one it revises no longer does.
        revised = f"10.5281/zenodo.{sv.ALLOWED_REVISIONS['zenodo']}"
        assert "latest published release" not in ids[revised]
        # ... and the Figshare version it was published as stays on record beside it.
        assert f"{state['figshare']['doi']}.v{sv.FIGSHARE_BASE_VERSION}" in ids
        assert sum("latest published release" in d for d in ids.values()) == 1
        # The CHANGELOG entry is marked published with the release date and both DOIs.
        released = str(cit["date-released"])
        assert released in head[0] and "published" in head[0] and "unreleased" not in head[0]
        entry = changelog.split(head[0], 1)[1].split("\n## [", 1)[0]
        assert zenodo_doi in entry and figshare_doi in entry
    else:
        # Until the release is published CITATION names an earlier one, and the CHANGELOG entry
        # says so.
        assert str(cit["version"]) != version and "unreleased" in head[0]
    prereg = json.loads((ART / "provenance.json").read_text())["prereg_version"]
    assert prereg.startswith("v0.6.0")  # the run's pre-registration, whatever the deposit
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
    # Exact allowlist (CTO #598 cond. 1): widen by one id, deliberately, per amendment.
    assert [a["id"] for a in rr] == ["RR-1", "RR-2"] and rr[0]["date"] == "2026-10-08"
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
        text = re.sub(r"(?<!\\)%.*", "", (ROOT / "paper" / rel).read_text())
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

    text = re.sub(r"(?<!\\)%.*", "", (ROOT / "paper" / "sections" / "corrections.tex").read_text())
    start = text.index("\\label{app:rr}")
    nxt = text.find("\\subsection", start)
    rr = " ".join(text[start : nxt if nxt != -1 else len(text)].split())
    for stale in ("re-creates", "re-create", "recreates", "still records"):
        assert stale not in rr, stale
    assert "no longer does" in rr and "does not record it" in rr


# RR-1's three text fields made false by the code retirement (CTO #585), corrected by RR-2.
RR1_STALE = {
    "RR-1.rerun_note": "re-run as documented re-creates the field",
    "RR-1.also_replaced_in_docs": "now shows LLM_KEY_SOURCE=<store>:<project>:<env>",
    "RR-1.out_of_scope": "is a separate decision raised with the CTO",
}


def test_rr2_corrects_rr1_text_only_and_leaves_rr1_byte_identical():
    """CTO #593 (a), #598: RR-2 is an appended text-only entry; RR-1 is unchanged byte for byte."""
    import hashlib
    import subprocess

    path = ROOT / "paper" / "data" / "run_record_amendments.json"
    raw = path.read_text()
    rr = json.loads(raw)["amendments"]
    old_raw = subprocess.run(
        ["git", "show", "ded9cfc:projects/perturb-seq-eval/paper/data/run_record_amendments.json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    old_rr1 = json.loads(old_raw)["amendments"]
    assert len(old_rr1) == 1 and rr[0] == old_rr1[0]
    # RR-1's serialized text is unchanged too: the file up to RR-1's closing brace is the old file's.
    head = old_raw[: old_raw.rindex("}", 0, old_raw.rindex("]"))]
    assert raw.startswith(head)
    rr2 = rr[1]
    assert rr2["id"] == "RR-2" and rr2["kind"] == "text-only" and rr2["files"] == []
    assert set(rr2["supersedes"]) == set(RR1_STALE)
    for field, stale in RR1_STALE.items():
        # the superseded RR-1 field really says the stale thing (else RR-2 corrects nothing)...
        assert stale in rr[0][field.split(".", 1)[1]], field
        # ...and RR-2 gives a real correction that does not repeat it
        new = rr2["supersedes"][field]
        assert isinstance(new, str) and len(new.split()) >= 12, field
        assert stale not in new, field
    assert set(json.loads(raw)) == {"amendments"}
    assert set(rr2) == {"id", "date", "source", "kind", "files", "supersedes", "rationale"}
    assert rr2["date"] == "2026-10-13" and "#598" in rr2["source"]
    # The entry is pinned (cond. 2, "corrections missing or trivial"): any edit to RR-2 is an RR-3.
    digest = hashlib.sha256(json.dumps(rr2, sort_keys=True, ensure_ascii=False).encode())
    assert digest.hexdigest() == "9fd352d98d470212511148eaf836145ca5c258a36aee5c71e7e4617ba17f2005"
    # Each correction states what is true now, and the code and docs agree with it.
    sup = {k: " ".join(v.split()).lower() for k, v in rr2["supersedes"].items()}
    assert "no longer does" in sup["RR-1.rerun_note"]
    assert "does not record the field" in sup["RR-1.rerun_note"]
    assert "c-key-source" in sup["RR-1.rerun_note"]
    assert "no longer sets llm_key_source" in sup["RR-1.also_replaced_in_docs"]
    for doc in ("README.md", "paper/README.md", "scripts/modal/app_v05.py"):
        assert doc.lower() in sup["RR-1.also_replaced_in_docs"], doc
        assert "LLM_KEY_SOURCE=" not in (ROOT / doc).read_text(), doc
    for named in (
        "not in the run files and not deposited",
        "unit-test fixtures",
        "pyproject.toml",
        "changelog",
        "cto #585",
    ):
        assert named in sup["RR-1.out_of_scope"], named
    assert "email" not in (ROOT / "pyproject.toml").read_text()
    pv_src = (ROOT / "src" / "perturb_eval" / "experiments" / "provenance.py").read_text()
    assert '"llm_key_source":' not in pv_src and "def parse_key_source" not in pv_src
    for v in sup.values():
        for bad in (
            "still records",
            "still writes",
            "separate decision",
            "open question",
            "re-creates",
        ):
            assert bad not in v, (bad, v)


_STALE_PATTERNS = (
    r"re-?creates?\s+(the\s+(llm_key_source\s+)?field|it\b)",
    r"llm_key_source\s*=\s*<store>",
    r"separate decision raised",
    r"still records the field",
)
_SCAN_SKIP = (".venv", "tests", "build", "artifacts", "paper/data", ".pytest_cache")


def _normalised(path):
    import re

    text = path.read_text(errors="ignore")
    if path.suffix == ".tex":  # LaTeX comments only; a '%' in Markdown is text
        text = re.sub(r"(?<!\\)%.*", "", text)
    text = text.replace("\\_", "_").replace("~", " ")
    text = re.sub(r"\\texttt\{([^}]*)\}", r"\1", text)
    text = re.sub(r"-\s+", "-", text)  # a hyphen broken across a line
    return " ".join(text.split()).lower()


def _scanned_docs():
    exts = ("*.md", "*.tex", "*.py", "*.cff", "*.yml")
    for path in sorted(p for e in exts for p in ROOT.rglob(e)):
        rel = path.relative_to(ROOT).as_posix()
        if not any(rel == s or rel.startswith(s + "/") for s in _SCAN_SKIP):
            yield rel, path


def test_rr1_stale_wording_is_not_presented_as_current():
    """CTO #598 cond. 2: no doc, paper source, script or metadata file repeats a superseded RR-1
    statement as current (normalised for case, LaTeX escapes, ~ and line-broken hyphens)."""
    import re

    scanned = dict(_scanned_docs())
    for must in (
        "README.md",
        "paper/README.md",
        "CHANGELOG.md",
        "CITATION.cff",
        "scripts/modal/app_v05.py",
        "paper/sections/corrections.tex",
    ):
        assert must in scanned, must  # the scan really covers the files RR-1 names
    for rel, path in scanned.items():
        text = _normalised(path)
        for pat in _STALE_PATTERNS:
            assert not re.search(pat, text), (rel, pat)


def test_stale_scan_normaliser_sees_through_formatting(tmp_path):
    import re

    cases = {
        "a.tex": "\\texttt{LLM\\_KEY\\_SOURCE=<store>:x:y} and Re-\ncreates~the field",
        "b.md": "Coverage 100% re-run as documented re-creates the field",
    }
    for name, body in cases.items():
        (tmp_path / name).write_text(body)
        text = _normalised(tmp_path / name)
        assert any(re.search(p, text) for p in _STALE_PATTERNS), name
    (tmp_path / "c.tex").write_text("% a re-run re-creates the field\nclean")
    assert not any(re.search(p, _normalised(tmp_path / "c.tex")) for p in _STALE_PATTERNS)


# ---- release state file, lineage records and the deposit-time sequence (0.6.3 is the next
# version of the published 0.6.2 records on both venues, approvals row 45, 2026-11-25) ----
def _sequence_steps(text):
    seq = text[text.index("# Deposit-time sequence") : text.index("\nfiles:")]
    lines = seq.splitlines()
    first = next(i for i, ln in enumerate(lines) if re.match(r"#\s+1\.", ln))
    steps, cur = {}, None
    for ln in lines[first:]:
        m = re.match(r"#\s+(\d+)\.", ln)
        if m:
            cur = int(m.group(1))
        steps.setdefault(cur, []).append(ln)
    return seq, {k: " ".join(v) for k, v in steps.items()}


def test_release_has_its_own_config_anchored_state_and_never_reuses_a_lineage_one(tmp_path):
    sv = _load("scripts/publish/submit_to_venues.py", "sv_state")
    cfg = sv.PublishConfig.load(ROOT / "publish.yml")
    assert cfg.state_file == "publish.state.v063.json"
    assert sv.resolve_state_path(None, cfg) == ROOT / "publish.state.v063.json"  # anchored to cfg
    assert sv.resolve_state_path(Path("x.json"), cfg) == Path("x.json")  # --state still wins
    old = json.loads((ROOT / "publish.state.json").read_text())
    assert old["zenodo"]["deposit_id"] == 19748260 and old["zenodo"]["published"] is True
    assert old["figshare"]["article_id"] == 32086920 and old["figshare"]["published"] is True
    new = sv.resolve_state_path(None, cfg)
    if new.exists():  # a superseded id may appear only as the permitted revision target
        st = json.loads(new.read_text())
        zen, fig = st.get("zenodo", {}), st.get("figshare", {})
        assert zen.get("deposit_id") not in sv.SUPERSEDED_RECORDS["zenodo"]
        if fig.get("article_id") in sv.SUPERSEDED_RECORDS["figshare"]:
            assert fig["article_id"] == fig.get("revision_of") == sv.ALLOWED_REVISIONS["figshare"]
    import dataclasses

    import pytest

    for bad in ("../elsewhere.json", "/tmp/abs.json"):
        with pytest.raises(ValueError, match="inside"):
            sv.resolve_state_path(None, dataclasses.replace(cfg, state_file=bad))
    (tmp_path / "real.json").write_text("{}")
    (tmp_path / "link.json").symlink_to(tmp_path / "real.json")
    with pytest.raises(ValueError, match="inside"):
        sv.resolve_state_path(None, dataclasses.replace(cfg, root=tmp_path, state_file="link.json"))
    (tmp_path / "publish.yml").write_text(
        (ROOT / "publish.yml")
        .read_text()
        .replace("state_file: publish.state.v063.json", "state_file:")
    )
    assert sv.PublishConfig.load(tmp_path / "publish.yml").state_file == ""


def test_directory_zips_are_byte_reproducible(tmp_path):
    sv = _load("scripts/publish/submit_to_venues.py", "sv_zip")
    src = tmp_path / "d"
    (src / "sub").mkdir(parents=True)
    (src / "b.txt").write_text("b")
    (src / "sub" / "a.txt").write_text("a")
    sv._zip_directory(src, tmp_path / "one.zip")
    import os
    import time

    os.utime(src / "b.txt", (time.time() + 3600, time.time() + 3600))  # a later mtime
    sv._zip_directory(src, tmp_path / "two.zip")
    assert sv._md5(tmp_path / "one.zip") == sv._md5(tmp_path / "two.zip")


def test_deposit_sequence_names_the_two_revisions_and_carries_no_raw_recipes():
    """CTO #647: the gated submitter is the implementation; the sequence names steps and never
    restores the deleted raw API recipes for operations on a published DOI."""
    text = (ROOT / "publish.yml").read_text()
    seq, steps = _sequence_steps(text)
    header = seq.split("#   1.")[0]
    assert "NEW VERSION" in header and "ALLOWED_REVISIONS" in header
    assert "PublishedRecordError" in header and "no raw API recipes" in header
    for raw in ("api.figshare.com", "zenodo.org/api", "actions/newversion", "curl ", "requests."):
        assert raw not in seq, raw
    assert "no POST/PUT/PATCH/DELETE" in steps[2]
    assert "commit it before step 4" in steps[3] and "UNPUBLISHED" in steps[3]
    assert "SEPARATE go to publish" in steps[4]
    assert "DraftRequiredError" in steps[4] and "expected_author" in steps[4]
    step5 = " ".join(steps[5].replace("#", " ").split())
    for named in (
        'CITATION.cff `version: "0.6.3"`',
        "date-released",
        "identifiers",
        "Figshare v9",
        'drop "the latest published release" from the 24518637 entry',
        "CHANGELOG 0.6.3 entry",
        "metadata-only",
        "isIdenticalTo",
    ):
        assert named in step5, named


def test_figshare_author_provenance_is_declared():
    """CTO #643: the Figshare author comes from the account profile, which the repo cannot assert;
    the deliberate Zenodo/Figshare name-form difference is written down where re-runs are documented."""
    for doc in ("README.md", "paper/README.md"):
        text = " ".join((ROOT / doc).read_text().replace("#", " ").split())
        assert "on Figshare the author comes from the depositing account's profile" in text, doc
        assert "a publish run checks it against publish.yml expected_author" in text, doc
        assert 'Zenodo "Mo, Mang-yin"' in text and 'Figshare "Mang-yin Mo"' in text, doc
        assert "do not re-add authors to the Figshare payload" in text, doc


def test_each_guard_layer_refuses_on_its_own(tmp_path, monkeypatch):
    """Every layer refuses by itself, so removing one layer is caught (not only the others)."""
    import pytest

    sv = _load("scripts/publish/submit_to_venues.py", "sv_layers")
    for venue, bad in (("zenodo", 20060974), ("figshare", 99), ("osf", 1)):
        with pytest.raises(sv.PublishedRecordError):
            sv._revision_target(venue, {"revision_of": bad})
    assert sv._revision_target("zenodo", {}) is None
    with pytest.raises(sv.PublishedRecordError):
        sv._refuse_superseded("figshare", None, allow=99)
    with pytest.raises(sv.PublishedRecordError):
        sv._refuse_superseded("zenodo", 24518637, allow=None)
    sv_, zsub, zcalls, _, _ = _submitter(
        monkeypatch, tmp_path, "zenodo", {}, routes=_revision_routes()
    )
    with pytest.raises(sv_.PublishedRecordError):
        zsub._new_version_of(20060974)
    sv_, fsub, fcalls, _, _ = _submitter(
        monkeypatch, tmp_path, "figshare", {}, routes=_revision_routes()
    )
    with pytest.raises(sv_.PublishedRecordError):
        fsub._remove_inherited_files(34562538)
    assert zcalls == [] and fcalls == []
    # A revision config must not resume a draft recorded for something else (each venue).
    zstate = {"zenodo": {"deposit_id": 777777, "bucket": "https://b/X"}}  # no revision_of
    sv_, zsub, zcalls, _, _ = _submitter(
        monkeypatch, tmp_path, "zenodo", zstate, routes=_revision_routes()
    )
    with pytest.raises(sv_.PublishedRecordError, match="not the new version"):
        zsub.submit([])
    assert zcalls == []


# ---- gaps found by the test review's mutations (T1-T18) ----
def _assert_no_authors(calls):
    for m, u, kw in calls:
        if isinstance(u, str):
            assert "/authors" not in u, u
        body = kw.get("json") if isinstance(kw, dict) else None
        if isinstance(body, dict):
            assert "authors" not in body, (m, u)


def test_already_published_revisions_are_never_touched_again(tmp_path, monkeypatch):
    import pytest

    for venue, state in (("zenodo", ZSTATE), ("figshare", FSTATE)):
        st = json.loads(json.dumps(state))
        st[venue]["published"] = True
        for dry in (True, False):
            sv, sub, calls, state_path, _ = _submitter(
                monkeypatch,
                tmp_path,
                venue,
                st,
                dry_run=dry,
                routes=_revision_routes(world=_prepared_world()),
            )
            with pytest.raises(sv.PublishedRecordError, match="already published"):
                sub.submit([])
            assert calls == [], (venue, dry)
            assert json.loads(state_path.read_text()) == st


def test_resumed_dry_runs_never_write_to_the_published_record_or_publish(tmp_path, monkeypatch):
    sv, sub, calls, state_path, _ = _submitter(
        monkeypatch, tmp_path, "zenodo", ZSTATE, routes=_revision_routes(world=_prepared_world())
    )
    sub.submit([])
    assert not any("24518637" in u for _, u, _ in calls)
    puts = [u for m, u, _ in calls if m == "put"]
    assert puts == [f"{ZEN_BASE}/deposit/depositions/{NEW_ZEN}"]
    assert not any(m == "delete" for m, _, _ in calls)  # flag set: no re-removal
    assert not any(m == "post" and u.endswith("publish") for m, u, _ in calls)
    assert "published" not in json.loads(state_path.read_text())["zenodo"]
    sv, sub, calls, state_path, _ = _submitter(
        monkeypatch, tmp_path, "figshare", FSTATE, routes=_revision_routes(world=_prepared_world())
    )
    sub.submit([])
    assert not any(m == "post" and u.endswith("publish") for m, u, _ in calls)
    assert not any(u.endswith("/reserve_doi") for _, u, _ in calls)
    assert not any(m == "delete" for m, _, _ in calls)
    _assert_no_authors(calls)
    assert "published" not in json.loads(state_path.read_text())["figshare"]


def test_public_snapshot_compares_files_too_and_is_unauthenticated(tmp_path, monkeypatch):
    import pytest

    routes = _revision_routes()
    seq = ["old", "new"]

    def public(url, kw):
        return {
            "version": 8,
            "files": [
                {"name": "paper.pdf", "supplied_md5": seq.pop(0) if len(seq) > 1 else seq[0]}
            ],
        }

    routes[("get", f"{FIG_BASE}/articles/32086920")] = public
    sv, sub, calls, _, _ = _submitter(monkeypatch, tmp_path, "figshare", {}, routes=routes)
    with pytest.raises(sv.PublishedRecordError, match="PUBLIC version changed"):
        sub.submit([])
    assert not any(m == "delete" for m, _, _ in calls)
    sv, sub, calls, _, _ = _submitter(monkeypatch, tmp_path, "figshare", {})
    sub.submit([])
    pub = [kw for m, u, kw in calls if m == "get" and u == f"{FIG_BASE}/articles/32086920"]
    assert pub and all("headers" not in kw for kw in pub)  # the PUBLIC view, never with the token
    first_write = next(i for i, c in enumerate(calls) if c[0] in ("put", "delete"))
    assert any(c[1] == f"{FIG_BASE}/articles/32086920" for c in calls[:first_write])
    last_write = max(i for i, c in enumerate(calls) if c[0] in ("put", "delete", "upload"))
    assert any(c[1] == f"{FIG_BASE}/articles/32086920" for c in calls[last_write + 1 :])


def test_plain_figshare_resume_puts_only_to_its_own_article(tmp_path, monkeypatch):
    st = {"figshare": {"article_id": 777, "doi": "10.6084/m9.figshare.777", "prepared": True}}
    sv, sub, calls, _, _ = _submitter(monkeypatch, tmp_path, "figshare", st, vcfg_patch=PLAIN)
    sub.submit([])
    assert [u for m, u, _ in calls if m == "put"] == [f"{FIG_BASE}/account/articles/777"]
    assert not any("32086920" in u for _, u, _ in calls if isinstance(u, str))


def test_publish_run_keeps_the_doi_and_never_reserves_one_on_32086920(tmp_path, monkeypatch):
    sv, sub, calls, state_path, _ = _submitter(
        monkeypatch,
        tmp_path,
        "figshare",
        FSTATE,
        dry_run=False,
        routes=_revision_routes(world=_prepared_world()),
    )
    sub.submit([])
    assert not any(u.endswith("/reserve_doi") for _, u, _ in calls)
    assert json.loads(state_path.read_text())["figshare"]["doi"] == "10.6084/m9.figshare.32086920"
    _assert_no_authors(calls)


def test_open_draft_check_needs_both_conditions(tmp_path, monkeypatch):
    import pytest

    for bad in (
        {"submitted": True, "state": "unsubmitted"},
        {"submitted": False, "state": "inprogress"},
    ):
        sv, sub, calls, _, _ = _submitter(
            monkeypatch, tmp_path, "zenodo", {}, routes=_revision_routes(draft=bad)
        )
        with pytest.raises(sv.PublishedRecordError, match="not an open draft"):
            sub.submit([])
        assert not any(m == "delete" for m, _, _ in calls)


def test_figshare_state_naming_another_article_under_the_revision_is_refused(tmp_path, monkeypatch):
    import pytest

    st = {"figshare": {"article_id": 34562538, "revision_of": 32086920}}
    sv, sub, calls, _, _ = _submitter(monkeypatch, tmp_path, "figshare", st)
    with pytest.raises(sv.PublishedRecordError, match="not the revision of"):
        sub.submit([])
    assert calls == []


def test_osf_superseded_records_and_any_revision_are_refused(tmp_path, monkeypatch):
    import pytest

    for state, patch in (
        ({"osf": {"project_id": "wmeuy"}}, None),
        ({"osf": {"project_id": "abcde", "preprint_id": "dhu4z_v1"}}, None),
        ({}, {"revision_of": 1}),
    ):
        sv, sub, calls, _, _ = _submitter(monkeypatch, tmp_path, "osf", state, vcfg_patch=patch)
        with pytest.raises(sv.PublishedRecordError):
            sub.submit([])
        assert calls == [], state


def test_single_venue_dry_runs_never_publish_through_main(tmp_path, monkeypatch):
    for venue, state in (("zenodo", ZSTATE), ("figshare", FSTATE)):
        (tmp_path / venue).mkdir()
        rc, calls, cfgdir, _, _ = _run_main(
            monkeypatch,
            tmp_path / venue,
            [venue, "--dry-run"],
            state=state,
            routes=_revision_routes(world=_prepared_world()),
        )
        assert rc == 0, venue
        assert not any(m == "post" and u.endswith("publish") for m, u, _ in calls), venue
        assert (
            "published" not in json.loads((cfgdir / "publish.state.v063.json").read_text())[venue]
        )


def test_main_reports_a_file_mismatch_and_the_next_venue_still_runs(tmp_path, monkeypatch):
    world = _prepared_world()
    world["zen"] = {"leftover.zip": "x"}  # the zenodo draft holds a file the release does not
    rc, calls, _, _, _ = _run_main(
        monkeypatch,
        tmp_path,
        ["all", "--dry-run"],
        state={**ZSTATE, **FSTATE},
        routes=_revision_routes(world=world),
    )
    assert rc == 1
    assert any("/account/articles/32086920" in u for _, u, _ in calls)  # figshare still ran


def test_a_disabled_venue_named_directly_makes_no_request(tmp_path, monkeypatch, capsys):
    rc, calls, _, _, _ = _run_main(monkeypatch, tmp_path, ["osf"])
    assert calls == [] and "disabled" in capsys.readouterr().out


def test_superseded_ids_are_refused_whatever_their_type():
    """Each layer on its own: _refuse_superseded compares as strings; _state_id rejects non-ints."""
    import pytest

    sv = _load("scripts/publish/submit_to_venues.py", "sv_types")
    for venue, i in (
        ("figshare", "32086920"),
        ("zenodo", "24518637"),
        ("zenodo", "24430429"),
        ("zenodo", "20074427"),
        ("zenodo", 19716140),
    ):
        with pytest.raises(sv.PublishedRecordError):
            sv._refuse_superseded(venue, i)
    for bad in ("23500555", 23500555.0, True):
        with pytest.raises(sv.PublishedRecordError, match="not an integer"):
            sv._state_id("zenodo", "deposit_id", bad)
    assert sv._state_id("zenodo", "deposit_id", None) is None


def test_figshare_publish_waits_until_every_file_is_available(tmp_path, monkeypatch):
    """CTO #651: a published DOI cannot be fixed by replacing a file, so the publish run refuses
    while any file is still processing; the dry run does not wait."""
    import pytest

    f = tmp_path / "v060_run_artifacts.zip"
    f.write_bytes(b"z")
    entry = {"name": "v060_run_artifacts.zip", "path": f, "md5": "m", "size": 1}
    for status, ok in (("ic_success", False), ("available", True)):
        world = _prepared_world()
        world["fig"] = {"v060_run_artifacts.zip": "m"}
        world["fig_status"] = {"v060_run_artifacts.zip": status}
        sv, sub, calls, state_path, _ = _submitter(
            monkeypatch,
            tmp_path,
            "figshare",
            FSTATE,
            dry_run=False,
            routes=_revision_routes(world=world),
        )
        if ok:
            sub.submit([entry])
            assert any(m == "post" and u.endswith("/32086920/publish") for m, u, _ in calls)
        else:
            with pytest.raises(sv.DraftMismatchError, match="still processing"):
                sub.submit([entry])
            assert not any(m == "post" and u.endswith("/publish") for m, u, _ in calls)
    world = _prepared_world()
    world["fig"] = {"v060_run_artifacts.zip": "m"}
    world["fig_status"] = {"v060_run_artifacts.zip": "ic_success"}
    sv, sub, calls, _, _ = _submitter(
        monkeypatch, tmp_path, "figshare", FSTATE, routes=_revision_routes(world=world)
    )
    sub.submit([entry])  # the dry run is not blocked by processing


def _files(tmp_path, *names):
    out = []
    for n in names:
        p = tmp_path / n
        p.write_bytes(n.encode())
        out.append({"name": n, "path": p, "md5": f"md5-{n}", "size": 1})
    return out


def test_availability_reads_the_listing_after_this_runs_uploads(tmp_path, monkeypatch):
    """A1: a file uploaded in this same publish run must be seen still processing (the check
    reads the GET made after the uploads, not the listing taken before them)."""
    import pytest

    entries = _files(tmp_path, "v060_run_artifacts.zip")
    world = _prepared_world()  # nothing on the article yet: the run uploads it
    world["fig_status"] = {"v060_run_artifacts.zip": "ic_success"}
    sv, sub, calls, _, _ = _submitter(
        monkeypatch,
        tmp_path,
        "figshare",
        FSTATE,
        dry_run=False,
        routes=_revision_routes(world=world),
    )
    with pytest.raises(sv.DraftMismatchError, match="still processing"):
        sub.submit(entries)
    assert any(c[0] == "upload" for c in calls)  # uploaded in this run ...
    assert not any(m == "post" and u.endswith("/publish") for m, u, _ in calls)  # ... not published


def test_availability_refuses_a_missing_status_and_checks_every_file(tmp_path, monkeypatch):
    """A2/A3: an absent status is not 'available'; and every file is checked, not only one."""
    import pytest

    names = ("paper.pdf", "v060_run_artifacts.zip", "supplement.zip")
    for statuses, pending in (
        ({"v060_run_artifacts.zip": "__missing__"}, "('v060_run_artifacts.zip', None)"),
        ({"v060_run_artifacts.zip": "ic_success"}, "('v060_run_artifacts.zip', 'ic_success')"),
    ):
        entries = _files(tmp_path, *names)
        world = _prepared_world()
        world["fig"] = {e["name"]: e["md5"] for e in entries}
        world["fig_status"] = statuses
        sv, sub, calls, _, _ = _submitter(
            monkeypatch,
            tmp_path,
            "figshare",
            FSTATE,
            dry_run=False,
            routes=_revision_routes(world=world),
        )
        with pytest.raises(sv.DraftMismatchError, match="still processing") as err:
            sub.submit(entries)
        assert pending in str(err.value)
        assert "paper.pdf" not in str(err.value) and "supplement.zip" not in str(err.value)
        assert not any(m == "post" and u.endswith("/publish") for m, u, _ in calls)


def test_availability_also_guards_the_plain_path(tmp_path, monkeypatch):
    """A4: the check is shared code, not part of the revision-only branch."""
    import pytest

    entries = _files(tmp_path, "paper.pdf")
    routes = {
        ("get", "/account/articles/777"): {
            "files": [
                {"name": "paper.pdf", "supplied_md5": "md5-paper.pdf", "status": "ic_success"}
            ],
            "authors": [{"full_name": "Mang-yin Mo"}],
        }
    }
    st = {"figshare": {"article_id": 777, "doi": "10.6084/m9.figshare.777", "prepared": True}}
    sv, sub, calls, _, _ = _submitter(
        monkeypatch, tmp_path, "figshare", st, dry_run=False, vcfg_patch=PLAIN, routes=routes
    )
    with pytest.raises(sv.DraftMismatchError, match="still processing"):
        sub.submit(entries)
    assert not any(m == "post" and u.endswith("/777/publish") for m, u, _ in calls)


def _norm(s: str) -> str:
    return " ".join(s.replace("\\\\", " ").split()).rstrip(".")


def test_every_title_surface_carries_the_paper_title():
    """Amendment 5 retitled the paper (CTO #896) and Amendment 6 retitled it again (approvals
    row 40). Every surface that names the work carries the manuscript's \\title verbatim, so a
    retitle cannot reach some surfaces and not others (QG Q6: publish.yml, the deposit title, was
    missed once). The pre-registration states the title in its header and in the governing
    amendment's rule (A6-2, the last amendment that sets a title); A5-2 keeps the superseded
    title verbatim, as history."""
    tex = (ROOT / "paper" / "paper.tex").read_text()
    title = _norm(re.search(r"\\title\{(.*?)\}\n", tex, re.S).group(1))
    pdftitle = _norm(re.search(r"pdftitle=\{(.*?)\}\}", tex, re.S).group(1))
    prereg = (ROOT / "paper" / "PREREGISTRATION.md").read_text()
    rules = re.findall(
        r"^### (A\d-\d) Amended rule \(title\)\nThe title becomes: \*(.*?)\*",
        prereg,
        re.MULTILINE | re.DOTALL,
    )
    surfaces = {
        "pdftitle": pdftitle,
        "CITATION.cff": _norm(yaml.safe_load((ROOT / "CITATION.cff").read_text())["title"]),
        "publish.yml": _norm(_cfg()["title"]),
        "README.md": _norm(
            re.search(r'\*\*"(.*?)"\*\*', (ROOT / "README.md").read_text(), re.S).group(1)
        ),
        "paper/README.md": _norm(
            (ROOT / "paper" / "README.md").read_text().splitlines()[0].removeprefix("# Paper — ")
        ),
        "docs/THESIS.md": _norm(
            (ROOT / "docs" / "THESIS.md").read_text().splitlines()[0].removeprefix("# Thesis — ")
        ),
        "SUBMISSION.md paste block": _norm(
            re.search(
                r"^Title:\s+(.*)$", (ROOT / "paper" / "SUBMISSION.md").read_text(), re.M
            ).group(1)
        ),
        "PREREGISTRATION.md header": _norm(
            re.search(r"^\*\*Paper:\*\* \*(.*?)\*", prereg, re.M | re.S).group(1)
        ),
        "PREREGISTRATION.md A6-2 (governing amendment)": _norm(rules[-1][1]),
    }
    # one "The title becomes" rule per retitling amendment, in order; the last one governs
    assert [h for h, _ in rules] == ["A5-2", "A6-2"], [h for h, _ in rules]
    assert _norm(rules[0][1]) != title  # A5-2 is quoted history, not rewritten to the new title
    wrong = {k: v for k, v in surfaces.items() if v != title}
    assert not wrong, f"title differs from paper.tex \\title on: {sorted(wrong)}"


def test_arxiv_override_keeps_every_result_token_and_states_its_length():
    """QG B16/B17: the venue override is hand-derived, and the tooling checks only its limits. Pin
    the tokens the derivation promises to keep, and the length its comment and the runbook state."""
    import tomllib

    cfg = (ROOT / "paper" / "arxiv.toml").read_text()
    ov = tomllib.loads(cfg)["abstract"]
    assert len(ov) <= 1920 and ov.isascii()
    for tok in (
        "0.286",
        "> 0.4",
        "Four of the five hypotheses are supported",
        "the cross-dataset transfer hypothesis is not",
        "every hypothesis could be evaluated",
        # the five hypotheses, named by what they claim (HACA-119)
        "low attainable error on Adamson 2016",
        "and on Norman 2019",
        "varied backbone choice by the Architect",
        "the rank correlation of each TDI component with error",
        "cross-dataset transfer of a calibrated TDI",
        "at the pre-registered level",
        "41 held-out",
        "21 Adamson",
        "15 Norman",
        "5 Norman",
        "27 model fits",
        # restored after the self-containment pass dropped or weakened them
        "a group of role-specialised agents",
        "(Haiku 4.5, Sonnet 5.5), the served model asserted per call",
        "every prompt carries the prior round's held-out error",
        "Haiku 4.5",
        "Sonnet 5.5",
        "CATTS",
        "2602.12276",
        "this is exploratory",
    ):
        assert tok in ov, tok
    assert not re.search(r"\bgates?\b", ov.replace("can gate its compute", ""))
    # HACA-119: the venue abstract names hypotheses in words, never by label or status word
    assert not re.search(r"\bH[1-5]\b|PASS|FAIL|UNEVALUATED|unevaluated", ov)
    # Self-containment: an abbreviation is defined at first use and then used again (one used
    # once is written out instead), no metric acronym appears undefined, the first rho is named,
    # the two datasets are said to be screens, and the role and model terms are glossed.
    defined = re.findall(r"\(([A-Z]{2,})\)", ov)
    assert defined == ["ACE", "TDI"], defined
    for abbr in defined:
        assert ov.index(f"({abbr})") == re.search(rf"\b{abbr}\b", ov).start() - 1, abbr
        assert len(re.findall(rf"\b{abbr}\b", ov)) >= 2, abbr
    assert not re.search(r"\b(CSD|WFR|LLM|HVG|MSD|CI)\b|Delta|singleton|doublet", ov)
    assert ov.index("Spearman's $\\rho$") == ov.index("$\\rho$") - len("Spearman's ")
    assert "on Norman 2019 (screens of the K562 cell line)" in ov and "from these screens" in ov
    assert "Perturb-seq (single-cell CRISPR screen)" in ov
    assert "it is not evidence that confidence anticipates difficulty" in ov  # no dangling "it"
    assert "that it anticipates" not in ov
    assert "the Architect (the model-choosing agent)" in ov
    assert "ranks tasks by error, meeting its criterion" in ov  # the antecedent of "The pass"
    assert f"This version is {len(ov)} characters, 0 non-ASCII" in cfg
    sub = (ROOT / "paper" / "SUBMISSION.md").read_text()
    assert f"The override is {len(ov)} characters, 0 non-ASCII" in sub


ARXIV_OTHER_DECIMALS = {"4.5", "5.5", "2602.12276"}  # the two model versions, the CATTS arXiv id


def _generated_macros() -> dict[str, str]:
    text = (ROOT / "paper/sections/generated_numbers.tex").read_text() + (
        ROOT / "paper/sections/generated_exploratory.tex"
    ).read_text()
    return dict(
        re.findall(r"^\\newcommand\{\\((?:res|expl)[A-Za-z]+)\}\{(.*)\}$", text, re.MULTILINE)
    )


def _arxiv_number_problems(ov: str, m: dict[str, str]) -> list[str]:
    """The venue abstract is typed by hand, so each result number in it is tied to the macro the
    manuscript prints, and every other decimal must be on a short explicit allow-list."""
    expected = [
        f"$\\rho$ = {m['resHFiveRho']} against > {m['resHFiveThreshold']}",
        (
            f"$\\rho$ = {m['explAdaConfRZeroMsdRho']} on Adamson and "
            f"{m['explNorConfRZeroMsdRho']} on Norman"
        ),
    ]
    problems = [f"missing: {e}" for e in expected if ov.count(e) != 1]
    rest = ov
    for e in expected:
        rest = rest.replace(e, "")
    decimals = re.findall(r"(?<![\w.])-?\d*\.\d+", rest)
    problems += [f"unlisted decimal: {d}" for d in decimals if d not in ARXIV_OTHER_DECIMALS]
    problems += [
        f"allow-listed decimal not used: {d}"
        for d in sorted(ARXIV_OTHER_DECIMALS)
        if d not in decimals
    ]
    return problems


def test_arxiv_override_numbers_are_the_generated_macros():
    import tomllib

    ov = tomllib.loads((ROOT / "paper" / "arxiv.toml").read_text())["abstract"]
    m = _generated_macros()
    for name in (
        "resHFiveRho",
        "resHFiveThreshold",
        "explAdaConfRZeroMsdRho",
        "explNorConfRZeroMsdRho",
    ):
        assert re.fullmatch(r"\d\.\d+", m[name]), (name, m[name])  # plain and non-negative here
    assert _arxiv_number_problems(ov, m) == []
    # the guard is live: a changed macro, a retyped number and a new decimal are each caught
    assert _arxiv_number_problems(ov, {**m, "resHFiveRho": "0.287"})
    assert _arxiv_number_problems(ov, {**m, "explNorConfRZeroMsdRho": "0.215"})
    assert _arxiv_number_problems(ov.replace("0.003 on Adamson", "0.004 on Adamson"), m)
    assert _arxiv_number_problems(ov + " (0.82 elsewhere)", m) == ["unlisted decimal: 0.82"]
    # wording the override must carry after the row-39 reframe and its quality gate
    for tok in (
        "the mean confidence stated before any feedback does not rank tasks",
        "in both screens. This too is exploratory; no claim is made.",
        "The pass is consistent with",
        "it is not evidence that",
        "A one-round probe and configuration recommender are specified, not evaluated.",
    ):
        assert tok in ov, tok
    assert "supported result" not in ov
    assert not re.search(r"(?<!mean )confidence stated before any feedback", ov)


def test_v052_record_20074427_is_now_merely_superseded(tmp_path, monkeypatch):
    """0.6.3 revises 0.6.2 (24518637); the v0.5.2 record 20074427, an earlier revision
    target, is an ordinary superseded record: every write to it is refused."""
    import pytest

    sv = _load("scripts/publish/submit_to_venues.py", "sv_v052")
    assert {20074427, 23422745, 24430429, 24518637} <= sv.SUPERSEDED_RECORDS["zenodo"]
    assert 20074427 not in sv.ALLOWED_REVISIONS.values()
    with pytest.raises(sv.PublishedRecordError):
        sv._revision_target("zenodo", {"revision_of": 20074427})
    with pytest.raises(sv.PublishedRecordError):
        sv._refuse_superseded("zenodo", 20074427, allow=sv.ALLOWED_REVISIONS["zenodo"])
    with pytest.raises(sv.PublishedRecordError):
        sv._refuse_superseded("zenodo", 20074427, allow=20074427)
    sv_, zsub, calls, _, _ = _submitter(
        monkeypatch, tmp_path, "zenodo", {}, routes=_revision_routes()
    )
    with pytest.raises(sv_.PublishedRecordError):
        zsub._new_version_of(20074427)
    assert calls == []
    for state, patch in (
        ({}, {"revision_of": 20074427}),
        ({"zenodo": {"deposit_id": 20074427}}, None),
        ({"zenodo": {"deposit_id": 20074427, "revision_of": 20074427}}, None),
    ):
        sv_, zsub, calls, state_path, _ = _submitter(
            monkeypatch, tmp_path, "zenodo", state, vcfg_patch=patch
        )
        with pytest.raises(sv_.PublishedRecordError):
            zsub.submit([])
        assert calls == [], (state, patch, calls)
        assert json.loads(state_path.read_text()) == state


def test_lineage_records_agree_with_the_permitted_revisions():
    """The tracked 0.6.2 record is what 0.6.3 revises: its ids are ALLOWED_REVISIONS, its own
    revision target (0.6.1) is merely superseded, and the Figshare base is the version after
    its recorded public baseline."""
    sv = _load("scripts/publish/submit_to_venues.py", "sv_lineage")
    v062 = json.loads((ROOT / "publish.state.v062.json").read_text())
    zen, fig = v062["zenodo"], v062["figshare"]
    assert zen["published"] is True and fig["published"] is True
    assert sv.ALLOWED_REVISIONS["zenodo"] == zen["deposit_id"]
    assert zen["revision_of"] == 24430429
    assert zen["revision_of"] in sv.SUPERSEDED_RECORDS["zenodo"]
    assert zen["revision_of"] != sv.ALLOWED_REVISIONS["zenodo"]
    assert sv.ALLOWED_REVISIONS["figshare"] == fig["article_id"] == fig["revision_of"]
    assert isinstance(fig["public_baseline"], list) and isinstance(fig["public_baseline"][0], int)
    assert sv.FIGSHARE_BASE_VERSION == fig["public_baseline"][0] + 1
    rel = _cfg()["venues"]["zenodo"]["related_identifiers"]
    assert {
        "identifier": f"10.5281/zenodo.{sv.ALLOWED_REVISIONS['zenodo']}",
        "relation": "isNewVersionOf",
        "scheme": "doi",
    } in rel
    assert sv.LINEAGE_STATE_FILES == frozenset(
        {
            "publish.state.json",
            "publish.state.v060.json",
            "publish.state.v061.json",
            "publish.state.v062.json",
        }
    )


def test_the_published_062_release_stays_on_record_while_063_is_only_prepared():
    """0.6.2 is public and 0.6.3 is not (approvals rows 43 and 45). Until 0.6.3 is published,
    CITATION.cff names 0.6.2 with the DOIs of its tracked lineage record, the CHANGELOG keeps a
    published 0.6.2 entry with both DOIs below an unreleased 0.6.3 entry, and no surface gives
    0.6.3 a DOI or says that 0.6.2 holds the reworded manuscript."""
    sv = _load("scripts/publish/submit_to_venues.py", "sv_062_on_record")
    v062 = json.loads((ROOT / "publish.state.v062.json").read_text())
    assert v062["zenodo"]["published"] is True and v062["figshare"]["published"] is True
    zenodo_doi = v062["zenodo"]["doi"]
    figshare_doi = f"{v062['figshare']['doi']}.v{v062['figshare']['public_baseline'][0] + 1}"
    assert (zenodo_doi, figshare_doi) == (
        "10.5281/zenodo.24518637",
        "10.6084/m9.figshare.32086920.v8",
    )
    state_path = sv.resolve_state_path(None, sv.PublishConfig.load(ROOT / "publish.yml"))
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    if state.get("zenodo", {}).get("published"):
        return  # 0.6.3 is out: test_keywords_and_citation_version_... checks the surfaces then
    cit = yaml.safe_load((ROOT / "CITATION.cff").read_text())
    assert _cfg()["version"] == "0.6.3" and str(cit["version"]) == "0.6.2"
    assert str(cit["date-released"]) == "2026-11-25"
    ids = {i["value"]: i.get("description", "") for i in cit["identifiers"]}
    assert "latest published release" in ids[zenodo_doi] and figshare_doi in ids
    # exactly one record is the latest, and it is not the 0.6.1 record that 0.6.2 revised
    assert sum("latest published release" in d for d in ids.values()) == 1
    revised = f"10.5281/zenodo.{v062['zenodo']['revision_of']}"
    assert revised == "10.5281/zenodo.24430429" and "latest published release" not in ids[revised]
    assert not any("0.6.3" in d for d in ids.values())  # no identifier is claimed for 0.6.3
    changelog = (ROOT / "CHANGELOG.md").read_text()
    heads = [ln for ln in changelog.splitlines() if ln.startswith("## [0.6.")]
    assert heads[0].startswith("## [0.6.3]") and "unreleased" in heads[0]
    assert heads[1] == "## [0.6.2] — 2026-11-25 (manuscript revision; published)"
    e063, e062 = (changelog.split(h, 1)[1].split("\n## [", 1)[0] for h in heads[:2])
    assert zenodo_doi in e062 and figshare_doi in e062 and "07a5e57b" in e062
    assert "before** the self-contained rewrite" in e062
    assert "It is not published" in " ".join(e063.split())
    # the next Figshare DOI does not exist yet, on any surface or as a parsed identifier
    surfaces = {
        rel: " ".join((ROOT / rel).read_text().split())
        for rel in ("CHANGELOG.md", "CITATION.cff", "README.md", "paper/SUBMISSION.md")
    }
    for rel, text in surfaces.items():
        assert "figshare.32086920.v9" not in text, rel
    assert not any(k.endswith(".v9") for k in ids)
    # 0.6.2 holds the wording BEFORE the rewrite, said where a reader meets the 0.6.2 record
    assert (
        "in the wording it had before the hypotheses and amendments were named in words"
        in (surfaces["README.md"])
    )
    assert "`0.6.2` holds it in the wording before that rewrite" in surfaces["paper/SUBMISSION.md"]
    assert "before the self-contained rewrite of the wording that is prepared as 0.6.3" in (
        surfaces["CITATION.cff"].replace("# ", "")
    )
    # "not published" is checked in the sentence that names 0.6.3, not anywhere in the file
    assert "prepared as archive version 0.6.3 and is **not published**" in surfaces["README.md"]
    assert "`0.6.3` is prepared and **not published**" in surfaces["paper/SUBMISSION.md"]
    assert "**`0.6.3`, prepared, not published**" in surfaces["paper/SUBMISSION.md"]
    for rel in ("README.md", "paper/SUBMISSION.md"):
        assert zenodo_doi in surfaces[rel], rel


def test_a_lineage_state_file_is_refused_from_either_source(tmp_path, monkeypatch):
    """No run may resolve its state to a published lineage record, whether --state names it or
    publish.yml's state_file does; main() raises before any request."""
    import dataclasses

    import pytest

    sv = _load("scripts/publish/submit_to_venues.py", "sv_lineage_guard")
    cfg = sv.PublishConfig.load(ROOT / "publish.yml")
    for name in sorted(sv.LINEAGE_STATE_FILES):
        with pytest.raises(ValueError, match="lineage"):
            sv.resolve_state_path(None, dataclasses.replace(cfg, state_file=name))
        with pytest.raises(ValueError, match="lineage"):
            sv.resolve_state_path(Path(name), cfg)
        with pytest.raises(ValueError, match="lineage"):
            sv.resolve_state_path(tmp_path / "sub" / name, cfg)
    with pytest.raises(ValueError, match="lineage"):
        sv.resolve_state_path(None, dataclasses.replace(cfg, state_file=""))  # legacy default
    link = tmp_path / "innocent.json"
    link.symlink_to(ROOT / "publish.state.v060.json")
    with pytest.raises(ValueError, match="lineage"):
        sv.resolve_state_path(link, cfg)  # a link to a lineage record is one
    lineage = (ROOT / "publish.state.v060.json").read_bytes()
    yml = (ROOT / "publish.yml").read_text()
    for i, name in enumerate(sorted(sv.LINEAGE_STATE_FILES)):
        via_yml = yml.replace("state_file: publish.state.v063.json", f"state_file: {name}")
        assert via_yml != yml
        for k, (cli, text) in enumerate(((True, yml), (False, via_yml))):
            run_dir = tmp_path / f"run{i}{k}"
            run_dir.mkdir()
            argv = ["all", "--dry-run"] if cli else ["all"]
            if cli:
                argv += ["--state", str(run_dir / "proj" / name)]
            calls = []
            with pytest.raises(ValueError, match="lineage"):
                _run_main(monkeypatch, run_dir, argv, yml=text, calls=calls)
            assert calls == [], (name, cli, calls)
            assert (run_dir / "proj" / "publish.state.v060.json").read_bytes() == lineage
            assert not (run_dir / "proj" / "publish.state.v063.json").exists()


def test_a_lineage_state_file_is_refused_by_case_variant_or_hard_link(tmp_path):
    """On a case-insensitive disk a different-case name, and anywhere a hard link, is the same
    lineage record; both are refused, not only the exact file name."""
    import os

    import pytest

    sv = _load("scripts/publish/submit_to_venues.py", "sv_lineage_alias")
    real = tmp_path / "publish.state.v060.json"
    real.write_text("{}")
    with pytest.raises(ValueError, match="lineage"):
        sv._refuse_lineage_state(tmp_path / "PUBLISH.STATE.V060.JSON")
    link = tmp_path / "innocent.json"
    os.link(real, link)
    with pytest.raises(ValueError, match="lineage"):
        sv._refuse_lineage_state(link)
    fresh = tmp_path / "publish.state.v063.json"
    assert sv._refuse_lineage_state(fresh) == fresh
