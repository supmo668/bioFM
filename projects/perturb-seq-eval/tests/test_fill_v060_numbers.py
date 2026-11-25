"""The manuscript's result values come ONLY from the committed v0.6.0 artifacts (CTO #491).

Every result macro is pinned to an independent key path in the artifacts (not to the
generator's own output), the prose claims that depend on artifact facts are pinned to
those facts, and the methods wording is pinned to the amendments it must describe.
"""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from numeric_env import header_line

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
GEN = PAPER / "sections" / "generated_numbers.tex"
RESULTS = PAPER / "sections" / "results.tex"
SETUP = PAPER / "sections" / "experimental_setup.tex"
MAIN = PAPER / "paper.tex"
CORR = PAPER / "sections" / "corrections.tex"
TEX_INPUTS = [MAIN, RESULTS, SETUP, CORR]
ART = ROOT / "artifacts" / "v0.6.0"

# Pre-registered constants / design facts that may appear as decimal literals in the scanned
# prose (never sweep results). Each must occur in paper/PREREGISTRATION.md and be used.
ALLOWED_LITERALS = {
    "results.tex": {"0.5", "2.35", "4.71", "5.84", "0.0475", "1.0"},
    "experimental_setup.tex": {"0.02", "0.3"},
    "paper.tex": set(),
    "corrections.tex": set(),
}
# Design facts that are not sweep results and not pre-registration constants (model size,
# the v0.5 default TDI weights quoted in the Metrics section).
DESIGN_LITERALS = {
    "results.tex": set(),
    "experimental_setup.tex": {"2.1"},
    "paper.tex": {"0.35", "0.25", "0.15"},
    "corrections.tex": set(),
}


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "fill_v060_numbers", ROOT / "scripts" / "paper" / "fill_v060_numbers.py"
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def fv():
    return _load_module()


@pytest.fixture(scope="module")
def macros() -> dict[str, str]:
    raw = dict(
        re.findall(r"^\\newcommand\{\\(res[A-Za-z]+)\}\{(.*)\}$", GEN.read_text(), flags=re.M)
    )
    return {k: v.replace("\\_", "_") for k, v in raw.items()}


@pytest.fixture(scope="module")
def art():
    s = json.loads((ART / "summary.json").read_text())
    p = json.loads((ART / "provenance.json").read_text())
    proj = json.loads((PAPER / "data" / "projection_v060.json").read_text())
    runs = [json.loads(line) for line in (ART / "lifecycle_runs.jsonl").read_text().splitlines()]
    runs = [r for r in runs if r.get("record_type") != "provenance" and "steps" in r]
    return s, p, proj, runs


@pytest.fixture(scope="module")
def land():
    return json.loads((PAPER / "data" / "land_v060.json").read_text())


def _strip(text: str) -> str:
    text = re.sub(r"\\[{}%]", "", text)  # escaped braces / percent are not structure
    return re.sub(r"(?<!\\)%.*", "", text)  # comments


# --------------------------------------------------------------------------- freshness
def test_generated_file_is_fresh():
    r = subprocess.run(
        [sys.executable, "scripts/paper/fill_v060_numbers.py", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr + r.stdout


def test_check_is_cwd_independent(tmp_path):
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts/paper/fill_v060_numbers.py"), "--check"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr + r.stdout


# --------------------------------------------------------------------------- macro <-> key path
def test_every_result_macro_is_pinned_to_an_artifact_key(fv, macros, art, land):
    s, p, proj, runs = art
    pr = s["preregistered"]
    h4 = {(r["dataset"], r["component"]): r for r in pr["H4"]["all_six"]}
    d4 = pr["H4"]["descriptive"]
    st = pr["H2"]["strata"]
    log = [c for c in p["llm_call_log"] if not c.get("cache_hit")]
    rep = p["llm_report"]
    f = fv.f
    expect: dict[str, str] = {
        "resRunId": p["run_id"],
        "resGitSha": p["git_sha"][:7],
        "resPreregVersion": p["prereg_version"],
        "resGitDirty": str(p["git_dirty"]).lower(),
        "resRunPython": str(p["python"]),
        "resHThreeEntropy": f(pr["H3"]["value"]),
        "resHThreeCeiling": f(pr["H3"]["ceiling_nats"]),
        "resHThreePickLinear": str(pr["H3"]["pick_counts"]["linear"]),
        "resHThreePickMlp": str(pr["H3"]["pick_counts"]["mlp"]),
        "resHThreePickScgpt": str(pr["H3"]["pick_counts"]["scgpt_small"]),
        "resHThreeNSteps": str(pr["H3"]["n_llm_architect_steps"]),
        "resHThreeExecNeStated": str(pr["H3"]["n_executed_ne_stated"]),
        "resHThreeNModels": str(pr["H3"]["n_distinct_model_ids"]),
        "resHThreeExecPickLinear": str(pr["H3"]["executed_pick_counts"]["linear"]),
        "resHThreeExecPickMlp": str(pr["H3"]["executed_pick_counts"]["mlp"]),
        "resHThreeExecPickScgpt": str(pr["H3"]["executed_pick_counts"]["scgpt_small"]),
        "resHThreeEntropyExecuted": f(pr["H3"]["entropy_executed_nats"]),
        "resHThreeNCounted": str(pr["H3"]["n_counted"]),
        "resHThreeNMissingStated": str(pr["H3"]["n_missing_stated"]),
        "resHThreeNMissingExecuted": str(pr["H3"]["n_missing_executed"]),
        "resHThreeNOffMenu": str(pr["H3"]["n_off_menu_stated"]),
        "resHThreeSmallestBreakdownN": str(min(v["n"] for v in pr["H3"]["by_model_id"].values())),
        "resHThreeMenuSize": str(len(pr["H3"]["menu"])),
        "resHThreeMillerMadowNats": f(
            pr["H3"]["miller_madow_nats"]
            if pr["H3"]["miller_madow_nats"] is not None
            else pr["H3"]["value"] + (len(pr["H3"]["menu"]) - 1) / (2 * pr["H3"]["n_counted"])
        ),
        "resHThreeMillerMadow": "not applicable"
        if all(v["n"] >= 50 for v in pr["H3"]["by_model_id"].values())
        else "; ".join(
            f"{k}: {f(v['miller_madow_nats'])}"
            for k, v in pr["H3"]["by_model_id"].items()
            if v["n"] < 50
        ),
        "resHFourNPassing": str(pr["H4"]["n_tests_passing"]),
        "resHFourNTests": str(pr["H4"]["n_tests"]),
        "resHFourRunsUndefined": "0",
        "resHFourTasksDropped": "0",
        "resHFiveRho": f(pr["H5"]["value"]),
        "resHFiveN": str(pr["H5"]["n"]),
        "resHFiveNFit": str(pr["H5"]["n_fit"]),
        "resHFiveCILo": f(pr["H5"]["ci_low"]),
        "resHFiveCIHi": f(pr["H5"]["ci_high"]),
        "resHFiveWAce": f(pr["H5"]["weights"]["ace_norm"], 2),
        "resHFiveWDc": f(pr["H5"]["weights"]["one_minus_delta_c"], 2),
        "resHFiveStdMeanAce": f(pr["H5"]["standardise_mean"]["ace_norm"], 4),
        "resHFiveStdSdAce": f(pr["H5"]["standardise_sd"]["ace_norm"], 4),
        "resHFiveStdMeanDc": f(pr["H5"]["standardise_mean"]["one_minus_delta_c"], 4),
        "resHFiveStdSdDc": f(pr["H5"]["standardise_sd"]["one_minus_delta_c"], 4),
        "resHFiveThreshold": f(pr["H5"]["threshold"], 1),
        "resTallyPass": str(pr["tally"]["PASS"]),
        "resTallyFail": str(pr["tally"]["FAIL"]),
        "resTallyUneval": str(pr["tally"]["UNEVALUATED"]),
        "resTallyOut": str(pr["tally"]["out_of"]),
        "resNLifecycleRuns": str(s["n_lifecycle_runs"]),
        "resNTrainerRuns": str(s["n_trainer_runs"]),
        "resNTasks": str(s["n_tasks_analysed"]),
        "resNSteps": str(s["n_steps_llm"]),
        "resNFallback": str(s["n_steps_fallback"]),
        "resNStepsMock": str(s["n_steps_mock"]),
        "resNStepsUnknown": str(s["n_steps_unknown"]),
        "resNCalls": str(rep["calls"]),
        "resStopEndTurn": str(rep["stop_reason_counts"]["end_turn"]),
        "resStopMaxTokens": str(rep["stop_reason_counts"]["max_tokens"]),
        "resServedMismatch": str(rep["served_mismatch_count"]),
        "resRefusals": str(sum(1 for c in p["llm_call_log"] if c["stop_reason"] == "refusal")),
        "resCacheStart": str(p["llm_cache_entries_at_start"]),
        "resCacheHits": str(p["llm_cache_hit_count"]),
        "resReplay": str(p["replay"]).lower(),
        "resSpendLLM": f(p["llm_cost_usd"], 2),
        "resSpendGPU": f(p["gpu_cost_usd"], 2),
        "resSpendPrior": f(p["prior_spend_usd"], 4),
        "resSpendPreflight": f(p["preflight_spend_usd"], 4),
        "resSpendTotal": f(p["cost_usd_actual"], 2),
        "resGPUHours": f(p["gpu_seconds"] / 3600, 2),
        "resSpendStopLine": f(p["entrypoint_kwargs"]["spend_stop_usd"], 0),
        "resKillLine": f(p["budget_cap_usd"], 0),
        "resSpendHaiku": f(rep["by_model"]["claude-haiku-4-5-20251001"], 2),
        "resSpendSonnet": f(rep["by_model"]["claude-sonnet-5-5"], 2),
        "resTokensIn": f"{sum(c['input_tokens'] for c in p['llm_call_log']):,}",
        "resTokensOut": f"{sum(c['output_tokens'] for c in p['llm_call_log']):,}",
        "resRosterHaiku": "claude-haiku-4-5-20251001",
        "resRosterSonnet": "claude-sonnet-5-5",
        "resStopReasonNone": "none" if p["stop_reason"] is None else str(p["stop_reason"]),
        "resNTrainerRecordsPerTask": str(p["trainer_grid"]["n_records_per_task"]),
        "resNDistinctConfigs": str(p["trainer_grid"]["n_distinct_configs_per_task"]),
        "resNDistinctFits": str(p["trainer_grid"]["n_distinct_fits_per_task"]),
        "resProjLLM": f(proj["llm_usd"], 2),
        "resProjGPU": f(proj["gpu_usd"], 2),
        "resProjTotal": f(proj["total_usd"], 2),
        "resProjLatency": f(proj["gpu_latency_per_round_s"], 1),
        "resCeilingLine": f(proj["ceiling_usd"], 0),
        "resPriceHaikuIn": f(p["llm_price_table"]["claude-haiku-4-5-20251001"]["input"], 2),
        "resPriceHaikuOut": f(p["llm_price_table"]["claude-haiku-4-5-20251001"]["output"], 2),
        "resPriceSonnetIn": f(p["llm_price_table"]["claude-sonnet-5-5"]["input"], 2),
        "resPriceSonnetOut": f(p["llm_price_table"]["claude-sonnet-5-5"]["output"], 2),
        "resHVGEntropy": f(p["entropies"]["architect_hvg_entropy_nats"]),
        "resHVGDistinctApplied": str(
            len({rd["values"]["hvg_count"] for r in runs for rd in r["applied_config_per_round"]})
        ),
        "resHVGAppliedValue": str(
            sorted(
                {rd["values"]["hvg_count"] for r in runs for rd in r["applied_config_per_round"]}
            )[0]
        ),
        "resNRoundsTotal": str(sum(len(r["applied_config_per_round"]) for r in runs)),
        "resValidatorSourcedRounds": str(
            sum(
                1
                for r in runs
                for rd in r["applied_config_per_round"]
                if "validator" in rd["sources"].values()
            )
        ),
        "resNValidatorSteps": str(
            sum(1 for r in runs for st in r["steps"] if st["agent_name"] == "Validator")
        ),
        "resValidatorAccepted": str(
            sum(
                1
                for r in runs
                for st in r["steps"]
                if st["agent_name"] == "Validator" and st["validator_accepted"] is True
            )
        ),
        "resValidatorRejected": str(
            sum(
                1
                for r in runs
                for st in r["steps"]
                if st["agent_name"] == "Validator" and st["validator_accepted"] is False
            )
        ),
        "resNFailover": str(
            sum(
                1
                for c in log
                if c["requested_model"]
                != (
                    "claude-sonnet-5-5" if c["role"] == "Validator" else "claude-haiku-4-5-20251001"
                )
            )
        ),
        "resLivenessOkPairs": str(
            sum(
                1
                for mdl in p["llm_roster_liveness"].values()
                for r in mdl["roles"].values()
                if r["ok"]
            )
        ),
        "resLivenessTotalPairs": str(
            sum(len(mdl["roles"]) for mdl in p["llm_roster_liveness"].values())
        ),
        "resRROneDate": "2026-10-08",
        "resRRTwoDate": "2026-10-13",
        "resManifestShaSuperseded": "323af965b631ce83",
        "resRROneFileCount": "6",
        "resLandSha": land["land_git_sha"],
        "resLandPR": str(land["pr_number"]),
        "resPostRunPathCount": str(len(land["post_run_changed_paths"])),
        "resThinkingHaiku": "off",  # recorded "none", in words
        "resThinkingSonnet": {"between_tools": "on between tool calls"}[
            p["llm_report"]["thinking"]["claude-sonnet-5-5"]["thinking"]["type"]
        ],
        "resEffortSonnet": p["llm_report"]["thinking"]["claude-sonnet-5-5"]["effort"],
        "resTemperatureHaiku": f(
            p["llm_report"]["sampling"]["claude-haiku-4-5-20251001"]["temperature"], 1
        ),
        "resSamplingSonnet": "API defaults",
        "resEvalGeneTasks": str(len(s["eval_genes_per_task"])),
        "resEvalGeneMismatch": str(len(s["eval_gene_mismatch_tasks"])),
    }
    for g, name in (("H1", "HOne"), ("H2", "HTwo")):
        r = pr[g]
        expect.update(
            {
                f"res{name}Median": f(r["value"]),
                f"res{name}N": str(r["n"]),
                f"res{name}IQRLo": f(r["iqr"][0]),
                f"res{name}IQRHi": f(r["iqr"][1]),
                f"res{name}Max": f(r["max"]),
                f"res{name}FracOver": f(r["fraction_over_gate"], 2),
                f"res{name}CILo": f(r["ci_low"]),
                f"res{name}CIHi": f(r["ci_high"]),
                f"res{name}Threshold": f(r["threshold"], 2),
            }
        )
    for k, name in (("singleton", "Singleton"), ("doublet", "Doublet")):
        expect.update(
            {
                f"resHTwo{name}N": str(st[k]["n"]),
                f"resHTwo{name}Median": f(st[k]["median"]),
                f"resHTwo{name}IQRLo": f(st[k]["iqr"][0]),
                f"resHTwo{name}IQRHi": f(st[k]["iqr"][1]),
                f"resHTwo{name}Max": f(st[k]["max"]),
                f"resHTwo{name}FracOver": f(st[k]["fraction_over_gate"], 2),
            }
        )
    for ds, dn in (("adamson_full", "Ada"), ("norman", "Nor")):
        for comp, cn in (
            ("ace_norm", "Ace"),
            ("one_minus_delta_c", "Dc"),
            ("tdi_lifecycle", "Tdi"),
        ):
            row = h4[(ds, comp)]
            expect.update(
                {
                    f"resHFour{dn}{cn}Rho": f(row["rho"]),
                    f"resHFour{dn}{cn}N": str(row["n"]),
                    f"resHFour{dn}{cn}CILo": f(row["ci_low"]),
                    f"resHFour{dn}{cn}CIHi": f(row["ci_high"]),
                    f"resHFour{dn}{cn}Pass": "undefined"
                    if row["passes"] is None
                    else ("yes" if row["passes"] else "no"),
                }
            )
            expect[f"resHFourPooled{cn}Rho"] = f(pr["H4"]["pooled_descriptive"][comp]["rho"])
        for comp, cn in (
            ("ace_norm_softmax", "AceSoftmax"),
            ("one_minus_delta_c_clipped", "DcClipped"),
        ):
            row = d4[ds][comp]
            expect.update(
                {
                    f"resHFour{dn}{cn}Rho": f(row["rho"]),
                    f"resHFour{dn}{cn}N": str(row["n"]),
                    f"resHFour{dn}{cn}CILo": f(row["ci_low"]),
                    f"resHFour{dn}{cn}CIHi": f(row["ci_high"]),
                }
            )
    for role, word in (
        ("DataCurator", "Curator"),
        ("Literature", "Literature"),
        ("Architect", "Architect"),
        ("Trainer", "Trainer"),
        ("Validator", "Validator"),
    ):
        expect[f"resCeiling{word}"] = str(rep["role_ceilings"][role])
        served = {c["served_model"] for c in log if c["role"] == role}
        assert len(served) == 1, (role, served)
        expect[f"resRoleServed{word}"] = served.pop()
        expect[f"resRoleCalls{word}"] = str(sum(1 for c in log if c["role"] == role))
    am = json.loads((PAPER / "data" / "amendments_v060.json").read_text())["amendments"]
    for a in am:
        word = WORDS[a["id"]]
        expect[f"resAmend{word}Version"] = a["prereg_version"] or r"\textemdash"
        expect[f"resAmend{word}Date"] = a["lock_date_utc"]
        expect[f"resAmend{word}Commit"] = ", ".join(a["lock_commits"])
        expect[f"resAmend{word}Note"] = a["lock_note"]
        expect[f"resAmend{word}Change"] = a["change"]
    s5 = json.loads((ROOT / "artifacts" / "v0.5.0" / "summary.json").read_text())
    p5 = json.loads((ROOT / "artifacts" / "v0.5.0" / "provenance.json").read_text())
    dist = s5["architect_backbone_distribution"]
    expect.update(
        {
            "resVFiveRecordCommit": json.loads((PAPER / "data" / "v050_record.json").read_text())[
                "record_commit"
            ],
            "resVFiveAdamsonMedian": f(s5["median_msd_adamson"]),
            "resVFiveNormanMedian": f(s5["median_msd_norman"]),
            "resVFiveNTasks": str(s5["n_tasks_analysed"]),
            "resVFiveNTrainerRuns": f"{s5['n_trainer_runs']:,}".replace(",", "\\,"),
            "resVFiveConfigsPerTask": str(s5["n_trainer_runs"] // s5["n_tasks_analysed"]),
            "resVFiveNLifecycleRuns": str(s5["n_lifecycle_runs"]),
            "resVFiveBackboneEntropy": f(s5["architect_backbone_entropy_nats"], 2),
            "resVFiveHVGEntropy": f(s5["architect_hvg_entropy_nats"], 2),
            "resVFiveNPicks": str(sum(dist.values())),
            "resVFiveScgptSharePct": f(100 * dist["scgpt_small"] / sum(dist.values()), 0),
            "resVFiveSpend": f(p5["total_cost_usd"], 2),
            "resVFiveGPUHours": f(p5["total_gpu_seconds"] / 3600, 2),
            "resVFiveBudgetCap": f(p5["budget_cap_usd"], 0),
        }
    )
    missing = sorted(set(expect) - set(macros))
    assert not missing, missing
    wrong = {k: (macros[k], v) for k, v in expect.items() if macros[k] != v}
    assert not wrong, wrong
    # every macro the generator emits is either pinned above or a verdict/summary/hash macro
    unpinned = sorted(
        k
        for k in macros
        if k not in expect
        and not re.fullmatch(
            r"res(H(One|Two|Three|Four|Five)Verdict|GateSummary|ManifestSha|ArchiveSha(Cache|Outputs))",
            k,
        )
    )
    assert not unpinned, unpinned


def test_verdicts_and_gate_summary(macros, art):
    s, *_ = art
    pr = s["preregistered"]
    for g, name in (
        ("H1", "HOne"),
        ("H2", "HTwo"),
        ("H3", "HThree"),
        ("H4", "HFour"),
        ("H5", "HFive"),
    ):
        want = {True: "supported", False: "not supported", None: "not evaluable"}[pr[g]["pass"]]
        assert macros[f"res{name}Verdict"] == want, g
    assert macros["resGateSummary"] == (
        "four of the five pre-registered hypotheses are supported and the cross-dataset transfer "
        "hypothesis is not; every hypothesis could be evaluated"
    )
    # HACA-119: an English sentence, with no hypothesis label and no capitalised status word
    assert not re.search(r"\bH[1-5]\b|PASS|FAIL|UNEVALUATED", macros["resGateSummary"])
    assert macros["resManifestSha"] != "n/a" and macros["resArchiveShaCache"] != "n/a"


def test_verdict_none_is_unevaluated(fv):
    assert fv.verdict(None) == "not evaluable"
    assert fv.verdict(True) == "supported" and fv.verdict(False) == "not supported"


GATE_CASES = [
    ({}, "all five pre-registered hypotheses are supported; every hypothesis could be evaluated"),
    (
        {"H5": False},
        "four of the five pre-registered hypotheses are supported and the cross-dataset transfer "
        "hypothesis is not; every hypothesis could be evaluated",
    ),
    (
        {"H2": False, "H3": False, "H4": False, "H5": False},
        "one of the five pre-registered hypotheses is supported and the attainable-error hypothesis "
        "on Norman, the backbone-choice hypothesis, the trace-feature ranking hypothesis and the "
        "cross-dataset transfer hypothesis are not; every hypothesis could be evaluated",
    ),
    (
        {g: False for g in ("H1", "H2", "H3", "H4", "H5")},
        "none of the five pre-registered hypotheses is supported; every hypothesis could be evaluated",
    ),
    (
        {g: None for g in ("H1", "H2", "H3", "H4", "H5")},
        "none of the five pre-registered hypotheses could be evaluated",
    ),
    (
        {"H1": False, "H5": False, "H3": None},
        "two of the five pre-registered hypotheses are supported and the attainable-error hypothesis "
        "on Adamson and the cross-dataset transfer hypothesis are not; the backbone-choice "
        "hypothesis could not be evaluated",
    ),
    (
        {"H5": None},
        "four of the five pre-registered hypotheses are supported; the cross-dataset transfer "
        "hypothesis could not be evaluated",
    ),
]


@pytest.mark.parametrize("patch,want", GATE_CASES)
def test_gate_summary_sentence_covers_every_outcome_mix(fv, patch, want):
    outcomes = {**{g: True for g in fv.HYPOTHESIS_NAMES}, **patch}
    got = fv.gate_summary(outcomes, 5)
    assert got == want
    assert not re.search(r"\bH[1-5]\b|PASS|FAIL|UNEVALUATED|\bno of\b", got)


def test_gate_summary_refuses_malformed_outcomes(fv):
    ok = {g: True for g in fv.HYPOTHESIS_NAMES}
    with pytest.raises(ValueError):
        fv.gate_summary(ok, 6)
    with pytest.raises(ValueError):
        fv.gate_summary({**ok, "H6": True}, 5)
    with pytest.raises(ValueError):
        fv.gate_summary({**ok, "H3": 1}, 5)  # an integer is not an outcome
    with pytest.raises(ValueError):
        fv.verdict(0)


def test_tally_that_disagrees_with_the_outcomes_is_refused(fv, tmp_path):
    def patch(s):
        s["preregistered"]["tally"] = {"PASS": 5, "FAIL": 0, "UNEVALUATED": 0, "out_of": 5}

    with pytest.raises(ValueError, match="tally disagrees"):
        _patched_build(fv, tmp_path, patch)


def test_numeric_invariants(macros):
    def num(k):
        return float(re.sub(r"[^0-9.\-]", "", macros[k]))

    for pre in ("HOne", "HTwo"):
        assert (
            num(f"{'res' + pre}IQRLo")
            <= num(f"res{pre}Median")
            <= num(f"res{pre}IQRHi")
            <= num(f"res{pre}Max")
        )
        assert num(f"res{pre}CILo") <= num(f"res{pre}Median") <= num(f"res{pre}CIHi")
    for key in (
        "HFourAdaAce",
        "HFourAdaDc",
        "HFourAdaTdi",
        "HFourNorAce",
        "HFourNorDc",
        "HFourNorTdi",
        "HFourAdaAceSoftmax",
        "HFourAdaDcClipped",
        "HFourNorAceSoftmax",
        "HFourNorDcClipped",
        "HFive",
    ):
        assert num(f"res{key}CILo") <= num(f"res{key}Rho") <= num(f"res{key}CIHi"), key
    assert int(macros["resHThreePickLinear"]) + int(macros["resHThreePickMlp"]) + int(
        macros["resHThreePickScgpt"]
    ) == int(macros["resHThreeNSteps"])
    assert int(macros["resStopEndTurn"]) + int(macros["resStopMaxTokens"]) == int(
        macros["resNCalls"]
    )
    assert (
        abs(num("resSpendLLM") + num("resSpendGPU") + num("resSpendPrior") - num("resSpendTotal"))
        < 0.011
    )
    assert (
        abs(
            num("resSpendHaiku")
            + num("resSpendSonnet")
            + num("resSpendPreflight")
            - num("resSpendLLM")
        )
        < 0.011
    )
    assert int(macros["resValidatorAccepted"]) + int(macros["resValidatorRejected"]) == int(
        macros["resNValidatorSteps"]
    )
    assert int(macros["resNTrainerRuns"]) == int(macros["resNTrainerRecordsPerTask"]) * int(
        macros["resNTasks"]
    )


def test_no_placeholder_values(macros):
    bad = {k: v for k, v in macros.items() if v.strip() in {"", "n/a", "nan", "None"} or "\n" in v}
    assert not bad, bad


def test_negative_values_use_a_real_minus(macros):
    for k, v in macros.items():
        assert not re.match(r"-\d", v), (
            k,
            v,
        )  # a bare hyphen would typeset as a hyphen in text mode
        if r"\ensuremath{-" in v:
            assert re.fullmatch(r"\\ensuremath\{-\d+\.\d+\}", v), (k, v)


# --------------------------------------------------------------------------- generator behaviour on other artifacts
def _patched_build(fv, tmp_path, patch):
    art = tmp_path / "art"
    shutil.copytree(ART, art)
    s = json.loads((art / "summary.json").read_text())
    patch(s)
    (art / "summary.json").write_text(json.dumps(s))
    return fv.build(
        art,
        PAPER / "data" / "projection_v060.json",
        ROOT / "configs" / "runs" / "20260929T035447Z-ce5f237.json",
        [],
    )


def test_fallback_count_follows_the_artifact(fv, tmp_path):
    m = _patched_build(fv, tmp_path, lambda s: s.__setitem__("n_steps_fallback", 3))
    assert m["NFallback"] == "3"


def test_trainer_run_count_follows_the_artifact(fv, tmp_path):
    m = _patched_build(fv, tmp_path, lambda s: s.__setitem__("n_trainer_runs", 1100))
    assert m["NTrainerRuns"] == "1100"


def test_unevaluated_gate_is_not_typeset_as_fail(fv, tmp_path):
    def patch(s):
        s["preregistered"]["H5"]["pass"] = None
        s["preregistered"]["tally"] = {"PASS": 4, "FAIL": 0, "UNEVALUATED": 1, "out_of": 5}
        for row in s["preregistered"]["H4"]["all_six"]:
            row["passes"] = None

    m = _patched_build(fv, tmp_path, patch)
    assert m["HFiveVerdict"] == "not evaluable"
    assert "not supported" not in m["HFiveVerdict"] and "is not" not in m["GateSummary"]
    assert m["GateSummary"] == (
        "four of the five pre-registered hypotheses are supported; the cross-dataset transfer "
        "hypothesis could not be evaluated"
    )
    assert m["HFourAdaAcePass"] == "undefined"


def test_missing_manifest_is_an_error(fv, tmp_path):
    with pytest.raises(FileNotFoundError):
        fv.build(ART, PAPER / "data" / "projection_v060.json", tmp_path / "missing.json", [])
    with pytest.raises(FileNotFoundError):
        fv.build(
            ART,
            PAPER / "data" / "projection_v060.json",
            ROOT / "configs" / "runs" / "20260929T035447Z-ce5f237.json",
            [tmp_path / "missing-archive.json"],
        )


def test_render_refuses_unsafe_values(fv):
    assert r"\newcommand{\resStopReasonNone}{spend\_stop}" in fv.render(
        {"StopReasonNone": "spend_stop"}
    )
    with pytest.raises(ValueError):
        fv.render({"RunId": "a%b"})
    with pytest.raises(ValueError):
        fv.render({"RunId": "a\nb"})
    assert r"\newcommand{\resHOneVerdict}{not supported}" in fv.render(
        {"HOneVerdict": "not supported"}
    )


# --------------------------------------------------------------------------- manuscript guards
def test_no_pending_placeholders_remain():
    for fpath in TEX_INPUTS + [PAPER / "README.md"]:
        assert "\\pending{" not in fpath.read_text(), fpath.name
        assert "PENDING" not in fpath.read_text(), fpath.name


def test_every_result_macro_used_is_defined_and_input_first(macros):
    for fpath in TEX_INPUTS:
        text = _strip(fpath.read_text())
        used = set(re.findall(r"\\(res[A-Z][A-Za-z]*)", text))
        assert not (used - set(macros)), (fpath.name, sorted(used - set(macros)))
        assert not re.search(r"\\res[A-Z][A-Za-z]*(?:[ \t]+[A-Za-z(]|\d)", text), (
            fpath.name
        )  # swallowed space / digit
        assert not re.search(
            r"\\(re)?newcommand\{\\res|\\def\\res|\\providecommand\{\\res", text
        ), fpath.name
    main = MAIN.read_text()
    assert main.index("\\input{sections/generated_numbers}") < main.index("\\res")
    names = re.findall(r"\\newcommand\{\\(res[A-Za-z]+)\}", GEN.read_text())
    assert len(names) == len(set(names))


@pytest.mark.parametrize(
    "rel",
    [
        "sections/results.tex",
        "sections/experimental_setup.tex",
        "paper.tex",
        "sections/corrections.tex",
    ],
)
def test_no_hand_typed_result_numbers(rel):
    """Any decimal literal in result-bearing prose must be a pre-registered constant, not a sweep value."""
    text = _strip((PAPER / rel).read_text())
    text = re.sub(r"\{[\d.]+\\linewidth\}", "", text)  # column / minipage widths
    text = re.sub(
        r"\\setlength\{[^}]*\}\{[^}]*\}", "", text
    )  # preamble lengths (e.g. emergencystretch)
    text = re.sub(r"[\d.]+(em|pt|ex)\b", "", text)  # layout lengths (e.g. leftmargin=1.2em)
    text = re.sub(r"(Haiku|Sonnet|Opus|Apache-)\s*\d\.\d", "", text)  # model versions / licence
    text = re.sub(r"\bPython\s+3\.1[0-9]\b", "", text)  # interpreter versions only
    literals = set(re.findall(r"(?<![\w.])\d*\.\d+(?!\.\d)", text))
    name = Path(rel).name
    allowed = ALLOWED_LITERALS[name] | DESIGN_LITERALS[name]
    assert literals == allowed, (sorted(literals - allowed), sorted(allowed - literals))
    prereg = (PAPER / "PREREGISTRATION.md").read_text()
    for lit in ALLOWED_LITERALS[name]:
        assert lit in prereg, lit


def test_corrections_integers_are_macros_or_quoted_design_facts():
    """corrections.tex may hold integers only as design facts or labelled register quotes; result values are macros."""
    text = _strip(CORR.read_text())
    assert "$41$" not in text and "of 36 each" not in text and "$15+5$" not in text
    assert "\\resNTasks" in text and "\\resVFiveNTasks" in text and "\\resHTwoSingletonN" in text
    text = re.sub(r"\\res[A-Z][A-Za-z]*", "", text)
    text = re.sub(
        r"\\(path|texttt|ref|label|cite[pt]?)\{[^}]*\}", "", text
    )  # paths, code, references
    text = re.sub(
        r"\\#\d+|DF-\d+|RR-\d+|SHA-256|[\d.]+(em|pt|ex)\b|\d\.\d+", "", text
    )  # register ids, lengths, decimals
    ints = set(re.findall(r"(?<![\w.\\])\d+(?![\w.])", text))
    allowed = {
        "2",
        "3",
        "4",
        "5",
        "7",
        "8",
        "15",
        "91",
    }  # shared tasks, seeds, digests, register quotes
    assert ints <= allowed, sorted(ints - allowed)


def test_braces_balanced():
    for fpath in TEX_INPUTS + [GEN]:
        depth = 0
        for ch in _strip(fpath.read_text()):
            depth += ch == "{"
            depth -= ch == "}"
            assert depth >= 0, fpath.name
        assert depth == 0, fpath.name


def test_prose_claims_match_artifacts(art, land):
    """Qualitative sentences that depend on artifact facts are pinned to those facts."""
    s, p, _, runs = art
    pr = s["preregistered"]
    res, setup, main = RESULTS.read_text(), SETUP.read_text(), MAIN.read_text()
    six = {(r["dataset"], r["component"]): r for r in pr["H4"]["all_six"]}
    # gate outcomes named in the abstract / results
    assert [pr[g]["pass"] for g in ("H1", "H2", "H3", "H4")] == [True] * 4 and pr["H5"][
        "pass"
    ] is False
    flat_main = " ".join(main.split())
    assert "The transfer hypothesis is not supported" in flat_main and "\\resGateSummary" in main
    # caption: 1-dC and TDI pass in both datasets, both ACE tests fail
    assert all(
        six[(d, c)]["passes"]
        for d in ("adamson_full", "norman")
        for c in ("one_minus_delta_c", "tdi_lifecycle")
    )
    assert all(
        not six[(d, "ace_norm")]["passes"] and six[(d, "ace_norm")]["rho"] < 0
        for d in ("adamson_full", "norman")
    )
    assert "$1-\\Delta C$ and\n$\\mathrm{TDI}_{\\mathrm{lifecycle}}$ in both datasets" in res
    # ACE sign: Adamson CI excludes zero, Norman CI includes zero — the prose says exactly that
    assert six[("adamson_full", "ace_norm")]["ci_high"] < 0 < six[("norman", "ace_norm")]["ci_high"]
    assert "Norman CI includes zero" in res and "exploratory" in res
    assert "correlates negatively" not in main.lower() and "not through" not in main
    # doublet stratum above the gate while the all-task median passes
    assert pr["H2"]["strata"]["doublet"]["median"] > pr["H2"]["threshold"] > pr["H2"]["value"]
    assert "lies above the criterion" in res
    # run-record facts
    assert (
        s["n_steps_fallback"] == s["n_steps_mock"] == s["n_steps_unknown"] == 0
        and "all LLM-sourced" in res
    )
    assert {r["n_rounds"] for r in runs} == {3} and "exactly three rounds" in res
    assert pr["H3"]["n_executed_ne_stated"] == 0 and "on every step" in res
    assert pr["H3"]["n_distinct_model_ids"] == 1 and "one model" in res
    assert p["llm_report"]["stop_reason_counts"]["max_tokens"] == 1 and "retried once" in res
    assert (
        p["stop_reason"] is None and p["cost_usd_actual"] < p["entrypoint_kwargs"]["spend_stop_usd"]
    )
    assert "Neither line was reached" in res
    assert {rd["values"]["hvg_count"] for r in runs for rd in r["applied_config_per_round"]} == {
        2000
    }
    assert "every applied choice was \\resHVGAppliedValue" in setup
    assert (
        p["gpu_cost_usd"] > 2.90
        and p["llm_cost_usd"] > 2.93
        and "both came in above the projection" in setup
    )
    assert (
        "\\resHFourAdaAceN" in main and "\\resHFourNorAceN" in main
    )  # Limitations n, not hand-typed
    # deposit gate (CTO #509/#526): run vs landed revision stated from the land record, with the
    # reproduction check; since HACA-119 it is stated once, in Reproducibility (paper.tex)
    assert "\\resLandSha" in main and "\\resPostRunPathCount" in main and "\\resLandPR" in main
    assert "reproduces every committed value" in main and "\\path{served_mismatch_count}" in main
    assert (
        "code paths the run did not reach" in main
        and "revision at which v0.6.0 was merged into the repository's main branch" in flat_main
        and "pull request~\\resLandPR" in main  # the number is introduced in words
    )
    flat_res = " ".join(_strip(res).split())
    assert "\\resLandSha" not in flat_res and "reproduces every committed value" not in flat_res
    para = main[main.index("\\resLandSha") : main.index("reproduces every committed value")]
    named = re.findall(r"\\path\{((?:src|scripts/modal)/[^}]*\.py)\}", para)
    assert sorted(named) == sorted(land["post_run_changed_paths"]), named
    assert land["run_git_sha"] == p["git_sha"][:7] and land["land_git_sha"] != land["run_git_sha"]
    for path in land["post_run_changed_paths"]:
        assert (ROOT / path).exists(), path


def test_methods_wording_matches_the_amendments():
    setup, main, res, readme = (
        SETUP.read_text(),
        MAIN.read_text(),
        RESULTS.read_text(),
        (PAPER / "README.md").read_text(),
    )
    # A2-7: the draw as implemented
    assert "topped up" in setup and "per-pool total" in setup
    assert (
        "every stratum is filled exactly" not in setup and "a stratum cannot be filled" not in main
    )
    # A3-2 / A3-3: Validator threshold gates the rule-based delta; the LLM Validator's own delta is not applied
    assert "recorded, not acted on" not in setup
    flat_setup = " ".join(setup.split())
    assert (
        "that decision selects a rule-based adjustment to the configuration" in flat_setup
        and "suggested adjustment is recorded and \\emph{not} applied" in flat_setup
    )
    # A4-1 / A4-3 / A2-8 / A2-1
    assert "H3 condition is unchanged" not in setup
    assert (
        "non-default sampling" in setup
        and "arrays of key--value pairs" in setup
        and "modality" in setup
        and "non-finite" in setup
    )
    assert "single model family" in setup and "same-family" in setup
    assert "ran over because" not in setup and "GPU line" not in setup
    assert "dry run" in setup
    # descriptive H4 rows and the H5 standardisation are present
    assert "\\resHFourAdaAceSoftmaxRho" in res and "\\resHFourNorDcClippedRho" in res
    assert "\\resHFiveStdMeanAce" in res and "\\resHFiveStdSdAce" in res
    assert "not computed" in res  # per-role distinct-proposal counts
    assert (
        "a statement about the\npool" in res
        and "Executed-pick counts" in res
        and "Miller--Madow" in res
    )
    assert (
        "\\resRoleServedValidator" in res and "\\resNFailover" in res and "\\resPriceHaikuIn" in res
    )
    # section Metrics points at the amended definitions (cited by the amendments table, not by code)
    assert (
        "Both changes were made by amendment before any data from this sweep existed "
        "(Table~\\ref{tab:amendments})"
        in " ".join(main.split())
        and "throughout"
        not in main[
            main.index("\\section{Metrics") : main.index(
                "\\section{", main.index("\\section{Metrics") + 1
            )
        ]
    )
    assert "generated_numbers" in readme and "\\pending" not in readme


def test_build_products_are_not_tracked():
    out = subprocess.run(
        [
            "git",
            "ls-files",
            "paper/paper.pdf",
            "paper/paper.aux",
            "paper/paper.log",
            "paper/paper.out",
            "paper/paper.blg",
            "paper/paper.bbl",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    assert out == [], out


def test_post_run_docs_and_prose_are_current():
    """After the sweep, nothing may still describe results as pending or the LLM condition as OpenRouter."""
    res, setup, main = RESULTS.read_text(), SETUP.read_text(), MAIN.read_text()
    assert (
        "\\path{eval_genes_per_task}" in MAIN.read_text()  # named in Reproducibility only
        and "\\resEvalGeneTasks" in res
        and "\\resEvalGeneMismatch" in res
    )
    assert "(HTTP status 401, 402, 403 or 404)" in setup
    assert "flagged as not implemented" in res and "not computed per stratum" in res
    assert (
        "\\sloppy " not in main and "\\sloppy\n" not in main
    )  # only the scoped sloppypar environment
    for rel, bad in (
        ("README.md", ("pending the v0.6.0 sweep",)),
        ("docs/THESIS.md", ("results are pending",)),
        ("CHANGELOG.md", ("sweep not yet run", "Results are placeholders")),
        ("LIVE_RUN.md", ()),
    ):
        text = (ROOT / rel).read_text()
        for phrase in bad:
            assert phrase not in text, (rel, phrase)
    assert "legacy" in (ROOT / "LIVE_RUN.md").read_text()[:600].lower()
    assert "anthropic_client.py" in (ROOT / "README.md").read_text()
    assert (
        "589d1e3b" not in (ROOT / "README.md").read_text()
        and "589d1e3b" not in (PAPER / "README.md").read_text()
    )
    app = (ROOT / "scripts" / "modal" / "app_v05.py").read_text()
    assert "free-tier" not in app and "589d1e3b" not in app
    assert (
        "ruling pending"
        not in (ROOT / "src/perturb_eval/agentic_lifecycle/architect_dispatch.py").read_text()
    )
    assert (
        "legacy" in (ROOT / "src/perturb_eval/llm/openrouter_client.py").read_text()[:400].lower()
    )


# --------------------------------------------------------------------------- land record vs git / generator
def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout


def test_post_run_paths_are_exactly_the_git_diff(land):
    """The paths the paper names as changed after the run are exactly git's answer (src + scripts/modal);
    a later src/modal change forces the land record and the sentence to be revisited."""
    _git("cat-file", "-e", f"{land['run_git_sha']}^{{commit}}")  # fails loudly on a shallow clone
    _git("merge-base", "--is-ancestor", land["land_git_sha"], "HEAD")
    changed = sorted(
        _git(
            "diff",
            "--name-only",
            "--relative",
            land["run_git_sha"],
            land["land_git_sha"],
            "--",
            "src",
            "scripts/modal",
        ).split()
    )
    assert changed == sorted(land["post_run_changed_paths"]), changed
    # After the land, only the recorded post-land paths (RR-1, D8) may differ (CTO #585), and never the analyser.
    after_land = sorted(
        _git(
            "diff",
            "--name-only",
            "--relative",
            land["land_git_sha"],
            "HEAD",
            "--",
            "src",
            "scripts/modal",
        ).split()
    )
    assert after_land == sorted(land["post_land_changed_paths"]), after_land
    assert "src/perturb_eval/experiments/e_v05_real_traces.py" not in after_land
    # ...and nothing under src/ or scripts/modal/ has changed since the last recorded code commit,
    # so a later edit to those files still forces this record to be revisited.
    _git("merge-base", "--is-ancestor", land["post_land_last_code_commit"], "HEAD")
    assert (
        _git(
            "diff",
            "--name-only",
            "--relative",
            land["post_land_last_code_commit"],
            "HEAD",
            "--",
            "src",
            "scripts/modal",
        ).split()
        == []
    )


def _build_with_land(fv, tmp_path, patch):
    ld = json.loads((PAPER / "data" / "land_v060.json").read_text())
    patch(ld)
    lp = tmp_path / "land.json"
    lp.write_text(json.dumps(ld))
    return fv.build(
        ART,
        PAPER / "data" / "projection_v060.json",
        ROOT / "configs" / "runs" / "20260929T035447Z-ce5f237.json",
        [],
        lp,
    )


@pytest.mark.parametrize("sha", ["deadbee", "5a45d4a", "ce5f238", "", "c"])
def test_land_record_for_another_run_is_rejected(fv, tmp_path, sha):
    with pytest.raises(ValueError):
        _build_with_land(fv, tmp_path, lambda d: d.__setitem__("run_git_sha", sha))


def test_land_sha_must_look_like_a_sha_and_differ_from_the_run(fv, tmp_path):
    with pytest.raises(ValueError):
        _build_with_land(fv, tmp_path, lambda d: d.__setitem__("land_git_sha", "see PR"))
    with pytest.raises(ValueError):
        _build_with_land(fv, tmp_path, lambda d: d.__setitem__("land_git_sha", d["run_git_sha"]))


def test_land_record_drives_the_land_macros(fv, tmp_path):
    n = len(json.loads((PAPER / "data" / "land_v060.json").read_text())["post_run_changed_paths"])

    def patch(d):
        d["land_git_sha"] = "abc1234"
        d["pr_number"] = 99
        d["post_run_changed_paths"].append("src/x.py")

    m = _build_with_land(fv, tmp_path, patch)
    assert (m["LandSha"], m["LandPR"], m["PostRunPathCount"]) == ("abc1234", "99", str(n + 1))


def test_landed_analyser_reproduces_the_committed_summary(tmp_path, art, fv):
    """The reproduction check the paper cites: the analyser at this revision, on the committed run files,
    reproduces every committed value; the only addition is served_mismatch_count = 0."""
    import os

    for name in ("trainer_runs.jsonl", "lifecycle_runs.jsonl", "provenance.json"):
        shutil.copy(ART / name, tmp_path / name)
    subprocess.run(
        [sys.executable, "-m", "perturb_eval.experiments.e_v05_real_traces", str(tmp_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
    )
    new = json.loads((tmp_path / "summary.json").read_text())
    assert new.pop("served_mismatch_count") == 0
    committed = art[0]
    # Every reported (rounded) value is identical: the macros built from the re-run summary
    # (before any tolerance below is applied) equal the macros built from the committed one.
    rerun = tmp_path / "rerun"
    rerun.mkdir()
    for name in ("lifecycle_runs.jsonl", "provenance.json"):
        shutil.copy(ART / name, rerun / name)
    (rerun / "summary.json").write_text(json.dumps(new))
    build_args = (
        PAPER / "data" / "projection_v060.json",
        ROOT / "configs" / "runs" / "20260929T035447Z-ce5f237.json",
        [],
        PAPER / "data" / "land_v060.json",
    )
    assert fv.build(rerun, *build_args) == fv.build(ART, *build_args)
    # The disclosed exception across numpy/BLAS builds (paper, Reproducibility; HACA-121/124):
    # these keys move by a few ulp with the build, so they must match within BLAS_MAX_ULP ulp,
    # element by element. Every other key stays exactly equal.
    import numpy as np

    for path in BLAS_ULP_PATHS:
        a, b = new, committed
        for k in path[:-1]:
            a, b = a[k], b[k]
        got, want = np.asarray(a[path[-1]], dtype=float), np.asarray(b[path[-1]], dtype=float)
        assert got.shape == want.shape, path
        try:
            np.testing.assert_array_max_ulp(got, want, maxulp=BLAS_MAX_ULP)
        except AssertionError as exc:
            # A new numpy/BLAS build, not necessarily a regression: name the build so it can
            # be recorded (tests/fixtures/numeric_environment.json) and the bound ruled on.
            raise AssertionError(f"{'/'.join(path)}: {exc}\n{header_line()}") from None
        a[path[-1]] = b[path[-1]]
    if sys.version_info < (3, 12):
        # The disclosed exception (paper, Reproducibility): before 3.12, float sum() is not
        # compensated, and exactly the backbone entropy (five keys) comes out one ulp HIGHER.
        import math

        moved = []
        for path in PY312_ENTROPY_PATHS:
            a, b = new, committed
            for k in path[:-1]:
                a, b = a[k], b[k]
            assert a[path[-1]] == math.nextafter(b[path[-1]], math.inf), path  # +1 ulp, exactly
            moved.append(a[path[-1]])
            a[path[-1]] = b[path[-1]]
        assert len(set(moved)) == 1  # one quantity, the same value in every key
    assert new == committed, sorted(
        k for k in set(new) | set(committed) if new.get(k) != committed.get(k)
    )


# The keys that move by a few ulp with the numpy/BLAS build (HACA-121): the H5 fit's weight
# on 1 - delta_c and its per-task Norman TDI scores. Observed: up to 4 ulp on the aarch64
# host (numpy 2.4.4, scipy-openblas 0.3.31), 2 on x86_64 CI; see
# tests/fixtures/numeric_environment.json. The bound (CTO ruling, HACA-124) equals the host's
# observed maximum, so a failure on a new build means: record the build, then rule on the bound.
BLAS_ULP_PATHS = (
    ("preregistered", "H5", "weights", "one_minus_delta_c"),
    ("preregistered", "H5", "norman_tdi"),
)
BLAS_MAX_ULP = 4
BLAS_DISCLOSURE = (
    "Across numpy and BLAS builds, two keys are reproduced to within four units in the last "
    "place rather than exactly: the cross-dataset ridge weight on $1-\\Delta C$ and the "
    "transferred index on each Norman task. Every reported value is identical."
)

# The one quantity that differs before Python 3.12 (paper: "five keys of summary.json").
PY312_ENTROPY_PATHS = (
    ("architect_backbone_entropy_nats",),
    ("architect_backbone_executed_entropy_nats",),
    ("preregistered", "H3", "by_model_id", "claude-haiku-4-5-20251001", "entropy_nats"),
    ("preregistered", "H3", "entropy_executed_nats"),
    ("preregistered", "H3", "value"),
)
PY312_DISCLOSURE = (
    "This holds on Python 3.12: Python 3.12 made the built-in \\texttt{sum()} over floats "
    "compensated, and before Python 3.12 the backbone entropy (stated and executed, which "
    "coincide here; five keys of \\texttt{summary.json}) comes out one unit in the last place "
    "higher. The run itself ran on Python \\resRunPython, and \\texttt{provenance.json} records "
    "that higher value. No reported figure or criterion outcome changes."
)


def test_reproduction_claim_states_its_python_requirement_and_cause():
    """CTO #629: wherever the paper claims the analyser reproduces summary.json, the claim is
    followed by the exact disclosure (requirement, cause, the run's own value), so an inverted,
    negated or relocated rewording fails, and the next editor cannot drop it as superstition."""
    assert len(PY312_ENTROPY_PATHS) == 5  # "five keys"
    # HACA-119: the claim is made exactly once across the manuscript, in Reproducibility
    # (paper.tex), and that copy carries the full disclosure.
    flat = {f.name: " ".join(_strip(f.read_text()).split()) for f in TEX_INPUTS}
    assert sum(t.count("reproduces every committed value") for t in flat.values()) == 1, flat.keys()
    assert flat["paper.tex"].count("reproduces every committed value") == 1
    claim_end = "reproduces every committed value of \\texttt{summary.json}. "
    assert claim_end + PY312_DISCLOSURE in flat["paper.tex"]
    # HACA-124: the ulp-bounded keys across numpy/BLAS builds are disclosed right after it.
    assert PY312_DISCLOSURE + " " + BLAS_DISCLOSURE in flat["paper.tex"]
    assert BLAS_MAX_ULP == 4 and len(BLAS_ULP_PATHS) == 2  # "four units", two named keys
    # Outside the paper, the same claim must carry the requirement too.
    changelog = " ".join((ROOT / "CHANGELOG.md").read_text().split())
    for m in re.finditer(r"reproduces the committed `summary\.json`", changelog):
        assert "Python 3.12" in changelog[m.start() : m.start() + 400], m.start()


# --------------------------------------------------------------------------- amendments / v0.5.0 record vs git and the register
def test_amendment_records_match_git_and_the_preregistration():
    am = json.loads((PAPER / "data" / "amendments_v060.json").read_text())["amendments"]
    prereg = (PAPER / "PREREGISTRATION.md").read_text()
    assert [a["id"] for a in am] == ["A1", "A2", "A3", "A4", "A5", "A6"]
    land = json.loads((PAPER / "data" / "land_v060.json").read_text())
    for a in am:
        n = a["id"][1]
        if a["prereg_version"]:
            assert f"## Amendment {n} (`prereg_version` = `{a['prereg_version']}`)" in prereg
        else:
            assert (
                f"Amendment {n} ({a['lock_date_utc']}, `{a['lock_commits'][0]}`)" in prereg
            )  # A1, named in the preamble
        first = a["lock_commits"][0]
        head_line = a["introduces"]  # the text the lock commit added to PREREGISTRATION.md
        assert head_line in _git(
            "show", f"{first}:projects/perturb-seq-eval/paper/PREREGISTRATION.md"
        )
        assert head_line not in _git(
            "show", f"{first}^:projects/perturb-seq-eval/paper/PREREGISTRATION.md"
        )
        for c in a["lock_commits"]:
            assert re.fullmatch(r"[0-9a-f]{7,40}", c), c
            before_run = (
                subprocess.run(
                    ["git", "merge-base", "--is-ancestor", c, land["run_git_sha"]], cwd=ROOT
                ).returncode
                == 0
            )
            # A1-A4 were locked before the run; A5 (approvals row 16) and A6 (approvals row 40)
            # were locked AFTER the outcome, and the record must say so rather than pass as a
            # pre-data amendment.
            assert before_run is not bool(a.get("post_outcome")), (a["id"], c)
            _git("merge-base", "--is-ancestor", c, "HEAD")  # on this history either way
            files = _git("show", "--name-only", "--format=", c)
            assert "paper/PREREGISTRATION.md" in files, c
            date = subprocess.run(
                ["git", "log", "-1", "--format=%cd", "--date=format-local:%Y-%m-%d", c],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
                env={**__import__("os").environ, "TZ": "UTC"},
            ).stdout.strip()
            assert date == a["lock_date_utc"], (c, date)
        assert (
            "\\" not in a["change"] and "{" not in a["change"]
        )  # typeset verbatim (`_` is escaped by render)
        assert (
            "1.3548" not in a["change"]
        )  # A4-2 states 1.3 carried in from the aborted run + the dry run separately
    a4 = next(a for a in am if a["id"] == "A4")
    # Compare FULL hashes: `%h` length follows git's auto-abbreviation, which grows with the
    # repository (7 chars when recorded, 8 later), so an abbreviated comparison breaks with no
    # change to the history it checks.
    assert sorted(
        _git(
            "log",
            "--format=%H",
            f"{a4['lock_commits'][0]}^..{land['run_git_sha']}",
            "--",
            "paper/PREREGISTRATION.md",
        ).split()
    ) == sorted(
        _git("rev-parse", "--verify", f"{c}^{{commit}}").strip() for c in a4["lock_commits"]
    )
    assert a4.get("lock_note")
    res = RESULTS.read_text()
    assert "\\label{tab:amendments}" in res and res.count("\\ref{tab:amendments}") >= 2
    assert SETUP.read_text().count("\\ref{tab:amendments}") >= 2


def test_v050_record_commit_and_register_quotes():
    vr = json.loads((PAPER / "data" / "v050_record.json").read_text())
    rc = vr["record_commit"]
    assert re.fullmatch(r"[0-9a-f]{7,40}", rc)
    added = _git(
        "log", "--format=%h", "--diff-filter=A", "--", "artifacts/v0.5.0/summary.json"
    ).split()
    assert added and added[-1].startswith(rc), added
    _git("merge-base", "--is-ancestor", rc, "HEAD")
    assert (
        _git("diff", "--name-only", rc, "HEAD", "--", "artifacts/v0.5.0").strip() == ""
    )  # record unchanged since
    register = (ROOT.parents[1] / vr["narrative_register"]).read_text()
    corr_text = CORR.read_text()
    for q in vr["narrative_quotes"]:
        assert q["register"] in register, q
        assert q["tex"] in corr_text, q
    corr = CORR.read_text()
    for mac in (
        "VFiveAdamsonMedian",
        "VFiveNormanMedian",
        "VFiveNTrainerRuns",
        "VFiveNLifecycleRuns",
        "VFiveBackboneEntropy",
        "VFiveScgptSharePct",
        "VFiveNPicks",
        "VFiveHVGEntropy",
        "VFiveSpend",
        "VFiveGPUHours",
        "VFiveRecordCommit",
    ):
        assert f"\\res{mac}" in corr, mac
    setup = SETUP.read_text()
    assert (
        "\\resThinkingSonnet" in setup and "\\resStopMaxTokens" in setup and "\\resNCalls" in setup
    )


def test_land_sha_is_the_pr_merge(land):
    full = _git("rev-parse", land["land_git_sha"]).strip()
    assert full == land["land_git_sha_full"]
    assert _git("log", "-1", "--format=%s", full).startswith(
        f"Merge pull request #{land['pr_number']} "
    )
    assert len(_git("log", "-1", "--format=%P", full).split()) == 2
    _git("merge-base", "--is-ancestor", land["run_git_sha"], full)


def test_render_number_allow_list(fv):
    assert r"\newcommand{\resX}{1\,944}" in fv.render({"X": "1\\,944"})
    assert r"\newcommand{\resX}{a\_b}" in fv.render({"X": "a_b"})
    for bad in ("1\\,94", "1\\,944x", "a%b", "a{b"):
        with pytest.raises(ValueError):
            fv.render({"X": bad})


def test_hand_typed_scan_still_flags_a_number_after_the_word_python(monkeypatch, tmp_path):
    """The Python-version exemption covers interpreter versions only, not a result number."""
    real = (PAPER / "sections/results.tex").read_text()
    for injected in ("(Python 0.86 of runs)", "Python\n0.86"):
        fake = tmp_path / "paper"
        (fake / "sections").mkdir(parents=True, exist_ok=True)
        (fake / "sections" / "results.tex").write_text(real + injected)
        monkeypatch.setattr(sys.modules[__name__], "PAPER", fake)
        with pytest.raises(AssertionError, match="0.86"):
            test_no_hand_typed_result_numbers("sections/results.tex")


WORDS = {"A1": "One", "A2": "Two", "A3": "Three", "A4": "Four", "A5": "Five", "A6": "Six"}


def test_amendments_table_rows_and_caption_follow_the_post_outcome_flags():
    """QG B12/B13: every amendment record has a row in tab:amendments; the post-outcome ones (A5,
    approvals row 16; A6, approvals row 40) carry the double dagger and the others do not; the
    caption never calls the whole table pre-data, and names the pre-data range from the records
    themselves. The table numbers the amendments 1-6 under a "No." header and its caption says
    "Amendments 1--4" in words: the record ids A1-A6 are not shown to the reader."""
    am = json.loads((PAPER / "data" / "amendments_v060.json").read_text())["amendments"]
    res = _strip(RESULTS.read_text())
    flags = {a["id"]: a.get("post_outcome", False) for a in am}
    assert all(type(v) is bool for v in flags.values()), flags
    assert [k for k, v in flags.items() if v] == ["A5", "A6"]
    assert "No. & Version label & Locked (UTC) & Lock commit(s) & Change" in res
    # amendments 2-4 have a version label and no git tag: the caption must not call the column tags
    flat = " ".join(res.split())
    assert "version tag" not in flat.lower()
    assert "amendments 5 and 6 are also git tags of that name" in flat
    assert "predates the version labels" in flat
    for a in am:
        w = WORDS[a["id"]]
        num = a["id"].removeprefix("A")
        assert num.isdigit(), a["id"]
        row = re.search(rf"^{num} & .*\\resAmend{w}Change \\\\$", res, re.M)
        assert row, f"no tab:amendments row for {a['id']}"
        assert f"\\resAmend{w}Version" in row.group(0), a["id"]  # the number matches its record
        assert ("\\ddagger" in row.group(0)) is flags[a["id"]], a["id"]
    cap = re.search(
        r"\\caption\{The six amendments to the pre-registration(.*?)\\label\{tab:amendments\}",
        res,
        re.S,
    )
    cap = " ".join(cap.group(1).split())
    assert "each locked before any data from this sweep existed (" not in cap
    assert len(am) == 6  # "The six amendments"
    pre = [k.removeprefix("A") for k, v in flags.items() if not v]
    assert (
        f"Amendments {pre[0]}--{pre[-1]} were each locked before any data from this sweep existed"
        in cap
    )
    assert "$^{\\ddagger}$Amendments 5 and 6 were locked \\emph{after} the outcome was known" in cap
    assert "no run exists under either" in cap
    assert "lock commits" in cap  # the column header is defined where it is used
    assert not re.search(r"\bA[1-6]\b", res), "an amendment record id is shown to the reader"


# --------------------------------------------------------------------------- HACA-119 wording
HLABEL = re.compile(r"\bH(?:\\,|~|\$?_\{?)?[1-5]\b")
REGISTER_CODE = re.compile(
    r"\bA\d(?:-{1,3}|\\nobreakdash-)\d+\b|\bDF-\d+|\\#\d+|\bR\d\b|\bRR-\d|record~0"
    r"|\b(?!SHA-)[A-Z]{2,}-\d+\b"
)
STATUS_WORD = re.compile(
    r"PASS|FAIL|UNEVALUATED|\\textsc\{(?i:pass|fail)\}|\\textbf\{(?i:pass|fail|unevaluated)\}"
)


def test_hypothesis_labels_appear_only_in_the_hypotheses_table():
    """HACA-119, tightened: the labels H1-H5 appear nowhere in the manuscript, the hypotheses
    table included (its label column was dropped because the text never used the labels), and
    the generated macros carry none. The table names each hypothesis as the text does."""
    for fpath in TEX_INPUTS + [GEN]:
        text = _strip(fpath.read_text())
        assert not HLABEL.search(text), (fpath.name, HLABEL.search(text))
    res = _strip(RESULTS.read_text())
    table = res[res.index("Hypothesis & Criterion & Outcome") : res.index("\\label{tab:gates}")]
    for name in (
        "\\emph{Attainable error on Adamson.}",
        "\\emph{Attainable error on Norman.}",
        "\\emph{Backbone choice.}",
        "\\emph{Trace-feature ranking.}",
        "\\emph{Cross-dataset transfer.}",
    ):
        assert table.count(name) == 1, name
    flat = " ".join(res.split())
    for name in (
        "attainable-error",
        "backbone-choice",
        "trace-feature ranking",
        "cross-dataset transfer",
    ):
        assert f"\\emph{{{name}}}" in flat, name  # the text introduces the same names


def test_no_capitalised_status_words_or_inline_register_codes():
    """HACA-119: no PASS/FAIL/UNEVALUATED (or a styled variant) in the manuscript, and no
    amendment, defect or ticket code (A2-7, A2--7, DF-07, #227, R3, HACA-119, record 0)."""
    for fpath in TEX_INPUTS + [GEN]:
        text = _strip(fpath.read_text())
        assert not STATUS_WORD.search(text), (fpath.name, STATUS_WORD.search(text))
        assert not REGISTER_CODE.search(text), (fpath.name, REGISTER_CODE.search(text))


@pytest.mark.parametrize(
    "bad",
    [
        "Results for H3",
        "$H_3$",
        "H\\,3",
        "see A2-7.",
        "see A2--7.",
        "A2\\nobreakdash-7",
        "PR~\\#227",
        "HACA-119",
        "\\textsc{pass}",
        "\\textbf{Fail}",
        "DF-07",
        "record~0",
    ],
)
def test_shorthand_guards_catch_variants(bad):
    assert HLABEL.search(bad) or REGISTER_CODE.search(bad) or STATUS_WORD.search(bad), bad


def test_clarity_pass_corrections_stay_true_to_the_code_and_the_run():
    """Statements a self-containment pass got wrong, each pinned to its source: the attainable
    error is an oracle (never "held-out"); two features in both screens meet the ranking
    criterion (never "the one feature"); the sweep's R is a training-budget index whose formula
    is the code's; the lifecycle has no critique-severity matrix and no per-round winner; the
    transfer composite is ridge-fitted, not the fixed-weight TDI_lifecycle."""
    from perturb_eval.experiments.heldout import R_SEED_INVARIANT_BACKBONES, trainer_config

    flat = {p.name: " ".join(_strip(p.read_text()).split()) for p in (MAIN, RESULTS, SETUP)}
    main, res, setup = flat["paper.tex"], flat["results.tex"], flat["experimental_setup.tex"]
    readme = " ".join((ROOT / "README.md").read_text().split())
    abstract = main[main.index("\\begin{abstract}") : main.index("\\end{abstract}")]

    # the oracle is not a held-out error, on any surface that states the hypotheses
    for name, text in (("abstract", abstract), ("results", res), ("README", readme)):
        assert "low held-out error" not in text, name
    for ds in ("Adamson", "Norman"):
        assert (
            f"\\emph{{Attainable error on {ds}.}} The best configuration of the trainer sweep, "
            "selected on the data it is scored on (an oracle quantity, \\S\\ref{subsec:oracle}), "
            f"attains low error on the {ds} tasks." in res
        )
    assert (
        "taking the best configuration for each task (a best-case bound, selected on the "
        in abstract
    )
    assert "(best configuration per task, an oracle bound)" in readme
    assert "ranks tasks by held-out error within each dataset" in readme

    # four of the six tests pass: two features in each of two screens
    h4 = json.loads((ROOT / "artifacts/v0.6.0/summary.json").read_text())["preregistered"]["H4"]
    assert h4["n_tests_passing"] == 4 and len(h4["all_six"]) == 6
    assert "the one feature" not in main and "The feature that meets" not in readme
    assert (
        "the features of a run's record (its \\emph{trace}) that meet the ranking criterion --- "
        "the drop in confidence across rounds and the composite that includes it --- are stated "
        "after the agents have been shown a held-out error" in main
    )
    assert (
        "The six within-dataset tests of the ranking hypothesis are these three features in "
        "each of the two screens." in res
    )

    # R in the trainer sweep: the stated formula is trainer_config's, and linear ignores it
    assert "round count" not in setup
    assert (
        "it sets the trainer's iteration budget, the number of training iterations, to $20+40R$"
        in setup
    )
    assert [trainer_config(r, 2026).max_iter for r in (1, 2, 3)] == [20 + 40 * r for r in (1, 2, 3)]
    assert R_SEED_INVARIANT_BACKBONES == {"linear"}
    assert "The \\textsc{linear} backbone ignores both $R$ and the seed" in setup

    # CSD / WFR
    assert "records neither critiques" not in res
    assert (
        "cannot be computed: the lifecycle records no critique-severity matrix and has no "
        "per-round winner" in res
    )

    # the transfer composite is not the fixed-weight TDI_lifecycle
    assert (
        "\\emph{Cross-dataset transfer.} A two-term composite of $\\mathrm{ACE}_{\\mathrm{norm}}$ "
        "and $1-\\Delta C$, with weights fitted by ridge regression on the Adamson tasks, ranks "
        "the Norman tasks by held-out error." in res
    )
    assert "a TDI calibrated on one screen" not in abstract
    assert "composite fitted on one screen (its weights estimated by regression" in abstract

    # earlier archived versions are not a complete two-item list
    for text in (main, setup):
        assert "(including versions 0.6.0 and 0.6.1, which report this run)" in text
        assert "(versions 0.6.0 and 0.6.1)" not in text

    # the amendment tag v0.6.0-a6 exists and marks the amendment, not a release
    for rel in ("CHANGELOG.md", "publish.yml", "paper/SUBMISSION.md"):
        text = " ".join((ROOT / rel).read_text().replace("#", " ").split())
        assert "creates the amendment tag" not in text and "to be created by the CTO" not in text, (
            rel
        )
        if rel != "paper/SUBMISSION.md":  # there the phrase is about the 0.6.2 record, truly
            assert "does not exist yet" not in text, rel
        assert "07a5e57b" in text and "not a release" in text, rel
    # ... and the CellForge reference correction is disclosed where a reader of the record looks
    for rel in ("CHANGELOG.md", "publish.yml"):
        text = " ".join((ROOT / rel).read_text().split())
        assert (
            "Xiangru Tang, Jiapeng Chen, Daniel Shao, Zhuoyun Yu and others (15 authors)" in text
        ), rel
        assert "Xiangru Chen and others" in text and "Wei, Yi" in text, rel
