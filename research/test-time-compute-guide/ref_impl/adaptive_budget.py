"""Adaptive budget allocation — Snell's compute-optimal strategy.

Idea: estimate the difficulty of the prompt, then route it to the TTC
strategy that wins at that difficulty level — and spend just enough budget.

- Easy prompts ─► sequential revision (few samples, quick improvements).
- Hard prompts ─► parallel best-of-N (sample a different mode).
- Medium       ─► weighted majority with a modest N.

We gauge difficulty by the spread / confidence of a small *probe* batch:
if the probe's verifier scores are tight and high → easy; wide and low → hard.

This is the algorithm behind the "smaller model beats 14x larger" headline:
uniform spending across all prompts is wasteful; adaptive spending is the win.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ref_impl.best_of_n import best_of_n
from ref_impl.iterative_revision import iterative_revision
from ref_impl.types import Candidate, Generator, Reviser, Verifier
from ref_impl.weighted_majority import weighted_majority


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass(frozen=True)
class AdaptiveResult:
    winner: Candidate
    difficulty: Difficulty
    probe_mean: float
    probe_spread: float
    budget_spent: int
    strategy_used: str


def _classify(mean: float, spread: float) -> Difficulty:
    """Very simple 2-D partition — real systems learn this."""
    if mean >= 0.8 and spread <= 0.1:
        return Difficulty.EASY
    if mean <= 0.3 or spread >= 0.4:
        return Difficulty.HARD
    return Difficulty.MEDIUM


def adaptive_route(
    prompt: str,
    generate: Generator,
    verify: Verifier,
    revise: Reviser,
    *,
    probe_n: int = 4,
    budget: int = 16,
) -> AdaptiveResult:
    if probe_n < 2:
        raise ValueError("probe_n must be >= 2 to compute a spread")
    probe = generate(prompt, n=probe_n)
    probe_scores = [verify(c, prompt=prompt) for c in probe]
    mean = sum(probe_scores) / len(probe_scores)
    spread = max(probe_scores) - min(probe_scores)
    difficulty = _classify(mean, spread)

    # Budget was partly spent on the probe.
    remaining = max(1, budget - probe_n)

    if difficulty is Difficulty.EASY:
        result = iterative_revision(
            prompt, generate, revise, verify,
            max_rounds=min(remaining, 4),
        )
        return AdaptiveResult(
            winner=result.winner, difficulty=difficulty,
            probe_mean=mean, probe_spread=spread,
            budget_spent=probe_n + len(result.trajectory),
            strategy_used="iterative_revision",
        )
    if difficulty is Difficulty.HARD:
        result = best_of_n(prompt, generate, verify, n=remaining)
        return AdaptiveResult(
            winner=result.winner, difficulty=difficulty,
            probe_mean=mean, probe_spread=spread,
            budget_spent=probe_n + len(result.candidates),
            strategy_used="best_of_n",
        )
    # MEDIUM
    result = weighted_majority(prompt, generate, verify, n=remaining)
    return AdaptiveResult(
        winner=result.winner, difficulty=difficulty,
        probe_mean=mean, probe_spread=spread,
        budget_spent=probe_n + remaining,
        strategy_used="weighted_majority",
    )
