"""Execute the Trainer agent's recipe on curated data + chosen backbone."""

from __future__ import annotations

import time
from typing import Any

import numpy as np

from perturb_eval.backbones import BackboneTrainConfig


def execute_trainer(
    *,
    backbone,
    X: np.ndarray,
    labels: np.ndarray,
    control_mask: np.ndarray,
    target_gene_idx: dict[str, int],
    trainer_proposal: dict[str, Any],
) -> dict:
    """Translate the Trainer proposal into ``BackboneTrainConfig`` and fit."""
    cfg = BackboneTrainConfig(
        top_k_genes=int(trainer_proposal.get("top_k_genes", 20)),
        seed=int(trainer_proposal.get("seed", 2026)),
        max_iter=int(trainer_proposal.get("epochs", 100)),
        learning_rate=float(trainer_proposal.get("lr", 1e-2)),
        ridge_lambda=float(trainer_proposal.get("ridge_lambda", 1.0)),
    )
    t0 = time.perf_counter()
    try:
        backbone.fit(X, labels.tolist(), control_mask, target_gene_idx, cfg)
        succeeded = True
        err_msg = ""
    except Exception as e:  # noqa: BLE001
        succeeded = False
        err_msg = f"{type(e).__name__}: {e}"
    return {
        "succeeded": succeeded,
        "error": err_msg,
        "n_train_perts": len(target_gene_idx),
        "wall_time_sec": time.perf_counter() - t0,
        "applied_config": {
            "lr": cfg.learning_rate,
            "max_iter": cfg.max_iter,
            "ridge_lambda": cfg.ridge_lambda,
        },
    }
