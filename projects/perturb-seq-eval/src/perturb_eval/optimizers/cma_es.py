"""Minimal (1+λ)-ES on the continuous relaxation of Φ.

This is a stripped-down evolutionary strategy sufficient for the 5-dim
config embedding used in perturb-eval. It keeps a Gaussian search
distribution (mean ``m`` and scalar step size ``sigma``), samples ``popsize``
offspring, and uses the one-fifth-success rule (Rechenberg 1973) to adapt
``sigma`` from observed objective values.

Full CMA-ES with rank-μ covariance updates is available via the ``cma``
package (declared in the research group of pyproject.toml); we use this
dependency-free version by default so the core test suite stays numpy-only.
See docs/SUPPLEMENT_DESIGN.md §2.4.
"""

from __future__ import annotations

import numpy as np

from perturb_eval.optimizers.base import Observation, config_to_vec, nearest_config
from perturb_eval.types import Config


class OnePlusLambdaES:
    """Numpy-only (1+λ)-ES on the continuous relaxation of Φ.

    Renamed from ``CMAESOptimizer`` (mc7 in docs/REVIEWER_CRITIQUE.md):
    reviewers from the evolutionary-computation community correctly
    pointed out that a Rechenberg one-fifth-success (1+λ) strategy is
    not CMA-ES (which includes rank-μ covariance adaptation). The class
    name now reflects what the code actually implements. The original
    ``CMAESOptimizer`` alias is retained for backwards compatibility
    with cached artifacts.
    """

    name: str = "one_plus_lambda_es"

    def __init__(
        self,
        config_space: tuple[Config, ...],
        seed: int = 0,
        sigma0: float = 0.3,
        popsize: int = 4,
    ) -> None:
        self._space = config_space
        self._rng = np.random.default_rng(seed)
        self._sigma = sigma0
        self._popsize = popsize
        # Seed mean at the centroid of the embedded space.
        embeddings = np.stack([config_to_vec(c) for c in config_space], axis=0)
        self._mean = embeddings.mean(axis=0)
        self._dim = self._mean.size
        self._last_batch: list[np.ndarray] = []

    def suggest(self, context: np.ndarray, observed: list[Observation]) -> Config:  # noqa: ARG002
        # If we have observations from the previous batch, update the mean + sigma
        # (one-fifth-success rule).
        if len(observed) >= self._popsize:
            recent = observed[-self._popsize:]
            ys = np.array([o.objective for o in recent])
            prev = ys[-1]
            success_rate = float(np.mean(ys[:-1] > prev))  # fraction worse than last
            if success_rate > 0.2:
                self._sigma *= 1.1
            else:
                self._sigma *= 0.9
            self._sigma = float(np.clip(self._sigma, 1e-3, 2.0))
            # Move mean toward the best of the recent batch.
            best = recent[int(np.argmin(ys))]
            self._mean = 0.5 * self._mean + 0.5 * config_to_vec(best.config)

        # Sample one offspring and project onto Φ.
        sample = self._mean + self._sigma * self._rng.standard_normal(self._dim)
        return nearest_config(sample, self._space)


# Backwards-compatible alias. Old code that constructs ``CMAESOptimizer`` keeps
# working; registry dispatch remains on the canonical name ``one_plus_lambda_es``.
CMAESOptimizer = OnePlusLambdaES
