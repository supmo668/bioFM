"""Tests for ``deterministic_stratum`` (T1, A6).

Python's built-in ``hash()`` on ``str`` is salted per process
(``PYTHONHASHSEED``), so any stratum assignment built on it differs between
interpreter runs. ``deterministic_stratum`` must be process-independent.
"""

from __future__ import annotations

import os
import subprocess
import sys
import zlib

import pytest

from perturb_eval.data.subsample import deterministic_stratum

LABELS = [
    "CBL_UBASH3A",
    "BAK1",
    "SAMD1_ZBTB1",
    "KLF1",
    "CEBPA_CEBPB",
    "FOXA1",
    "TP53",
    "MAP2K6_ELMSAN1",
    "ctrl",
    "ZBTB10_PTPN12",
]

_SNIPPET = (
    "from perturb_eval.data.subsample import deterministic_stratum;"
    f"print([deterministic_stratum(s, 3) for s in {LABELS!r}])"
)


def _run_with_hashseed(seed: str) -> str:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = seed
    proc = subprocess.run(
        [sys.executable, "-c", _SNIPPET],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout.strip()


def test_stratum_is_process_independent() -> None:
    out1 = _run_with_hashseed("1")
    out2 = _run_with_hashseed("2")
    assert out1, "subprocess printed nothing"
    assert out1 == out2


def test_stratum_regression_pin() -> None:
    # Pinned literal: zlib.crc32(b"CBL_UBASH3A") % 3 == 0 (computed once).
    assert deterministic_stratum("CBL_UBASH3A", 3) == 0
    # Pinned literals: BAK1 -> 0, SAMD1_ZBTB1 -> 1 (k=3).
    assert deterministic_stratum("BAK1", 3) == 0
    assert deterministic_stratum("SAMD1_ZBTB1", 3) == 1


def test_stratum_matches_crc32_and_is_in_range() -> None:
    for s in LABELS:
        v = deterministic_stratum(s, 5)
        assert v == zlib.crc32(s.encode("utf-8")) % 5
        assert 0 <= v < 5


@pytest.mark.parametrize("k", [0, -1])
def test_stratum_rejects_k_below_one(k: int) -> None:
    with pytest.raises(ValueError):
        deterministic_stratum("BAK1", k)
