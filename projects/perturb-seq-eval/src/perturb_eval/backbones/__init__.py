"""Backbone-predictor registry (see docs/SUPPLEMENT_DESIGN.md §3)."""

from __future__ import annotations

from perturb_eval.backbones.base import (
    BackboneFitArtifacts,
    BackbonePredictor,
    BackboneTrainConfig,
    log_fold_change,
    mean_squared_deviation,
    per_perturbation_mean,
)
from perturb_eval.backbones.linear import LinearBackbone
from perturb_eval.backbones.mlp import MLPBackbone
from perturb_eval.backbones.scgpt_small import HAS_TORCH, SCGPTSmallBackbone

_REGISTRY = {
    "linear": LinearBackbone,
    "mlp": MLPBackbone,
    "scgpt_small": SCGPTSmallBackbone,
}


def available_backbones() -> tuple[str, ...]:
    """Names of backbones that can be instantiated in the current environment."""
    names = ["linear", "mlp"]
    if HAS_TORCH:
        names.append("scgpt_small")
    return tuple(names)


def count_fitted_params(backbone: object) -> int:
    """Learned-parameter count of a FITTED backbone (T8b provenance).

    torch backbones (``_model`` with ``.parameters()``, i.e. scgpt_small, whose
    embedding vocabulary scales with the HVG count): sum of ``numel``. numpy
    backbones (linear, mlp): total size of the fitted ndarray attributes.
    """
    import numpy as np

    model = getattr(backbone, "_model", None)
    if model is not None and hasattr(model, "parameters"):
        return int(sum(p.numel() for p in model.parameters()))
    return int(sum(v.size for v in vars(backbone).values() if isinstance(v, np.ndarray)))


def build_backbone(name: str) -> BackbonePredictor:
    """Instantiate a backbone by name. Raises on unknown or unavailable names."""
    if name not in _REGISTRY:
        raise ValueError(
            f"unknown backbone {name!r}; known: {sorted(_REGISTRY)}"
        )
    if name == "scgpt_small" and not HAS_TORCH:
        raise ImportError(
            "scgpt_small backbone requires PyTorch; run "
            "`poetry install --with scgpt`."
        )
    return _REGISTRY[name]()


__all__ = [
    "BackboneFitArtifacts",
    "BackbonePredictor",
    "BackboneTrainConfig",
    "LinearBackbone",
    "MLPBackbone",
    "SCGPTSmallBackbone",
    "available_backbones",
    "build_backbone",
    "count_fitted_params",
    "log_fold_change",
    "mean_squared_deviation",
    "per_perturbation_mean",
]
