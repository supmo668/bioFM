"""Unit tests for TTC strategies — all with a fake generator (no model I/O)."""

from __future__ import annotations

import pytest

from ttc.config import RunConfig, SamplingConfig, StrategyName
from ttc.scoring import GCContentVerifier
from ttc.strategies import dispatch


@pytest.mark.unit
def test_greedy_returns_single_candidate(fake_generator) -> None:  # noqa: ANN001
    cfg = RunConfig(
        strategy=StrategyName.GREEDY, prompt="AC", n_samples=1,
        sampling=SamplingConfig(max_new_tokens=8, do_sample=False),
    )
    result = dispatch(StrategyName.GREEDY, fake_generator, cfg, GCContentVerifier())
    assert result.strategy == StrategyName.GREEDY
    assert len(result.candidates) == 1
    assert result.compute_budget == 8


@pytest.mark.unit
def test_best_of_n_picks_highest_scored(fake_generator) -> None:  # noqa: ANN001
    cfg = RunConfig(
        strategy=StrategyName.BEST_OF_N, prompt="AC", n_samples=6,
        sampling=SamplingConfig(max_new_tokens=16),
    )
    result = dispatch(StrategyName.BEST_OF_N, fake_generator, cfg, GCContentVerifier())
    assert len(result.candidates) == 6
    # Winner must have the maximum score in the pool.
    assert result.winner == result.candidates[result.scores.index(max(result.scores))]
    # First pool item is ACGTACGTACGTACGT → 50% GC → best score (1.0).
    assert result.winner.text == "ACGTACGTACGTACGT"


@pytest.mark.unit
def test_best_of_n_budget_scales_linearly(fake_generator) -> None:  # noqa: ANN001
    cfg = RunConfig(
        strategy=StrategyName.BEST_OF_N, prompt="AC", n_samples=4,
        sampling=SamplingConfig(max_new_tokens=10),
    )
    result = dispatch(StrategyName.BEST_OF_N, fake_generator, cfg, GCContentVerifier())
    assert result.compute_budget == 40  # 4 candidates × 10 tokens


@pytest.mark.unit
def test_self_consistency_ignores_external_verifier(fake_generator) -> None:  # noqa: ANN001
    cfg = RunConfig(
        strategy=StrategyName.SELF_CONSISTENCY, prompt="AC", n_samples=6,
        sampling=SamplingConfig(max_new_tokens=16),
    )

    class _ShouldNotBeCalled:
        name = "should_not_be_called"
        def __call__(self, *a, **kw) -> float:
            raise AssertionError("self-consistency must not call external verifier")

    result = dispatch(StrategyName.SELF_CONSISTENCY, fake_generator, cfg, _ShouldNotBeCalled())
    assert result.verifier_name == "kmer_consensus"
    assert len(result.candidates) == 6


@pytest.mark.unit
def test_temperature_sweep_covers_grid(fake_generator) -> None:  # noqa: ANN001
    cfg = RunConfig(
        strategy=StrategyName.TEMPERATURE_SWEEP, prompt="AC", n_samples=8,
        sampling=SamplingConfig(max_new_tokens=10),
        temperature_grid=(0.5, 1.0, 1.5, 2.0),
    )
    result = dispatch(StrategyName.TEMPERATURE_SWEEP, fake_generator, cfg, GCContentVerifier())
    # 8 samples / 4 temps = 2 per temp → 8 total candidates
    assert len(result.candidates) == 8
    assert result.compute_budget == 80


@pytest.mark.unit
def test_unknown_strategy_raises(fake_generator) -> None:  # noqa: ANN001
    cfg = RunConfig(strategy=StrategyName.GREEDY, prompt="AC")
    with pytest.raises(KeyError):
        dispatch("does_not_exist", fake_generator, cfg, GCContentVerifier())  # type: ignore[arg-type]
