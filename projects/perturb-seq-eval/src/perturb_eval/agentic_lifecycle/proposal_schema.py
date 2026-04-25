"""Pydantic v2 schemas for the five-agent lifecycle proposals.

The schemas preserve the dict-based contract at the ``AgentPool.propose``
boundary (for backward compat with the existing MockAgentPool/CellForge
adapter) but add:

  * a wider Architect configuration space (backbone, HVG, LR, λ, epochs,
    n_agents, n_rounds) so agents make genuine choices across runs;
  * a :class:`StructuredCritique` inside :class:`ValidatorProposal` so
    the next round's Architect can apply a targeted delta, not just read
    a free-text rationale.

See ``.claude/plans/v0.5.0-real-perturb-seq.md`` §Phase 2.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

HVG_CHOICES = (500, 1000, 2000, 5000)
HvgCount = Literal[500, 1000, 2000, 5000]
HvgMethod = Literal["seurat", "scanpy"]
SplitStrategy = Literal["per_pert_holdout", "unseen_gene"]
BatchCorrection = Literal["none", "combat", "harmony"]
BackboneName = Literal["linear", "mlp", "scgpt_small"]


class _BaseProposal(BaseModel):
    """Base class that tolerates extra keys from noisy LLM output."""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)


class DataCuratorProposal(_BaseProposal):
    hvg_method: HvgMethod = "seurat"
    hvg_count: HvgCount = 2000
    qc_mito_max: float = Field(default=12.0, gt=0, le=100)
    split_strategy: SplitStrategy = "per_pert_holdout"
    batch_correction: BatchCorrection = "none"


class LiteratureProposal(_BaseProposal):
    pathway_prior: dict[str, float] = Field(default_factory=dict)
    ppi_neighbors: tuple[str, ...] = ()
    tool_calls: tuple[str, ...] = ()
    expected_up: tuple[str, ...] = ()
    expected_down: tuple[str, ...] = ()

    def model_post_init(self, _ctx: Any, /) -> None:
        for gene, weight in self.pathway_prior.items():
            if not (0.0 <= weight <= 1.0):
                raise ValueError(
                    f"pathway_prior[{gene!r}] = {weight} outside [0, 1]"
                )


class ArchitectProposal(_BaseProposal):
    backbone: BackboneName = "linear"
    n_agents: int = Field(default=5, ge=2, le=8)
    n_rounds: int = Field(default=2, ge=1, le=5)
    hvg_count: HvgCount = 2000
    learning_rate: float = Field(default=1e-2, gt=0)
    ridge_lambda: float = Field(default=1.0, ge=0)
    epochs: int = Field(default=40, ge=1, le=500)


class TrainerProposal(_BaseProposal):
    lr: float = Field(default=1e-2, gt=0)
    epochs: int = Field(default=50, ge=1, le=500)
    ridge_lambda: float = Field(default=1.0, ge=0)


class StructuredCritique(_BaseProposal):
    """Validator critique feedback loop payload."""

    which_genes_failed: tuple[str, ...] = ()
    suggested_next_config_delta: dict[str, Any] = Field(default_factory=dict)
    accept_reason: str = ""


class ValidatorProposal(_BaseProposal):
    dynamic_threshold_msd: float = Field(default=0.1, ge=0.02, le=0.3)
    critique: StructuredCritique = Field(default_factory=StructuredCritique)


_ROLE_TO_SCHEMA: dict[str, type[_BaseProposal]] = {
    "DataCurator": DataCuratorProposal,
    "Literature": LiteratureProposal,
    "Architect": ArchitectProposal,
    "Trainer": TrainerProposal,
    "Validator": ValidatorProposal,
}


def parse_proposal(role: str, data: dict) -> _BaseProposal:
    """Validate a raw LLM/dict payload into the role-specific schema.

    Extra fields are tolerated (LLMs frequently add commentary keys).
    Missing optional fields fall back to defaults; missing required
    fields raise :class:`ValueError` via Pydantic.
    """
    try:
        schema = _ROLE_TO_SCHEMA[role]
    except KeyError as exc:  # pragma: no cover — guarded by caller
        raise ValueError(f"unknown role {role!r}") from exc
    return schema.model_validate(data)


__all__ = [
    "ArchitectProposal",
    "DataCuratorProposal",
    "LiteratureProposal",
    "StructuredCritique",
    "TrainerProposal",
    "ValidatorProposal",
    "parse_proposal",
]
