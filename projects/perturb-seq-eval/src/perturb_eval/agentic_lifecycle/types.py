"""Immutable data carriers for one complete lifecycle run.

See docs/plans/2026-04-22-end-to-end-agentic-lifecycle.md Task 1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Optional, get_args

# Where a LifecycleStep's proposal came from (D4 / C-KEY-2):
#   * "llm"      — served by an OpenRouter pool model; ``model_id`` names it.
#                  The ONLY rows the analyser's per-role entropy counts.
#   * "fallback" — LLMAgentPool's deterministic rule-based default after a
#                  documented runtime LLM failure; ``model_id`` is None. Any
#                  such row in the real sweep marks the run FAILED (C-KEY-2).
#   * "mock"     — any non-LLM, deterministic pool: MockAgentPool (offline
#                  tests) and CellForgeAgentPool (CellForge's rule-based
#                  agents; the seed is unused, no pool model is drawn).
#                  ``model_id`` is None. Never counted as an LLM choice.
StepSource = Literal["llm", "fallback", "mock"]
STEP_SOURCES: tuple[str, ...] = get_args(StepSource)


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
    """One agent's contribution within one round (propose + LLM rating).

    ``model_id`` / ``source`` record provenance of ``proposal_content`` —
    see :data:`StepSource`. The loop always writes both from the pool's
    ``propose`` output; the defaults only serve hand-built steps (tests).
    """

    round_index: int
    agent_name: str
    proposal_content: dict[str, Any]
    rationale: str
    llm_confidence: float
    execution_artifact_path: str | None
    wall_time_sec: float
    succeeded: bool
    model_id: str | None = None
    source: StepSource = "llm"


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
    # T8b provenance: train-only HVG size / forced-target count per round
    # (the DataCurator may change n_top_hvg between rounds), the selection
    # mode, and the learned-parameter count of the last successfully fitted
    # backbone. Defaults keep hand-built runs (tests, stubs) valid.
    hvg_n_per_round: tuple[int, ...] = ()
    hvg_n_forced_per_round: tuple[int, ...] = ()
    hvg_mode: str | None = None
    n_params: int | None = None
