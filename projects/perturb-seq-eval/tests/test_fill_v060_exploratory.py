"""The exploratory v0.6.0 values come ONLY from the committed artifacts (CTO #491).

The generator must reproduce the committed pre-registered ``one_minus_delta_c`` correlation
before it emits anything, its outputs must be fresh, and a changed confidence in the artifact
must change them (so these tests are live, not a snapshot of themselves).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "v0.6.0"
SCRIPT = ROOT / "scripts" / "paper" / "fill_v060_exploratory.py"
GEN = ROOT / "paper" / "sections" / "generated_exploratory.tex"
DATA = ROOT / "paper" / "data" / "exploratory_v060.json"
LOCKED = ROOT / "paper" / "sections" / "generated_numbers.tex"
N_TASKS = {"adamson_full": 21, "norman": 20}
LOCKED_RHO = {"adamson_full": "resHFourAdaDcRho", "norman": "resHFourNorDcRho"}


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def fx():
    return _load(SCRIPT, "fill_v060_exploratory")


@pytest.fixture(scope="module")
def built(fx) -> dict:
    return fx.build(ART)


@pytest.fixture(scope="module")
def committed() -> dict:
    return json.loads(DATA.read_text())


@pytest.fixture(scope="module")
def macros() -> dict[str, str]:
    return dict(
        re.findall(
            r"^\\newcommand\{\\(expl[A-Za-z]+)\}\{(.*)\}$", GEN.read_text(), flags=re.MULTILINE
        )
    )


def _copy_artifacts(dst: Path) -> Path:
    dst.mkdir()
    for name in ("lifecycle_runs.jsonl", "trainer_runs.jsonl", "summary.json", "provenance.json"):
        shutil.copy2(ART / name, dst / name)
    return dst


def _check(*extra: str, cwd: Path = ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--check", *extra],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


# --------------------------------------------------------------------------- freshness
def test_committed_outputs_are_fresh(tmp_path):
    r = _check(cwd=tmp_path)  # cwd-independent, like the locked generator
    assert r.returncode == 0, r.stderr + r.stdout


def test_committed_files_equal_a_fresh_build(fx, built, committed):
    assert GEN.read_text() == fx.render(fx.macros(built))
    assert fx.same(committed, json.loads(fx.render_json(built)))


def test_check_fails_on_a_stale_macro_file(tmp_path):
    stale = tmp_path / "generated_exploratory.tex"
    stale.write_text(GEN.read_text().replace("explNQuantities}{", "explNQuantities}{9", 1))
    r = _check("--out", str(stale))
    assert r.returncode == 1 and "stale" in r.stderr


def test_check_fails_on_a_stale_json(tmp_path, committed):
    stale = json.loads(json.dumps(committed))
    stale["screens"]["norman"]["quantities"]["conf_sd_round0"]["value"] += 1e-6
    path = tmp_path / "exploratory_v060.json"
    path.write_text(json.dumps(stale))
    r = _check("--json-out", str(path))
    assert r.returncode == 1 and "stale" in r.stderr


# --------------------------------------------------------------------------- H4 reproduction
def test_reproduces_the_committed_h4_rho(fx, built):
    summary = json.loads((ART / "summary.json").read_text())
    locked = dict(
        re.findall(
            r"^\\newcommand\{\\(res[A-Za-z]+)\}\{(.*)\}$", LOCKED.read_text(), flags=re.MULTILINE
        )
    )
    rows = {
        r["dataset"]: r
        for r in summary["preregistered"]["H4"]["all_six"]
        if r["component"] == "one_minus_delta_c"
    }
    assert set(built["h4_reproduction"]) == set(N_TASKS)
    for ds, got in built["h4_reproduction"].items():
        assert got["rho"] == pytest.approx(rows[ds]["rho"], abs=1e-9)
        assert got["n"] == rows[ds]["n"] == N_TASKS[ds]
        assert fx.f(got["rho"]) == locked[LOCKED_RHO[ds]]


def test_refuses_to_emit_when_h4_is_not_reproduced(fx, tmp_path):
    art = _copy_artifacts(tmp_path / "art")
    summary = json.loads((art / "summary.json").read_text())
    for row in summary["preregistered"]["H4"]["all_six"]:
        if row["component"] == "one_minus_delta_c":
            row["rho"] += 0.001
    (art / "summary.json").write_text(json.dumps(summary))
    with pytest.raises(ValueError, match="H4 reproduction failed"):
        fx.build(art)
    out, js = tmp_path / "out.tex", tmp_path / "out.json"
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--artifacts", str(art), "--out", str(out)]
        + ["--json-out", str(js)],
        capture_output=True,
        check=False,
        text=True,
    )
    assert r.returncode != 0 and not out.exists() and not js.exists()


# --------------------------------------------------------------------------- content
def test_every_macro_value_is_tex_safe(fx, macros):
    assert len(macros) == GEN.read_text().count("\\newcommand")
    for name, value in macros.items():
        assert fx.ENSUREMATH_NEG.fullmatch(value) or fx.SAFE_VALUE.fullmatch(
            value.replace("\\_", "_")
        ), (name, value)


def test_macros_are_pinned_to_the_json(fx, macros, committed):
    """Each printed value is the JSON's value through ``f``; none is typed."""
    assert macros["explRunId"] == committed["run_id"]
    assert macros["explNQuantities"] == str(
        sum(len(s["quantities"]) for s in committed["screens"].values())
    )
    assert macros["explNQuantitiesPerScreen"] == str(
        len(committed["screens"]["norman"]["quantities"])
    )
    for ds, dn in fx.DS.items():
        q = committed["screens"][ds]["quantities"]
        assert macros[f"expl{dn}DcMsdROneRho"] == fx.f(q["one_minus_delta_c_vs_msd_round1"]["rho"])
        assert macros[f"expl{dn}ConfRZeroMsdCILo"] == fx.f(q["conf_round0_vs_final_msd"]["ci_low"])
        assert macros[f"expl{dn}ConfSdRTwo"] == fx.f(q["conf_sd_round2"]["value"])
        assert macros[f"expl{dn}RoleValidatorConfChange"] == fx.f(
            q["role_Validator_conf_change"]["value"]
        )
        assert macros[f"expl{dn}LotoDcRhoMin"] == fx.f(
            q["h4_one_minus_delta_c_leave_one_task_out"]["min"]
        )
        assert macros[f"expl{dn}OraclePctRankMedian"] == fx.f(
            q["final_msd_pct_rank_median"]["value"], 1
        )


def test_json_lists_its_inputs_sha256_and_run(committed):
    prov = json.loads((ART / "provenance.json").read_text())
    assert committed["run_id"] == prov["run_id"]
    assert set(committed["inputs_sha256"]) == {
        f"artifacts/v0.6.0/{n}"
        for n in ("lifecycle_runs.jsonl", "trainer_runs.jsonl", "summary.json", "provenance.json")
    }
    for rel, digest in committed["inputs_sha256"].items():
        assert digest == hashlib.sha256((ROOT / rel).read_bytes()).hexdigest(), rel


def test_rho_bounds_and_task_counts(committed):
    n_corr = 0
    for ds, screen in committed["screens"].items():
        assert screen["n_tasks"] == N_TASKS[ds] == len(screen["per_task"])
        for name, q in screen["quantities"].items():
            assert q["n"] == N_TASKS[ds], (ds, name)
            if q["kind"] == "spearman":
                n_corr += 1
                assert -1.0 <= q["ci_low"] <= q["rho"] <= q["ci_high"] <= 1.0, (ds, name)
            elif q["kind"] == "range":
                assert -1.0 <= q["min"] <= q["max"] <= 1.0, (ds, name)
            elif q["kind"] == "sd":
                assert q["value"] >= 0.0
        loto = screen["quantities"]["h4_one_minus_delta_c_leave_one_task_out"]
        assert loto["min"] <= committed["h4_reproduction"][ds]["rho"] <= loto["max"]
    assert committed["counts"]["n_correlations"] == n_corr
    assert committed["counts"]["n_quantities"] == sum(
        len(s["quantities"]) for s in committed["screens"].values()
    )


def test_the_requested_quantities_are_all_present(committed):
    roles = ("DataCurator", "Literature", "Architect", "Trainer", "Validator")
    want = {f"conf_round{r}_vs_final_msd" for r in range(3)}
    want |= {"one_minus_delta_c_vs_msd_round1", "one_minus_delta_c_vs_msd_round0"}
    want |= {"ace_round0_vs_final_msd", "msd_round0_vs_msd_round2", "msd_round1_vs_msd_round2"}
    want |= {f"conf_sd_round{r}" for r in range(3)}
    want |= {f"role_{role}_conf_round{r}" for role in roles for r in range(3)}
    want |= {f"role_{role}_conf_change" for role in roles}
    want |= {"final_msd_vs_oracle_min", "final_msd_pct_rank_median"}
    want |= {"h4_one_minus_delta_c_leave_one_task_out"}
    for screen in committed["screens"].values():
        assert set(screen["quantities"]) == want


# --------------------------------------------------------------------------- liveness
def test_changing_one_confidence_changes_the_output(fx, built, tmp_path):
    """One round-1 confidence is changed (round 1 leaves the pre-registered features alone),
    in a run chosen so that its task's seed median must move."""
    art = _copy_artifacts(tmp_path / "art")
    lines = (art / "lifecycle_runs.jsonl").read_text().splitlines()
    rows = [json.loads(line) for line in lines]
    by_task: dict[tuple[str, str], list[int]] = {}
    for i, row in enumerate(rows):
        if "steps" in row:
            by_task.setdefault((row["dataset"], row["task_id"]), []).append(i)

    def mean_r1(row: dict) -> float:
        return statistics.fmean(s["llm_confidence"] for s in row["steps"] if s["round_index"] == 1)

    target = None
    for (ds, _task), idx in sorted(by_task.items()):
        ranked = sorted(idx, key=lambda i: mean_r1(rows[i]))
        means = [mean_r1(rows[i]) for i in ranked]
        if len(idx) == 3 and means[0] < means[1] < means[2]:
            target = (ds, ranked[1])  # the middle seed: it IS the task's median
            break
    assert target is not None, "no task with three distinct round-1 mean confidences"
    ds, i = target
    step = max(
        (s for s in rows[i]["steps"] if s["round_index"] == 1), key=lambda s: s["llm_confidence"]
    )
    before = mean_r1(rows[i])
    step["llm_confidence"] = 0.0
    # the old median was strictly between the other two seeds, so lowering it moves the median
    assert mean_r1(rows[i]) < before
    lines[i] = json.dumps(rows[i])
    (art / "lifecycle_runs.jsonl").write_text("\n".join(lines) + "\n")

    changed = fx.build(art)  # H4 is still reproduced: round 1 feeds no pre-registered feature
    old, new = built["screens"][ds]["quantities"], changed["screens"][ds]["quantities"]
    assert new["conf_sd_round1"]["value"] != old["conf_sd_round1"]["value"]
    assert new["conf_sd_round0"]["value"] == old["conf_sd_round0"]["value"]
    assert changed["h4_reproduction"] == built["h4_reproduction"]
    assert changed["inputs_sha256"] != built["inputs_sha256"]
    assert not fx.same(json.loads(fx.render_json(changed)), json.loads(fx.render_json(built)))
    assert _check("--artifacts", str(art)).returncode == 1


# --------------------------------------------------------------------------- figures
def test_figures_render_from_the_committed_json(tmp_path):
    pytest.importorskip("matplotlib")  # optional `paper` dependency group
    figs = _load(ROOT / "scripts" / "paper" / "make_v060_figures.py", "make_v060_figures")
    old = sys.argv
    sys.argv = ["make_v060_figures.py", "--out-dir", str(tmp_path)]
    try:
        assert figs.main() == 0
    finally:
        sys.argv = old
    for name in ("fig_h4_scatter.pdf", "fig_confidence_by_round.pdf"):
        assert (tmp_path / name).read_bytes().startswith(b"%PDF")
        assert (ROOT / "paper" / "figures" / name).is_file()


# --------------------------------------------------------------------------- generator guards
def test_macros_count_the_correlations_per_screen(macros, committed):
    """The caption's per-screen count is a macro, derived from the quantities themselves."""
    per_screen = {
        sum(q["kind"] == "spearman" for q in s["quantities"].values())
        for s in committed["screens"].values()
    }
    assert len(per_screen) == 1
    n = per_screen.pop()
    assert committed["counts"]["n_correlations_per_screen"] == n
    assert macros["explNCorrelationsPerScreen"] == str(n)
    assert macros["explNCorrelations"] == str(n * len(committed["screens"]))
    caption = " ".join(RESULTS.read_text().split())
    assert "are shown, \\explNCorrelationsPerScreen{} per screen." in caption
    assert not re.search(r"\b(?:nine|\d+) per screen", caption)


@pytest.mark.parametrize("round_index", [0, 1])
@pytest.mark.parametrize("bad", [float("inf"), float("nan")])
def test_a_non_finite_earlier_round_msd_stops_the_build(fx, round_index, bad):
    run = next(
        json.loads(line)
        for line in (ART / "lifecycle_runs.jsonl").read_text().splitlines()
        if '"steps"' in line
    )
    fx._run_features(run)  # the committed run is accepted
    run["msd_per_round"][round_index] = bad
    with pytest.raises(ValueError, match=f"round-{round_index} MSD is not finite"):
        fx._run_features(run)


def test_imported_private_helpers_keep_their_signatures():
    """The generator calls private helpers of the pre-registered module. A rename or a changed
    parameter must fail here, by name, and not as an AttributeError inside a build."""
    import inspect

    from perturb_eval import metrics
    from perturb_eval.experiments import preregistered as pre

    want = {
        "_round_vector": ["steps", "r"],
        "_pairs": ["table", "key"],
        "_finite": ["v"],
        "rho": ["x", "y"],
        "spearman_with_ci": ["x", "y", "B", "seed"],
        "per_task_table": ["lifecycle_rows"],
        "task_key": ["row"],
    }
    got = {name: list(inspect.signature(getattr(pre, name)).parameters) for name in want}
    assert got == want
    assert list(inspect.signature(metrics.ace_d).parameters) == ["confidences"]
    assert isinstance(metrics._EPS, float) and 0.0 < metrics._EPS < 1e-6
    assert pre.H4_DATASETS == ("adamson_full", "norman")
    assert (pre.BOOTSTRAP_B, pre.BOOTSTRAP_SEED, pre.CI_LEVEL) == (10000, 2026, 0.95)
    # the shapes the generator unpacks
    vec, why = pre._round_vector([], 0)
    assert vec is None and isinstance(why, str)
    c = pre.spearman_with_ci([1.0, 2.0, 3.0, 4.0], [1.0, 3.0, 2.0, 4.0])
    assert {"rho", "n", "ci_low", "ci_high", "n_boot_valid", "reason"} <= set(c)


# --------------------------------------------------------------------------- manuscript guards
RESULTS = ROOT / "paper" / "sections" / "results.tex"
MAIN = ROOT / "paper" / "paper.tex"
TEX_INPUTS = [
    MAIN,
    RESULTS,
    ROOT / "paper" / "sections" / "experimental_setup.tex",
    ROOT / "paper" / "sections" / "corrections.tex",
]
EXPL_USE = re.compile(r"\\(expl[A-Z][A-Za-z]*)")
# TeX drops the white space after a control word, a line end included, so a macro followed by
# a word, an opening parenthesis or a digit needs ``{}``.
EXPL_SWALLOW = re.compile(r"\\expl[A-Z][A-Za-z]*(?:\s+[A-Za-z(]|\d)")
EXPL_REDEFINE = re.compile(
    r"\\(?:re)?newcommand\*?\s*\{?\\expl|\\(?:[egx]?def|let)\s*\\expl|\\providecommand\*?\s*\{?\\expl"
    r"|\\DeclareRobustCommand\*?\s*\{?\\expl"
)


def _strip_comments(text: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", text)


def test_every_exploratory_macro_used_is_defined_and_input_first(macros):
    used_anywhere: set[str] = set()
    for fpath in TEX_INPUTS:
        text = _strip_comments(fpath.read_text())
        used = set(EXPL_USE.findall(text))
        used_anywhere |= used
        assert not (used - set(macros)), (fpath.name, sorted(used - set(macros)))
        assert not EXPL_SWALLOW.search(text), (fpath.name, EXPL_SWALLOW.search(text))
        assert not EXPL_REDEFINE.search(text), (fpath.name, EXPL_REDEFINE.search(text))
    assert used_anywhere, "the manuscript uses no exploratory macro: this guard checks nothing"
    main = _strip_comments(MAIN.read_text())
    load = main.index("\\input{sections/generated_exploratory}")
    assert load < main.index("\\begin{document}")
    assert load < main.index("\\expl") and load < main.index("\\input{sections/results}")
    names = re.findall(r"\\newcommand\{\\(expl[A-Za-z]+)\}", GEN.read_text())
    assert len(names) == len(set(names)) == len(macros)
    # the two generated families do not collide
    locked = re.findall(r"\\newcommand\{\\([A-Za-z]+)\}", LOCKED.read_text())
    assert not set(names) & set(locked)


@pytest.mark.parametrize(
    "bad",
    [
        "\\explAdaNTasks tasks",
        "\\explAdaNTasks\ntasks",
        "\\explAdaNTasks (of them)",
        "\\explAdaNTasks2",
        "\\renewcommand{\\explAdaNTasks}{22}",
        "\\newcommand\\explAdaNTasks{22}",
        "\\def\\explAdaNTasks{22}",
        "\\gdef\\explAdaNTasks{22}",
        "\\providecommand{\\explAdaNTasks}{22}",
    ],
)
def test_exploratory_macro_guards_catch_variants(bad):
    assert EXPL_SWALLOW.search(bad) or EXPL_REDEFINE.search(bad), bad


def test_exploratory_macro_guards_accept_the_safe_forms():
    for ok in (
        "\\explAdaNTasks{} tasks",
        "$n=\\explAdaNTasks$; CI",
        "\\explAdaNTasks, and",
        "[\\explAdaLotoDcRhoMin, \\explAdaLotoDcRhoMax]",
    ):
        assert not EXPL_SWALLOW.search(ok) and not EXPL_REDEFINE.search(ok), ok


def _flat(path: Path) -> str:
    return " ".join(_strip_comments(path.read_text()).split())


def test_qualitative_prose_is_pinned_to_the_json_and_the_summary(committed):
    """Each sentence that states a sign, an order or an interval's relation to zero is paired
    with the value it rests on: the fact must hold AND the sentence must still be in the text,
    so neither can change alone."""
    res, main = _flat(RESULTS), _flat(MAIN)
    q = {ds: s["quantities"] for ds, s in committed["screens"].items()}
    ada, nor = q["adamson_full"], q["norman"]

    def says(text: str, sentence: str) -> None:
        assert sentence in text, f"sentence no longer in the manuscript: {sentence!r}"

    # round-0 mean confidence: both intervals include zero
    for s in (ada, nor):
        c = s["conf_round0_vs_final_msd"]
        assert c["ci_low"] < 0.0 < c["ci_high"]
    says(res, "has no detectable rank association with the final error in either screen")
    says(res, "both intervals include zero")
    says(main, "on Norman, both confidence intervals including zero")
    says(main, "the mean confidence stated before any feedback does not rank tasks")

    # round-0 ACE: Norman's interval excludes zero (negative); Adamson's includes it, same sign
    assert nor["ace_round0_vs_final_msd"]["ci_high"] < 0.0
    a = ada["ace_round0_vs_final_msd"]
    assert a["rho"] < 0.0 and a["ci_low"] < 0.0 < a["ci_high"]
    says(
        res,
        "is negatively associated with the final error ($\\rho=\\explNorAceRZeroMsdRho$, interval excluding zero)",
    )
    says(res, "on Adamson the estimate has the same sign and its interval includes zero")

    # rounds 1 and 2: negative, interval below zero, in both screens
    for s in (ada, nor):
        for r in (1, 2):
            c = s[f"conf_round{r}_vs_final_msd"]
            assert c["rho"] < 0.0 and c["ci_high"] < 0.0, (r, c)
    says(
        res,
        "The mean confidence of rounds $1$ and $2$ is strongly and negatively rank-associated with the final error",
    )

    # 1 - delta_c against the errors the agents were shown: positive, interval above zero
    for s in (ada, nor):
        for r in (0, 1):
            assert s[f"one_minus_delta_c_vs_msd_round{r}"]["ci_low"] > 0.0
    says(res, "$1-\\Delta C$ is associated with the errors the agents had been shown")

    # which role moves
    for s in (ada, nor):
        cur = s["role_DataCurator_conf_change"]["value"]
        val = s["role_Validator_conf_change"]["value"]
        arch = s["role_Architect_conf_change"]["value"]
        assert cur < 0.0 < val
        assert abs(arch) < abs(cur) and abs(arch) < abs(val)
        assert s["role_Validator_conf_round0"]["value"] == min(
            s[f"role_{role}_conf_round0"]["value"]
            for role in ("DataCurator", "Literature", "Architect", "Trainer", "Validator")
        )
    says(res, "states a low confidence in round $0$ and a much higher one afterwards")
    says(res, "DataCurator's falls")
    says(res, "Architect's barely moves")

    # spread across tasks: smaller before feedback than in round 2
    for s in (ada, nor):
        assert s["conf_sd_round0"]["value"] < s["conf_sd_round2"]["value"]
    says(res, "it hardly varies across tasks")

    # the error: rank order stable across rounds and close to the oracle's; level differs by screen
    for s in (ada, nor):
        assert s["msd_round0_vs_msd_round2"]["ci_low"] > 0.0
        assert s["msd_round1_vs_msd_round2"]["ci_low"] > 0.0
        assert s["final_msd_vs_oracle_min"]["ci_low"] > 0.0
    says(res, "it barely changes from round to round")
    says(res, "ranks tasks almost as the trainer sweep's oracle does")
    says(main, "the rank order of tasks by error is nearly the same from round to round")
    assert ada["final_msd_pct_rank_median"]["value"] != nor["final_msd_pct_rank_median"]["value"]
    says(res, "percentile rank within the trainer sweep differs between the screens")
    assert "so the difficulty proxy does not depend on the agents' choices" not in res

    # the pre-registered values the same prose leans on (summary.json, not the generator)
    pr = json.loads((ART / "summary.json").read_text())["preregistered"]
    passing = [r for r in pr["H4"]["all_six"] if r["rho"] > pr["H4"]["threshold"]]
    assert len(passing) == pr["H4"]["n_tests_passing"] == 4
    for r in passing:
        assert 0.0 < r["ci_low"] < pr["H4"]["threshold"], r
    says(res, "the lower bound of the interval lies above zero and below the criterion value")
    h5 = pr["H5"]
    assert h5["ci_low"] < 0.0 < h5["ci_high"] and h5["ci_low"] < h5["threshold"] < h5["ci_high"]
    says(res, "The interval contains both zero and the criterion value")
    says(main, "with an interval that contains both zero and the criterion")
    # the fit size printed with the transfer weights is the fit's own n
    assert h5["n_fit"] == N_TASKS["adamson_full"] and h5["n"] == N_TASKS["norman"]
    says(res, "with $n=\\resHFiveNFit$ tasks in the fit")


def test_the_reading_of_the_pass_does_not_use_the_criterion_word():
    """'Supported' is the paper's word for a criterion outcome (results, the hypotheses table).
    The interpretive reading of the ranking pass must not borrow it, and the claims about
    pre-feedback confidence are about the MEAN confidence (round-0 ACE on Norman is not null)."""
    texts = {p.name: _flat(p) for p in TEX_INPUTS}
    for name, text in texts.items():
        assert "supported result" not in text, name
        assert "What this run supports" not in text and "what it supports" not in text, name
        assert not re.search(
            r"(?<!mean )confidences? stated before any (?:such )?feedback", text
        ), name
    main, res = texts["paper.tex"], texts["results.tex"]
    assert (
        main.count("the pre-registered pass is consistent with") == 3
    )  # abstract, discussion, conclusion
    assert "the pre-registered pass is consistent with" in res
    assert "No pre-registered or claimed signal here is available before compute is spent" in main
    assert "Nothing here shows a signal" not in main
    # the subsection order: both pre-registered results, then the post-outcome material
    order = [
        res.index(f"\\label{{{k}}}")
        for k in ("sec:tdi-real", "subsec:h5", "subsec:exploratory", "subsec:runrecord")
    ]
    assert order == sorted(order)
    expl = res[order[2] : order[3]]
    for label in ("tab:exploratory", "fig:conf-by-round", "fig:h4-scatter"):
        assert f"\\label{{{label}}}" in expl, label
        assert f"\\ref{{{label}}}" in res, label
    # the amendment is named in words and points at the table that describes it
    assert (
        "The figure was added after the outcome was known, under the sixth amendment to the "
        "pre-registration (Table~\\ref{tab:amendments})." in expl
    )
    assert "Amendment 6" not in res
    assert "\\resHFourAdaAceN" not in res[order[1] : order[2]]  # the transfer fit cites its own n


def test_the_feedback_paragraph_states_what_each_role_is_shown():
    """The disclosure is read off the prompt builders, so it is pinned to them: the Architect's
    prompt has no rationale, the other roles get the truncated context, and round 0 has none."""
    from perturb_eval.agentic_lifecycle import llm_agent_pool as pool

    context = {
        "last_validator_rationale": "RATIONALE-MARKER " + "x" * 200,
        "last_msd": 0.123456,
        "literature": {"expected_up": [f"UP{i}" for i in range(9)], "expected_down": ["DN0"]},
        "validator_critique_delta": {"learning_rate": 0.001},
        "validator_failed_genes": tuple(f"gene_{i}" for i in range(10)),
    }
    arch = pool._architect_prompt("T", 1, context, "norman")
    assert "0.123456" in arch and "RATIONALE-MARKER" not in arch
    assert "gene_4" in arch and "gene_5" not in arch  # at most five failed-gene labels
    assert "UP4" in arch and "UP5" not in arch  # at most five expected genes per direction
    for role in ("DataCurator", "Literature", "Trainer", "Validator"):
        prompt = pool._simple_prompt(role, "T", 1, context, "norman")
        assert "0.123456" in prompt and "RATIONALE-MARKER" in prompt
        assert "x" * 104 not in prompt  # each value is cut to 120 characters
        assert "Context: {}" in pool._simple_prompt(role, "T", 0, {}, "norman")
    assert "Prior round MSD: None" in pool._architect_prompt("T", 0, {}, "norman")
    setup = _flat(ROOT / "paper" / "sections" / "experimental_setup.tex")
    for sentence in (
        "every role's prompt carries the previous round's held-out MSD",
        "it does not carry the rationale described next",
        "each value cut to its first $120$ characters",
        "The failed-gene labels are placeholder column labels, not gene symbols",
        "only the round-$0$ confidences are stated before any error feedback",
    ):
        assert sentence in setup, sentence
    assert "\\label{par:feedback}" in setup
    assert "\\ref{par:feedback}" in _flat(RESULTS) and "\\ref{par:feedback}" in _flat(MAIN)
    prereg = " ".join((ROOT / "paper" / "PREREGISTRATION.md").read_text().split())
    assert "and the context goes into every agent's prompt. Round 0" not in prereg
    assert "*Dated note, 2026-11-24" in prereg and "so it is not a seventh amendment" in prereg
    assert "`figure_only`" in prereg and "make_v060_figures.py" in prereg


# --------------------------------------------------------------------------- figure inputs
def _figure_constants() -> dict:
    """SCREENS / FEATURES / ROLES / ROUNDS of the figure script, read without importing it
    (it imports matplotlib at module level, which this environment may not have)."""
    import ast

    tree = ast.parse((ROOT / "scripts" / "paper" / "make_v060_figures.py").read_text())
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            name = getattr(node.targets[0], "id", None)
            if name in {"SCREENS", "FEATURES", "ROLES", "ROUNDS"}:
                out[name] = ast.literal_eval(node.value)
    assert set(out) == {"SCREENS", "FEATURES", "ROLES", "ROUNDS"}
    return out


def test_the_keys_the_figure_script_reads_exist_in_the_json(fx, committed):
    k = _figure_constants()
    assert set(k["SCREENS"]) == set(committed["screens"]) == set(fx.DS)
    assert tuple(k["FEATURES"]) == fx.SCATTER_KEYS
    assert tuple(k["ROLES"]) == tuple(fx.ROLES) and tuple(k["ROUNDS"]) == fx.ROUNDS
    for ds in k["SCREENS"]:
        screen = committed["screens"][ds]
        assert len(screen["per_task"]) == N_TASKS[ds]
        for row in screen["per_task"]:
            for key in (*k["FEATURES"], "msd"):
                assert isinstance(row[key], float), (ds, row["task"], key)
            assert row["msd"] > 0.0  # drawn on a logarithmic axis
        for role in k["ROLES"]:
            for r in k["ROUNDS"]:
                assert isinstance(
                    screen["quantities"][f"role_{role}_conf_round{r}"]["value"], float
                )
        by_round = screen["figure_only"]["median_msd_by_round"]
        assert len(by_round) == len(k["ROUNDS"]) and all(isinstance(v, float) for v in by_round)
        # the one figure-only quantity is the median of the per-task column it summarises
        for r in k["ROUNDS"]:
            assert by_round[r] == pytest.approx(
                statistics.median(row["msd_round"][r] for row in screen["per_task"]), rel=1e-12
            )


def test_the_figures_plot_the_json_values(tmp_path, monkeypatch, committed):
    """Capture what reaches matplotlib and compare it with the JSON; no PDF bytes are asserted."""
    pytest.importorskip("matplotlib")  # optional `paper` dependency group
    from matplotlib.axes import Axes

    figs = _load(ROOT / "scripts" / "paper" / "make_v060_figures.py", "make_v060_figures_capture")
    scattered: list[tuple[list, list]] = []
    plotted: list[tuple[list, list]] = []
    real_scatter, real_plot = Axes.scatter, Axes.plot

    def scatter(self, x, y, *a, **kw):
        scattered.append((list(x), list(y)))
        return real_scatter(self, x, y, *a, **kw)

    def plot(self, x, y, *a, **kw):
        plotted.append((list(x), list(y)))
        return real_plot(self, x, y, *a, **kw)

    monkeypatch.setattr(Axes, "scatter", scatter)
    monkeypatch.setattr(Axes, "plot", plot)
    figs.scatter(committed, tmp_path / "scatter.pdf")
    want = []
    for ds in figs.SCREENS:
        rows = committed["screens"][ds]["per_task"]
        for key in figs.FEATURES:
            want.append(([r[key] for r in rows], [r["msd"] for r in rows]))
    assert scattered == want and plotted == []
    figs.confidence_by_round(committed, tmp_path / "rounds.pdf")
    want = []
    for ds in figs.SCREENS:
        q = committed["screens"][ds]["quantities"]
        for role in figs.ROLES:
            want.append(
                (list(figs.ROUNDS), [q[f"role_{role}_conf_round{r}"]["value"] for r in figs.ROUNDS])
            )
        want.append(
            (list(figs.ROUNDS), committed["screens"][ds]["figure_only"]["median_msd_by_round"])
        )
    assert plotted == want
    assert len(scattered) == len(figs.SCREENS) * len(figs.FEATURES)  # nothing else was scattered
