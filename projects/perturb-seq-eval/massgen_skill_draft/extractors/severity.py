"""LLM-driven severity projection.

For each ``AgentVote.reason`` string, call a lightweight rater backend
(prompts/severity_rater.md) and return a severity in [0, 1]. The rater is
abstract here — the concrete MassGen integration will inject the selected
backend from the parent run's config.

This module is deliberately small: the only non-obvious logic is (a) the
per-call cache to avoid re-rating the same reason twice, and (b) the
graceful-degradation default for truncated / missing reasons.
"""

from __future__ import annotations

from typing import Callable, Protocol


class AgentVoteLike(Protocol):
    voter_id: str
    voted_for: str
    reason: str


RaterBackend = Callable[[str], float]
"""Any callable that maps a prompt (rendered from the template) to a float in [0,1]."""


DEFAULT_SEVERITY_ON_MISSING_REASON = 0.2
"""A weak 'I have no signal' prior, logged when we skip the LLM call."""


def project_severity(
    agent_ids: list[str],
    votes: list[AgentVoteLike],
    rater: RaterBackend,
    *,
    prompt_template: str,
) -> list[list[float]]:
    """Return an N × (N-1) severity matrix S in the order of ``agent_ids``.

    S[i][k] is the severity from critic agent_ids[i] on target agent_ids[j],
    where j is the k-th agent that is not i (same projection shape used by
    ``perturb_eval.types.RoundTrace``).
    """
    n = len(agent_ids)
    mat: list[list[float]] = [[0.0] * (n - 1) for _ in range(n)]
    if n <= 1:
        return mat
    idx = {a: i for i, a in enumerate(agent_ids)}
    cache: dict[str, float] = {}

    for v in votes:
        src = idx.get(v.voter_id)
        if src is None:
            continue
        for tgt_id in agent_ids:
            if tgt_id == v.voter_id:
                continue
            # Only compute severity from voter against non-chosen alternatives.
            if tgt_id == v.voted_for:
                continue
            key = (v.reason or "").strip()
            if not key:
                sev = DEFAULT_SEVERITY_ON_MISSING_REASON
            else:
                if key not in cache:
                    prompt = prompt_template.format(
                        voter_id=v.voter_id,
                        voted_for=v.voted_for,
                        answer_labels=",".join(agent_ids),
                        reason_text=v.reason,
                    )
                    cache[key] = float(max(0.0, min(1.0, rater(prompt))))
                sev = cache[key]
            tgt = idx[tgt_id]
            col = tgt if tgt < src else tgt - 1
            mat[src][col] = sev
    return mat
