"""Per-agent choice-entropy probe.

The paper's §5 "Agent degrees of freedom" analysis asks: given the wide
configuration space Phase 2 exposes, do agents actually *use* it? The
freedom probe quantifies choice diversity per agent role + field across
lifecycle traces.

Traces can be a sequence of sequences of either :class:`LifecycleStep`
dataclass instances (the production path) or plain dicts with keys
``agent_name`` and ``proposal_content`` (the test fixture shape). Both
are accepted.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Any, Iterable, Sequence

_EPS = 1e-12


def _coerce_step(step: Any) -> tuple[str, dict]:
    if hasattr(step, "agent_name") and hasattr(step, "proposal_content"):
        return (step.agent_name, dict(step.proposal_content))
    return (str(step["agent_name"]), dict(step.get("proposal_content", {})))


def _hashable(value: Any) -> Any:
    """Numbers and strings hash directly; dicts/lists get JSON-serialised."""
    if isinstance(value, (int, float, str, bool, type(None))):
        return value
    try:
        import json

        return json.dumps(value, sort_keys=True, default=str)
    except TypeError:
        return repr(value)


def choice_entropy(values: Iterable[Any]) -> float:
    """Shannon entropy (in nats) of the value distribution."""
    counts = Counter(_hashable(v) for v in values)
    total = sum(counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        p = c / total
        if p > _EPS:
            h -= p * math.log(p)
    return h


def per_agent_field_entropy(
    traces: Sequence[Sequence[Any]],
    *,
    agent: str,
    field: str,
) -> float:
    """Entropy of ``proposal_content[field]`` across traces, filtered by agent."""
    values: list[Any] = []
    for trace in traces:
        for step in trace:
            name, content = _coerce_step(step)
            if name == agent and field in content:
                values.append(content[field])
    return choice_entropy(values)


def summarise_choice_distribution(
    traces: Sequence[Sequence[Any]],
    *,
    agent: str,
    field: str,
) -> dict[str, int]:
    """Return a name-keyed histogram for reporting in figures/tables."""
    counts: Counter[str] = Counter()
    for trace in traces:
        for step in trace:
            name, content = _coerce_step(step)
            if name == agent and field in content:
                counts[str(_hashable(content[field]))] += 1
    return dict(counts)
