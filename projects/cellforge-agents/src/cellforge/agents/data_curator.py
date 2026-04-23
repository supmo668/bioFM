"""Agent 1 — Data Curator."""

from __future__ import annotations

from cellforge.agents.base import BaseAgent
from cellforge.problem import Context, Critique, Proposal
from cellforge.tools.omics import OmicsTool


class DataCuratorAgent(BaseAgent):
    name = "DataCurator"

    def __init__(self, tool: OmicsTool | None = None) -> None:
        self.tool = tool or OmicsTool()

    def propose(self, ctx: Context) -> Proposal:
        dataset_id = self.tool.fetch(ctx.problem.modality.value, ctx.problem.perturbation)
        qc = self.tool.qc(dataset_id)
        passes_qc = qc.pct_mito_max < 25 and qc.doublet_rate < 0.1
        return Proposal(
            agent=self.name,
            content={
                "dataset_id": qc.dataset_id,
                "n_cells": qc.n_cells,
                "n_genes": qc.n_genes,
                "hvgs": qc.hvgs,
                "pct_mito_max": qc.pct_mito_max,
                "doublet_rate": qc.doublet_rate,
                "passes_qc": passes_qc,
            },
            rationale=(
                f"Fetched {qc.dataset_id}: {qc.n_cells:,} cells × {qc.n_genes:,} genes. "
                f"Mito ≤ {qc.pct_mito_max:.1f}%, doublets {qc.doublet_rate:.2%}. "
                f"{'Ready for downstream.' if passes_qc else 'Needs additional filtering.'}"
            ),
            confidence=0.85 if passes_qc else 0.5,
            tools_used=(self.tool.name,),
        )

    def critique(self, ctx: Context, other: Proposal) -> Critique:
        """Flag architectures that ignore cell count or HVG selection."""
        if other.agent == "Architect":
            content = other.content
            # Architects should account for cell count choice of batch size
            if "d_model" in content and content["d_model"] > 1024:
                return Critique(
                    from_agent=self.name,
                    on_agent=other.agent,
                    severity=0.6,
                    comment="d_model > 1024 likely OOMs at 48k cells — consider 512 or gradient checkpointing.",
                )
        return super().critique(ctx, other)
