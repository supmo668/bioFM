from __future__ import annotations

from ref_impl.majority_vote import majority_vote


def test_majority_wins(deterministic_generator) -> None:  # noqa: ANN001
    # With pool size 4, n=8 → answer_A appears 4 times, B and C 2 each.
    r = majority_vote("p", deterministic_generator, n=8)
    assert r.winner.text == "answer_A"
    assert r.counts["answer_A"] >= r.counts["answer_B"]


def test_counts_sum_to_n(deterministic_generator) -> None:  # noqa: ANN001
    r = majority_vote("p", deterministic_generator, n=10)
    assert sum(r.counts.values()) == 10


def test_custom_projection() -> None:
    from ref_impl.types import Candidate

    pool = [
        Candidate("x=7.0000", tokens=1),
        Candidate("x=7.0001", tokens=1),  # same numeric answer, different text
        Candidate("x=8.0",   tokens=1),
    ]

    def gen(prompt: str, *, n: int = 1):  # noqa: ARG001
        return [pool[i % len(pool)] for i in range(n)]

    def project(c: Candidate) -> str:
        return f"{round(float(c.text.split('=')[-1]))}"

    r = majority_vote("p", gen, n=6, project=project)
    # 4 of 6 samples round to "7" → majority
    assert project(r.winner) == "7"
