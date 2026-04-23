"""Shared fixtures: deterministic fake generator, reviser, verifier."""

from __future__ import annotations

import pytest

from ref_impl.types import Candidate


def _pool():
    return [
        Candidate("answer_A", tokens=10),
        Candidate("answer_A", tokens=10),  # duplicate to create a majority
        Candidate("answer_B", tokens=10),
        Candidate("answer_C", tokens=10),
    ]


@pytest.fixture
def deterministic_generator():
    pool = _pool()

    def _gen(prompt: str, *, n: int = 1) -> list[Candidate]:  # noqa: ARG001
        return [pool[i % len(pool)] for i in range(n)]

    return _gen


@pytest.fixture
def length_verifier():
    """Rewards longer answers — standin for any domain verifier."""
    def _v(c: Candidate, *, prompt: str = "") -> float:  # noqa: ARG001
        return float(len(c.text))
    return _v


@pytest.fixture
def answer_preferring_verifier():
    """Gives answer_A the highest score so tests have a deterministic winner."""
    scores = {"answer_A": 0.9, "answer_B": 0.3, "answer_C": 0.1}

    def _v(c: Candidate, *, prompt: str = "") -> float:  # noqa: ARG001
        return scores.get(c.text, 0.0)

    return _v


@pytest.fixture
def improving_reviser():
    """Each revision *appends* a token, so length-verifier score rises."""
    def _r(prompt: str, draft: Candidate) -> Candidate:  # noqa: ARG001
        return Candidate(text=draft.text + "!", tokens=draft.tokens + 1)
    return _r


@pytest.fixture
def plateauing_reviser():
    """Returns the same draft — verifier score never improves."""
    def _r(prompt: str, draft: Candidate) -> Candidate:  # noqa: ARG001
        return Candidate(text=draft.text, tokens=draft.tokens)
    return _r
