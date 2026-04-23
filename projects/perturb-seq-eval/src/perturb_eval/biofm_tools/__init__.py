"""HuggingFace-backed biological foundation-model tools for CellForge agents.

This package lets the Literature + Validator agents consult real
pretrained BioFMs (BioGPT for target-gene mechanism retrieval, and a
Geneformer-class gene-embedding model for perturbation-response
validation) instead of rule-based canned responses. Used inside the
Modal image for the live-trace collection run; all imports are
lazy so the core package still installs without torch/transformers.
"""

from __future__ import annotations

__all__ = ["biogpt_literature", "geneformer_validator"]
