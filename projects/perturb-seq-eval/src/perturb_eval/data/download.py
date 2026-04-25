"""Idempotent SHA-gated downloaders for scPerturb-packaged Perturb-seq data.

The scPerturb project (Peidli et al. 2024) re-packages every major
perturb-seq dataset as a single h5ad with harmonised ``obs.perturbation``
and ``var.gene_symbol`` columns. We pin to Zenodo record 13350497.
"""

from __future__ import annotations

import hashlib
import logging
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

ZENODO_RECORD = 13350497
_ZENODO_URL = "https://zenodo.org/api/records/{record}/files/{filename}/content"


@dataclass(frozen=True)
class DatasetSpec:
    """Declarative spec for one scPerturb dataset download."""

    name: str
    remote_filename: str
    local_filename: str
    url: str
    # SHA256 may be None when we haven't pinned it yet; the caller can
    # override via the ``sha256`` argument to :func:`fetch_adamson` /
    # :func:`fetch_norman`.
    sha256: Optional[str] = field(default=None)
    # Minimum expected file size (bytes). Truncation guard: anything
    # smaller is treated as a partial/corrupt download and re-fetched.
    # None disables the check (e.g. in unit tests).
    min_bytes: Optional[int] = field(default=None)


DATASETS: dict[str, DatasetSpec] = {
    "adamson_pilot": DatasetSpec(
        name="adamson_pilot",
        remote_filename="AdamsonWeissman2016_GSM2406675_10X001.h5ad",
        local_filename="Adamson2016_pilot.h5ad",
        url=_ZENODO_URL.format(
            record=ZENODO_RECORD,
            filename="AdamsonWeissman2016_GSM2406675_10X001.h5ad",
        ),
        min_bytes=10 * 1024 * 1024,  # actual ~34 MB; guard at 10 MB
    ),
    "adamson_10X005": DatasetSpec(
        name="adamson_10X005",
        remote_filename="AdamsonWeissman2016_GSM2406677_10X005.h5ad",
        local_filename="Adamson2016_10X005.h5ad",
        url=_ZENODO_URL.format(
            record=ZENODO_RECORD,
            filename="AdamsonWeissman2016_GSM2406677_10X005.h5ad",
        ),
        min_bytes=50 * 1024 * 1024,  # actual ~133 MB
    ),
    "adamson_10X010": DatasetSpec(
        name="adamson_10X010",
        remote_filename="AdamsonWeissman2016_GSM2406681_10X010.h5ad",
        local_filename="Adamson2016_10X010.h5ad",
        url=_ZENODO_URL.format(
            record=ZENODO_RECORD,
            filename="AdamsonWeissman2016_GSM2406681_10X010.h5ad",
        ),
        min_bytes=200 * 1024 * 1024,  # actual ~450 MB
    ),
    "norman": DatasetSpec(
        name="norman",
        remote_filename="NormanWeissman2019_filtered.h5ad",
        local_filename="NormanWeissman2019_filtered.h5ad",
        url=_ZENODO_URL.format(
            record=ZENODO_RECORD,
            filename="NormanWeissman2019_filtered.h5ad",
        ),
        min_bytes=500 * 1024 * 1024,  # actual ~699 MB
    ),
}

ADAMSON_SUBSETS: tuple[str, ...] = ("adamson_pilot", "adamson_10X005", "adamson_10X010")


def _download(url: str, dest: Path) -> None:
    """Fetch ``url`` into ``dest``. Split out so tests can patch it."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    logger.info("downloading %s -> %s", url, dest)
    urllib.request.urlretrieve(url, dest)  # noqa: S310 — pinned Zenodo URL


def _sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _verify_sha256(path: Path, expected: str) -> None:
    if not path.exists():
        raise FileNotFoundError(path)
    actual = _sha256_of(path)
    if actual != expected:
        raise ValueError(
            f"SHA256 mismatch for {path}: expected {expected}, got {actual}"
        )


def _looks_truncated(path: Path, min_bytes: Optional[int]) -> bool:
    """Detect obviously-partial downloads vs the spec's expected minimum."""
    if min_bytes is None:
        return False
    try:
        return path.stat().st_size < min_bytes
    except OSError:
        return True


def _fetch(
    spec: DatasetSpec,
    *,
    dest_dir: Path,
    sha256: Optional[str],
    min_bytes: Optional[int] = None,
) -> Path:
    """Download ``spec`` into ``dest_dir``.

    ``min_bytes`` overrides the spec's built-in truncation guard — pass
    ``0`` or ``None`` to disable (used by unit tests that mock
    ``_download`` with tiny payloads).
    """
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / spec.local_filename
    effective_sha = sha256 if sha256 is not None else spec.sha256
    effective_min = min_bytes if min_bytes is not None else spec.min_bytes

    if dest.exists() and _looks_truncated(dest, effective_min):
        logger.warning(
            "cached file %s looks truncated (%d bytes, expected >= %s) — re-downloading",
            dest, dest.stat().st_size, effective_min,
        )
        dest.unlink()

    if dest.exists() and effective_sha is not None:
        try:
            _verify_sha256(dest, effective_sha)
            logger.info("already present + SHA matches: %s", dest)
            return dest
        except ValueError:
            logger.warning("SHA mismatch on cached file — re-downloading %s", dest)
            dest.unlink()
    elif dest.exists():
        # File present but no SHA to verify — trust it.
        logger.info("already present (no SHA pin): %s", dest)
        return dest

    _download(spec.url, dest)
    if _looks_truncated(dest, effective_min):
        raise ValueError(
            f"download appears truncated: {dest} "
            f"({dest.stat().st_size} bytes, expected >= {effective_min})"
        )
    if effective_sha is not None:
        _verify_sha256(dest, effective_sha)
    return dest


def fetch_adamson(
    *,
    dest_dir: Path,
    sha256: Optional[str] = None,
    subset: str = "pilot",
    min_bytes: Optional[int] = None,
) -> Path:
    """Download an Adamson 2016 subset h5ad.

    Parameters
    ----------
    dest_dir
        Directory to place the file. Created if missing.
    sha256
        If provided, the file is verified against this hex digest after
        download (and a cached file is re-verified before the fetch is
        skipped).
    subset
        One of ``{"pilot", "10X005", "10X010"}`` — pilot is the smallest
        (~34 MB, 7 TFs); the other two add ~47 more perturbations each
        across the full Adamson Cell 2016 set.

    Returns
    -------
    Path
        Absolute path to the h5ad on disk.
    """
    key = f"adamson_{subset}" if subset != "pilot" else "adamson_pilot"
    if key not in DATASETS:
        raise ValueError(
            f"unknown Adamson subset {subset!r}; "
            f"try one of {['pilot', '10X005', '10X010']}"
        )
    return _fetch(DATASETS[key], dest_dir=dest_dir, sha256=sha256, min_bytes=min_bytes)


def fetch_adamson_all(*, dest_dir: Path) -> dict[str, Path]:
    """Fetch all three Adamson subsets (pilot + 10X005 + 10X010, ~200 MB total).

    Returns a dict mapping subset key to local path. Each call is idempotent.
    """
    return {
        key: _fetch(DATASETS[key], dest_dir=dest_dir, sha256=None)
        for key in ADAMSON_SUBSETS
    }


def fetch_norman(
    *,
    dest_dir: Path,
    sha256: Optional[str] = None,
    min_bytes: Optional[int] = None,
) -> Path:
    """Download the Norman 2019 h5ad (~120 MB).

    Norman encodes double knockdowns as ``GENE_A+GENE_B`` in
    ``obs.perturbation``. The loader in
    :mod:`perturb_eval.experiments.norman` handles both singletons and
    doublets via the same canonical dict shape as Adamson.
    """
    return _fetch(DATASETS["norman"], dest_dir=dest_dir, sha256=sha256, min_bytes=min_bytes)
