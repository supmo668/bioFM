"""Agent 2 — Literature / Prior."""

from __future__ import annotations

from cellforge.agents.base import BaseAgent
from cellforge.problem import Context, Critique, Proposal
from cellforge.tools.literature import LiteratureTool


class LiteratureAgent(BaseAgent):
    name = "Literature"

    def __init__(self, tool: LiteratureTool | None = None) -> None:
        self.tool = tool or LiteratureTool()

    def propose(self, ctx: Context) -> Proposal:
        mech = self.tool.mechanism(ctx.problem.perturbation)
        hits = self.tool.search(ctx.problem.perturbation, max_hits=5)
        confidence = 0.75 if mech.get("pathways", ["unknown"]) != ["unknown"] else 0.35
        return Proposal(
            agent=self.name,
            content={
                "pathways": mech["pathways"],
                "expected_up": mech.get("up", []),
                "expected_down": mech.get("down", []),
                "references": [h.pmid for h in hits],
            },
            rationale=(
                f"{ctx.problem.perturbation} is linked to pathways {mech['pathways']}; "
                f"{len(mech.get('up', []))} expected-up and {len(mech.get('down', []))} expected-down genes."
            ),
            confidence=confidence,
            tools_used=(self.tool.name,),
        )

    def critique(self, ctx: Context, other: Proposal) -> Critique:
        """Validator should be checking against our expected gene list."""
        if other.agent == "Validator":
            expected = set(self._expected_genes(ctx))
            checked = set(other.content.get("checked_genes", []))
            if expected and not expected.issubset(checked):
                missing = expected - checked
                return Critique(
                    from_agent=self.name,
                    on_agent=other.agent,
                    severity=0.7,
                    comment=f"Validator did not check expected marker genes: {sorted(missing)[:5]}",
                )
        return super().critique(ctx, other)

    def _expected_genes(self, ctx: Context) -> list[str]:
        mech = self.tool.mechanism(ctx.problem.perturbation)
        return list(mech.get("up", [])) + list(mech.get("down", []))
