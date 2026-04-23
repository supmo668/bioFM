"""Shared types and helpers for the optimizer stack.

See docs/SUPPLEMENT_DESIGN.md §2. Every optimizer satisfies the
:class:`Optimizer` Protocol and is dispatched by :func:`build_optimizer`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

from perturb_eval.types import Config


@dataclass(frozen=True)
class Observation:
    """One (phi, context, objective) triple from an evaluator run."""

    config: Config
    context: np.ndarray          # 4-d probe signature x
    objective: float             # lower = better (MSD)


def config_to_vec(phi: Config) -> np.ndarray:
    """Continuous relaxation of a Config: n_agents and n_rounds min-max
    scaled, backbone one-hot concatenated.

    This is the embedding every optimizer uses internally so that (a) CMA-ES
    can treat Φ as ℝⁿ and (b) the contextual GP has a well-defined distance
    on discrete configs.
    """
    backbone_index = {"scGPT": 0, "scPRINT-2": 1, "scFoundation": 2}.get(phi.backbone, 0)
    n_backbones = 3
    vec = np.zeros(2 + n_backbones, dtype=np.float64)
    vec[0] = phi.n_agents / 5.0
    vec[1] = phi.n_rounds / 3.0
    vec[2 + backbone_index] = 1.0
    return vec


def nearest_config(v: np.ndarray, space: tuple[Config, ...]) -> Config:
    """Project a continuous point back onto the finite configuration space."""
    candidates = np.stack([config_to_vec(c) for c in space], axis=0)
    dists = np.linalg.norm(candidates - v, axis=1)
    return space[int(np.argmin(dists))]


class Optimizer(Protocol):
    """Protocol every optimizer must satisfy."""

    name: str

    def suggest(self, context: np.ndarray, observed: list[Observation]) -> Config: ...
