"""Smoke tests exercising the high-level runner via injection."""

from __future__ import annotations

import pytest

from ttc.config import RunConfig, SamplingConfig, StrategyName
from ttc.runner import run_strategy
from ttc.scoring import GCContentVerifier


@pytest.mark.unit
def test_run_strategy_with_injected_deps(fake_generator) -> None:  # noqa: ANN001
    cfg = RunConfig(
        strategy=StrategyName.BEST_OF_N, prompt="AC", n_samples=3,
        sampling=SamplingConfig(max_new_tokens=8),
    )
    result = run_strategy(cfg, generate=fake_generator, verifier=GCContentVerifier())
    assert len(result.candidates) == 3
    assert result.winner.tokens_generated == 8
    assert result.verifier_name == "gc_content"


@pytest.mark.unit
def test_runner_records_strategy_name(fake_generator) -> None:  # noqa: ANN001
    cfg = RunConfig(
        strategy=StrategyName.SELF_CONSISTENCY, prompt="AC", n_samples=4,
        sampling=SamplingConfig(max_new_tokens=8),
    )
    result = run_strategy(cfg, generate=fake_generator, verifier=GCContentVerifier())
    assert result.strategy == StrategyName.SELF_CONSISTENCY
