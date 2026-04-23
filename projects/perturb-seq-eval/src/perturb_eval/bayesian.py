"""Bayesian recommender: probe signature → recommended Config under a budget.

Likelihood
----------
For each configuration φ ∈ Φ, we assume the probe signature x is drawn from a
Gaussian ``N(μ_φ, Σ_φ)`` whose parameters are learned on a calibration set. The
prior ``π(φ)`` is configurable (default: favour smaller configs).

The posterior ``P(φ | x) ∝ π(φ) · N(x; μ_φ, Σ_φ)`` is computed in log-space for
numerical stability. The MAP recommendation is

    φ̂(x) = argmax_{φ ∈ Φ, FLOPs(φ) ≤ B}  log π(φ) + log N(x; μ_φ, Σ_φ)

Why Gaussian?
-------------
With ≤ ~100 calibration tasks and 4-d signatures, a mean + diagonal covariance
is enough. When the calibration set grows we can swap in a full covariance or a
Gaussian mixture without changing the public API.
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass, field

import numpy as np

from perturb_eval.probe import ProbeSignature
from perturb_eval.types import DEFAULT_CONFIG_SPACE, Config


@dataclass(frozen=True)
class Recommendation:
    """What the recommender returns."""

    config: Config
    log_posterior: float
    log_likelihoods: dict[str, float]      # per-config log-likelihood, for audit
    ranked: tuple[Config, ...]             # config_space sorted by log posterior
    budget: float
    fit_on_n_tasks: int


@dataclass
class BayesianRecommender:
    """Gaussian-likelihood recommender with pluggable prior.

    Calibrate with ``fit(task_logs)``, then query with ``recommend(signature)``.
    """

    config_space: tuple[Config, ...] = DEFAULT_CONFIG_SPACE
    prior_scale: float = 3.0                # higher ⇒ stronger penalty on large configs
    default_likelihood_var: float = 0.05    # used before any calibration

    # Populated by fit():
    _means: dict[str, np.ndarray] = field(default_factory=dict)
    _vars: dict[str, np.ndarray] = field(default_factory=dict)
    _n_fit: int = 0

    # -------------------------------------------------------------------
    # Calibration
    # -------------------------------------------------------------------
    def fit(self, task_logs: Iterable[tuple[ProbeSignature, Config]]) -> "BayesianRecommender":
        """Fit μ_φ, σ²_φ from (probe_signature, observed_φ*) tuples.

        If a configuration receives < 2 samples, we back off to the global
        mean/variance so the posterior stays defined everywhere.
        """
        buckets: dict[str, list[np.ndarray]] = {_key(c): [] for c in self.config_space}
        for x, cfg in task_logs:
            key = _key(cfg)
            if key not in buckets:
                # Configs outside the declared space still contribute to the pool.
                buckets[key] = []
            buckets[key].append(np.array(x.as_vector(), dtype=np.float64))

        all_xs = [x for bucket in buckets.values() for x in bucket]
        if not all_xs:
            # No data: use sane uniform defaults so recommend() still works.
            dim = 4
            self._means = {_key(c): np.zeros(dim) for c in self.config_space}
            self._vars = {_key(c): np.full(dim, self.default_likelihood_var)
                          for c in self.config_space}
            self._n_fit = 0
            return self

        global_mean = np.mean(all_xs, axis=0)
        global_var = np.var(all_xs, axis=0, ddof=0)
        # Floor variance to avoid degenerate likelihoods.
        global_var = np.maximum(global_var, self.default_likelihood_var)

        self._means = {}
        self._vars = {}
        for cfg in self.config_space:
            k = _key(cfg)
            samples = buckets.get(k, [])
            if len(samples) >= 2:
                self._means[k] = np.mean(samples, axis=0)
                self._vars[k] = np.maximum(np.var(samples, axis=0, ddof=0),
                                            self.default_likelihood_var)
            else:
                self._means[k] = global_mean
                self._vars[k] = global_var
        self._n_fit = len(all_xs)
        return self

    # -------------------------------------------------------------------
    # Inference
    # -------------------------------------------------------------------
    def recommend(
        self,
        signature: ProbeSignature,
        *,
        budget: float = math.inf,
    ) -> Recommendation:
        """Return the MAP configuration under a compute budget."""
        if not self._means:
            # Unfit: degenerate to prior only. Pick smallest config under budget.
            self.fit([])
        x = np.array(signature.as_vector(), dtype=np.float64)

        log_posts: dict[str, float] = {}
        for cfg in self.config_space:
            k = _key(cfg)
            if cfg.flops_proxy() > budget:
                continue
            ll = _gaussian_log_lik(x, self._means[k], self._vars[k])
            lp = self._log_prior(cfg)
            log_posts[k] = ll + lp

        if not log_posts:
            raise ValueError("no configuration fits the requested budget")

        winner_key = max(log_posts, key=log_posts.__getitem__)
        ranked_keys = sorted(log_posts, key=log_posts.__getitem__, reverse=True)
        ranked = tuple(
            next(c for c in self.config_space if _key(c) == k) for k in ranked_keys
        )
        winner = next(c for c in self.config_space if _key(c) == winner_key)

        return Recommendation(
            config=winner,
            log_posterior=log_posts[winner_key],
            log_likelihoods=log_posts,
            ranked=ranked,
            budget=budget,
            fit_on_n_tasks=self._n_fit,
        )

    # -------------------------------------------------------------------
    # Prior
    # -------------------------------------------------------------------
    def _log_prior(self, cfg: Config) -> float:
        """Favour smaller configurations — exponential on FLOPs proxy."""
        return -cfg.flops_proxy() / self.prior_scale


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _key(cfg: Config) -> str:
    return f"{cfg.n_agents}|{cfg.n_rounds}|{cfg.backbone}"


def _gaussian_log_lik(x: np.ndarray, mean: np.ndarray, var: np.ndarray) -> float:
    """Log-likelihood under a diagonal-covariance Gaussian."""
    # -(1/2) Σ [ (x-μ)²/σ² + log(2π σ²) ]
    diff = x - mean
    return float(-0.5 * np.sum(diff * diff / var + np.log(2 * math.pi * var)))
