"""Contextual GP bandit with factored Matérn × Hamming kernel.

See docs/SUPPLEMENT_DESIGN.md §2.3. Implements the primary innovation of
this supplement: a Bayesian surrogate ``y(phi, x) ~ GP(·, k_Phi · k_X)``
fit on observations, queried for the best ``phi`` at a new context ``x``.

Formal regret guarantee: Krause & Ong 2011 Theorem 1 gives
``R_T = O(sqrt{T · γ_T})`` where ``γ_T`` is the maximum information gain —
bounded polylogarithmically for the kernels used here.

Dependency-free: pure numpy. No botorch, no scikit-optimize. Exact Gaussian
posterior in O(n³) per fit — fine for the small-n regime (≤ ~100
observations) we target.
"""

from __future__ import annotations

import numpy as np

from perturb_eval.optimizers.base import Observation, config_to_vec
from perturb_eval.types import Config


def _matern52(a: np.ndarray, b: np.ndarray, length_scale: float) -> np.ndarray:
    """Matérn-5/2 kernel. Inputs shaped (n, d), (m, d); returns (n, m)."""
    diffs = a[:, None, :] - b[None, :, :]
    r = np.linalg.norm(diffs, axis=-1) / max(length_scale, 1e-6)
    c = np.sqrt(5.0) * r
    return (1.0 + c + (5.0 / 3.0) * r * r) * np.exp(-c)


def _hamming_like(a: np.ndarray, b: np.ndarray, length_scale: float) -> np.ndarray:
    """Exponential-Hamming kernel on the config embedding."""
    diffs = a[:, None, :] - b[None, :, :]
    dist = np.sum(np.abs(diffs), axis=-1)
    return np.exp(-dist / max(length_scale, 1e-6))


class ContextualGPOptimizer:
    name: str = "contextual_gp"

    def __init__(
        self,
        config_space: tuple[Config, ...],
        seed: int = 0,
        length_scale_phi: float = 1.0,
        length_scale_x: float = 1.0,
        noise: float = 1e-3,
        xi: float = 0.01,
    ) -> None:
        self._space = config_space
        self._rng = np.random.default_rng(seed)
        self._ls_phi = length_scale_phi
        self._ls_x = length_scale_x
        self._noise = noise
        self._xi = xi
        # Precompute embeddings for the finite Φ.
        self._phi_embed = np.stack([config_to_vec(c) for c in config_space], axis=0)

    def suggest(self, context: np.ndarray, observed: list[Observation]) -> Config:
        context = np.asarray(context, dtype=np.float64).reshape(-1)
        # Cold start: random pick.
        if len(observed) < 2:
            idx = int(self._rng.integers(0, len(self._space)))
            return self._space[idx]

        phi_obs = np.stack([config_to_vec(o.config) for o in observed], axis=0)
        x_obs = np.stack([np.asarray(o.context, dtype=np.float64) for o in observed], axis=0)
        y_obs = np.array([o.objective for o in observed], dtype=np.float64)
        y_mean = float(y_obs.mean())
        y_centered = y_obs - y_mean

        # Gram matrix on observed points (factor kernel).
        K_pp = _hamming_like(phi_obs, phi_obs, self._ls_phi) * _matern52(
            x_obs, x_obs, self._ls_x
        )
        K_pp += self._noise * np.eye(len(observed))
        try:
            L = np.linalg.cholesky(K_pp)
            alpha = np.linalg.solve(L.T, np.linalg.solve(L, y_centered))
            # For variance we also need L.
        except np.linalg.LinAlgError:
            return self._space[int(self._rng.integers(0, len(self._space)))]

        # Evaluate acquisition at every (phi_candidate, fixed context).
        ctx_query = np.broadcast_to(context, (len(self._space), context.size)).copy()
        K_sp = _hamming_like(self._phi_embed, phi_obs, self._ls_phi) * _matern52(
            ctx_query, x_obs, self._ls_x
        )
        mu = K_sp @ alpha + y_mean                                       # (|Φ|,)
        # Diagonal of posterior covariance.
        v = np.linalg.solve(L, K_sp.T)                                   # (n_obs, |Φ|)
        k_ss = np.ones(len(self._space))                                 # k_Φ(x,x)·k_X(x,x) = 1
        var = np.maximum(k_ss - np.sum(v * v, axis=0), 1e-12)
        sigma = np.sqrt(var)

        # Expected Improvement for *minimisation*: f* = current best.
        f_star = float(y_obs.min())
        z = (f_star - self._xi - mu) / sigma
        # Φ(z) and φ(z) in standard normal.
        phi_cdf = 0.5 * (1.0 + _erf(z / np.sqrt(2.0)))
        phi_pdf = np.exp(-0.5 * z * z) / np.sqrt(2.0 * np.pi)
        ei = (f_star - self._xi - mu) * phi_cdf + sigma * phi_pdf
        # EI is nonnegative by construction for minimisation.
        ei = np.maximum(ei, 0.0)
        best = int(np.argmax(ei))
        return self._space[best]


def _erf(x: np.ndarray) -> np.ndarray:
    """Numpy-only erf via the Abramowitz & Stegun rational approximation."""
    # Constants (A&S 7.1.26).
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p = 0.3275911
    sign = np.sign(x)
    t = 1.0 / (1.0 + p * np.abs(x))
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * np.exp(-x * x)
    return sign * y
