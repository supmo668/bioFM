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


def backbones_of(space: tuple[Config, ...]) -> tuple[str, ...]:
    """Sorted unique backbone names of a config space: the one-hot vocabulary."""
    return tuple(sorted({c.backbone for c in space}))


def config_to_vec(phi: Config, backbones: tuple[str, ...]) -> np.ndarray:
    """Continuous relaxation of a Config: n_agents and n_rounds min-max
    scaled, backbone one-hot (over ``backbones``) concatenated.

    ``backbones`` is the vocabulary derived by the caller from its config
    space via :func:`backbones_of`. A backbone outside it raises
    ``ValueError`` -- there is no silent default slot (T18 / A5: the old
    hard-coded ``.get(backbone, 0)`` collapsed every real backbone onto
    one index).

    This is the embedding every optimizer uses internally so that (a) CMA-ES
    can treat Φ as ℝⁿ and (b) the contextual GP has a well-defined distance
    on discrete configs.
    """
    if phi.backbone not in backbones:
        raise ValueError(
            f"unknown backbone {phi.backbone!r}; expected one of {backbones!r}"
        )
    vec = np.zeros(2 + len(backbones), dtype=np.float64)
    vec[0] = phi.n_agents / 5.0
    vec[1] = phi.n_rounds / 3.0
    vec[2 + backbones.index(phi.backbone)] = 1.0
    return vec


def nearest_config(
    v: np.ndarray, space: tuple[Config, ...], backbones: tuple[str, ...]
) -> Config:
    """Project a continuous point back onto the finite configuration space."""
    candidates = np.stack([config_to_vec(c, backbones) for c in space], axis=0)
    dists = np.linalg.norm(candidates - v, axis=1)
    return space[int(np.argmin(dists))]


class Optimizer(Protocol):
    """Protocol every optimizer must satisfy."""

    name: str

    def suggest(self, context: np.ndarray, observed: list[Observation]) -> Config: ...
