"""Generate the EXPLORATORY (not pre-registered) v0.6.0 analysis: JSON record and LaTeX macros.

From round 1 on, each agent's prompt carries the previous round's held-out error
(``last_msd``, ``agentic_lifecycle/loop.py``), so the confidence drop ``1 - delta_c`` that the
pre-registered trace-feature test reads is stated after that feedback. The pre-registered
outcomes are not re-decided here; this script adds labelled exploratory quantities beside
them. It reads ONLY ``artifacts/v0.6.0/{lifecycle_runs.jsonl,trainer_runs.jsonl,summary.json,
provenance.json}`` and writes

* ``paper/data/exploratory_v060.json`` -- every computed value, the run id, each input's sha256;
* ``paper/sections/generated_exploratory.tex`` -- one ``\\expl...`` macro per printed value.

The Spearman estimate and the task bootstrap are the pre-registered ones, imported from
``perturb_eval.experiments.preregistered`` (``rho``, ``spearman_with_ci``, ``per_task_table``);
the unit is the task, each task value is the median over its seeds, and every estimate is
computed within one screen. Before anything is emitted the script must reproduce the committed
``one_minus_delta_c`` correlation of both screens (``summary.json``), or it raises.

No number is typed into a .tex file by hand (CTO #491); ``--check`` regenerates and fails if a
committed output differs. The macro file is compared as text; the JSON is compared value by
value with a relative tolerance of ``JSON_REL_TOL``, because a different numpy/BLAS build can
move a float by a few ulp (HACA-121) and that is not staleness.

    .venv/bin/python scripts/paper/fill_v060_exploratory.py [--check]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fill_v060_numbers import ENSUREMATH_NEG, SAFE_VALUE, f  # one formatting helper

from perturb_eval import metrics
from perturb_eval.experiments import preregistered as pre

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUTS = ("lifecycle_runs.jsonl", "trainer_runs.jsonl", "summary.json", "provenance.json")
DS = {"adamson_full": "Ada", "norman": "Nor"}
ROLES = {
    "DataCurator": "Curator",
    "Literature": "Literature",
    "Architect": "Architect",
    "Trainer": "Trainer",
    "Validator": "Validator",
}
ROUNDS = (0, 1, 2)
ROUND_WORDS = ("Zero", "One", "Two")
H4_KEY = "one_minus_delta_c"
SCATTER_KEYS = ("ace_norm", "one_minus_delta_c", "tdi_lifecycle")
N_ANALYSES = 8  # the families (a)-(h) below
REPRODUCTION_ABS_TOL = 1e-9
JSON_REL_TOL = 1e-9


def _sha256(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _median(values: list[float], what: str) -> float:
    if not values:
        raise ValueError(f"{what}: no defined seed value; the manuscript cannot print n/a")
    return float(statistics.median(values))


def _corr(x: list[float], y: list[float], what: str) -> dict:
    """The pre-registered Spearman with its task bootstrap; an undefined estimate is an error."""
    c = pre.spearman_with_ci(x, y)
    if c["rho"] is None or c["ci_low"] is None or c["ci_high"] is None:
        raise ValueError(f"{what}: Spearman rho is undefined ({c['reason']})")
    return {
        "kind": "spearman",
        "rho": c["rho"],
        "n": c["n"],
        "ci_low": c["ci_low"],
        "ci_high": c["ci_high"],
        "n_boot_valid": c["n_boot_valid"],
    }


def _run_features(run: dict) -> dict:
    """Per-run inputs of the exploratory quantities (LLM-sourced steps only, as in H4)."""
    steps = run["steps"]
    rounds = sorted({int(s["round_index"]) for s in steps})
    msd = [float(v) for v in run["msd_per_round"]]
    if rounds != list(ROUNDS) or len(msd) != len(ROUNDS):
        raise ValueError(f"{run.get('task_id')}: expected rounds 0, 1, 2; got {rounds}")
    if msd[-1] != float(run["final_msd_topk"]):
        raise ValueError(f"{run.get('task_id')}: final_msd_topk is not the last round's MSD")
    # The last round's MSD is checked through the pre-registered table (an undefined value
    # raises in ``_task_rows``). Rounds 0 and 1 are read only here, so a non-finite value
    # (a failed fit is recorded as inf) must stop the build instead of reaching a median.
    for r in ROUNDS[:-1]:
        if not math.isfinite(msd[r]):
            raise ValueError(
                f"{run.get('task_id')}: round-{r} MSD is not finite ({msd[r]!r}); "
                "the exploratory quantities need a finite held-out error in every round"
            )
    out: dict = {"msd": msd, "mean_conf": [], "role_conf": {role: [] for role in ROLES}}
    for r in ROUNDS:
        vec, why = pre._round_vector(steps, r)  # the pre-registered C(r)
        if vec is None:
            raise ValueError(f"{run.get('task_id')}: {why}")
        out["mean_conf"].append(float(np.mean(vec)))
        for role in ROLES:
            got = [
                float(s["llm_confidence"])
                for s in steps
                if s["round_index"] == r and s["agent_name"] == role and s.get("source") == "llm"
            ]
            if len(got) != 1:
                raise ValueError(f"{run.get('task_id')}: round {r} has {len(got)} {role} steps")
            out["role_conf"][role].append(got[0])
    # Pre-feedback analogue of the H4 ACE feature: metrics.ace_d on C(0), same guards as A2-10.
    vec0, _ = pre._round_vector(steps, 0)
    if sum(vec0) <= metrics._EPS:
        raise ValueError(f"{run.get('task_id')}: round-0 confidences sum to zero")
    out["ace_r0"] = float(metrics.ace_d(vec0))
    return out


def _task_rows(runs: list[dict], trainer: list[dict]) -> list[dict]:
    """One row per (dataset, task): the pre-registered table plus seed medians of the extras."""
    table = pre.per_task_table(runs)
    by_task: dict[tuple[str, str], list[dict]] = {}
    for run in runs:
        by_task.setdefault(pre.task_key(run), []).append(_run_features(run))
    sweep: dict[tuple[str, str], list[float]] = {}
    for rec in trainer:
        if "task" in rec and pre._finite(rec.get("msd_topk")):
            sweep.setdefault(pre.task_key(rec), []).append(float(rec["msd_topk"]))
    rows = []
    for base in table:
        key = (base["dataset"], base["task"])
        feats = by_task[key]
        if any(base[k] is None for k in (*SCATTER_KEYS, "msd")):
            raise ValueError(f"{key}: a pre-registered component or the MSD is undefined")
        row = {k: base[k] for k in ("dataset", "task", *SCATTER_KEYS, "msd")}
        row["n_seeds"] = len(feats)
        row["msd_round"] = [_median([x["msd"][r] for x in feats], f"{key} MSD") for r in ROUNDS]
        row["mean_conf"] = [
            _median([x["mean_conf"][r] for x in feats], f"{key} confidence") for r in ROUNDS
        ]
        row["role_conf"] = {
            role: [
                _median([x["role_conf"][role][r] for x in feats], f"{key} {role}") for r in ROUNDS
            ]
            for role in ROLES
        }
        row["ace_r0"] = _median([x["ace_r0"] for x in feats], f"{key} round-0 ACE")
        if row["msd_round"][-1] != row["msd"]:
            raise ValueError(f"{key}: last-round MSD median differs from the pre-registered table")
        records = sweep.get(key, [])
        row["n_trainer_records"] = len(records)
        row["oracle_min_msd"] = min(records) if records else None
        below = sum(v < row["msd"] for v in records)
        equal = sum(v == row["msd"] for v in records)
        row["msd_pct_rank"] = 100.0 * (below + 0.5 * equal) / len(records) if records else None
        rows.append(row)
    return rows


def _screen(rows: list[dict], n_records_per_task: int) -> dict:
    msd = [r["msd"] for r in rows]
    q: dict[str, dict] = {}
    # (a) mean stated confidence at each round vs final-round MSD
    for r in ROUNDS:
        q[f"conf_round{r}_vs_final_msd"] = _corr(
            [x["mean_conf"][r] for x in rows], msd, f"confidence r{r}"
        )
    # (b) 1 - delta_c vs the MSD of round 1 (shown to agents before round 2) and of round 0
    for r in (1, 0):
        q[f"one_minus_delta_c_vs_msd_round{r}"] = _corr(
            [x[H4_KEY] for x in rows], [x["msd_round"][r] for x in rows], f"1-dC vs MSD r{r}"
        )
    # (c) ace_d on round-0 confidences vs final MSD
    q["ace_round0_vs_final_msd"] = _corr([x["ace_r0"] for x in rows], msd, "round-0 ACE")
    # (d) rank agreement of the rounds' MSDs
    for r in (0, 1):
        q[f"msd_round{r}_vs_msd_round2"] = _corr(
            [x["msd_round"][r] for x in rows], [x["msd_round"][2] for x in rows], f"MSD r{r} vs r2"
        )
    # (e) across-task sample standard deviation (ddof = 1) of mean confidence at each round
    for r in ROUNDS:
        q[f"conf_sd_round{r}"] = {
            "kind": "sd",
            "value": float(statistics.stdev([x["mean_conf"][r] for x in rows])),
            "n": len(rows),
        }
    # (f) per-role mean (over tasks) confidence at each round, and its change round 0 -> round 2
    for role in ROLES:
        for r in ROUNDS:
            q[f"role_{role}_conf_round{r}"] = {
                "kind": "mean",
                "value": float(np.mean([x["role_conf"][role][r] for x in rows])),
                "n": len(rows),
            }
        q[f"role_{role}_conf_change"] = {
            "kind": "mean_change",
            "value": float(
                np.mean([x["role_conf"][role][2] - x["role_conf"][role][0] for x in rows])
            ),
            "n": len(rows),
        }
    # (g) lifecycle final MSD vs the trainer sweep of the same task
    bad = [x["task"] for x in rows if x["n_trainer_records"] != n_records_per_task]
    if bad:
        raise ValueError(f"tasks without {n_records_per_task} finite trainer records: {bad}")
    q["final_msd_vs_oracle_min"] = _corr(
        msd, [x["oracle_min_msd"] for x in rows], "lifecycle vs oracle"
    )
    q["final_msd_pct_rank_median"] = {
        "kind": "median",
        "value": float(statistics.median([x["msd_pct_rank"] for x in rows])),
        "n": len(rows),
        "n_trainer_records_per_task": n_records_per_task,
    }
    # (h) leave-one-task-out range of the committed H4 rho for 1 - delta_c
    xs, ys = (np.asarray(v, dtype=np.float64) for v in pre._pairs(rows, H4_KEY))
    loto = []
    for i in range(xs.size):
        keep = np.arange(xs.size) != i
        value = pre.rho(xs[keep], ys[keep])
        if value is None:
            raise ValueError(f"leave-one-out rho undefined without {rows[i]['task']}")
        loto.append(value)
    q["h4_one_minus_delta_c_leave_one_task_out"] = {
        "kind": "range",
        "min": min(loto),
        "max": max(loto),
        "n": len(loto),
        "task_at_min": rows[int(np.argmin(loto))]["task"],
        "task_at_max": rows[int(np.argmax(loto))]["task"],
    }
    return {
        "n_tasks": len(rows),
        "quantities": q,
        # plotted in fig_confidence_by_round, not typeset as macros
        "figure_only": {
            "median_msd_by_round": [
                float(statistics.median([x["msd_round"][r] for x in rows])) for r in ROUNDS
            ]
        },
        "per_task": [
            {k: x[k] for k in ("task", *SCATTER_KEYS, "msd", "msd_round", "mean_conf", "n_seeds")}
            for x in rows
        ],
    }


def build(artifacts: Path) -> dict:
    """The full exploratory record. Raises unless the committed H4 rho is reproduced."""
    inputs = {name: _sha256(artifacts / name) for name in INPUTS}
    summary = json.loads((artifacts / "summary.json").read_text())
    prov = json.loads((artifacts / "provenance.json").read_text())
    if summary["run_id"] != prov["run_id"]:
        raise ValueError("summary.json and provenance.json name different runs")
    runs = [r for r in _jsonl(artifacts / "lifecycle_runs.jsonl") if "steps" in r]
    trainer = _jsonl(artifacts / "trainer_runs.jsonl")
    rows = _task_rows(runs, trainer)
    committed = {
        r["dataset"]: r
        for r in summary["preregistered"]["H4"]["all_six"]
        if r["component"] == H4_KEY
    }
    reproduction, screens = {}, {}
    for ds in pre.H4_DATASETS:
        ds_rows = [r for r in rows if r["dataset"] == ds]
        got = pre.spearman_with_ci(*pre._pairs(ds_rows, H4_KEY))
        want = committed[ds]
        for k in ("rho", "ci_low", "ci_high"):
            if got[k] is None or not math.isclose(
                got[k], want[k], rel_tol=0.0, abs_tol=REPRODUCTION_ABS_TOL
            ):
                raise ValueError(
                    f"H4 reproduction failed for {ds} {H4_KEY} {k}: {got[k]!r} vs committed {want[k]!r}"
                )
        if got["n"] != want["n"]:
            raise ValueError(f"H4 reproduction failed for {ds}: n {got['n']} vs {want['n']}")
        reproduction[ds] = {
            "rho": got["rho"],
            "n": got["n"],
            "ci_low": got["ci_low"],
            "ci_high": got["ci_high"],
            "committed_rho": want["rho"],
        }
        screens[ds] = _screen(ds_rows, int(prov["trainer_grid"]["n_records_per_task"]))
    per_screen = {len(s["quantities"]) for s in screens.values()}
    if len(per_screen) != 1:
        raise ValueError("the screens report different numbers of quantities")
    corr_per_screen = {
        sum(q["kind"] == "spearman" for q in s["quantities"].values()) for s in screens.values()
    }
    if len(corr_per_screen) != 1:
        raise ValueError("the screens report different numbers of correlations")
    n_corr_per_screen = corr_per_screen.pop()
    n_corr = n_corr_per_screen * len(screens)
    return {
        "label": "exploratory: not pre-registered; the pre-registered outcomes are not re-decided",
        "generator": "scripts/paper/fill_v060_exploratory.py",
        "run_id": prov["run_id"],
        "prereg_version": prov["prereg_version"],
        "inputs_sha256": {f"artifacts/v0.6.0/{k}": v for k, v in inputs.items()},
        "estimator": {
            "module": "perturb_eval.experiments.preregistered",
            "unit": "task (median over seeds), within screen",
            "spearman": "average-rank; percentile bootstrap over tasks",
            "bootstrap_B": pre.BOOTSTRAP_B,
            "bootstrap_seed": pre.BOOTSTRAP_SEED,
            "ci_level": pre.CI_LEVEL,
            "sd": "sample standard deviation across tasks (ddof = 1)",
            "role_mean": "mean over tasks of the task's seed-median stated confidence",
            "pct_rank": "100 * (records below + half the records equal) / records, within the task",
        },
        "h4_reproduction": reproduction,
        "counts": {
            "n_analyses": N_ANALYSES,
            "n_quantities_per_screen": per_screen.pop(),
            "n_quantities": sum(len(s["quantities"]) for s in screens.values()),
            "n_correlations": n_corr,
            "n_correlations_per_screen": n_corr_per_screen,
        },
        "screens": screens,
    }


def macros(data: dict) -> dict[str, str]:
    m: dict[str, str] = {"RunId": data["run_id"]}
    c = data["counts"]
    m["NAnalyses"] = str(c["n_analyses"])
    m["NQuantities"] = str(c["n_quantities"])
    m["NQuantitiesPerScreen"] = str(c["n_quantities_per_screen"])
    m["NCorrelations"] = str(c["n_correlations"])
    m["NCorrelationsPerScreen"] = str(c["n_correlations_per_screen"])
    m["BootstrapB"] = str(data["estimator"]["bootstrap_B"])

    def corr(key: str, q: dict) -> None:
        m[f"{key}Rho"] = f(q["rho"])
        m[f"{key}N"] = str(q["n"])
        m[f"{key}CILo"] = f(q["ci_low"])
        m[f"{key}CIHi"] = f(q["ci_high"])

    for ds, dn in DS.items():
        q = data["screens"][ds]["quantities"]
        m[f"{dn}NTasks"] = str(data["screens"][ds]["n_tasks"])
        for r, word in zip(ROUNDS, ROUND_WORDS):
            corr(f"{dn}ConfR{word}Msd", q[f"conf_round{r}_vs_final_msd"])
            m[f"{dn}ConfSdR{word}"] = f(q[f"conf_sd_round{r}"]["value"])
            for role, rn in ROLES.items():
                m[f"{dn}Role{rn}ConfR{word}"] = f(q[f"role_{role}_conf_round{r}"]["value"])
        for role, rn in ROLES.items():
            m[f"{dn}Role{rn}ConfChange"] = f(q[f"role_{role}_conf_change"]["value"])
        corr(f"{dn}DcMsdROne", q["one_minus_delta_c_vs_msd_round1"])
        corr(f"{dn}DcMsdRZero", q["one_minus_delta_c_vs_msd_round0"])
        corr(f"{dn}AceRZeroMsd", q["ace_round0_vs_final_msd"])
        corr(f"{dn}MsdRZeroVsRTwo", q["msd_round0_vs_msd_round2"])
        corr(f"{dn}MsdROneVsRTwo", q["msd_round1_vs_msd_round2"])
        corr(f"{dn}Oracle", q["final_msd_vs_oracle_min"])
        m[f"{dn}OraclePctRankMedian"] = f(q["final_msd_pct_rank_median"]["value"], 1)
        loto = q["h4_one_minus_delta_c_leave_one_task_out"]
        m[f"{dn}LotoDcRhoMin"] = f(loto["min"])
        m[f"{dn}LotoDcRhoMax"] = f(loto["max"])
    return m


def render(m: dict[str, str]) -> str:
    lines = [
        "% GENERATED by scripts/paper/fill_v060_exploratory.py from artifacts/v0.6.0 — do not edit by hand.",
        "% EXPLORATORY quantities (not pre-registered); every value is one of these macros (CTO #491).",
    ]
    for k in sorted(m):
        if not re.fullmatch(r"[A-Za-z]+", k):
            raise ValueError(f"bad macro name {k!r}")
        v = m[k]
        if not ENSUREMATH_NEG.fullmatch(v) and not SAFE_VALUE.fullmatch(v):
            raise ValueError(f"macro {k} holds a value that is not TeX-safe: {v!r}")
        if not ENSUREMATH_NEG.fullmatch(v):
            v = v.replace("_", "\\_")
        lines.append(f"\\newcommand{{\\expl{k}}}{{{v}}}")
    return "\n".join(lines) + "\n"


def render_json(data: dict) -> str:
    return json.dumps(data, indent=1, sort_keys=True, allow_nan=False) + "\n"


def same(a, b) -> bool:
    """Structural equality; floats agree within ``JSON_REL_TOL`` (ulp noise is not staleness)."""
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if isinstance(a, float) and isinstance(b, float):
        return math.isclose(a, b, rel_tol=JSON_REL_TOL, abs_tol=JSON_REL_TOL)
    return type(a) is type(b) and a == b


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifacts", type=Path, default=PROJECT_ROOT / "artifacts" / "v0.6.0")
    ap.add_argument(
        "--out",
        type=Path,
        default=PROJECT_ROOT / "paper" / "sections" / "generated_exploratory.tex",
    )
    ap.add_argument(
        "--json-out", type=Path, default=PROJECT_ROOT / "paper" / "data" / "exploratory_v060.json"
    )
    ap.add_argument(
        "--check", action="store_true", help="regenerate and fail if a committed output differs"
    )
    a = ap.parse_args()
    data = build(a.artifacts)
    text = render(macros(data))
    if a.check:
        stale = []
        if not a.out.exists() or a.out.read_text() != text:
            stale.append(a.out)
        # round-trip through JSON so both sides have the same types
        fresh = json.loads(render_json(data))
        if not a.json_out.exists() or not same(json.loads(a.json_out.read_text()), fresh):
            stale.append(a.json_out)
        for path in stale:
            print(f"{path} is stale: regenerate with fill_v060_exploratory.py", file=sys.stderr)
        if stale:
            return 1
        print(f"{a.out} and {a.json_out} match the artifacts")
        return 0
    a.json_out.write_text(render_json(data))
    a.out.write_text(text)
    print(f"wrote {a.json_out} and {a.out} ({text.count(chr(10))} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
