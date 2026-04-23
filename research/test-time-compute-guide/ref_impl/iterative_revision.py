"""Iterative revision — Snell mechanism #2 (Sequential, Inference-STI).

Algorithm:
    1. Generate an initial draft.
    2. Feed (prompt, draft) through a *reviser* to produce a revised draft.
    3. Optionally score each draft with a verifier and keep the best-so-far.
    4. Stop when the verifier score plateaus, or when ``max_rounds`` is reached.

The reviser is typically the same model prompted with a critique template, or
a separately trained "revision" model. Canonical: Snell et al. 2024
(Section 4, "Refining the Proposal Distribution").
"""

from __future__ import annotations

from dataclasses import dataclass

from ref_impl.types import Candidate, Generator, Reviser, Verifier


@dataclass(frozen=True)
class RevisionResult:
    winner: Candidate
    trajectory: tuple[Candidate, ...]  # draft[0], draft[1], ...
    scores: tuple[float, ...]
    total_tokens: int
    converged: bool


def iterative_revision(
    prompt: str,
    generate: Generator,
    revise: Reviser,
    verify: Verifier,
    *,
    max_rounds: int = 4,
    improvement_threshold: float = 1e-4,
) -> RevisionResult:
    if max_rounds < 1:
        raise ValueError("max_rounds must be >= 1")

    drafts: list[Candidate] = generate(prompt, n=1)
    if not drafts:
        raise RuntimeError("generator returned no candidates")
    scores: list[float] = [verify(drafts[0], prompt=prompt)]
    converged = False

    for _ in range(max_rounds - 1):
        next_draft = revise(prompt, drafts[-1])
        next_score = verify(next_draft, prompt=prompt)
        drafts.append(next_draft)
        scores.append(next_score)
        if next_score - scores[-2] < improvement_threshold:
            converged = True
            break

    best_idx = max(range(len(scores)), key=scores.__getitem__)
    return RevisionResult(
        winner=drafts[best_idx],
        trajectory=tuple(drafts),
        scores=tuple(scores),
        total_tokens=sum(d.tokens for d in drafts),
        converged=converged,
    )
