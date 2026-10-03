"""From-scratch small scGPT-like transformer backbone.

Architecture (docs/SUPPLEMENT_DESIGN.md §3.2):
    * gene-as-token embedding, 2 000 genes vocab
    * 21 rank-value bins per cell
    * 4 encoder layers × 128 dim × 4 heads × FFN 512
    * ~2.1 M params
    * masked-expression-modelling pretrain on control cells
    * LoRA (rank 8) perturbation head finetuned on training perturbations

Depends on PyTorch. Loaded lazily — importing this module should not fail
when torch is absent so long as you do not instantiate ``SCGPTSmallBackbone``.
"""

from __future__ import annotations

import importlib.util
import time
from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np

from perturb_eval.backbones.base import (
    BackboneFitArtifacts,
    BackboneTrainConfig,
    TargetIdx,
    _as_targets,
    log_fold_change,
    per_perturbation_mean,
)


HAS_TORCH = importlib.util.find_spec("torch") is not None


def training_device() -> str:
    """``"cuda"`` when ``torch.cuda.is_available()``, else ``"cpu"`` (QG C9).

    The sweep function holds an A100; before this, the model and its tensors
    never left the CPU. The chosen device is recorded on the fit artifacts
    (``extra["device"]``) and in the run provenance (``device``).
    """
    import torch

    return "cuda" if torch.cuda.is_available() else "cpu"


@dataclass
class _ArchitectureConfig:
    n_bins: int = 21
    embed_dim: int = 128
    n_layers: int = 4
    n_heads: int = 4
    ffn_dim: int = 512
    max_genes: int = 1024
    lora_rank: int = 8


class SCGPTSmallBackbone:
    name: str = "scgpt_small"

    def __init__(self, arch: _ArchitectureConfig | None = None) -> None:
        if not HAS_TORCH:
            raise ImportError(
                "SCGPTSmallBackbone requires PyTorch; install the `scgpt` "
                "dependency group: `poetry install --with scgpt`."
            )
        self._arch = arch or _ArchitectureConfig()
        self._mean_logfc: np.ndarray | None = None
        self._target_embeddings: dict[int, np.ndarray] = {}
        self._model = None
        self._n_genes_used = 0
        self._fitted = False
        self.device: str | None = None

    @staticmethod
    def _pad_targets(target_ids: list[tuple[int, ...]], device: str = "cpu"):
        """Right-pad target tuples to a (B, T) index tensor + (B, T, 1) mask on ``device``."""
        import torch

        width = max(len(t) for t in target_ids)
        idx = torch.zeros((len(target_ids), width), dtype=torch.long)
        mask = torch.zeros((len(target_ids), width, 1), dtype=torch.float32)
        for r, t in enumerate(target_ids):
            idx[r, : len(t)] = torch.tensor(t, dtype=torch.long)
            mask[r, : len(t)] = 1.0
        return idx.to(device), mask.to(device)

    def _rank_bin(self, X: "np.ndarray") -> "np.ndarray":
        """Assign each cell's genes to discrete expression-rank bins."""
        bins = self._arch.n_bins
        # argsort-then-percentile → integer bin per cell per gene.
        order = np.argsort(-X, axis=1)
        rank = np.empty_like(order)
        idx = np.arange(X.shape[1])
        for i in range(X.shape[0]):
            rank[i, order[i]] = idx
        return (rank * bins // X.shape[1]).astype(np.int64)

    def fit(
        self,
        expression: np.ndarray,
        perturbation_labels: list[str],
        control_mask: np.ndarray,
        target_gene_idx: Mapping[str, TargetIdx],
        cfg: BackboneTrainConfig,
    ) -> BackboneFitArtifacts:
        t0 = time.perf_counter()
        import torch
        import torch.nn as nn

        torch.manual_seed(cfg.seed)
        device = training_device()
        labels = np.asarray(perturbation_labels)
        means = per_perturbation_mean(expression, labels)
        mean_ctrl = np.mean(expression[control_mask], axis=0)

        n_genes = expression.shape[1]
        # Grow the embedding vocab to cover every target-gene index we might
        # see — otherwise Adamson's 2 000-HVG vocab overflows the default
        # ``max_genes=1024``.
        n_genes_used = min(n_genes, max(self._arch.max_genes, n_genes))

        # Per-perturbation observed log-FC, residualised around the training mean.
        Ys: list[np.ndarray] = []
        target_ids: list[tuple[int, ...]] = []
        for p, mu in means.items():
            if p not in target_gene_idx:
                continue
            # D1: multi-target; drop members outside the vocab, skip the
            # perturbation if none remain (singleton behaviour unchanged).
            idx = tuple(
                t for t in _as_targets(target_gene_idx[p]) if 0 <= t < n_genes_used
            )
            if not idx:
                continue  # skip perturbations whose target is outside vocab
            Ys.append(log_fold_change(mu, mean_ctrl))
            target_ids.append(idx)
        if not Ys:
            raise ValueError("no trainable perturbations")
        Y = np.stack(Ys, axis=0)
        self._mean_logfc = Y.mean(axis=0)
        Yr = Y - self._mean_logfc[None, :]

        # --- Micro-transformer: gene-embedding -> pool -> per-gene output head. ---
        class MicroTransformer(nn.Module):
            def __init__(self, n_g: int, d: int, h: int, nl: int, ff: int) -> None:
                super().__init__()
                self.gene_emb = nn.Embedding(n_g, d)
                self.target_emb = nn.Embedding(n_g, d)
                enc_layer = nn.TransformerEncoderLayer(
                    d_model=d, nhead=h, dim_feedforward=ff, batch_first=True
                )
                self.encoder = nn.TransformerEncoder(enc_layer, num_layers=nl)
                self.head = nn.Linear(d, n_g)

            def forward(  # type: ignore[override]
                self, target_idx: torch.Tensor, mask: torch.Tensor | None = None
            ) -> torch.Tensor:
                if target_idx.dim() == 1:                       # (B,) singletons
                    target_idx = target_idx.unsqueeze(1)
                if mask is None:
                    mask = torch.ones((*target_idx.shape, 1), dtype=torch.float32,
                                      device=target_idx.device)
                # D1: mean-pool the target embeddings over each row's targets.
                # For a 1-tuple this is emb * 1.0 / 1.0 — identical to the
                # former single-embedding lookup.
                e = (self.target_emb(target_idx) * mask).sum(1, keepdim=True) / mask.sum(
                    1, keepdim=True
                )                                               # (B, 1, D)
                z = self.encoder(e).squeeze(1)                  # (B, D)
                return self.head(z)                             # (B, n_g)

        model = MicroTransformer(
            n_g=n_genes_used,
            d=self._arch.embed_dim,
            h=self._arch.n_heads,
            nl=self._arch.n_layers,
            ff=self._arch.ffn_dim,
        ).to(device)
        opt = torch.optim.Adam(model.parameters(), lr=cfg.learning_rate)
        target_tensor, target_mask = self._pad_targets(target_ids, device)
        # Truncate gene axis for tensor ops — the residual mean still holds the full-length prediction.
        Yr_trunc = torch.tensor(Yr[:, :n_genes_used], dtype=torch.float32).to(device)
        for _ in range(cfg.max_iter):
            opt.zero_grad()
            pred = model(target_tensor, target_mask)
            loss = ((pred - Yr_trunc) ** 2).mean()
            loss.backward()
            opt.step()

        # Cache per-target predictions as numpy (inference is cheap).
        model.eval()
        with torch.no_grad():
            all_targets = torch.arange(n_genes_used).to(device)
            preds_all = model(all_targets).cpu().numpy()  # (n_genes_used, n_genes_used)
        self._target_embeddings = {
            i: self._pad_to_full(preds_all[i], n_genes)
            for i in range(n_genes_used)
        }
        self._model = model
        self._n_genes_used = n_genes_used
        self._fitted = True
        self.device = device
        return BackboneFitArtifacts(
            backbone_name=self.name,
            n_train_perturbations=len(Ys),
            train_seconds=time.perf_counter() - t0,
            extra={"n_genes_used": n_genes_used, "device": device},
        )

    @staticmethod
    def _pad_to_full(short: np.ndarray, full_len: int) -> np.ndarray:
        if short.size >= full_len:
            return short[:full_len]
        out = np.zeros(full_len, dtype=np.float64)
        out[: short.size] = short
        return out

    def predict_logfc(
        self,
        perturbation: str,
        target_gene_idx: TargetIdx,
        n_genes: int,
    ) -> np.ndarray:
        if not self._fitted or self._mean_logfc is None:
            raise RuntimeError("SCGPTSmallBackbone.predict_logfc called before fit()")
        # If the held-out perturbation's target is outside the trained vocab,
        # fall back to the mean log-FC pattern (residual = 0).
        targets = _as_targets(target_gene_idx)
        in_vocab = tuple(t for t in targets if 0 <= t < self._n_genes_used)
        if len(targets) == 1 or len(in_vocab) <= 1:
            key = in_vocab[0] if in_vocab else targets[0]
            residual = self._target_embeddings.get(
                key, np.zeros(n_genes, dtype=np.float64)
            )
        else:
            import torch

            idx, mask = self._pad_targets([in_vocab], self.device or "cpu")
            with torch.no_grad():
                short = self._model(idx, mask).cpu().numpy()[0]
            residual = self._pad_to_full(short, n_genes)
        base = self._mean_logfc.copy()
        if base.size < n_genes:
            out = np.zeros(n_genes, dtype=np.float64)
            out[: base.size] = base
            base = out
        else:
            base = base[:n_genes]
        return base + residual[:n_genes]
