"""May the sandbox produce a number? — the gate, stated as artifacts rather than as a flag.

The validation barrier is the project's stated bottleneck, and this module is the smallest
honest expression of it: a simulator that cannot say *why* it is not ready is indistinguishable
from one that is willing to make something up.

So readiness is not a boolean the code sets. It is a report over the artifacts the build plan
makes human-owned, each one named, each with what it blocks and who owns it. The environment
refuses while any BLOCKING artifact is absent, and the refusal carries this report — so the
caller learns which six quotes or which signature stand between them and a prediction, rather
than receiving a number whose provenance they would have to reconstruct.

Nothing here reads a biological value. It reads whether files exist and whether their
validators accept them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Artifact:
    """One input the sandbox depends on, and what its absence costs."""

    key: str
    relpath: str
    owner: str  # "principal" | "CTO" | "agent"
    blocks: str
    plan_task: str
    #: True when a missing artifact must stop a prediction. False when its absence degrades
    #: the answer but an honest answer is still possible, and the degradation is reportable.
    blocking: bool = True


#: The artifacts, in the order a reader should resolve them.
REQUIRED_ARTIFACTS: tuple[Artifact, ...] = (
    Artifact(
        "theta",
        "configs/theta_priors.yaml",
        "principal",
        "every transport prediction: the fit refuses unsourced θ",
        "T20",
    ),
    Artifact(
        "transport_prior",
        "configs/transport_prior.yaml",
        "principal",
        "the MAP fit; at three reference compounds the result is substantially prior-determined",
        "T28",
    ),
    Artifact(
        "reference_compounds",
        "configs/m1_reference_compounds.yaml",
        "principal",
        "the M1 gate check: the independent yardstick the model is scored against",
        "T21",
    ),
    Artifact(
        "adjudicated_labels",
        "configs/pgp_adjudication.csv",
        "principal",
        "the two P-gp groups every subgroup coverage claim conditions on",
        "T14",
    ),
    Artifact(
        "chip_records",
        "data/processed/chip_records.parquet",
        "principal",
        "calibration: without records there is no interval, only a point guess",
        "M0b",
    ),
    Artifact(
        "evaluator_signature",
        "configs/evaluator_freeze.yaml",
        "principal",
        "any reported metric: an unsigned evaluator may still be edited",
        "M0c",
        blocking=False,
    ),
)


@dataclass(frozen=True)
class ArtifactStatus:
    key: str
    present: bool
    accepted: bool | None  # None when no validator exists, or when the file is absent
    detail: str
    artifact: Artifact


@dataclass(frozen=True)
class ReadinessReport:
    """What the sandbox can and cannot do right now, and exactly why."""

    statuses: tuple[ArtifactStatus, ...]
    project_root: Path
    notes: tuple[str, ...] = field(default_factory=tuple)

    @property
    def blocking_absent(self) -> tuple[ArtifactStatus, ...]:
        return tuple(s for s in self.statuses if s.artifact.blocking and not s.accepted)

    @property
    def can_predict(self) -> bool:
        return not self.blocking_absent

    @property
    def degradations(self) -> tuple[str, ...]:
        """Non-blocking gaps that change how a result must be read."""
        return tuple(
            f"{s.key}: {s.detail} (affects {s.artifact.blocks})"
            for s in self.statuses
            if not s.artifact.blocking and not s.accepted
        )

    def refusal(self) -> str:
        """The message a caller gets instead of a number. Names artifacts, owners and tasks."""
        if self.can_predict:
            raise ValueError("refusal() called on a ready sandbox")
        lines = [
            (
                "REFUSED: the sandbox cannot produce a transport prediction yet, and will not "
                "produce one without the inputs below. This is the validation barrier stated "
                "mechanically rather than argued about: each line is an artifact, its owner, "
                "and what its absence blocks."
            ),
        ]
        for s in self.blocking_absent:
            a = s.artifact
            lines.append(
                f"  - {a.key} ({a.plan_task}, owner: {a.owner}) at {a.relpath} — {s.detail}. "
                f"Blocks: {a.blocks}."
            )
        if self.degradations:
            lines.append("Non-blocking, but they change how any future result must be read:")
            lines += [f"  - {d}" for d in self.degradations]
        return "\n".join(lines)


def _theta_status(root: Path, artifact: Artifact) -> ArtifactStatus:
    path = root / artifact.relpath
    if not path.is_file():
        return ArtifactStatus(
            artifact.key,
            False,
            None,
            "absent; its absence is how Global Constraint 1 is enforced (S6), so this is the "
            "designed state until a human ratifies a filled file",
            artifact,
        )
    from chipsim.transport.theta import ThetaConfig, ThetaError

    try:
        cfg = ThetaConfig.load(path)
    except ThetaError as exc:
        return ArtifactStatus(artifact.key, True, False, f"present but refused: {exc}", artifact)
    return ArtifactStatus(
        artifact.key,
        True,
        True,
        f"accepted: {cfg.cited_count} cited, {cfg.assumed_count} assumed"
        + (f" ({', '.join(cfg.assumed_fields())})" if cfg.assumed_fields() else ""),
        artifact,
    )


def _prior_status(root: Path, artifact: Artifact) -> ArtifactStatus:
    path = root / artifact.relpath
    if not path.is_file():
        return ArtifactStatus(artifact.key, False, None, "absent", artifact)
    from chipsim.transport.prior import TransportPrior, TransportPriorError

    try:
        prior = TransportPrior.load(path)
    except TransportPriorError as exc:
        return ArtifactStatus(artifact.key, True, False, f"present but refused: {exc}", artifact)
    assumed = prior.assumed_entries()
    return ArtifactStatus(
        artifact.key,
        True,
        True,
        "accepted"
        + (f"; explicit assumption(s): {', '.join(assumed)}" if assumed else "; both cited"),
        artifact,
    )


def _reference_status(root: Path, artifact: Artifact) -> ArtifactStatus:
    path = root / artifact.relpath
    if not path.is_file():
        return ArtifactStatus(artifact.key, False, None, "absent", artifact)
    from chipsim.harmonize.reference_compounds import (
        ReferenceCompoundError,
        load_reference_compounds,
    )

    try:
        frame = load_reference_compounds(path)
    except ReferenceCompoundError as exc:
        return ArtifactStatus(artifact.key, True, False, f"present but refused: {exc}", artifact)
    return ArtifactStatus(artifact.key, True, True, f"accepted: {len(frame)} entries", artifact)


def _exists_only(root: Path, artifact: Artifact) -> ArtifactStatus:
    """For artifacts whose validator is not built yet: presence is all that can be checked.

    `accepted` stays None rather than True, because "the file is there" is a weaker claim than
    "a validator accepted it" and the report must not blur the two.
    """
    path = root / artifact.relpath
    if not path.is_file():
        return ArtifactStatus(artifact.key, False, None, "absent", artifact)
    return ArtifactStatus(
        artifact.key,
        True,
        None,
        "present, but no validator is built for it yet, so acceptance is unverified",
        artifact,
    )


_CHECKS = {
    "theta": _theta_status,
    "transport_prior": _prior_status,
    "reference_compounds": _reference_status,
}


def assess(project_root: Path) -> ReadinessReport:
    """Report, per artifact, whether the sandbox may use it. Reads files, never values."""
    root = Path(project_root)
    statuses = tuple(_CHECKS.get(a.key, _exists_only)(root, a) for a in REQUIRED_ARTIFACTS)
    notes = (
        (
            "Readiness is computed from artifacts on disk at call time, not cached: a sandbox "
            "that remembered it was ready would keep answering after an input was withdrawn."
        ),
    )
    return ReadinessReport(statuses=statuses, project_root=root, notes=notes)
