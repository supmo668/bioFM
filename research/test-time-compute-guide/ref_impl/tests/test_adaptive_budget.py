from __future__ import annotations

from ref_impl.adaptive_budget import Difficulty, adaptive_route
from ref_impl.types import Candidate


def _gen_factory(pool_texts: list[str]):
    def _gen(prompt: str, *, n: int = 1):  # noqa: ARG001
        return [Candidate(pool_texts[i % len(pool_texts)], tokens=1) for i in range(n)]
    return _gen


def _identity_reviser(prompt: str, draft: Candidate) -> Candidate:  # noqa: ARG001
    return draft


def test_easy_prompt_routes_to_revision() -> None:
    gen = _gen_factory(["answer_A"])  # all identical, max score
    def verify(c: Candidate, *, prompt: str = "") -> float:  # noqa: ARG001
        return 0.95  # tight, high → EASY
    r = adaptive_route("p", gen, verify, _identity_reviser, probe_n=4, budget=16)
    assert r.difficulty is Difficulty.EASY
    assert r.strategy_used == "iterative_revision"


def test_hard_prompt_routes_to_bon() -> None:
    gen = _gen_factory(["a", "b", "c"])

    def verify(c: Candidate, *, prompt: str = "") -> float:  # noqa: ARG001
        # Wide spread: a=0.9, b=0.0, c=0.5 → spread 0.9, mean 0.47 → HARD
        return {"a": 0.9, "b": 0.0, "c": 0.5}[c.text]

    r = adaptive_route("p", gen, verify, _identity_reviser, probe_n=3, budget=12)
    assert r.difficulty is Difficulty.HARD
    assert r.strategy_used == "best_of_n"


def test_medium_prompt_routes_to_weighted_majority() -> None:
    gen = _gen_factory(["x", "y"])

    def verify(c: Candidate, *, prompt: str = "") -> float:  # noqa: ARG001
        return 0.55 if c.text == "x" else 0.45  # mean 0.5, spread 0.1 → MEDIUM

    r = adaptive_route("p", gen, verify, _identity_reviser, probe_n=2, budget=8)
    assert r.difficulty is Difficulty.MEDIUM
    assert r.strategy_used == "weighted_majority"


def test_probe_n_below_two_rejected() -> None:
    import pytest
    gen = _gen_factory(["a"])
    def v(c, *, prompt: str = ""):  # noqa: ANN001, ARG001
        return 1.0
    with pytest.raises(ValueError):
        adaptive_route("p", gen, v, _identity_reviser, probe_n=1, budget=8)
