"""Bug-exposing tests for the accepted P0-P5 quality-gate findings.

One class per finding ID (C4, C5, C6, C9, C10/C18, C12, C14, C15, C16, C22,
C23/C24, C27, OWN-1). Each was written before its fix and run RED against the
pre-fix tree (``workstreams/perturb-seq-eval/qgr/evidence/qg-p0p5-red.txt``).
None of them changes what the pre-registered experiment measures.
"""

from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from perturb_eval.agentic_lifecycle.loop import MockAgentPool, run_agentic_lifecycle
from perturb_eval.experiments import preregistered as pr


PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_V05 = PROJECT_ROOT / "scripts" / "modal" / "app_v05.py"
PREREG_PIN = {
    "path": "projects/perturb-seq-eval/paper/PREREGISTRATION.md",
    "sha256": "a" * 64,
    "commit": "0c2932a" + "0" * 33,
}
EXACT_COMMAND = (
    "LLM_KEY_SOURCE=infisical:syntropyhealth-app:dev infisical run "
    "--projectId <INFISICAL_PROJECT_ID> --env dev -- modal run "
    "scripts/modal/app_v05.py::entrypoint --version v0.6.0 --norman-n-singletons 15 "
    "--norman-n-doublets 5 --seeds 3"
)


def _full_liveness(env):  # CTO #467: preflight now probes EVERY roster model
    from perturb_eval.llm.anthropic_client import ANTHROPIC_POOL

    return {
        m.model_id: {"live": True, "verdict": "ok", "probed_at": "2026-09-28T23:00:00+00:00"}
        for m in ANTHROPIC_POOL.models
    }


def _matrix():
    """Controls + four knockdowns, each lowering its own column."""
    rng = np.random.default_rng(7)
    n_per, n_cols = 40, 60
    names = ["CTRL", "A", "B", "C", "D"]
    X = rng.standard_normal((n_per * len(names), n_cols)) * 0.3 + 2.0
    labels = np.repeat(np.asarray(names), n_per)
    tgi = {"A": 5, "B": 10, "C": 15, "D": 20}
    for p, g in tgi.items():
        X[labels == p, g] -= 2.0
    return X, labels, labels == "CTRL", tgi


def _ds() -> dict:
    X, labels, ctrl, tgi = _matrix()
    return {"X": X, "labels": labels, "control_mask": ctrl, "target_gene_idx": tgi}


def _lifecycle(pool=None, **over):
    X, labels, ctrl, tgi = _matrix()
    kw = dict(
        task_id="hold_D",
        X=X,
        labels=labels,
        control_mask=ctrl,
        target_gene_idx=tgi,
        held_out="D",
        agent_pool=pool or MockAgentPool(seed=0),
        max_rounds=1,
        seed=2026,
        dataset="adamson_full",
    )
    kw.update(over)
    return run_agentic_lifecycle(**kw)


def _app_fn(name: str) -> ast.FunctionDef:
    tree = ast.parse(APP_V05.read_text())
    return next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)


def _called_names(fn: ast.AST) -> set[str]:
    return {
        c.func.id for c in ast.walk(fn) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
    }


# ---------------------------------------------------------------- C4
class TestC4TrainerErrorTaxonomy:
    """trainer_exec had a bare ``except Exception``: a programming error became a
    silent ``final_msd=inf`` record the analyser did not flag."""

    def _patch_fit(self, monkeypatch, exc: BaseException) -> None:
        from perturb_eval.backbones.linear import LinearBackbone

        def boom(self, *a, **k):
            raise exc

        monkeypatch.setattr(LinearBackbone, "fit", boom)

    def test_type_error_propagates(self, monkeypatch) -> None:
        self._patch_fit(monkeypatch, TypeError("bad arg"))
        with pytest.raises(TypeError, match="bad arg"):
            _lifecycle(backbone_override="linear")

    def test_backbone_unavailable_propagates(self, monkeypatch) -> None:
        from perturb_eval.agentic_lifecycle.architect_dispatch import BackboneUnavailableError

        self._patch_fit(monkeypatch, BackboneUnavailableError("scgpt_small unavailable"))
        with pytest.raises(BackboneUnavailableError):
            _lifecycle(backbone_override="linear")

    def test_memory_error_gives_flagged_error_record(self, monkeypatch) -> None:
        from perturb_eval.experiments.e_v05_real_traces import _is_error_record
        from perturb_eval.experiments.v05_sweep import lifecycle_record

        self._patch_fit(monkeypatch, MemoryError("host RAM"))
        rec = lifecycle_record(
            task="D",
            dataset_name="adamson_full",
            ds=_ds(),
            seed=1,
            pool=MockAgentPool(seed=0),  # A2-2: fixed 3 rounds
            backbone_override="linear",
        )
        assert _is_error_record(rec)
        assert rec["error_class"] == "transient"
        assert rec["error_type"] == "builtins.MemoryError"
        assert "MemoryError" in rec["traceback"]
        assert rec["error"].startswith("MemoryError")
        trainer = [s for s in rec["steps"] if s["agent_name"] == "Trainer"]
        assert trainer and trainer[0]["succeeded"] is False
        assert rec["final_msd_topk"] == float("inf")

    def test_clean_run_record_is_not_an_error_record(self) -> None:
        from perturb_eval.experiments.e_v05_real_traces import _is_error_record
        from perturb_eval.experiments.v05_sweep import lifecycle_record

        rec = lifecycle_record(
            task="D", dataset_name="adamson_full", ds=_ds(), seed=1, pool=MockAgentPool(seed=0)
        )  # A2-2: fixed 3 rounds
        assert not _is_error_record(rec)


# ---------------------------------------------------------------- C15
class _TwoBackbonePool(MockAgentPool):
    def propose(self, role, round_index, task_id, context, *, seed, dataset):
        out = super().propose(role, round_index, task_id, context, seed=seed, dataset=dataset)
        if role == "Architect":
            out = {**out, "content": {"backbone": "mlp" if round_index == 0 else "linear"}}
        return out


class TestC15ParamsPerRound:
    def test_backbone_and_params_recorded_per_round(self) -> None:
        run = _lifecycle(_TwoBackbonePool(seed=0), max_rounds=2, validator_threshold_override=-1.0)
        assert [b for b, _ in run.n_params_per_round] == ["mlp", "linear"]
        assert all(isinstance(n, int) and n > 0 for _, n in run.n_params_per_round)
        assert run.n_params == run.n_params_per_round[-1][1]
        assert run.backbone_used == "linear"

    def test_n_params_reset_when_last_round_fails(self, monkeypatch) -> None:
        from perturb_eval.backbones.linear import LinearBackbone

        def oom(self, *a, **k):
            raise MemoryError("oom")

        monkeypatch.setattr(LinearBackbone, "fit", oom)
        run = _lifecycle(_TwoBackbonePool(seed=0), max_rounds=2, validator_threshold_override=-1.0)
        assert run.n_params_per_round[0][0] == "mlp" and run.n_params_per_round[0][1] > 0
        assert run.n_params_per_round[1] == ("linear", None)
        # Round 0's mlp count is NOT filed under round 1's linear backbone.
        assert run.n_params is None

    def test_collect_params_uses_per_round_pairs(self) -> None:
        from perturb_eval.experiments.provenance import collect_hvg_and_params

        _, params = collect_hvg_and_params(
            [],
            [
                {
                    "dataset": "norman",
                    "task_id": "B",
                    "backbone_used": "linear",
                    "n_params": None,
                    "n_params_per_round": [["mlp", 42], ["linear", None]],
                }
            ],
        )
        assert params["norman:B"]["lifecycle"] == {"mlp": [42]}


# ---------------------------------------------------------------- C6
class TestC6CacheKeyAndFlag:
    BASE = dict(
        task_id="SNAI1", round_index=0, role="Architect", prompt="p", model_id="m/x:free", seed=2026
    )

    def test_dataset_is_in_the_cache_key(self) -> None:
        from perturb_eval.llm.openrouter_client import _cache_key

        a = _cache_key(**self.BASE, dataset="adamson_full")
        b = _cache_key(**self.BASE, dataset="norman")
        assert a != b

    def test_dataset_is_required(self) -> None:
        from perturb_eval.llm.openrouter_client import _cache_key

        with pytest.raises(TypeError):
            _cache_key(**self.BASE)  # type: ignore[call-arg]

    def _resp(self, content: str) -> MagicMock:
        r = MagicMock()
        r.status_code = 200
        r.json.return_value = {"choices": [{"message": {"content": content}}]}
        return r

    def test_chat_result_flags_cache_hit(self, tmp_path: Path) -> None:
        from perturb_eval.llm.openrouter_client import OpenRouterClient

        kw = dict(role="Validator", task_id="SNAI1", round_index=0, prompt="p", seed=0)
        c1 = OpenRouterClient(api_key="test", cache_dir=tmp_path)
        with patch.object(c1._session, "post", return_value=self._resp('{"ok": 1}')):
            fresh = c1.chat_json(**kw, dataset="adamson_full")
        assert fresh.cache_hit is False
        c2 = OpenRouterClient(api_key="test", cache_dir=tmp_path)
        with patch.object(c2._session, "post", side_effect=AssertionError("network")):
            hit = c2.chat_json(**kw, dataset="adamson_full")
        assert hit.cache_hit is True and hit.content == fresh.content
        # Same task/prompt/seed/model in the OTHER dataset is not a cache hit.
        c3 = OpenRouterClient(api_key="test", cache_dir=tmp_path)
        with patch.object(c3._session, "post", return_value=self._resp('{"ok": 2}')) as post:
            other = c3.chat_json(**kw, dataset="norman")
        assert post.called and other.cache_hit is False and other.content == {"ok": 2}

    def test_pool_threads_dataset_and_flags_cache_hit(self, tmp_path: Path) -> None:
        from perturb_eval.agentic_lifecycle.llm_agent_pool import LLMAgentPool
        from perturb_eval.llm.openrouter_client import ChatResult

        seen: list[dict] = []

        class _Client:
            def chat_json(self, **kw):
                seen.append(kw)
                # A2-1: a stated confidence, so the reply is an llm step.
                return ChatResult(
                    content={"backbone": "mlp", "confidence": 0.5},
                    model_id="m/x:free",
                    cache_hit=True,
                )

        pool = LLMAgentPool(client=_Client(), cache_dir=tmp_path)
        out = pool.propose("Architect", 0, "SNAI1", {}, seed=1, dataset="norman")
        assert seen[0]["dataset"] == "norman"
        assert out["cache_hit"] is True

    def test_loop_passes_dataset_and_records_cache_hit_on_step(self) -> None:
        seen: set[str] = set()

        class _Pool(MockAgentPool):
            def propose(self, role, round_index, task_id, context, *, seed, dataset):
                seen.add(dataset)
                out = super().propose(
                    role, round_index, task_id, context, seed=seed, dataset=dataset
                )
                return {**out, "source": "llm", "model_id": "m/x:free", "cache_hit": True}

        run = _lifecycle(_Pool(seed=0), dataset="norman")
        assert seen == {"norman"}
        assert run.steps and all(s.cache_hit is True for s in run.steps)

    def test_mock_steps_have_no_cache_flag(self) -> None:
        run = _lifecycle()
        assert all(s.cache_hit is None for s in run.steps)

    def test_run_requires_dataset(self) -> None:
        X, labels, ctrl, tgi = _matrix()
        with pytest.raises(TypeError):
            run_agentic_lifecycle(
                task_id="t",
                X=X,
                labels=labels,
                control_mask=ctrl,  # type: ignore[call-arg]
                target_gene_idx=tgi,
                held_out="D",
                agent_pool=MockAgentPool(seed=0),
                max_rounds=1,
                seed=1,
            )

    def test_provenance_records_cache_dir(self) -> None:
        prov = _build_prov(llm_cache_dir="/biofm_cache/llm")
        assert prov["llm_cache_dir"] == "/biofm_cache/llm"
        call = next(
            c
            for c in ast.walk(_app_fn("run_v05_sweep"))
            if isinstance(c, ast.Call)
            and isinstance(c.func, ast.Name)
            and c.func.id == "build_provenance"
        )
        assert "llm_cache_dir" in {k.arg for k in call.keywords}


def _build_prov(**over) -> dict:
    from perturb_eval.experiments import heldout
    from perturb_eval.experiments import provenance as pv
    from perturb_eval.experiments.v05_tasks import TaskPlan

    kw = dict(
        run_id="r",
        git_sha="a" * 40,
        git_dirty=False,
        entrypoint_kwargs={k: 1 for k in pv.REQUIRED_ENTRYPOINT_KWARGS},
        datasets=[],
        task_plan=TaskPlan(adamson=("A",), norman_singletons=(), norman_doublets=()),
        tasks_excluded=[],
        llm_pool=[],
        gpu="A100-40GB",
        hourly_usd=1.32,
        budget_cap_usd=28.0,
        # A2-4: the trainer grid is a required provenance block.
        trainer_grid=heldout.trainer_grid(backbones=("linear",), r_sweep=(1,), seeds=(0,)),
    )
    kw.update(over)
    return pv.build_provenance(**kw)


# ---------------------------------------------------------------- C9
class TestC9ScgptDevice:
    def _fit(self):
        from perturb_eval.backbones import BackboneTrainConfig
        from perturb_eval.backbones.scgpt_small import SCGPTSmallBackbone

        X, labels, ctrl, tgi = _matrix()
        bb = SCGPTSmallBackbone()
        art = bb.fit(X, labels.tolist(), ctrl, tgi, BackboneTrainConfig(max_iter=1, seed=0))
        return bb, art

    def test_cpu_device_recorded(self) -> None:
        pytest.importorskip("torch")
        from perturb_eval.backbones.scgpt_small import training_device

        assert training_device() == "cpu"
        bb, art = self._fit()
        assert art.extra["device"] == "cpu"
        assert bb.predict_logfc("D", (20, 5), n_genes=60).shape == (60,)

    def test_cuda_available_moves_model_and_tensors(self, monkeypatch) -> None:
        torch = pytest.importorskip("torch")
        module_to: list = []
        tensor_to: list = []

        def mod_to(self, *a, **k):
            module_to.append(a[0] if a else k.get("device"))
            return self

        def ten_to(self, *a, **k):
            tensor_to.append(a[0] if a else k.get("device"))
            return self

        monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
        monkeypatch.setattr(torch.nn.Module, "to", mod_to)
        monkeypatch.setattr(torch.Tensor, "to", ten_to)
        _, art = self._fit()
        assert "cuda" in module_to
        assert "cuda" in tensor_to
        assert art.extra["device"] == "cuda"

    def test_provenance_records_device(self) -> None:
        assert _build_prov(device="cpu")["device"] == "cpu"
        call = next(
            c
            for c in ast.walk(_app_fn("run_v05_sweep"))
            if isinstance(c, ast.Call)
            and isinstance(c.func, ast.Name)
            and c.func.id == "build_provenance"
        )
        assert "device" in {k.arg for k in call.keywords}


# ---------------------------------------------------------------- C5 / C27 task key
def _prov_rec(**over) -> dict:
    rec = {
        "record_type": "provenance",
        "run_id": "run-abc",
        "git_sha": "deadbeef",
        "status": "ok",
        "finished_at": 1.0,
        "preregistration": dict(PREREG_PIN),
    }
    rec.update(over)
    return rec


def _write(path: Path, rows: list[dict]) -> Path:
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    return path


def _trow(task: str, dataset: str, msd: float) -> dict:
    return {
        "dataset": dataset,
        "task": task,
        "backbone": "linear",
        "N": 3,
        "R": 1,
        "seed": 1,
        "msd_topk": msd,
    }


def _llm_step(role: str, r: int, conf: float, content: dict | None = None) -> dict:
    return {
        "round_index": r,
        "agent_name": role,
        "proposal_content": content or {},
        "llm_confidence": conf,
        "source": "llm",
        "model_id": "m/x:free",
    }


def _lrow(task: str, dataset: str, msd: float, spread: float = 0.1) -> dict:
    steps = []
    roles = ("DataCurator", "Literature", "Architect", "Trainer", "Validator")
    for r in (0, 1):
        for i, role in enumerate(roles):
            content = (
                {"backbone": ("linear", "mlp", "scgpt_small")[i % 3]} if role == "Architect" else {}
            )
            steps.append(_llm_step(role, r, 0.3 + (r + 1) * spread * i / 4, content))
    return {
        "dataset": dataset,
        "task_id": task,
        "seed": 1,
        "final_msd_topk": msd,
        "n_rounds": 2,
        "steps": steps,
    }


def _files(tmp_path: Path, trows, lrows, tprov=None, lprov=None):
    t = _write(tmp_path / "trainer_runs.jsonl", ([tprov] if tprov else []) + trows)
    lf = _write(tmp_path / "lifecycle_runs.jsonl", ([lprov] if lprov else []) + lrows)
    return t, lf


class TestC5DatasetTaskKey:
    def test_snai1_in_both_datasets_counts_once_each(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.e_v05_real_traces import analyse_v05_run

        trows = [
            _trow("SNAI1", "adamson_full", 0.10),
            _trow("SNAI1", "norman", 0.90),
            _trow("A2", "adamson_full", 0.12),
            _trow("N2", "norman", 0.8),
        ]
        lrows = [_lrow(t["task"], t["dataset"], 0.5) for t in trows]
        t, lf = _files(tmp_path, trows, lrows, _prov_rec(), _prov_rec())
        s = analyse_v05_run(t, lf)
        best = s["best_config_per_task"]
        assert best["adamson_full:SNAI1"]["best_msd"] == pytest.approx(0.10)
        assert best["norman:SNAI1"]["best_msd"] == pytest.approx(0.90)
        assert s["preregistered"]["H1"]["n"] == 2
        assert s["preregistered"]["H2"]["n"] == 2
        assert s["median_msd_norman"] == pytest.approx(0.85)
        assert s["n_tasks_trainer"] == s["n_tasks_lifecycle"] == 4

    def test_same_task_name_in_different_datasets_raises(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.e_v05_real_traces import analyse_v05_run

        t, lf = _files(
            tmp_path,
            [_trow("SNAI1", "adamson_full", 0.1)],
            [_lrow("SNAI1", "norman", 0.5)],
            _prov_rec(),
            _prov_rec(),
        )
        with pytest.raises(ValueError, match="task sets differ"):
            analyse_v05_run(t, lf)

    def test_one_task_key_helper(self) -> None:
        import perturb_eval.experiments.e_v05_real_traces as mod

        assert pr.task_key({"dataset": "norman", "task": "SNAI1"}) == ("norman", "SNAI1")
        assert pr.task_key({"dataset": "norman", "task_id": "SNAI1"}) == ("norman", "SNAI1")
        assert not hasattr(mod, "_task_key")
        assert mod.task_key is pr.task_key


# ---------------------------------------------------------------- C10 / C18
def _multi_task(tmp_path: Path, tprov=None, lprov=None):
    trows, lrows = [], []
    for ds in ("adamson_full", "norman"):
        for i in range(5):
            name = f"{ds[:1].upper()}{i}"
            trows.append(_trow(name, ds, 0.05 + 0.01 * i))
            lrows.append(_lrow(name, ds, 0.1 + 0.1 * i, spread=0.05 + 0.1 * i))
    return _files(tmp_path, trows, lrows, tprov, lprov)


class TestC10C18PinAndDiagnostic:
    GATES = ("H1", "H2", "H3", "H4", "H5")

    def _analyse(self, *a, **k):
        from perturb_eval.experiments.e_v05_real_traces import analyse_v05_run

        return analyse_v05_run(*a, **k)

    def test_pinned_fixture_is_evaluable(self, tmp_path: Path) -> None:
        s = self._analyse(*_multi_task(tmp_path, _prov_rec(), _prov_rec()))
        assert s["status"] == "ok"
        assert s["preregistered"]["H1"]["pass"] is not None
        assert s["preregistered"]["H4"]["pass"] is not None

    def _assert_withdrawn(self, s: dict) -> None:
        for g in self.GATES:
            assert s["preregistered"][g]["pass"] is None, g
        assert s["preregistered"]["tally"]["UNEVALUATED"] == 5
        assert s["preregistered"]["tally"]["PASS"] == s["preregistered"]["tally"]["FAIL"] == 0

    def test_unpinned_run_is_diagnostic(self, tmp_path: Path) -> None:
        p = _prov_rec()
        del p["preregistration"]
        s = self._analyse(*_multi_task(tmp_path, p, p))
        assert s["status"] == "UNPINNED"
        self._assert_withdrawn(s)

    def test_null_pin_is_unpinned(self, tmp_path: Path) -> None:
        p = _prov_rec(preregistration=None)
        s = self._analyse(*_multi_task(tmp_path, p, p))
        assert s["status"] == "UNPINNED"
        self._assert_withdrawn(s)

    def test_pins_differ_raise(self, tmp_path: Path) -> None:
        other = dict(PREREG_PIN, commit="f" * 40)
        with pytest.raises(ValueError, match="preregistration pin differs"):
            self._analyse(*_multi_task(tmp_path, _prov_rec(), _prov_rec(preregistration=other)))

    def test_legacy_no_provenance_is_diagnostic(self, tmp_path: Path) -> None:
        s = self._analyse(*_multi_task(tmp_path))
        assert s["status"] == "legacy_no_provenance"
        self._assert_withdrawn(s)

    def test_partial_diagnostic_withdraws_all_five(self, tmp_path: Path) -> None:
        p = _prov_rec(status="partial")
        s = self._analyse(*_multi_task(tmp_path, p, p), allow_partial="diagnosis")
        assert s["status"] == "PARTIAL_DIAGNOSTIC_ONLY"
        self._assert_withdrawn(s)

    def test_tally_counts_none_as_unevaluated(self) -> None:
        t = pr.tally(
            {
                "H1": {"pass": True},
                "H2": {"pass": False},
                "H3": {"pass": None},
                "H4": {"pass": None},
                "H5": {"pass": True},
            }
        )
        assert t == {"PASS": 2, "FAIL": 1, "UNEVALUATED": 2, "out_of": 5}


# ---------------------------------------------------------------- C12
class TestC12PreregisteredDesignLocked:
    def _run(self, tmp_path: Path, **kw):
        from perturb_eval.experiments.v05_preflight import preflight
        from perturb_eval.experiments.v05_tasks import TaskPlan

        genes = ("TFA", "CBL")
        ds = {
            "X": np.zeros((2, 2)),
            "labels": np.array(["CTRL", "CTRL"]),
            "control_mask": np.array([True, True]),
            "target_gene_idx": {"TFA": (0,)},
            "perturbations": ("TFA",),
            "gene_names": genes,
        }
        kwargs = {
            "backbones": ("linear",),
            "version": "v0.6.0",
            "doublet_delim": "_",
            "llm_key_source": {"store": "infisical"},
            "preregistration": dict(PREREG_PIN),
            "preregistration_error": None,
        }
        kwargs.update(kw)
        return preflight(
            kwargs=kwargs,
            datasets_spec_or_loaded={"adamson_full": ds},
            task_plan=TaskPlan(adamson=("TFA",), norman_singletons=(), norman_doublets=()),
            env={"ANTHROPIC_API_KEY": "sk-or-test-SENTINEL"},
            out_dir=tmp_path / "o",
            probe_fn=_full_liveness,
        )

    @pytest.mark.parametrize(
        "over", [{"max_tasks_override": 2}, {"include_norman": False}, {"include_adamson": False}]
    )
    def test_preregistered_version_refuses_shrunk_design(self, tmp_path, over) -> None:
        from perturb_eval.experiments.v05_preflight import PreflightError

        with pytest.raises(PreflightError, match=r"41 = 21 \+ 15 \+ 5") as ei:
            self._run(tmp_path, **over)
        assert next(iter(over)) in str(ei.value)

    def test_non_preregistered_version_may_shrink(self, tmp_path) -> None:
        rep = self._run(tmp_path, version="v0.6.0-smoke", max_tasks_override=1)
        assert rep.ok


# ---------------------------------------------------------------- C14 / OWN-1
def _rec(steps, **extra) -> dict:
    return {"dataset": "adamson_full", "task_id": "T", "steps": steps, **extra}


class TestC14StatusAndEntropies:
    def test_fallback_beats_budget(self) -> None:
        from perturb_eval.experiments.v05_sweep import derive_status

        recs = [_rec([{"agent_name": "Architect", "source": "fallback"}])]
        assert derive_status(recs, cost_usd=30.0, kill_usd=28.0) == "failed_fallback"
        assert (
            derive_status(recs, cost_usd=1.0, kill_usd=28.0, stop_reason="spend_stop")
            == "failed_fallback"
        )

    def test_exactly_at_cap_is_ok(self) -> None:
        from perturb_eval.experiments.v05_sweep import derive_status

        assert derive_status([], cost_usd=28.0, kill_usd=28.0) == "ok"
        assert derive_status([], cost_usd=28.0001, kill_usd=28.0) == "partial"

    def test_transient_errors_alone_are_ok(self) -> None:
        from perturb_eval.experiments.v05_sweep import derive_status

        recs = [
            _rec(
                [],
                error="MemoryError: x",
                error_class="transient",
                error_type="builtins.MemoryError",
                traceback="tb",
            )
        ]
        assert derive_status(recs, cost_usd=1.0, kill_usd=28.0) == "ok"

    def test_stop_reason_is_partial(self) -> None:
        from perturb_eval.experiments.v05_sweep import derive_status

        assert (
            derive_status([], cost_usd=12.5, kill_usd=28.0, stop_reason="spend_stop") == "partial"
        )

    def test_entropies_none_without_llm_steps(self) -> None:
        from perturb_eval.experiments.v05_sweep import provenance_entropies

        recs = [
            _rec(
                [
                    {
                        "agent_name": "Architect",
                        "source": "fallback",
                        "proposal_content": {"backbone": "linear", "hvg_count": 500},
                    }
                ]
            )
        ]
        e = provenance_entropies(recs)
        assert e["architect_backbone_entropy_nats"] is None
        assert e["architect_hvg_entropy_nats"] is None
        assert e["architect_backbone_distribution"] == {}
        assert provenance_entropies([])["architect_backbone_entropy_nats"] is None

    def test_entropies_match_the_analyser_llm_only(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.e_v05_real_traces import analyse_v05_run
        from perturb_eval.experiments.v05_sweep import provenance_entropies

        t, lf = _multi_task(tmp_path, _prov_rec(), _prov_rec())
        lrows = [json.loads(x) for x in lf.read_text().splitlines()[1:]]
        mixed = lrows + [
            _rec(
                [
                    {
                        "agent_name": "Architect",
                        "source": "mock",
                        "proposal_content": {"backbone": "linear"},
                    }
                ]
            )
        ]
        e = provenance_entropies(mixed)
        s = analyse_v05_run(t, lf)
        assert e["architect_backbone_entropy_nats"] == pytest.approx(
            s["architect_backbone_entropy_nats"]
        )
        assert e["architect_backbone_distribution"] == s["architect_backbone_distribution"]

    def test_app_v05_uses_the_single_producers(self) -> None:
        fn = _app_fn("run_v05_sweep")
        called = _called_names(fn)
        assert {"derive_status", "provenance_entropies"} <= called
        assert "per_agent_field_entropy" not in ast.unparse(fn)


class TestOwn1SpendStop:
    @pytest.mark.parametrize(
        "cost,expected",
        [
            (0.0, None),
            (12.0, None),
            (12.0001, "spend_stop"),
            (28.0, "spend_stop"),
            (28.0001, "hard_kill"),
            (100.0, "hard_kill"),
        ],
    )
    def test_spend_guard_boundaries_strict(self, cost, expected) -> None:
        from perturb_eval.experiments.v05_sweep import spend_guard

        assert spend_guard(cost, stop_usd=12.0, kill_usd=28.0) == expected

    def test_sweep_kwarg_default_and_recorded(self) -> None:
        from perturb_eval.experiments import provenance as pv

        fn = _app_fn("run_v05_sweep")
        kwonly = {a.arg: d for a, d in zip(fn.args.kwonlyargs, fn.args.kw_defaults)}
        assert isinstance(kwonly["spend_stop_usd"], ast.Constant)
        assert kwonly["spend_stop_usd"].value == 12.0
        assert "spend_stop_usd" in pv.REQUIRED_ENTRYPOINT_KWARGS
        ep = _app_fn("entrypoint")
        keys = {
            k.value
            for d in ast.walk(ep)
            if isinstance(d, ast.Dict)
            for k in d.keys
            if isinstance(k, ast.Constant)
        }
        assert "spend_stop_usd" in keys
        assert "spend_guard" in _called_names(fn)

    def test_finalize_records_stop_reason_and_cost(self) -> None:
        from perturb_eval.experiments import provenance as pv

        fin = pv.finalize_provenance(
            _build_prov(started_at="2026-09-25T00:00:00+00:00"),
            finished_at="2026-09-25T01:00:00+00:00",
            gpu_seconds=1.0,
            cost_usd_actual=12.3,
            counts={},
            entropies={},
            hvg_n_per_task={},
            params_per_task={},
            budget_hit=False,
            status="partial",
            unparseable_lines={n: [] for n in pv.JSONL_NAMES},
            stop_reason="spend_stop",
            cost_usd_at_stop=12.01,
        )
        assert fin["stop_reason"] == "spend_stop"
        assert fin["cost_usd_at_stop"] == pytest.approx(12.01)


# ---------------------------------------------------------------- C16
class TestC16ControlPredicates:
    def test_one_predicate_per_dataset_in_label_contract(self) -> None:
        from perturb_eval.data import label_contract as lc

        assert set(lc.CONTROL_PREDICATES) == {"adamson_full", "norman"}
        adam, norm = lc.CONTROL_PREDICATES["adamson_full"], lc.CONTROL_PREDICATES["norman"]
        for raw in (
            "*",
            "62(mod)_pBA581",
            "63(mod)_pBA580",
            "3x_neg_ctrl_pMJ144-1",
            "Gal4-4(mod)_pBA582",
        ):
            assert adam(raw), raw
        assert not adam("DDIT3_pDS263")
        for label in ("non-targeting", "NT", "ntc", "CTRL", "control"):
            assert norm(label), label
        assert not norm("CBL_UBASH3A")

    def test_perturbations_is_control_delegates(self) -> None:
        from perturb_eval.data.perturbations import is_control

        for label in (
            "CTRL",
            "ctrl",
            "NT",
            "*",
            "62(mod)_pBA581",  # existing behaviour
            "63(mod)_pBA580",
            "3x_neg_ctrl_pMJ144-1",
            "Gal4-4(mod)_pBA582",
        ):
            assert is_control(label), label
        assert not is_control("SNAI1")

    def test_loaders_use_the_contract_predicates(self) -> None:
        from perturb_eval.data import label_contract as lc
        from perturb_eval.experiments import e2_adamson, norman

        assert norman._is_control_label is lc.is_norman_control
        c = e2_adamson.parse_adamson_construct("63(mod)_pBA580")
        assert c.kind == "control"
        src = (PROJECT_ROOT / "src/perturb_eval/experiments/e2_adamson.py").read_text()
        assert "_CONTROL_PREFIXES = (" not in src


# ---------------------------------------------------------------- C22
class TestC22VersionValidated:
    @pytest.mark.parametrize("v", ["v0.6.0", "v0.6.0-smoke", "v1.2.3rc1", "v0.6.0.a_b"])
    def test_good(self, v) -> None:
        from perturb_eval.experiments.v05_sweep import validate_version, version_out_dir

        assert validate_version(v) == v
        assert version_out_dir(v) == Path("/data") / v

    @pytest.mark.parametrize(
        "v",
        [
            "",
            "v0.6",
            "0.6.0",
            "../etc",
            "v0.6.0/../../etc",
            "/abs",
            "v0.6.0 x",
            "v0.6.0/sub",
            "v0.6.0\n",
        ],
    )
    def test_bad(self, v) -> None:
        from perturb_eval.experiments.v05_sweep import validate_version, version_out_dir

        with pytest.raises(ValueError):
            validate_version(v)
        with pytest.raises(ValueError):
            version_out_dir(v)

    def test_resolves_under_root(self, tmp_path) -> None:
        from perturb_eval.experiments.v05_sweep import version_out_dir

        assert version_out_dir("v0.6.0", root=tmp_path) == tmp_path.resolve() / "v0.6.0"

    def test_app_v05_uses_it(self) -> None:
        fn = _app_fn("run_v05_sweep")
        assert "version_out_dir" in _called_names(fn)
        assert 'Path(f"/data/{version}")' not in ast.unparse(fn)


# ---------------------------------------------------------------- C23 / C24
class TestC23C24DocsAndCli:
    @pytest.mark.parametrize("rel", ["scripts/modal/app_v05.py", "README.md", "paper/README.md"])
    def test_exact_command_documented(self, rel) -> None:
        text = (PROJECT_ROOT / rel).read_text()
        flat = " ".join(re.sub(r"\\+\n", " ", text).split())
        assert EXACT_COMMAND in flat, rel
        assert "source .env" not in text, rel
        assert "PREREGISTRATION.md" in text, rel

    def test_cli_defaults_to_v060(self) -> None:
        from perturb_eval.experiments.e_v05_real_traces import main, parse_cli

        a = parse_cli([])
        assert a.trainer == Path("artifacts/v0.6.0/trainer_runs.jsonl")
        assert a.lifecycle == Path("artifacts/v0.6.0/lifecycle_runs.jsonl")
        assert a.out == Path("artifacts/v0.6.0/summary.json")
        import inspect

        defaults = {k: v.default for k, v in inspect.signature(main).parameters.items()}
        assert defaults["trainer_jsonl"] == Path("artifacts/v0.6.0/trainer_runs.jsonl")

    def test_cli_positional_dir(self, tmp_path) -> None:
        from perturb_eval.experiments.e_v05_real_traces import parse_cli

        a = parse_cli([str(tmp_path)])
        assert a.trainer == tmp_path / "trainer_runs.jsonl"
        assert a.lifecycle == tmp_path / "lifecycle_runs.jsonl"
        assert a.out == tmp_path / "summary.json"
        b = parse_cli([str(tmp_path), "--out", str(tmp_path / "s.json")])
        assert b.out == tmp_path / "s.json" and b.trainer == tmp_path / "trainer_runs.jsonl"

    def test_no_v050_log_tags(self) -> None:
        assert "[v0.5.0]" not in APP_V05.read_text()


# ---------------------------------------------------------------- C11
class TestC11LiteratureParagraph:
    def test_literature_role_is_a_bare_prompt(self) -> None:
        tex = (PROJECT_ROOT / "paper/sections/experimental_setup.tex").read_text()
        for word in ("BioGPT", "PubMed", "STRING"):
            assert word not in tex, word
        assert "no retrieval tools" in tex
        # The C2/C3/C8 marker was resolved by amendment A2-3 (PREREGISTRATION.md):
        # the executors APPLY the parsed fields with a fixed precedence.
        assert "% PENDING principal ruling C2/C3/C8" not in tex
        assert "\\emph{apply} the parsed fields" in tex
        assert "Validator delta $>$ Architect $>$ DataCurator $>$ Trainer" in tex


# ---------------------------------------------------------------- C27
class TestC27Nits:
    def test_mock_pool_is_hashseed_independent(self) -> None:
        code = (
            "from perturb_eval.agentic_lifecycle.loop import MockAgentPool;"
            "print(MockAgentPool(seed=0).propose('DataCurator', 0, 't', {}, seed=0, "
            "dataset='d')['confidence'])"
        )
        outs = set()
        for hs in ("0", "1", "12345"):
            env = dict(os.environ, PYTHONHASHSEED=hs)
            outs.add(
                subprocess.run(
                    [sys.executable, "-c", code],
                    env=env,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
            )
        assert len(outs) == 1, outs

    def test_rho_is_public_with_private_alias(self) -> None:
        assert pr.rho is pr._rho
        src = (PROJECT_ROOT / "scripts/local/prereg_null_fwer.py").read_text()
        assert "import _rho" not in src and "rho" in src
