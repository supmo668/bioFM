from __future__ import annotations

from ref_impl.iterative_revision import iterative_revision
from ref_impl.types import Candidate


def test_score_rises_monotonically(length_verifier, improving_reviser) -> None:  # noqa: ANN001
    def gen(prompt: str, *, n: int = 1):  # noqa: ARG001
        return [Candidate("x", tokens=1)]
    r = iterative_revision("p", gen, improving_reviser, length_verifier, max_rounds=4)
    assert list(r.scores) == sorted(r.scores)
    assert r.winner.text == "x!!!"


def test_plateau_triggers_convergence(length_verifier, plateauing_reviser) -> None:  # noqa: ANN001
    def gen(prompt: str, *, n: int = 1):  # noqa: ARG001
        return [Candidate("abc", tokens=3)]
    r = iterative_revision("p", gen, plateauing_reviser, length_verifier, max_rounds=8)
    assert r.converged
    assert len(r.trajectory) == 2  # initial draft + one revision that didn't improve


def test_counts_all_trajectory_tokens(length_verifier, improving_reviser) -> None:  # noqa: ANN001
    def gen(prompt: str, *, n: int = 1):  # noqa: ARG001
        return [Candidate("x", tokens=1)]
    r = iterative_revision("p", gen, improving_reviser, length_verifier, max_rounds=4)
    assert r.total_tokens == 1 + 2 + 3 + 4  # each revision adds one token
