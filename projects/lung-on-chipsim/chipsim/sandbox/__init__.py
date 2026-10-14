"""The sandbox: the delivery surface for the ChipSim transport surrogate.

Deliberately NOT one of `chipsim.SUBPACKAGES`. That tuple is the A&D §4.4 layer set — the
ten *modelling* layers — and the test suite asserts it matches the architecture exactly. The
sandbox is how the model is served and interpreted, not a layer of the model, so adding it
there would misreport the architecture to make a packaging decision look tidy.

Three modules, separated because they answer different questions:

- `readiness` — may this environment produce a number at all? It reads the artifacts the plan
  makes human-owned and reports, per artifact, whether it exists and what it blocks.
- `interpretability` — what must accompany a number for it to be actionable? The response
  contract, independent of any model.
- `env` — the aviary `Environment` that an agent drives. Imports `fhaviary`, so it is imported
  lazily: the first two modules are usable, and testable, without it.
"""

from __future__ import annotations

__all__ = ["interpretability", "readiness"]
