"""Optimizer registry."""

from __future__ import annotations

from perturb_eval.optimizers.base import Observation, Optimizer, config_to_vec, nearest_config
from perturb_eval.optimizers.cma_es import CMAESOptimizer, OnePlusLambdaES
from perturb_eval.optimizers.contextual_gp import ContextualGPOptimizer
from perturb_eval.optimizers.random_baseline import RandomOptimizer
from perturb_eval.types import Config

_REGISTRY: dict[str, type] = {
    "random": RandomOptimizer,
    "cma_es": OnePlusLambdaES,             # retained alias; see mc7 in REVIEWER_CRITIQUE.md
    "one_plus_lambda_es": OnePlusLambdaES,  # canonical name
    "contextual_gp": ContextualGPOptimizer,
}


def available_optimizers() -> tuple[str, ...]:
    return tuple(_REGISTRY)


def build_optimizer(
    name: str,
    *,
    config_space: tuple[Config, ...],
    seed: int = 0,
    **kwargs: object,
) -> Optimizer:
    if name not in _REGISTRY:
        raise ValueError(
            f"unknown optimizer {name!r}; known: {sorted(_REGISTRY)}"
        )
    cls = _REGISTRY[name]
    return cls(config_space=config_space, seed=seed, **kwargs)  # type: ignore[call-arg]


__all__ = [
    "CMAESOptimizer",
    "ContextualGPOptimizer",
    "Observation",
    "Optimizer",
    "RandomOptimizer",
    "available_optimizers",
    "build_optimizer",
    "config_to_vec",
    "nearest_config",
]
