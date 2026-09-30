"""Generate ``paper/sections/generated_numbers.tex`` from the v0.6.0 artifacts.

Every result value in the manuscript is a LaTeX macro defined here, computed from
``artifacts/v0.6.0/{summary.json,provenance.json,lifecycle_runs.jsonl}`` (the analyser's
output and the run record) and the pre-registered projection file. A number typed into
a .tex file by hand is a defect (CTO #491); ``--check`` regenerates and fails if the
committed file differs. Every default path resolves against the project root, so the
script behaves the same from any working directory; a missing input is an error, never
an ``n/a`` in the paper.

    .venv/bin/python scripts/paper/fill_v060_numbers.py [--check]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKSTREAM = PROJECT_ROOT.parents[1] / "workstreams" / "perturb-seq-eval"
ROLES = ("DataCurator", "Literature", "Architect", "Trainer", "Validator")
COMP = {"ace_norm": "Ace", "one_minus_delta_c": "Dc", "tdi_lifecycle": "Tdi"}
DESCRIPTIVE = {"ace_norm_softmax": "AceSoftmax", "one_minus_delta_c_clipped": "DcClipped"}
DS = {"adamson_full": "Ada", "norman": "Nor"}
WORDS = {
    "DataCurator": "Curator",
    "Literature": "Literature",
    "Architect": "Architect",
    "Trainer": "Trainer",
    "Validator": "Validator",
}
HAIKU = "claude-haiku-4-5-20251001"
SONNET = "claude-sonnet-5-5"
PRIMARY = {role: (SONNET if role == "Validator" else HAIKU) for role in ROLES}
# Macro values are typeset verbatim; anything outside this alphabet (or a verdict) is refused.
SAFE_VALUE = re.compile(r"[A-Za-z0-9.,:;()+\- /_]*")  # `_` is escaped at emission
ENSUREMATH_NEG = re.compile(
    r"\\ensuremath\{-\d+(\.\d+)?\}|\d{1,3}(\\,\d{3})+"
)  # negatives; thin-space thousands
VERDICTS = {r"\textbf{PASS}", r"\textbf{FAIL}", r"\textbf{UNEVALUATED}"}


def f(x, d: int = 3) -> str:
    """Fixed-point text; negatives are wrapped so the minus sign survives text mode."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        raise ValueError("a result value is undefined; the manuscript cannot print n/a")
    s = f"{float(x):.{d}f}"
    return rf"\ensuremath{{{s}}}" if s.startswith("-") else s


def verdict(ok) -> str:
    if ok is None:
        return r"\textbf{UNEVALUATED}"
    return r"\textbf{PASS}" if ok else r"\textbf{FAIL}"


def _sha16(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def build(
    artifacts: Path,
    projection: Path,
    manifest: Path,
    archives: list[Path],
    land: Path | None = None,
    amendments: Path | None = None,
    v050: Path | None = None,
) -> dict[str, str]:
    s = json.loads((artifacts / "summary.json").read_text())
    p = json.loads((artifacts / "provenance.json").read_text())
    proj = json.loads(projection.read_text())
    runs = [
        json.loads(line) for line in (artifacts / "lifecycle_runs.jsonl").read_text().splitlines()
    ]
    runs = [r for r in runs if "steps" in r and "applied_config_per_round" in r]
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
    for k, name in (("singleton", "Singleton"), ("doublet", "Doublet")):
        st = pr["H2"]["strata"][k]
        m[f"HTwo{name}Median"] = f(st["median"])
        m[f"HTwo{name}N"] = str(st["n"])
        m[f"HTwo{name}IQRLo"] = f(st["iqr"][0])
        m[f"HTwo{name}IQRHi"] = f(st["iqr"][1])
        m[f"HTwo{name}Max"] = f(st["max"])
        m[f"HTwo{name}FracOver"] = f(st["fraction_over_gate"], 2)
    # ---- H3
    h3 = pr["H3"]
    m["HThreeEntropy"] = f(h3["value"])
    m["HThreeCeiling"] = f(h3["ceiling_nats"])
    m["HThreeVerdict"] = verdict(h3["pass"])
    for bb, name in (("linear", "Linear"), ("mlp", "Mlp"), ("scgpt_small", "Scgpt")):
        m[f"HThreePick{name}"] = str(h3["pick_counts"].get(bb, 0))
    m["HThreeNSteps"] = str(h3["n_llm_architect_steps"])
    m["HThreeExecNeStated"] = str(h3["n_executed_ne_stated"])
    m["HThreeNModels"] = str(h3["n_distinct_model_ids"])
    for bb, name in (("linear", "Linear"), ("mlp", "Mlp"), ("scgpt_small", "Scgpt")):
        m[f"HThreeExecPick{name}"] = str(h3["executed_pick_counts"].get(bb, 0))
    m["HThreeEntropyExecuted"] = f(h3["entropy_executed_nats"])
    m["HThreeNCounted"] = str(h3["n_counted"])
    m["HThreeNMissingStated"] = str(h3["n_missing_stated"])
    m["HThreeNMissingExecuted"] = str(h3["n_missing_executed"])
    m["HThreeNOffMenu"] = str(h3["n_off_menu_stated"])
    # Miller-Madow bias-corrected entropy H + (K-1)/(2N) (pre-registration, H3 "Bias"): typeset beside the
    # plug-in value as descriptive (CTO #496); the gate stays the plug-in value. The analyser only fills
    # miller_madow_nats for breakdowns with N < 50, so the pooled value is computed here by the same formula.
    k_menu = len(h3["menu"])
    mm = h3["miller_madow_nats"]
    if mm is None:
        mm = h3["value"] + (k_menu - 1) / (2 * h3["n_counted"])
    m["HThreeMillerMadowNats"] = f(mm)
    m["HThreeMenuSize"] = str(k_menu)
    # Per-breakdown Miller-Madow is pre-registered only for N < 50; the smallest breakdown here is per model_id.
    small = {k: v for k, v in h3["by_model_id"].items() if v["n"] < 50}
    m["HThreeSmallestBreakdownN"] = str(min(v["n"] for v in h3["by_model_id"].values()))
    m["HThreeMillerMadow"] = (
        "; ".join(f"{k}: {f(v['miller_madow_nats'])}" for k, v in small.items())
        if small
        else "not applicable"
    )
    # ---- H4 (six pre-registered tests + the two descriptive forms per dataset)
    h4 = pr["H4"]
    for row in h4["all_six"]:
        key = f"HFour{DS[row['dataset']]}{COMP[row['component']]}"
        m[f"{key}Rho"] = f(row["rho"])
        m[f"{key}N"] = str(row["n"])
        m[f"{key}CILo"] = f(row["ci_low"])
        m[f"{key}CIHi"] = f(row["ci_high"])
        m[f"{key}Pass"] = (
            "undefined" if row["passes"] is None else ("yes" if row["passes"] else "no")
        )
    for ds, dn in DS.items():
        for comp, cn in DESCRIPTIVE.items():
            row = h4["descriptive"][ds][comp]
            m[f"HFour{dn}{cn}Rho"] = f(row["rho"])
            m[f"HFour{dn}{cn}N"] = str(row["n"])
            m[f"HFour{dn}{cn}CILo"] = f(row["ci_low"])
            m[f"HFour{dn}{cn}CIHi"] = f(row["ci_high"])
    for comp, name in COMP.items():
        m[f"HFourPooled{name}Rho"] = f(h4["pooled_descriptive"][comp]["rho"])
    m["HFourNPassing"] = str(h4["n_tests_passing"])
    m["HFourNTests"] = str(h4["n_tests"])
    m["HFourVerdict"] = verdict(h4["pass"])
    ex = h4["exclusions"]
    m["HFourRunsUndefined"] = str(sum(v["runs_undefined"] for d in ex.values() for v in d.values()))
    m["HFourTasksDropped"] = str(sum(v["tasks_dropped"] for d in ex.values() for v in d.values()))
    # ---- H5 (weights AND the Adamson standardisation, as pre-registered)
    h5 = pr["H5"]
    m["HFiveRho"] = f(h5["value"])
    m["HFiveN"] = str(h5["n"])
    m["HFiveCILo"] = f(h5["ci_low"])
    m["HFiveCIHi"] = f(h5["ci_high"])
    m["HFiveWAce"] = f(h5["weights"]["ace_norm"], 2)
    m["HFiveWDc"] = f(h5["weights"]["one_minus_delta_c"], 2)
    m["HFiveStdMeanAce"] = f(h5["standardise_mean"]["ace_norm"], 4)
    m["HFiveStdSdAce"] = f(h5["standardise_sd"]["ace_norm"], 4)
    m["HFiveStdMeanDc"] = f(h5["standardise_mean"]["one_minus_delta_c"], 4)
    m["HFiveStdSdDc"] = f(h5["standardise_sd"]["one_minus_delta_c"], 4)
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
    # ---- run record (analyser counters first, the call log second)
    rep = p["llm_report"]
    log = p["llm_call_log"]
    live = [c for c in log if not c.get("cache_hit")]
    m["NLifecycleRuns"] = str(s["n_lifecycle_runs"])
    m["NTrainerRuns"] = str(s["n_trainer_runs"])
    m["NTasks"] = str(s["n_tasks_analysed"])
    m["NSteps"] = str(s["n_steps_llm"])
    m["NFallback"] = str(s["n_steps_fallback"])
    m["NStepsMock"] = str(s["n_steps_mock"])
    m["NStepsUnknown"] = str(s["n_steps_unknown"])
    m["NCalls"] = str(rep["calls"])
    m["StopEndTurn"] = str(rep["stop_reason_counts"].get("end_turn", 0))
    m["StopMaxTokens"] = str(rep["stop_reason_counts"].get("max_tokens", 0))
    m["ServedMismatch"] = str(rep["served_mismatch_count"])
    m["Refusals"] = str(sum(1 for c in log if c.get("stop_reason") == "refusal"))
    m["CacheStart"] = str(p["llm_cache_entries_at_start"])
    m["CacheHits"] = str(p["llm_cache_hit_count"])
    m["Replay"] = str(p["replay"]).lower()
    m["SpendLLM"] = f(p["llm_cost_usd"], 2)
    m["SpendGPU"] = f(p["gpu_cost_usd"], 2)
    m["SpendPrior"] = f(p["prior_spend_usd"], 4)
    m["SpendPreflight"] = f(p["preflight_spend_usd"], 4)
    m["SpendTotal"] = f(p["cost_usd_actual"], 2)
    m["GPUHours"] = f(p["gpu_seconds"] / 3600, 2)
    m["SpendStopLine"] = f(p["entrypoint_kwargs"]["spend_stop_usd"], 0)
    m["KillLine"] = f(p["budget_cap_usd"], 0)
    m["SpendHaiku"] = f(rep["by_model"][HAIKU], 2)
    m["SpendSonnet"] = f(rep["by_model"][SONNET], 2)
    m["TokensIn"] = f"{sum(c.get('input_tokens', 0) for c in log):,}"
    m["TokensOut"] = f"{sum(c.get('output_tokens', 0) for c in log):,}"
    for role in ROLES:
        m[f"Ceiling{WORDS[role]}"] = str(rep["role_ceilings"][role])
        served = {c["served_model"] for c in live if c["role"] == role}
        if len(served) != 1:
            raise ValueError(
                f"{role} was served by {sorted(served)}; the paper states one model per role"
            )
        m[f"RoleServed{WORDS[role]}"] = served.pop()
        m[f"RoleCalls{WORDS[role]}"] = str(sum(1 for c in live if c["role"] == role))
    m["NFailover"] = str(sum(1 for c in live if c["requested_model"] != PRIMARY[c["role"]]))
    pool = set(p["llm_pool"])
    if pool != {HAIKU, SONNET}:
        raise ValueError(f"roster {sorted(pool)} is not the amendment-4 roster")
    m["RosterHaiku"] = HAIKU
    m["RosterSonnet"] = SONNET
    price = p["llm_price_table"]
    m["PriceHaikuIn"] = f(price[HAIKU]["input"], 2)
    m["PriceHaikuOut"] = f(price[HAIKU]["output"], 2)
    m["PriceSonnetIn"] = f(price[SONNET]["input"], 2)
    m["PriceSonnetOut"] = f(price[SONNET]["output"], 2)
    liveness = p["llm_roster_liveness"]
    m["LivenessOkPairs"] = str(
        sum(1 for mdl in liveness.values() for r in mdl["roles"].values() if r["ok"])
    )
    m["LivenessTotalPairs"] = str(sum(len(mdl["roles"]) for mdl in liveness.values()))
    m["StopReasonNone"] = "none" if p["stop_reason"] is None else str(p["stop_reason"])
    grid = p["trainer_grid"]
    m["NTrainerRecordsPerTask"] = str(grid["n_records_per_task"])
    m["NDistinctConfigs"] = str(grid["n_distinct_configs_per_task"])
    m["NDistinctFits"] = str(grid["n_distinct_fits_per_task"])
    # ---- what the lifecycle actually applied (A2-3 / A3-2 / A3-3 facts)
    rounds = [rd for r in runs for rd in r["applied_config_per_round"]]
    hvg_values = sorted({rd["values"]["hvg_count"] for rd in rounds})
    m["NRoundsTotal"] = str(len(rounds))
    m["HVGDistinctApplied"] = str(len(hvg_values))
    m["HVGAppliedValue"] = (
        str(hvg_values[0]) if len(hvg_values) == 1 else "; ".join(map(str, hvg_values))
    )
    m["HVGEntropy"] = f(p["entropies"]["architect_hvg_entropy_nats"])
    m["ValidatorSourcedRounds"] = str(
        sum(1 for rd in rounds if "validator" in rd["sources"].values())
    )
    vsteps = [st for r in runs for st in r["steps"] if st["agent_name"] == "Validator"]
    m["NValidatorSteps"] = str(len(vsteps))
    m["ValidatorAccepted"] = str(sum(1 for st in vsteps if st["validator_accepted"] is True))
    m["ValidatorRejected"] = str(sum(1 for st in vsteps if st["validator_accepted"] is False))
    # ---- projection (pre-registered in A4-2; the JSON is the plan's copy)
    m["ProjLLM"] = f(proj["llm_usd"], 2)
    m["ProjGPU"] = f(proj["gpu_usd"], 2)
    m["ProjTotal"] = f(proj["total_usd"], 2)
    m["ProjLatency"] = f(proj["gpu_latency_per_round_s"], 1)
    m["CeilingLine"] = f(proj["ceiling_usd"], 0)
    # ---- run revision vs landed revision (deposit gate, CTO #509/#526): the paths that changed after
    # the run are named from the land record, never typed into the .tex
    land_path = land or (PROJECT_ROOT / "paper" / "data" / "land_v060.json")
    ld = json.loads(land_path.read_text())
    for key in ("run_git_sha", "land_git_sha"):
        if not re.fullmatch(r"[0-9a-f]{7,40}", str(ld[key])):
            raise ValueError(f"land record's {key} is not a 7-40 hex git sha: {ld[key]!r}")
    if not p["git_sha"].startswith(ld["run_git_sha"]):
        raise ValueError("land record's run_git_sha does not match provenance git_sha")
    if p["git_sha"].startswith(ld["land_git_sha"]) or ld["land_git_sha"].startswith(
        ld["run_git_sha"]
    ):
        raise ValueError("land record's land_git_sha must differ from the run's git sha")
    m["LandSha"] = ld["land_git_sha"]
    m["LandPR"] = str(ld["pr_number"])
    m["PostRunPathCount"] = str(len(ld["post_run_changed_paths"]))
    # ---- A4-1 thinking / sampling facts from the run record (CTO #532 ii)
    th = rep["thinking"]
    sm = rep["sampling"]
    m["ThinkingHaiku"] = str((th.get(HAIKU) or {}).get("thinking", {}).get("type", "none"))
    m["ThinkingSonnet"] = str((th.get(SONNET) or {}).get("thinking", {}).get("type", "none"))
    m["EffortSonnet"] = str((th.get(SONNET) or {}).get("effort", "default"))
    m["TemperatureHaiku"] = f(sm[HAIKU]["temperature"], 1)
    m["SamplingSonnet"] = (
        "API defaults"
        if not sm.get(SONNET)
        else "; ".join(f"{k} {v}" for k, v in sm[SONNET].items())
    )
    # ---- amendments table (CTO #532 i): ids, versions, lock commits, UTC lock dates, one-line change
    am = json.loads(
        (amendments or (PROJECT_ROOT / "paper" / "data" / "amendments_v060.json")).read_text()
    )
    for a in am["amendments"]:
        word = {"A2": "Two", "A3": "Three", "A4": "Four"}[a["id"]]
        m[f"Amend{word}Version"] = a["prereg_version"]
        m[f"Amend{word}Date"] = a["lock_date_utc"]
        m[f"Amend{word}Commit"] = ", ".join(a["lock_commits"])
        m[f"Amend{word}Change"] = a["change"]
    # ---- v0.5.0 record (CTO #532 iii): every v0.5.0 figure in the corrections appendix is read, not typed
    vr = json.loads((v050 or (PROJECT_ROOT / "paper" / "data" / "v050_record.json")).read_text())
    s5 = json.loads((PROJECT_ROOT / "artifacts" / "v0.5.0" / "summary.json").read_text())
    p5 = json.loads((PROJECT_ROOT / "artifacts" / "v0.5.0" / "provenance.json").read_text())
    dist = s5["architect_backbone_distribution"]
    m["VFiveRecordCommit"] = vr["record_commit"]
    m["VFiveAdamsonMedian"] = f(s5["median_msd_adamson"])
    m["VFiveNormanMedian"] = f(s5["median_msd_norman"])
    m["VFiveNTasks"] = str(s5["n_tasks_analysed"])
    m["VFiveNTrainerRuns"] = f"{s5['n_trainer_runs']:,}".replace(",", "\\,")
    m["VFiveConfigsPerTask"] = str(s5["n_trainer_runs"] // s5["n_tasks_analysed"])
    m["VFiveNLifecycleRuns"] = str(s5["n_lifecycle_runs"])
    m["VFiveBackboneEntropy"] = f(s5["architect_backbone_entropy_nats"], 2)
    m["VFiveHVGEntropy"] = f(s5["architect_hvg_entropy_nats"], 2)
    m["VFiveNPicks"] = str(sum(dist.values()))
    m["VFiveScgptSharePct"] = f(100 * dist["scgpt_small"] / sum(dist.values()), 0)
    m["VFiveSpend"] = f(p5["total_cost_usd"], 2)
    m["VFiveGPUHours"] = f(p5["total_gpu_seconds"] / 3600, 2)
    m["VFiveBudgetCap"] = f(p5["budget_cap_usd"], 0)
    # ---- integrity anchors (a missing file is an error, never n/a)
    # A2-5: H1/H2 and H4/H5 cite the same per-task evaluation-gene list (summary.json)
    m["EvalGeneTasks"] = str(len(s["eval_genes_per_task"]))
    m["EvalGeneMismatch"] = str(len(s["eval_gene_mismatch_tasks"]))
    m["ManifestSha"] = _sha16(manifest)
    for i, a in enumerate(archives):
        m[f"ArchiveSha{'Cache' if i == 0 else 'Outputs'}"] = _sha16(a)
    return m


def render(m: dict[str, str]) -> str:
    lines = [
        "% GENERATED by scripts/paper/fill_v060_numbers.py from artifacts/v0.6.0 — do not edit by hand.",
        "% Every result value in the manuscript is one of these macros (CTO #491: no hand-typed numbers).",
    ]
    for k in sorted(m):
        if not re.fullmatch(r"[A-Za-z]+", k):
            raise ValueError(f"bad macro name {k!r}")
        v = m[k]
        if v not in VERDICTS and not ENSUREMATH_NEG.fullmatch(v) and not SAFE_VALUE.fullmatch(v):
            raise ValueError(f"macro {k} holds a value that is not TeX-safe: {v!r}")
        if v not in VERDICTS and not ENSUREMATH_NEG.fullmatch(v):
            v = v.replace("_", "\\_")
        lines.append(f"\\newcommand{{\\res{k}}}{{{v}}}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifacts", type=Path, default=PROJECT_ROOT / "artifacts" / "v0.6.0")
    ap.add_argument(
        "--projection", type=Path, default=PROJECT_ROOT / "paper" / "data" / "projection_v060.json"
    )
    ap.add_argument(
        "--manifest",
        type=Path,
        default=PROJECT_ROOT / "configs" / "runs" / "20260929T035447Z-ce5f237.json",
    )
    ap.add_argument(
        "--archive-manifests",
        type=Path,
        nargs="*",
        default=[
            WORKSTREAM
            / "qgr"
            / "evidence"
            / "llm-cache-archive-20260928T220916Z-291efad.manifest.json",
            WORKSTREAM
            / "qgr"
            / "evidence"
            / "output-archive-20260928T220916Z-291efad.manifest.json",
        ],
    )
    ap.add_argument("--land", type=Path, default=PROJECT_ROOT / "paper" / "data" / "land_v060.json")
    ap.add_argument(
        "--out", type=Path, default=PROJECT_ROOT / "paper" / "sections" / "generated_numbers.tex"
    )
    ap.add_argument(
        "--check", action="store_true", help="regenerate and fail if the committed file differs"
    )
    a = ap.parse_args()
    text = render(build(a.artifacts, a.projection, a.manifest, a.archive_manifests, a.land))
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
