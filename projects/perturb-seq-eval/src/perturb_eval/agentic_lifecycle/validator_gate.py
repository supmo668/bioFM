"""Validator agent step: score a trained backbone, gate on MSD, emit a
structured critique the next round's Architect can consume.

See ``.claude/plans/v0.5.0-real-perturb-seq.md`` §Phase 2.3.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from perturb_eval.agentic_lifecycle.types import (
    ExecutedValidation,
    StructuredCritiqueDTO,
)
from perturb_eval.backbones import mean_squared_deviation

_BACKBONE_ROTATION = ("linear", "mlp", "scgpt_small")


def suggest_config_delta(
    *,
    accepted: bool,
    msd: float,
    threshold_msd: float,
    current_backbone: str,
    deg_sign_agreement: float,
) -> dict[str, Any]:
    """Heuristic: what should the Architect change next round?

    The rules encode a lightweight troubleshooting prior the paper can
    document:

    * Accepted → empty delta (no change suggested).
    * Low sign agreement (<0.5) → backbone class mismatch, rotate backbone.
    * Signs mostly right but magnitude off → shrink learning rate or
      raise ridge.
    * Catastrophic MSD (>10× threshold) → also lower epochs (overfit
      risk) and bump ridge.
    """
    if accepted:
        return {}

    delta: dict[str, Any] = {}
    if deg_sign_agreement < 0.5:
        idx = _BACKBONE_ROTATION.index(current_backbone) if current_backbone in _BACKBONE_ROTATION else 0
        delta["backbone"] = _BACKBONE_ROTATION[(idx + 1) % len(_BACKBONE_ROTATION)]
    else:
        delta["learning_rate"] = 1e-3
        if msd > 10.0 * threshold_msd:
            delta["ridge_lambda"] = 5.0
            delta["epochs"] = 20
    return delta


def score_and_gate(
    *,
    backbone,
    X: np.ndarray,
    labels: np.ndarray,
    control_mask: np.ndarray,
    held_out: str,
    held_out_target_idx: int,
    threshold_msd: float = 0.5,
    biofm_agreement: float = 0.5,
    gene_names: tuple[str, ...] | None = None,
) -> ExecutedValidation:
    """Compute MSD-on-top-K-DEGs, decide accept/reject, emit critique."""
    mask_p = labels == held_out
    mask_c = control_mask
    if not mask_p.any() or not mask_c.any():
        return ExecutedValidation(
            msd_topk=float("inf"),
            biofm_agreement=0.0,
            deg_overlap_at_k=0.0,
            accepted=False,
            rationale="held-out perturbation has no cells",
            critique=StructuredCritiqueDTO(
                accept_reason="held-out perturbation missing",
            ),
        )

    pred = backbone.predict_logfc(held_out, held_out_target_idx, n_genes=X.shape[1])
    truth = np.mean(X[mask_p], axis=0) - np.mean(X[mask_c], axis=0)
    top_k = np.argsort(-np.abs(truth))[:20]
    msd = float(mean_squared_deviation(pred, truth, top_k))
    deg_overlap = float(np.mean(np.sign(pred[top_k]) == np.sign(truth[top_k])))
    accepted = bool(msd <= threshold_msd)

    rationale = (
        f"MSD@20 = {msd:.4f}, DEG-sign agreement = {deg_overlap:.2f}, "
        f"Geneformer cosine = {biofm_agreement:.2f}. "
        + ("Accepted." if accepted else f"Rejected: MSD exceeds threshold {threshold_msd}.")
    )

    failed_genes: tuple[str, ...] = ()
    if not accepted:
        sign_mismatch = np.sign(pred[top_k]) != np.sign(truth[top_k])
        mismatch_idx = top_k[sign_mismatch]
        if gene_names is not None and len(gene_names) == X.shape[1]:
            failed_genes = tuple(
                str(gene_names[int(i)]) for i in mismatch_idx[:10]
            )
        else:
            failed_genes = tuple(f"gene_{int(i)}" for i in mismatch_idx[:10])

    delta = suggest_config_delta(
        accepted=accepted,
        msd=msd,
        threshold_msd=threshold_msd,
        current_backbone=getattr(backbone, "name", "linear"),
        deg_sign_agreement=deg_overlap,
    )

    critique = StructuredCritiqueDTO(
        which_genes_failed=failed_genes,
        suggested_next_config_delta=delta,
        accept_reason=("accepted" if accepted else f"MSD {msd:.3f} > {threshold_msd}"),
    )

    return ExecutedValidation(
        msd_topk=msd,
        biofm_agreement=biofm_agreement,
        deg_overlap_at_k=deg_overlap,
        accepted=accepted,
        rationale=rationale,
        critique=critique,
    )
