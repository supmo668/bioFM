"""T2 — v0.5 task-list construction is a pure, deterministic function.

Fixtures are label/score-only: no expression matrices, no random generation.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from perturb_eval.experiments.v05_tasks import TaskPlan, build_task_lists

PROJECT_ROOT = Path(__file__).resolve().parent.parent

NORMAN_LABELS = [
    "CBL_UBASH3A",
    "KLF1_MAP2K6",
    "CEBPE_RUNX1T1",
    "ETS2_IKZF3",
    "CBL",
    "KLF1",
    "CEBPA",
    "SPI1",
    "UBASH3B",
    "MAP2K6",
    "ETS2",
    "IKZF3",
    "SET",
]

_SUBSET_A = [
    ("ATF4", 0.91), ("ATF6", 0.12), ("XBP1", 0.55), ("HSPA5", 1.40),
    ("DDIT3", 0.33), ("ERN1", 0.08), ("EIF2AK3", 0.71), ("SEC61A1", 0.26),
    ("SEL1L", 0.47), ("HYOU1", 0.64), ("DNAJB9", 0.19), ("SRPR", 0.83),
    ("TMED2", 0.05), ("OST4", 0.38), ("SPCS3", 0.97),
]
_SUBSET_B = [
    ("CREB3", 0.44), ("NFYA", 0.21), ("PDIA6", 1.10), ("CALR", 0.62),
    ("CANX", 0.15), ("P4HB", 0.89), ("SYVN1", 0.30), ("UFM1", 0.52),
    ("DERL2", 0.02), ("EDEM1", 0.77), ("MBTPS1", 0.36), ("MBTPS2", 0.68),
    ("SEC63", 0.11), ("SSR2", 0.49), ("TIMM23", 1.25),
]

ADAMSON_SUMMARY = {
    "adamson_10X005": dict(_SUBSET_A),
    "adamson_10X010": dict(_SUBSET_B),
}

KWARGS = dict(
    norman_n_singletons=6,
    norman_n_doublets=2,
    adamson_n_per_bin=3,
    adamson_n_bins=3,
    seed=2026,
)


def _plan(summary=ADAMSON_SUMMARY, labels=NORMAN_LABELS, **overrides) -> TaskPlan:
    kw = {**KWARGS, "doublet_delim": "_", **overrides}
    return build_task_lists(summary, labels, **kw)


_CHILD = """
import json, sys
sys.path.insert(0, {tests!r})
from test_v05_tasks import _plan
print(json.dumps(_plan().to_dict(), sort_keys=True))
"""


def _run_child(hashseed: str) -> str:
    env = {**os.environ, "PYTHONHASHSEED": hashseed}
    out = subprocess.run(
        [sys.executable, "-c", _CHILD.format(tests=str(PROJECT_ROOT / "tests"))],
        env=env,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout.strip()


def test_identical_across_pythonhashseed() -> None:
    a = _run_child("1")
    b = _run_child("2")
    assert a and a == b
    payload = json.loads(a)
    assert payload["adamson"] and payload["norman_singletons"]


def test_insertion_order_of_adamson_summary_is_irrelevant() -> None:
    reversed_summary = {
        k: dict(reversed(list(ADAMSON_SUMMARY[k].items())))
        for k in reversed(list(ADAMSON_SUMMARY))
    }
    assert list(reversed_summary) != list(ADAMSON_SUMMARY)
    assert _plan() == _plan(summary=reversed_summary)
    assert _plan(labels=list(reversed(NORMAN_LABELS))) == _plan()


def test_underscore_doublets_classified_and_counts_reported() -> None:
    plan = _plan()
    doublet_pool = {lbl for lbl in NORMAN_LABELS if "_" in lbl}
    assert set(plan.norman_doublets) <= doublet_pool
    assert len(plan.norman_doublets) == 2
    assert not set(plan.norman_singletons) & doublet_pool
    # Exact count (6) is pinned by T11's test_previous_underfill_case_now_filled_exactly.
    assert 1 <= len(plan.norman_singletons) <= 6
    assert plan.eligible_counts["norman_doublets"] == 4
    assert plan.eligible_counts["norman_singletons"] == 9
    assert plan.eligible_counts["adamson"] == 30
    assert len(plan.adamson) == 9
    assert plan.all_tasks == plan.adamson + plan.norman_singletons + plan.norman_doublets
    json.dumps(plan.to_dict())  # JSON-serialisable


# ---------------------------------------------------------------------------
# T11 — exact stratum fill + stratum-count assertion (C-RG-2, D1-confirm)
# ---------------------------------------------------------------------------


PLUS_POOL = [
    "CBL+UBASH3A", "KLF1+MAP2K6", "CEBPE+RUNX1T1", "ETS2+IKZF3",
    "FOXA1+HOXB9", "SET+KLF1",
    "CBL", "KLF1", "CEBPA", "SPI1", "UBASH3B", "MAP2K6", "ETS2", "IKZF3",
    "SET", "FOXA1",
]


def test_wrong_delim_raises_with_eligible_doublet_count() -> None:
    with pytest.raises(AssertionError) as exc:
        _plan(labels=PLUS_POOL, norman_n_singletons=3, norman_n_doublets=5)
    msg = str(exc.value)
    assert "eligible doublets: 0" in msg
    assert "requested 5" in msg and "got 0" in msg


def test_right_delim_returns_exactly_requested_doublets() -> None:
    plan = _plan(
        labels=PLUS_POOL, norman_n_singletons=3, norman_n_doublets=5, doublet_delim="+"
    )
    assert len(plan.norman_doublets) == 5
    assert all("+" in d for d in plan.norman_doublets)
    assert len(plan.norman_singletons) == 3


def test_previous_underfill_case_now_filled_exactly() -> None:
    # T2's fixture: 9 singletons, 3 CRC32 strata, 6 requested -> old sampler gave 5.
    plan = _plan()
    assert len(plan.norman_singletons) == 6
    assert len(set(plan.norman_singletons)) == 6
    assert not {s for s in plan.norman_singletons if "_" in s}
    assert len(plan.norman_doublets) == 2


def test_singleton_pool_smaller_than_request_raises() -> None:
    with pytest.raises(AssertionError) as exc:
        _plan(norman_n_singletons=10)
    msg = str(exc.value)
    assert "requested 10" in msg and "eligible singletons: 9" in msg


# Tied scores make quantile bins uneven (6 in one bin, 4 in another), so the
# per-bin draw alone yields 3 + 3 = 6 of the 9 requested.
_TIED_ADAMSON = {
    "adamson_full": {
        "ATF4": 0.0, "ATF6": 0.0, "XBP1": 0.0, "HSPA5": 0.0, "DDIT3": 0.0,
        "ERN1": 0.0, "EIF2AK3": 1.0, "SEC61A1": 2.0, "SEL1L": 3.0, "HYOU1": 4.0,
    }
}


def test_adamson_uneven_bins_filled_exactly() -> None:
    plan = _plan(summary=_TIED_ADAMSON)
    assert len(plan.adamson) == 9
    assert len(set(plan.adamson)) == 9
    assert plan == _plan(summary=_TIED_ADAMSON)


def test_adamson_pool_smaller_than_request_raises() -> None:
    small = {"adamson_full": {"ATF4": 0.1, "ATF6": 0.2, "XBP1": 0.3, "HSPA5": 0.4, "DDIT3": 0.5}}
    with pytest.raises(AssertionError) as exc:
        _plan(summary=small)
    msg = str(exc.value)
    assert "requested 9" in msg and "eligible adamson: 5" in msg


# D1-confirm: the sweep default is 15 singletons + 5 doublets.
D1_SINGLETONS = [f"GENE{i:03d}" for i in range(40)]
D1_DOUBLETS = [f"GENE{i:03d}_GENE{i + 1:03d}" for i in range(0, 24, 2)]
D1_LABELS = D1_SINGLETONS + D1_DOUBLETS


def _d1_plan() -> TaskPlan:
    return _plan(labels=D1_LABELS, norman_n_singletons=15, norman_n_doublets=5)


_D1_CHILD = """
import json, sys
sys.path.insert(0, {tests!r})
from test_v05_tasks import _d1_plan
print(json.dumps(_d1_plan().to_dict(), sort_keys=True))
"""


def test_d1_default_is_exactly_15_plus_5() -> None:
    assert len(D1_SINGLETONS) >= 30 and len(D1_DOUBLETS) >= 10
    plan = _d1_plan()
    assert len(plan.norman_singletons) == 15
    assert len(plan.norman_doublets) == 5
    assert set(plan.norman_singletons) <= set(D1_SINGLETONS)
    assert set(plan.norman_doublets) <= set(D1_DOUBLETS)


def test_d1_identical_across_pythonhashseed() -> None:
    outs = []
    for hs in ("1", "2"):
        env = {**os.environ, "PYTHONHASHSEED": hs}
        res = subprocess.run(
            [sys.executable, "-c", _D1_CHILD.format(tests=str(PROJECT_ROOT / "tests"))],
            env=env, cwd=str(PROJECT_ROOT), capture_output=True, text=True, check=True,
        )
        outs.append(res.stdout.strip())
    assert outs[0] and outs[0] == outs[1]
    payload = json.loads(outs[0])
    assert len(payload["norman_singletons"]) == 15
    assert len(payload["norman_doublets"]) == 5
