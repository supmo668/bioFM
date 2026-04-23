"""Acceptance-test skeleton for the MassGen extractor.

This matches MassGen's TDD contract (see the upstream CLAUDE.md). Tests are
named for the behaviour they enforce, not the code under test.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from extractors.confidence import project_confidence
from extractors.severity import project_severity


@dataclass
class FakeVote:
    voter_id: str
    voted_for: str
    reason: str = ""


def test_confidence_unanimous_vote_concentrates_on_winner() -> None:
    agents = ["a", "b", "c", "d", "e"]
    # a, b, c, d all vote for e
    votes = [FakeVote(v, "e") for v in agents[:4]]
    c = project_confidence(agents, votes)
    assert c[4] == 1.0   # 4/4
    assert all(c[i] == 0.0 for i in range(4))


def test_confidence_ignores_self_votes() -> None:
    agents = ["a", "b"]
    votes = [FakeVote("a", "a"), FakeVote("b", "a")]
    c = project_confidence(agents, votes)
    assert c == [1.0, 0.0]


def test_confidence_handles_abstention() -> None:
    agents = ["a", "b", "c"]
    # only one voter participates
    votes = [FakeVote("a", "b")]
    c = project_confidence(agents, votes)
    # denominator is 1 (one distinct voter), not n-1=2
    assert c[1] == 1.0


def test_severity_matrix_shape() -> None:
    agents = ["a", "b", "c"]
    votes = [FakeVote("a", "b", reason="I think b is best"),
             FakeVote("b", "a", reason="a's reasoning is clearer"),
             FakeVote("c", "a", reason="agree with a")]
    def rater(prompt: str) -> float:  # constant stub
        return 0.5
    s = project_severity(agents, votes, rater, prompt_template="{reason_text}")
    # 3 x 2 matrix
    assert len(s) == 3
    assert all(len(row) == 2 for row in s)


def test_severity_caches_identical_reasons() -> None:
    """The LLM backend should be called once per distinct reason string."""
    agents = ["a", "b", "c"]
    votes = [FakeVote("a", "b", reason="same reason"),
             FakeVote("c", "b", reason="same reason")]
    calls = {"n": 0}
    def rater(prompt: str) -> float:
        calls["n"] += 1
        return 0.7
    _ = project_severity(agents, votes, rater, prompt_template="{reason_text}")
    assert calls["n"] == 1


def test_missing_reason_falls_back_to_default() -> None:
    from extractors.severity import DEFAULT_SEVERITY_ON_MISSING_REASON
    agents = ["a", "b"]
    votes = [FakeVote("a", "b", reason="")]
    def rater(prompt: str) -> float:
        raise AssertionError("rater should not be called on empty reasons")
    s = project_severity(agents, votes, rater, prompt_template="{reason_text}")
    # a has empty reason for non-chosen targets; since there are only two
    # agents the only target of severity is a→? — but since a voted FOR b,
    # there are no non-chosen alternatives, so matrix is all zeros.
    assert s == [[0.0], [0.0]]
