"""Unit tests for bayesian.py."""

from __future__ import annotations

import math

import pytest

from perturb_eval.bayesian import BayesianRecommender
from perturb_eval.probe import ProbeSignature
from perturb_eval.types import Config


@pytest.fixture
def easy_signature() -> ProbeSignature:
    return ProbeSignature(ace_norm=0.2, mean_conf=0.85, max_conf=0.95, csd=0.01)


@pytest.fixture
def hard_signature() -> ProbeSignature:
    return ProbeSignature(ace_norm=0.95, mean_conf=0.45, max_conf=0.6, csd=0.15)


@pytest.fixture
def labelled_fit_data(easy_signature, hard_signature) -> list[tuple[ProbeSignature, Config]]:  # noqa: ANN001
    """A small calibration set: easy signatures ↔ small configs, hard ↔ large."""
    small = Config(n_agents=3, n_rounds=1, backbone="scGPT")
    large = Config(n_agents=5, n_rounds=3, backbone="scGPT")
    return (
        [(easy_signature, small)] * 5
        + [(hard_signature, large)] * 5
    )


@pytest.mark.unit
class TestBayesianRecommender:
    def test_unfit_recommender_still_returns_config(self, easy_signature) -> None:  # noqa: ANN001
        rec = BayesianRecommender().recommend(easy_signature)
        assert isinstance(rec.config, Config)

    def test_prior_favours_small_under_no_data(self, easy_signature) -> None:  # noqa: ANN001
        """With no calibration data the Gaussian likelihood is flat, so prior wins
        and the smallest-FLOPs config should top the ranking."""
        rec = BayesianRecommender().recommend(easy_signature)
        top = rec.ranked[0]
        assert top.flops_proxy() == min(c.flops_proxy() for c in rec.ranked)

    def test_fit_changes_recommendation(self, labelled_fit_data, easy_signature, hard_signature) -> None:  # noqa: ANN001
        rec = BayesianRecommender().fit(labelled_fit_data)
        easy_rec = rec.recommend(easy_signature)
        hard_rec = rec.recommend(hard_signature)
        # Hard signature should recommend a larger config than easy signature.
        assert hard_rec.config.flops_proxy() >= easy_rec.config.flops_proxy()

    def test_budget_filters_configs(self, easy_signature) -> None:  # noqa: ANN001
        rec = BayesianRecommender().recommend(easy_signature, budget=3)
        assert rec.config.flops_proxy() <= 3

    def test_empty_budget_raises(self, easy_signature) -> None:  # noqa: ANN001
        with pytest.raises(ValueError):
            BayesianRecommender().recommend(easy_signature, budget=0)

    def test_log_likelihoods_finite(self, labelled_fit_data, easy_signature) -> None:  # noqa: ANN001
        rec = BayesianRecommender().fit(labelled_fit_data).recommend(easy_signature)
        assert all(math.isfinite(v) for v in rec.log_likelihoods.values())

    def test_fit_count_reported(self, labelled_fit_data, easy_signature) -> None:  # noqa: ANN001
        rec = BayesianRecommender().fit(labelled_fit_data).recommend(easy_signature)
        assert rec.fit_on_n_tasks == len(labelled_fit_data)
