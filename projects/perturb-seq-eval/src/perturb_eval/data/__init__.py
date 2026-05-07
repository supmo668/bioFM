"""Real-data loaders + fair subsampling.

Two responsibilities:
  * ``download.py`` — idempotent fetch from the scPerturb Zenodo mirror,
    SHA256-gated.
  * ``subsample.py`` — deterministic stratified sampling so the paper's
    "fair subsample" claim is reproducible from a single seed.
"""

from perturb_eval.data.download import (
    ADAMSON_SUBSETS,
    DATASETS,
    DatasetSpec,
    fetch_adamson,
    fetch_adamson_all,
    fetch_norman,
)
from perturb_eval.data.subsample import (
    mean_abs_logfc_per_target,
    stratified_subsample,
)

__all__ = [
    "ADAMSON_SUBSETS",
    "DATASETS",
    "DatasetSpec",
    "fetch_adamson",
    "fetch_adamson_all",
    "fetch_norman",
    "mean_abs_logfc_per_target",
    "stratified_subsample",
]
