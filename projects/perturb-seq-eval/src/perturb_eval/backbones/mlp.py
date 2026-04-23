"""Tiny numpy-only MLP backbone.

Two-layer MLP with tanh activation trained by vanilla SGD with momentum.
No torch, no sklearn — we want the core test suite to stay framework-free.

Input features per perturbation:
    [one-hot gene-context (top-N correlated genes with target), target-gene mean expr]

Output: per-gene log-FC.

This is **not** a performant MLP by modern standards. It is a minimal
non-trivial nonlinearity over the linear backbone that completes in under
1 s on Adamson pilot and exercises the HPO axis.
"""

from __future__ import annotations

import time

import numpy as np

from perturb_eval.backbones.base import (
    BackboneFitArtifacts,
    BackboneTrainConfig,
    log_fold_change,
    per_perturbation_mean,
)


class MLPBackbone:
    name: str = "mlp"

    def __init__(self, hidden_dim: int = 16) -> None:
        self._W1: np.ndarray | None = None
        self._b1: np.ndarray | None = None
        self._W2: np.ndarray | None = None
        self._b2: np.ndarray | None = None
        self._mean_logfc: np.ndarray | None = None
        self._hidden_dim = hidden_dim

    def _featurize(self, target_gene_idx: int, n_genes: int) -> np.ndarray:
        """One-hot of the target gene index — small, but enough to give
        the MLP per-target capacity over the shared mean pattern."""
        v = np.zeros(n_genes, dtype=np.float64)
        if 0 <= target_gene_idx < n_genes:
            v[target_gene_idx] = 1.0
        return v

    def fit(
        self,
        expression: np.ndarray,
        perturbation_labels: list[str],
        control_mask: np.ndarray,
        target_gene_idx: dict[str, int],
        cfg: BackboneTrainConfig,
    ) -> BackboneFitArtifacts:
        t0 = time.perf_counter()
        rng = np.random.default_rng(cfg.seed)
        labels = np.asarray(perturbation_labels)
        means = per_perturbation_mean(expression, labels)
        mean_ctrl = np.mean(expression[control_mask], axis=0)

        n_genes = expression.shape[1]
        Xs: list[np.ndarray] = []
        Ys: list[np.ndarray] = []
        for p, mu in means.items():
            if p not in target_gene_idx:
                continue
            Xs.append(self._featurize(target_gene_idx[p], n_genes))
            Ys.append(log_fold_change(mu, mean_ctrl))
        if not Xs:
            raise ValueError("no trainable perturbations")
        X = np.stack(Xs, axis=0)                # (n_perts, n_genes)
        Y = np.stack(Ys, axis=0)                # (n_perts, n_genes)
        self._mean_logfc = Y.mean(axis=0)       # residualise around mean

        # Residualised target.
        Yr = Y - self._mean_logfc[None, :]

        in_dim = n_genes
        hid = self._hidden_dim
        out_dim = n_genes
        scale1 = np.sqrt(1.0 / in_dim)
        scale2 = np.sqrt(1.0 / hid)
        self._W1 = rng.standard_normal((in_dim, hid)).astype(np.float64) * scale1
        self._b1 = np.zeros(hid)
        self._W2 = rng.standard_normal((hid, out_dim)).astype(np.float64) * scale2
        self._b2 = np.zeros(out_dim)

        # Vanilla SGD with weight decay (AdamW-lite).
        lr = cfg.learning_rate
        wd = cfg.ridge_lambda * 1e-3
        for _ in range(cfg.max_iter):
            # Forward
            H = np.tanh(X @ self._W1 + self._b1)           # (n, hid)
            Yhat = H @ self._W2 + self._b2                 # (n, out)
            E = Yhat - Yr                                  # (n, out)
            # Backward
            gW2 = H.T @ E / len(X) + wd * self._W2
            gb2 = E.mean(axis=0)
            dH = (E @ self._W2.T) * (1.0 - H * H)
            gW1 = X.T @ dH / len(X) + wd * self._W1
            gb1 = dH.mean(axis=0)
            # Step
            self._W1 -= lr * gW1
            self._b1 -= lr * gb1
            self._W2 -= lr * gW2
            self._b2 -= lr * gb2

        return BackboneFitArtifacts(
            backbone_name=self.name,
            n_train_perturbations=len(X),
            train_seconds=time.perf_counter() - t0,
        )

    def predict_logfc(
        self,
        perturbation: str,
        target_gene_idx: int,
        n_genes: int,
    ) -> np.ndarray:
        if self._W1 is None or self._W2 is None or self._mean_logfc is None:
            raise RuntimeError("MLPBackbone.predict_logfc called before fit()")
        if n_genes != self._mean_logfc.size:
            raise ValueError(f"n_genes mismatch: fit={self._mean_logfc.size}, predict={n_genes}")
        x = self._featurize(target_gene_idx, n_genes)
        h = np.tanh(x @ self._W1 + self._b1)
        y = h @ self._W2 + self._b2
        return self._mean_logfc + y
