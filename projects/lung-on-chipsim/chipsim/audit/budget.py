"""R9 · budget ledger with PRE-EMPTIVE re-projection from measured throughput.

The plan costs 1,240 complexes at **90 complexes/GPU-h** — the principal's ruling,
legitimate because the PVR states 80–100. The risk was put to him and he took it,
so it is recorded plainly rather than softened:

    1,240 / 90 = 13.8 GPU-h x $1.95 = $26.87   fits
    1,240 / 80 = 15.5 GPU-h x $1.95 = $30.22   BREACHES the $30 ceiling

**The apparent $3.13 of headroom is an artefact of the assumption, not margin.**

So 90 is treated as **provisional until batch 1 measures it** (the A9 shape: a
planning number a single early measurement can replace), and this module makes the
assumption *measured* rather than merely disclosed.

## Why a spent-so-far ledger is not enough

A guard that compares **spent** against the ceiling discovers a breach at the
moment it is too late to avoid — the money is already gone. Every other gate in
this design is pre-hoc: P0 measures before any spend, G3 halts before the batch.
R9 matches by **projecting the total from realised throughput and halting before
the remaining work is dispatched**.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


def _finite_positive(name: str, value: float) -> float:
    """Reject NaN, inf and non-positive values.

    NaN is called out explicitly because `nan > ceiling` is False, so a NaN
    projection would sail through a breach check and authorise the spend. That
    exact defect has already appeared twice in this package — in `icc` and in
    `rho` — and both times it authorised rather than refused.
    """
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and positive; got {value!r}")
    return float(value)


@dataclass(frozen=True)
class Projection:
    """A total-cost projection built from what actually happened so far."""

    measured_rate: float
    planned_rate: float
    complexes_done: int
    complexes_remaining: int
    spent_usd: float
    projected_total_usd: float
    ceiling_usd: float

    @property
    def breaches(self) -> bool:
        """Derived, never stored.

        A stored verdict lets a `Projection` be constructed whose flag contradicts
        the numbers printed to justify it — the defect found in `HaltDecision`,
        where `proceed=True` sat happily beside `worst_power=0.11`.
        """
        return self.projected_total_usd > self.ceiling_usd

    @property
    def rate_ratio(self) -> float:
        """Measured over planned. Below 1.0 means slower than assumed."""
        return self.measured_rate / self.planned_rate

    def reason(self) -> str:
        verdict = "HALT" if self.breaches else "CONTINUE"
        return (
            f"{verdict}: measured {self.measured_rate:.1f} complexes/GPU-h against a "
            f"planned {self.planned_rate:.1f} ({self.rate_ratio:.2f}x). "
            f"{self.complexes_done} done for ${self.spent_usd:.2f}; "
            f"{self.complexes_remaining} remaining project a total of "
            f"${self.projected_total_usd:.2f} against a ${self.ceiling_usd:.2f} ceiling. "
            "Projected from REALISED throughput, not from the planning assumption."
        )


def project_from_measurement(
    *,
    complexes_done: int,
    gpu_hours_used: float,
    complexes_remaining: int,
    usd_per_gpu_hour: float = 1.95,
    planned_rate: float = 90.0,
    ceiling_usd: float = 30.0,
) -> Projection:
    """Re-project total cost from batch-1 throughput, BEFORE the rest is dispatched.

    `planned_rate` defaults to the ruled 90/GPU-h so the projection reports how far
    reality has moved from the assumption, which is the number that makes 90
    auditable rather than merely stated.
    """
    if complexes_done < 1:
        raise ValueError(
            f"complexes_done={complexes_done}; a projection needs at least one "
            "completed complex — there is nothing to measure a rate from"
        )
    if complexes_remaining < 0:
        raise ValueError(f"complexes_remaining={complexes_remaining} is negative")
    gpu_hours_used = _finite_positive("gpu_hours_used", gpu_hours_used)
    usd_per_gpu_hour = _finite_positive("usd_per_gpu_hour", usd_per_gpu_hour)
    planned_rate = _finite_positive("planned_rate", planned_rate)
    ceiling_usd = _finite_positive("ceiling_usd", ceiling_usd)

    measured_rate = complexes_done / gpu_hours_used
    spent = gpu_hours_used * usd_per_gpu_hour
    # Remaining cost at the MEASURED rate, not the planned one. Using the plan here
    # would make the guard re-assert the assumption it exists to test.
    remaining_hours = complexes_remaining / measured_rate
    projected_total = spent + remaining_hours * usd_per_gpu_hour

    return Projection(
        measured_rate=measured_rate,
        planned_rate=planned_rate,
        complexes_done=complexes_done,
        complexes_remaining=complexes_remaining,
        spent_usd=spent,
        projected_total_usd=projected_total,
        ceiling_usd=ceiling_usd,
    )


def authorize_batch(
    projection: Projection,
    *,
    batch_complexes: int,
    usd_per_gpu_hour: float = 1.95,
) -> None:
    """Raise rather than dispatch a batch whose projected total breaches the ceiling.

    Refuses on the **projection**, not on spend-so-far. A ledger that authorises
    while `ceiling - spent` still reads healthy will authorise its way into a
    breach one batch at a time, each step individually affordable.
    """
    if batch_complexes < 1:
        raise ValueError(f"batch_complexes={batch_complexes}; nothing to authorize")
    if projection.breaches:
        raise BudgetBreach(
            f"refusing to dispatch {batch_complexes} complexes: {projection.reason()}"
        )


class BudgetBreach(RuntimeError):
    """Raised BEFORE the spend that would breach the ceiling, never after."""
