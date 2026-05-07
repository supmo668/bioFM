"""Unit tests for the v0.5.0 real-trace analysis module.

The analyzer consumes two JSONL files (``trainer_runs.jsonl`` and
``lifecycle_runs.jsonl``) produced by ``scripts/modal/app_v05.py`` and
emits the headline summary tables/figures for the paper rewrite.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from perturb_eval.experiments.e_v05_real_traces import (
    BestConfigPerTask,
    analyse_v05_run,
    best_config_per_task,
    median_msd_per_config,
    tdi_vs_held_out_msd,
)


def _write_trainer_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")


def _write_lifecycle_jsonl(path: Path, rows: list[dict]) -> None:
    _write_trainer_jsonl(path, rows)  # same format


class TestBestConfigPerTask:
    def test_picks_minimum_msd_per_task(self, tmp_path: Path) -> None:
        trainer = tmp_path / "trainer.jsonl"
        _write_trainer_jsonl(
            trainer,
            [
                {"dataset": "adamson_full", "task": "TFA", "backbone": "linear",
                 "N": 3, "R": 1, "seed": 1, "msd_topk": 0.5},
                {"dataset": "adamson_full", "task": "TFA", "backbone": "mlp",
                 "N": 5, "R": 2, "seed": 1, "msd_topk": 0.2},
                {"dataset": "adamson_full", "task": "TFA", "backbone": "linear",
                 "N": 3, "R": 1, "seed": 2, "msd_topk": 0.4},
                {"dataset": "adamson_full", "task": "TFB", "backbone": "mlp",
                 "N": 3, "R": 1, "seed": 1, "msd_topk": 0.8},
            ],
        )
        best = best_config_per_task(trainer)
        assert best["TFA"].best_msd == pytest.approx(0.2)
        assert best["TFA"].best_config["backbone"] == "mlp"
        assert best["TFB"].best_msd == pytest.approx(0.8)

    def test_aggregates_median_across_seeds(self, tmp_path: Path) -> None:
        trainer = tmp_path / "trainer.jsonl"
        _write_trainer_jsonl(
            trainer,
            [
                {"dataset": "adamson_full", "task": "TFA", "backbone": "linear",
                 "N": 3, "R": 1, "seed": s, "msd_topk": m}
                for s, m in enumerate([0.1, 0.2, 0.3], start=1)
            ],
        )
        median = median_msd_per_config(trainer)
        # (linear, 3, 1) median = 0.2
        entry = next(r for r in median if r["backbone"] == "linear")
        assert entry["median_msd"] == pytest.approx(0.2)


class TestTDIVsHeldOutMSD:
    def test_returns_spearman_float_per_feature(self, tmp_path: Path) -> None:
        lifecycle = tmp_path / "lifecycle.jsonl"
        # Build traces where ACE correlates with MSD.
        rows = []
        rng = np.random.default_rng(0)
        for task_i in range(20):
            # fake ACE feature in steps; msd scales with it
            ace = 0.1 + task_i * 0.04
            msd = ace * 5 + rng.normal(0, 0.05)
            rows.append(
                {
                    "task_id": f"t{task_i}",
                    "seed": 1,
                    "final_msd_topk": float(msd),
                    "steps": [
                        {"agent_name": "Architect", "proposal_content": {"ace_proxy": float(ace)}},
                    ],
                }
            )
        _write_lifecycle_jsonl(lifecycle, rows)
        corr = tdi_vs_held_out_msd(lifecycle, feature_path=("Architect", "ace_proxy"))
        # Positive Spearman since ace_proxy grows with msd.
        assert corr["spearman"] > 0.8
        assert corr["n"] == 20


class TestAnalyseV05Run:
    def test_end_to_end_summary_dict(self, tmp_path: Path) -> None:
        trainer = tmp_path / "trainer.jsonl"
        lifecycle = tmp_path / "lifecycle.jsonl"
        _write_trainer_jsonl(
            trainer,
            [
                {"dataset": "adamson_full", "task": f"TF{i}",
                 "backbone": "linear", "N": 3, "R": 1, "seed": 1,
                 "msd_topk": 0.1 + 0.01 * i}
                for i in range(5)
            ]
            + [
                {"dataset": "norman", "task": f"N{i}",
                 "backbone": "mlp", "N": 3, "R": 1, "seed": 1,
                 "msd_topk": 0.2 + 0.01 * i}
                for i in range(5)
            ],
        )
        _write_lifecycle_jsonl(
            lifecycle,
            [
                {"task_id": f"TF{i}", "seed": 1,
                 "final_msd_topk": 0.15 + 0.01 * i,
                 "steps": [
                     {"agent_name": "Architect",
                      "proposal_content": {"backbone": ["linear", "mlp", "scgpt_small"][i % 3]}},
                 ]}
                for i in range(5)
            ],
        )
        summary = analyse_v05_run(trainer, lifecycle)
        assert "median_msd_adamson" in summary
        assert "median_msd_norman" in summary
        assert "architect_backbone_entropy_nats" in summary
        assert "n_trainer_runs" in summary
        assert "n_lifecycle_runs" in summary
        assert summary["n_trainer_runs"] == 10
        assert summary["n_lifecycle_runs"] == 5
        # Gate check fields present (even if gate isn't met on tiny synthetic fixture).
        assert "gate_adamson_median_below_0_20" in summary
        assert "gate_norman_median_below_0_30" in summary
        assert "gate_architect_entropy_above_0_5_nats" in summary


class TestRobustToMissingData:
    def test_empty_trainer_file(self, tmp_path: Path) -> None:
        trainer = tmp_path / "trainer.jsonl"
        lifecycle = tmp_path / "lifecycle.jsonl"
        trainer.write_text("")
        lifecycle.write_text("")
        summary = analyse_v05_run(trainer, lifecycle)
        assert summary["n_trainer_runs"] == 0
        assert summary["n_lifecycle_runs"] == 0

    def test_skips_malformed_lines(self, tmp_path: Path) -> None:
        trainer = tmp_path / "trainer.jsonl"
        trainer.write_text(
            '{"dataset": "adamson_full", "task": "TFA", "backbone": "linear", '
            '"N": 3, "R": 1, "seed": 1, "msd_topk": 0.1}\n'
            "{not valid json}\n"
            '{"dataset": "adamson_full", "task": "TFB", "backbone": "mlp", '
            '"N": 3, "R": 1, "seed": 1, "msd_topk": 0.2}\n'
        )
        best = best_config_per_task(trainer)
        assert set(best) == {"TFA", "TFB"}

    def test_skips_infinite_msd(self, tmp_path: Path) -> None:
        trainer = tmp_path / "trainer.jsonl"
        _write_trainer_jsonl(
            trainer,
            [
                {"dataset": "adamson_full", "task": "TFA", "backbone": "linear",
                 "N": 3, "R": 1, "seed": 1, "msd_topk": float("inf")},
                {"dataset": "adamson_full", "task": "TFA", "backbone": "mlp",
                 "N": 5, "R": 2, "seed": 1, "msd_topk": 0.2},
            ],
        )
        best = best_config_per_task(trainer)
        assert best["TFA"].best_msd == pytest.approx(0.2)


class TestBestConfigPerTaskDTO:
    def test_bestconfig_is_dataclass(self) -> None:
        bc = BestConfigPerTask(task="TFA", best_msd=0.1, best_config={"backbone": "mlp"}, n_configs_tried=42)
        assert bc.task == "TFA"
        assert bc.best_msd == 0.1
        assert bc.best_config["backbone"] == "mlp"
