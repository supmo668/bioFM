"""ACE, CSD, ΔACE, ΔC, WFR, CST, TDI.

All functions are pure: they operate on ``RoundTrace`` / ``RunTrace`` and return
new ``RoundMetrics`` / ``RunMetrics`` objects.

Math is implemented in ``numpy`` for numerical stability (softmax with log-sum-exp,
variance with ddof=0) but no heavyweight deps beyond that.
"""

from __future__ import annotations

import math

import numpy as np

from perturb_eval.types import RoundMetrics, RoundTrace, RunMetrics, RunTrace

_EPS = 1e-12


# ---------------------------------------------------------------------------
# M1 — Agent Confidence Entropy (ACE)
# ---------------------------------------------------------------------------

def ace(confidences: tuple[float, ...], *, temperature: float = 1.0) -> float:
    """Shannon entropy (nats) of the softmax-normalised confidence distribution.

    Parameters
    ----------
    confidences:
        Per-agent confidence in [0, 1], one per agent.
    temperature:
        Softmax temperature. τ=1 (default) is the natural scale. Lower τ
        sharpens the distribution; raising τ flattens it.

    Returns
    -------
    float
        Entropy in nats, in [0, log(N)].
    """
    if not confidences:
        raise ValueError("confidences is empty")
    if temperature <= 0:
        raise ValueError("temperature must be positive")
    x = np.asarray(confidences, dtype=np.float64) / temperature
    # log-sum-exp for numerical stability
    m = float(np.max(x))
    log_z = m + math.log(float(np.sum(np.exp(x - m))))
    log_p = x - log_z
    p = np.exp(log_p)
    # H = -Σ p_i log p_i  (handles p_i -> 0 via p_i * log p_i -> 0)
    return float(-np.sum(p * log_p))


def ace_norm(confidences: tuple[float, ...], *, temperature: float = 1.0) -> float:
    """ACE normalised to [0, 1] by the maximum possible entropy log(N)."""
    n = len(confidences)
    if n <= 1:
        return 0.0
    return ace(confidences, temperature=temperature) / math.log(n)


# ---------------------------------------------------------------------------
# M1' — Direct simplex-projection entropy (ACE_D)
# ---------------------------------------------------------------------------

def ace_d(confidences: tuple[float, ...]) -> float:
    """Normalised entropy of the simplex-projected confidence vector.

    Unlike :func:`ace_norm` (which routes through softmax with temperature),
    this normalises by direct sum so that concentrated confidences collapse
    to a point mass and flat confidences stay uniform. Removes the free
    temperature parameter entirely.

    * ``(0.5, 0.5, 0.5, 0.5, 0.5)`` → 1.0 (uniform).
    * ``(1.0, 0.0, 0.0, 0.0, 0.0)`` → 0.0 (point mass).
    * All-zero input → 0.0 (by convention, no information).

    Returns
    -------
    float
        Entropy normalised by log(N), in [0, 1].
    """
    if not confidences:
        raise ValueError("confidences is empty")
    arr = np.asarray(confidences, dtype=np.float64)
    if bool(np.any(arr < 0.0)):
        raise ValueError("confidences must be non-negative")
    n = arr.size
    if n <= 1:
        return 0.0
    total = float(arr.sum())
    if total <= _EPS:
        return 0.0
    p = arr / total
    nonzero = p > _EPS
    if not bool(np.any(nonzero)):
        return 0.0
    h = float(-np.sum(p[nonzero] * np.log(p[nonzero])))
    return h / math.log(n)


# ---------------------------------------------------------------------------
# M2 — Critique Severity Dispersion (CSD)
# ---------------------------------------------------------------------------

def critique_severity_dispersion(
    critique_severities: tuple[tuple[float, ...], ...],
) -> float:
    """Variance (ddof=0) of all finite entries of the critique matrix.

    Diagonal entries are excluded (an agent doesn't critique itself). If the
    matrix is empty, returns 0.
    """
    flat = _flatten_critiques(critique_severities)
    if len(flat) == 0:
        return 0.0
    return float(np.var(flat, ddof=0))


def critique_severity_max(
    critique_severities: tuple[tuple[float, ...], ...],
) -> float:
    """Largest severity in the critique matrix — the "loudest critic" signal."""
    flat = _flatten_critiques(critique_severities)
    return float(np.max(flat)) if len(flat) else 0.0


def critique_severity_star(
    critique_severities: tuple[tuple[float, ...], ...],
) -> float:
    """Excess severity over the median (``CSD★`` in docs/SUPPLEMENT_DESIGN.md §1).

    Defined as ``(max − median) / (1 − median + ε)`` over off-diagonal
    severities. Matches the thesis prose "one large critique dwarfs many
    small" — bimodal-variance CSD does not.

    * Flat matrix → 0.
    * All-ones matrix → 0 (no excess).
    * Lone outlier at 1.0 among 0.1s → near 1.
    * Bounded in ``[0, 1]``.
    """
    flat = _flatten_critiques(critique_severities)
    if len(flat) == 0:
        return 0.0
    hi = float(np.max(flat))
    med = float(np.median(flat))
    denom = 1.0 - med + _EPS
    # If max ≤ median (degenerate, e.g. all-ones), excess is 0.
    if hi <= med:
        return 0.0
    excess = (hi - med) / denom
    return float(max(0.0, min(1.0, excess)))


def _flatten_critiques(matrix: tuple[tuple[float, ...], ...]) -> np.ndarray:
    """Return a 1-D array of off-diagonal entries (if square) or all entries."""
    if not matrix:
        return np.empty(0)
    rows = [list(r) for r in matrix]
    n_rows = len(rows)
    n_cols = max(len(r) for r in rows) if rows else 0
    # If square, treat as an adjacency matrix with undefined diagonal and drop it.
    if n_rows == n_cols:
        return np.array(
            [rows[i][j] for i in range(n_rows) for j in range(n_cols) if i != j],
            dtype=np.float64,
        )
    # Rectangular (e.g. 5 critics × 4 targets) — already excludes self-critique.
    return np.array([v for r in rows for v in r], dtype=np.float64)


# ---------------------------------------------------------------------------
# Per-round convenience
# ---------------------------------------------------------------------------

def round_metrics(rt: RoundTrace) -> RoundMetrics:
    confs = rt.confidences
    arr = np.asarray(confs, dtype=np.float64)
    csd = critique_severity_dispersion(rt.critique_severities)
    return RoundMetrics(
        round_index=rt.round_index,
        ace=ace(confs),
        ace_norm=ace_norm(confs),
        mean_confidence=float(np.mean(arr)) if arr.size else 0.0,
        max_confidence=float(np.max(arr)) if arr.size else 0.0,
        csd=csd,
        csd_max=critique_severity_max(rt.critique_severities),
        winner_index=rt.winner_index,
        consensus_score=rt.consensus_score,
    )


# ---------------------------------------------------------------------------
# M3 — Round-over-round convergence signals
# ---------------------------------------------------------------------------

def delta_ace(rounds: tuple[RoundMetrics, ...]) -> float:
    """ACE_norm(R) − ACE_norm(0). Negative = converging."""
    if len(rounds) < 2:
        return 0.0
    return rounds[-1].ace_norm - rounds[0].ace_norm


def delta_mean_confidence(rounds: tuple[RoundMetrics, ...]) -> float:
    """mean_conf(R) − mean_conf(0). Positive = team growing confident."""
    if len(rounds) < 2:
        return 0.0
    return rounds[-1].mean_confidence - rounds[0].mean_confidence


def winner_flip_rate(rounds: tuple[RoundMetrics, ...]) -> float:
    """Fraction of consecutive round-pairs where the winner changed.

    For R rounds the denominator is R-1; returns 0 if R < 2.
    """
    if len(rounds) < 2:
        return 0.0
    flips = sum(
        1 for r in range(1, len(rounds)) if rounds[r].winner_index != rounds[r - 1].winner_index
    )
    return flips / (len(rounds) - 1)


# ---------------------------------------------------------------------------
# M4 — Task Difficulty Index (TDI)
# ---------------------------------------------------------------------------

# Default TDI coefficients — sensible priors until calibration overrides them.
#   α  weight on final ACE_norm      (residual disagreement)
#   β  weight on final CSD           (residual critique dispersion)
#   γ  weight on (1 − clipped ΔC)    (lack of convergence)
#   δ  weight on WFR                 (instability)
DEFAULT_TDI_COEFFS: dict[str, float] = {"alpha": 0.35, "beta": 0.25, "gamma": 0.25, "delta": 0.15}


def tdi(
    rounds: tuple[RoundMetrics, ...],
    *,
    coeffs: dict[str, float] | None = None,
) -> float:
    """Composite Task Difficulty Index. Higher = harder task.

    Linearly combines the four signals; result is clipped to [0, 1].
    """
    if not rounds:
        return 0.0
    c = coeffs or DEFAULT_TDI_COEFFS
    last = rounds[-1]
    # ΔC normalised to [0, 1]: +1 (huge rise in mean conf) -> 0 (no difficulty),
    # 0 or negative (no improvement) -> 1 (full difficulty contribution).
    dc = delta_mean_confidence(rounds)
    dc_clipped = max(0.0, min(1.0, dc))
    lack_of_conv = 1.0 - dc_clipped
    wfr = winner_flip_rate(rounds)
    raw = (
        c["alpha"] * last.ace_norm
        + c["beta"] * last.csd
        + c["gamma"] * lack_of_conv
        + c["delta"] * wfr
    )
    return float(max(0.0, min(1.0, raw)))


# ---------------------------------------------------------------------------
# M4' — TDI with pairwise interaction terms (TDI2)
# ---------------------------------------------------------------------------

# Allowed interaction keys. Kept explicit to surface typos loudly.
_TDI2_INTERACTIONS: dict[str, tuple[str, str]] = {
    "ace_norm_x_lack_conv": ("ace_norm", "lack_conv"),
    "csd_x_wfr":            ("csd", "wfr"),
    "csd_x_ace_norm":       ("csd", "ace_norm"),
    "csd_x_lack_conv":      ("csd", "lack_conv"),
    "ace_norm_x_wfr":       ("ace_norm", "wfr"),
    "lack_conv_x_wfr":      ("lack_conv", "wfr"),
}


def tdi2(
    rounds: tuple[RoundMetrics, ...],
    *,
    coeffs: dict[str, float] | None = None,
    interaction_coeffs: dict[str, float] | None = None,
) -> float:
    """``TDI`` extended with pairwise interaction terms (see docs/SUPPLEMENT_DESIGN.md §1).

    When ``interaction_coeffs`` is empty or ``None`` this is exactly
    :func:`tdi` — TDI2 is a nested super-model of TDI.

    Supported interaction keys are the six pairwise products of the four
    base features ``{ace_norm, csd, lack_conv, wfr}``. Each product is
    clipped to ``[0, 1]`` before weighting; the final sum is clipped too.

    Raises
    ------
    ValueError
        If ``interaction_coeffs`` contains an unrecognised key.
    """
    if not rounds:
        return 0.0
    base = tdi(rounds, coeffs=coeffs)
    if not interaction_coeffs:
        return base

    last = rounds[-1]
    dc_clipped = max(0.0, min(1.0, delta_mean_confidence(rounds)))
    feats = {
        "ace_norm":  float(max(0.0, min(1.0, last.ace_norm))),
        "csd":       float(max(0.0, min(1.0, last.csd))),
        "lack_conv": 1.0 - dc_clipped,
        "wfr":       float(max(0.0, min(1.0, winner_flip_rate(rounds)))),
    }
    contribution = 0.0
    for key, weight in interaction_coeffs.items():
        if key not in _TDI2_INTERACTIONS:
            raise ValueError(
                f"unknown interaction term {key!r}; expected one of "
                f"{sorted(_TDI2_INTERACTIONS)}"
            )
        a, b = _TDI2_INTERACTIONS[key]
        contribution += weight * feats[a] * feats[b]
    return float(max(0.0, min(1.0, base + contribution)))


# ---------------------------------------------------------------------------
# Run-level roll-up
# ---------------------------------------------------------------------------

def run_metrics(trace: RunTrace, *, coeffs: dict[str, float] | None = None) -> RunMetrics:
    per_round = tuple(round_metrics(rt) for rt in trace.rounds)
    return RunMetrics(
        task_id=trace.task_id,
        per_round=per_round,
        delta_ace=delta_ace(per_round),
        delta_mean_confidence=delta_mean_confidence(per_round),
        winner_flip_rate=winner_flip_rate(per_round),
        final_consensus_score=per_round[-1].consensus_score if per_round else 0.0,
        tdi=tdi(per_round, coeffs=coeffs),
    )
