"""MassGen-inspired orchestrator: propose → critique → vote, with iterative refinement.

The orchestrator is deliberately small and deterministic so the *pattern* is
visible. For a production system, swap ``run`` for an async implementation that
dispatches agents concurrently.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from cellforge.agents.base import BaseAgent
from cellforge.problem import Context, Critique, Problem, Proposal

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RoundResult:
    round_index: int
    proposals: tuple[Proposal, ...]
    critiques: tuple[Critique, ...]


@dataclass(frozen=True)
class ConsensusResult:
    winner: Proposal
    all_proposals: tuple[Proposal, ...]
    all_critiques: tuple[Critique, ...]
    rounds: tuple[RoundResult, ...]
    converged: bool
    consensus_score: float  # mean confidence of winner weighted by acceptance


class Orchestrator:
    """Drives the 5-agent loop to consensus."""

    def __init__(
        self,
        agents: list[BaseAgent],
        *,
        max_rounds: int = 2,
        consensus_threshold: float = 0.7,
    ) -> None:
        if not agents:
            raise ValueError("orchestrator needs at least one agent")
        self.agents = agents
        self.max_rounds = max_rounds
        self.consensus_threshold = consensus_threshold

    def run(self, problem: Problem) -> ConsensusResult:
        all_proposals: list[Proposal] = []
        all_critiques: list[Critique] = []
        rounds: list[RoundResult] = []
        converged = False

        for r in range(self.max_rounds):
            ctx = Context(
                problem=problem,
                prior_proposals=tuple(all_proposals),
                prior_critiques=tuple(all_critiques),
                round_index=r,
            )

            # ---- 1. every agent proposes ----------------------------------
            round_proposals: list[Proposal] = []
            for agent in self.agents:
                prop = agent.propose(ctx)
                round_proposals.append(prop)
                logger.info("round %d %s confidence=%.2f", r, agent.name, prop.confidence)

            # ---- 2. every agent critiques every other's proposal ----------
            round_critiques: list[Critique] = []
            for agent in self.agents:
                for other in round_proposals:
                    if other.agent == agent.name:
                        continue
                    round_critiques.append(agent.critique(ctx, other))

            rounds.append(RoundResult(round_index=r, proposals=tuple(round_proposals),
                                       critiques=tuple(round_critiques)))
            all_proposals.extend(round_proposals)
            all_critiques.extend(round_critiques)

            # ---- 3. vote: winner is the proposal with best (confidence - mean critique severity)
            score = self._score_round(round_proposals, round_critiques)
            winner_idx = max(range(len(round_proposals)), key=score.__getitem__)

            if score[winner_idx] >= self.consensus_threshold:
                converged = True
                return ConsensusResult(
                    winner=round_proposals[winner_idx],
                    all_proposals=tuple(all_proposals),
                    all_critiques=tuple(all_critiques),
                    rounds=tuple(rounds),
                    converged=True,
                    consensus_score=score[winner_idx],
                )

        # Didn't converge — return the best of the last round anyway.
        last = rounds[-1]
        final_score = self._score_round(list(last.proposals), list(last.critiques))
        winner_idx = max(range(len(last.proposals)), key=final_score.__getitem__)
        return ConsensusResult(
            winner=last.proposals[winner_idx],
            all_proposals=tuple(all_proposals),
            all_critiques=tuple(all_critiques),
            rounds=tuple(rounds),
            converged=converged,
            consensus_score=final_score[winner_idx],
        )

    @staticmethod
    def _score_round(proposals: list[Proposal], critiques: list[Critique]) -> list[float]:
        scores: list[float] = []
        for p in proposals:
            relevant = [c for c in critiques if c.on_agent == p.agent]
            mean_severity = sum(c.severity for c in relevant) / len(relevant) if relevant else 0.0
            scores.append(max(0.0, p.confidence - mean_severity))
        return scores
