"""Unit tests for the auto-download data loaders.

The loaders must be idempotent (skip if file exists and SHA matches),
verify integrity (SHA256 gate), and raise a clear error on network failure.
Network access is mocked — no real HTTP in unit tests.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from unittest.mock import patch

import pytest

from perturb_eval.data.download import (
    DatasetSpec,
    fetch_adamson,
    fetch_norman,
    _verify_sha256,
)


def _write_bytes(path: Path, data: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


class TestVerifySha256:
    def test_match_passes(self, tmp_path: Path) -> None:
        target = tmp_path / "file.bin"
        sha = _write_bytes(target, b"hello world")
        _verify_sha256(target, sha)  # no raise

    def test_mismatch_raises(self, tmp_path: Path) -> None:
        target = tmp_path / "file.bin"
        _write_bytes(target, b"hello world")
        with pytest.raises(ValueError, match="SHA256 mismatch"):
            _verify_sha256(target, "0" * 64)

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            _verify_sha256(tmp_path / "nope.bin", "0" * 64)


class TestFetchAdamson:
    def test_skips_when_present_and_sha_matches(self, tmp_path: Path) -> None:
        sha = _write_bytes(tmp_path / "Adamson2016_pilot.h5ad", b"fake-pilot-data")
        with patch("perturb_eval.data.download._download") as mock_dl:
            out = fetch_adamson(dest_dir=tmp_path, sha256=sha, min_bytes=0)
            mock_dl.assert_not_called()
        assert out == tmp_path / "Adamson2016_pilot.h5ad"

    def test_downloads_when_missing(self, tmp_path: Path) -> None:
        payload = b"downloaded-pilot-data"
        sha = hashlib.sha256(payload).hexdigest()

        def fake_download(url: str, dest: Path) -> None:
            dest.write_bytes(payload)

        with patch("perturb_eval.data.download._download", side_effect=fake_download):
            out = fetch_adamson(dest_dir=tmp_path, sha256=sha, min_bytes=0)
        assert out.read_bytes() == payload

    def test_raises_on_sha_mismatch_after_download(self, tmp_path: Path) -> None:
        def fake_download(url: str, dest: Path) -> None:
            dest.write_bytes(b"corrupted")

        with patch("perturb_eval.data.download._download", side_effect=fake_download):
            with pytest.raises(ValueError, match="SHA256 mismatch"):
                fetch_adamson(dest_dir=tmp_path, sha256="0" * 64, min_bytes=0)

    def test_default_path_is_under_project_data(self, tmp_path: Path) -> None:
        payload = b"pilot"
        sha = hashlib.sha256(payload).hexdigest()
        with patch("perturb_eval.data.download._download") as mock_dl:
            mock_dl.side_effect = lambda url, dest: dest.write_bytes(payload)
            out = fetch_adamson(dest_dir=tmp_path, sha256=sha, min_bytes=0)
        assert out.name == "Adamson2016_pilot.h5ad"
        assert out.parent == tmp_path


class TestFetchNorman:
    def test_default_filename(self, tmp_path: Path) -> None:
        payload = b"norman-data"
        sha = hashlib.sha256(payload).hexdigest()
        with patch("perturb_eval.data.download._download") as mock_dl:
            mock_dl.side_effect = lambda url, dest: dest.write_bytes(payload)
            out = fetch_norman(dest_dir=tmp_path, sha256=sha, min_bytes=0)
        assert out.name == "NormanWeissman2019_filtered.h5ad"
        assert out.parent == tmp_path

    def test_idempotent(self, tmp_path: Path) -> None:
        sha = _write_bytes(tmp_path / "NormanWeissman2019_filtered.h5ad", b"cached")
        with patch("perturb_eval.data.download._download") as mock_dl:
            fetch_norman(dest_dir=tmp_path, sha256=sha, min_bytes=0)
            mock_dl.assert_not_called()

    def test_zenodo_url_uses_correct_record(self, tmp_path: Path) -> None:
        captured: list[str] = []

        def capture(url: str, dest: Path) -> None:
            captured.append(url)
            dest.write_bytes(b"x")

        with patch("perturb_eval.data.download._download", side_effect=capture):
            try:
                fetch_norman(dest_dir=tmp_path, sha256="0" * 64, min_bytes=0)
            except ValueError:
                pass  # SHA mismatch expected
        assert len(captured) == 1
        assert "zenodo.org" in captured[0]
        assert "13350497" in captured[0]
        assert "NormanWeissman2019" in captured[0]


class TestDatasetSpec:
    def test_has_adamson_and_norman(self) -> None:
        from perturb_eval.data.download import DATASETS
        assert "adamson_pilot" in DATASETS
        assert "norman" in DATASETS
        assert isinstance(DATASETS["adamson_pilot"], DatasetSpec)

    def test_urls_point_to_zenodo(self) -> None:
        from perturb_eval.data.download import DATASETS
        for name, spec in DATASETS.items():
            assert "zenodo.org" in spec.url, f"{name} URL not from Zenodo"


# ---------------------------------------------------------------------------
# T19 / A7 — fail closed on unpinned data (A&D §5 W6)
# ---------------------------------------------------------------------------

import logging
import re

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_LOCAL_PILOT = _PROJECT_ROOT / "data" / "Adamson2016_pilot.h5ad"
_PILOT_SHA = "119e3c1cf7dede4e13f887b86f9bcd797a9dc29213ee57d36aa80012d93f1c1c"
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


class TestFailClosedUnpinned:
    def test_raises_when_cached_file_has_no_sha_pin(self, tmp_path: Path) -> None:
        # norman has no pin (until T21): a cached file must NOT be trusted.
        cached = tmp_path / "NormanWeissman2019_filtered.h5ad"
        _write_bytes(cached, b"unverified-bytes")
        with patch("perturb_eval.data.download._download") as mock_dl:
            with pytest.raises(ValueError, match=r"norman.*NormanWeissman2019_filtered\.h5ad"):
                fetch_norman(dest_dir=tmp_path, min_bytes=0)
            mock_dl.assert_not_called()

    def test_trust_unpinned_returns_cached_path_with_warning(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        cached = tmp_path / "NormanWeissman2019_filtered.h5ad"
        _write_bytes(cached, b"unverified-bytes")
        with caplog.at_level(logging.WARNING, logger="perturb_eval.data.download"):
            with patch("perturb_eval.data.download._download") as mock_dl:
                out = fetch_norman(dest_dir=tmp_path, min_bytes=0, trust_unpinned=True)
                mock_dl.assert_not_called()
        assert out == cached
        warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert any("norman" in r.getMessage() and "unpinned" in r.getMessage().lower()
                   for r in warnings), [r.getMessage() for r in warnings]

    def test_raises_on_fresh_download_with_no_pin(self, tmp_path: Path) -> None:
        with patch("perturb_eval.data.download._download") as mock_dl:
            mock_dl.side_effect = lambda url, dest: dest.write_bytes(b"x")
            with pytest.raises(ValueError, match="norman"):
                fetch_norman(dest_dir=tmp_path, min_bytes=0)
            mock_dl.assert_not_called()
        assert not (tmp_path / "NormanWeissman2019_filtered.h5ad").exists()

    def test_fetch_adamson_all_raises_when_unpinned(self, tmp_path: Path) -> None:
        for key in ("adamson_pilot", "adamson_10X005", "adamson_10X010"):
            from perturb_eval.data.download import DATASETS
            _write_bytes(tmp_path / DATASETS[key].local_filename, b"cached")
        from perturb_eval.data.download import fetch_adamson_all
        with patch("perturb_eval.data.download._download") as mock_dl:
            mock_dl.side_effect = lambda url, dest: dest.write_bytes(b"refetched")
            with pytest.raises(ValueError):
                fetch_adamson_all(dest_dir=tmp_path, min_bytes=0)

    def test_mismatch_raises_and_does_not_leave_bad_file(self, tmp_path: Path) -> None:
        # Cached file with the wrong digest: re-download, verify, still wrong -> raise,
        # and the mismatched bytes must not stay in the cache.
        cached = tmp_path / "Adamson2016_pilot.h5ad"
        _write_bytes(cached, b"stale")
        with patch("perturb_eval.data.download._download") as mock_dl:
            mock_dl.side_effect = lambda url, dest: dest.write_bytes(b"still-wrong")
            with pytest.raises(ValueError, match="SHA256 mismatch"):
                fetch_adamson(dest_dir=tmp_path, sha256="0" * 64, min_bytes=0)
            assert mock_dl.call_count == 1
        assert not cached.exists()

    def test_mismatch_even_with_trust_unpinned_raises(self, tmp_path: Path) -> None:
        with patch("perturb_eval.data.download._download") as mock_dl:
            mock_dl.side_effect = lambda url, dest: dest.write_bytes(b"wrong")
            with pytest.raises(ValueError, match="SHA256 mismatch"):
                fetch_adamson(dest_dir=tmp_path, sha256="0" * 64, min_bytes=0,
                              trust_unpinned=True)

    def test_is_pinned(self) -> None:
        pinned = DatasetSpec(name="a", remote_filename="r", local_filename="l",
                             url="u", sha256="a" * 64)
        unpinned = DatasetSpec(name="a", remote_filename="r", local_filename="l", url="u")
        malformed = DatasetSpec(name="a", remote_filename="r", local_filename="l",
                                url="u", sha256="not-hex")
        assert pinned.is_pinned() is True
        assert unpinned.is_pinned() is False
        assert malformed.is_pinned() is False

    def test_pilot_pin_is_recorded(self) -> None:
        from perturb_eval.data.download import DATASETS
        assert DATASETS["adamson_pilot"].sha256 == _PILOT_SHA

    @pytest.mark.skipif(not _LOCAL_PILOT.exists(),
                        reason="local-pilot-absent: data/Adamson2016_pilot.h5ad not present")
    def test_pilot_pin_equals_local_file_digest(self) -> None:
        from perturb_eval.data.download import DATASETS, _sha256_of
        assert _sha256_of(_LOCAL_PILOT) == DATASETS["adamson_pilot"].sha256

    @pytest.mark.xfail(
        strict=True,
        reason="T21: digests pinned after T20 prints them from the Modal volume",
    )
    def test_all_specs_pinned(self) -> None:
        from perturb_eval.data.download import DATASETS
        for name, spec in DATASETS.items():
            assert spec.sha256 is not None and _HEX64.match(spec.sha256), name
            assert spec.is_pinned(), name
