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
    # A2-1: the role's own stated confidence in [0, 1] on an "llm" step (the
    # loop refuses an "llm" step without one); ``None`` on a "fallback" step —
    # never imputed.
    llm_confidence: float | None
    execution_artifact_path: str | None
    wall_time_sec: float
    succeeded: bool
    model_id: str | None = None
    source: StepSource = "llm"
    # QG C6: True when the LLM reply was served from the disk cache (not a
    # fresh call), False for a fresh call; None for non-LLM pools (mock /
    # fallback / CellForge) that have no cache.
    cache_hit: bool | None = None
    # A2-6 (Architect steps only; None elsewhere): the backbone the Architect
    # STATED (gates H3; None when it stated none, e.g. a fallback step) and the
    # backbone that EXECUTED (``backbone_used``, the spec name) after the
    # Validator's delta / any outer override.
    backbone_stated: str | None = None
    backbone_used: str | None = None
    # A2-2 (Validator steps only; None elsewhere): the round's verdict and the
    # threshold it was judged against. Recorded; they never stop the run.
    validator_accepted: bool | None = None
    validator_threshold_msd: float | None = None


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
    # mode, and the learned-parameter count. Defaults keep hand-built runs
    # (tests, stubs) valid.
    hvg_n_per_round: tuple[int, ...] = ()
    hvg_n_forced_per_round: tuple[int, ...] = ()
    hvg_mode: str | None = None
    # QG C15: ``n_params`` is the LAST round's count (None if that round's fit
    # failed) and ``n_params_per_round`` pairs each round's backbone with its
    # own count, so no count is ever filed under another round's backbone.
    n_params: int | None = None
    n_params_per_round: tuple[tuple[str, int | None], ...] = ()
    # QG C4: error-record fields of the first TRANSIENT trainer failure in the
    # run (``error``, ``error_type``, ``error_class``, ``traceback``), or None.
    # ``lifecycle_record`` flattens them into the JSONL record so the analyser
    # counts the run as an error record.
    error_fields: dict[str, Any] | None = None
    # A2-2: every round's MSD (``final_msd_topk`` is the last round's).
    msd_per_round: tuple[float, ...] = ()
    # A2-3: per round, the resolved value of each agent-controlled field, which
    # tier supplied it, and whether an executor actually APPLIED it (QG-2):
    # {"values": {...}, "sources": {field: "validator" | "architect" |
    # "datacurator" | "trainer" | "default"}, "applied": {field: bool},
    # "not_applied_reason": {field: str}}. ``qc_mito_max`` is resolved and
    # recorded but applied=False: no mito cell filter exists in the lifecycle.
    applied_config_per_round: tuple[dict[str, Any], ...] = ()
    # A2-5: the task's evaluation genes (full-axis column indices, rank order),
    # shared with the trainer path; the Validator's MSD is over exactly these.
    eval_gene_idx: tuple[int, ...] = ()
    n_eval_genes: int = 0
