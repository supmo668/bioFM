"""Amendment 2 (PREREGISTRATION.md, prereg_version v0.6.0-a4): lifecycle-side rules.

A2-1 required verbalised confidence; A2-2 exactly three rounds, Validator
verdict/threshold recorded but non-stopping; A2-3 agent configuration applied
with precedence Validator delta > Architect > DataCurator > defaults (driven
through real ``parse_proposal`` output); A2-6 stated vs executed backbone,
pinned menu; A2-8 dataset + modality in every role's system preamble and an
empty, version-namespaced LLM cache. No network: every client is a fake.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest
from pydantic import ValidationError

from perturb_eval.agentic_lifecycle.llm_agent_pool import LLMAgentPool
from perturb_eval.agentic_lifecycle.proposal_schema import BACKBONE_MENU, parse_proposal
from perturb_eval.agentic_lifecycle.types import ExecutedValidation, StructuredCritiqueDTO
from perturb_eval.llm.openrouter_client import ChatResult

ROLES = ("DataCurator", "Literature", "Architect", "Trainer", "Validator")

# Minimal schema-valid replies (A2-1: confidence; A2-6: Architect backbone).
VALID = {
    "DataCurator": {"hvg_count": 500, "confidence": 0.61},
    "Literature": {"expected_up": ["A"], "confidence": 0.52},
    "Architect": {"backbone": "linear", "confidence": 0.73},
    "Trainer": {"lr": 0.02, "epochs": 30, "ridge_lambda": 2.0, "confidence": 0.44},
    "Validator": {"dynamic_threshold_msd": 0.25, "confidence": 0.9},
}


class ScriptedClient:
    """Fake OpenRouter client: per-role reply (dict, or callable(round) -> dict)."""

    def __init__(self, replies: dict | None = None, *, cache_hit: bool = False) -> None:
        self.replies = {**VALID, **(replies or {})}
        self.prompts: dict[tuple[str, int], str] = {}
        self.cache_hit = cache_hit

    def chat_json(self, *, role, task_id, round_index, prompt, seed, dataset):
        self.prompts[(role, round_index)] = prompt
        rep = self.replies[role]
        content = rep(round_index) if callable(rep) else rep
        return ChatResult(
            content=json.loads(json.dumps(content)), model_id="fake/m", cache_hit=self.cache_hit
        )


def _pool(client, tmp_path: Path) -> LLMAgentPool:
    return LLMAgentPool(client=client, cache_dir=tmp_path)


def _toy():
    rng = np.random.default_rng(0)
    X = rng.standard_normal((200, 40)) * 0.3 + 2.0
    labels = np.asarray(["CTRL"] * 50 + ["A"] * 50 + ["B"] * 50 + ["C"] * 50)
    X[50:100, 5] -= 2.0
    X[100:150, 10] -= 2.0
    X[150:200, 15] -= 2.0
    return X, labels, labels == "CTRL", {"A": 5, "B": 10, "C": 15}


def _run(pool, **kw):
    from perturb_eval.agentic_lifecycle.loop import run_agentic_lifecycle

    X, labels, cm, tgi = _toy()
    kw.setdefault("max_rounds", 3)
    return run_agentic_lifecycle(
        task_id="hold_C",
        X=X,
        labels=labels,
        control_mask=cm,
        target_gene_idx=tgi,
        held_out="C",
        agent_pool=pool,
        seed=2026,
        dataset="adamson_full",
        **kw,
    )


# =========================================================================== A2-1
class TestA2_1_RequiredConfidence:
    @pytest.mark.parametrize("role", ROLES)
    def test_missing_confidence_is_schema_failure(self, role) -> None:
        payload = {k: v for k, v in VALID[role].items() if k != "confidence"}
        with pytest.raises(ValidationError):
            parse_proposal(role, payload)

    @pytest.mark.parametrize("role", ROLES)
    @pytest.mark.parametrize(
        "bad", ["0.7", "high", None, True, -0.01, 1.01, float("nan"), float("inf"), [0.5]]
    )
    def test_non_numeric_non_finite_or_out_of_range_is_schema_failure(self, role, bad) -> None:
        with pytest.raises(ValidationError):
            parse_proposal(role, {**VALID[role], "confidence": bad})

    @pytest.mark.parametrize("role", ROLES)
    @pytest.mark.parametrize("ok", [0, 0.0, 0.5, 1, 1.0])
    def test_in_range_confidence_accepted(self, role, ok) -> None:
        assert parse_proposal(role, {**VALID[role], "confidence": ok}).confidence == ok

    def test_pool_carries_the_stated_confidence_not_a_default(self, tmp_path) -> None:
        pool = _pool(ScriptedClient(), tmp_path)
        for role in ROLES:
            out = pool.propose(role, 0, "t", {}, seed=0, dataset="adamson_full")
            assert out["source"] == "llm"
            assert out["confidence"] == VALID[role]["confidence"]
            assert "confidence" not in out["content"]

    @pytest.mark.parametrize("role", ROLES)
    def test_pool_missing_confidence_falls_back_and_is_never_imputed(self, role, tmp_path) -> None:
        payload = {k: v for k, v in VALID[role].items() if k != "confidence"}
        pool = _pool(ScriptedClient({role: payload}), tmp_path)
        out = pool.propose(role, 0, "t", {}, seed=0, dataset="adamson_full")
        assert out["source"] == "fallback" and out["model_id"] is None
        assert out["confidence"] is None  # never imputed

    def test_fallback_on_transport_error_has_no_imputed_confidence(self, tmp_path) -> None:
        from perturb_eval.llm.openrouter_client import OpenRouterError

        failing = MagicMock()
        failing.chat_json = MagicMock(side_effect=OpenRouterError("down"))
        out = _pool(failing, tmp_path).propose(
            "Trainer", 0, "t", {}, seed=0, dataset="adamson_full"
        )
        assert out["source"] == "fallback" and out["confidence"] is None

    @pytest.mark.parametrize("role", ROLES)
    def test_one_missing_confidence_makes_the_run_invalid(self, role, tmp_path) -> None:
        from perturb_eval.experiments.v05_sweep import derive_status

        payload = {k: v for k, v in VALID[role].items() if k != "confidence"}
        run = _run(_pool(ScriptedClient({role: payload}), tmp_path), max_rounds=1)
        from dataclasses import asdict

        step = next(s for s in run.steps if s.agent_name == role)
        assert step.source == "fallback" and step.llm_confidence is None
        assert derive_status([asdict(run)], cost_usd=0.0, kill_usd=28.0) == "failed_fallback"

    @pytest.mark.parametrize("role", ROLES)
    def test_every_role_prompt_requires_confidence(self, role, tmp_path) -> None:
        client = ScriptedClient()
        _pool(client, tmp_path).propose(role, 0, "t", {}, seed=0, dataset="norman")
        prompt = client.prompts[(role, 0)]
        assert '"confidence"' in prompt and "[0, 1]" in prompt and "required" in prompt

    def test_loop_refuses_an_llm_step_without_a_valid_confidence(self) -> None:
        from perturb_eval.agentic_lifecycle.loop import MockAgentPool

        class BadPool(MockAgentPool):
            def propose(self, role, round_index, task_id, context, *, seed, dataset):
                out = super().propose(
                    role, round_index, task_id, context, seed=seed, dataset=dataset
                )
                return {**out, "source": "llm", "model_id": "m", "confidence": None}

        with pytest.raises(ValueError, match="confidence"):
            _run(BadPool(), max_rounds=1)


# =========================================================================== A2-2
class TestA2_2_FixedThreeRounds:
    def test_three_rounds_run_even_when_validator_accepts_every_round(self, tmp_path) -> None:
        run = _run(_pool(ScriptedClient(), tmp_path), validator_threshold_override=1e9)
        assert run.n_rounds == 3
        assert sorted({s.round_index for s in run.steps}) == [0, 1, 2]
        assert len(run.steps) == 15
        val = [s for s in run.steps if s.agent_name == "Validator"]
        assert [s.validator_accepted for s in val] == [True, True, True]

    def test_three_rounds_run_when_validator_rejects_every_round(self, tmp_path) -> None:
        run = _run(_pool(ScriptedClient(), tmp_path), validator_threshold_override=-1.0)
        assert run.n_rounds == 3
        assert [s.validator_accepted for s in run.steps if s.agent_name == "Validator"] == [
            False,
            False,
            False,
        ]

    def test_validator_threshold_is_read_from_the_schema_field_and_recorded(self, tmp_path) -> None:
        run = _run(_pool(ScriptedClient(), tmp_path))
        val = [s for s in run.steps if s.agent_name == "Validator"]
        assert [s.validator_threshold_msd for s in val] == [0.25, 0.25, 0.25]
        assert all(isinstance(s.validator_accepted, bool) for s in val)

    @staticmethod
    def _distinct_msd_gate(monkeypatch, msds=(0.3, 0.1, 0.2)) -> None:
        """QG-4: rounds must be distinguishable — the gate returns a DIFFERENT
        MSD per round, and the best round (0.1) is deliberately not the last."""
        import perturb_eval.agentic_lifecycle.loop as loop_mod

        it = iter(msds)

        def fake_gate(**kw):
            return ExecutedValidation(
                msd_topk=next(it),
                biofm_agreement=0.5,
                deg_overlap_at_k=0.5,
                accepted=True,
                rationale="r",
                critique=StructuredCritiqueDTO(),
            )

        monkeypatch.setattr(loop_mod, "score_and_gate", fake_gate)

    def test_final_msd_is_round_two(self, tmp_path, monkeypatch) -> None:
        self._distinct_msd_gate(monkeypatch)
        run = _run(_pool(ScriptedClient(), tmp_path))
        assert run.msd_per_round == (0.3, 0.1, 0.2)
        assert run.final_msd_topk == 0.2  # the LAST round's, not the min (0.1) or first (0.3)

    def test_sweep_record_final_msd_is_round_two(self, tmp_path, monkeypatch) -> None:
        from perturb_eval.experiments.v05_sweep import lifecycle_record

        self._distinct_msd_gate(monkeypatch)
        X, labels, cm, tgi = _toy()
        ds = {"X": X, "labels": labels, "control_mask": cm, "target_gene_idx": tgi}
        rec = lifecycle_record(
            task="C",
            dataset_name="adamson_full",
            ds=ds,
            seed=0,
            pool=_pool(ScriptedClient(), tmp_path),
        )
        assert tuple(rec["msd_per_round"]) == (0.3, 0.1, 0.2)
        assert rec["final_msd_topk"] == 0.2

    def test_sweep_record_always_runs_three_rounds(self) -> None:
        from perturb_eval.experiments.v05_sweep import LIFECYCLE_N_ROUNDS, lifecycle_record

        assert LIFECYCLE_N_ROUNDS == 3
        seen = {}

        def fn(**kw):
            seen.update(kw)
            return _run(
                __import__(
                    "perturb_eval.agentic_lifecycle.loop", fromlist=["MockAgentPool"]
                ).MockAgentPool(),
                max_rounds=1,
            )

        X, labels, cm, tgi = _toy()
        ds = {"X": X, "labels": labels, "control_mask": cm, "target_gene_idx": tgi}
        lifecycle_record(task="C", dataset_name="adamson_full", ds=ds, seed=0, pool=None, run_fn=fn)
        assert seen["max_rounds"] == 3

    @pytest.mark.parametrize("n", [1, 2, 4])
    def test_sweep_refuses_any_other_round_count(self, n) -> None:
        from perturb_eval.experiments.v05_sweep import iter_lifecycle_records, lifecycle_record

        with pytest.raises(ValueError, match="three rounds|3 rounds"):
            lifecycle_record(
                task="C",
                dataset_name="adamson_full",
                ds={},
                seed=0,
                pool=None,
                run_fn=lambda **k: None,
                max_rounds=n,
            )
        with pytest.raises(ValueError, match="three rounds|3 rounds"):
            list(iter_lifecycle_records(datasets=[], seeds=[0], pool=None, max_rounds=n))


# =========================================================================== A2-3
class TestA2_3_ConfigApplied:
    def test_precedence_validator_over_architect_over_datacurator_over_default(self) -> None:
        from perturb_eval.agentic_lifecycle.architect_dispatch import resolve_applied_config

        dc = parse_proposal(
            "DataCurator", {"hvg_count": 500, "qc_mito_max": 9.0, "confidence": 0.5}
        )
        arch = parse_proposal(
            "Architect",
            {"backbone": "mlp", "hvg_count": 1000, "learning_rate": 0.003, "confidence": 0.5},
        )
        cfg, src = resolve_applied_config(
            datacurator=dc.model_dump(),
            datacurator_stated=dc.model_fields_set,
            architect=arch.model_dump(),
            architect_stated=arch.model_fields_set,
            critique_delta={"learning_rate": 1e-4},
        )
        assert (cfg["hvg_count"], src["hvg_count"]) == (1000, "architect")
        assert (cfg["learning_rate"], src["learning_rate"]) == (1e-4, "validator")
        assert (cfg["qc_mito_max"], src["qc_mito_max"]) == (9.0, "datacurator")
        assert (cfg["backbone"], src["backbone"]) == ("mlp", "architect")
        # Not stated by anyone -> default (the Architect's schema default is NOT a statement).
        assert src["ridge_lambda"] == "default" and src["epochs"] == "default"

    def test_datacurator_hvg_applies_when_architect_does_not_state_it(self) -> None:
        from perturb_eval.agentic_lifecycle.architect_dispatch import resolve_applied_config

        dc = parse_proposal("DataCurator", {"hvg_count": 500, "confidence": 0.5})
        arch = parse_proposal("Architect", {"backbone": "linear", "confidence": 0.5})
        cfg, src = resolve_applied_config(
            datacurator=dc.model_dump(),
            datacurator_stated=dc.model_fields_set,
            architect=arch.model_dump(),
            architect_stated=arch.model_fields_set,
            critique_delta=None,
        )
        assert (cfg["hvg_count"], src["hvg_count"]) == (500, "datacurator")

    def test_parsed_proposals_drive_the_executors(self, tmp_path, monkeypatch) -> None:
        """Real parse_proposal output (via LLMAgentPool) -> applied values reach
        the HVG selector and the backbone fit; the Validator's delta wins next round."""
        import perturb_eval.agentic_lifecycle.loop as loop_mod
        from perturb_eval.data import hvg as hvg_mod

        hvg_calls: list[int] = []
        real_select = hvg_mod.select_hvg_train_only

        def spy_select(X, train_mask, n_top, **kw):
            hvg_calls.append(int(n_top))
            return real_select(X, train_mask, n_top, **kw)

        monkeypatch.setattr(hvg_mod, "select_hvg_train_only", spy_select)

        fit_cfgs: list = []
        from perturb_eval.backbones.linear import LinearBackbone

        real_fit = LinearBackbone.fit

        def spy_fit(self, X, labels, cm, tgi, cfg):
            fit_cfgs.append(cfg)
            return real_fit(self, X, labels, cm, tgi, cfg)

        monkeypatch.setattr(LinearBackbone, "fit", spy_fit)

        def fake_gate(**kw):
            return ExecutedValidation(
                msd_topk=1.0,
                biofm_agreement=0.5,
                deg_overlap_at_k=0.5,
                accepted=False,
                rationale="r",
                critique=StructuredCritiqueDTO(
                    suggested_next_config_delta={"learning_rate": 1e-4, "hvg_count": 1000}
                ),
            )

        monkeypatch.setattr(loop_mod, "score_and_gate", fake_gate)
        client = ScriptedClient(
            {
                "DataCurator": {"hvg_count": 500, "qc_mito_max": 8.0, "confidence": 0.6},
                "Architect": {
                    "backbone": "linear",
                    "learning_rate": 0.005,
                    "ridge_lambda": 3.0,
                    "epochs": 25,
                    "confidence": 0.7,
                },
                "Trainer": {"lr": 0.09, "epochs": 99, "ridge_lambda": 9.0, "confidence": 0.4},
            }
        )
        run = _run(_pool(client, tmp_path), max_rounds=2)
        # Round 0: DataCurator's HVG (Architect silent on it), Architect's trainer fields.
        assert hvg_calls[0] == 500
        assert fit_cfgs[0].learning_rate == 0.005
        assert fit_cfgs[0].ridge_lambda == 3.0
        assert fit_cfgs[0].max_iter == 25
        # Round 1: Validator delta overrides Architect and DataCurator.
        assert hvg_calls[1] == 1000
        assert fit_cfgs[1].learning_rate == 1e-4
        assert fit_cfgs[1].ridge_lambda == 3.0
        a0, a1 = run.applied_config_per_round
        assert a0["values"]["hvg_count"] == 500 and a0["sources"]["hvg_count"] == "datacurator"
        assert a0["values"]["qc_mito_max"] == 8.0
        assert a1["values"]["learning_rate"] == 1e-4
        assert a1["sources"]["learning_rate"] == "validator"
        assert a1["sources"]["ridge_lambda"] == "architect"

    def test_qc_mito_max_is_recorded_as_not_applied(self, tmp_path) -> None:
        """QG-2: ``execute_data_curator`` only LOGS the mito threshold — there is
        no per-cell mito fraction in the lifecycle dataset and no cell filter —
        so the per-round record must say so explicitly instead of filing the
        DataCurator's value as applied. Every other field IS applied."""
        client = ScriptedClient(
            {"DataCurator": {"hvg_count": 500, "qc_mito_max": 8.0, "confidence": 0.6}}
        )
        run = _run(_pool(client, tmp_path), max_rounds=1)
        (a,) = run.applied_config_per_round
        # The value and its source are still recorded ...
        assert a["values"]["qc_mito_max"] == 8.0
        assert a["sources"]["qc_mito_max"] == "datacurator"
        # ... but the record says it was NOT applied, and why.
        assert set(a["applied"]) == set(a["values"])
        assert a["applied"]["qc_mito_max"] is False
        reason = a["not_applied_reason"]["qc_mito_max"]
        assert "mito" in reason and "not implemented" in reason
        assert set(a["not_applied_reason"]) == {"qc_mito_max"}
        for field in set(a["values"]) - {"qc_mito_max"}:
            assert a["applied"][field] is True, field

    def test_not_applied_flag_survives_the_sweep_record(self, tmp_path) -> None:
        from perturb_eval.experiments.v05_sweep import lifecycle_record

        X, labels, cm, tgi = _toy()
        ds = {"X": X, "labels": labels, "control_mask": cm, "target_gene_idx": tgi}
        rec = lifecycle_record(
            task="C",
            dataset_name="adamson_full",
            ds=ds,
            seed=0,
            pool=_pool(ScriptedClient(), tmp_path),
        )
        for a in json.loads(json.dumps(rec, default=str))["applied_config_per_round"]:
            assert a["applied"]["qc_mito_max"] is False
            assert a["not_applied_reason"]["qc_mito_max"]

    def test_applied_config_is_in_the_sweep_record(self, tmp_path) -> None:
        from perturb_eval.experiments.v05_sweep import lifecycle_record

        X, labels, cm, tgi = _toy()
        ds = {"X": X, "labels": labels, "control_mask": cm, "target_gene_idx": tgi}
        rec = lifecycle_record(
            task="C",
            dataset_name="adamson_full",
            ds=ds,
            seed=0,
            pool=_pool(ScriptedClient(), tmp_path),
        )
        json.dumps(rec, default=str)
        assert len(rec["applied_config_per_round"]) == 3
        for a in rec["applied_config_per_round"]:
            assert (
                set(a["values"])
                == set(a["sources"])
                >= {
                    "backbone",
                    "hvg_count",
                    "qc_mito_max",
                    "learning_rate",
                    "ridge_lambda",
                    "epochs",
                }
            )


# =========================================================================== A2-6
class TestA2_6_StatedVsExecutedBackbone:
    def test_menu_is_pinned(self) -> None:
        from perturb_eval.agentic_lifecycle import validator_gate

        assert BACKBONE_MENU == ("linear", "mlp", "scgpt_small")
        assert tuple(validator_gate._BACKBONE_ROTATION) == BACKBONE_MENU

    def test_architect_prompt_offers_exactly_the_menu(self, tmp_path) -> None:
        client = ScriptedClient()
        _pool(client, tmp_path).propose("Architect", 0, "t", {}, seed=0, dataset="norman")
        prompt = client.prompts[("Architect", 0)]
        assert '"linear" | "mlp" | "scgpt_small"' in prompt

    @pytest.mark.parametrize("bad", [None, "scgpt", "transformer", "LINEAR", ""])
    def test_missing_or_off_menu_backbone_is_schema_failure(self, bad, tmp_path) -> None:
        payload = {"confidence": 0.5}
        if bad is not None:
            payload["backbone"] = bad
        with pytest.raises(ValidationError):
            parse_proposal("Architect", payload)
        out = _pool(ScriptedClient({"Architect": payload}), tmp_path).propose(
            "Architect", 0, "t", {}, seed=0, dataset="adamson_full"
        )
        assert out["source"] == "fallback"
        assert "backbone" not in out["content"]  # never defaulted

    def test_steps_record_stated_and_executed_backbone(self, tmp_path, monkeypatch) -> None:
        import perturb_eval.agentic_lifecycle.loop as loop_mod

        def fake_gate(**kw):
            return ExecutedValidation(
                msd_topk=1.0,
                biofm_agreement=0.5,
                deg_overlap_at_k=0.5,
                accepted=False,
                rationale="r",
                critique=StructuredCritiqueDTO(suggested_next_config_delta={"backbone": "mlp"}),
            )

        monkeypatch.setattr(loop_mod, "score_and_gate", fake_gate)
        run = _run(_pool(ScriptedClient(), tmp_path), max_rounds=2)
        arch = [s for s in run.steps if s.agent_name == "Architect"]
        assert [(s.backbone_stated, s.backbone_used) for s in arch] == [
            ("linear", "linear"),
            ("linear", "mlp"),
        ]
        assert run.backbone_used == "mlp"
        # The spec's field name (A2-6) is ``backbone_used``; no second name.
        assert not hasattr(arch[0], "backbone_executed")
        for s in run.steps:
            if s.agent_name != "Architect":
                assert s.backbone_stated is None and s.backbone_used is None

    def test_fallback_architect_step_states_no_backbone(self, tmp_path) -> None:
        run = _run(
            _pool(ScriptedClient({"Architect": {"confidence": 0.5}}), tmp_path), max_rounds=1
        )
        arch = next(s for s in run.steps if s.agent_name == "Architect")
        assert arch.source == "fallback"
        assert arch.backbone_stated is None
        assert arch.backbone_used in BACKBONE_MENU


# =========================================================================== A2-8
class TestA2_8_PromptAndCache:
    @pytest.mark.parametrize("role", ROLES)
    @pytest.mark.parametrize(
        "dataset,needles",
        [
            ("adamson_full", ("Adamson 2016", "K562", "CRISPR interference")),
            ("norman", ("Norman 2019", "K562", "CRISPR activation")),
        ],
    )
    def test_dataset_and_modality_in_every_role_system_preamble(
        self, role, dataset, needles, tmp_path
    ) -> None:
        client = ScriptedClient()
        _pool(client, tmp_path).propose(role, 0, "t", {}, seed=0, dataset=dataset)
        preamble = client.prompts[(role, 0)].split("\n\n", 1)[0]
        for n in needles:
            assert n in preamble, (role, n, preamble)

    def test_unknown_dataset_is_refused(self, tmp_path) -> None:
        with pytest.raises(ValueError, match="dataset"):
            _pool(ScriptedClient(), tmp_path).propose("Trainer", 0, "t", {}, seed=0, dataset="toy")

    def test_prereg_version_and_namespace(self, tmp_path) -> None:
        from perturb_eval.llm.openrouter_client import PREREG_VERSION, versioned_cache_dir

        assert PREREG_VERSION == "v0.6.0-a4"
        assert versioned_cache_dir(tmp_path) == tmp_path / "v0.6.0-a4"
        assert versioned_cache_dir(tmp_path, "vX") == tmp_path / "vX"

    def test_count_cache_entries_sees_client_writes(self, tmp_path) -> None:
        from perturb_eval.llm.openrouter_client import (
            OpenRouterClient,
            count_cache_entries,
            versioned_cache_dir,
        )

        ns = versioned_cache_dir(tmp_path)
        assert count_cache_entries(ns) == 0  # absent namespace counts as empty
        # A sibling namespace (an earlier version's cache) is not counted.
        (tmp_path / "v0.5.0" / "ab").mkdir(parents=True)
        (tmp_path / "v0.5.0" / "ab" / "x.json").write_text("{}")
        resp = MagicMock(status_code=200)
        resp.json.return_value = {"choices": [{"message": {"content": '{"a": 1}'}}]}
        session = MagicMock()
        session.post.return_value = resp
        client = OpenRouterClient(api_key="k", cache_dir=ns, session=session)
        assert count_cache_entries(ns) == 0
        client.chat_json(
            role="Trainer", task_id="t", round_index=0, prompt="p", seed=0, dataset="norman"
        )
        assert count_cache_entries(ns) == 1

    def test_cache_start_record(self, tmp_path) -> None:
        from perturb_eval.experiments.v05_sweep import llm_cache_start

        rec = llm_cache_start(tmp_path)
        assert rec == {
            "prereg_version": "v0.6.0-a4",
            "llm_cache_namespace": str(tmp_path / "v0.6.0-a4"),
            "llm_cache_entries_at_start": 0,
        }
        (tmp_path / "v0.6.0-a4" / "ab").mkdir(parents=True)
        (tmp_path / "v0.6.0-a4" / "ab" / "k.json").write_text("{}")
        assert llm_cache_start(tmp_path)["llm_cache_entries_at_start"] == 1

    def test_cache_end_record_counts_hits_and_flags_replay(self) -> None:
        from perturb_eval.experiments.v05_sweep import llm_cache_end

        rows = [
            {
                "steps": [
                    {"source": "llm", "cache_hit": False},
                    {"source": "llm", "cache_hit": False},
                    {"source": "mock", "cache_hit": None},
                ]
            },
            {"record_type": "provenance", "steps": [{"source": "llm", "cache_hit": True}]},
        ]
        assert llm_cache_end(rows, entries_at_start=0) == {
            "llm_cache_hit_count": 0,
            "replay": False,
            "replay_reasons": [],
        }
        rows.append({"steps": [{"source": "llm", "cache_hit": True}]})
        end = llm_cache_end(rows, entries_at_start=0)
        assert end["llm_cache_hit_count"] == 1 and end["replay"] is True
        end2 = llm_cache_end(rows[:1], entries_at_start=5)
        assert end2["replay"] is True and end2["llm_cache_hit_count"] == 0
        assert any("5" in r for r in end2["replay_reasons"])

    def test_cache_hit_flag_reaches_the_step(self, tmp_path) -> None:
        run = _run(_pool(ScriptedClient(cache_hit=True), tmp_path), max_rounds=1)
        assert all(s.cache_hit is True for s in run.steps)

    def test_app_v05_uses_the_namespaced_cache_and_records_it(self) -> None:
        src = (Path(__file__).resolve().parents[1] / "scripts" / "modal" / "app_v05.py").read_text()
        assert "versioned_cache_dir(" in src
        assert "llm_cache_start(" in src and "llm_cache_end(" in src
        # The client must not be pointed at the un-namespaced root any more.
        assert "cache_dir=Path(_LLM_CACHE_DIR)" not in src


def test_nan_confidence_json_literal_is_rejected() -> None:
    payload = json.loads('{"backbone": "mlp", "confidence": NaN}')
    assert math.isnan(payload["confidence"])
    with pytest.raises(ValidationError):
        parse_proposal("Architect", payload)
