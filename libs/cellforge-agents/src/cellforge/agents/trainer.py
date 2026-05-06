"""Agent 4 — Trainer / Experiment."""

from __future__ import annotations

from cellforge.agents.base import BaseAgent
from cellforge.problem import Context, Critique, Proposal
from cellforge.tools.trainer import TrainerTool


class TrainerAgent(BaseAgent):
    name = "Trainer"

    def __init__(self, tool: TrainerTool | None = None) -> None:
        self.tool = tool or TrainerTool()

    def propose(self, ctx: Context) -> Proposal:
        # Inspect prior proposals for n_cells and backbone. If the curator or
        # architect hasn't spoken yet we fall back to sane defaults.
        n_cells = 50_000
        backbone = "scGPT"
        for p in ctx.prior_proposals:
            if p.agent == "DataCurator":
                n_cells = int(p.content.get("n_cells", n_cells))
            if p.agent == "Architect":
                backbone = str(p.content.get("backbone", backbone))

        recipe = self.tool.build(n_cells, backbone, ctx.problem.budget_seconds)
        return Proposal(
            agent=self.name,
            content={
                "optimizer": recipe.optimizer,
                "lr": recipe.lr,
                "epochs": recipe.epochs,
                "batch_size": recipe.batch_size,
                "cv_split": recipe.cv_split,
                "early_stop_rule": recipe.early_stop_rule,
                "grad_accum": recipe.grad_accum,
                "backbone": backbone,
            },
            rationale=(
                f"Adamw + lr={recipe.lr} for {recipe.epochs} epochs on {backbone} "
                f"with batch={recipe.batch_size}; {recipe.cv_split} CV, early stop on {recipe.early_stop_rule}."
            ),
            confidence=0.8,
            tools_used=(self.tool.name,),
        )

    def critique(self, ctx: Context, other: Proposal) -> Critique:
        """Warn if architect picks a model that won't fit our budget."""
        if other.agent == "Architect" and other.content.get("d_model", 0) > 2048:
            return Critique(
                from_agent=self.name,
                on_agent=other.agent,
                severity=0.8,
                comment="d_model > 2048 won't fit the compute budget; downgrade or use LoRA.",
            )
        return super().critique(ctx, other)
