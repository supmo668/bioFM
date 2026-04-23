"""Immutable data carriers for problems, proposals, critiques."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Modality(str, Enum):
    SCRNA = "scRNA-seq"
    SCATAC = "scATAC-seq"
    CITE = "CITE-seq"


@dataclass(frozen=True)
class Problem:
    """A perturbation-response modelling task."""

    perturbation: str  # e.g. "GSK3B knockout", "LPS 100 ng/mL", "IL-6 stim"
    modality: Modality = Modality.SCRNA
    organism: str = "human"
    cell_type_hint: str | None = None
    target_deg_count: int = 500  # downstream evaluation: top-K DEG agreement
    budget_seconds: int = 60  # soft compute budget for the whole run


@dataclass(frozen=True)
class Proposal:
    """A single agent's structured proposal."""

    agent: str
    content: dict[str, Any]  # agent-specific payload (dataset id, architecture, etc.)
    rationale: str
    confidence: float  # [0, 1]
    tools_used: tuple[str, ...] = ()


@dataclass(frozen=True)
class Critique:
    """One agent's critique of another agent's proposal."""

    from_agent: str
    on_agent: str
    severity: float  # 0.0 (approve) → 1.0 (reject)
    comment: str


@dataclass(frozen=True)
class Context:
    """Shared blackboard passed to every agent at each round."""

    problem: Problem
    prior_proposals: tuple[Proposal, ...] = field(default_factory=tuple)
    prior_critiques: tuple[Critique, ...] = field(default_factory=tuple)
    round_index: int = 0
