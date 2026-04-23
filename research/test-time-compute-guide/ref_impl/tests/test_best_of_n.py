from __future__ import annotations

import pytest

from ref_impl.best_of_n import best_of_n


def test_returns_argmax(deterministic_generator, answer_preferring_verifier) -> None:  # noqa: ANN001
    r = best_of_n("p", deterministic_generator, answer_preferring_verifier, n=8)
    assert r.winner.text == "answer_A"
    assert len(r.candidates) == 8


def test_counts_tokens(deterministic_generator, length_verifier) -> None:  # noqa: ANN001
    r = best_of_n("p", deterministic_generator, length_verifier, n=4)
    assert r.total_tokens == 40  # 4 × 10


def test_rejects_zero_n(deterministic_generator, length_verifier) -> None:  # noqa: ANN001
    with pytest.raises(ValueError):
        best_of_n("p", deterministic_generator, length_verifier, n=0)


def test_empty_generator_raises(length_verifier) -> None:  # noqa: ANN001
    def empty(prompt: str, *, n: int = 1):  # noqa: ARG001
        return []
    with pytest.raises(RuntimeError):
        best_of_n("p", empty, length_verifier, n=4)
