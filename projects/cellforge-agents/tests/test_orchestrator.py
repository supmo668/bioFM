"""Tests for the propose → critique → vote loop."""

from __future__ import annotations

import pytest

from cellforge.agents import build_default_team
from cellforge.agents.base import BaseAgent
from cellforge.orchestrator import Orchestrator
from cellforge.problem import Context, Critique, Modality, Problem, Proposal


@pytest.mark.unit
class TestOrchestrator:
    def test_runs_all_five_agents(self) -> None:
        orch = Orchestrator(build_default_team(), max_rounds=1)
        result = orch.run(Problem(perturbation="GSK3B knockout", modality=Modality.SCRNA))
        agents_seen = {p.agent for p in result.rounds[0].proposals}
        assert len(agents_seen) == 5

    def test_critiques_cover_every_other_agent(self) -> None:
        orch = Orchestrator(build_default_team(), max_rounds=1)
        result = orch.run(Problem(perturbation="LPS stim", modality=Modality.SCRNA))
        # 5 agents × 4 others = 20 critiques per round
        assert len(result.rounds[0].critiques) == 20

    def test_converges_when_confidence_high(self) -> None:
        orch = Orchestrator(build_default_team(), max_rounds=2, consensus_threshold=0.5)
        result = orch.run(Problem(perturbation="GSK3B knockout", modality=Modality.SCRNA))
        assert result.converged
        assert result.consensus_score >= 0.5

    def test_winner_is_a_real_proposal(self) -> None:
        orch = Orchestrator(build_default_team(), max_rounds=1)
        result = orch.run(Problem(perturbation="IL-6 stim", modality=Modality.SCRNA))
        assert result.winner in result.all_proposals

    def test_empty_team_rejected(self) -> None:
        with pytest.raises(ValueError):
            Orchestrator([], max_rounds=1)

    def test_second_round_sees_prior_state(self) -> None:
        """A tracked agent must receive prior_proposals on round 2."""

        seen_rounds: list[int] = []
        seen_prior_counts: list[int] = []

        class TrackingAgent(BaseAgent):
            name = "Tracking"

            def propose(self, ctx: Context) -> Proposal:
                seen_rounds.append(ctx.round_index)
                seen_prior_counts.append(len(ctx.prior_proposals))
                return Proposal(agent=self.name, content={}, rationale="x", confidence=0.1)

            def critique(self, ctx: Context, other: Proposal) -> Critique:  # noqa: ARG002
                return Critique(from_agent=self.name, on_agent=other.agent,
                                severity=0.9, comment="low-confidence dummy")

        orch = Orchestrator([TrackingAgent()], max_rounds=2, consensus_threshold=0.99)
        orch.run(Problem(perturbation="x", modality=Modality.SCRNA))
        assert seen_rounds == [0, 1]
        assert seen_prior_counts[0] == 0
        assert seen_prior_counts[1] == 1
