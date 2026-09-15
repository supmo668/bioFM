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
    "drugbank.tsv": b"drugbank_id\tname\n DB90001\tlepirudin\n",
    "drugbank-slim.tsv": b"drugbank_id\tname\nDB00002\tcetuximab\n",
    "proteins.tsv": b"drugbank_id\tuniprot_id\nDB90001\tP08183\n",
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


def _dvc_remote_url() -> str | None:
    """The configured default remote's url, as DVC itself resolves it across
    .dvc/config and .dvc/config.local. None when no url is configured on this
    machine. (DVC writes section headers as `['remote "local"']`, quotes included,
    which configparser reads as a differently-named section — so ask dvc.)"""
    import subprocess

    def _get(key: str) -> str | None:
        r = subprocess.run(
            ["dvc", "config", key], cwd=PROJECT_ROOT, capture_output=True, text=True, check=False
        )
        return r.stdout.strip() or None if r.returncode == 0 else None

    name = _get("core.remote")
    return _get(f"remote.{name}.url") if name else None


def _dvc_status(*args: str):
    import subprocess

    return subprocess.run(
        ["dvc", "status", *args], cwd=PROJECT_ROOT, capture_output=True, text=True, check=False
    )


@pytest.mark.integration
@_blocked_on_t2
def test_t4_dvc_pointers_track_the_snapshot():
    """T4's four done-conditions (defects 5, 10; (b)/(c) amended r2.11 — one
    pointer per TSV, because a directory pointer is unsatisfiable while
    provenance.yaml / PROVENANCE.md / SHA256SUMS.json are git-tracked inside
    data/raw/drugbank/, dvc/output.py:670).

    (a) no .tsv is git-tracked — asked of the INDEX, because `git status
        --porcelain` can see neither an ignored payload nor a committed one (QG-7);
    (b) each pointer describes ITS OWN TSV (path, size, md5) — here with the
        snapshot on disk, which is this test's precondition;
    (c) `dvc status -q` on all three exits 0 — the ONLY form with an exit-code
        contract; without `-q` dvc exits 0 on stale and deleted outs alike (QG-1);
    (d) SHA256SUMS.json is tracked.
    (b)/(d) are also asserted UNGATED in tests/test_provenance.py (QG-8), so that a
    missing provenance.yaml turns them into failures there rather than skips here.
    """
    import subprocess

    import yaml

    # (a)
    tracked_tsv = subprocess.run(
        ["git", "ls-files", "--", "data/raw/**/*.tsv"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    assert tracked_tsv == [], f"payload TSVs are git-tracked: {tracked_tsv}"

    # (b) — bound to the file each pointer names.
    for rel in ds.DVC_POINTERS:
        pointer = PROJECT_ROOT / rel
        assert pointer.is_file(), f"T4 has not run: {rel} is absent"
        tsv = pointer.with_suffix("")
        assert tsv.is_file(), f"{tsv.name} is not on disk — fetch the snapshot before this leg"
        defects = ds.pointer_defects(
            yaml.safe_load(pointer.read_text()), expected_path=tsv.name, file=tsv
        )
        assert defects == [], f"{rel}: " + "; ".join(defects)
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", rel],
            cwd=PROJECT_ROOT,
            capture_output=True,
            check=False,
        )
        assert tracked.returncode == 0, f"{rel} exists but is untracked"

    # (c) — quiet for the verdict, verbose for the diagnosis.
    quiet = _dvc_status("-q", *ds.DVC_POINTERS)
    if quiet.returncode != 0:
        verbose = _dvc_status(*ds.DVC_POINTERS)
        raise AssertionError(
            f"dvc status is not up to date:\n{verbose.stdout}{verbose.stderr}{quiet.stderr}"
        )

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


@pytest.mark.integration
@_blocked_on_t2
def test_t4_snapshot_is_pushed_to_the_remote():
    """A committed pointer whose blob exists only in this worktree's .dvc/cache is
    not recoverable — `git worktree remove` destroys the only copy, which is the
    data-loss incident .dvc/config warns about (QG-2). Skips when no remote url is
    configured on this machine (S9's own rule)."""
    if not _dvc_remote_url():
        pytest.skip("no DVC remote url configured on this machine (.dvc/config.local)")
    quiet = _dvc_status("--cloud", "-q", *ds.DVC_POINTERS)
    if quiet.returncode != 0:
        verbose = _dvc_status("--cloud", *ds.DVC_POINTERS)
        raise AssertionError(
            "snapshot is not pushed to the DVC remote:\n"
            f"{verbose.stdout}{verbose.stderr}{quiet.stderr}"
        )
