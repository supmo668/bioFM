"""Dataset protocol, real-data loaders, and fair subsampling.

Three responsibilities:
  * ``protocol.py`` — the ``PerturbSeqDataset`` protocol, the ``PerturbSeqSplit``
    record and the synthetic stub. Stdlib only.
  * ``download.py`` — idempotent fetch from the scPerturb Zenodo mirror,
    SHA256-gated.
  * ``subsample.py`` — deterministic stratified sampling so the paper's
    "fair subsample" claim is reproducible from a single seed.

``protocol.py`` used to be ``perturb_eval/data.py``, a module sibling of this
package. A package shadows a same-named module, so from the moment this package
was added (v0.5.0-phase1, two days after the module) every name in it became
unreachable and ``from perturb_eval.data import PerturbSeqSplit`` raised
ImportError — which broke ``adamson_loader`` and, through it, the
``scripts/live_smoke.py`` command documented in LIVE_RUN.md. Moving the module
in here and re-exporting restores that import verbatim.

Note ``fetch_*`` vs ``load_*``: ``fetch_adamson``/``fetch_norman`` download the
h5ad; ``load_adamson``/``load_norman`` read one into a dataset.
"""

from perturb_eval.data.download import (
    ADAMSON_SUBSETS,
    DATASETS,
    DatasetSpec,
    fetch_adamson,
    fetch_adamson_all,
    fetch_norman,
)
from perturb_eval.data.protocol import (
    PerturbSeqDataset,
    PerturbSeqSplit,
    SyntheticPerturbSeq,
    load_adamson,
    load_norman,
)
from perturb_eval.data.subsample import (
    mean_abs_logfc_per_target,
    stratified_subsample,
)

__all__ = [
    "ADAMSON_SUBSETS",
    "DATASETS",
    "DatasetSpec",
    "PerturbSeqDataset",
    "PerturbSeqSplit",
    "SyntheticPerturbSeq",
    "fetch_adamson",
    "fetch_adamson_all",
    "fetch_norman",
    "load_adamson",
    "load_norman",
    "mean_abs_logfc_per_target",
    "stratified_subsample",
]
