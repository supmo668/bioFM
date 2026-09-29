"""Generate ``paper/sections/generated_numbers.tex`` from the v0.6.0 artifacts.

Every result value in the manuscript is a LaTeX macro defined here, computed from
``artifacts/v0.6.0/summary.json`` (the analyser's output), ``provenance.json`` and the
plan's projection file. A number typed into a .tex file by hand is a defect (CTO #491);
``--check`` regenerates and fails if the committed file differs.

    .venv/bin/python scripts/paper/fill_v060_numbers.py --artifacts artifacts/v0.6.0 \
        --projection paper/data/projection_v060.json --out paper/sections/generated_numbers.tex [--check]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

ROLES = ("DataCurator", "Literature", "Architect", "Trainer", "Validator")
COMP = {"ace_norm": "Ace", "one_minus_delta_c": "Dc", "tdi_lifecycle": "Tdi"}
DS = {"adamson_full": "Ada", "norman": "Nor"}
WORDS = {
    "DataCurator": "Curator",
    "Literature": "Literature",
    "Architect": "Architect",
    "Trainer": "Trainer",
    "Validator": "Validator",
}


def f(x, d=3):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    return f"{float(x):.{d}f}"


def verdict(ok):
    return r"\textbf{PASS}" if ok else r"\textbf{FAIL}"


def build(
    artifacts: Path, projection: Path, manifest: Path | None, archives: list[Path]
) -> dict[str, str]:
    s = json.loads((artifacts / "summary.json").read_text())
    p = json.loads((artifacts / "provenance.json").read_text())
    proj = json.loads(projection.read_text())
    pr = s["preregistered"]
    m: dict[str, str] = {}
    # ---- run identity
    m["RunId"] = p["run_id"]
    m["GitSha"] = p["git_sha"][:7]
    m["PreregVersion"] = p["prereg_version"]
    m["GitDirty"] = str(p["git_dirty"]).lower()
    # ---- H1 / H2
    for g, name in (("H1", "HOne"), ("H2", "HTwo")):
        r = pr[g]
        m[f"{name}Median"] = f(r["value"])
        m[f"{name}N"] = str(r["n"])
        m[f"{name}IQRLo"] = f(r["iqr"][0])
        m[f"{name}IQRHi"] = f(r["iqr"][1])
        m[f"{name}Max"] = f(r["max"])
        m[f"{name}FracOver"] = f(r["fraction_over_gate"], 2)
        m[f"{name}CILo"] = f(r["ci_low"])
        m[f"{name}CIHi"] = f(r["ci_high"])
        m[f"{name}Threshold"] = f(r["threshold"], 2)
        m[f"{name}Verdict"] = verdict(r["pass"])
    st = pr["H2"].get("strata", {})
    for k, name in (("singleton", "Singleton"), ("doublet", "Doublet")):
        if k in st:
            m[f"HTwo{name}Median"] = f(st[k]["median"])
            m[f"HTwo{name}N"] = str(st[k]["n"])
    # ---- H3
    h3 = pr["H3"]
    m["HThreeEntropy"] = f(h3["value"])
    m["HThreeCeiling"] = f(h3["ceiling_nats"])
    m["HThreeVerdict"] = verdict(h3["pass"])
    for bb, name in (("linear", "Linear"), ("mlp", "Mlp"), ("scgpt_small", "Scgpt")):
        m[f"HThreePick{name}"] = str(h3["pick_counts"].get(bb, 0))
    m["HThreeNSteps"] = str(sum(h3["pick_counts"].values()))
    m["HThreeExecNeStated"] = str(h3["n_executed_ne_stated"])
    m["HThreeNModels"] = str(len(h3.get("by_model_id") or {}))
    # ---- H4
    h4 = pr["H4"]
    for row in h4["all_six"]:
        key = f"HFour{DS[row['dataset']]}{COMP[row['component']]}"
        m[f"{key}Rho"] = f(row["rho"])
        m[f"{key}N"] = str(row["n"])
        m[f"{key}CILo"] = f(row["ci_low"])
        m[f"{key}CIHi"] = f(row["ci_high"])
        m[f"{key}Pass"] = "yes" if row["passes"] else "no"
    for comp, name in COMP.items():
        pooled = h4.get("pooled_descriptive", {}).get(comp, {})
        m[f"HFourPooled{name}Rho"] = f(pooled.get("rho"))
    m["HFourNPassing"] = str(h4["n_tests_passing"])
    m["HFourNTests"] = str(h4["n_tests"])
    m["HFourVerdict"] = verdict(h4["pass"])
    m["HFourValue"] = f(h4["value"])
    ex = h4.get("exclusions", {})
    m["HFourRunsUndefined"] = str(
        sum(v.get("runs_undefined", 0) for d in ex.values() for v in d.values())
    )
    m["HFourTasksDropped"] = str(
        sum(v.get("tasks_dropped", 0) for d in ex.values() for v in d.values())
    )
    # ---- H5
    h5 = pr["H5"]
    m["HFiveRho"] = f(h5["value"])
    m["HFiveN"] = str(h5["n"])
    m["HFiveCILo"] = f(h5.get("ci_low"))
    m["HFiveCIHi"] = f(h5.get("ci_high"))
    m["HFiveWAce"] = f(h5["weights"]["ace_norm"], 2)
    m["HFiveWDc"] = f(h5["weights"]["one_minus_delta_c"], 2)
    m["HFiveVerdict"] = verdict(h5["pass"])
    m["HFiveThreshold"] = f(h5["threshold"], 1)
    t = pr["tally"]
    m["TallyPass"] = str(t["PASS"])
    m["TallyFail"] = str(t["FAIL"])
    m["TallyUneval"] = str(t["UNEVALUATED"])
    m["TallyOut"] = str(t["out_of"])
    failed = [g for g in ("H1", "H2", "H3", "H4", "H5") if pr[g]["pass"] is False]
    m["GateSummary"] = (
        f"{t['PASS']} of {t['out_of']} gates pass"
        + (f"; {', '.join(failed)} fail" + ("s" if len(failed) == 1 else "") if failed else "")
        + f" ({t['UNEVALUATED']} unevaluated)"
    )
    # ---- run record
    rep = p["llm_report"]
    log = p["llm_call_log"]
    m["NLifecycleRuns"] = str(
        s.get("n_lifecycle_runs") or len({(c["task_id"], c["round_index"]) for c in log}) // 3
        if False
        else (s.get("n_lifecycle_runs") or "n/a")
    )
    m["NCalls"] = str(rep["calls"])
    m["StopEndTurn"] = str(rep["stop_reason_counts"].get("end_turn", 0))
    m["StopMaxTokens"] = str(rep["stop_reason_counts"].get("max_tokens", 0))
    m["ServedMismatch"] = str(rep["served_mismatch_count"])
    m["Refusals"] = str(sum(1 for c in log if c.get("stop_reason") == "refusal"))
    m["CacheStart"] = str(p["llm_cache_entries_at_start"])
    m["CacheHits"] = str(p["llm_cache_hit_count"])
    m["Replay"] = str(p["replay"]).lower()
    m["NFallback"] = str(s.get("n_fallback_steps", s.get("source_counts", {}).get("fallback", 0)))
    m["NSteps"] = str(
        sum(1 for c in log if not c.get("cache_hit"))
        - rep["stop_reason_counts"].get("max_tokens", 0)
    )
    m["SpendLLM"] = f(p["llm_cost_usd"], 2)
    m["SpendGPU"] = f(p["gpu_cost_usd"], 2)
    m["SpendPrior"] = f(p["prior_spend_usd"], 4)
    m["SpendPreflight"] = f(p["preflight_spend_usd"], 4)
    m["SpendTotal"] = f(p["cost_usd_actual"], 2)
    m["GPUHours"] = f(p["gpu_seconds"] / 3600, 2)
    m["SpendStopLine"] = f(p["entrypoint_kwargs"]["spend_stop_usd"], 0)
    m["SpendHaiku"] = f(rep["by_model"]["claude-haiku-4-5-20251001"], 2)
    m["SpendSonnet"] = f(rep["by_model"]["claude-sonnet-5-5"], 2)
    m["TokensIn"] = f"{sum(c.get('input_tokens', 0) for c in log):,}"
    m["TokensOut"] = f"{sum(c.get('output_tokens', 0) for c in log):,}"
    for role in ROLES:
        m[f"Ceiling{WORDS[role]}"] = str(rep["role_ceilings"][role])
    m["RosterHaiku"] = p["llm_pool"][0]
    m["RosterSonnet"] = p["llm_pool"][1]
    m["StopReasonNone"] = "none" if p["stop_reason"] is None else str(p["stop_reason"])
    grid = p["trainer_grid"]
    m["NTrainerRecordsPerTask"] = str(grid["n_records_per_task"])
    m["NDistinctConfigs"] = str(grid["n_distinct_configs_per_task"])
    m["NDistinctFits"] = str(grid["n_distinct_fits_per_task"])
    m["NTrainerRuns"] = str(grid["n_records_per_task"] * 41)
    # ---- projection (plan figures)
    m["ProjLLM"] = f(proj["llm_usd"], 2)
    m["ProjGPU"] = f(proj["gpu_usd"], 2)
    m["ProjTotal"] = f(proj["total_usd"], 2)
    m["ProjLatency"] = f(proj["gpu_latency_per_round_s"], 1)
    m["KillLine"] = f(proj["kill_line_usd"], 0)
    m["CeilingLine"] = f(proj["ceiling_usd"], 0)
    # ---- hashes
    m["ManifestSha"] = (
        hashlib.sha256(manifest.read_bytes()).hexdigest()[:16]
        if manifest and manifest.exists()
        else "n/a"
    )
    for i, a in enumerate(archives):
        m[f"ArchiveSha{'Cache' if i == 0 else 'Outputs'}"] = (
            hashlib.sha256(a.read_bytes()).hexdigest()[:16] if a.exists() else "n/a"
        )
    return m


def render(m: dict[str, str]) -> str:
    lines = [
        "% GENERATED by scripts/paper/fill_v060_numbers.py from artifacts/v0.6.0 — do not edit by hand.",
        "% Every result value in the manuscript is one of these macros (CTO #491: no hand-typed numbers).",
    ]
    for k in sorted(m):
        assert re.fullmatch(r"[A-Za-z]+", k), k
        lines.append(f"\\newcommand{{\\res{k}}}{{{m[k]}}}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifacts", type=Path, default=Path("artifacts/v0.6.0"))
    ap.add_argument("--projection", type=Path, default=Path("paper/data/projection_v060.json"))
    ap.add_argument(
        "--manifest", type=Path, default=Path("configs/runs/20260929T035447Z-ce5f237.json")
    )
    ap.add_argument(
        "--archive-manifests",
        type=Path,
        nargs="*",
        default=[
            Path(
                "../../workstreams/perturb-seq-eval/qgr/evidence/llm-cache-archive-20260928T220916Z-291efad.manifest.json"
            ),
            Path(
                "../../workstreams/perturb-seq-eval/qgr/evidence/output-archive-20260928T220916Z-291efad.manifest.json"
            ),
        ],
    )
    ap.add_argument("--out", type=Path, default=Path("paper/sections/generated_numbers.tex"))
    ap.add_argument(
        "--check", action="store_true", help="regenerate and fail if the committed file differs"
    )
    a = ap.parse_args()
    text = render(build(a.artifacts, a.projection, a.manifest, a.archive_manifests))
    if a.check:
        current = a.out.read_text() if a.out.exists() else ""
        if current != text:
            print(f"{a.out} is stale: regenerate with fill_v060_numbers.py", file=sys.stderr)
            return 1
        print(f"{a.out} matches the artifacts")
        return 0
    a.out.write_text(text)
    print(f"wrote {a.out} ({text.count(chr(10))} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
