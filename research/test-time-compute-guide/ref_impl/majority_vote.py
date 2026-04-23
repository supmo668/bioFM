"""Self-consistency / majority vote — (Parallel, Inference-AGG).

Algorithm:
    1. Draw ``n`` candidates (usually with temperature > 0).
    2. Group by final-answer equivalence class (exact match on a projection).
    3. Return the most populous class's exemplar.

Canonical paper: Wang et al. 2022, "Self-Consistency Improves Chain of Thought
Reasoning in Language Models" (arXiv:2203.11171).
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass

from ref_impl.types import Candidate, Generator


@dataclass(frozen=True)
class MajorityResult:
    winner: Candidate
    counts: dict[str, int]  # projected answer -> count
    total_tokens: int


def _default_project(c: Candidate) -> str:
    """Default equivalence projection: the full text, stripped."""
    return c.text.strip()


def majority_vote(
    prompt: str,
    generate: Generator,
    *,
    n: int,
    project: Callable[[Candidate], str] | None = None,
) -> MajorityResult:
    if n < 1:
        raise ValueError("n must be >= 1")
    project = project or _default_project
    candidates = generate(prompt, n=n)
    if not candidates:
        raise RuntimeError("generator returned no candidates")
    counts: Counter[str] = Counter(project(c) for c in candidates)
    winner_key, _ = counts.most_common(1)[0]
    # Pick the first candidate whose projection matches the winning key.
    winner = next(c for c in candidates if project(c) == winner_key)
    return MajorityResult(
        winner=winner,
        counts=dict(counts),
        total_tokens=sum(c.tokens for c in candidates),
    )
