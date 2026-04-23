"""Unit tests for metrics.py."""

from __future__ import annotations

import math

import pytest

from perturb_eval.metrics import (
    ace,
    ace_norm,
    critique_severity_dispersion,
    critique_severity_max,
    delta_ace,
    delta_mean_confidence,
    round_metrics,
    run_metrics,
    tdi,
    winner_flip_rate,
)
from perturb_eval.types import RoundMetrics


@pytest.mark.unit
class TestACE:
    def test_uniform_confidences_max_entropy(self) -> None:
        h = ace_norm((0.5, 0.5, 0.5, 0.5, 0.5))
        assert h == pytest.approx(1.0, abs=1e-9)

    def test_single_agent_zero_entropy(self) -> None:
        assert ace_norm((0.9,)) == 0.0

    def test_sharper_distribution_lower_entropy(self) -> None:
        # Low temperature sharpens softmax -> lower entropy.
        h_hot = ace((0.9, 0.1, 0.1, 0.1, 0.1), temperature=1.0)
        h_cold = ace((0.9, 0.1, 0.1, 0.1, 0.1), temperature=0.2)
        assert h_cold < h_hot

    def test_bounds(self) -> None:
        assert 0.0 <= ace_norm((0.1, 0.2, 0.3, 0.4, 0.5)) <= 1.0

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError):
            ace(())

    def test_negative_temperature_raises(self) -> None:
        with pytest.raises(ValueError):
            ace((0.5, 0.5), temperature=-1)


@pytest.mark.unit
class TestCSD:
    def test_flat_matrix_zero_variance(self) -> None:
        m = ((0.5, 0.5, 0.5, 0.5),) * 5
        assert critique_severity_dispersion(m) == 0.0

    def test_spread_matrix_nonzero_variance(self) -> None:
        m = ((0.1, 0.9, 0.5, 0.5), (0.5, 0.5, 0.9, 0.1)) + ((0.5, 0.5, 0.5, 0.5),) * 3
        assert critique_severity_dispersion(m) > 0.0

    def test_max_returns_largest_entry(self) -> None:
        m = ((0.1, 0.3, 0.2, 0.9),) * 5
        assert critique_severity_max(m) == pytest.approx(0.9)

    def test_square_matrix_drops_diagonal(self) -> None:
        """A 5x5 with huge diagonal should still show low variance
        if off-diagonal is uniform."""
        m = tuple(
            tuple(99.0 if i == j else 0.5 for j in range(5))
            for i in range(5)
        )
        assert critique_severity_dispersion(m) == 0.0


@pytest.mark.unit
class TestRoundMetrics:
    def test_builds_all_fields(self, easy_round) -> None:  # noqa: ANN001
        rm = round_metrics(easy_round)
        assert isinstance(rm, RoundMetrics)
        assert rm.max_confidence == 0.95
        assert rm.winner_index == 4
        assert rm.ace_norm >= 0
        assert rm.csd == pytest.approx(0.0, abs=1e-10)  # flat matrix


@pytest.mark.unit
class TestConvergenceSignals:
    def test_delta_ace_negative_on_converging(self, converging_run) -> None:  # noqa: ANN001
        per_round = tuple(round_metrics(r) for r in converging_run.rounds)
        assert delta_ace(per_round) < 0

    def test_delta_mean_confidence_positive_on_converging(self, converging_run) -> None:  # noqa: ANN001
        per_round = tuple(round_metrics(r) for r in converging_run.rounds)
        assert delta_mean_confidence(per_round) > 0

    def test_wfr_zero_on_stable_winner(self, converging_run) -> None:  # noqa: ANN001
        per_round = tuple(round_metrics(r) for r in converging_run.rounds)
        # rounds 0→1 flips (0→4); rounds 1→2 stable. So WFR = 1/2 = 0.5.
        assert winner_flip_rate(per_round) == pytest.approx(0.5)

    def test_wfr_one_on_thrashing(self, thrashing_run) -> None:  # noqa: ANN001
        per_round = tuple(round_metrics(r) for r in thrashing_run.rounds)
        assert winner_flip_rate(per_round) == pytest.approx(1.0)

    def test_single_round_returns_zero_deltas(self, easy_round) -> None:  # noqa: ANN001
        per_round = (round_metrics(easy_round),)
        assert delta_ace(per_round) == 0.0
        assert delta_mean_confidence(per_round) == 0.0
        assert winner_flip_rate(per_round) == 0.0


@pytest.mark.unit
class TestTDI:
    def test_converging_has_lower_tdi_than_thrashing(
        self, converging_run, thrashing_run,  # noqa: ANN001
    ) -> None:
        c_per = tuple(round_metrics(r) for r in converging_run.rounds)
        t_per = tuple(round_metrics(r) for r in thrashing_run.rounds)
        assert tdi(c_per) < tdi(t_per)

    def test_tdi_bounded(self, thrashing_run) -> None:  # noqa: ANN001
        per_round = tuple(round_metrics(r) for r in thrashing_run.rounds)
        t = tdi(per_round)
        assert 0.0 <= t <= 1.0

    def test_empty_returns_zero(self) -> None:
        assert tdi(()) == 0.0


@pytest.mark.unit
class TestRunMetrics:
    def test_end_to_end(self, converging_run) -> None:  # noqa: ANN001
        m = run_metrics(converging_run)
        assert m.task_id == "converging"
        assert len(m.per_round) == 3
        assert m.delta_ace < 0
        assert m.delta_mean_confidence > 0
        assert m.final_consensus_score == pytest.approx(0.8)
        assert 0.0 <= m.tdi <= 1.0
        assert not math.isnan(m.tdi)
