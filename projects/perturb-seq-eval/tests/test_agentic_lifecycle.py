"""Unit + integration tests for the end-to-end agentic lifecycle package.

See docs/plans/2026-04-22-end-to-end-agentic-lifecycle.md for the plan.
"""

from __future__ import annotations

import numpy as np
import pytest

from perturb_eval.agentic_lifecycle.types import (
    ExecutedProposal,
    ExecutedValidation,
    LifecycleRun,
    LifecycleStep,
)


@pytest.mark.unit
def test_lifecycle_run_is_frozen_and_holds_msd() -> None:
    step = LifecycleStep(
        round_index=0,
        agent_name="Trainer",
        proposal_content={"lr": 1e-3},
        rationale="ok",
        llm_confidence=0.8,
        execution_artifact_path=None,
        wall_time_sec=0.1,
        succeeded=True,
    )
    run = LifecycleRun(
        task_id="DDIT3",
        steps=(step,),
        final_msd_topk=0.005,
        final_validator_agreement=0.7,
        n_rounds=1,
        n_agents=5,
        backbone_used="linear",
    )
    with pytest.raises(Exception):
        run.final_msd_topk = 0.0  # type: ignore[misc]
    assert run.final_msd_topk == 0.005
    assert run.steps[0].agent_name == "Trainer"


@pytest.mark.unit
def test_data_curator_applies_hvg_filter() -> None:
    from perturb_eval.agentic_lifecycle.data_curator_exec import execute_data_curator
    X = np.random.default_rng(0).standard_normal((200, 500))
    labels = np.asarray(["CTRL"] * 100 + ["A"] * 100)
    curated = execute_data_curator(
        X=X, labels=labels,
        proposal={"n_top_hvg": 200, "pct_mito_max": 15.0},
        # T8b: train_mask is now required (HVG ranked on training rows only).
        train_mask=np.ones(200, dtype=bool),
    )
    assert curated["X"].shape == (200, 200)
    assert curated["labels"].shape == (200,)
    assert curated["execution_meta"]["applied_hvg"] == 200


@pytest.mark.unit
def test_literature_extractor_passes_through_biogpt_output() -> None:
    from perturb_eval.agentic_lifecycle.literature_exec import extract_expected_genes
    proposal = {
        "pathways": ["UPR", "ER stress"],
        "expected_up": ["ATF4", "CHOP", "DDIT3"],
        "expected_down": ["HSPA5"],
    }
    extracted = extract_expected_genes(proposal)
    assert set(extracted["up"]) == {"ATF4", "CHOP", "DDIT3"}
    assert set(extracted["down"]) == {"HSPA5"}
    assert set(extracted["pathways"]) == {"UPR", "ER stress"}


@pytest.mark.unit
def test_architect_dispatch_returns_backbone_and_name() -> None:
    from perturb_eval.agentic_lifecycle.architect_dispatch import dispatch_architect
    for bb_name in ("linear", "mlp"):
        backbone, chosen_name = dispatch_architect({"backbone": bb_name})
        assert chosen_name == bb_name
        assert hasattr(backbone, "fit")
        assert hasattr(backbone, "predict_logfc")


@pytest.mark.unit
def test_architect_dispatch_maps_scgpt_alias_or_falls_back() -> None:
    from perturb_eval.agentic_lifecycle.architect_dispatch import dispatch_architect
    backbone, chosen = dispatch_architect({"backbone": "scGPT"})
    assert chosen in ("linear", "scgpt_small")
    assert hasattr(backbone, "fit")


@pytest.mark.unit
def test_trainer_exec_fits_and_returns_meta() -> None:
    from perturb_eval.agentic_lifecycle.trainer_exec import execute_trainer
    from perturb_eval.backbones import build_backbone
    rng = np.random.default_rng(0)
    X = rng.standard_normal((200, 40)) * 0.3 + 2.0
    labels = np.asarray(["CTRL"] * 50 + ["A"] * 50 + ["B"] * 50 + ["C"] * 50)
    X[50:100, 2] -= 2.0
    control_mask = labels == "CTRL"
    backbone = build_backbone("linear")
    meta = execute_trainer(
        backbone=backbone, X=X, labels=labels, control_mask=control_mask,
        target_gene_idx={"A": 2, "B": 5, "C": 7},
        trainer_proposal={"optimizer": "adamw", "lr": 1e-2, "epochs": 50},
        seed=2026,
    )
    assert meta["succeeded"] is True
    assert meta["n_train_perts"] == 3
    assert meta["wall_time_sec"] >= 0


@pytest.mark.unit
def test_validator_gate_produces_finite_msd_and_flag() -> None:
    from perturb_eval.agentic_lifecycle.validator_gate import score_and_gate
    from perturb_eval.backbones import BackboneTrainConfig, build_backbone
    from perturb_eval.data.hvg import top_deg_columns
    rng = np.random.default_rng(0)
    X = rng.standard_normal((200, 40)) * 0.3 + 2.0
    labels = np.asarray(["CTRL"] * 100 + ["A"] * 100)
    X[100:, 2] -= 2.0
    control_mask = labels == "CTRL"
    bb = build_backbone("linear")
    bb.fit(X, labels.tolist(), control_mask, {"A": 2},
           BackboneTrainConfig(max_iter=50, seed=0))
    report = score_and_gate(
        backbone=bb, X=X, labels=labels, control_mask=control_mask,
        held_out="A", held_out_target_idx=2, threshold_msd=0.5,
        eval_cols=top_deg_columns(X, labels, control_mask, "A"),  # A2-5
    )
    assert report.msd_topk >= 0
    assert isinstance(report.accepted, bool)


@pytest.mark.unit
def test_executed_proposal_and_validation_types_are_frozen() -> None:
    p = ExecutedProposal(
        agent_name="Trainer", proposal_content={}, rationale="x",
        llm_confidence=0.5, execution_artifact_path=None,
        wall_time_sec=0.0, succeeded=True,
    )
    v = ExecutedValidation(
        msd_topk=0.1, biofm_agreement=0.5, deg_overlap_at_k=0.6,
        accepted=False, rationale="x",
    )
    with pytest.raises(Exception):
        p.succeeded = False  # type: ignore[misc]
    with pytest.raises(Exception):
        v.accepted = True  # type: ignore[misc]


@pytest.mark.unit
def test_agentic_lifecycle_terminates_and_produces_msd() -> None:
    from perturb_eval.agentic_lifecycle.loop import MockAgentPool, run_agentic_lifecycle

    rng = np.random.default_rng(0)
    X = rng.standard_normal((200, 40)) * 0.3 + 2.0
    labels = np.asarray(["CTRL"] * 50 + ["A"] * 50 + ["B"] * 50 + ["C"] * 50)
    X[50:100, 5] -= 2.0
    X[100:150, 10] -= 2.0
    X[150:200, 15] -= 2.0
    control_mask = labels == "CTRL"
    target_gene_idx = {"A": 5, "B": 10, "C": 15}
    pool = MockAgentPool(seed=0)
    run = run_agentic_lifecycle(
        task_id="hold_C",
        X=X, labels=labels, control_mask=control_mask,
        target_gene_idx=target_gene_idx, held_out="C",
        agent_pool=pool, max_rounds=2, seed=2026,
        dataset="adamson_full",
    )
    assert run.n_rounds <= 2
    assert run.final_msd_topk >= 0.0
    assert run.backbone_used in ("linear", "mlp", "scgpt_small")
    assert len(run.steps) >= 5


# --- T5 / A2: the run seed reaches the LLM pool and the trainer -------------


def _seed_fixture():
    """Tiny numpy matrix: controls + four perturbations, each knocking a gene down."""
    rng = np.random.default_rng(7)
    n_per, n_genes = 40, 60
    names = ["CTRL", "A", "B", "C", "D"]
    X = rng.standard_normal((n_per * len(names), n_genes)) * 0.3 + 2.0
    labels = np.repeat(np.asarray(names), n_per)
    target_gene_idx = {"A": 5, "B": 10, "C": 15, "D": 20}
    for p, g in target_gene_idx.items():
        X[labels == p, g] -= 2.0
    control_mask = labels == "CTRL"
    return X, labels, control_mask, target_gene_idx


class _SeedRecordingPool:
    """Stub pool: MockAgentPool proposals, but records every seed it is handed."""

    def __init__(self) -> None:
        from perturb_eval.agentic_lifecycle.loop import MockAgentPool
        self._inner = MockAgentPool(seed=0)
        self.seeds: list[int] = []

    def propose(self, role, round_index, task_id, context, *, seed, dataset):
        self.seeds.append(seed)
        return self._inner.propose(role, round_index, task_id, context, seed=seed, dataset=dataset)


def _run_with_seed(seed: int, pool=None):
    from perturb_eval.agentic_lifecycle.loop import run_agentic_lifecycle
    X, labels, control_mask, target_gene_idx = _seed_fixture()
    return run_agentic_lifecycle(
        task_id="hold_D",
        X=X, labels=labels, control_mask=control_mask,
        target_gene_idx=target_gene_idx, held_out="D",
        agent_pool=pool if pool is not None else _SeedRecordingPool(),
        max_rounds=1, backbone_override="mlp",
        validator_threshold_override=0.0,
        seed=seed,
        dataset="adamson_full",
    )


@pytest.mark.unit
def test_lifecycle_msd_differs_across_seeds() -> None:
    run_a = _run_with_seed(2026)
    run_b = _run_with_seed(2027)
    assert run_a.backbone_used == "mlp"
    assert np.isfinite(run_a.final_msd_topk) and np.isfinite(run_b.final_msd_topk)
    assert run_a.final_msd_topk != run_b.final_msd_topk


@pytest.mark.unit
def test_lifecycle_passes_run_seed_to_agent_pool() -> None:
    pool = _SeedRecordingPool()
    _run_with_seed(4242, pool=pool)
    assert pool.seeds, "pool.propose was never called"
    assert set(pool.seeds) == {4242}


@pytest.mark.unit
def test_execute_trainer_passes_seed_into_backbone_config() -> None:
    from perturb_eval.agentic_lifecycle.trainer_exec import execute_trainer

    captured = {}

    class _SpyBackbone:
        def fit(self, X, labels, control_mask, target_gene_idx, cfg):
            captured["seed"] = cfg.seed

    X, labels, control_mask, target_gene_idx = _seed_fixture()
    meta = execute_trainer(
        backbone=_SpyBackbone(), X=X, labels=labels, control_mask=control_mask,
        target_gene_idx=target_gene_idx,
        trainer_proposal={"lr": 1e-2, "epochs": 5, "seed": 9999},
        seed=31337,
    )
    assert meta["succeeded"] is True
    # The run seed wins; an LLM-supplied "seed" key is ignored.
    assert captured["seed"] == 31337


@pytest.mark.unit
def test_run_agentic_lifecycle_requires_seed() -> None:
    from perturb_eval.agentic_lifecycle.loop import MockAgentPool, run_agentic_lifecycle
    X, labels, control_mask, target_gene_idx = _seed_fixture()
    with pytest.raises(TypeError):
        run_agentic_lifecycle(  # type: ignore[call-arg]
            task_id="hold_D",
            X=X, labels=labels, control_mask=control_mask,
            target_gene_idx=target_gene_idx, held_out="D",
            agent_pool=MockAgentPool(seed=0), max_rounds=1,
            dataset="adamson_full",
        )


@pytest.mark.unit
def test_execute_trainer_requires_seed() -> None:
    from perturb_eval.agentic_lifecycle.trainer_exec import execute_trainer
    from perturb_eval.backbones import build_backbone
    X, labels, control_mask, target_gene_idx = _seed_fixture()
    with pytest.raises(TypeError):
        execute_trainer(  # type: ignore[call-arg]
            backbone=build_backbone("linear"), X=X, labels=labels,
            control_mask=control_mask, target_gene_idx=target_gene_idx,
            trainer_proposal={"lr": 1e-2, "epochs": 5},
        )


# --- T10 / A4 + D1: held-out target remap raises; tuple targets --------------


def _run_lifecycle(target_gene_idx, held_out="D", backbone="linear", seed=2026):
    from perturb_eval.agentic_lifecycle.loop import MockAgentPool, run_agentic_lifecycle
    X, labels, control_mask, _ = _seed_fixture()
    return run_agentic_lifecycle(
        task_id=f"hold_{held_out}",
        X=X, labels=labels, control_mask=control_mask,
        target_gene_idx=target_gene_idx, held_out=held_out,
        agent_pool=MockAgentPool(seed=0),
        max_rounds=1, backbone_override=backbone,
        validator_threshold_override=0.0,
        seed=seed,
        dataset="adamson_full",
    )


@pytest.mark.unit
def test_missing_held_out_target_raises() -> None:
    """No silent index-0 fallback: a held-out label without a target is an error."""
    _, _, _, target_gene_idx = _seed_fixture()
    without_d = {p: i for p, i in target_gene_idx.items() if p != "D"}
    with pytest.raises(ValueError, match="'D'"):
        _run_lifecycle(without_d, held_out="D")


@pytest.mark.unit
def test_remap_held_out_target_two_tuple_maps_to_two_hvg_columns() -> None:
    from perturb_eval.agentic_lifecycle.loop import _remap_held_out_target
    top_indices = np.asarray([7, 3, 9, 12])
    remapped = _remap_held_out_target(
        {"A": 7, "AB": (9, 3)}, held_out="AB", top_indices=top_indices,
    )
    assert remapped == (2, 1)


@pytest.mark.unit
def test_remap_held_out_target_int_is_one_tuple() -> None:
    from perturb_eval.agentic_lifecycle.loop import _remap_held_out_target
    top_indices = np.asarray([7, 3, 9, 12])
    assert _remap_held_out_target({"A": 12}, held_out="A", top_indices=top_indices) == (3,)
    assert _remap_held_out_target({"A": (12,)}, held_out="A", top_indices=top_indices) == (3,)


@pytest.mark.unit
def test_remap_held_out_target_outside_hvg_subset_raises() -> None:
    """Any target gene of the held-out perturbation dropped from the HVG subset → loud."""
    from perturb_eval.agentic_lifecycle.loop import _remap_held_out_target
    top_indices = np.asarray([7, 3, 9, 12])
    with pytest.raises(ValueError, match=r"'AB'.*\b44\b"):
        _remap_held_out_target(
            {"AB": (9, 44)}, held_out="AB", top_indices=top_indices,
        )
    with pytest.raises(ValueError, match=r"'A'.*\b44\b"):
        _remap_held_out_target({"A": 44}, held_out="A", top_indices=top_indices)


@pytest.mark.unit
def test_remap_held_out_target_missing_label_raises() -> None:
    from perturb_eval.agentic_lifecycle.loop import _remap_held_out_target
    with pytest.raises(ValueError, match="'Z'"):
        _remap_held_out_target({"A": 7}, held_out="Z", top_indices=np.asarray([7]))


@pytest.mark.unit
@pytest.mark.parametrize("backbone", ["linear", "mlp"])
def test_one_tuple_targets_match_int_targets_exactly(backbone: str) -> None:
    """A 1-tuple must be byte-identical to today's int path (D1: singletons are 1-tuples)."""
    _, _, _, target_gene_idx = _seed_fixture()
    as_tuples = {p: (i,) for p, i in target_gene_idx.items()}
    run_int = _run_lifecycle(target_gene_idx, backbone=backbone)
    run_tup = _run_lifecycle(as_tuples, backbone=backbone)
    assert np.isfinite(run_int.final_msd_topk)
    assert run_tup.final_msd_topk == run_int.final_msd_topk


# --- T12 / D4: model_id + source on every LifecycleStep ----------------------


class _StubTransport:
    """Client stub serving minimal valid proposals from pool model ``x/y``
    (A2-1: a stated confidence; A2-6: an on-menu Architect backbone)."""

    def chat_json(self, *, role, task_id, round_index, prompt, seed, dataset):  # noqa: ARG002
        from perturb_eval.llm.openrouter_client import ChatResult
        return ChatResult(content={"confidence": 0.5, "backbone": "linear"}, model_id="x/y")


class _RateLimitedClient:
    def chat_json(self, *, role, task_id, round_index, prompt, seed, dataset):  # noqa: ARG002
        from perturb_eval.llm.openrouter_client import RateLimitedError
        raise RateLimitedError("no models available (all cooling)")


class _TypeErrorClient:
    def chat_json(self, *, role, task_id, round_index, prompt, seed, dataset):  # noqa: ARG002
        raise TypeError("programming error inside the client")


def _llm_pool(client, tmp_path):
    from perturb_eval.agentic_lifecycle.llm_agent_pool import LLMAgentPool
    return LLMAgentPool(client=client, cache_dir=tmp_path)


@pytest.mark.unit
def test_lifecycle_step_defaults_model_id_none_source_llm() -> None:
    step = LifecycleStep(
        round_index=0, agent_name="Trainer", proposal_content={}, rationale="",
        llm_confidence=0.5, execution_artifact_path=None, wall_time_sec=0.0,
        succeeded=True,
    )
    assert step.model_id is None
    assert step.source == "llm"


@pytest.mark.unit
def test_loop_records_serving_model_id_and_source_llm(tmp_path) -> None:
    run = _run_with_seed(2026, pool=_llm_pool(_StubTransport(), tmp_path))
    assert len(run.steps) == 5
    for step in run.steps:
        assert step.model_id == "x/y", step
        assert step.source == "llm", step


@pytest.mark.unit
def test_loop_records_fallback_with_schema_default_content(tmp_path) -> None:
    from perturb_eval.agentic_lifecycle.proposal_schema import schema_defaults

    run = _run_with_seed(2026, pool=_llm_pool(_RateLimitedClient(), tmp_path))
    assert len(run.steps) == 5
    for step in run.steps:
        assert step.source == "fallback", step
        assert step.model_id is None, step
        # A2-1/A2-6: the optional schema defaults only; no imputed confidence
        # and no defaulted Architect backbone.
        assert step.proposal_content == schema_defaults(step.agent_name)
        assert step.llm_confidence is None


@pytest.mark.unit
def test_loop_propagates_programming_error_from_client(tmp_path) -> None:
    with pytest.raises(TypeError):
        _run_with_seed(2026, pool=_llm_pool(_TypeErrorClient(), tmp_path))


@pytest.mark.unit
def test_mock_pool_steps_are_source_mock_not_llm() -> None:
    run = _run_with_seed(2026)  # _SeedRecordingPool -> MockAgentPool
    assert run.steps
    for step in run.steps:
        assert step.source == "mock", step
        assert step.model_id is None, step


@pytest.mark.unit
def test_loop_rejects_pool_output_without_source() -> None:
    from perturb_eval.agentic_lifecycle.loop import MockAgentPool

    class _NoSourcePool(MockAgentPool):
        def propose(self, role, round_index, task_id, context, *, seed, dataset):
            out = super().propose(role, round_index, task_id, context, seed=seed, dataset=dataset)
            out.pop("source", None)
            return out

    with pytest.raises(KeyError):
        _run_with_seed(2026, pool=_NoSourcePool(seed=0))


@pytest.mark.unit
def test_loop_rejects_unknown_source_literal() -> None:
    from perturb_eval.agentic_lifecycle.loop import MockAgentPool

    class _BadSourcePool(MockAgentPool):
        def propose(self, role, round_index, task_id, context, *, seed, dataset):
            out = super().propose(role, round_index, task_id, context, seed=seed, dataset=dataset)
            return {**out, "source": "llm-ish"}

    with pytest.raises(ValueError):
        _run_with_seed(2026, pool=_BadSourcePool(seed=0))


@pytest.mark.unit
def test_lifecycle_run_jsonl_round_trips_model_id_and_source(tmp_path) -> None:
    import json
    from dataclasses import asdict

    llm_run = _run_with_seed(2026, pool=_llm_pool(_StubTransport(), tmp_path / "a"))
    fb_run = _run_with_seed(2026, pool=_llm_pool(_RateLimitedClient(), tmp_path / "b"))
    path = tmp_path / "runs.jsonl"
    path.write_text("".join(json.dumps(asdict(r)) + "\n" for r in (llm_run, fb_run)))
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    for run, row in zip((llm_run, fb_run), rows):
        back = tuple(LifecycleStep(**s) for s in row["steps"])
        assert [(s.model_id, s.source) for s in back] == [
            (s.model_id, s.source) for s in run.steps
        ]
    assert {s["source"] for s in rows[0]["steps"]} == {"llm"}
    assert {s["model_id"] for s in rows[0]["steps"]} == {"x/y"}
    assert {s["source"] for s in rows[1]["steps"]} == {"fallback"}
    assert {s["model_id"] for s in rows[1]["steps"]} == {None}
