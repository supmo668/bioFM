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
