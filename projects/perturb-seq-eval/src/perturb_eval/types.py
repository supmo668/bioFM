"""Immutable data carriers used across the package.

Everything here is ``frozen=True`` so a logged trace is safe to serialise,
hash, and pass between processes without defensive copies.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RoundTrace:
    """One round of the 5-agent orchestration."""

    round_index: int
    agent_names: tuple[str, ...]                  # e.g. ("DataCurator", ..., "Validator")
    confidences: tuple[float, ...]                # c_i ∈ [0, 1], same order as agent_names
    critique_severities: tuple[tuple[float, ...], ...]  # S[i][j] severity row i critiquing col j
    winner_index: int                             # argmax over consensus score
    consensus_score: float                        # from the orchestrator
    compute_tokens: int = 0                       # accounting for FLOPs-matched comparisons


@dataclass(frozen=True)
class RunTrace:
    """A full orchestrator run for one task."""

    task_id: str
    rounds: tuple[RoundTrace, ...]
    converged: bool
    backbone: str = "unknown"

    @property
    def n_rounds(self) -> int:
        return len(self.rounds)

    @property
    def n_agents(self) -> int:
        return len(self.rounds[0].agent_names) if self.rounds else 0


@dataclass(frozen=True)
class RoundMetrics:
    """Per-round derived metrics."""

    round_index: int
    ace: float                # raw entropy (nats)
    ace_norm: float           # entropy / log(N), in [0, 1]
    mean_confidence: float
    max_confidence: float
    csd: float                # variance of critique matrix
    csd_max: float            # max severity in the critique matrix
    winner_index: int
    consensus_score: float


@dataclass(frozen=True)
class RunMetrics:
    """Run-level metrics, the scalar summary used for calibration."""

    task_id: str
    per_round: tuple[RoundMetrics, ...]
    delta_ace: float          # ACE(R) - ACE(0); negative = converging
    delta_mean_confidence: float  # mean(c, R) - mean(c, 0); positive = converging
    winner_flip_rate: float
    final_consensus_score: float
    tdi: float                # composite difficulty index


@dataclass(frozen=True)
class Config:
    """Orchestrator hyperparameters, i.e. the thing the recommender picks."""

    n_agents: int = 5
    n_rounds: int = 2
    backbone: str = "scGPT"

    def flops_proxy(self) -> int:
        """A crude but monotonic proxy for compute — enough for relative budgets."""
        # Weight backbones roughly by parameter count.
        weights = {"scGPT": 1, "scFoundation": 1, "scPRINT-2": 2, "BioFM-265M": 1,
                   "Geneformer": 1, "UCE": 1}
        return self.n_agents * self.n_rounds * weights.get(self.backbone, 1)


# Canonical config space used by the default recommender.
DEFAULT_CONFIG_SPACE: tuple[Config, ...] = tuple(
    Config(n_agents=a, n_rounds=r, backbone=b)
    for a in (3, 5)
    for r in (1, 2, 3)
    for b in ("scGPT", "scPRINT-2")
)
