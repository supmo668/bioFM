"""Multi-round agentic lifecycle: propose → execute → critique → refine.

The loop consumes an :class:`AgentPool` that can produce a proposal per
agent role. In production the pool is :class:`CellForgeAgentPool`
(see ``cellforge_pool.py``); for unit tests we ship :class:`MockAgentPool`
so the loop is testable offline.

Refinement between rounds: the Validator's rationale + the previous
MSD are threaded into the next round's ``context`` so each agent can
adjust its proposal. The loop terminates early when the Validator
accepts (MSD ≤ threshold).

See docs/plans/2026-04-22-end-to-end-agentic-lifecycle.md Task 7.
"""

from __future__ import annotations

import time
import zlib
from dataclasses import dataclass
from typing import Protocol

import numpy as np

from perturb_eval.agentic_lifecycle.architect_dispatch import resolve_architect_config
from perturb_eval.backbones import build_backbone, count_fitted_params
from perturb_eval.data.hvg import HVG_MODE, all_target_columns, remap_targets
from perturb_eval.agentic_lifecycle.data_curator_exec import execute_data_curator
from perturb_eval.agentic_lifecycle.literature_exec import extract_expected_genes
from perturb_eval.agentic_lifecycle.trainer_exec import execute_trainer
from perturb_eval.agentic_lifecycle.types import STEP_SOURCES, LifecycleRun, LifecycleStep
from perturb_eval.agentic_lifecycle.validator_gate import score_and_gate


class AgentPool(Protocol):
    """Produces structured proposals per role, with optional refinement context.

    ``propose`` returns ``{"content", "rationale", "confidence", "model_id",
    "source"}`` plus an optional ``cache_hit`` (bool; LLM pools only).
    ``source`` is REQUIRED and must be one of
    :data:`~perturb_eval.agentic_lifecycle.types.STEP_SOURCES`; the loop
    raises rather than defaulting it, so no pool can masquerade as "llm".
    ``dataset`` names the dataset the task is held out from; an LLM pool puts
    it in its cache key (QG C6: the same gene symbol is a task in both
    Adamson and Norman).
    """

    def propose(
        self,
        role: str,
        round_index: int,
        task_id: str,
        context: dict,
        *,
        seed: int,
        dataset: str,
    ) -> dict: ...


@dataclass
class MockAgentPool:
    """Deterministic offline pool used in unit tests (``source="mock"``)."""

    seed: int = 0

    def propose(
        self,
        role: str,
        round_index: int,
        task_id: str,
        context: dict,
        *,
        seed: int,  # noqa: ARG002 — mock uses self.seed
        dataset: str,  # noqa: ARG002 — mock has no cache
    ) -> dict:
        out = self._propose(role, round_index, task_id)
        return {**out, "model_id": None, "source": "mock"}

    def _propose(self, role: str, round_index: int, task_id: str) -> dict:
        # zlib.crc32, not hash(): str hashes are salted per process
        # (PYTHONHASHSEED), which made the mock's draws differ run to run (QG C27).
        rng = np.random.default_rng(
            self.seed + round_index * 11 + (zlib.crc32(role.encode()) % 97)
        )
        if role == "DataCurator":
            return {
                "content": {"n_top_hvg": 40, "pct_mito_max": 12.0},
                "rationale": f"tight HVG for {task_id}",
                "confidence": float(rng.uniform(0.6, 0.9)),
            }
        if role == "Literature":
            return {
                "content": {
                    "pathways": ["UPR"],
                    "expected_up": ["A"],
                    "expected_down": [],
                },
                "rationale": "stub literature",
                "confidence": 0.5,
            }
        if role == "Architect":
            return {
                "content": {"backbone": "linear"},
                "rationale": "stub architect",
                "confidence": 0.6,
            }
        if role == "Trainer":
            return {
                "content": {"lr": 1e-2, "epochs": 50, "ridge_lambda": 1.0},
                "rationale": "stub trainer",
                "confidence": 0.55,
            }
        if role == "Validator":
            return {
                "content": {"threshold_msd": 0.5},
                "rationale": "stub validator",
                "confidence": 0.5,
            }
        raise ValueError(f"unknown role {role}")


_ROLES = ("DataCurator", "Literature", "Architect", "Trainer", "Validator")

Target = int | tuple[int, ...]


def _as_target_tuple(t: Target) -> tuple[int, ...]:
    """D1: a singleton target is a 1-tuple; normalise ``int`` → ``(int,)``."""
    return tuple(int(i) for i in t) if isinstance(t, (tuple, list)) else (int(t),)


def _to_backbone_target(t: tuple[int, ...]) -> Target:
    """Hand singletons to the backbone as a plain ``int`` so a 1-tuple takes the
    exact same code path as today's int targets; multi-target stays a tuple."""
    return t[0] if len(t) == 1 else t


def _remap_held_out_target(
    target_gene_idx: dict[str, Target],
    *,
    held_out: str,
    top_indices: np.ndarray,
) -> tuple[int, ...]:
    """Map the held-out perturbation's target gene(s) into HVG-subset columns.

    Every target gene is remapped element-wise. Raises ``ValueError`` if the
    held-out label has no target entry, or if ANY of its target genes is not
    in ``top_indices`` — there is no index-0 fallback (A4).
    """
    if held_out not in target_gene_idx:
        raise ValueError(
            f"held-out perturbation {held_out!r} has no entry in target_gene_idx"
        )
    old_to_new: dict[int, int] = {}
    for new, old in enumerate(np.asarray(top_indices).tolist()):
        old_to_new.setdefault(int(old), new)  # first hit, as np.where(...)[0][0]
    remapped: list[int] = []
    for gene in _as_target_tuple(target_gene_idx[held_out]):
        if gene not in old_to_new:
            raise ValueError(
                f"held-out perturbation {held_out!r}: target gene index {gene} "
                f"is not in the HVG subset used for scoring"
            )
        remapped.append(old_to_new[gene])
    return tuple(remapped)


def _step_provenance(role: str, agent_out: dict) -> tuple[str | None, str, bool | None]:
    """``(model_id, source, cache_hit)`` from a pool's propose output — fail loud (D4)."""
    source = agent_out["source"]
    if source not in STEP_SOURCES:
        raise ValueError(
            f"{role}: pool returned source={source!r}; expected one of {STEP_SOURCES}"
        )
    model_id = agent_out.get("model_id")
    if (source == "llm") != (model_id is not None):
        raise ValueError(
            f"{role}: source={source!r} with model_id={model_id!r} — an 'llm' "
            "step must name its serving model and only an 'llm' step may"
        )
    cache_hit = agent_out.get("cache_hit")
    if cache_hit is not None and not isinstance(cache_hit, bool):
        raise ValueError(f"{role}: cache_hit must be bool or None, got {cache_hit!r}")
    return model_id, source, cache_hit


def run_agentic_lifecycle(
    *,
    task_id: str,
    X: np.ndarray,
    labels: np.ndarray,
    control_mask: np.ndarray,
    target_gene_idx: dict[str, int | tuple[int, ...]],
    held_out: str,
    agent_pool: AgentPool,
    seed: int,
    dataset: str,
    max_rounds: int = 2,
    backbone_override: str | None = None,
    validator_threshold_override: float | None = None,
) -> LifecycleRun:
    """Run the end-to-end agentic lifecycle for one held-out perturbation.

    Each round runs all five agents in sequence (DataCurator → Literature →
    Architect → Trainer → Validator), executes every proposal, and records
    a :class:`LifecycleStep`. The loop terminates early if the Validator
    accepts the trained model.

    ``target_gene_idx`` values may be an ``int`` or a ``tuple[int, ...]``
    (D1 multi-target contract; a 1-tuple behaves exactly like the int).
    A ``held_out`` label absent from ``target_gene_idx`` raises ``ValueError``.

    ``seed`` is required: it is passed to every ``agent_pool.propose`` call
    (and so into the LLM cache key) and to ``execute_trainer`` (and so into
    ``BackboneTrainConfig.seed``). ``dataset`` (the dataset ``held_out`` is
    drawn from) is required for the same reason (QG C6).

    Trainer failures (QG C4): a programming / unclassified exception from the
    backbone fit propagates; a TRANSIENT one fails that round's Trainer step
    and its error fields are carried on ``LifecycleRun.error_fields``.
    """
    steps: list[LifecycleStep] = []
    context: dict = {}
    final_msd = float("inf")
    final_agreement = 0.0
    backbone_used = "linear"
    r = 0

    if held_out not in target_gene_idx:
        raise ValueError(
            f"held-out perturbation {held_out!r} has no entry in target_gene_idx"
        )
    targets = {p: _as_target_tuple(t) for p, t in target_gene_idx.items()}
    train_mask = labels != held_out
    train_targets = {p: t for p, t in targets.items() if p != held_out}
    target_cols = all_target_columns(targets)
    hvg_n_per_round: list[int] = []
    hvg_n_forced_per_round: list[int] = []
    n_params: int | None = None
    n_params_per_round: list[tuple[str, int | None]] = []
    error_fields: dict | None = None

    for r in range(max_rounds):
        dc = agent_pool.propose("DataCurator", r, task_id, context, seed=seed,
                                  dataset=dataset)
        lit = agent_pool.propose("Literature", r, task_id, context, seed=seed,
                                  dataset=dataset)
        arch = agent_pool.propose("Architect", r, task_id, context, seed=seed,
                                  dataset=dataset)
        trn = agent_pool.propose("Trainer", r, task_id, context, seed=seed,
                                  dataset=dataset)
        val = agent_pool.propose("Validator", r, task_id, context, seed=seed,
                                  dataset=dataset)

        t0 = time.perf_counter()
        # T8b: HVG ranked on training cells only; every target column (training
        # + held-out) is forced in — its identity comes from the label, not
        # from held-out expression — so no target can fall outside the cut.
        curated = execute_data_curator(
            X=X,
            labels=labels,
            proposal=dc["content"],
            train_mask=train_mask,
            force_include=target_cols,
        )
        hvg_n_per_round.append(int(curated["execution_meta"]["hvg_n"]))
        hvg_n_forced_per_round.append(int(curated["execution_meta"]["hvg_n_forced"]))
        literature = extract_expected_genes(lit["content"])
        # The outer optimizer may override the Architect's backbone choice
        # — this is what lets the contextual-BO search over the backbone
        # axis while the Architect still contributes the hyperparameter
        # rationale (same pattern as Archon's inference-time HPO).
        arch_content = dict(arch["content"])
        if backbone_override is not None:
            arch_content["backbone"] = backbone_override
        # v0.5.0: merge the previous round's validator critique delta so
        # the Architect can target-fix on rejection.
        critique_delta = context.get("validator_critique_delta")
        arch_cfg = resolve_architect_config(arch_content, critique_delta=critique_delta)
        backbone = build_backbone(arch_cfg["backbone"])
        backbone_used = arch_cfg["backbone"]
        # Remap the target-gene indices through the curated HVG index map
        # (all targets were forced in, so none is dropped).
        train_targets_curated = {
            p: _to_backbone_target(t)
            for p, t in remap_targets(train_targets, curated["top_gene_indices"]).items()
        }
        tinfo = execute_trainer(
            backbone=backbone,
            X=curated["X"],
            labels=curated["labels"],
            control_mask=control_mask[train_mask],
            target_gene_idx=train_targets_curated,
            trainer_proposal=trn["content"],
            seed=seed,
        )
        # QG C15: reset every round — a failed fit never inherits the count of
        # an earlier round's (possibly different) backbone.
        n_params = count_fitted_params(backbone) if tinfo["succeeded"] else None
        n_params_per_round.append((backbone_used, n_params))
        if tinfo.get("error_fields") and error_fields is None:
            error_fields = dict(tinfo["error_fields"])

        round_wall = time.perf_counter() - t0
        for role, agent_out in (
            ("DataCurator", dc),
            ("Literature", lit),
            ("Architect", arch),
            ("Trainer", trn),
            ("Validator", val),
        ):
            model_id, source, cache_hit = _step_provenance(role, agent_out)
            steps.append(
                LifecycleStep(
                    round_index=r,
                    agent_name=role,
                    proposal_content=dict(agent_out["content"]),
                    rationale=str(agent_out.get("rationale", "")),
                    llm_confidence=float(agent_out["confidence"]),
                    execution_artifact_path=None,
                    wall_time_sec=round_wall,
                    succeeded=tinfo["succeeded"] if role == "Trainer" else True,
                    model_id=model_id,
                    source=source,
                    cache_hit=cache_hit,
                )
            )

        # Validator gate on the full dataset (held-out evaluation). We
        # slice X/labels/control_mask to the HVG subspace the Trainer saw,
        # but we keep *all* cells (including held-out) so observed log-FC
        # can be computed against real held-out counts.
        top_indices = curated["top_gene_indices"]
        # float64 view: the real-data loaders return a float32 full-vocab matrix.
        X_hvg = np.asarray(X[:, top_indices], dtype=np.float64)
        remapped = _to_backbone_target(
            _remap_held_out_target(targets, held_out=held_out, top_indices=top_indices)
        )
        threshold = (
            validator_threshold_override
            if validator_threshold_override is not None
            else float(val["content"].get("threshold_msd", 0.5))
        )
        # If the Trainer step failed, skip the Validator scoring (avoids
        # ``predict_logfc called before fit()`` when the backbone was never
        # fit). We still record the round so the rationale is preserved.
        if not tinfo["succeeded"]:
            from perturb_eval.agentic_lifecycle.types import ExecutedValidation
            report = ExecutedValidation(
                msd_topk=float("inf"), biofm_agreement=0.0,
                deg_overlap_at_k=0.0, accepted=False,
                rationale=f"Trainer failed: {tinfo.get('error', '')}",
            )
        else:
            report = score_and_gate(
                backbone=backbone,
                X=X_hvg,
                labels=labels,
                control_mask=control_mask,
                held_out=held_out,
                held_out_target_idx=remapped,
                threshold_msd=threshold,
            )
        final_msd = report.msd_topk
        final_agreement = report.biofm_agreement

        if report.accepted:
            break

        context = {
            "last_validator_rationale": report.rationale,
            "last_msd": report.msd_topk,
            "literature": literature,
            "validator_critique_delta": (
                dict(report.critique.suggested_next_config_delta)
                if report.critique is not None
                else {}
            ),
            "validator_failed_genes": (
                report.critique.which_genes_failed
                if report.critique is not None
                else ()
            ),
        }

    return LifecycleRun(
        task_id=task_id,
        steps=tuple(steps),
        final_msd_topk=float(final_msd),
        final_validator_agreement=float(final_agreement),
        n_rounds=r + 1,
        n_agents=len(_ROLES),
        backbone_used=backbone_used,
        hvg_n_per_round=tuple(hvg_n_per_round),
        hvg_n_forced_per_round=tuple(hvg_n_forced_per_round),
        hvg_mode=HVG_MODE,
        n_params=n_params,
        n_params_per_round=tuple(n_params_per_round),
        error_fields=error_fields,
    )
