"""E2 — offline grid fill over (phi, task, seed).

Every backbone in Φ is trained on a leave-one-perturbation-out split of
real Adamson 2016 / Norman 2019 cells (see ``e2_adamson.py`` for the
concrete trainer entry-point) and the held-out MSD is recorded. Results
cache to Parquet (or JSONL for environments without pyarrow).

v0.5.0 removed the legacy ``_build_synthetic_dataset`` helper and the
``train_grid_cell_synthetic`` runner — the paper's headline forbids any
synthetic Perturb-seq generation. The real-data trainer is
``perturb_eval.experiments.e2_adamson.train_grid_cell_adamson``.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from itertools import product
from pathlib import Path
from typing import Iterable

from perturb_eval.backbones import BackboneTrainConfig
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


def write_results_jsonl(results: Iterable[GridCellResult], path: str | Path) -> None:
    """Portable write path when pyarrow isn't available."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for r in results:
            f.write(json.dumps(asdict(r)))
            f.write("\n")
