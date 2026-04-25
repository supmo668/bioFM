"""Tests for the v0.5.0 paper-number filler."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "paper" / "fill_v050_numbers.py"
spec = importlib.util.spec_from_file_location("fill_v050_numbers", SCRIPT)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
sys.modules["fill_v050_numbers"] = mod
spec.loader.exec_module(mod)


def test_fill_resolves_all_summary_tokens() -> None:
    summary = {
        "median_msd_adamson": 0.123,
        "median_msd_norman": 0.234,
        "architect_backbone_entropy_nats": 1.05,
        "architect_hvg_entropy_nats": 0.67,
        "n_lifecycle_runs": 120,
        "n_lifecycle_finite": 118,
        "best_config_per_task": {
            f"TF{i}": {"best_config": {"dataset": "adamson_full"}} for i in range(21)
        } | {
            f"N{i}": {"best_config": {"dataset": "norman"}} for i in range(15)
        },
        "gate_adamson_median_below_0_20": True,
        "gate_norman_median_below_0_30": True,
        "gate_architect_entropy_above_0_5_nats": True,
    }
    tokens = mod.fill(summary)
    assert tokens["ADAMSON_MEDIAN_MSD"] == "0.123"
    assert tokens["NORMAN_MEDIAN_MSD"] == "0.234"
    assert tokens["ADAMSON_N_TASKS"] == "21"
    assert tokens["NORMAN_N_TASKS"] == "15"
    assert tokens["ARCHITECT_BACKBONE_ENTROPY_NATS"] == "1.05"
    assert "PASS" in tokens["GATE_ADAMSON"]


def test_substitute_handles_escaped_latex_underscores() -> None:
    template = "median = {{ADAMSON_MEDIAN_MSD}}, entropy = $\\mathbf{{{ARCHITECT\\_BACKBONE\\_ENTROPY_NATS}}}$"
    tokens = {"ADAMSON_MEDIAN_MSD": "0.15", "ARCHITECT_BACKBONE_ENTROPY_NATS": "1.05"}
    out = mod.substitute(template, tokens)
    assert "0.15" in out
    assert "1.05" in out


def test_nan_becomes_na() -> None:
    summary = {"median_msd_adamson": float("nan")}
    tokens = mod.fill(summary)
    assert tokens["ADAMSON_MEDIAN_MSD"] == "n/a"


def test_gate_false_becomes_fail() -> None:
    summary = {"gate_adamson_median_below_0_20": False}
    tokens = mod.fill(summary)
    assert "FAIL" in tokens["GATE_ADAMSON"]
