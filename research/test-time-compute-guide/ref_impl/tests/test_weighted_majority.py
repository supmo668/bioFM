from __future__ import annotations

from ref_impl.types import Candidate
from ref_impl.weighted_majority import weighted_majority


def test_weights_tip_the_vote(answer_preferring_verifier) -> None:  # noqa: ANN001
    # Pool arranged so that vanilla majority would pick "wrong", but weighted
    # majority (answer_A score 0.9 vs others 0.1-0.3) picks answer_A.
    pool = [
        Candidate("answer_A", tokens=1),
        Candidate("answer_B", tokens=1),
        Candidate("answer_B", tokens=1),  # B has count majority
    ]

    def gen(prompt: str, *, n: int = 1):  # noqa: ARG001
        return pool[:n]

    r = weighted_majority("p", gen, answer_preferring_verifier, n=3)
    # answer_A score = 0.9 ; answer_B total = 0.3 + 0.3 = 0.6 → A still wins.
    assert r.winner.text == "answer_A"
    assert r.class_scores["answer_A"] == 0.9


def test_degenerates_to_majority_when_scores_equal() -> None:
    pool = [
        Candidate("answer_A", tokens=1),
        Candidate("answer_B", tokens=1),
        Candidate("answer_B", tokens=1),
    ]

    def gen(prompt: str, *, n: int = 1):  # noqa: ARG001
        return pool[:n]

    def uniform(c: Candidate, *, prompt: str = "") -> float:  # noqa: ARG001
        return 1.0

    r = weighted_majority("p", gen, uniform, n=3)
    assert r.winner.text == "answer_B"
