"""Test-time compute strategies.

Each strategy takes a ``GenerateFn`` (pure callable: prompt → candidates) plus a
``Verifier``, and returns a :class:`StrategyResult`. This functional shape makes
tests trivial — no heavy model needed.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from ttc.config import RunConfig, SamplingConfig, StrategyName
from ttc.scoring import KmerConsensusVerifier, Verifier


@dataclass(frozen=True)
class Candidate:
    text: str
    tokens_generated: int


GenerateFn = Callable[[str, SamplingConfig], list[Candidate]]


@dataclass(frozen=True)
class StrategyResult:
    strategy: StrategyName
    winner: Candidate
    candidates: tuple[Candidate, ...]
    scores: tuple[float, ...]
    compute_budget: int  # total tokens generated across all candidates
    verifier_name: str


def _greedy(generate: GenerateFn, cfg: RunConfig, verifier: Verifier) -> StrategyResult:
    sampling = SamplingConfig(
        max_new_tokens=cfg.sampling.max_new_tokens,
        temperature=0.0,
        top_k=1,
        top_p=1.0,
        do_sample=False,
        num_return_sequences=1,
    )
    cands = generate(cfg.prompt, sampling)
    if not cands:
        raise RuntimeError("generator returned no candidates")
    scores = tuple(verifier(c.text, prompt=cfg.prompt) for c in cands)
    return StrategyResult(
        strategy=StrategyName.GREEDY,
        winner=cands[0],
        candidates=tuple(cands),
        scores=scores,
        compute_budget=sum(c.tokens_generated for c in cands),
        verifier_name=verifier.name,
    )


def _best_of_n(generate: GenerateFn, cfg: RunConfig, verifier: Verifier) -> StrategyResult:
    sampling = SamplingConfig(
        max_new_tokens=cfg.sampling.max_new_tokens,
        temperature=cfg.sampling.temperature,
        top_k=cfg.sampling.top_k,
        top_p=cfg.sampling.top_p,
        do_sample=True,
        num_return_sequences=cfg.n_samples,
    )
    cands = generate(cfg.prompt, sampling)
    scores = tuple(verifier(c.text, prompt=cfg.prompt) for c in cands)
    best_idx = max(range(len(cands)), key=scores.__getitem__)
    return StrategyResult(
        strategy=StrategyName.BEST_OF_N,
        winner=cands[best_idx],
        candidates=tuple(cands),
        scores=scores,
        compute_budget=sum(c.tokens_generated for c in cands),
        verifier_name=verifier.name,
    )


def _self_consistency(generate: GenerateFn, cfg: RunConfig, _unused: Verifier) -> StrategyResult:
    sampling = SamplingConfig(
        max_new_tokens=cfg.sampling.max_new_tokens,
        temperature=cfg.sampling.temperature,
        top_k=cfg.sampling.top_k,
        top_p=cfg.sampling.top_p,
        do_sample=True,
        num_return_sequences=cfg.n_samples,
    )
    cands = generate(cfg.prompt, sampling)
    # The verifier *is* the pool: each candidate is scored by how well it
    # matches k-mer statistics of the others. Ignore the incoming verifier.
    consensus = KmerConsensusVerifier(k=6).fit([c.text for c in cands])
    scores = tuple(consensus(c.text, prompt=cfg.prompt) for c in cands)
    best_idx = max(range(len(cands)), key=scores.__getitem__)
    return StrategyResult(
        strategy=StrategyName.SELF_CONSISTENCY,
        winner=cands[best_idx],
        candidates=tuple(cands),
        scores=scores,
        compute_budget=sum(c.tokens_generated for c in cands),
        verifier_name=consensus.name,
    )


def _temperature_sweep(generate: GenerateFn, cfg: RunConfig, verifier: Verifier) -> StrategyResult:
    all_cands: list[Candidate] = []
    all_scores: list[float] = []
    per_temp = max(1, cfg.n_samples // max(1, len(cfg.temperature_grid)))
    for t in cfg.temperature_grid:
        sampling = SamplingConfig(
            max_new_tokens=cfg.sampling.max_new_tokens,
            temperature=t,
            top_k=cfg.sampling.top_k,
            top_p=cfg.sampling.top_p,
            do_sample=True,
            num_return_sequences=per_temp,
        )
        cands = generate(cfg.prompt, sampling)
        all_cands.extend(cands)
        all_scores.extend(verifier(c.text, prompt=cfg.prompt) for c in cands)
    best_idx = max(range(len(all_cands)), key=all_scores.__getitem__)
    return StrategyResult(
        strategy=StrategyName.TEMPERATURE_SWEEP,
        winner=all_cands[best_idx],
        candidates=tuple(all_cands),
        scores=tuple(all_scores),
        compute_budget=sum(c.tokens_generated for c in all_cands),
        verifier_name=verifier.name,
    )


STRATEGIES: dict[StrategyName, Callable[[GenerateFn, RunConfig, Verifier], StrategyResult]] = {
    StrategyName.GREEDY: _greedy,
    StrategyName.BEST_OF_N: _best_of_n,
    StrategyName.SELF_CONSISTENCY: _self_consistency,
    StrategyName.TEMPERATURE_SWEEP: _temperature_sweep,
}


def dispatch(
    strategy: StrategyName,
    generate: GenerateFn,
    cfg: RunConfig,
    verifier: Verifier,
) -> StrategyResult:
    if strategy not in STRATEGIES:
        raise KeyError(f"unknown strategy: {strategy}")
    return STRATEGIES[strategy](generate, cfg, verifier)


# Re-export a reference to Candidate for package __init__
__all__: Sequence[str] = ("Candidate", "StrategyResult", "dispatch", "STRATEGIES")
