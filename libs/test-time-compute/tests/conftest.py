"""Shared test fixtures — all of them avoid downloading model weights."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from ttc.config import SamplingConfig
from ttc.strategies import Candidate


def _fake_generator(
    texts_by_sampling: list[str] | None = None,
) -> Callable[[str, SamplingConfig], list[Candidate]]:
    """Build a deterministic stand-in generator.

    Returns ``num_return_sequences`` candidates, cycling through a fixed pool.
    """

    pool = texts_by_sampling or [
        "ACGTACGTACGTACGT",  # balanced GC
        "AAAAAAAAAAAAAAAA",  # 0% GC
        "GCGCGCGCGCGCGCGC",  # 100% GC
        "ACGTACGTACGTACGA",  # near balanced
        "CCGGCCGGCCGGCCGG",  # high GC
        "ATATATATATATATAT",  # 0% GC
    ]

    def _gen(prompt: str, sampling: SamplingConfig) -> list[Candidate]:  # noqa: ARG001
        n = sampling.num_return_sequences
        return [
            Candidate(text=pool[i % len(pool)], tokens_generated=sampling.max_new_tokens)
            for i in range(n)
        ]

    return _gen


@pytest.fixture
def fake_generator():  # noqa: ANN201 - pytest fixture
    return _fake_generator()


@pytest.fixture
def tiny_pool():  # noqa: ANN201
    return [
        "ACGTACGT",
        "ACGTACGT",
        "ACGTACGT",
        "AAAAGGGG",  # outlier
    ]
