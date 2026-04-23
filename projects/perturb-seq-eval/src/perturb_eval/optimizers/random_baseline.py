"""Uniform random optimizer — the floor every real optimizer must beat."""

from __future__ import annotations

import numpy as np

from perturb_eval.optimizers.base import Observation
from perturb_eval.types import Config


class RandomOptimizer:
    name: str = "random"

    def __init__(self, config_space: tuple[Config, ...], seed: int = 0) -> None:
        self._space = config_space
        self._rng = np.random.default_rng(seed)

    def suggest(self, context: np.ndarray, observed: list[Observation]) -> Config:  # noqa: ARG002
        idx = int(self._rng.integers(0, len(self._space)))
        return self._space[idx]
