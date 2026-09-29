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
}
# Design facts that are not sweep results and not pre-registration constants (model size,
# the v0.5 default TDI weights quoted in the Metrics section).
DESIGN_LITERALS = {
    "results.tex": set(),
    "experimental_setup.tex": {"2.1"},
    "paper.tex": {"0.35", "0.25", "0.15"},
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
    return dict(
        re.findall(r"^\\newcommand\{\\(res[A-Za-z]+)\}\{(.*)\}$", GEN.read_text(), flags=re.M)
    )


@pytest.fixture(scope="module")
def art():
    s = json.loads((ART / "summary.json").read_text())
    p = json.loads((ART / "provenance.json").read_text())
    proj = json.loads((PAPER / "data" / "projection_v060.json").read_text())
    runs = [json.loads(line) for line in (ART / "lifecycle_runs.jsonl").read_text().splitlines()]
    runs = [r for r in runs if r.get("record_type") != "provenance" and "steps" in r]
    return s, p, proj, runs


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
def test_every_result_macro_is_pinned_to_an_artifact_key(fv, macros, art):
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
        want = {True: r"\textbf{PASS}", False: r"\textbf{FAIL}", None: r"\textbf{UNEVALUATED}"}[
            pr[g]["pass"]
        ]
        assert macros[f"res{name}Verdict"] == want, g
    assert macros["resGateSummary"] == "4 of 5 gates pass; H5 fails (0 unevaluated)"
    assert macros["resManifestSha"] != "n/a" and macros["resArchiveShaCache"] != "n/a"


def test_verdict_none_is_unevaluated(fv):
    assert fv.verdict(None) == r"\textbf{UNEVALUATED}"
    assert fv.verdict(True) == r"\textbf{PASS}" and fv.verdict(False) == r"\textbf{FAIL}"


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
    assert m["HFiveVerdict"] == r"\textbf{UNEVALUATED}"
    assert "FAIL" not in m["HFiveVerdict"] and "fail" not in m["GateSummary"]
    assert "1 unevaluated" in m["GateSummary"]
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
    with pytest.raises(ValueError):
        fv.render({"StopReasonNone": "spend_stop"})
    with pytest.raises(ValueError):
        fv.render({"RunId": "a%b"})
    with pytest.raises(ValueError):
        fv.render({"RunId": "a\nb"})
    assert r"\newcommand{\resHOneVerdict}{\textbf{PASS}}" in fv.render(
        {"HOneVerdict": r"\textbf{PASS}"}
    )


# --------------------------------------------------------------------------- manuscript guards
def test_no_pending_placeholders_remain():
    for fpath in TEX_INPUTS + [PAPER / "README.md"]:
        assert "\\pending{" not in fpath.read_text(), fpath.name
        assert "PENDING" not in fpath.read_text(), fpath.name


def test_every_result_macro_used_is_defined_and_input_first(macros):
    for fpath in TEX_INPUTS:
        text = _strip(fpath.read_text())
        used = set(re.findall(r"\\(res[A-Za-z]+)", text))
        assert not (used - set(macros)), (fpath.name, sorted(used - set(macros)))
        assert not re.search(r"\\res[A-Za-z]+(?:[ \t]+[A-Za-z(]|\d)", text), (
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
    "rel", ["sections/results.tex", "sections/experimental_setup.tex", "paper.tex"]
)
def test_no_hand_typed_result_numbers(rel):
    """Any decimal literal in result-bearing prose must be a pre-registered constant, not a sweep value."""
    text = _strip((PAPER / rel).read_text())
    text = re.sub(r"\{[\d.]+\\linewidth\}", "", text)  # column / minipage widths
    text = re.sub(r"(Haiku|Sonnet|Opus|Apache-)\s*\d\.\d", "", text)  # model versions / licence
    literals = set(re.findall(r"(?<![\w.])\d*\.\d+(?!\.\d)", text))
    name = Path(rel).name
    allowed = ALLOWED_LITERALS[name] | DESIGN_LITERALS[name]
    assert literals == allowed, (sorted(literals - allowed), sorted(allowed - literals))
    prereg = (PAPER / "PREREGISTRATION.md").read_text()
    for lit in ALLOWED_LITERALS[name]:
        assert lit in prereg, lit


def test_braces_balanced():
    for fpath in TEX_INPUTS + [GEN]:
        depth = 0
        for ch in _strip(fpath.read_text()):
            depth += ch == "{"
            depth -= ch == "}"
            assert depth >= 0, fpath.name
        assert depth == 0, fpath.name


def test_prose_claims_match_artifacts(art):
    """Qualitative sentences that depend on artifact facts are pinned to those facts."""
    s, p, _, runs = art
    pr = s["preregistered"]
    res, setup, main = RESULTS.read_text(), SETUP.read_text(), MAIN.read_text()
    six = {(r["dataset"], r["component"]): r for r in pr["H4"]["all_six"]}
    # gate outcomes named in the abstract / results
    assert [pr[g]["pass"] for g in ("H1", "H2", "H3", "H4")] == [True] * 4 and pr["H5"][
        "pass"
    ] is False
    assert "H5 fails" in main and "\\resGateSummary" in main
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
    assert "lies above the gate" in res
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
    assert "neither reached" in res
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
    assert "score\\_and\\_gate" in setup and "suggested\\_next\\_config\\_delta" in setup
    # A4-1 / A4-3 / A2-8 / A2-1
    assert "H3 condition is unchanged" not in setup
    assert (
        "non-default sampling" in setup
        and "key/value" in setup
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
    # section Metrics points at the amended definitions
    assert (
        "A2-10" in main
        and "A2-11" in main
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
    ).stdout.split()
    assert out == [], out
