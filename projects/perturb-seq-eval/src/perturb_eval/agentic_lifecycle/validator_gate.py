"""Validator agent step: score a trained backbone + gate on MSD threshold."""

from __future__ import annotations

import numpy as np

from perturb_eval.agentic_lifecycle.types import ExecutedValidation
from perturb_eval.backbones import mean_squared_deviation


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
) -> ExecutedValidation:
    """Compute MSD-on-top-K-DEGs and accept/reject against the threshold."""
    mask_p = labels == held_out
    mask_c = control_mask
    if not mask_p.any() or not mask_c.any():
        return ExecutedValidation(
            msd_topk=float("inf"),
            biofm_agreement=0.0,
            deg_overlap_at_k=0.0,
            accepted=False,
            rationale="held-out perturbation has no cells",
        )
    pred = backbone.predict_logfc(held_out, held_out_target_idx, n_genes=X.shape[1])
    truth = np.mean(X[mask_p], axis=0) - np.mean(X[mask_c], axis=0)
    top_k = np.argsort(-np.abs(truth))[:20]
    msd = mean_squared_deviation(pred, truth, top_k)
    deg_overlap = float(np.mean(np.sign(pred[top_k]) == np.sign(truth[top_k])))
    accepted = bool(msd <= threshold_msd)
    rationale = (
        f"MSD@20 = {msd:.4f}, DEG-sign agreement = {deg_overlap:.2f}, "
        f"Geneformer cosine = {biofm_agreement:.2f}. "
        + ("Accepted." if accepted else f"Rejected: MSD exceeds threshold {threshold_msd}.")
    )
    return ExecutedValidation(
        msd_topk=float(msd),
        biofm_agreement=biofm_agreement,
        deg_overlap_at_k=deg_overlap,
        accepted=accepted,
        rationale=rationale,
    )
