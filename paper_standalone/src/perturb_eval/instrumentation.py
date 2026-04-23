"""Non-invasive instrumentation for the CellForge orchestrator.

We do *not* patch the orchestrator class. Instead we accept its
``ConsensusResult`` (or any object with a ``.rounds`` iterable exposing
``.proposals`` and ``.critiques``) and translate it into a ``RunTrace``. This
means the orchestrator stays single-responsibility and the evaluation layer is
easy to swap.
"""

from __future__ import annotations

from typing import Any

from perturb_eval.types import RoundTrace, RunTrace


def _build_critique_matrix(
    critiques: list[Any],
    agent_names: list[str],
) -> tuple[tuple[float, ...], ...]:
    """Build an N×(N-1)-shaped severity matrix in agent_names order.

    Row i of the output lists severities from agent_i on the other N-1 agents,
    in the order of `agent_names` with agent_i skipped.
    """
    idx = {name: i for i, name in enumerate(agent_names)}
    n = len(agent_names)
    rows: list[list[float]] = [[0.0] * (n - 1) for _ in range(n)]
    # Accumulator: for each critic, collect (target_idx, severity) pairs.
    for c in critiques:
        src = idx.get(getattr(c, "from_agent", None))
        tgt = idx.get(getattr(c, "on_agent", None))
        sev = float(getattr(c, "severity", 0.0))
        if src is None or tgt is None or src == tgt:
            continue
        # Project tgt onto the N-1-wide row (skip src's column).
        col = tgt if tgt < src else tgt - 1
        rows[src][col] = sev
    return tuple(tuple(r) for r in rows)


def round_trace_from_consensus_round(
    r_obj: Any,
    round_index: int,
    compute_tokens: int = 0,
) -> RoundTrace:
    """Build a RoundTrace from an orchestrator ``RoundResult``-like object."""
    proposals = list(r_obj.proposals)
    critiques = list(r_obj.critiques)
    agent_names = [p.agent for p in proposals]
    confidences = tuple(float(p.confidence) for p in proposals)
    matrix = _build_critique_matrix(critiques, agent_names)
    # Winner within the round: argmax of (confidence − mean severity received).
    sev_received = [0.0] * len(proposals)
    for c in critiques:
        try:
            j = agent_names.index(c.on_agent)
        except ValueError:
            continue
        sev_received[j] += float(c.severity)
    # divide by number of critics pointing at j (N-1) for mean
    n = len(proposals)
    mean_received = [s / (n - 1) if n > 1 else 0.0 for s in sev_received]
    scores = [confidences[i] - mean_received[i] for i in range(n)]
    winner_index = int(max(range(n), key=scores.__getitem__)) if n else 0
    consensus_score = float(scores[winner_index]) if n else 0.0
    return RoundTrace(
        round_index=round_index,
        agent_names=tuple(agent_names),
        confidences=confidences,
        critique_severities=matrix,
        winner_index=winner_index,
        consensus_score=consensus_score,
        compute_tokens=compute_tokens,
    )


def run_trace_from_consensus(
    result: Any,
    task_id: str,
    *,
    backbone: str = "unknown",
    compute_tokens_per_round: int | list[int] = 0,
) -> RunTrace:
    """Build a RunTrace from an orchestrator ``ConsensusResult``-like object."""
    rounds_obj = list(result.rounds)
    if isinstance(compute_tokens_per_round, int):
        tokens_seq = [compute_tokens_per_round] * len(rounds_obj)
    else:
        tokens_seq = list(compute_tokens_per_round)
        if len(tokens_seq) != len(rounds_obj):
            raise ValueError("compute_tokens_per_round length mismatch")
    round_traces = tuple(
        round_trace_from_consensus_round(r, idx, tokens_seq[idx])
        for idx, r in enumerate(rounds_obj)
    )
    return RunTrace(
        task_id=task_id,
        rounds=round_traces,
        converged=bool(getattr(result, "converged", False)),
        backbone=backbone,
    )
