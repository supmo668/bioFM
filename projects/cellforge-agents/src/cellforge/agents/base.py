"""Base agent contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from cellforge.problem import Context, Critique, Proposal


class BaseAgent(ABC):
    """All agents share this two-method contract.

    ``propose`` emits a structured :class:`Proposal`; ``critique`` scores
    another agent's proposal. The orchestrator drives both.
    """

    name: str

    @abstractmethod
    def propose(self, ctx: Context) -> Proposal: ...

    def critique(self, ctx: Context, other: Proposal) -> Critique:
        """Default: gentle approval — subclasses override for real checks."""
        return Critique(
            from_agent=self.name,
            on_agent=other.agent,
            severity=0.2,
            comment=f"{self.name} has no domain-specific critique for {other.agent}",
        )
