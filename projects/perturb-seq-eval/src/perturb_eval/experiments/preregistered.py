"""Pre-registered estimators for H1-H5 (``paper/PREREGISTRATION.md``).

Principal-ratified 2026-09-24 (decisions D-H4, D-EST, D-WHEN); implemented and
tested before any v0.6.0 sweep data exists. Every function is pure: it takes
already-parsed JSONL rows / per-task tables and returns plain dicts.

Component definitions (per lifecycle run; derived from :mod:`perturb_eval.metrics`)
=================================================================================

Round ``r``'s confidence vector ``C(r)`` is the ``llm_confidence`` of the run's
steps with ``round_index == r`` and ``source == "llm"`` (``fallback``, ``mock``
and unlabelled steps are excluded). The run's rounds are the distinct
``round_index`` values over all its steps; ``first``/``last`` are the min/max.
A round that a component reads with fewer than two LLM-sourced steps (or a
non-finite confidence) makes that component **undefined** for the run: it is
``None`` with a reason, and is excluded -- never imputed -- from the seed median.
ACE is also undefined when the final round's confidences sum to zero. Both ACE
checks run BEFORE ``metrics.ace_d`` is called (amendment 2, A2-10), so its
N = 0 error, N = 1 value 0.0 and all-zero value 0.0 never reach a component.

Gated components (amendment 2, ``prereg_version`` = ``v0.6.0-a2``):

==================  ===========================================================  ===================================
component           formula                                                      code
==================  ===========================================================  ===================================
``ace_norm``        ``ACE(C(last))`` = entropy of the direct simplex projection   ``metrics.ace_d`` (A2-10; the key
                    (no temperature) / ln N, on [0, 1]                           keeps the name ``ace_norm``)
``delta_c``         ``mean C(last) - mean C(first)``; UNDEFINED for a one-round   ``metrics.delta_mean_confidence``
                    run (not metrics.py's 0.0; principal ruling 2026-09-25)       (called only with >= 2 rounds)
``one_minus_        ``1 - delta_c``, UNCLIPPED, on [0, 2] (A2-11)                 ``per_run_components``
delta_c``
``tdi_lifecycle``   ``7/12 * ace_norm + 5/12 * one_minus_delta_c``, NO outer      ``tdi_lifecycle`` below
                    clip, on [0, 17/12] (A2-11)
==================  ===========================================================  ===================================

Descriptive only (``DESCRIPTIVE_COMPONENTS``: carried in the per-run and per-task
tables and reported beside H4, never entering a gate, test or fit):

=============================  ===============================================  ============================
``ace_norm_softmax``           softmax(tau=1) entropy of C(last) / ln N          ``metrics.ace_norm``
``one_minus_delta_c_clipped``  ``1 - min(max(delta_c, 0), 1)``                  the normalisation in
                                                                                ``metrics.tdi``
=============================  ===============================================  ============================

``tdi_lifecycle``'s weights are ``metrics.DEFAULT_TDI_COEFFS`` alpha (0.35, on
ACE) and gamma (0.25, on 1 - delta_c) renormalised over the two:
``0.35/0.60 = 7/12`` and ``0.25/0.60 = 5/12``, carried over unchanged by
amendment 2. It is a score on [0, 17/12], not an index on [0, 1], and a DIFFERENT quantity from
the four-component TDI of ``metrics.tdi``: CSD (critique-matrix variance) and
WFR (winner flip rate) are structurally undefined for the five-role lifecycle,
which records neither a critique matrix nor a winner, so the four-component TDI
is not evaluated.

Estimators (D-EST)
==================

* unit = task; per task, each component and the lifecycle ``final_msd_topk``
  are the median over the task's seeds (``per_task_table``);
* Spearman rho with average-rank ties; percentile bootstrap CI over TASKS,
  ``B = 10_000`` resamples, fixed ``seed = 2026`` (``spearman_with_ci``);
  resamples whose ranks are constant are dropped and counted;
* H4 (``h4``): rho per component WITHIN Adamson and WITHIN Norman (6 tests);
  the pooled rho is descriptive only; no in-sample calibration;
* H5 (``h5``): ridge on Adamson only, ``alpha = 1.0``, applied unchanged to Norman;
* H1/H2 (``h1_h2_stats``); H3 (``architect_backbone_stats`` + ``h3_from_stats``):
  entropy of the Architect's STATED backbone over LLM-sourced Architect steps,
  ceiling ln|BACKBONE_MENU|; the executed backbone is reported alongside and
  does not gate (amendment 2, A2-6).

Every gate returns ``{"gate", "value", "threshold", "pass", "evaluable",
"reason", ...}``; ``pass`` is ``None`` whenever the gate is not evaluable
(never ``False`` by default). A gate needs at least ``MIN_TASKS = 3`` tasks.
"""

from __future__ import annotations

import math
import statistics
from collections import Counter, defaultdict
from typing import Any, Iterable, Mapping, Sequence, get_args

import numpy as np

from perturb_eval import metrics
from perturb_eval.agentic_lifecycle.proposal_schema import BackboneName
from perturb_eval.types import RoundMetrics

BOOTSTRAP_B: int = 10_000
BOOTSTRAP_SEED: int = 2026
CI_LEVEL: float = 0.95
MIN_TASKS: int = 3
RIDGE_ALPHA: float = 1.0

H1_THRESHOLD = 0.20
H2_THRESHOLD = 0.30
H3_THRESHOLD = 0.5
H4_THRESHOLD = 0.5
H5_THRESHOLD = 0.4

_W_SUM = metrics.DEFAULT_TDI_COEFFS["alpha"] + metrics.DEFAULT_TDI_COEFFS["gamma"]
TDI_LIFECYCLE_WEIGHTS: dict[str, float] = {
    "ace_norm": metrics.DEFAULT_TDI_COEFFS["alpha"] / _W_SUM,
    "one_minus_delta_c": metrics.DEFAULT_TDI_COEFFS["gamma"] / _W_SUM,
}
H4_COMPONENTS: tuple[str, ...] = ("ace_norm", "one_minus_delta_c", "tdi_lifecycle")
H4_DATASETS: tuple[str, ...] = ("adamson_full", "norman")
SINGLE_ROUND_REASON = "single-round run: ΔC requires >= 2 rounds"
H5_FEATURES: tuple[str, ...] = ("ace_norm", "one_minus_delta_c")
# Amendment 2 (A2-10, A2-11): reported beside the gated components; enter no gate, test or fit.
DESCRIPTIVE_COMPONENTS: tuple[str, ...] = ("ace_norm_softmax", "one_minus_delta_c_clipped")
ZERO_SUM_REASON = "round {r}: LLM-sourced confidences sum to zero (ACE undefined)"
# Amendment 2 (A2-6): the pinned Architect menu; H3's ceiling is ln|menu|. Any
# change to the menu is a measurand change.
BACKBONE_MENU: tuple[str, ...] = tuple(get_args(BackboneName))
MILLER_MADOW_MAX_N: int = 50
STRUCTURALLY_UNDEFINED: dict[str, str] = {
    "csd": "critique-matrix variance: the five-role lifecycle records no critique matrix",
    "wfr": "winner flip rate: the five-role lifecycle has no per-round winner",
}


# ---------------------------------------------------------------------------
# gate-result shape
# ---------------------------------------------------------------------------

def _gate(gate: str, value: Any, threshold: float, passed: bool | None,
          reason: str | None, **extra: Any) -> dict:
    evaluable = passed is not None
    return {"gate": gate, "value": value, "threshold": threshold,
            "pass": passed if evaluable else None, "evaluable": evaluable,
            "reason": reason, **extra}


def not_licensed(result: dict, why: str) -> dict:
    """Return ``result`` with its gate withdrawn (diagnostic summaries)."""
    return {**result, "pass": None, "evaluable": False, "reason": why}


# ---------------------------------------------------------------------------
# per-run components
# ---------------------------------------------------------------------------

def tdi_lifecycle(ace_norm: float, one_minus_delta_c: float) -> float:
    """Default-weighted two-component TDI, with NO outer clip (amendment 2, A2-11).

    ``7/12 * ACE + 5/12 * (1 - ΔC)`` with ACE on [0, 1] and unclipped 1 - ΔC on
    [0, 2], so the score lies on [0, 17/12]; it is not an index on [0, 1].
    """
    return float(TDI_LIFECYCLE_WEIGHTS["ace_norm"] * ace_norm
                 + TDI_LIFECYCLE_WEIGHTS["one_minus_delta_c"] * one_minus_delta_c)


def _is_llm(step: Mapping) -> bool:
    return step.get("source") == "llm"


def _round_vector(steps: Sequence[Mapping], r: int) -> tuple[tuple[float, ...] | None, str | None]:
    confs = [s.get("llm_confidence") for s in steps
             if s.get("round_index") == r and _is_llm(s)]
    if len(confs) < 2:
        return None, f"round {r}: {len(confs)} LLM-sourced step(s) (< 2 required)"
    try:
        vec = tuple(float(c) for c in confs)
    except (TypeError, ValueError):
        return None, f"round {r}: non-numeric llm_confidence"
    if not all(math.isfinite(c) for c in vec):
        return None, f"round {r}: non-finite llm_confidence"
    return vec, None


def _round_metrics(r: int, vec: tuple[float, ...]) -> RoundMetrics:
    # CSD / winner fields are structurally undefined here (NaN / -1); only the
    # confidence-derived fields are read by the functions this module calls.
    return RoundMetrics(round_index=r, ace=metrics.ace(vec), ace_norm=metrics.ace_norm(vec),
                        mean_confidence=float(np.mean(vec)), max_confidence=float(max(vec)),
                        csd=float("nan"), csd_max=float("nan"), winner_index=-1,
                        consensus_score=float("nan"))


def per_run_components(run: Mapping) -> dict:
    """``{ace_norm, delta_c, one_minus_delta_c, tdi_lifecycle, ace_norm_softmax,
    one_minus_delta_c_clipped, n_rounds, reasons}``.

    ``ace_norm`` is ``metrics.ace_d(C(last))`` (A2-10); ``one_minus_delta_c`` is
    ``1 - ΔC`` unclipped (A2-11). ``ace_norm_softmax`` and
    ``one_minus_delta_c_clipped`` are descriptive only. A component is ``None``
    when a round it reads is undefined; ``reasons`` maps each ``None``
    component to why.
    """
    steps = list(run.get("steps") or [])
    rounds = sorted({int(s["round_index"]) for s in steps if s.get("round_index") is not None})
    out: dict[str, Any] = {"ace_norm": None, "delta_c": None, "one_minus_delta_c": None,
                           "tdi_lifecycle": None, "ace_norm_softmax": None,
                           "one_minus_delta_c_clipped": None, "n_rounds": len(rounds),
                           "reasons": {}}
    if not rounds:
        for k in (*H4_COMPONENTS, *DESCRIPTIVE_COMPONENTS):
            out["reasons"][k] = "run has no steps"
        return out
    first, last = rounds[0], rounds[-1]
    v_last, why_last = _round_vector(steps, last)
    v_first, why_first = _round_vector(steps, first)

    # A2-10: both checks run BEFORE metrics.ace_d is called. _round_vector has
    # already refused < 2 LLM-sourced steps (ace_d's N = 0 error / N = 1 -> 0.0).
    if v_last is None:
        out["reasons"]["ace_norm"] = why_last
        out["reasons"]["ace_norm_softmax"] = why_last
    else:
        out["ace_norm_softmax"] = float(metrics.ace_norm(v_last))
        if sum(v_last) <= metrics._EPS:  # ace_d's all-zero convention (0.0) must not reach a component
            out["reasons"]["ace_norm"] = ZERO_SUM_REASON.format(r=last)
        else:
            out["ace_norm"] = float(metrics.ace_d(v_last))

    if first == last:
        # Principal ruling 2026-09-25: NOT metrics.py's ΔC = 0 convention,
        # which would score immediate acceptance as maximal difficulty.
        out["reasons"]["one_minus_delta_c"] = SINGLE_ROUND_REASON
        out["reasons"]["one_minus_delta_c_clipped"] = SINGLE_ROUND_REASON
    elif v_first is None or v_last is None:
        out["reasons"]["one_minus_delta_c"] = why_first or why_last
        out["reasons"]["one_minus_delta_c_clipped"] = why_first or why_last
    else:
        rms = (_round_metrics(first, v_first), _round_metrics(last, v_last))
        dc = float(metrics.delta_mean_confidence(rms))
        out["delta_c"] = dc
        out["one_minus_delta_c"] = 1.0 - dc  # A2-11: unclipped, on [0, 2]
        out["one_minus_delta_c_clipped"] = 1.0 - max(0.0, min(1.0, dc))  # descriptive only

    if out["ace_norm"] is None or out["one_minus_delta_c"] is None:
        out["reasons"]["tdi_lifecycle"] = (
            out["reasons"].get("one_minus_delta_c") or out["reasons"].get("ace_norm"))
    else:
        out["tdi_lifecycle"] = tdi_lifecycle(out["ace_norm"], out["one_minus_delta_c"])
    return out


def _finite(v: Any) -> bool:
    try:
        return math.isfinite(float(v))
    except (TypeError, ValueError):
        return False


def task_key(row: Mapping) -> tuple[str, str] | None:
    """``(dataset, task)`` for a trainer (``task``) or lifecycle (``task_id``) row;
    ``None`` when the row names no task. The ONE task-identity helper (QG C5/C27):
    a gene symbol can be a task in both Adamson and Norman (e.g. SNAI1, SPI1),
    so a bare task name is never an identity."""
    task = row.get("task_id", row.get("task"))
    if task is None:
        return None
    return str(row.get("dataset", "unknown")), str(task)


def per_task_table(lifecycle_rows: Iterable[Mapping]) -> list[dict]:
    """One row per ``(dataset, task)``: seed medians of each component and of MSD.

    Undefined components and non-finite ``final_msd_topk`` values are excluded
    from their median (``n_seeds`` records how many entered; ``undefined``
    lists the excluded seeds with reasons). A median over zero seeds is ``None``.
    """
    groups: dict[tuple[str, str], list[Mapping]] = defaultdict(list)
    for r in lifecycle_rows:
        key = task_key(r)
        if key is None:
            continue
        groups[key].append(r)
    table = []
    for (dataset, task) in sorted(groups):
        runs = groups[(dataset, task)]
        vals: dict[str, list[float]] = {k: [] for k in (*H4_COMPONENTS, *DESCRIPTIVE_COMPONENTS,
                                                        "msd")}
        undefined: dict[str, list[dict]] = {k: [] for k in H4_COMPONENTS}
        n_single = 0
        for run in runs:
            comp = per_run_components(run)
            n_single += comp["n_rounds"] == 1
            for k in H4_COMPONENTS:
                if comp[k] is None:
                    undefined[k].append({"seed": run.get("seed"), "reason": comp["reasons"][k]})
                else:
                    vals[k].append(comp[k])
            for k in DESCRIPTIVE_COMPONENTS:  # descriptive only: carried, never gated
                if comp[k] is not None:
                    vals[k].append(comp[k])
            if _finite(run.get("final_msd_topk")):
                vals["msd"].append(float(run["final_msd_topk"]))
        row: dict[str, Any] = {"task": task, "dataset": dataset}
        for k, v in vals.items():
            row[k] = float(statistics.median(v)) if v else None
        row["n_seeds"] = {k: len(v) for k, v in vals.items()}
        row["n_runs"] = len(runs)
        row["n_single_round_runs"] = n_single
        row["undefined"] = {k: v for k, v in undefined.items() if v}
        table.append(row)
    return table


# ---------------------------------------------------------------------------
# Spearman with a bootstrap CI over tasks
# ---------------------------------------------------------------------------

def _avg_rank(a: np.ndarray) -> np.ndarray:
    _, inv, cnt = np.unique(a, return_inverse=True, return_counts=True)
    cum = np.cumsum(cnt)
    return (cum - (cnt - 1) / 2.0)[inv]


def rho(x: np.ndarray, y: np.ndarray) -> float | None:
    """Average-rank Spearman rho; ``None`` when either rank vector is constant."""
    rx, ry = _avg_rank(x), _avg_rank(y)
    rx, ry = rx - rx.mean(), ry - ry.mean()
    den = math.sqrt(float(rx @ rx) * float(ry @ ry))
    if den == 0.0:
        return None
    return float(rx @ ry) / den


# Kept: PREREGISTRATION.md cites ``preregistered._rho`` by name.
_rho = rho


def _percentile_ci(stats: list[float]) -> tuple[float | None, float | None]:
    if not stats:
        return None, None
    tail = (1.0 - CI_LEVEL) / 2.0 * 100.0
    lo, hi = np.percentile(np.asarray(stats), [tail, 100.0 - tail])
    return float(lo), float(hi)


def spearman_with_ci(x: Sequence[float], y: Sequence[float], *,
                     B: int = BOOTSTRAP_B, seed: int = BOOTSTRAP_SEED) -> dict:
    """``{rho, n, ci_low, ci_high, B, seed, n_boot_valid, reason}``.

    Percentile bootstrap: ``B`` resamples of task indices with replacement from
    ``numpy.random.default_rng(seed)``; resamples with constant ranks in either
    variable are dropped (``n_boot_valid`` counts the rest). ``rho`` is ``None``
    for ``n < MIN_TASKS`` or constant input.
    """
    xa, ya = np.asarray(x, dtype=np.float64), np.asarray(y, dtype=np.float64)
    if xa.shape != ya.shape:
        raise ValueError(f"x and y differ in length: {xa.shape} vs {ya.shape}")
    n = int(xa.size)
    out = {"rho": None, "n": n, "ci_low": None, "ci_high": None, "B": B, "seed": seed,
           "n_boot_valid": 0, "reason": None}
    if n < MIN_TASKS:
        out["reason"] = f"n={n} < {MIN_TASKS} tasks"
        return out
    rho_hat = rho(xa, ya)
    if rho_hat is None:
        out["reason"] = "constant ranks: Spearman rho undefined"
        return out
    rng = np.random.default_rng(seed)
    boots: list[float] = []
    for idx in rng.integers(0, n, size=(B, n)):
        r = rho(xa[idx], ya[idx])
        if r is not None:
            boots.append(r)
    out["rho"] = rho_hat
    out["n_boot_valid"] = len(boots)
    out["ci_low"], out["ci_high"] = _percentile_ci(boots)
    return out


def _median_ci(v: np.ndarray, *, B: int, seed: int) -> tuple[float | None, float | None]:
    rng = np.random.default_rng(seed)
    boots = [float(np.median(v[idx])) for idx in rng.integers(0, v.size, size=(B, v.size))]
    return _percentile_ci(boots)


# ---------------------------------------------------------------------------
# H1 / H2
# ---------------------------------------------------------------------------

def _describe(v: np.ndarray, threshold: float) -> dict:
    if v.size == 0:
        return {"n": 0, "median": None, "iqr": None, "max": None, "fraction_over_gate": None}
    q1, q3 = np.percentile(v, [25, 75])
    return {"n": int(v.size), "median": float(np.median(v)), "iqr": [float(q1), float(q3)],
            "max": float(v.max()), "fraction_over_gate": float(np.mean(v > threshold))}


def h1_h2_stats(best_by_task: Mapping[str, float], threshold: float, *, gate: str,
                strata: Mapping[str, str] | None = None,
                B: int = BOOTSTRAP_B, seed: int = BOOTSTRAP_SEED) -> dict:
    """Oracle MSD per task (min over the distinct backbone x R configurations run,
    amendment 2, A2-4) -> median gate (``median < threshold``).

    Reports n, median, IQR (25th/75th percentiles), max, fraction of tasks
    with MSD strictly above ``threshold``, a percentile bootstrap CI of the
    median over tasks, and the same descriptives per stratum when ``strata``
    (task -> stratum name) is given.
    """
    tasks = sorted(t for t, m in best_by_task.items() if _finite(m))
    v = np.asarray([float(best_by_task[t]) for t in tasks], dtype=np.float64)
    d = _describe(v, threshold)
    ci_low = ci_high = None
    if v.size >= MIN_TASKS:
        ci_low, ci_high = _median_ci(v, B=B, seed=seed)
        passed, reason = bool(d["median"] < threshold), None
    else:
        passed, reason = None, f"n={v.size} < {MIN_TASKS} tasks"
    extra: dict[str, Any] = {k: d[k] for k in ("n", "iqr", "max", "fraction_over_gate")}
    extra.update(ci_low=ci_low, ci_high=ci_high, B=B, seed=seed)
    if strata is not None:
        groups: dict[str, list[float]] = defaultdict(list)
        for t, m in zip(tasks, v):
            groups[strata.get(t, "unassigned")].append(float(m))
        extra["strata"] = {s: _describe(np.asarray(g), threshold) for s, g in sorted(groups.items())}
    return _gate(gate, d["median"], threshold, passed, reason, **extra)


# ---------------------------------------------------------------------------
# H3
# ---------------------------------------------------------------------------

def _plugin_entropy(counts: Mapping[str, int]) -> float | None:
    """Plug-in (maximum-likelihood) Shannon entropy in nats; ``None`` for N = 0."""
    n = sum(counts.values())
    if n == 0:
        return None
    return float(-sum((c / n) * math.log(c / n) for c in counts.values() if c > 0))


def _miller_madow(counts: Mapping[str, int]) -> float | None:
    """``H + (K - 1) / (2N)`` for ``N < MILLER_MADOW_MAX_N`` (A2-6), else ``None``.

    K is the size of the pinned menu (``len(BACKBONE_MENU)``), as in A2-6's
    worked example (K = 3), not the number of observed categories."""
    n = sum(counts.values())
    h = _plugin_entropy(counts)
    if h is None or n >= MILLER_MADOW_MAX_N:
        return None
    k = len(BACKBONE_MENU)
    return h + (k - 1) / (2 * n)


def _step_field(step: Mapping, name: str) -> Any:
    """``step[name]`` if recorded on the step, else ``proposal_content[name]``."""
    if step.get(name) is not None:
        return step[name]
    return (step.get("proposal_content") or {}).get(name)


def architect_backbone_stats(steps: Iterable[Mapping]) -> dict:
    """H3 inputs over the LLM-sourced Architect steps in ``steps`` (A2-6).

    * STATED backbone (``backbone_stated``; gates H3): a step whose stated
      backbone is missing or off ``BACKBONE_MENU`` is a schema failure -- never
      defaulted, never counted (``n_missing_stated``, ``n_off_menu_stated``).
    * EXECUTED backbone (``backbone_executed``, or ``backbone_used``; the backbone
      that ran after the Validator's delta): reported alongside, never gates.

    Steps whose ``source`` is not ``"llm"`` and non-Architect steps are ignored.
    """
    stated: Counter[str] = Counter()
    executed: Counter[str] = Counter()
    off_menu: Counter[str] = Counter()
    by_model: dict[str, Counter[str]] = defaultdict(Counter)
    n_llm = n_missing = n_ne = n_missing_exec = 0
    for s in steps:
        if s.get("agent_name") != "Architect" or not _is_llm(s):
            continue
        n_llm += 1
        st = _step_field(s, "backbone_stated")
        ex = _step_field(s, "backbone_executed")
        if ex is None:
            ex = _step_field(s, "backbone_used")
        if ex is None:
            n_missing_exec += 1
        else:
            executed[str(ex)] += 1
        if st is None:
            n_missing += 1
            continue
        if st not in BACKBONE_MENU:
            off_menu[str(st)] += 1
            continue
        stated[st] += 1
        by_model[str(s.get("model_id"))][st] += 1
        if ex is not None and ex != st:
            n_ne += 1
    return {
        "menu": list(BACKBONE_MENU),
        "n_llm_architect_steps": n_llm,
        "n_counted": sum(stated.values()),
        "stated_counts": dict(sorted(stated.items())),
        "entropy_stated_nats": _plugin_entropy(stated),
        "miller_madow_stated_nats": _miller_madow(stated),
        "executed_counts": dict(sorted(executed.items())),
        "entropy_executed_nats": _plugin_entropy(executed),
        "n_executed_ne_stated": n_ne,
        "n_missing_executed": n_missing_exec,
        "n_missing_stated": n_missing,
        "n_off_menu_stated": sum(off_menu.values()),
        "off_menu_values": dict(sorted(off_menu.items())),
        "by_model_id": {m: {"n": sum(c.values()), "pick_counts": dict(sorted(c.items())),
                            "entropy_nats": _plugin_entropy(c),
                            "miller_madow_nats": _miller_madow(c)}
                        for m, c in sorted(by_model.items())},
    }


def h3(entropy_nats: float | None, *, pick_counts: Mapping[str, int], n_llm_steps: int,
       n_distinct_model_ids: int, threshold: float = H3_THRESHOLD,
       schema_failure: str | None = None, **descriptive: Any) -> dict:
    """Entropy of the Architect's STATED backbone picks as a gate (A2-6).

    ``ceiling_nats`` is ln|BACKBONE_MENU|, read from the pinned menu.
    ``schema_failure`` (a reason) withdraws the gate: a missing or off-menu
    stated backbone on an LLM-sourced step makes the run invalid (A2-1/A2-6).
    ``descriptive`` fields (executed picks etc.) are carried and never gate.
    """
    if schema_failure is not None:
        passed, reason = None, schema_failure
    elif entropy_nats is None:
        passed, reason = None, "no LLM-sourced Architect step carries a stated backbone"
    else:
        passed, reason = bool(entropy_nats >= threshold), None
    return _gate("H3", entropy_nats, threshold, passed, reason,
                 pick_counts=dict(pick_counts), n_llm_architect_steps=n_llm_steps,
                 n_distinct_model_ids=n_distinct_model_ids, menu=list(BACKBONE_MENU),
                 ceiling_nats=math.log(len(BACKBONE_MENU)), **descriptive)


def h3_from_stats(stats: Mapping[str, Any], *, n_distinct_model_ids: int | None = None,
                  threshold: float = H3_THRESHOLD) -> dict:
    """H3 gate from :func:`architect_backbone_stats`: gates on the stated
    entropy; executed picks, the stated != executed count, schema-failure
    counts and the per-``model_id`` breakdown are reported alongside."""
    n_bad = stats["n_missing_stated"] + stats["n_off_menu_stated"]
    failure = None
    if n_bad:
        failure = (f"schema failure (A2-1/A2-6): {stats['n_missing_stated']} LLM-sourced Architect "
                   f"step(s) with no stated backbone and {stats['n_off_menu_stated']} with an "
                   f"off-menu stated backbone {stats['off_menu_values']}; never defaulted or "
                   "counted, and the run is invalid")
    if n_distinct_model_ids is None:
        n_distinct_model_ids = len(stats["by_model_id"])
    return h3(stats["entropy_stated_nats"], pick_counts=stats["stated_counts"],
              n_llm_steps=stats["n_llm_architect_steps"],
              n_distinct_model_ids=n_distinct_model_ids, threshold=threshold,
              schema_failure=failure,
              n_counted=stats["n_counted"],
              miller_madow_nats=stats["miller_madow_stated_nats"],
              executed_pick_counts=stats["executed_counts"],
              entropy_executed_nats=stats["entropy_executed_nats"],
              n_executed_ne_stated=stats["n_executed_ne_stated"],
              n_missing_executed=stats["n_missing_executed"],
              n_missing_stated=stats["n_missing_stated"],
              n_off_menu_stated=stats["n_off_menu_stated"],
              off_menu_values=stats["off_menu_values"],
              by_model_id=stats["by_model_id"])


# ---------------------------------------------------------------------------
# H4
# ---------------------------------------------------------------------------

def _pairs(table: Sequence[Mapping], key: str) -> tuple[list[float], list[float]]:
    rows = [r for r in table if r.get(key) is not None and r.get("msd") is not None]
    return [float(r[key]) for r in rows], [float(r["msd"]) for r in rows]


def _exclusions(table: Sequence[Mapping]) -> dict:
    """Per component: runs left undefined (and how many were single-round), and
    tasks with no defined value (or no finite MSD) that drop out of its rho."""
    out = {}
    for k in H4_COMPONENTS:
        undef = [u for r in table for u in (r.get("undefined") or {}).get(k, [])]
        out[k] = {"runs_undefined": len(undef),
                  "runs_single_round": sum(u["reason"] == SINGLE_ROUND_REASON for u in undef),
                  "tasks_dropped": sum(r.get(k) is None or r.get("msd") is None for r in table)}
    return out


def h4(task_table: Sequence[Mapping], *, B: int = BOOTSTRAP_B, seed: int = BOOTSTRAP_SEED,
       threshold: float = H4_THRESHOLD) -> dict:
    """Spearman rho(component, lifecycle MSD) for each of ``H4_COMPONENTS``,
    computed WITHIN each of ``H4_DATASETS`` separately: 6 tests (default
    weights, no in-sample calibration). The rho over all tasks pooled is
    reported as ``pooled_descriptive`` and never gates.

    PASS if any of the 6 evaluable rho > threshold; FAIL only if all 6 are
    evaluable and none passes; otherwise UNEVALUATED.
    """
    per_dataset, exclusions = {}, {}
    for ds in H4_DATASETS:
        rows = [r for r in task_table if r.get("dataset") == ds]
        per_dataset[ds] = {k: spearman_with_ci(*_pairs(rows, k), B=B, seed=seed)
                           for k in H4_COMPONENTS}
        exclusions[ds] = _exclusions(rows)
    pooled = {k: spearman_with_ci(*_pairs(task_table, k), B=B, seed=seed) for k in H4_COMPONENTS}
    # A2-10 / A2-11: the softmax ACE and the clipped 1-ΔC are reported beside the
    # gated tests, per dataset, and never enter the gate.
    descriptive = {ds: {k: spearman_with_ci(*_pairs([r for r in task_table
                                                      if r.get("dataset") == ds], k),
                                            B=B, seed=seed)
                        for k in DESCRIPTIVE_COMPONENTS}
                   for ds in H4_DATASETS}
    rhos = {(ds, k): c["rho"] for ds, cs in per_dataset.items() for k, c in cs.items()
            if c["rho"] is not None}
    n_tests = len(H4_DATASETS) * len(H4_COMPONENTS)
    best = max(rhos.values()) if rhos else None
    if any(r > threshold for r in rhos.values()):
        passed, reason = True, None
    elif len(rhos) == n_tests:
        passed, reason = False, None
    else:
        missing = {f"{ds}:{k}": per_dataset[ds][k]["reason"] for ds in H4_DATASETS
                   for k in H4_COMPONENTS if (ds, k) not in rhos}
        passed, reason = None, f"test(s) not evaluable and none passes: {missing}"
    # CTO #269 (b): report ALL SIX with their n regardless of outcome (pass, fail or undefined), so a
    # single-test PASS is self-evident and selective reporting is structurally impossible.
    all_six = [
        {"dataset": ds, "component": k, "rho": c["rho"], "n": c["n"],
         "ci_low": c["ci_low"], "ci_high": c["ci_high"], "reason": c["reason"],
         "passes": None if c["rho"] is None else bool(c["rho"] > threshold)}
        for ds in H4_DATASETS for k, c in ((k, per_dataset[ds][k]) for k in H4_COMPONENTS)
    ]
    return _gate("H4", best, threshold, passed, reason, per_dataset=per_dataset,
                 all_six=all_six, n_tests_passing=sum(1 for r in all_six if r["passes"]),
                 pooled_descriptive=pooled, descriptive=descriptive,
                 exclusions=exclusions, n_tests=n_tests,
                 structurally_undefined=dict(STRUCTURALLY_UNDEFINED),
                 tdi_lifecycle_weights=dict(TDI_LIFECYCLE_WEIGHTS),
                 n_tasks=len(task_table))


# ---------------------------------------------------------------------------
# H5
# ---------------------------------------------------------------------------

def fit_ridge(X: Sequence[Sequence[float]], y: Sequence[float], *, alpha: float) -> dict:
    """Closed-form ridge on column-standardised features, centred target.

    ``w = (Z'Z + alpha I)^-1 Z'(y - mean y)`` with ``Z = (X - mean) / sd``
    (population sd). A constant column gets weight 0 (its sd is stored as 1).
    Returns ``{weights, mean, sd, intercept, constant_columns}`` (numpy arrays).
    """
    Xa, ya = np.asarray(X, dtype=np.float64), np.asarray(y, dtype=np.float64)
    mu = Xa.mean(axis=0)
    sd = Xa.std(axis=0)
    const = sd == 0.0
    sd = np.where(const, 1.0, sd)
    Z = (Xa - mu) / sd
    Z[:, const] = 0.0
    w = np.linalg.solve(Z.T @ Z + alpha * np.eye(Z.shape[1]), Z.T @ (ya - ya.mean()))
    return {"weights": w, "mean": mu, "sd": sd, "intercept": float(ya.mean()),
            "constant_columns": [int(i) for i in np.flatnonzero(const)]}


def _complete(table: Sequence[Mapping]) -> list[Mapping]:
    return [r for r in table
            if r.get("msd") is not None and all(r.get(k) is not None for k in H5_FEATURES)]


def h5(adamson_table: Sequence[Mapping], norman_table: Sequence[Mapping], *,
       alpha: float = RIDGE_ALPHA, B: int = BOOTSTRAP_B, seed: int = BOOTSTRAP_SEED,
       threshold: float = H5_THRESHOLD) -> dict:
    """Fit ridge TDI weights on Adamson (target: per-task lifecycle MSD), apply
    them unchanged to Norman, gate on Spearman rho(Norman TDI, Norman MSD).

    Norman TDI = sum_k w_k (x_k - mean_k) / sd_k with Adamson's mean/sd; the
    intercept is omitted (it does not change ranks).
    """
    ad, no = _complete(adamson_table), _complete(norman_table)
    base = {"n_fit": len(ad), "n": len(no), "alpha": alpha, "features": list(H5_FEATURES)}
    if len(ad) < MIN_TASKS:
        return _gate("H5", None, threshold, None,
                     f"Adamson fit set n={len(ad)} < {MIN_TASKS} tasks", **base)
    fit = fit_ridge([[float(r[k]) for k in H5_FEATURES] for r in ad],
                    [float(r["msd"]) for r in ad], alpha=alpha)
    w, mu, sd = fit["weights"], fit["mean"], fit["sd"]
    names = list(H5_FEATURES)
    base.update(weights=dict(zip(names, map(float, w))),
                standardise_mean=dict(zip(names, map(float, mu))),
                standardise_sd=dict(zip(names, map(float, sd))),
                intercept=fit["intercept"],
                constant_features=[names[i] for i in fit["constant_columns"]])
    norman_tdi = [float(sum(w[i] * (float(r[k]) - mu[i]) / sd[i] for i, k in enumerate(names)))
                  for r in no]
    base["norman_tasks"] = [r.get("task") for r in no]
    base["norman_tdi"] = norman_tdi
    corr = spearman_with_ci(norman_tdi, [float(r["msd"]) for r in no], B=B, seed=seed)
    base.update(ci_low=corr["ci_low"], ci_high=corr["ci_high"], B=B, seed=seed,
                n_boot_valid=corr["n_boot_valid"])
    if corr["rho"] is None:
        return _gate("H5", None, threshold, None, corr["reason"], **base)
    return _gate("H5", corr["rho"], threshold, bool(corr["rho"] > threshold), None, **base)


def tally(results: Mapping[str, Mapping]) -> dict:
    """PASS / FAIL / UNEVALUATED counts, always out of the number of gates."""
    t = {"PASS": 0, "FAIL": 0, "UNEVALUATED": 0, "out_of": len(results)}
    for r in results.values():
        t["UNEVALUATED" if r["pass"] is None else ("PASS" if r["pass"] else "FAIL")] += 1
    return t
