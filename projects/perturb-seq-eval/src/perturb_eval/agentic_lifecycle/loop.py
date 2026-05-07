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
from dataclasses import dataclass
from typing import Protocol

import numpy as np

from perturb_eval.agentic_lifecycle.architect_dispatch import resolve_architect_config
from perturb_eval.backbones import build_backbone
from perturb_eval.agentic_lifecycle.data_curator_exec import execute_data_curator
from perturb_eval.agentic_lifecycle.literature_exec import extract_expected_genes
from perturb_eval.agentic_lifecycle.trainer_exec import execute_trainer
from perturb_eval.agentic_lifecycle.types import LifecycleRun, LifecycleStep
from perturb_eval.agentic_lifecycle.validator_gate import score_and_gate


class AgentPool(Protocol):
    """Produces structured proposals per role, with optional refinement context."""

    def propose(
        self,
        role: str,
        round_index: int,
        task_id: str,
        context: dict,
    ) -> dict: ...


@dataclass
class MockAgentPool:
    """Deterministic offline pool used in unit tests."""

    seed: int = 0

    def propose(
        self,
        role: str,
        round_index: int,
        task_id: str,
        context: dict,
    ) -> dict:
        rng = np.random.default_rng(self.seed + round_index * 11 + (abs(hash(role)) % 97))
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


def run_agentic_lifecycle(
    *,
    task_id: str,
    X: np.ndarray,
    labels: np.ndarray,
    control_mask: np.ndarray,
    target_gene_idx: dict[str, int],
    held_out: str,
    agent_pool: AgentPool,
    max_rounds: int = 2,
    backbone_override: str | None = None,
    validator_threshold_override: float | None = None,
) -> LifecycleRun:
    """Run the end-to-end agentic lifecycle for one held-out perturbation.

    Each round runs all five agents in sequence (DataCurator → Literature →
    Architect → Trainer → Validator), executes every proposal, and records
    a :class:`LifecycleStep`. The loop terminates early if the Validator
    accepts the trained model.
    """
    steps: list[LifecycleStep] = []
    context: dict = {}
    final_msd = float("inf")
    final_agreement = 0.0
    backbone_used = "linear"
    r = 0

    train_mask = labels != held_out
    train_targets = {p: i for p, i in target_gene_idx.items() if p != held_out}

    for r in range(max_rounds):
        dc = agent_pool.propose("DataCurator", r, task_id, context)
        lit = agent_pool.propose("Literature", r, task_id, context)
        arch = agent_pool.propose("Architect", r, task_id, context)
        trn = agent_pool.propose("Trainer", r, task_id, context)
        val = agent_pool.propose("Validator", r, task_id, context)

        t0 = time.perf_counter()
        curated = execute_data_curator(
            X=X[train_mask],
            labels=labels[train_mask],
            proposal=dc["content"],
        )
        # Guarantee that every target-gene index survives the HVG filter —
        # otherwise the Trainer's target_gene_idx table collapses to empty
        # and the whole round fails. This is a safety net on top of the
        # DataCurator's proposal (NOT a replacement): we keep its HVG set
        # and only *add* the target-gene indices that were dropped.
        top_idx_set = {int(i) for i in curated["top_gene_indices"].tolist()}
        missing_targets = [
            int(i) for i in target_gene_idx.values() if int(i) not in top_idx_set
        ]
        if missing_targets:
            augmented = np.concatenate(
                [curated["top_gene_indices"], np.asarray(missing_targets, dtype=np.int64)]
            )
            curated = {
                "X": X[train_mask][:, augmented],
                "labels": labels[train_mask],
                "top_gene_indices": augmented,
                "execution_meta": {
                    **curated["execution_meta"],
                    "added_target_genes": len(missing_targets),
                },
            }
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
        # Remap the target-gene indices through the curated HVG index map.
        # Skip perturbations whose target gene was discarded by the DataCurator
        # (n_top_hvg may be much smaller than the original vocab).
        top_idx_arr = np.asarray(curated["top_gene_indices"])
        old_to_new = {int(old): new for new, old in enumerate(top_idx_arr.tolist())}
        train_targets_curated = {
            p: old_to_new[i] for p, i in train_targets.items() if int(i) in old_to_new
        }
        tinfo = execute_trainer(
            backbone=backbone,
            X=curated["X"],
            labels=curated["labels"],
            control_mask=control_mask[train_mask],
            target_gene_idx=train_targets_curated,
            trainer_proposal=trn["content"],
        )

        round_wall = time.perf_counter() - t0
        for role, agent_out in (
            ("DataCurator", dc),
            ("Literature", lit),
            ("Architect", arch),
            ("Trainer", trn),
            ("Validator", val),
        ):
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
                )
            )

        # Validator gate on the full dataset (held-out evaluation). We
        # slice X/labels/control_mask to the HVG subspace the Trainer saw,
        # but we keep *all* cells (including held-out) so observed log-FC
        # can be computed against real held-out counts.
        top_indices = curated["top_gene_indices"]
        X_hvg = X[:, top_indices]
        if held_out in target_gene_idx:
            real_idx = target_gene_idx[held_out]
            hits = np.where(top_indices == real_idx)[0]
            remapped = int(hits[0]) if hits.size else 0
        else:
            remapped = 0
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
    )
