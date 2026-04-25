"""Immutable data carriers for one complete lifecycle run.

See docs/plans/2026-04-22-end-to-end-agentic-lifecycle.md Task 1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class ExecutedProposal:
    """An agent's proposal after it has been executed against real artefacts."""

    agent_name: str
    proposal_content: dict[str, Any]
    rationale: str
    llm_confidence: float
    execution_artifact_path: str | None
    wall_time_sec: float
    succeeded: bool


@dataclass(frozen=True)
class StructuredCritiqueDTO:
    """Validator critique payload consumed by the next round's Architect.

    Kept as a plain dataclass (not a Pydantic model) so it's trivially
    serialisable alongside other ``types.py`` DTOs. The Pydantic mirror
    lives in :mod:`proposal_schema` for LLM-output validation.
    """

    which_genes_failed: tuple[str, ...] = ()
    suggested_next_config_delta: dict[str, Any] = field(default_factory=dict)
    accept_reason: str = ""


@dataclass(frozen=True)
class ExecutedValidation:
    """Validator's report after scoring a trained model."""

    msd_topk: float
    biofm_agreement: float
    deg_overlap_at_k: float
    accepted: bool
    rationale: str
    critique: Optional[StructuredCritiqueDTO] = None


@dataclass(frozen=True)
class LifecycleStep:
    """One agent's contribution within one round (propose + LLM rating)."""

    round_index: int
    agent_name: str
    proposal_content: dict[str, Any]
    rationale: str
    llm_confidence: float
    execution_artifact_path: str | None
    wall_time_sec: float
    succeeded: bool


@dataclass(frozen=True)
class LifecycleRun:
    """A full multi-round run on one perturbation task."""

    task_id: str
    steps: tuple[LifecycleStep, ...]
    final_msd_topk: float
    final_validator_agreement: float
    n_rounds: int
    n_agents: int
    backbone_used: str
