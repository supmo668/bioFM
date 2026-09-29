"""Amendment 2 analyser contracts (paper/PREREGISTRATION.md, "Amendment 2").

* A2-8 (QG-1): a REPLAY -- any LLM step served from the cache, a non-empty
  version-namespaced cache at sweep start, a provenance ``replay`` flag, or a
  provenance ``prereg_version`` other than the pinned one -- is summarised as
  DIAGNOSTIC-ONLY and never licenses a gate.
* A2-5 (QG-10): the analyser cites the per-task evaluation-gene list beside
  H1/H2 and H4/H5 and checks that the trainer and lifecycle records of a task
  carry the same list; a disagreement is DIAGNOSTIC-ONLY and names the task.

Fixtures are tiny JSONL files written into ``tmp_path``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from perturb_eval.experiments.e_v05_real_traces import analyse_v05_run
from perturb_eval.llm.openrouter_client import PREREG_VERSION

GATES = ("H1", "H2", "H3", "H4", "H5")
GATE_BOOLS = (
    "gate_adamson_median_below_0_20",
    "gate_norman_median_below_0_30",
    "gate_architect_entropy_above_0_5_nats",
)

EVAL_IDX = [3, 1, 2]
EVAL_NAMES = ["G3", "G1", "G2"]


def _prov(**over) -> dict:
    rec = {
        "record_type": "provenance",
        "run_id": "run-abc",
        "git_sha": "deadbeef",
        "tasks": ["T0", "T1"],
        "status": "ok",
        "finished_at": 1234.0,
        "preregistration": {
            "path": "projects/perturb-seq-eval/paper/PREREGISTRATION.md",
            "sha256": "a" * 64,
            "commit": "b" * 40,
        },
        # A2-8: the pinned version and the empty, version-namespaced cache.
        "prereg_version": PREREG_VERSION,
        "llm_cache_namespace": f"/cache/{PREREG_VERSION}",
        "llm_cache_entries_at_start": 0,
    }
    rec.update(over)
    return rec


def _write(path: Path, rows: list[dict]) -> Path:
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    return path


def _eval_fields(idx=EVAL_IDX, names=EVAL_NAMES) -> dict:
    out: dict = {"eval_gene_idx": list(idx), "n_eval_genes": len(idx)}
    if names is not None:
        out["eval_genes"] = list(names)
    return out


def _trainer_row(
    task: str, msd: float = 0.1, dataset: str = "adamson_full", *, eval_fields: dict | None = None
) -> dict:
    row = {
        "dataset": dataset,
        "task": task,
        "backbone": "linear",
        "N": 3,
        "R": 1,
        "seed": 1,
        "msd_topk": msd,
        "wall_sec": 0.1,
        "hvg_n": 2000,
        "hvg_n_forced": 0,
        "hvg_mode": "seurat",
        "n_params": 10,
    }
    if eval_fields is not None:
        row.update(eval_fields)
    return row


def _arch(bb: str, *, cache_hit: bool | None = False, source: str = "llm") -> dict:
    s = {
        "round_index": 0,
        "agent_name": "Architect",
        "proposal_content": {"backbone": bb, "hvg_count": 2000},
        "model_id": "m/x" if source == "llm" else None,
        "source": source,
        "backbone_stated": bb,
    }
    if cache_hit is not None:
        s["cache_hit"] = cache_hit
    return s


def _life_row(
    task: str,
    steps: list[dict],
    msd: float = 0.2,
    dataset: str = "adamson_full",
    *,
    eval_fields: dict | None = None,
) -> dict:
    row = {"dataset": dataset, "task_id": task, "seed": 1, "final_msd_topk": msd, "steps": steps}
    if eval_fields is not None:
        row.update(eval_fields)
    return row


def _files(
    tmp_path: Path,
    trainer_rows: list[dict],
    life_rows: list[dict],
    *,
    prov: dict | None,
) -> tuple[Path, Path]:
    head = [prov] if prov is not None else []
    return (
        _write(tmp_path / "trainer_runs.jsonl", head + trainer_rows),
        _write(tmp_path / "lifecycle_runs.jsonl", head + life_rows),
    )


def _clean(tmp_path: Path, *, prov: dict | None = None, steps=None) -> tuple[Path, Path]:
    steps = steps if steps is not None else [_arch("mlp")]
    ef = _eval_fields()
    return _files(
        tmp_path,
        [_trainer_row("T0", eval_fields=ef)],
        [_life_row("T0", steps, eval_fields=ef)],
        prov=prov if prov is not None else _prov(),
    )


def _assert_not_licensed(summary: dict) -> None:
    assert summary["status"] != "ok"
    for k in GATE_BOOLS:
        assert summary[k] is None, k
    for g in GATES:
        res = summary["preregistered"][g]
        assert res["pass"] is None, g
        assert res["evaluable"] is False, g


# ---------------------------------------------------------------- A2-8 / QG-1
class TestA28ReplayNeverLicensed:
    def test_clean_run_is_ok_and_reports_cache_fields(self, tmp_path: Path) -> None:
        t, l = _clean(tmp_path)
        s = analyse_v05_run(t, l)
        assert s["status"] == "ok"
        assert s["replay"] is False
        assert s["replay_reasons"] == []
        assert s["prereg_version"] == PREREG_VERSION
        assert s["llm_cache_entries_at_start"] == 0
        assert s["llm_cache_hit_count"] == 0
        assert s["gate_architect_entropy_above_0_5_nats"] is not None

    def test_cache_hit_step_is_replay(self, tmp_path: Path) -> None:
        t, l = _clean(tmp_path, steps=[_arch("mlp"), _arch("linear", cache_hit=True)])
        s = analyse_v05_run(t, l)
        assert s["status"] == "REPLAY_DIAGNOSTIC_ONLY"
        assert s["replay"] is True
        assert s["llm_cache_hit_count"] == 1
        assert any("cache" in r for r in s["replay_reasons"])
        _assert_not_licensed(s)

    def test_cache_hit_on_non_llm_step_does_not_count(self, tmp_path: Path) -> None:
        # Only LLM-sourced steps can be served from the LLM cache.
        t, l = _clean(
            tmp_path, steps=[_arch("mlp"), _arch("linear", cache_hit=True, source="mock")]
        )
        s = analyse_v05_run(t, l)
        assert s["llm_cache_hit_count"] == 0
        assert s["replay"] is False
        assert s["status"] == "ok"

    def test_entries_at_start_is_replay(self, tmp_path: Path) -> None:
        t, l = _clean(tmp_path, prov=_prov(llm_cache_entries_at_start=7))
        s = analyse_v05_run(t, l)
        assert s["status"] == "REPLAY_DIAGNOSTIC_ONLY"
        assert s["replay"] is True
        assert s["llm_cache_entries_at_start"] == 7
        assert any("7" in r for r in s["replay_reasons"])
        _assert_not_licensed(s)

    def test_provenance_replay_flag_is_replay(self, tmp_path: Path) -> None:
        t, l = _clean(tmp_path, prov=_prov(replay=True, replay_reasons=["recorded by the sweep"]))
        s = analyse_v05_run(t, l)
        assert s["status"] == "REPLAY_DIAGNOSTIC_ONLY"
        assert s["replay"] is True
        assert "recorded by the sweep" in s["replay_reasons"]
        _assert_not_licensed(s)

    def test_finalised_provenance_json_replay_flag_is_replay(self, tmp_path: Path) -> None:
        # The JSONL headers are written at start; the finalised provenance.json
        # carries llm_cache_hit_count / replay from llm_cache_end.
        t, l = _clean(tmp_path)
        (tmp_path / "provenance.json").write_text(
            json.dumps(
                {
                    "run_id": "run-abc",
                    "git_sha": "deadbeef",
                    "status": "ok",
                    "finished_at": 9.0,
                    "llm_cache_hit_count": 3,
                    "replay": True,
                    "replay_reasons": ["3 LLM step(s) served from the cache (must be 0)"],
                }
            )
        )
        s = analyse_v05_run(t, l)
        assert s["status"] == "REPLAY_DIAGNOSTIC_ONLY"
        assert s["replay"] is True
        _assert_not_licensed(s)

    def test_prereg_version_mismatch_is_diagnostic(self, tmp_path: Path) -> None:
        t, l = _clean(tmp_path, prov=_prov(prereg_version="v0.6.0"))
        s = analyse_v05_run(t, l)
        assert s["status"] == "PREREG_VERSION_MISMATCH_DIAGNOSTIC_ONLY"
        assert s["prereg_version"] == "v0.6.0"
        assert s["replay"] is False
        _assert_not_licensed(s)

    def test_replay_status_from_sweep_provenance_is_not_partial(self, tmp_path: Path) -> None:
        # derive_status may finalise a replay as status="replay": a finished
        # replay is DIAGNOSTIC-ONLY, never refused as partial.
        t, l = _clean(tmp_path, prov=_prov(status="replay", llm_cache_entries_at_start=2))
        s = analyse_v05_run(t, l)
        assert s["status"] == "REPLAY_DIAGNOSTIC_ONLY"
        _assert_not_licensed(s)

    def test_replay_never_hides_behind_partial_hatch(self, tmp_path: Path) -> None:
        t, l = _clean(tmp_path, prov=_prov(status="partial", llm_cache_entries_at_start=2))
        s = analyse_v05_run(t, l, allow_partial="budget stop; diagnostic read")
        assert s["status"] == "PARTIAL_DIAGNOSTIC_ONLY"
        assert s["replay"] is True
        assert s["replay_reasons"]
        _assert_not_licensed(s)

    def test_legacy_run_without_provenance_reports_cache_fields(self, tmp_path: Path) -> None:
        t, l = _files(
            tmp_path,
            [_trainer_row("T0")],
            [_life_row("T0", [_arch("mlp", cache_hit=None)])],
            prov=None,
        )
        s = analyse_v05_run(t, l)
        assert s["status"] == "legacy_no_provenance"
        assert s["prereg_version"] is None
        assert s["llm_cache_entries_at_start"] is None
        assert s["llm_cache_hit_count"] == 0
        assert s["replay"] is False


# ---------------------------------------------------------------- A2-5 / QG-10
class TestA25EvalGenesCited:
    def test_agreement_emits_list_and_stays_ok(self, tmp_path: Path) -> None:
        ef = _eval_fields()
        t, l = _files(
            tmp_path,
            [
                _trainer_row("T0", eval_fields=ef),
                _trainer_row("T0", 0.3, eval_fields=ef) | {"seed": 2},
                _trainer_row(
                    "N0", dataset="norman", eval_fields=_eval_fields([5, 6], ["G5", "G6"])
                ),
            ],
            [
                _life_row("T0", [_arch("mlp")], eval_fields=ef),
                _life_row(
                    "N0",
                    [_arch("linear")],
                    dataset="norman",
                    eval_fields=_eval_fields([5, 6], ["G5", "G6"]),
                ),
            ],
            prov=_prov(),
        )
        s = analyse_v05_run(t, l)
        assert s["status"] == "ok"
        assert s["eval_genes_per_task"] == {
            "adamson_full/T0": EVAL_NAMES,
            "norman/N0": ["G5", "G6"],
        }
        assert s["eval_gene_mismatch_tasks"] == []

    def test_mismatching_task_is_diagnostic_and_named(self, tmp_path: Path) -> None:
        ok = _eval_fields()
        other = _eval_fields([3, 1, 9], ["G3", "G1", "G9"])
        t, l = _files(
            tmp_path,
            [_trainer_row("T0", eval_fields=ok), _trainer_row("T1", eval_fields=ok)],
            [
                _life_row("T0", [_arch("mlp")], eval_fields=ok),
                _life_row("T1", [_arch("mlp")], eval_fields=other),
            ],
            prov=_prov(),
        )
        s = analyse_v05_run(t, l)
        assert s["status"] == "EVAL_GENE_MISMATCH_DIAGNOSTIC_ONLY"
        assert s["eval_gene_mismatch_tasks"] == ["adamson_full/T1"]
        assert "adamson_full/T0" in s["eval_genes_per_task"]
        _assert_not_licensed(s)

    def test_one_path_missing_fields_for_a_task_is_mismatch(self, tmp_path: Path) -> None:
        ok = _eval_fields()
        t, l = _files(
            tmp_path,
            [_trainer_row("T0", eval_fields=ok), _trainer_row("T1", eval_fields=ok)],
            [
                _life_row("T0", [_arch("mlp")], eval_fields=ok),
                _life_row("T1", [_arch("mlp")]),  # no A2-5 fields on this path
            ],
            prov=_prov(),
        )
        s = analyse_v05_run(t, l)
        assert s["status"] == "EVAL_GENE_MISMATCH_DIAGNOSTIC_ONLY"
        assert s["eval_gene_mismatch_tasks"] == ["adamson_full/T1"]
        _assert_not_licensed(s)

    def test_disagreement_within_one_path_is_mismatch(self, tmp_path: Path) -> None:
        ok = _eval_fields()
        other = _eval_fields([3, 1, 9], ["G3", "G1", "G9"])
        t, l = _files(
            tmp_path,
            [_trainer_row("T0", eval_fields=ok), _trainer_row("T0", 0.3, eval_fields=other)],
            [_life_row("T0", [_arch("mlp")], eval_fields=ok)],
            prov=_prov(),
        )
        s = analyse_v05_run(t, l)
        assert s["status"] == "EVAL_GENE_MISMATCH_DIAGNOSTIC_ONLY"
        assert s["eval_gene_mismatch_tasks"] == ["adamson_full/T0"]

    def test_indices_without_names_are_cited_by_index(self, tmp_path: Path) -> None:
        ef = _eval_fields(names=None)
        t, l = _files(
            tmp_path,
            [_trainer_row("T0", eval_fields=ef)],
            [_life_row("T0", [_arch("mlp")], eval_fields=ef)],
            prov=_prov(),
        )
        s = analyse_v05_run(t, l)
        assert s["status"] == "ok"
        assert s["eval_genes_per_task"] == {"adamson_full/T0": EVAL_IDX}

    def test_legacy_rows_without_fields_record_none_with_reason(self, tmp_path: Path) -> None:
        t, l = _files(
            tmp_path,
            [_trainer_row("T0")],
            [_life_row("T0", [_arch("mlp", cache_hit=None)])],
            prov=None,
        )
        s = analyse_v05_run(t, l)
        assert s["status"] == "legacy_no_provenance"
        assert s["eval_genes_per_task"] is None
        assert isinstance(s["eval_genes_reason"], str) and s["eval_genes_reason"]
        assert s["eval_gene_mismatch_tasks"] == []

    def test_pinned_run_without_any_fields_records_none_not_mismatch(self, tmp_path: Path) -> None:
        t, l = _files(
            tmp_path, [_trainer_row("T0")], [_life_row("T0", [_arch("mlp")])], prov=_prov()
        )
        s = analyse_v05_run(t, l)
        assert s["status"] == "ok"
        assert s["eval_genes_per_task"] is None
        assert s["eval_genes_reason"]
        assert s["eval_gene_mismatch_tasks"] == []


@pytest.mark.parametrize("trigger", ["cache_hit", "entries_at_start", "replay_flag", "version"])
def test_every_replay_trigger_withdraws_every_gate(tmp_path: Path, trigger: str) -> None:
    if trigger == "cache_hit":
        t, l = _clean(tmp_path, steps=[_arch("mlp", cache_hit=True)])
    elif trigger == "entries_at_start":
        t, l = _clean(tmp_path, prov=_prov(llm_cache_entries_at_start=1))
    elif trigger == "replay_flag":
        t, l = _clean(tmp_path, prov=_prov(replay=True))
    else:
        t, l = _clean(tmp_path, prov=_prov(prereg_version="v0.5.0"))
    s = analyse_v05_run(t, l)
    assert s["status"] in ("REPLAY_DIAGNOSTIC_ONLY", "PREREG_VERSION_MISMATCH_DIAGNOSTIC_ONLY")
    _assert_not_licensed(s)


class TestServedModelMismatch:
    """A4-1: a served model that differs from the requested one is a fallback-class event; the
    analyser must not license a run whose provenance records one (whatever the client did)."""

    def test_report_count_is_diagnostic_only(self, tmp_path: Path) -> None:
        t, l = _clean(tmp_path, prov=_prov(llm_report={"served_mismatch_count": 1}))
        s = analyse_v05_run(t, l)
        assert s["status"] == "SERVED_MODEL_MISMATCH_DIAGNOSTIC_ONLY"
        assert s["served_mismatch_count"] == 1
        _assert_not_licensed(s)

    def test_call_log_row_is_diagnostic_only(self, tmp_path: Path) -> None:
        log = [
            {
                "role": "Trainer",
                "requested_model": "a",
                "served_model": "b",
                "served_equals_requested": False,
            }
        ]
        t, l = _clean(tmp_path, prov=_prov(llm_call_log=log))
        s = analyse_v05_run(t, l)
        assert s["status"] == "SERVED_MODEL_MISMATCH_DIAGNOSTIC_ONLY"
        assert s["served_mismatch_count"] == 1
        _assert_not_licensed(s)

    def test_zero_mismatches_stay_ok(self, tmp_path: Path) -> None:
        t, l = _clean(tmp_path, prov=_prov(llm_report={"served_mismatch_count": 0}))
        s = analyse_v05_run(t, l)
        assert s["status"] == "ok" and s["served_mismatch_count"] == 0
