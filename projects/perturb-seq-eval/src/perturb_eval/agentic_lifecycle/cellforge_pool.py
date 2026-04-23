"""CellForge-backed AgentPool.

Wraps the real CellForge 5-agent roster (`cellforge.agents.*`) so the
lifecycle loop can drive them. Reuses the BioFM-grounded tools (BioGPT
for Literature, Geneformer for Validator) when ``use_biofm=True``.

See CellForge paper, arXiv:2508.02276, for the propose-critique-vote
methodology this class adapts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CellForgeAgentPool:
    """Pool that instantiates CellForge agents once and exposes the
    per-role ``propose`` hook expected by :func:`run_agentic_lifecycle`.

    ``use_biofm``: if ``True`` and the optional BioFM tools import, the
    Literature agent is backed by :class:`BioGPTMechanismTool` and the
    Validator by :class:`GeneformerValidatorTool`. Otherwise the
    CellForge defaults (mock deterministic tools) are used.
    """

    use_biofm: bool = True
    modality: str = "scRNA"
    organism: str = "human"
    cell_type_hint: str | None = "K562"
    _agents: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        from cellforge.agents.architect import ArchitectAgent
        from cellforge.agents.data_curator import DataCuratorAgent
        from cellforge.agents.literature import LiteratureAgent
        from cellforge.agents.trainer import TrainerAgent
        from cellforge.agents.validator import ValidatorAgent

        lit_tool = None
        val_tool = None
        if self.use_biofm:
            try:
                from perturb_eval.biofm_tools.biogpt_literature import (
                    BioGPTMechanismTool,
                )
                from perturb_eval.biofm_tools.geneformer_validator import (
                    GeneformerValidatorTool,
                )
                lit_tool = BioGPTMechanismTool()
                val_tool = GeneformerValidatorTool()
            except Exception:  # noqa: BLE001 — fall back silently if BioFM tools unavailable
                lit_tool, val_tool = None, None

        # LiteratureAgent and ValidatorAgent accept an optional `tool` kwarg
        # in our extended CellForge build; swallow if the upstream version
        # doesn't expose it.
        try:
            lit = LiteratureAgent(tool=lit_tool) if lit_tool else LiteratureAgent()
        except TypeError:
            lit = LiteratureAgent()
        try:
            val = ValidatorAgent(tool=val_tool) if val_tool else ValidatorAgent()
        except TypeError:
            val = ValidatorAgent()

        self._agents = {
            "DataCurator": DataCuratorAgent(),
            "Literature": lit,
            "Architect": ArchitectAgent(),
            "Trainer": TrainerAgent(),
            "Validator": val,
        }

    def propose(
        self,
        role: str,
        round_index: int,
        task_id: str,
        context: dict,
    ) -> dict:
        """Delegate to the CellForge agent and normalise the output shape
        to what :func:`run_agentic_lifecycle` expects."""
        from cellforge.problem import Context, Modality, Problem

        modality_enum = {
            "scRNA": Modality.SCRNA,
            "scRNA-seq": Modality.SCRNA,
        }.get(self.modality, Modality.SCRNA)

        problem = Problem(
            perturbation=f"{task_id} knockdown",
            modality=modality_enum,
            organism=self.organism,
            cell_type_hint=self.cell_type_hint,
        )
        ctx = Context(
            problem=problem,
            prior_proposals=(),
            prior_critiques=(),
            round_index=round_index,
        )
        agent = self._agents[role]
        proposal = agent.propose(ctx)
        return {
            "content": dict(proposal.content),
            "rationale": proposal.rationale,
            "confidence": float(proposal.confidence),
        }
