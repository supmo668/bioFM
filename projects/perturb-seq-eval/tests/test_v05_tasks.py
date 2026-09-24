"""T2 — v0.5 task-list construction is a pure, deterministic function.

Fixtures are label/score-only: no expression matrices, no random generation.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

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
    # Exact-count enforcement is T11's assertion; the per-stratum draw can
    # under-fill when a CRC32 stratum is small, so only bound it here.
    assert 1 <= len(plan.norman_singletons) <= 6
    assert plan.eligible_counts["norman_doublets"] == 4
    assert plan.eligible_counts["norman_singletons"] == 9
    assert plan.eligible_counts["adamson"] == 30
    assert len(plan.adamson) == 9
    assert plan.all_tasks == plan.adamson + plan.norman_singletons + plan.norman_doublets
    json.dumps(plan.to_dict())  # JSON-serialisable
