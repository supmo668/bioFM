"""Amendment 2 measurand fixes (paper/PREREGISTRATION.md, A2-6, A2-10, A2-11).

Hand-built fixtures only; every expected value can be checked by hand.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from perturb_eval import metrics
from perturb_eval.experiments import preregistered as pr
from perturb_eval.experiments.e_v05_real_traces import analyse_v05_run, architect_entropies


def _step(r: int, agent: str, conf: float, source: str = "llm", **extra) -> dict:
    return {
        "round_index": r,
        "agent_name": agent,
        "llm_confidence": conf,
        "source": source,
        "model_id": "m/a" if source == "llm" else None,
        "proposal_content": {},
        **extra,
    }


def _run(
    rounds: list[list[float]],
    task: str = "A",
    seed: int = 1,
    msd: float = 0.1,
    dataset: str = "adamson_full",
) -> dict:
    agents = ("DataCurator", "Literature", "Architect", "Trainer", "Validator")
    steps = [_step(r, agents[i], c) for r, confs in enumerate(rounds) for i, c in enumerate(confs)]
    return {
        "task_id": task,
        "dataset": dataset,
        "seed": seed,
        "final_msd_topk": msd,
        "n_rounds": len(rounds),
        "steps": steps,
    }


# ---------------------------------------------------------------------------
# A2-11: 1-ΔC and TDI_lifecycle are unclipped
# ---------------------------------------------------------------------------


class TestA211Unclipped:
    def test_falling_confidence_ranks_above_flat(self) -> None:
        flat = pr.per_run_components(_run([[0.6] * 5, [0.6] * 5, [0.6] * 5]))
        falling = pr.per_run_components(_run([[0.8] * 5, [0.6] * 5, [0.4] * 5]))
        assert flat["one_minus_delta_c"] == pytest.approx(1.0)
        assert falling["one_minus_delta_c"] == pytest.approx(1.4)
        assert falling["one_minus_delta_c"] > flat["one_minus_delta_c"]
        # ACE is identical (uniform last rounds), so TDI inherits the 1-ΔC ordering
        assert falling["ace_norm"] == pytest.approx(flat["ace_norm"]) == pytest.approx(1.0)
        assert falling["tdi_lifecycle"] > flat["tdi_lifecycle"]
        # the clipped value, descriptive only, ties them (the defect A2-11 removes)
        assert falling["one_minus_delta_c_clipped"] == flat["one_minus_delta_c_clipped"] == 1.0

    def test_tdi_above_one_is_not_clipped(self) -> None:
        out = pr.per_run_components(_run([[0.8] * 5, [0.2] * 5]))
        # ACE (ace_d of a uniform vector) = 1; 1-ΔC = 1 - (0.2 - 0.8) = 1.6
        assert out["ace_norm"] == pytest.approx(1.0)
        assert out["one_minus_delta_c"] == pytest.approx(1.6)
        assert out["tdi_lifecycle"] == pytest.approx(7 / 12 * 1.0 + 5 / 12 * 1.6)
        assert out["tdi_lifecycle"] > 1.0

    def test_tdi_function_has_no_outer_clip(self) -> None:
        assert pr.tdi_lifecycle(1.0, 2.0) == pytest.approx(17 / 12)
        assert pr.tdi_lifecycle(0.0, 0.0) == 0.0
        assert pr.tdi_lifecycle(0.5, 1.5) == pytest.approx(7 / 24 + 7.5 / 12)

    def test_weights_carried_over_unchanged(self) -> None:
        assert pr.TDI_LIFECYCLE_WEIGHTS == {
            "ace_norm": pytest.approx(7 / 12),
            "one_minus_delta_c": pytest.approx(5 / 12),
        }

    def test_one_minus_delta_c_range_endpoints(self) -> None:
        up = pr.per_run_components(_run([[0.0, 0.0], [1.0, 1.0]]))
        down = pr.per_run_components(_run([[1.0, 1.0], [0.0, 0.0]]))
        assert up["one_minus_delta_c"] == pytest.approx(0.0)
        assert down["one_minus_delta_c"] == pytest.approx(2.0)
        assert down["one_minus_delta_c_clipped"] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# A2-10: ACE is ace_d; the softmax value is descriptive only
# ---------------------------------------------------------------------------


class TestA210AceD:
    def test_ace_uses_full_range(self) -> None:
        conc = pr.per_run_components(_run([[0.5] * 5, [1.0, 0.0, 0.0, 0.0, 0.0]]))
        assert conc["ace_norm"] == pytest.approx(0.0)
        # the softmax value of the same vector sits in the narrow band near 1
        assert conc["ace_norm_softmax"] == pytest.approx(metrics.ace_norm((1.0, 0, 0, 0, 0)))
        assert conc["ace_norm_softmax"] > 0.9

    def test_softmax_not_called_for_gated_value(self, monkeypatch) -> None:
        monkeypatch.setattr(metrics, "ace_norm", lambda *_a, **_k: 123.0)
        out = pr.per_run_components(_run([[0.2, 0.4], [0.3, 0.9]]))
        assert out["ace_norm"] == pytest.approx(metrics.ace_d((0.3, 0.9)))
        assert out["ace_norm_softmax"] == 123.0
        assert out["tdi_lifecycle"] == pytest.approx(
            pr.tdi_lifecycle(out["ace_norm"], out["one_minus_delta_c"])
        )

    def test_descriptive_keys_carried_in_task_table_but_not_gated(self) -> None:
        rows = [_run([[0.2] * 5, [0.1 * (s + 1)] * 5], seed=s) for s in range(3)]
        (row,) = pr.per_task_table(rows)
        assert {"ace_norm_softmax", "one_minus_delta_c_clipped"} <= set(row)
        assert row["n_seeds"]["ace_norm_softmax"] == 3
        assert set(pr.H4_COMPONENTS) == {"ace_norm", "one_minus_delta_c", "tdi_lifecycle"}
        assert set(pr.H5_FEATURES) == {"ace_norm", "one_minus_delta_c"}
        for k in pr.DESCRIPTIVE_COMPONENTS:
            assert k not in pr.H4_COMPONENTS and k not in pr.H5_FEATURES

    def test_h4_reports_descriptive_rho_beside_but_never_gates_on_it(self) -> None:
        # the descriptive softmax value ranks MSD perfectly; every gated component anti-ranks it
        table = [
            {
                "task": f"t{i}",
                "dataset": "adamson_full",
                "ace_norm": 1.0 - 0.1 * i,
                "one_minus_delta_c": 1.0 - 0.1 * i,
                "tdi_lifecycle": 1.0 - 0.1 * i,
                "ace_norm_softmax": 0.9 + 0.01 * i,
                "one_minus_delta_c_clipped": 0.5,
                "msd": 0.1 * i,
                "n_seeds": {},
                "undefined": {},
            }
            for i in range(5)
        ]
        res = pr.h4(table, B=50, seed=1)
        desc = res["descriptive"]["adamson_full"]
        assert desc["ace_norm_softmax"]["rho"] == pytest.approx(1.0)
        assert desc["one_minus_delta_c_clipped"]["rho"] is None  # constant
        assert res["n_tests_passing"] == 0
        assert res["value"] == pytest.approx(-1.0)
        assert len(res["all_six"]) == 6
        assert all(r["component"] in pr.H4_COMPONENTS for r in res["all_six"])


# ---------------------------------------------------------------------------
# A2-6: H3 gates on the STATED backbone; executed reported alongside
# ---------------------------------------------------------------------------


def _arch(stated=None, executed=None, *, source="llm", model_id="m/a", **extra) -> dict:
    s = {
        "agent_name": "Architect",
        "source": source,
        "model_id": model_id,
        "proposal_content": {},
        **extra,
    }
    if stated is not None:
        s["backbone_stated"] = stated
    if executed is not None:
        s["backbone_executed"] = executed
    return s


class TestA26H3Stated:
    def test_menu_is_pinned_and_ceiling_derived(self) -> None:
        from perturb_eval.agentic_lifecycle.validator_gate import _BACKBONE_ROTATION

        assert pr.BACKBONE_MENU == ("linear", "mlp", "scgpt_small")
        assert set(_BACKBONE_ROTATION) == set(pr.BACKBONE_MENU)
        res = pr.h3(0.7, pick_counts={"linear": 1}, n_llm_steps=1, n_distinct_model_ids=1)
        assert res["ceiling_nats"] == pytest.approx(math.log(3))
        assert res["menu"] == list(pr.BACKBONE_MENU)

    def test_ceiling_and_miller_madow_follow_the_menu_not_a_literal(self, monkeypatch) -> None:
        """QG-11 (A2-6): ``h3()`` reads the ceiling from the menu constant and
        Miller-Madow uses K = |menu|. A four-name menu must give ln 4 and
        (4 - 1) / (2N); a hard-coded ln 3 or K = 3 fails here."""
        menu4 = ("linear", "mlp", "scgpt_small", "transformer")
        monkeypatch.setattr(pr, "BACKBONE_MENU", menu4)
        res = pr.h3(0.7, pick_counts={"linear": 1}, n_llm_steps=1, n_distinct_model_ids=1)
        assert res["menu"] == list(menu4)
        assert res["ceiling_nats"] == pytest.approx(math.log(4))
        assert res["ceiling_nats"] != pytest.approx(math.log(3))
        # Miller-Madow: N = 4 stated picks (3 linear, 1 mlp), K = |menu| = 4.
        steps = [_arch("linear")] * 3 + [_arch("mlp")]
        st = pr.architect_backbone_stats(steps)
        h = -(0.75 * math.log(0.75) + 0.25 * math.log(0.25))
        assert st["menu"] == list(menu4)
        assert st["entropy_stated_nats"] == pytest.approx(h)
        assert st["miller_madow_stated_nats"] == pytest.approx(h + (4 - 1) / (2 * 4))
        assert st["miller_madow_stated_nats"] != pytest.approx(h + (3 - 1) / (2 * 4))
        # And the menu-wide gate output derived from those stats carries ln 4.
        assert pr.h3_from_stats(st)["ceiling_nats"] == pytest.approx(math.log(4))

    def test_entropy_from_stated_not_executed(self) -> None:
        # Stated: 2 linear, 2 mlp; executed: all overridden to scgpt_small.
        steps = [
            _arch("linear", "scgpt_small"),
            _arch("linear", "scgpt_small"),
            _arch("mlp", "scgpt_small"),
            _arch("mlp", "scgpt_small"),
        ]
        st = pr.architect_backbone_stats(steps)
        assert st["stated_counts"] == {"linear": 2, "mlp": 2}
        assert st["entropy_stated_nats"] == pytest.approx(math.log(2))
        assert st["executed_counts"] == {"scgpt_small": 4}
        assert st["entropy_executed_nats"] == pytest.approx(0.0)
        assert st["n_executed_ne_stated"] == 4
        assert st["n_counted"] == 4

    def test_executed_legacy_name_backbone_used_is_read(self) -> None:
        st = pr.architect_backbone_stats([_arch("mlp", backbone_used="linear")])
        assert st["executed_counts"] == {"linear": 1}
        assert st["n_executed_ne_stated"] == 1

    def test_missing_stated_is_never_defaulted_or_counted(self) -> None:
        steps = [
            _arch("linear", "linear"),
            _arch("mlp", "mlp"),
            _arch(None, "linear", proposal_content={"backbone": "linear"}),
        ]
        st = pr.architect_backbone_stats(steps)
        assert st["stated_counts"] == {"linear": 1, "mlp": 1}
        assert st["n_missing_stated"] == 1
        assert st["n_counted"] == 2
        assert st["entropy_stated_nats"] == pytest.approx(math.log(2))

    def test_off_menu_stated_is_never_counted(self) -> None:
        steps = [_arch("linear"), _arch("mlp"), _arch("scgpt"), _arch("transformer")]
        st = pr.architect_backbone_stats(steps)
        assert st["stated_counts"] == {"linear": 1, "mlp": 1}
        assert st["n_off_menu_stated"] == 2
        assert st["off_menu_values"] == {"scgpt": 1, "transformer": 1}

    def test_non_llm_steps_excluded(self) -> None:
        steps = [
            _arch("linear"),
            _arch("mlp", source="fallback"),
            _arch("mlp", source="mock"),
            _arch("mlp", source=None),
            {"agent_name": "Trainer", "source": "llm", "backbone_stated": "mlp"},
        ]
        st = pr.architect_backbone_stats(steps)
        assert st["stated_counts"] == {"linear": 1}
        assert st["n_llm_architect_steps"] == 1

    def test_schema_failure_withdraws_gate(self) -> None:
        steps = [_arch(b) for b in ("linear", "mlp", "scgpt_small")] + [_arch(None)]
        st = pr.architect_backbone_stats(steps)
        res = pr.h3_from_stats(st)
        assert res["pass"] is None and res["evaluable"] is False
        assert "schema failure" in res["reason"]
        assert res["n_missing_stated"] == 1

    def test_h3_from_stats_gates_on_stated(self) -> None:
        steps = [_arch(b, "linear") for b in ("linear", "mlp", "scgpt_small")]
        res = pr.h3_from_stats(pr.architect_backbone_stats(steps))
        assert res["value"] == pytest.approx(math.log(3))
        assert res["pass"] is True
        assert res["pick_counts"] == {"linear": 1, "mlp": 1, "scgpt_small": 1}
        assert res["executed_pick_counts"] == {"linear": 3}
        assert res["n_executed_ne_stated"] == 2
        assert res["n_llm_architect_steps"] == 3

    def test_no_stated_picks_is_unevaluable(self) -> None:
        res = pr.h3_from_stats(pr.architect_backbone_stats([]))
        assert res["pass"] is None and res["value"] is None

    def test_miller_madow_beside_plugin_for_small_n(self) -> None:
        steps = (
            [_arch("linear", model_id="m/a")] * 3
            + [_arch("mlp", model_id="m/a")]
            + [_arch(b, model_id="m/b") for b in ("linear", "mlp", "scgpt_small")] * 20
        )
        st = pr.architect_backbone_stats(steps)
        a, b = st["by_model_id"]["m/a"], st["by_model_id"]["m/b"]
        h_a = -(0.75 * math.log(0.75) + 0.25 * math.log(0.25))
        assert a["n"] == 4 and a["entropy_nats"] == pytest.approx(h_a)
        assert a["miller_madow_nats"] == pytest.approx(
            h_a + (3 - 1) / (2 * 4)
        )  # K = |menu| = 3 (A2-6)
        assert b["n"] == 60 and b["entropy_nats"] == pytest.approx(math.log(3))
        assert b["miller_madow_nats"] is None  # N >= 50: plug-in only
        assert st["miller_madow_stated_nats"] is None  # pooled N = 64 >= 50

    def test_analyser_h3_uses_stated(self, tmp_path: Path) -> None:
        rows = []
        for i, (stated, executed) in enumerate(
            [("linear", "mlp"), ("mlp", "mlp"), ("scgpt_small", "mlp")]
        ):
            rows.append(
                {
                    "task_id": f"A{i}",
                    "dataset": "adamson_full",
                    "seed": 1,
                    "final_msd_topk": 0.1,
                    "steps": [
                        dict(
                            _arch(stated, executed),
                            round_index=0,
                            llm_confidence=0.5,
                            proposal_content={"backbone": executed},
                        )
                    ],
                }
            )
        e = architect_entropies(rows)
        assert e["architect_backbone_entropy_nats"] == pytest.approx(math.log(3))
        assert e["architect_backbone_distribution"] == {"linear": 1, "mlp": 1, "scgpt_small": 1}
        assert e["architect_backbone_executed_distribution"] == {"mlp": 3}
        assert e["architect_backbone_executed_entropy_nats"] == pytest.approx(0.0)
        assert e["architect_backbone_n_executed_ne_stated"] == 2

        tj, lj = tmp_path / "t.jsonl", tmp_path / "l.jsonl"
        trainer = [
            {
                "dataset": "adamson_full",
                "task": f"A{i}",
                "backbone": "linear",
                "N": 3,
                "R": 1,
                "seed": 1,
                "msd_topk": 0.1,
            }
            for i in range(3)
        ]
        tj.write_text("".join(json.dumps(r) + "\n" for r in trainer))
        lj.write_text("".join(json.dumps(r) + "\n" for r in rows))
        summary = analyse_v05_run(tj, lj)
        h3 = summary["preregistered"]["H3"]
        assert h3["value"] == pytest.approx(math.log(3))
        assert h3["executed_pick_counts"] == {"mlp": 3}
        assert h3["n_executed_ne_stated"] == 2


# ---------------------------------------------------------------------------
# A2-4: N is dropped; configurations are backbone x R, seeds are replicates
# ---------------------------------------------------------------------------


def _trow(backbone: str, R: int, seed: int, msd: float, task: str = "TFA", **extra) -> dict:
    return {
        "dataset": "adamson_full",
        "task": task,
        "backbone": backbone,
        "R": R,
        "seed": seed,
        "msd_topk": msd,
        **extra,
    }


class TestA24NoNAxis:
    def _write(self, tmp_path: Path, rows: list[dict]) -> Path:
        p = tmp_path / "trainer.jsonl"
        p.write_text("".join(json.dumps(r) + "\n" for r in rows))
        return p

    def test_oracle_is_min_over_distinct_backbone_x_r_configs(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.e_v05_real_traces import best_config_per_task

        rows = [
            _trow("linear", 1, 1, 0.50),
            _trow("linear", 1, 2, 0.50),  # linear ignores seed
            _trow("mlp", 2, 1, 0.30),
            _trow("mlp", 2, 2, 0.20),
            _trow("mlp", 3, 1, 0.40),
            _trow("mlp", 3, 2, float("nan")),
        ]
        bc = best_config_per_task(self._write(tmp_path, rows))[("adamson_full", "TFA")]
        assert bc.best_msd == pytest.approx(0.20)
        assert bc.best_config == {"backbone": "mlp", "R": 2, "seed": 2, "dataset": "adamson_full"}
        assert "N" not in bc.best_config
        assert (
            bc.n_configs_tried == 3
        )  # distinct (backbone, R) actually run: linear/1, mlp/2, mlp/3
        assert bc.n_records == 5  # finite records
        assert bc.seeds == (1, 2)

    def test_r_invariant_backbone_counts_once_matching_trainer_grid(self, tmp_path: Path) -> None:
        """QG-7 / amendment 3: linear at R=1,2,3 x 2 seeds is ONE configuration; the
        analyser's n_configs_tried and trainer_grid's n_distinct_configs_per_task agree."""
        from perturb_eval.experiments import heldout
        from perturb_eval.experiments.e_v05_real_traces import best_config_per_task

        rows = [_trow("linear", R, s, 0.5) for R in (1, 2, 3) for s in (1, 2)]
        rows += [_trow("mlp", R, s, 0.3) for R in (1, 2, 3) for s in (1, 2)]
        bc = best_config_per_task(self._write(tmp_path, rows))[("adamson_full", "TFA")]
        grid = heldout.trainer_grid(backbones=("linear", "mlp"), r_sweep=(1, 2, 3), seeds=(1, 2))
        assert bc.n_configs_tried == 4 == grid["n_distinct_configs_per_task"]
        assert grid["n_distinct_fits_per_task"] == 7 and bc.n_records == 12

    def test_legacy_n_field_is_not_a_config_axis(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.e_v05_real_traces import (
            best_config_per_task,
            median_msd_per_config,
        )

        rows = [
            _trow("linear", 1, 1, 0.1, N=3),
            _trow("linear", 1, 1, 0.2, N=5),
            _trow("linear", 1, 2, 0.3, N=3),
        ]
        p = self._write(tmp_path, rows)
        assert best_config_per_task(p)[("adamson_full", "TFA")].n_configs_tried == 1
        (entry,) = median_msd_per_config(p)
        assert set(entry) == {"dataset", "backbone", "R", "median_msd", "n_seeds"}
        assert entry["median_msd"] == pytest.approx(0.2)
        assert entry["n_seeds"] == 3

    def test_median_per_config_groups_backbone_x_r(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.e_v05_real_traces import median_msd_per_config

        rows = [_trow("mlp", 1, s, m) for s, m in ((1, 0.1), (2, 0.3))] + [
            _trow("mlp", 2, s, m) for s, m in ((1, 0.5), (2, 0.7))
        ]
        out = sorted(median_msd_per_config(self._write(tmp_path, rows)), key=lambda r: r["R"])
        assert [(r["backbone"], r["R"], r["median_msd"], r["n_seeds"]) for r in out] == [
            ("mlp", 1, pytest.approx(0.2), 2),
            ("mlp", 2, pytest.approx(0.6), 2),
        ]
