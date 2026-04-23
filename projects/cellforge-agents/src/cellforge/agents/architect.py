"""Agent 3 — Model Architect."""

from __future__ import annotations

from cellforge.agents.base import BaseAgent
from cellforge.problem import Context, Critique, Proposal
from cellforge.tools.biofm_catalog import BioFMCatalog


class ArchitectAgent(BaseAgent):
    name = "Architect"

    def __init__(self, catalog: BioFMCatalog | None = None) -> None:
        self.catalog = catalog or BioFMCatalog()

    def propose(self, ctx: Context) -> Proposal:
        candidates = self.catalog.suggest(ctx.problem.modality.value)
        if not candidates:
            return Proposal(
                agent=self.name,
                content={"backbone": None},
                rationale=f"No backbone in catalog for modality {ctx.problem.modality.value}",
                confidence=0.1,
                tools_used=(self.catalog.name,),
            )
        # pick first suggestion (the doc orders by recommendation strength)
        pick = candidates[0]
        d_model = 512  # conservative default; DataCurator can veto larger
        return Proposal(
            agent=self.name,
            content={
                "backbone": pick.name,
                "head": "perturbation_adapter",
                "d_model": d_model,
                "n_layers": 12,
                "alternatives": [c.name for c in candidates[1:]],
            },
            rationale=f"{pick.name} — {pick.note}. Plus a small perturbation adapter head.",
            confidence=0.7,
            tools_used=(self.catalog.name,),
        )
