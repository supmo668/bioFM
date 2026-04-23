"""High-level TTC runner — wires a loaded BioFM into the pure strategy layer."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from ttc.config import RunConfig, SamplingConfig
from ttc.scoring import Verifier, build_verifier
from ttc.strategies import Candidate, StrategyResult, dispatch

logger = logging.getLogger(__name__)


def _real_generate_factory(model: Any, tokenizer: Any) -> Callable[[str, SamplingConfig], list[Candidate]]:
    """Build a GenerateFn closure around a real HF causal LM.

    Uses the same space-separated preprocessing as ``biofm_eval.Generator``.
    """

    import torch  # imported here so pure-Python tests don't need torch

    device = next(model.parameters()).device

    def _gen(prompt: str, sampling: SamplingConfig) -> list[Candidate]:
        spaced = " ".join(prompt)
        enc = tokenizer(spaced, return_tensors="pt", padding=True)
        enc = {
            k: v.to(device)
            for k, v in enc.items()
            if k not in {"token_type_ids", "attention_mask"}
        }
        kwargs = dict(
            max_new_tokens=sampling.max_new_tokens,
            do_sample=sampling.do_sample,
            num_return_sequences=sampling.num_return_sequences,
            top_k=sampling.top_k,
            top_p=sampling.top_p,
        )
        if sampling.do_sample and sampling.temperature > 0:
            kwargs["temperature"] = sampling.temperature
        with torch.inference_mode():
            out = model.generate(**enc, **kwargs)
        texts = tokenizer.batch_decode(out, skip_special_tokens=True)
        prompt_len = enc["input_ids"].shape[-1]
        per_cand_tokens = int(out.shape[-1] - prompt_len)
        return [Candidate(text=t.replace(" ", ""), tokens_generated=per_cand_tokens) for t in texts]

    return _gen


def run_strategy(
    cfg: RunConfig,
    *,
    generate: Callable[[str, SamplingConfig], list[Candidate]] | None = None,
    verifier: Verifier | None = None,
) -> StrategyResult:
    """Execute a TTC run.

    ``generate`` and ``verifier`` are injected for testability. When omitted,
    the real BioFM is loaded lazily.
    """

    if generate is None or verifier is None:
        from ttc.model_loader import load_biofm  # lazy

        loaded = load_biofm(cfg.model_name)
        if generate is None:
            generate = _real_generate_factory(loaded.model, loaded.tokenizer)
        if verifier is None:
            verifier = build_verifier(cfg.verifier)

    logger.info("Running %s on prompt=%r n=%d", cfg.strategy.value, cfg.prompt, cfg.n_samples)
    return dispatch(cfg.strategy, generate, cfg, verifier)


__all__ = ["Candidate", "StrategyResult", "run_strategy"]
