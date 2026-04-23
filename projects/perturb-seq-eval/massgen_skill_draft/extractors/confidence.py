"""Vote-share projection of per-agent confidence (no LLM).

Given a round's ``AgentVote`` records, agent j's projected confidence is

    ĉ_j = (number of peer votes pointing at j) / (N − 1)

where N is the number of voting agents in the round. If some voters abstain,
the denominator is adjusted accordingly.

This projection is deterministic, cheap, and well-defined when the
orchestrator records votes categorically (one voter → one voted_for).
"""

from __future__ import annotations

from collections import Counter
from typing import Iterable, Protocol


class AgentVoteLike(Protocol):
    voter_id: str
    voted_for: str


def project_confidence(
    agent_ids: list[str],
    votes: Iterable[AgentVoteLike],
) -> list[float]:
    """Return [ĉ_j]_{j=1..N} in the order of ``agent_ids``."""
    n = len(agent_ids)
    if n == 0:
        return []
    if n == 1:
        return [1.0]
    idx = {a: i for i, a in enumerate(agent_ids)}
    counts = Counter()
    voters_seen: set[str] = set()
    for v in votes:
        if v.voted_for not in idx:
            continue
        if v.voter_id == v.voted_for:   # self-votes excluded
            continue
        counts[v.voted_for] += 1
        voters_seen.add(v.voter_id)
    # Denominator: number of *other* voters who could have voted for j.
    # If some voters abstained, divide by (distinct voters seen) instead of (n-1).
    denom = max(1, min(n - 1, len(voters_seen)))
    return [counts.get(a, 0) / denom for a in agent_ids]
