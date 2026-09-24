"""Idempotent SHA-gated downloaders for scPerturb-packaged Perturb-seq data.

The scPerturb project (Peidli et al. 2024) re-packages every major
perturb-seq dataset as a single h5ad with harmonised ``obs.perturbation``
and ``var.gene_symbol`` columns. We pin to Zenodo record 13350497.
"""

from __future__ import annotations

import hashlib
import logging
import re
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

ZENODO_RECORD = 13350497
_ZENODO_URL = "https://zenodo.org/api/records/{record}/files/{filename}/content"
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class DatasetSpec:
    """Declarative spec for one scPerturb dataset download."""

    name: str
    remote_filename: str
    local_filename: str
    url: str
    # SHA256 pin. None means "not pinned yet" (T21 pins the rest); an
    # unpinned spec fails closed in :func:`_fetch` unless the caller passes a
    # ``sha256`` override or explicitly opts in with ``trust_unpinned=True``.
    sha256: Optional[str] = field(default=None)
    # Minimum expected file size (bytes). Truncation guard: anything
    # smaller is treated as a partial/corrupt download and re-fetched.
    # None disables the check (e.g. in unit tests).
    min_bytes: Optional[int] = field(default=None)

    def is_pinned(self) -> bool:
        """True iff ``sha256`` is a well-formed 64-char lowercase hex digest."""
        return self.sha256 is not None and bool(_HEX64.match(self.sha256))


DATASETS: dict[str, DatasetSpec] = {
    "adamson_pilot": DatasetSpec(
        name="adamson_pilot",
        remote_filename="AdamsonWeissman2016_GSM2406675_10X001.h5ad",
        local_filename="Adamson2016_pilot.h5ad",
        url=_ZENODO_URL.format(
            record=ZENODO_RECORD,
            filename="AdamsonWeissman2016_GSM2406675_10X001.h5ad",
        ),
        # Digest of the local data/Adamson2016_pilot.h5ad (34,557,246 bytes).
        sha256="119e3c1cf7dede4e13f887b86f9bcd797a9dc29213ee57d36aa80012d93f1c1c",
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
        sha256="6c6eca0f53f8887b86597e2a4ff512ff2b2d3d9c78ee7deec9a6e7d6ae859d01",  # T20/T21: Zenodo md5 8657391920e7f8b3e6fd52745777002a verified
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
        sha256="e70fcd49808cab8d724de8d5a332940911206e1c8ef44cc7b568d048ed795c85",  # T20/T21: Zenodo md5 2fa44ea61a8dd35742af618638ec65fc verified
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
        sha256="efde6f5301fe256725dce1d980f37bd96a13481a9a16135515897368e631affc",  # T20/T21: Zenodo md5 c870e6967d91c017d9da827bab183cd6 verified
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
    trust_unpinned: bool = False,
) -> Path:
    """Download ``spec`` into ``dest_dir``, failing closed on unpinned data.

    ``min_bytes`` overrides the spec's built-in truncation guard — pass
    ``0`` or ``None`` to disable (used by unit tests that mock
    ``_download`` with tiny payloads).

    With no effective digest (neither ``sha256`` nor ``spec.sha256``) a cached
    file is NOT trusted and nothing is downloaded: :class:`ValueError` is
    raised, unless ``trust_unpinned=True`` — then a cached file is returned
    (or a fresh download kept) with a logged WARNING. A digest mismatch always
    raises and the mismatched file is removed from the cache.
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

    if effective_sha is None and not trust_unpinned:
        state = "cached file" if dest.exists() else "download target"
        raise ValueError(
            f"dataset {spec.name!r} has no SHA256 pin; refusing to use {state} "
            f"{dest} (pin DatasetSpec.sha256, pass sha256=, or trust_unpinned=True)"
        )

    if dest.exists() and effective_sha is not None:
        try:
            _verify_sha256(dest, effective_sha)
            logger.info("already present + SHA matches: %s", dest)
            return dest
        except ValueError:
            logger.warning("SHA mismatch on cached file — re-downloading %s", dest)
            dest.unlink()
    elif dest.exists():
        logger.warning(
            "trust_unpinned=True: using UNPINNED cached file for %r without "
            "digest verification: %s", spec.name, dest,
        )
        return dest

    _download(spec.url, dest)
    if _looks_truncated(dest, effective_min):
        raise ValueError(
            f"download appears truncated: {dest} "
            f"({dest.stat().st_size} bytes, expected >= {effective_min})"
        )
    if effective_sha is not None:
        try:
            _verify_sha256(dest, effective_sha)
        except ValueError:
            dest.unlink(missing_ok=True)  # never leave mismatched bytes cached
            raise
    else:
        logger.warning(
            "trust_unpinned=True: downloaded UNPINNED file for %r without "
            "digest verification: %s", spec.name, dest,
        )
    return dest


def fetch_adamson(
    *,
    dest_dir: Path,
    sha256: Optional[str] = None,
    subset: str = "pilot",
    min_bytes: Optional[int] = None,
    trust_unpinned: bool = False,
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
    trust_unpinned
        Opt-in escape hatch: use/keep a file with no SHA256 pin (logged
        WARNING). Default False — unpinned data raises ``ValueError``.

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
    return _fetch(
        DATASETS[key], dest_dir=dest_dir, sha256=sha256,
        min_bytes=min_bytes, trust_unpinned=trust_unpinned,
    )


def fetch_adamson_all(
    *,
    dest_dir: Path,
    min_bytes: Optional[int] = None,
    trust_unpinned: bool = False,
) -> dict[str, Path]:
    """Fetch all three Adamson subsets (pilot + 10X005 + 10X010, ~200 MB total).

    Returns a dict mapping subset key to local path. Each call is idempotent.
    Each subset is verified against its ``DATASETS`` pin; an unpinned subset
    raises ``ValueError`` unless ``trust_unpinned=True``.
    """
    return {
        key: _fetch(
            DATASETS[key], dest_dir=dest_dir, sha256=None,
            min_bytes=min_bytes, trust_unpinned=trust_unpinned,
        )
        for key in ADAMSON_SUBSETS
    }


def fetch_norman(
    *,
    dest_dir: Path,
    sha256: Optional[str] = None,
    min_bytes: Optional[int] = None,
    trust_unpinned: bool = False,
) -> Path:
    """Download the Norman 2019 h5ad (~699 MB).

    Norman (scPerturb bundle) encodes double knockdowns as ``_``-joined
    symbols (``GENE_A_GENE_B``, e.g. ``CBL_UBASH3A``) in ``obs.perturbation``;
    singletons are bare symbols. The loader in
    :mod:`perturb_eval.experiments.norman` (``doublet_delim="_"``) handles
    both via the same canonical dict shape as Adamson.
    """
    return _fetch(
        DATASETS["norman"], dest_dir=dest_dir, sha256=sha256,
        min_bytes=min_bytes, trust_unpinned=trust_unpinned,
    )
