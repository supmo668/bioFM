"""T3 — snapshot fetch tests.

The live fetch is blocked on T2 (H pins the commit), so the unit conditions here
run against a stubbed downloader and the network leg is marked integration.
That split is the plan's own rule: a task whose real input is human-gated gets a
fixture-backed unit condition plus an explicitly deferred integration condition
(Global Constraints / defect 33).
"""

import json
from pathlib import Path

import pytest

from chipsim.ingest import drugbank_snapshot as ds

PROJECT_ROOT = Path(__file__).resolve().parent.parent

VALID = "a" * 40
CONTENT = {
    "drugbank.tsv": b"drugbank_id\tname\n DB00001\tlepirudin\n",
    "drugbank-slim.tsv": b"drugbank_id\tname\nDB00002\tcetuximab\n",
    "proteins.tsv": b"drugbank_id\tuniprot_id\nDB00001\tP08183\n",
}


@pytest.fixture
def stub_download(monkeypatch):
    """Replace the network call with deterministic bytes."""
    calls = []

    def _fake(url, target):
        calls.append(url)
        target.write_bytes(CONTENT[target.name])

    monkeypatch.setattr(ds, "_download", _fake)
    return calls


# --------------------------------------------------------------------------- #
# commit validation — both halves of the contract (defect 32)
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "bad,why",
    [
        ("a" * 39, "39 chars — too short"),
        ("a" * 41, "41 chars — too long"),
        ("g" * 40, "40 chars but not hex"),
        ("A" * 40, "40 hex chars but uppercase"),
        ("main", "a branch name"),
        ("", "empty"),
        (None, "not a string"),
    ],
)
def test_fetch_rejects_a_non_commit(tmp_path, bad, why):
    dest = tmp_path / "drugbank"
    with pytest.raises(ValueError):
        ds.fetch_snapshot(dest, bad)
    assert not dest.exists() or not list(dest.iterdir()), f"dest was touched for {why}"


def test_rejection_leaves_an_existing_dest_untouched(tmp_path):
    """A pre-existing snapshot must survive a bad call unchanged."""
    dest = tmp_path / "drugbank"
    dest.mkdir()
    (dest / "keepme.txt").write_text("prior state")
    with pytest.raises(ValueError):
        ds.fetch_snapshot(dest, "z" * 40)
    assert (dest / "keepme.txt").read_text() == "prior state"
    assert [p.name for p in dest.iterdir()] == ["keepme.txt"]


# --------------------------------------------------------------------------- #
# the happy path, against a stubbed downloader
# --------------------------------------------------------------------------- #


def test_fetch_writes_three_files_flat(tmp_path, stub_download):
    dest = tmp_path / "drugbank"
    digests = ds.fetch_snapshot(dest, VALID)

    assert set(digests) == set(ds.SNAPSHOT_FILES)
    for name in ds.SNAPSHOT_FILES:
        assert (dest / name).is_file(), f"{name} not written flat into dest"
    # FLAT: no nested data/ level (defect 7)
    assert not (dest / "data").exists()


def test_fetch_urls_are_pinned_to_the_commit(tmp_path, stub_download):
    ds.fetch_snapshot(tmp_path / "drugbank", VALID)
    assert len(stub_download) == 3
    for url in stub_download:
        assert VALID in url, "fetch did not pin the URL to the commit"
        assert "/dhimmel/drugbank/" in url


def test_fetch_requests_one_url_per_file(tmp_path, stub_download):
    """Each URL must name its OWN file.

    The commit-and-repo check above passes for a `snapshot_url` hard-coded to
    always return `.../drugbank.tsv` — i.e. a fetch that downloads one file three
    times and stores it under three names. `stub_download` writes CONTENT keyed on
    the TARGET, so it can never observe the wrong URL; this asserts the URL set.
    """
    ds.fetch_snapshot(tmp_path / "drugbank", VALID)
    assert set(stub_download) == {ds.snapshot_url(VALID, n) for n in ds.SNAPSHOT_FILES}
    assert len(set(stub_download)) == 3, "the same URL was fetched more than once"


@pytest.mark.parametrize("name", ["drugbank.tsv", "drugbank-slim.tsv", "proteins.tsv"])
def test_snapshot_url_names_the_file_and_the_data_subdir(name):
    """Also pins `_REPO_SUBDIR`, which no test previously touched."""
    url = ds.snapshot_url(VALID, name)
    assert url.endswith(f"/data/{name}")
    assert VALID in url


def test_manifest_matches_the_files_on_disk(tmp_path, stub_download):
    dest = tmp_path / "drugbank"
    digests = ds.fetch_snapshot(dest, VALID)

    manifest = json.loads((dest / ds.MANIFEST_NAME).read_text())
    assert manifest["source_commit"] == VALID
    assert manifest["files"] == digests
    assert manifest["fetched_utc"]
    # digests are real, not placeholders
    import hashlib

    for name, digest in digests.items():
        assert digest == hashlib.sha256(CONTENT[name]).hexdigest()


def test_verify_snapshot_accepts_a_clean_fetch(tmp_path, stub_download):
    dest = tmp_path / "drugbank"
    ds.fetch_snapshot(dest, VALID)
    assert ds.verify_snapshot(dest) == json.loads((dest / ds.MANIFEST_NAME).read_text())["files"]


def test_verify_snapshot_detects_post_fetch_mutation(tmp_path, stub_download):
    """defect 2 — a file edited after fetch must not pass as the pinned snapshot."""
    dest = tmp_path / "drugbank"
    ds.fetch_snapshot(dest, VALID)
    (dest / "proteins.tsv").write_bytes(b"tampered\n")
    with pytest.raises(ds.SnapshotFetchError, match="sha256 mismatch"):
        ds.verify_snapshot(dest)


def test_verify_snapshot_detects_a_deleted_file(tmp_path, stub_download):
    dest = tmp_path / "drugbank"
    ds.fetch_snapshot(dest, VALID)
    (dest / "drugbank.tsv").unlink()
    with pytest.raises(ds.SnapshotFetchError, match="missing"):
        ds.verify_snapshot(dest)


def test_verify_snapshot_requires_a_manifest(tmp_path, stub_download):
    dest = tmp_path / "drugbank"
    ds.fetch_snapshot(dest, VALID)
    (dest / ds.MANIFEST_NAME).unlink()
    with pytest.raises(ds.SnapshotFetchError, match="unverifiable"):
        ds.verify_snapshot(dest)


# --------------------------------------------------------------------------- #
# atomicity — the property most likely to be wrong
# --------------------------------------------------------------------------- #


def test_a_failure_midway_leaves_dest_empty(tmp_path, monkeypatch):
    """The third download fails; nothing may be published.

    A partial snapshot carrying a manifest would be indistinguishable from a
    complete one, and every later integrity check would agree with it.
    """

    def _flaky(url, target):
        if target.name == "proteins.tsv":
            raise ds.SnapshotFetchError("simulated network failure")
        target.write_bytes(CONTENT[target.name])

    monkeypatch.setattr(ds, "_download", _flaky)
    dest = tmp_path / "drugbank"
    assert not dest.exists()
    with pytest.raises(ds.SnapshotFetchError):
        ds.fetch_snapshot(dest, VALID)

    # `dest` never existed, so `not dest.exists()` short-circuits the whole
    # assertion. Check the published-content condition explicitly instead.
    published = list(dest.iterdir()) if dest.exists() else []
    assert published == [], f"partial snapshot was published: {published}"


def test_a_failure_midway_leaves_an_EXISTING_snapshot_intact(tmp_path, monkeypatch):
    """The case that actually matters, and was untested.

    `fetch_snapshot` publishes with sequential `shutil.move` calls, which is not
    atomic. A failure part-way over an EXISTING good snapshot can leave a mixed
    old/new tree — and `verify_snapshot` would then bless it against whichever
    manifest won. This test records the ACTUAL behaviour so a future change to
    directory-swap publishing is a visible improvement rather than a silent one.
    """
    dest = tmp_path / "drugbank"

    def _ok(url, target):
        target.write_bytes(CONTENT[target.name])

    monkeypatch.setattr(ds, "_download", _ok)
    ds.fetch_snapshot(dest, VALID)
    before = {p.name: p.read_bytes() for p in dest.iterdir()}
    assert ds.verify_snapshot(dest)

    def _flaky(url, target):
        if target.name == "proteins.tsv":
            raise ds.SnapshotFetchError("simulated failure over an existing snapshot")
        target.write_bytes(CONTENT[target.name] + b"-NEW")

    monkeypatch.setattr(ds, "_download", _flaky)
    with pytest.raises(ds.SnapshotFetchError):
        ds.fetch_snapshot(dest, VALID)

    after = {p.name: p.read_bytes() for p in dest.iterdir()}
    assert after == before, (
        "a failed re-fetch modified the existing snapshot. The download stages in a "
        "tempdir, so nothing should reach `dest` unless every file downloaded."
    )
    assert ds.verify_snapshot(dest), "the prior snapshot no longer verifies"


def test_http_error_is_surfaced_not_swallowed(tmp_path, monkeypatch):
    class Resp:
        status_code = 404

        def iter_content(self, chunk_size=None):
            return iter(())

    monkeypatch.setattr(ds.requests, "get", lambda *a, **k: Resp())
    with pytest.raises(ds.SnapshotFetchError, match="404"):
        ds.fetch_snapshot(tmp_path / "drugbank", VALID)


# --------------------------------------------------------------------------- #
# the live leg — deferred on T2
# --------------------------------------------------------------------------- #


#: T1/T2's human artifact. No agent may write it — a fabricated source_commit
#: would make the whole provenance claim a confident lie.
LIVE_PROVENANCE = PROJECT_ROOT / "data" / "raw" / "drugbank" / "provenance.yaml"

#: Keyed on the ARTIFACT, not an unconditional skip. An unconditional skip stays
#: green and silent forever after T2 lands; this one lifts itself the moment the
#: human delivers, so the integration leg cannot be forgotten.
_blocked_on_t2 = pytest.mark.skipif(
    not LIVE_PROVENANCE.exists(),
    reason="T4a/T4 integration leg — blocked on T2 (H pins the snapshot commit); "
    "auto-lifts when data/raw/drugbank/provenance.yaml lands",
)


def _pinned_commit() -> str:
    import yaml

    return yaml.safe_load(LIVE_PROVENANCE.read_text())["source_commit"]


@pytest.mark.network
@pytest.mark.integration
@_blocked_on_t2
def test_live_fetch_against_the_pinned_commit(tmp_path):
    """T4a's done-condition: the three TSVs exist and their recomputed sha256s
    equal SHA256SUMS.json.

    Runs only once data/raw/drugbank/provenance.yaml carries a real source_commit
    — which no agent may write.
    """
    digests = ds.fetch_snapshot(tmp_path, _pinned_commit())
    assert set(digests) == set(ds.SNAPSHOT_FILES)
    for name in ds.SNAPSHOT_FILES:
        assert (tmp_path / name).is_file()
    assert ds.verify_snapshot(tmp_path) == digests


@pytest.mark.integration
@_blocked_on_t2
def test_t4_dvc_pointer_tracks_the_snapshot():
    """T4's four done-conditions (defects 5, 10):
    (a) git status lists no .tsv; (b) drugbank.dvc exists, is git-tracked, and
    parses as YAML with a non-empty outs[0].md5; (c) dvc status is up-to-date;
    (d) SHA256SUMS.json is git-tracked.
    """
    import subprocess

    import yaml

    # (a)
    porcelain = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert not [line for line in porcelain.splitlines() if line.endswith(".tsv")]

    # (b)
    pointer = PROJECT_ROOT / "data" / "raw" / "drugbank.dvc"
    assert pointer.is_file(), "T4 has not run: data/raw/drugbank.dvc is absent"
    doc = yaml.safe_load(pointer.read_text())
    assert doc["outs"][0]["md5"]
    assert (
        subprocess.run(
            ["git", "ls-files", "--error-unmatch", "data/raw/drugbank.dvc"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            check=False,
        ).returncode
        == 0
    )

    # (c)
    status = subprocess.run(
        ["dvc", "status", "data/raw/drugbank.dvc"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert status.returncode == 0, status.stderr

    # (d)
    assert (
        subprocess.run(
            ["git", "ls-files", "--error-unmatch", f"data/raw/drugbank/{ds.MANIFEST_NAME}"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            check=False,
        ).returncode
        == 0
    )
