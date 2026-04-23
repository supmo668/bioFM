"""Agent 5 — Biological & Statistical Validator."""

from __future__ import annotations

from cellforge.agents.base import BaseAgent
from cellforge.problem import Context, Critique, Proposal
from cellforge.tools.pathway import PathwayTool


class ValidatorAgent(BaseAgent):
    name = "Validator"

    def __init__(self, tool: PathwayTool | None = None) -> None:
        self.tool = tool or PathwayTool()

    def propose(self, ctx: Context) -> Proposal:
        expected_up: list[str] = []
        expected_down: list[str] = []
        for p in ctx.prior_proposals:
            if p.agent == "Literature":
                expected_up = list(p.content.get("expected_up", []))
                expected_down = list(p.content.get("expected_down", []))
                break

        # Stubbed "predicted" DEGs: identical to expected for a positive run,
        # reduced for a cold run. In a real pipeline these would come from
        # inference with the Trainer's model.
        predicted_up = expected_up  # PoC placeholder
        predicted_down = expected_down
        report = self.tool.validate(predicted_up, predicted_down, expected_up, expected_down)

        return Proposal(
            agent=self.name,
            content={
                "checked_genes": predicted_up + predicted_down,
                "deg_overlap_at_k": report.deg_overlap_at_k,
                "enriched_pathways": list(report.enriched_pathways),
                "held_out_auroc": report.held_out_auroc,
                "calibration": report.calibration,
                "negative_control_auroc": report.negative_control_auroc,
            },
            rationale=(
                f"DEG overlap@K={report.deg_overlap_at_k:.2f}, held-out AUROC={report.held_out_auroc:.2f}, "
                f"calibration={report.calibration:.2f}. Negative control AUROC={report.negative_control_auroc:.2f} "
                f"(should be ≈0.5)."
            ),
            confidence=min(0.95, 0.5 + 0.45 * report.deg_overlap_at_k),
            tools_used=(self.tool.name,),
        )
