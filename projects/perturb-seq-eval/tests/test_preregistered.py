"""Pre-registered estimators (paper/PREREGISTRATION.md, principal-ratified 2026-09-24).

Hand-built lifecycle JSONL fixtures only: every value below is written out
literally so the expected statistic can be checked by hand.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from perturb_eval import metrics
from perturb_eval.experiments import preregistered as pr
from perturb_eval.experiments.e_v05_real_traces import analyse_v05_run

GATE_KEYS = {"gate", "value", "threshold", "pass", "evaluable", "reason"}


def _step(r: int, agent: str, conf: float, source: str = "llm", **content) -> dict:
    return {"round_index": r, "agent_name": agent, "llm_confidence": conf,
            "source": source, "model_id": "m/a" if source == "llm" else None,
            "proposal_content": dict(content)}


def _run(task: str, seed: int, msd: float, rounds: list[list[float]],
         dataset: str = "adamson_full") -> dict:
    agents = ("DataCurator", "Literature", "Architect", "Trainer", "Validator")
    steps = [_step(r, agents[i], c) for r, confs in enumerate(rounds)
             for i, c in enumerate(confs)]
    return {"task_id": task, "dataset": dataset, "seed": seed,
            "final_msd_topk": msd, "n_rounds": len(rounds), "steps": steps}


# ---------------------------------------------------------------------------
# per_run_components
# ---------------------------------------------------------------------------

class TestPerRunComponents:
    def test_matches_metrics_module_exactly(self) -> None:
        first, last = [0.2, 0.4, 0.6, 0.8, 0.5], [0.9, 0.1, 0.5, 0.7, 0.3]
        out = pr.per_run_components(_run("A", 1, 0.1, [first, last]))
        assert out["ace_norm"] == pytest.approx(metrics.ace_norm(tuple(last)))
        dc = sum(last) / 5 - sum(first) / 5
        assert out["one_minus_delta_c"] == pytest.approx(1.0 - max(0.0, min(1.0, dc)))
        w = pr.TDI_LIFECYCLE_WEIGHTS
        assert w["ace_norm"] == pytest.approx(0.35 / 0.60)
        assert w["one_minus_delta_c"] == pytest.approx(0.25 / 0.60)
        assert out["tdi_lifecycle"] == pytest.approx(
            w["ace_norm"] * out["ace_norm"] + w["one_minus_delta_c"] * out["one_minus_delta_c"])
        assert out["reasons"] == {}

    def test_rising_confidence_lowers_one_minus_delta_c(self) -> None:
        out = pr.per_run_components(_run("A", 1, 0.1, [[0.1] * 5, [0.6] * 5]))
        assert out["one_minus_delta_c"] == pytest.approx(0.5)

    def test_fallback_only_final_round_is_undefined_not_imputed(self) -> None:
        run = _run("A", 1, 0.1, [[0.2, 0.4, 0.6, 0.8, 0.5]])
        run["steps"] += [_step(1, a, 0.9, source="fallback")
                         for a in ("DataCurator", "Literature", "Architect")]
        out = pr.per_run_components(run)
        assert out["ace_norm"] is None
        assert out["one_minus_delta_c"] is None
        assert out["tdi_lifecycle"] is None
        assert "round 1" in out["reasons"]["ace_norm"]
        assert "< 2" in out["reasons"]["ace_norm"]

    def test_mock_and_unlabelled_steps_are_not_llm(self) -> None:
        run = _run("A", 1, 0.1, [[0.2, 0.4]])
        run["steps"][1]["source"] = "mock"
        run["steps"].append({"round_index": 0, "agent_name": "Trainer",
                             "llm_confidence": 0.3, "proposal_content": {}})
        out = pr.per_run_components(run)
        assert out["ace_norm"] is None

    def test_single_round_run_delta_c_undefined(self) -> None:
        # Principal ruling 2026-09-25: ΔC needs >= 2 rounds. metrics.py's
        # ΔC = 0 convention (-> 1-ΔC = 1, maximal difficulty) is NOT used.
        out = pr.per_run_components(_run("A", 1, 0.1, [[0.2, 0.4, 0.6]]))
        assert out["n_rounds"] == 1
        assert out["delta_c"] is None
        assert out["one_minus_delta_c"] is None
        assert out["tdi_lifecycle"] is None
        assert out["reasons"]["one_minus_delta_c"] == pr.SINGLE_ROUND_REASON
        assert out["reasons"]["tdi_lifecycle"] == pr.SINGLE_ROUND_REASON
        assert pr.SINGLE_ROUND_REASON == "single-round run: ΔC requires >= 2 rounds"
        # ACE_norm is unaffected
        assert out["ace_norm"] == pytest.approx(metrics.ace_norm((0.2, 0.4, 0.6)))


# ---------------------------------------------------------------------------
# per_task_table
# ---------------------------------------------------------------------------

class TestPerTaskTable:
    def test_seed_median(self) -> None:
        rows = [
            _run("A", 1, 0.10, [[0.1] * 5, [0.2] * 5]),
            _run("A", 2, 0.30, [[0.1] * 5, [0.5] * 5]),
            _run("A", 3, 0.20, [[0.1] * 5, [0.9] * 5]),
        ]
        table = pr.per_task_table(rows)
        (row,) = table
        assert row["task"] == "A" and row["dataset"] == "adamson_full"
        assert row["msd"] == pytest.approx(0.20)
        # 1-ΔC per seed: 0.9, 0.6, 0.2 -> median 0.6
        assert row["one_minus_delta_c"] == pytest.approx(0.6)
        assert row["n_seeds"]["msd"] == 3

    def test_undefined_seed_excluded_from_median(self) -> None:
        bad = _run("A", 3, 0.9, [[0.1]])  # one llm step -> undefined
        rows = [_run("A", 1, 0.1, [[0.1] * 5, [0.2] * 5]),
                _run("A", 2, 0.3, [[0.1] * 5, [0.4] * 5]), bad]
        (row,) = pr.per_task_table(rows)
        assert row["n_seeds"]["ace_norm"] == 2
        assert row["one_minus_delta_c"] == pytest.approx((0.9 + 0.7) / 2)
        assert row["undefined"]["ace_norm"]  # reason recorded per seed

    def test_non_finite_msd_excluded(self) -> None:
        rows = [_run("A", 1, float("inf"), [[0.1] * 5]), _run("A", 2, 0.4, [[0.1] * 5])]
        (row,) = pr.per_task_table(rows)
        assert row["msd"] == pytest.approx(0.4)
        assert row["n_seeds"]["msd"] == 1


# ---------------------------------------------------------------------------
# spearman_with_ci
# ---------------------------------------------------------------------------

class TestSpearman:
    def test_perfect_rank(self) -> None:
        res = pr.spearman_with_ci([1, 2, 3, 4, 5], [10, 20, 30, 40, 50], B=200, seed=1)
        assert res["rho"] == pytest.approx(1.0)
        assert res["n"] == 5

    def test_ties_use_average_ranks(self) -> None:
        res = pr.spearman_with_ci([1, 1, 2, 3], [1, 2, 3, 4], B=50, seed=1)
        # ranks x = 1.5,1.5,3,4 ; y = 1,2,3,4
        assert res["rho"] == pytest.approx(0.9486832980505138)

    def test_deterministic_bootstrap(self) -> None:
        x = [0.3, 0.1, 0.8, 0.5, 0.9, 0.2, 0.4, 0.65, 0.15, 0.72, 0.33, 0.58, 0.05, 0.91, 0.47]
        y = [0.2, 0.3, 0.7, 0.4, 0.6, 0.1, 0.9, 0.35, 0.25, 0.81, 0.12, 0.66, 0.44, 0.52, 0.08]
        a = pr.spearman_with_ci(x, y, B=500, seed=7)
        b = pr.spearman_with_ci(x, y, B=500, seed=7)
        c = pr.spearman_with_ci(x, y, B=500, seed=8)
        assert (a["ci_low"], a["ci_high"]) == (b["ci_low"], b["ci_high"])
        assert (a["ci_low"], a["ci_high"]) != (c["ci_low"], c["ci_high"])
        assert a["ci_low"] <= a["rho"] <= a["ci_high"]

    def test_n_below_three_is_undefined(self) -> None:
        res = pr.spearman_with_ci([1, 2], [1, 2], B=10, seed=1)
        assert res["rho"] is None and res["n"] == 2

    def test_bootstrap_defaults_are_preregistered(self) -> None:
        assert pr.BOOTSTRAP_B == 10_000
        assert isinstance(pr.BOOTSTRAP_SEED, int)
        assert pr.RIDGE_ALPHA == 1.0


# ---------------------------------------------------------------------------
# gates
# ---------------------------------------------------------------------------

def _table(tasks: list[tuple[str, str, float, float, float]]) -> list[dict]:
    """(task, dataset, ace_norm, one_minus_delta_c, msd) -> per-task rows."""
    out = []
    for t, ds, a, d, m in tasks:
        out.append({"task": t, "dataset": ds, "ace_norm": a, "one_minus_delta_c": d,
                    "tdi_lifecycle": pr.tdi_lifecycle(a, d), "msd": m,
                    "n_seeds": {}, "undefined": {}})
    return out


class TestH4:
    def test_ace_perfectly_ranks_msd_passes(self) -> None:
        table = _table([(f"t{i}", "adamson_full", 0.1 * i, 0.5, 0.01 * i) for i in range(1, 8)])
        res = pr.h4(table, B=200, seed=3)
        assert GATE_KEYS <= set(res)
        assert res["pass"] is True and res["evaluable"] is True
        assert res["per_dataset"]["adamson_full"]["ace_norm"]["rho"] == pytest.approx(1.0)
        assert res["threshold"] == 0.5
        assert res["n_tests"] == 6
        assert set(res["structurally_undefined"]) == {"csd", "wfr"}

    def test_pass_is_none_when_n_below_three(self) -> None:
        table = _table([("a", "norman", 0.1, 0.2, 0.1), ("b", "norman", 0.2, 0.3, 0.2)])
        res = pr.h4(table, B=50, seed=3)
        assert res["pass"] is None and res["evaluable"] is False
        assert res["reason"]

    def test_all_three_components_reported_per_dataset(self) -> None:
        table = _table([(f"t{i}", "norman", 0.5, 0.1 * (7 - i), 0.01 * i) for i in range(7)])
        res = pr.h4(table, B=50, seed=3)
        assert set(res["per_dataset"]) == {"adamson_full", "norman"}
        for ds in ("adamson_full", "norman"):
            assert set(res["per_dataset"][ds]) == {"ace_norm", "one_minus_delta_c", "tdi_lifecycle"}
        assert res["per_dataset"]["norman"]["ace_norm"]["rho"] is None  # constant
        assert res["per_dataset"]["adamson_full"]["ace_norm"]["n"] == 0
        assert res["pass"] is None  # some of the 6 unevaluable, none passes: cannot conclude FAIL

    def test_passes_if_either_dataset_passes(self) -> None:
        # Adamson: every component anti-ranks MSD; Norman: ACE ranks it perfectly.
        ad = _table([(f"a{i}", "adamson_full", 0.1 * i, 0.1 * i, 0.1 * (5 - i)) for i in range(4)])
        no = _table([(f"n{i}", "norman", 0.1 * i, 0.5, 0.1 * i) for i in range(4)])
        res = pr.h4(ad + no, B=50, seed=3)
        assert res["per_dataset"]["adamson_full"]["ace_norm"]["rho"] == pytest.approx(-1.0)
        assert res["per_dataset"]["norman"]["ace_norm"]["rho"] == pytest.approx(1.0)
        assert res["pass"] is True

    def test_pooled_rho_is_descriptive_only(self) -> None:
        # Within each dataset every component anti-ranks MSD (rho = -1), but
        # pooled across datasets ACE_norm ranks MSD with rho = 0.543 > 0.5.
        ad = _table([(f"a{i}", "adamson_full", v, v, m)
                     for i, (v, m) in enumerate([(0.1, 0.3), (0.2, 0.2), (0.3, 0.1)])])
        no = _table([(f"n{i}", "norman", v, v, m)
                     for i, (v, m) in enumerate([(0.7, 0.9), (0.8, 0.8), (0.9, 0.7)])])
        res = pr.h4(ad + no, B=50, seed=3)
        assert res["pooled_descriptive"]["ace_norm"]["rho"] == pytest.approx(1 - 96 / 210)
        assert res["pooled_descriptive"]["ace_norm"]["rho"] > 0.5
        assert res["pass"] is False  # all 6 per-dataset tests evaluable, none > 0.5
        assert res["value"] == pytest.approx(-1.0)

    def test_single_round_exclusions_counted(self) -> None:
        two = [[0.1] * 5, [0.5] * 5]
        rows = []
        for i in range(4):
            rows += [_run(f"a{i}", 1, 0.1 * (i + 1), two), _run(f"a{i}", 2, 0.1 * (i + 1), two)]
        rows.append(_run("a0", 3, 0.1, [[0.2, 0.4, 0.6, 0.8, 0.5]]))  # one round, excluded
        # task a9: only single-round runs -> drops out of 1-ΔC / TDI rho, kept for ACE
        rows += [_run("a9", s, 0.9, [[0.2, 0.4, 0.6, 0.8, 0.5]]) for s in (1, 2, 3)]
        table = pr.per_task_table(rows)
        a0 = next(r for r in table if r["task"] == "a0")
        assert a0["n_seeds"]["one_minus_delta_c"] == 2
        assert a0["n_single_round_runs"] == 1
        res = pr.h4(table, B=50, seed=3)
        ex = res["exclusions"]["adamson_full"]
        assert ex["one_minus_delta_c"] == {"runs_undefined": 4, "runs_single_round": 4,
                                           "tasks_dropped": 1}
        assert ex["tdi_lifecycle"]["tasks_dropped"] == 1
        assert ex["ace_norm"] == {"runs_undefined": 0, "runs_single_round": 0, "tasks_dropped": 0}
        assert res["per_dataset"]["adamson_full"]["ace_norm"]["n"] == 5
        assert res["per_dataset"]["adamson_full"]["one_minus_delta_c"]["n"] == 4


class TestH5:
    def _tables(self):
        ad = _table([(f"a{i}", "adamson_full", 0.9 + 0.01 * i, 0.3 + 0.05 * (i % 3), 0.02 * i)
                     for i in range(8)])
        no = _table([(f"n{i}", "norman", 0.9 + 0.012 * i, 0.4 + 0.03 * (i % 2), 0.03 * i)
                     for i in range(6)])
        return ad, no

    def test_weights_fit_on_adamson_only_and_applied_unchanged(self, monkeypatch) -> None:
        ad, no = self._tables()
        seen: list[tuple] = []
        real = pr.fit_ridge

        def spy(X, y, *, alpha):
            seen.append((X, y, alpha))
            return real(X, y, alpha=alpha)

        monkeypatch.setattr(pr, "fit_ridge", spy)
        res = pr.h5(ad, no, B=100, seed=4)
        assert len(seen) == 1
        X, y, alpha = seen[0]
        assert alpha == pr.RIDGE_ALPHA
        # The fit sees exactly the Adamson rows and nothing else.
        assert [list(row) for row in X] == [[r[k] for k in pr.H5_FEATURES] for r in ad]
        assert list(y) == [r["msd"] for r in ad]
        assert GATE_KEYS <= set(res)
        assert res["threshold"] == 0.4
        assert res["n_fit"] == len(ad) and res["n"] == len(no)
        # Applied unchanged: recomputing Norman TDI from the reported weights
        w, mu, sd = res["weights"], res["standardise_mean"], res["standardise_sd"]
        expected = [sum(w[k] * (r[k] - mu[k]) / sd[k] for k in pr.H5_FEATURES) for r in no]
        assert res["norman_tdi"] == pytest.approx(expected)

    def test_norman_too_small_not_evaluable(self) -> None:
        ad, no = self._tables()
        res = pr.h5(ad, no[:2], B=50, seed=4)
        assert res["pass"] is None and res["evaluable"] is False


class TestH1H2:
    def test_summary_statistics(self) -> None:
        best = {"a": 0.1, "b": 0.2, "c": 0.3, "d": 0.4, "e": 0.5}
        res = pr.h1_h2_stats(best, threshold=0.35, gate="H1", B=200, seed=5)
        assert GATE_KEYS <= set(res)
        assert res["value"] == pytest.approx(0.3)
        assert res["pass"] is True
        assert res["iqr"] == [pytest.approx(0.2), pytest.approx(0.4)]
        assert res["max"] == pytest.approx(0.5)
        assert res["fraction_over_gate"] == pytest.approx(2 / 5)
        assert res["ci_low"] <= res["value"] <= res["ci_high"]
        assert res["n"] == 5

    def test_strata_split(self) -> None:
        best = {"s1": 0.1, "s2": 0.2, "s3": 0.3, "d1": 0.8, "d2": 0.9}
        strata = {"s1": "singleton", "s2": "singleton", "s3": "singleton",
                  "d1": "doublet", "d2": "doublet"}
        res = pr.h1_h2_stats(best, threshold=0.3, gate="H2", strata=strata, B=100, seed=5)
        assert res["strata"]["singleton"]["median"] == pytest.approx(0.2)
        assert res["strata"]["doublet"]["n"] == 2

    def test_small_n_not_evaluable(self) -> None:
        res = pr.h1_h2_stats({"a": 0.1}, threshold=0.2, gate="H1", B=10, seed=5)
        assert res["pass"] is None and res["evaluable"] is False


class TestH3:
    def test_gate_shape(self) -> None:
        res = pr.h3(0.7, pick_counts={"linear": 2, "mlp": 1}, n_llm_steps=3,
                    n_distinct_model_ids=1)
        assert GATE_KEYS <= set(res) and res["pass"] is True
        none = pr.h3(None, pick_counts={}, n_llm_steps=0, n_distinct_model_ids=0)
        assert none["pass"] is None and none["evaluable"] is False


# ---------------------------------------------------------------------------
# wiring into analyse_v05_run
# ---------------------------------------------------------------------------

def _write(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))


def test_analyse_v05_run_carries_preregistered_block(tmp_path: Path) -> None:
    prereg = {"path": "paper/PREREGISTRATION.md", "sha256": "a" * 64, "commit": "c" * 40}
    prov = {"record_type": "provenance", "run_id": "r1", "git_sha": "g1", "status": "ok",
            "finished_at": "2026-09-25T00:00:00Z", "preregistration": prereg,
            "tasks": {"adamson": [f"A{i}" for i in range(4)],
                      "norman_singletons": ["N0", "N1", "N2"], "norman_doublets": ["N3_N4"]}}
    tasks = [("adamson_full", f"A{i}") for i in range(4)] + \
            [("norman", t) for t in ("N0", "N1", "N2", "N3_N4")]
    trainer = [{"dataset": ds, "task": t, "backbone": "linear", "N": 3, "R": 1, "seed": 1,
                "msd_topk": 0.05 * (k + 1)} for k, (ds, t) in enumerate(tasks)]
    life = []
    for k, (ds, t) in enumerate(tasks):
        for s in (1, 2, 3):
            run = _run(t, s, 0.05 * (k + 1), [[0.1 * ((k % 5) + 1)] * 5, [0.5] * 5], dataset=ds)
            for st in run["steps"]:
                if st["agent_name"] == "Architect":
                    st["proposal_content"] = {"backbone": ["linear", "mlp", "scgpt_small"][k % 3]}
            life.append(run)
    tj, lj = tmp_path / "trainer_runs.jsonl", tmp_path / "lifecycle_runs.jsonl"
    _write(tj, [prov] + trainer)
    _write(lj, [prov] + life)
    summary = analyse_v05_run(tj, lj)
    assert summary["preregistration"] == prereg
    block = summary["preregistered"]
    assert set(block) >= {"H1", "H2", "H3", "H4", "H5", "tally"}
    for h in ("H1", "H2", "H3", "H4", "H5"):
        assert GATE_KEYS <= set(block[h]), h
    assert block["H2"]["strata"]["doublet"]["n"] == 1
    assert block["tally"]["out_of"] == 5
    assert summary["gate_adamson_median_below_0_20"] is block["H1"]["pass"]
    assert math.isfinite(block["H4"]["per_dataset"]["adamson_full"]["one_minus_delta_c"]["rho"])
    assert "pooled_descriptive" in block["H4"]


def test_dead_estimator_removed() -> None:
    import perturb_eval.experiments.e_v05_real_traces as mod
    assert not hasattr(mod, "tdi_vs_held_out_msd")


class TestH4ReportAllSix:
    """CTO #269 (b): all six rho are reported with their n REGARDLESS of outcome, so a single-test
    PASS is self-evident from the table and selective reporting is structurally impossible."""

    def test_all_six_rows_present_when_pass_by_one_test_and_others_undefined(self) -> None:
        # Adamson: ACE ranks MSD perfectly (one passing test); Norman: only 2 tasks -> every Norman test undefined.
        table = _table([(f"a{i}", "adamson_full", 0.1 * i, 0.5, 0.01 * i) for i in range(1, 8)]
                       + [("n1", "norman", 0.2, 0.3, 0.1), ("n2", "norman", 0.4, 0.6, 0.2)])
        res = pr.h4(table, B=200, seed=3)
        rows = res["all_six"]
        assert len(rows) == 6
        assert {(r["dataset"], r["component"]) for r in rows} == {
            (ds, k) for ds in ("adamson_full", "norman") for k in ("ace_norm", "one_minus_delta_c", "tdi_lifecycle")}
        for r in rows:
            assert set(r) >= {"dataset", "component", "rho", "n", "ci_low", "ci_high", "reason", "passes"}
            assert (r["rho"] is None) == (r["reason"] is not None)
        norman = [r for r in rows if r["dataset"] == "norman"]
        assert all(r["rho"] is None and r["n"] == 2 and r["passes"] is None for r in norman)
        # 1-dC is constant here, so TDI_lifecycle inherits ACE's ranking exactly: TWO tests pass, not one.
        # That is the within-dataset dependence the pre-registration states (TDI is built from the other two).
        assert res["pass"] is True and res["n_tests_passing"] == 2
        passing = {(r["dataset"], r["component"]) for r in res["all_six"] if r["passes"]}
        assert passing == {("adamson_full", "ace_norm"), ("adamson_full", "tdi_lifecycle")}

    def test_all_six_rows_present_on_fail(self) -> None:
        table = _table([(f"a{i}", "adamson_full", 0.1 * i, 0.1 * i, 0.07 - 0.01 * i) for i in range(1, 8)]
                       + [(f"n{i}", "norman", 0.1 * i, 0.1 * i, 0.07 - 0.01 * i) for i in range(1, 8)])
        res = pr.h4(table, B=200, seed=3)
        assert len(res["all_six"]) == 6 and res["pass"] is False and res["n_tests_passing"] == 0
