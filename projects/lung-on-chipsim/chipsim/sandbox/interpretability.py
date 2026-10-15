"""The response contract: what must accompany a number for it to be actionable.

The principal's instruction of 2026-10-14 is explicit — the endpoint *"must also carry metadata
& context on interpretability, not just a simulation result"*. This module is that contract,
and it is deliberately written as a REQUIRED structure rather than an optional verbose mode,
because the two differ in exactly the case that matters: a caller in a hurry.

The reasoning is the project's own thesis. Validation, not modelling capacity, is the
bottleneck. A predicted exposure that a wet-lab scientist cannot interrogate does not displace
a wet experiment; it adds a number they must now also check. So every response carries:

- **the interval and what makes it mean anything** — the nominal coverage, the calibration-set
  size it was computed from, and the subgroup it is conditional on. A 90% interval from a
  20-point calibration set is an honest object; the same interval with its n hidden is not.
- **provenance per parameter** — whether each θ field the prediction used was cited, derived or
  assumed. A reader deciding whether to trust an exposure needs to know two of six fields were
  assumptions, and which two.
- **the nearest supporting evidence** — which curated records the calibration rests on, so a
  reader can judge whether their compound resembles anything the model has seen.
- **an abstention, as a first-class outcome** — `Abstention` is not an error and not a null
  prediction. A system that never declines has not been calibrated, only fitted.

Nothing here computes a prediction. It is the shape a prediction must arrive in, so that the
shape cannot be skipped by whoever implements the model later.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

#: Provenance classes, matching chipsim.transport.sourcing so one vocabulary spans the project.
Provenance = Literal["cited", "derived", "assumed"]


@dataclass(frozen=True)
class ParameterProvenance:
    """One parameter the prediction used, and how far it can be trusted."""

    name: str
    provenance: Provenance
    citation: str | None = None
    note: str | None = None

    def __post_init__(self) -> None:
        if self.provenance in ("cited", "derived") and not (self.citation or "").strip():
            raise ValueError(
                f"parameter {self.name!r} is {self.provenance} but carries no citation. The "
                "whole point of reporting provenance is that a reader can resolve it."
            )


@dataclass(frozen=True)
class CoverageBasis:
    """What makes an interval mean something. Every field here is load-bearing."""

    nominal: float
    calibration_n: int
    subgroup: str
    method: str
    #: True when `nominal` is a guarantee conditional on `subgroup`, False when it is marginal.
    #: §5E of the PVR forbids stating coverage in marginal terms, so a marginal interval must
    #: say so rather than borrow the authority of a conditional one.
    group_conditional: bool

    def __post_init__(self) -> None:
        if not 0.0 < self.nominal < 1.0:
            raise ValueError(f"nominal coverage must be a probability, got {self.nominal!r}")
        if self.calibration_n < 1:
            raise ValueError(
                "an interval with no calibration points is not an interval. Report an "
                "abstention instead."
            )

    @property
    def caveat(self) -> str:
        """The sentence a reader needs next to the interval, generated from the basis itself."""
        kind = "conditional on " + self.subgroup if self.group_conditional else "MARGINAL"
        return (
            f"{self.nominal:.0%} nominal coverage by {self.method}, {kind}, from "
            f"{self.calibration_n} calibration point(s). At this n the realised coverage has "
            "its own sampling error, which is why the figure is reported with the count rather "
            "than alone."
        )


@dataclass(frozen=True)
class SupportingEvidence:
    """A curated record the calibration rests on. Identity and source only, never a value."""

    record_id: str
    source: str
    similarity_basis: str


@dataclass(frozen=True)
class Abstention:
    """A declined prediction. An outcome, not a failure.

    Carries the same interpretability obligations as a prediction: a reader is owed the reason,
    what would change it, and the provenance of whatever was consulted before declining.
    """

    reason: str
    what_would_change_it: str
    parameters: tuple[ParameterProvenance, ...] = field(default_factory=tuple)
    domain_note: str | None = None
    kind: Literal["abstention"] = "abstention"

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Prediction:
    """A prediction and everything required to act on it.

    Construction enforces the contract: an interval without its basis, or a prediction whose
    parameters are undeclared, cannot be built. That is the point — the structure is the
    guarantee, not the documentation.
    """

    quantity: str
    unit: str
    point: float
    interval_low: float
    interval_high: float
    coverage: CoverageBasis
    parameters: tuple[ParameterProvenance, ...]
    evidence: tuple[SupportingEvidence, ...]
    model_version: str
    #: Free-text, for what the structure cannot carry: the mechanism the model thinks dominates,
    #: a known limitation that applies to this input, a conflict between sources.
    reading: str = ""
    kind: Literal["prediction"] = "prediction"

    def __post_init__(self) -> None:
        if not self.parameters:
            raise ValueError(
                "a prediction with no declared parameters cannot be interpreted; if the model "
                "truly used none, say so with an explicit entry"
            )
        if not (self.interval_low <= self.point <= self.interval_high):
            raise ValueError(
                f"point {self.point!r} lies outside its own interval "
                f"[{self.interval_low!r}, {self.interval_high!r}]"
            )

    @property
    def assumed_parameters(self) -> tuple[str, ...]:
        return tuple(p.name for p in self.parameters if p.provenance == "assumed")

    def as_dict(self) -> dict:
        """The wire form. The caveat and the assumed list are MATERIALISED, not computed by the
        caller: a client that forgot to call `caveat` would otherwise publish a bare interval."""
        out = asdict(self)
        out["coverage"]["caveat"] = self.coverage.caveat
        out["assumed_parameters"] = list(self.assumed_parameters)
        out["interpretability_contract"] = (
            "This response is a decision object, not a measurement. The interval's meaning is "
            "given by coverage.caveat; the trustworthiness of the inputs is given per parameter "
            "in `parameters`; `assumed_parameters` lists those entered without a citation. No "
            "value here was written by a coding agent."
        )
        return out
