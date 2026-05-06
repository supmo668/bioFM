"""Thin wrapper over ``AnnotatedModel`` / HF ``AutoModelForCausalLM`` with graceful fallback.

If ``biofm_eval`` is installed (the package cloned at ``research/biofm-eval``) we use
``AnnotatedModel`` — otherwise we fall back to the plain HF classes so the code still
runs on any causal LM for development.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Protocol

logger = logging.getLogger(__name__)


class CausalLM(Protocol):
    def generate(self, **kwargs: Any) -> Any: ...
    def __call__(self, **kwargs: Any) -> Any: ...
    def eval(self) -> "CausalLM": ...


class Tokenizer(Protocol):
    pad_token_id: int | None

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...
    def batch_decode(self, *args: Any, **kwargs: Any) -> list[str]: ...


@dataclass(frozen=True)
class LoadedModel:
    model: CausalLM
    tokenizer: Tokenizer
    device: str


def load_biofm(model_name: str, dtype: str = "bfloat16") -> LoadedModel:
    """Load a BioFM-compatible causal LM with biofm-eval if available."""
    import torch

    torch_dtype = getattr(torch, dtype)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    try:
        from biofm_eval import AnnotatedModel, AnnotationTokenizer  # type: ignore
        model = AnnotatedModel.from_pretrained(model_name, torch_dtype=torch_dtype)
        tokenizer = AnnotationTokenizer.from_pretrained(model_name)
        logger.info("Loaded %s via biofm_eval.AnnotatedModel", model_name)
    except Exception as e:  # pragma: no cover - depends on env
        logger.warning("biofm_eval unavailable (%s); falling back to HF AutoModel", e)
        from transformers import AutoModelForCausalLM, AutoTokenizer
        model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch_dtype)
        tokenizer = AutoTokenizer.from_pretrained(model_name)

    model.eval()
    model = model.to(device)
    return LoadedModel(model=model, tokenizer=tokenizer, device=device)
