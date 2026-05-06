"""Backend protocol — any object with a ``complete`` method works."""

from __future__ import annotations

from typing import Protocol


class LLMBackend(Protocol):
    """Minimal backend contract used by agents.

    Real backends (OpenAI, Anthropic, vLLM) wrap their SDK; tests use
    :class:`cellforge.backends.MockBackend`.
    """

    name: str

    def complete(self, system: str, user: str, *, max_tokens: int = 512) -> str: ...
