"""P3 analyser contract tests (T14 reader, T15 hard-fail, T16 llm-only entropy,
C-KEY-2 fallback refusal, partial-run refusal).

Fixtures are tiny JSONL files written into ``tmp_path``.
"""

from __future__ import annotations

import json
import logging
import math
from pathlib import Path

import pytest

from perturb_eval.experiments.e_v05_real_traces import (
    ROLES,
    _read_jsonl,
    analyse_v05_run,
    main,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
V050 = PROJECT_ROOT / "artifacts" / "v0.5.0"


def _prov(**over) -> dict:
    rec = {
        "record_type": "provenance",
        "run_id": "run-abc",
        "git_sha": "deadbeef",
        "tasks": ["T0", "T1"],
        "status": "ok",
        "finished_at": 1234.0,
    }
    rec.update(over)
    return rec


def _write(path: Path, rows: list[dict]) -> Path:
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    return path


def _trainer_row(task: str, msd: float = 0.1, dataset: str = "adamson_full") -> dict:
    return {
        "dataset": dataset, "task": task, "backbone": "linear", "N": 3, "R": 1,
        "seed": 1, "msd_topk": msd, "wall_sec": 0.1, "hvg_n": 2000,
        "hvg_n_forced": 0, "hvg_mode": "seurat", "n_params": 10,
    }


def _step(role: str, content: dict, source: str | None = "llm") -> dict:
    s = {"round_index": 0, "agent_name": role, "proposal_content": content,
         "model_id": "m/x" if source == "llm" else None}
    if source is not None:
        s["source"] = source
    return s


def _life_row(task: str, steps: list[dict], msd: float = 0.2) -> dict:
    return {"task_id": task, "seed": 1, "final_msd_topk": msd, "steps": steps}


def _run(tmp_path: Path, trainer_rows, life_rows, *, tprov=None, lprov=None):
    t_rows = ([tprov] if tprov is not None else []) + trainer_rows
    l_rows = ([lprov] if lprov is not None else []) + life_rows
    return (_write(tmp_path / "trainer_runs.jsonl", t_rows),
            _write(tmp_path / "lifecycle_runs.jsonl", l_rows))


def _arch(bb: str, source: str | None = "llm") -> dict:
    return _step("Architect", {"backbone": bb, "hvg_count": 2000}, source)


# ---------------------------------------------------------------- T14 reader
class TestReadJsonlProvenance:
    def test_record0_provenance_split_from_rows(self, tmp_path: Path) -> None:
        p = _write(tmp_path / "x.jsonl", [_prov(), _trainer_row("T0"), _trainer_row("T1")])
        prov, rows = _read_jsonl(p)
        assert prov is not None and prov["run_id"] == "run-abc"
        assert len(rows) == 2
        assert all(r.get("record_type") != "provenance" for r in rows)

    def test_no_provenance_returns_none(self, tmp_path: Path) -> None:
        p = _write(tmp_path / "x.jsonl", [_trainer_row("T0")])
        prov, rows = _read_jsonl(p)
        assert prov is None
        assert len(rows) == 1

    def test_missing_file(self, tmp_path: Path) -> None:
        assert _read_jsonl(tmp_path / "nope.jsonl") == (None, [])

    def test_legacy_artifacts_warn(self, tmp_path: Path, caplog) -> None:
        t, l = _run(tmp_path, [_trainer_row("T0")], [_life_row("T0", [_arch("mlp")])])
        with caplog.at_level(logging.WARNING):
            summary = analyse_v05_run(t, l)
        assert "legacy artifact without provenance record" in caplog.text
        assert summary["status"] == "legacy_no_provenance"


# ---------------------------------------------------------------- T15 hard-fail
class TestTaskSetHardFail:
    def test_disjoint_sets_raise_naming_both_sides(self, tmp_path: Path) -> None:
        t, l = _run(tmp_path, [_trainer_row("A"), _trainer_row("B")],
                    [_life_row("B", [_arch("mlp")]), _life_row("C", [_arch("mlp")])])
        with pytest.raises(ValueError) as ei:
            analyse_v05_run(t, l)
        msg = str(ei.value)
        assert "task sets differ" in msg
        assert "only-trainer=['A']" in msg
        assert "only-lifecycle=['C']" in msg

    def test_check_happens_before_any_computation(self, tmp_path: Path, monkeypatch) -> None:
        import perturb_eval.experiments.e_v05_real_traces as mod

        def _boom(*a, **k):
            raise AssertionError("computation ran before task-set check")

        monkeypatch.setattr(mod, "per_agent_field_entropy", _boom)
        monkeypatch.setattr(mod, "best_config_per_task", _boom)
        t, l = _run(tmp_path, [_trainer_row("A")], [_life_row("C", [_arch("mlp")])])
        with pytest.raises(ValueError, match="task sets differ"):
            analyse_v05_run(t, l)

    def test_equal_sets_report_counts(self, tmp_path: Path) -> None:
        t, l = _run(
            tmp_path,
            [_trainer_row("T0"), _trainer_row("T0", 0.3), _trainer_row("T1")],
            [_life_row("T0", [_arch("mlp")]), _life_row("T0", [_arch("mlp")]),
             _life_row("T1", [_arch("linear")])],
            tprov=_prov(), lprov=_prov(),
        )
        s = analyse_v05_run(t, l)
        assert s["n_tasks_trainer"] == s["n_tasks_lifecycle"] == 2
        assert s["n_lifecycle_runs"] == 3
        assert s["n_lifecycle_runs_unique_tasks"] == 2
        assert s["status"] == "ok"
        assert s["run_id"] == "run-abc" and s["git_sha"] == "deadbeef"

    def test_run_id_mismatch_raises(self, tmp_path: Path) -> None:
        t, l = _run(tmp_path, [_trainer_row("T0")], [_life_row("T0", [_arch("mlp")])],
                    tprov=_prov(run_id="r1"), lprov=_prov(run_id="r2"))
        with pytest.raises(ValueError, match=r"run_id.*r1.*r2"):
            analyse_v05_run(t, l)

    def test_git_sha_mismatch_raises(self, tmp_path: Path) -> None:
        t, l = _run(tmp_path, [_trainer_row("T0")], [_life_row("T0", [_arch("mlp")])],
                    tprov=_prov(git_sha="aaa"), lprov=_prov(git_sha="bbb"))
        with pytest.raises(ValueError, match=r"git_sha.*aaa.*bbb"):
            analyse_v05_run(t, l)

    def test_provenance_in_only_one_file_raises(self, tmp_path: Path) -> None:
        t, l = _run(tmp_path, [_trainer_row("T0")], [_life_row("T0", [_arch("mlp")])],
                    tprov=_prov())
        with pytest.raises(ValueError, match="provenance record present in only one"):
            analyse_v05_run(t, l)

    def test_main_does_not_write_summary_on_failure(self, tmp_path: Path) -> None:
        t, l = _run(tmp_path, [_trainer_row("A")], [_life_row("C", [_arch("mlp")])])
        out = tmp_path / "summary.json"
        with pytest.raises(ValueError):
            main(t, l, out)
        assert not out.exists()

    def test_committed_v050_artifacts_raise(self, tmp_path: Path) -> None:
        """REGRESSION: the committed v0.5.0 JSONLs share only 2 of 36 tasks."""
        t = V050 / "trainer_runs.jsonl"
        l = V050 / "lifecycle_runs.jsonl"
        assert t.exists() and l.exists()
        out = tmp_path / "summary.json"
        with pytest.raises(ValueError, match="task sets differ") as ei:
            main(t, l, out)
        print("v0.5.0 regression error:", ei.value)
        assert not out.exists()


# ---------------------------------------------------------------- T16 entropy
class TestLlmOnlyEntropy:
    def test_mixed_sources_entropy_over_llm_only(self, tmp_path: Path) -> None:
        steps_by_task = {
            "T0": [_arch("linear"), _arch("scgpt_small", "mock")],
            "T1": [_arch("mlp"), _arch("scgpt_small", "mock")],
            "T2": [_arch("linear"), _arch("scgpt_small", None)],
        }
        t, l = _run(tmp_path, [_trainer_row(k) for k in steps_by_task],
                    [_life_row(k, v) for k, v in steps_by_task.items()],
                    tprov=_prov(), lprov=_prov())
        s = analyse_v05_run(t, l)
        expected = -(2 / 3 * math.log(2 / 3) + 1 / 3 * math.log(1 / 3))
        assert s["architect_backbone_entropy_nats"] == pytest.approx(expected)
        assert s["architect_backbone_distribution"] == {"linear": 2, "mlp": 1}
        assert s["architect_hvg_entropy_nats"] == pytest.approx(0.0)
        assert s["entropy_by_role"]["Architect"] == pytest.approx(expected)
        assert s["n_steps_llm"] == 3
        assert s["n_steps_mock"] == 2
        assert s["n_steps_unknown"] == 1
        assert s["n_steps_fallback"] == 0

    def test_entropy_by_role_has_all_five_roles_null_when_no_llm(self, tmp_path: Path) -> None:
        t, l = _run(tmp_path, [_trainer_row("T0")], [_life_row("T0", [_arch("mlp")])],
                    tprov=_prov(), lprov=_prov())
        s = analyse_v05_run(t, l)
        assert set(s["entropy_by_role"]) == set(ROLES)
        assert len(ROLES) == 5
        for role in ROLES:
            if role != "Architect":
                assert s["entropy_by_role"][role] is None
        assert s["entropy_by_role"]["Architect"] == pytest.approx(0.0)

    def test_legacy_steps_without_source_never_counted_as_llm(self, tmp_path: Path) -> None:
        t, l = _run(tmp_path, [_trainer_row("T0")],
                    [_life_row("T0", [_arch("mlp", None), _arch("linear", None)])])
        s = analyse_v05_run(t, l)
        assert s["n_steps_unknown"] == 2
        assert s["n_steps_llm"] == 0
        assert s["architect_backbone_entropy_nats"] is None
        assert s["architect_hvg_entropy_nats"] is None
        assert s["architect_backbone_distribution"] == {}
        assert s["gate_architect_entropy_above_0_5_nats"] is False

    def test_all_fallback_diagnostic_entropy_null(self, tmp_path: Path) -> None:
        t, l = _run(tmp_path, [_trainer_row("T0")],
                    [_life_row("T0", [_arch("mlp", "fallback"), _arch("linear", "fallback")])],
                    tprov=_prov(), lprov=_prov())
        s = analyse_v05_run(t, l, allow_fallback_for_diagnosis=True)
        assert s["n_steps_fallback"] == 2
        assert s["architect_backbone_entropy_nats"] is None
        assert all(v is None for v in s["entropy_by_role"].values())


# ---------------------------------------------------------------- C-KEY-2
class TestFallbackRefusal:
    def test_fallback_step_refuses(self, tmp_path: Path) -> None:
        t, l = _run(tmp_path, [_trainer_row("T0")],
                    [_life_row("T0", [_arch("mlp"), _arch("linear", "fallback")])],
                    tprov=_prov(), lprov=_prov())
        with pytest.raises(ValueError, match=r"run FAILED: 1 fallback steps"):
            analyse_v05_run(t, l)

    def test_fallback_step_refuses_even_for_legacy(self, tmp_path: Path) -> None:
        t, l = _run(tmp_path, [_trainer_row("T0")],
                    [_life_row("T0", [_arch("linear", "fallback")])])
        with pytest.raises(ValueError, match="run FAILED"):
            analyse_v05_run(t, l)

    def test_status_failed_fallback_refuses(self, tmp_path: Path) -> None:
        t, l = _run(tmp_path, [_trainer_row("T0")], [_life_row("T0", [_arch("mlp")])],
                    tprov=_prov(), lprov=_prov(status="failed_fallback"))
        with pytest.raises(ValueError, match=r"run FAILED: 0 fallback steps.*failed_fallback"):
            analyse_v05_run(t, l)

    def test_diagnostic_hatch_marks_status(self, tmp_path: Path) -> None:
        t, l = _run(tmp_path, [_trainer_row("T0")],
                    [_life_row("T0", [_arch("mlp"), _arch("linear", "fallback")])],
                    tprov=_prov(status="failed_fallback"), lprov=_prov(status="failed_fallback"))
        s = analyse_v05_run(t, l, allow_fallback_for_diagnosis=True)
        assert s["status"] == "FAILED_FALLBACK_DIAGNOSTIC_ONLY"
        assert s["n_steps_fallback"] == 1
        assert s["architect_backbone_entropy_nats"] == pytest.approx(0.0)
        # Gates are never licensed by a diagnostic summary.
        for k in ("gate_adamson_median_below_0_20", "gate_norman_median_below_0_30",
                  "gate_architect_entropy_above_0_5_nats"):
            assert s[k] is None


# ---------------------------------------------------------------- partial runs
class TestPartialRefusal:
    @pytest.mark.parametrize("over", [{"status": "partial"}, {"finished_at": None},
                                      {"status": "running"}])
    def test_partial_or_unfinished_refuses(self, tmp_path: Path, over) -> None:
        prov = _prov(**over)
        if over.get("finished_at", 1) is None:
            del prov["finished_at"]
        t, l = _run(tmp_path, [_trainer_row("T0")], [_life_row("T0", [_arch("mlp")])],
                    tprov=prov, lprov=prov)
        with pytest.raises(ValueError, match="partial"):
            analyse_v05_run(t, l)

    def test_allow_partial_marks_status(self, tmp_path: Path) -> None:
        prov = _prov(status="partial")
        t, l = _run(tmp_path, [_trainer_row("T0")], [_life_row("T0", [_arch("mlp")])],
                    tprov=prov, lprov=prov)
        s = analyse_v05_run(t, l, allow_partial=True)
        assert s["status"] == "PARTIAL_DIAGNOSTIC_ONLY"
        assert s["gate_architect_entropy_above_0_5_nats"] is None

    def test_status_failed_refuses_without_hatch(self, tmp_path: Path) -> None:
        prov = _prov(status="failed")
        t, l = _run(tmp_path, [_trainer_row("T0")], [_life_row("T0", [_arch("mlp")])],
                    tprov=prov, lprov=prov)
        with pytest.raises(ValueError, match="status='failed'"):
            analyse_v05_run(t, l, allow_partial=True, allow_fallback_for_diagnosis=True)

    def test_finalised_provenance_json_overrides_header(self, tmp_path: Path) -> None:
        """JSONL record 0 is written at start (no finished_at); the finalised
        provenance.json next to the JSONLs carries status + finished_at."""
        header = _prov(status="running")
        del header["finished_at"]
        t, l = _run(tmp_path, [_trainer_row("T0")], [_life_row("T0", [_arch("mlp")])],
                    tprov=header, lprov=header)
        (tmp_path / "provenance.json").write_text(json.dumps(
            {"run_id": "run-abc", "git_sha": "deadbeef", "status": "ok", "finished_at": 9.0}))
        assert analyse_v05_run(t, l)["status"] == "ok"

    def test_finalised_provenance_json_run_id_mismatch(self, tmp_path: Path) -> None:
        t, l = _run(tmp_path, [_trainer_row("T0")], [_life_row("T0", [_arch("mlp")])],
                    tprov=_prov(), lprov=_prov())
        (tmp_path / "provenance.json").write_text(json.dumps(
            {"run_id": "other", "git_sha": "deadbeef", "status": "ok", "finished_at": 9.0}))
        with pytest.raises(ValueError, match="provenance.json"):
            analyse_v05_run(t, l)
