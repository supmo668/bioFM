"""Unit tests for the extended metrics (ACE_D, CSD*, TDI2).

See docs/SUPPLEMENT_DESIGN.md §1 for design rationale. These metrics are
additive: all existing metric tests must continue to pass unchanged.
"""

from __future__ import annotations

import math

import pytest

from perturb_eval.metrics import (
    ace_d,
    ace_norm,
    critique_severity_star,
    critique_severity_dispersion,
    round_metrics,
    tdi,
    tdi2,
)


# ---------------------------------------------------------------------------
# ACE_D — simplex-projection entropy
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestACED:
    def test_uniform_confidences_max_entropy(self) -> None:
        """Uniform confidences saturate entropy just like ACE_H."""
        assert ace_d((0.5, 0.5, 0.5, 0.5, 0.5)) == pytest.approx(1.0, abs=1e-9)

    def test_concentrated_confidence_zero_entropy(self) -> None:
        """(1,0,0,0,0) simplex-normalises to a point mass → H=0.

        This is the signature difference vs ACE_H, which returns ~0.85 on
        the same input because softmax of bounded values stays near-uniform.
        """
        assert ace_d((1.0, 0.0, 0.0, 0.0, 0.0)) == pytest.approx(0.0, abs=1e-12)

    def test_disagrees_with_softmax_ace_on_concentrated(self) -> None:
        c = (1.0, 0.0, 0.0, 0.0, 0.0)
        h_softmax = ace_norm(c)
        h_simplex = ace_d(c)
        assert h_softmax - h_simplex > 0.5, (
            "ACE_H and ACE_D must disagree on concentrated inputs (the "
            "whole point of introducing ACE_D); got H_soft=%.3f, H_sim=%.3f"
            % (h_softmax, h_simplex)
        )

    def test_bounds(self) -> None:
        assert 0.0 <= ace_d((0.1, 0.2, 0.3, 0.4, 0.5)) <= 1.0

    def test_single_agent_zero_entropy(self) -> None:
        assert ace_d((0.9,)) == 0.0

    def test_all_zero_confidences_returns_zero(self) -> None:
        """No information → define entropy as 0 (avoid ZeroDivisionError)."""
        assert ace_d((0.0, 0.0, 0.0, 0.0, 0.0)) == 0.0

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError):
            ace_d(())

    def test_negative_confidence_raises(self) -> None:
        """Confidences are probabilities; negative values are ill-defined."""
        with pytest.raises(ValueError):
            ace_d((-0.1, 0.5, 0.5, 0.5, 0.5))


# ---------------------------------------------------------------------------
# CSD★ — excess severity over median
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCSDStar:
    def test_flat_matrix_zero(self) -> None:
        m = ((0.5, 0.5, 0.5, 0.5),) * 5
        assert critique_severity_star(m) == 0.0

    def test_lone_outlier_near_one(self) -> None:
        """Nineteen at 0.1, one at 1.0 — this is the 'one severe critic'
        archetype that variance-based CSD fails to flag."""
        rows = [[0.1] * 4 for _ in range(5)]
        rows[0][0] = 1.0  # single outlier
        m = tuple(tuple(r) for r in rows)
        assert critique_severity_star(m) > 0.9

    def test_outlier_pattern_star_beats_variance(self) -> None:
        """On a 'lone severe critic' matrix, CSD★ should detect what CSD
        (variance) misses."""
        rows = [[0.1] * 4 for _ in range(5)]
        rows[0][0] = 1.0
        m = tuple(tuple(r) for r in rows)
        assert critique_severity_star(m) > critique_severity_dispersion(m) * 2

    def test_bounded_zero_to_one(self) -> None:
        rows = [[0.1, 0.3, 0.7, 1.0] for _ in range(5)]
        m = tuple(tuple(r) for r in rows)
        v = critique_severity_star(m)
        assert 0.0 <= v <= 1.0

    def test_all_max_returns_zero(self) -> None:
        """If every entry is 1.0, there is no excess — CSD★ = 0."""
        m = ((1.0, 1.0, 1.0, 1.0),) * 5
        assert critique_severity_star(m) == 0.0

    def test_empty_returns_zero(self) -> None:
        assert critique_severity_star(()) == 0.0


# ---------------------------------------------------------------------------
# TDI2 — TDI with pairwise interaction terms
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestTDI2:
    def test_reduces_to_tdi_when_interactions_zero(self, converging_run) -> None:  # noqa: ANN001
        per_round = tuple(round_metrics(r) for r in converging_run.rounds)
        base = tdi(per_round)
        with_zero_interactions = tdi2(per_round, interaction_coeffs={})
        assert with_zero_interactions == pytest.approx(base, abs=1e-9)

    def test_interaction_term_affects_result(self, thrashing_run) -> None:  # noqa: ANN001
        per_round = tuple(round_metrics(r) for r in thrashing_run.rounds)
        base = tdi(per_round)
        with_interaction = tdi2(
            per_round,
            interaction_coeffs={"ace_norm_x_lack_conv": 0.2},
        )
        assert with_interaction != pytest.approx(base, abs=1e-9)

    def test_bounded_zero_to_one(self, thrashing_run) -> None:  # noqa: ANN001
        per_round = tuple(round_metrics(r) for r in thrashing_run.rounds)
        v = tdi2(
            per_round,
            interaction_coeffs={
                "ace_norm_x_lack_conv": 0.5,
                "csd_x_wfr": 0.5,
                "csd_x_ace_norm": 0.5,
            },
        )
        assert 0.0 <= v <= 1.0
        assert not math.isnan(v)

    def test_empty_returns_zero(self) -> None:
        assert tdi2(()) == 0.0

    def test_unknown_interaction_key_raises(self, converging_run) -> None:  # noqa: ANN001
        per_round = tuple(round_metrics(r) for r in converging_run.rounds)
        with pytest.raises(ValueError, match="unknown interaction term"):
            tdi2(per_round, interaction_coeffs={"nonexistent_term": 0.1})
