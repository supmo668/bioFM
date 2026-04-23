"""Pluggable verifiers for scoring generated sequences.

Each verifier implements :class:`Verifier` — a callable that maps a generated
DNA string (plus optional context) to a float where *higher is better*. The
module is dependency-light so ``tests/test_scoring.py`` can run without torch.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Protocol


VALID_BASES = frozenset("ACGTN")


class Verifier(Protocol):
    """Score a candidate generated sequence. Higher is better."""

    name: str

    def __call__(self, candidate: str, *, prompt: str = "") -> float: ...


class GCContentVerifier:
    """Reward candidates whose GC content is close to a target band.

    Biological motivation: most human coding regions sit at ~50% GC; wildly
    off-target GC is usually an artefact.
    """

    name = "gc_content"

    def __init__(self, target: float = 0.5, tolerance: float = 0.1) -> None:
        self.target = target
        self.tolerance = tolerance

    def __call__(self, candidate: str, *, prompt: str = "") -> float:  # noqa: ARG002
        seq = _clean(candidate)
        if not seq:
            return -math.inf
        gc = (seq.count("G") + seq.count("C")) / len(seq)
        dist = abs(gc - self.target)
        # Smooth reward: 1.0 at target, 0.0 at tolerance, negative beyond.
        return 1.0 - dist / self.tolerance


class KmerConsensusVerifier:
    """Score a candidate by k-mer overlap with a reference set.

    Used for self-consistency: the "reference set" is the *other* candidates,
    so the winning sequence is the one most representative of the pool.
    """

    name = "kmer_consensus"

    def __init__(self, k: int = 6) -> None:
        self.k = k
        self._reference_kmers: Counter[str] = Counter()

    def fit(self, references: list[str]) -> "KmerConsensusVerifier":
        self._reference_kmers = Counter()
        for ref in references:
            self._reference_kmers.update(_kmers(_clean(ref), self.k))
        return self

    def __call__(self, candidate: str, *, prompt: str = "") -> float:  # noqa: ARG002
        if not self._reference_kmers:
            return 0.0
        cand_kmers = _kmers(_clean(candidate), self.k)
        if not cand_kmers:
            return 0.0
        total_ref = sum(self._reference_kmers.values())
        # Average reference frequency of this candidate's k-mers.
        score = sum(self._reference_kmers.get(km, 0) for km in cand_kmers) / len(cand_kmers)
        return score / total_ref if total_ref else 0.0


class LogLikelihoodVerifier:
    """Score by the model's own per-token log-likelihood on the candidate.

    Requires a loaded HF-style causal LM. Kept as a callable class so it can be
    swapped with mock scorers in tests without instantiating a model.
    """

    name = "log_likelihood"

    def __init__(self, model: object, tokenizer: object) -> None:  # pragma: no cover - needs torch
        self._model = model
        self._tokenizer = tokenizer

    def __call__(self, candidate: str, *, prompt: str = "") -> float:  # pragma: no cover
        import torch

        text = prompt + candidate
        spaced = " ".join(text)  # BioToken expects space-separated bases
        enc = self._tokenizer(spaced, return_tensors="pt")
        enc = {k: v for k, v in enc.items() if k in {"input_ids"}}
        with torch.inference_mode():
            out = self._model(**enc, labels=enc["input_ids"])
        # HF returns mean NLL in `.loss`; flip sign so higher is better.
        return -float(out.loss.item())


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _clean(seq: str) -> str:
    return "".join(c for c in seq.upper() if c in VALID_BASES)


def _kmers(seq: str, k: int) -> list[str]:
    if len(seq) < k:
        return []
    return [seq[i : i + k] for i in range(len(seq) - k + 1)]


def build_verifier(name: str, **kwargs: object) -> Verifier:
    """Factory so CLI can select verifier by string."""
    registry: dict[str, type[Verifier]] = {
        "gc_content": GCContentVerifier,
        "kmer_consensus": KmerConsensusVerifier,
    }
    if name not in registry:
        raise KeyError(f"unknown verifier: {name}. known={list(registry)}")
    return registry[name](**kwargs)  # type: ignore[arg-type]
