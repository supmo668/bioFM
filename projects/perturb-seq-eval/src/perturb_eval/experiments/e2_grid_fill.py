"""E2 — offline grid fill over (phi, task, seed).

Every backbone in Φ is trained on a leave-one-perturbation-out split of
the dataset and the held-out MSD is recorded. Results cache to Parquet
(or JSONL for environments without pyarrow) so the E3 optimizer
comparison runs on cached evaluations rather than re-training every time.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict
from itertools import product
from pathlib import Path
from typing import Iterable

import numpy as np

from perturb_eval.backbones import (
    BackboneTrainConfig,
    build_backbone,
    mean_squared_deviation,
)
from perturb_eval.experiments.common import GridCellResult
from perturb_eval.types import Config


def enumerate_grid(
    phis: Iterable[Config],
    tasks: Iterable[str],
    seeds: Iterable[int],
) -> list[tuple[Config, str, int]]:
    """Cartesian product of (phi, task, seed)."""
    return [(phi, task, seed) for phi, task, seed in product(phis, tasks, seeds)]


def phi_identifier(phi: Config) -> str:
    return f"a{phi.n_agents}_r{phi.n_rounds}_{phi.backbone}"


def _train_cfg_from_phi(phi: Config) -> BackboneTrainConfig:
    """More agents and rounds → larger effective training budget per cell."""
    return BackboneTrainConfig(
        top_k_genes=20,
        max_iter=20 + 20 * phi.n_rounds,
        learning_rate=1e-2,
        ridge_lambda=1.0,
    )


def _build_synthetic_dataset(
    task: str,
    seed: int,
    n_cells: int,
    n_genes: int,
    n_perts: int,
) -> dict:
    """Toy scRNA-ish dataset used by the synthetic grid-cell runner."""
    rng = np.random.default_rng(seed)
    perturbations = tuple(f"{task}_P{i}" for i in range(n_perts))
    target_gene_idx = {p: (i * max(1, n_genes // n_perts)) % n_genes for i, p in enumerate(perturbations)}
    n_ctrl = n_cells // 4
    base = rng.standard_normal((n_ctrl, n_genes)).astype(np.float64) * 0.3 + 2.0
    X = [base]
    labels = ["CTRL"] * n_ctrl
    per_pert = (n_cells - n_ctrl) // n_perts
    for p in perturbations:
        rows = rng.standard_normal((per_pert, n_genes)).astype(np.float64) * 0.3 + 2.0
        rows[:, target_gene_idx[p]] -= 2.0
        X.append(rows)
        labels.extend([p] * per_pert)
    Xarr = np.vstack(X)
    labels_arr = np.asarray(labels)
    return {
        "X": Xarr,
        "labels": labels_arr,
        "control_mask": labels_arr == "CTRL",
        "target_gene_idx": target_gene_idx,
        "perturbations": perturbations,
    }


def train_grid_cell_synthetic(
    phi: Config,
    task: str,
    seed: int,
    *,
    n_cells: int = 400,
    n_genes: int = 40,
    n_perts: int = 4,
) -> GridCellResult:
    """Train one (phi, task, seed) cell on a synthetic dataset. CPU-only."""
    ds = _build_synthetic_dataset(task, seed, n_cells, n_genes, n_perts)
    # Rotate the held-out perturbation by task name and seed for variety.
    held_idx = (abs(hash(task)) + seed) % n_perts
    held = ds["perturbations"][held_idx]
    train_mask = ds["labels"] != held
    t0 = time.perf_counter()
    backbone = build_backbone(phi.backbone if phi.backbone in {"linear", "mlp", "scgpt_small"} else "linear")
    train_targets = {p: idx for p, idx in ds["target_gene_idx"].items() if p != held}
    backbone.fit(
        ds["X"][train_mask],
        ds["labels"][train_mask].tolist(),
        ds["control_mask"][train_mask],
        train_targets,
        _train_cfg_from_phi(phi),
    )
    pred = backbone.predict_logfc(held, ds["target_gene_idx"][held], n_genes=n_genes)
    mask_p = ds["labels"] == held
    mask_c = ds["control_mask"]
    truth = np.mean(ds["X"][mask_p], axis=0) - np.mean(ds["X"][mask_c], axis=0)
    top_k = np.argsort(-np.abs(truth))[:20]
    msd = mean_squared_deviation(pred, truth, top_k)
    return GridCellResult(
        phi_id=phi_identifier(phi),
        task=task,
        seed=seed,
        msd_topk=msd,
        wall_time_sec=time.perf_counter() - t0,
        backbone_name=backbone.name,
    )


def write_results_jsonl(results: Iterable[GridCellResult], path: str | Path) -> None:
    """Portable write path when pyarrow isn't available."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for r in results:
            f.write(json.dumps(asdict(r)))
            f.write("\n")
