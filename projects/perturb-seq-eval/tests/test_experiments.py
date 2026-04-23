"""Unit tests for the experiment runners E1, E2, E3.

See docs/SUPPLEMENT_DESIGN.md §4. Every runner is testable on tiny
synthetic inputs (≤ 200 ms) so CI stays fast and the Modal budget is
only spent on the headline run.
"""

from __future__ import annotations

import numpy as np
import pytest

from perturb_eval.experiments import (
    GridCellResult,
    OptimizerTrajectory,
    enumerate_grid,
    probe_signature_from_trace,
    run_e1_metric_overlap,
    run_e3_optimizer_comparison,
    train_grid_cell_synthetic,
)
from perturb_eval.types import Config, RoundTrace, RunTrace


@pytest.mark.unit
class TestE1MetricOverlap:
    def test_runs_and_returns_expected_schema(self) -> None:
        out = run_e1_metric_overlap(n_traces=100, seed=2026)
        assert "spearman_matrix" in out
        assert "feature_names" in out
        assert "drop_candidates" in out
        feats = out["feature_names"]
        assert {"ace_h", "ace_d", "csd", "csd_star", "tdi", "tdi2"}.issubset(set(feats))
        rho = out["spearman_matrix"]
        assert rho.shape == (len(feats), len(feats))
        # Diagonal is 1.0 by definition of Spearman.
        np.testing.assert_allclose(np.diag(rho), 1.0, atol=1e-9)
        # |rho| ≤ 1
        assert np.all(np.abs(rho) <= 1.0 + 1e-9)

    def test_drop_candidates_is_list_of_strings(self) -> None:
        out = run_e1_metric_overlap(n_traces=50, seed=0)
        assert isinstance(out["drop_candidates"], list)
        for s in out["drop_candidates"]:
            assert isinstance(s, str)


@pytest.mark.unit
class TestE2Grid:
    def test_enumerate_grid_cartesian_product(self) -> None:
        phis = (Config(n_agents=3, n_rounds=1, backbone="scGPT"),
                Config(n_agents=5, n_rounds=2, backbone="scPRINT-2"))
        tasks = ("A", "B")
        seeds = (7, 13)
        cells = list(enumerate_grid(phis, tasks, seeds))
        assert len(cells) == 2 * 2 * 2
        # Uniqueness
        assert len(set(cells)) == len(cells)

    def test_train_grid_cell_synthetic_returns_finite_msd(self) -> None:
        phi = Config(n_agents=5, n_rounds=2, backbone="scGPT")
        result = train_grid_cell_synthetic(phi=phi, task="A", seed=2026, n_cells=120)
        assert isinstance(result, GridCellResult)
        assert np.isfinite(result.msd_topk)
        assert result.msd_topk >= 0
        assert result.wall_time_sec >= 0


@pytest.mark.unit
class TestE3OptimizerComparison:
    def _toy_grid(self) -> dict[tuple[str, str], float]:
        """MSD grid: small configs are better at 'easy', large at 'hard'."""
        out: dict[tuple[str, str], float] = {}
        for a in (3, 5):
            for r in (1, 2):
                for b in ("scGPT", "scPRINT-2"):
                    phi_key = f"a={a}r={r}b={b}"
                    size = a * r
                    out[(phi_key, "easy")] = (size - 3) ** 2 / 10.0
                    out[(phi_key, "hard")] = (size - 8) ** 2 / 10.0
        return out

    def _tasks_and_contexts(self) -> dict[str, np.ndarray]:
        return {
            "easy": np.array([0.0, 0.0, 0.0, 0.0]),
            "hard": np.array([1.0, 0.0, 0.0, 0.0]),
        }

    def test_returns_one_trajectory_per_optimizer(self) -> None:
        grid = self._toy_grid()
        ctx = self._tasks_and_contexts()
        trajectories = run_e3_optimizer_comparison(
            grid=grid,
            contexts=ctx,
            optimizers=("random", "cma_es", "contextual_gp"),
            n_iterations=6,
            n_seeds=2,
        )
        names = {t.optimizer for t in trajectories}
        assert names == {"random", "cma_es", "contextual_gp"}
        for t in trajectories:
            assert isinstance(t, OptimizerTrajectory)
            assert len(t.best_msd_per_iter) == 6
            # Best-so-far is monotonically non-increasing within each task.
            per_task = t.best_msd_per_iter
            assert all(per_task[i + 1] <= per_task[i] + 1e-9 for i in range(len(per_task) - 1))


@pytest.mark.unit
class TestProbeSignature:
    def test_produces_4_dim_vector(self) -> None:
        rt = RoundTrace(
            round_index=0,
            agent_names=("A", "B", "C", "D", "E"),
            confidences=(0.8, 0.4, 0.3, 0.3, 0.7),
            critique_severities=((0.1, 0.2, 0.3, 0.4),) * 5,
            winner_index=0,
            consensus_score=0.55,
        )
        trace = RunTrace(task_id="t", rounds=(rt,), converged=False, backbone="scGPT")
        x = probe_signature_from_trace(trace)
        assert x.shape == (4,)
        assert np.all(np.isfinite(x))
