"""Best-of-N — Snell mechanism #1 (Parallel, Inference-SEA + VER).

Algorithm:
    1. Draw ``n`` independent candidates from the generator.
    2. Score each with a verifier.
    3. Return the argmax.

Canonical papers: Cobbe et al. 2021 (ORM); Lightman et al. 2023 (PRM);
Snell et al. 2024 (compute-optimal allocation).
"""

from __future__ import annotations

from dataclasses import dataclass

from ref_impl.types import Candidate, Generator, Verifier


@dataclass(frozen=True)
class BoNResult:
    winner: Candidate
    candidates: tuple[Candidate, ...]
    scores: tuple[float, ...]
    total_tokens: int


def best_of_n(
    prompt: str,
    generate: Generator,
    verify: Verifier,
    *,
    n: int,
) -> BoNResult:
    if n < 1:
        raise ValueError("n must be >= 1")
    candidates = generate(prompt, n=n)
    if not candidates:
        raise RuntimeError("generator returned no candidates")
    scores = tuple(verify(c, prompt=prompt) for c in candidates)
    winner_idx = max(range(len(candidates)), key=scores.__getitem__)
    return BoNResult(
        winner=candidates[winner_idx],
        candidates=tuple(candidates),
        scores=scores,
        total_tokens=sum(c.tokens for c in candidates),
    )
