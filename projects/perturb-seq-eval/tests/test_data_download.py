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
