"""Immutable configuration objects for TTC runs.

Every dataclass here is ``frozen=True`` so a run descriptor can be serialised
to JSONL next to its results without risk of post-hoc mutation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class StrategyName(str, Enum):
    GREEDY = "greedy"
    BEST_OF_N = "best_of_n"
    SELF_CONSISTENCY = "self_consistency"
    TEMPERATURE_SWEEP = "temperature_sweep"


@dataclass(frozen=True)
class SamplingConfig:
    """Hyper-parameters passed straight to ``model.generate``."""

    max_new_tokens: int = 64
    temperature: float = 1.0
    top_k: int = 4
    top_p: float = 1.0
    do_sample: bool = True
    num_return_sequences: int = 1


@dataclass(frozen=True)
class RunConfig:
    """Top-level config for one TTC run."""

    strategy: StrategyName
    model_name: str = "m42-health/BioFM-265M"
    prompt: str = "ATGCGTACGT"
    n_samples: int = 8
    sampling: SamplingConfig = field(default_factory=SamplingConfig)
    seed: int | None = 42

    # verifier selection — plain string so new verifiers don't require an enum change
    verifier: str = "log_likelihood"

    # for temperature sweep only
    temperature_grid: tuple[float, ...] = (0.4, 0.7, 1.0, 1.3)
