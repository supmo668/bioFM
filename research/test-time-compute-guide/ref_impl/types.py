"""Minimal shared types used across every reference implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Candidate:
    """One generated output + its compute cost."""

    text: str
    tokens: int = 0  # accounting for FLOPs-matched comparisons


class Generator(Protocol):
    """A model that turns a prompt into one or more candidates.

    ``n`` is the number of independent samples to draw (parallel TTC).
    """

    def __call__(self, prompt: str, *, n: int = 1) -> list[Candidate]: ...


class Verifier(Protocol):
    """Score a candidate: higher is better.

    Either a PRM (process reward model, scores intermediate steps),
    an ORM (outcome reward model, scores the final answer), or any hand-rolled
    domain checker.
    """

    def __call__(self, candidate: Candidate, *, prompt: str = "") -> float: ...


class Reviser(Protocol):
    """A model that takes a prompt + draft and produces a revised draft."""

    def __call__(self, prompt: str, draft: Candidate) -> Candidate: ...
