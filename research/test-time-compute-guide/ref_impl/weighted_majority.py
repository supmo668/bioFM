"""Verifier-weighted majority — (Parallel, Inference-VER + AGG).

Combines Best-of-N's verifier signal with majority-vote's robustness:
each candidate contributes its verifier score to its equivalence class;
the class with the largest *total score* wins.

When all verifier scores are 1.0 this degenerates to vanilla majority vote.

Canonical formulation: Snell et al. 2024 "weighted Best-of-N"; also explored
in Can 1B LLM Surpass 405B LLM? (arXiv:2502.06703) as PRM-weighted voting.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass

from ref_impl.types import Candidate, Generator, Verifier


@dataclass(frozen=True)
class WeightedResult:
    winner: Candidate
    class_scores: dict[str, float]
    total_tokens: int


def _default_project(c: Candidate) -> str:
    return c.text.strip()


def weighted_majority(
    prompt: str,
    generate: Generator,
    verify: Verifier,
    *,
    n: int,
    project: Callable[[Candidate], str] | None = None,
) -> WeightedResult:
    if n < 1:
        raise ValueError("n must be >= 1")
    project = project or _default_project
    candidates = generate(prompt, n=n)
    if not candidates:
        raise RuntimeError("generator returned no candidates")

    class_scores: dict[str, float] = defaultdict(float)
    scores = [verify(c, prompt=prompt) for c in candidates]
    for c, s in zip(candidates, scores, strict=True):
        class_scores[project(c)] += s

    winner_key = max(class_scores, key=class_scores.__getitem__)
    # Among candidates in the winning class, pick the one with the highest
    # individual verifier score — a tiny but standard tiebreak.
    winner = max(
        (c for c in candidates if project(c) == winner_key),
        key=lambda c: scores[candidates.index(c)],
    )
    return WeightedResult(
        winner=winner,
        class_scores=dict(class_scores),
        total_tokens=sum(c.tokens for c in candidates),
    )
