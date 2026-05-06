"""Test-time compute scaling for genomic foundation models (BioFM-265M and friends)."""

from ttc.config import RunConfig, StrategyName
from ttc.runner import Candidate, StrategyResult, run_strategy

__all__ = [
    "Candidate",
    "RunConfig",
    "StrategyName",
    "StrategyResult",
    "run_strategy",
]
