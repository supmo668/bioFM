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
    # Single Zenodo parent: the newest published v0.5.x version (v0.5.2), confirmed by the
    # read-only GETs; the concept DOI in the notes carries the rest of the chain (CTO #639).
    zen = [r for r in rel if r["relation"] == "isNewVersionOf" and "zenodo" in r["identifier"]]
    assert [r["identifier"] for r in zen] == ["10.5281/zenodo.20074427"]
    cit = (ROOT / "CITATION.cff").read_text()
    assert "10.5281/zenodo.20074427" in cit  # the version the new deposit supersedes is on record
    assert "v5 = v0.5.1" not in cit  # Figshare v5 matches Zenodo v0.5.2 by checksum, not v0.5.1
    changelog = (ROOT / "CHANGELOG.md").read_text()
    assert "Known gap: 0.5.1 and 0.5.2 are not documented here" in changelog
    assert (
        "10.5281/zenodo.20074427" in changelog and "No release note is reconstructed" in changelog
    )


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
NEW_ZEN = 23500555  # the new-version draft id Zenodo would return (newer than 20074427)
ZBUCKET = f"{ZEN_BASE}/files/new-draft-bucket"


def _world():
    return {
        "zen_inherited": {"f1": "paper.pdf", "f2": "supplement.zip"},
        "zen": {},
        "fig_inherited": {11: "paper.pdf", 12: "supplement.zip"},
        "fig": {},
        "fig_authors": [{"full_name": "Mang-yin Mo"}],
    }


def _revision_routes(public_versions=(5,), world=None, draft=None):
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
        held = [{"name": n, "supplied_md5": "old"} for n in w["fig_inherited"].values()]
        held += [{"name": n, "supplied_md5": m} for n, m in w["fig"].items()]
        return {"files": held, "authors": w["fig_authors"]}

    return {
        ("post", "/deposit/depositions/20074427/actions/newversion"): {
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
        "revision_of": 20074427,
        "inherited_files_removed": True,
        "prepared": True,
    }
}
FSTATE = {
    "figshare": {
        "article_id": 32086920,
        "revision_of": 32086920,
        "doi": "10.6084/m9.figshare.32086920",
        "public_baseline": [5, [["paper.pdf", "old"]]],
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
    assert sv.ALLOWED_REVISIONS == {"zenodo": 20074427, "figshare": 32086920}
    assert sv.ZENODO_CONCEPT == 19716140 and sv.FIGSHARE_BASE_VERSION == 5
    cfg = yaml.safe_load((ROOT / "publish.yml").read_text())["venues"]
    assert cfg["zenodo"]["revision_of"] == 20074427
    assert cfg["figshare"]["revision_of"] == 32086920
    assert "revision_of" not in cfg["osf"]
    rel = {r["identifier"] for r in cfg["zenodo"]["related_identifiers"]}
    assert f"10.6084/m9.figshare.32086920.v{sv.FIGSHARE_BASE_VERSION}" in rel


def test_published_or_superseded_records_are_refused_before_any_request(tmp_path, monkeypatch):
    import pytest

    cases = (
        ("zenodo", {"zenodo": {"deposit_id": 19748260, "published": True}}, None),
        ("zenodo", {"zenodo": {"deposit_id": 20074427}}, None),  # the target itself, as a draft
        ("zenodo", {"zenodo": {"deposit_id": "20074427", "revision_of": 20074427}}, None),  # str
        ("zenodo", {"zenodo": {"deposit_id": 20060974}}, PLAIN),
        ("zenodo", {"zenodo": {"deposit_id": 23411021, "bucket": "x"}}, None),  # mixing
        ("zenodo", {}, {"revision_of": 20060974}),  # any other revision target
        ("zenodo", {}, {"revision_of": 20074427.0}),  # not an int
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


def test_zenodo_revision_dry_run_touches_20074427_only_via_newversion(tmp_path, monkeypatch):
    routes = _revision_routes()
    sv, sub, calls, state_path, cfg = _submitter(monkeypatch, tmp_path, "zenodo", {}, routes=routes)
    f = tmp_path / "paper.pdf"
    f.write_bytes(b"v060")
    sub.submit([{"name": "paper.pdf", "path": f, "md5": "m"}])
    on_target = [(m, u) for m, u, _ in calls if "20074427" in u]
    assert on_target == [("post", f"{ZEN_BASE}/deposit/depositions/20074427/actions/newversion")]
    deletes = [u for m, u, _ in calls if m == "delete"]
    assert deletes == [
        f"{ZEN_BASE}/deposit/depositions/{NEW_ZEN}/files/f1",
        f"{ZEN_BASE}/deposit/depositions/{NEW_ZEN}/files/f2",
    ]
    assert ("put", f"{ZBUCKET}/paper.pdf") in [(m, u) for m, u, _ in calls]
    meta = next(kw for m, u, kw in calls if m == "put" and u.endswith(f"/{NEW_ZEN}"))["json"][
        "metadata"
    ]
    assert meta["version"] == "0.6.0" and "standalone" not in meta["notes"]
    assert "next version of this record" in meta["notes"]
    zen_parents = [
        r["identifier"]
        for r in meta["related_identifiers"]
        if r["relation"] == "isNewVersionOf" and "zenodo" in r["identifier"]
    ]
    assert zen_parents == ["10.5281/zenodo.20074427"]
    assert not any(m == "post" and u.endswith("/actions/publish") for m, u, _ in calls)  # dry run
    st = json.loads(state_path.read_text())["zenodo"]
    assert st == {
        "deposit_id": NEW_ZEN,
        "bucket": ZBUCKET,
        "revision_of": 20074427,
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
    routes = _revision_routes()
    routes[("post", "/deposit/depositions/20074427/actions/newversion")] = {
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
    assert not any("20074427" in u for _, u, _ in calls)
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
        "public_baseline": [5, [["paper.pdf", "old"]]],
        "inherited_files_removed": True,
        "prepared": True,
    }


def test_figshare_revision_refuses_a_base_other_than_v5_and_stops_on_public_change(
    tmp_path, monkeypatch
):
    import pytest

    sv, sub, calls, _, _ = _submitter(
        monkeypatch, tmp_path, "figshare", {}, routes=_revision_routes(public_versions=(6,))
    )
    with pytest.raises(sv.PublishedRecordError, match="starts only from v5"):
        sub.submit([])
    assert calls and all(m == "get" for m, _, _ in calls)
    # The public view changes after the metadata PUT: stop BEFORE deleting any file.
    sv, sub, calls, _, _ = _submitter(
        monkeypatch, tmp_path, "figshare", {}, routes=_revision_routes(public_versions=(5, 6))
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
        routes=_revision_routes(public_versions=(6,), world=_prepared_world()),
    )
    with pytest.raises(sv.PublishedRecordError, match="PUBLIC version changed"):
        sub.submit([])
    assert not any(m in ("put", "post", "delete") for m, _, _ in calls)


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


def _run_main(monkeypatch, tmp_path, argv, state=None, routes=None):
    """Run the real main() with the network stubbed: publish.yml copied to a config dir that is NOT
    the working directory, so the state file must be anchored to the config, not to cwd."""
    sv = _load("scripts/publish/submit_to_venues.py", "sv_main_run")
    cfgdir, cwd = tmp_path / "proj", tmp_path / "elsewhere"
    cfgdir.mkdir()
    cwd.mkdir()
    (cfgdir / "publish.yml").write_text((ROOT / "publish.yml").read_text())
    if state is not None:
        (cfgdir / "publish.state.v060.json").write_text(json.dumps(state))
    legacy = '{"zenodo": {"deposit_id": 19748260, "published": true}}'
    (cfgdir / "publish.state.json").write_text(legacy)
    env = tmp_path / ".env"
    env.write_text("")
    calls = []
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
    st = json.loads((cfgdir / "publish.state.v060.json").read_text())
    assert st["zenodo"]["deposit_id"] == NEW_ZEN and st["zenodo"]["revision_of"] == 20074427
    assert st["zenodo"]["prepared"] is True and st["figshare"]["prepared"] is True
    assert st["figshare"]["article_id"] == 32086920 and st["figshare"]["revision_of"] == 32086920
    assert "published" not in st["zenodo"] and "published" not in st["figshare"]
    assert not (cwd / "publish.state.v060.json").exists()
    assert (cfgdir / "publish.state.json").read_text() == legacy
    posts = [u for m, u, _ in calls if m == "post"]
    assert not any(u.endswith("/actions/publish") or u.endswith("/publish") for u in posts), posts
    assert not any(
        u.endswith("/deposit/depositions") or u.endswith("/account/articles") for u in posts
    )


def test_main_publish_without_a_recorded_draft_creates_nothing(tmp_path, monkeypatch):
    rc, calls, cfgdir, _, _ = _run_main(monkeypatch, tmp_path, ["all"])
    assert rc == 1
    assert not [c for c in calls if c[0] in ("post", "put", "delete")], calls
    assert not (cfgdir / "publish.state.v060.json").exists()


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
    st = json.loads((cfgdir / "publish.state.v060.json").read_text())
    assert st["zenodo"]["published"] is True and st["figshare"]["published"] is True


def test_main_reports_a_mismatched_state_and_continues(tmp_path, monkeypatch):
    seeded = {"figshare": {"article_id": 34562538}}  # the discarded standalone draft
    rc, calls, _, _, _ = _run_main(monkeypatch, tmp_path, ["all", "--dry-run"], state=seeded)
    assert rc == 1  # figshare refused ...
    assert not any("34562538" in c[1] or "32086920" in c[1] for c in calls), calls
    assert any(c[1].endswith("/20074427/actions/newversion") for c in calls)  # ... zenodo still ran


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


# ---- v0.6.0 is a NEW STANDALONE record on both venues (principal 2026-10-15, CTO #620) ----
SUPERSEDED = ("20074427", "20060974", "19748260", "19716140", "19716141", "19721470", "32086920")


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


def test_v060_release_has_its_own_state_and_never_reuses_the_v050_one(tmp_path):
    sv = _load("scripts/publish/submit_to_venues.py", "sv_state")
    cfg = sv.PublishConfig.load(ROOT / "publish.yml")
    assert cfg.state_file == "publish.state.v060.json"
    assert sv.resolve_state_path(None, cfg) == ROOT / "publish.state.v060.json"  # anchored to cfg
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
        .replace("state_file: publish.state.v060.json", "state_file:")
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
        sv._refuse_superseded("zenodo", 20074427, allow=None)
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
    assert not any("20074427" in u for _, u, _ in calls)
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
            "version": 5,
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
            "published" not in json.loads((cfgdir / "publish.state.v060.json").read_text())[venue]
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
    for venue, i in (("figshare", "32086920"), ("zenodo", "20074427"), ("zenodo", 19716140)):
        with pytest.raises(sv.PublishedRecordError):
            sv._refuse_superseded(venue, i)
    for bad in ("23500555", 23500555.0, True):
        with pytest.raises(sv.PublishedRecordError, match="not an integer"):
            sv._state_id("zenodo", "deposit_id", bad)
    assert sv._state_id("zenodo", "deposit_id", None) is None
