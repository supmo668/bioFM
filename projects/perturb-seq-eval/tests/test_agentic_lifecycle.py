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
    )
    assert meta["succeeded"] is True
    assert meta["n_train_perts"] == 3
    assert meta["wall_time_sec"] >= 0


@pytest.mark.unit
def test_validator_gate_produces_finite_msd_and_flag() -> None:
    from perturb_eval.agentic_lifecycle.validator_gate import score_and_gate
    from perturb_eval.backbones import BackboneTrainConfig, build_backbone
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
        agent_pool=pool, max_rounds=2,
    )
    assert run.n_rounds <= 2
    assert run.final_msd_topk >= 0.0
    assert run.backbone_used in ("linear", "mlp", "scgpt_small")
    assert len(run.steps) >= 5
