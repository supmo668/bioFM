"""Amendment 2, A2-5 (lifecycle side): one gene universe for the top-20 DEGs.

The task's 20 evaluation genes are selected ONCE on the dataset's full gene axis
(:func:`perturb_eval.data.hvg.top_deg_columns`), force-included in every round's
feature set, and the Validator scores MSD on exactly those genes. The run record
carries the list, identical to the trainer record's for the same task.
"""

from __future__ import annotations

import numpy as np
import pytest

from perturb_eval.agentic_lifecycle.loop import MockAgentPool
from perturb_eval.data import hvg as hvg_mod


def _ds(n_genes: int = 60) -> dict:
    rng = np.random.default_rng(3)
    labels = np.asarray(["CTRL"] * 40 + ["A"] * 40 + ["B"] * 40 + ["C"] * 40)
    X = rng.standard_normal((160, n_genes)) * 0.3 + 2.0
    X[40:80, 5] -= 2.0
    X[80:120, 10] -= 2.0
    X[120:160, 15] -= 2.0
    # Low-variance genes that still move under C: without force-include they
    # would fall outside a small HVG cut.
    X[:, 40:50] = 2.0 + rng.standard_normal((160, 10)) * 0.01
    X[120:160, 40:50] += 0.05
    return {
        "X": X, "labels": labels, "control_mask": labels == "CTRL",
        "target_gene_idx": {"A": (5,), "B": (10,), "C": (15,)},
        "gene_names": np.asarray([f"G{i}" for i in range(n_genes)]),
    }


class _SmallHvgPool(MockAgentPool):
    """DataCurator asks for 3 HVG, so the eval genes can only be present if forced."""

    def propose(self, role, round_index, task_id, context, *, seed, dataset):
        out = super().propose(role, round_index, task_id, context, seed=seed, dataset=dataset)
        if role == "DataCurator":
            out = {**out, "content": {**out["content"], "n_top_hvg": 3}}
        return out


def _run(ds, pool=None, **kw):
    from perturb_eval.agentic_lifecycle.loop import run_agentic_lifecycle

    return run_agentic_lifecycle(
        task_id="hold_C", X=ds["X"], labels=ds["labels"], control_mask=ds["control_mask"],
        target_gene_idx=ds["target_gene_idx"], held_out="C",
        agent_pool=pool or _SmallHvgPool(seed=0), seed=0, dataset="adamson_full",
        backbone_override="linear", **kw,
    )


def test_run_carries_the_full_axis_eval_genes() -> None:
    ds = _ds()
    run = _run(ds)
    expected = hvg_mod.top_deg_columns(ds["X"], ds["labels"], ds["control_mask"], "C")
    assert list(run.eval_gene_idx) == [int(i) for i in expected]
    assert run.n_eval_genes == 20


def test_eval_genes_selected_once_and_force_included_every_round(monkeypatch) -> None:
    ds = _ds()
    top_calls: list[str] = []
    real_top = hvg_mod.top_deg_columns

    def spy_top(X, labels, cm, held, *a, **k):
        top_calls.append(held)
        return real_top(X, labels, cm, held, *a, **k)

    monkeypatch.setattr(hvg_mod, "top_deg_columns", spy_top)
    sels = []
    real_select = hvg_mod.select_hvg_train_only

    def spy_select(X, train_mask, n_top, **kw):
        sel = real_select(X, train_mask, n_top, **kw)
        sels.append(({int(i) for i in kw.get("force_include", ())}, sel))
        return sel

    monkeypatch.setattr(hvg_mod, "select_hvg_train_only", spy_select)
    run = _run(ds)
    assert top_calls == ["C"]  # once per run
    assert len(sels) == 3  # A2-2: three rounds
    evals = set(run.eval_gene_idx)
    for forced, sel in sels:
        assert evals <= forced
        assert {5, 10, 15} <= forced  # targets still forced (convention 1)
        assert evals <= {int(i) for i in sel.indices}
    # hvg_n_forced records the forced columns the variance cut did not pick.
    assert list(run.hvg_n_forced_per_round) == [sel.n_forced for _, sel in sels]
    assert all(n > 0 for n in run.hvg_n_forced_per_round)


def test_validator_scores_on_the_eval_genes(monkeypatch) -> None:
    import perturb_eval.agentic_lifecycle.loop as loop_mod

    ds = _ds()
    seen = []
    real_gate = loop_mod.score_and_gate

    def spy_gate(**kw):
        seen.append(kw)
        return real_gate(**kw)

    monkeypatch.setattr(loop_mod, "score_and_gate", spy_gate)
    sel_indices = []
    real_select = hvg_mod.select_hvg_train_only

    def spy_select(X, train_mask, n_top, **kw):
        sel = real_select(X, train_mask, n_top, **kw)
        sel_indices.append(np.asarray(sel.indices))
        return sel

    monkeypatch.setattr(hvg_mod, "select_hvg_train_only", spy_select)
    run = _run(ds)
    assert len(seen) == 3
    for kw, idx in zip(seen, sel_indices):
        cols = np.asarray(kw["eval_cols"])
        # Mapped back to the full axis, the scored columns are the eval genes, in rank order.
        assert [int(i) for i in idx[cols]] == list(run.eval_gene_idx)


def test_score_and_gate_requires_eval_cols_and_scores_on_them() -> None:
    from perturb_eval.agentic_lifecycle.validator_gate import score_and_gate

    class ZeroModel:
        name = "linear"

        def predict_logfc(self, held, tgt, n_genes):
            return np.zeros(n_genes)

    ds = _ds()
    X = ds["X"]
    with pytest.raises(TypeError):
        score_and_gate(backbone=ZeroModel(), X=X, labels=ds["labels"],  # type: ignore[call-arg]
                       control_mask=ds["control_mask"], held_out="C", held_out_target_idx=15)
    cols = np.asarray([40, 41, 3])
    rep = score_and_gate(backbone=ZeroModel(), X=X, labels=ds["labels"],
                         control_mask=ds["control_mask"], held_out="C",
                         held_out_target_idx=15, eval_cols=cols)
    truth = X[ds["labels"] == "C"].mean(0) - X[ds["control_mask"]].mean(0)
    assert rep.msd_topk == pytest.approx(float(np.mean(truth[cols] ** 2)))


def test_trainer_and_lifecycle_records_carry_the_identical_eval_gene_list() -> None:
    from perturb_eval.experiments.heldout import iter_trainer_records
    from perturb_eval.experiments.v05_sweep import lifecycle_record

    ds = _ds()
    trainer = list(iter_trainer_records(dataset_name="adamson_full", ds=ds, tasks=["C"],
                                        backbones=("linear",), r_sweep=(1,), seeds=(0,)))
    life = lifecycle_record(task="C", dataset_name="adamson_full", ds=ds, seed=0,
                            pool=_SmallHvgPool(seed=0), backbone_override="linear")
    assert trainer and "error" not in trainer[0]
    assert life["eval_gene_idx"] == trainer[0]["eval_gene_idx"]
    assert life["n_eval_genes"] == trainer[0]["n_eval_genes"] == 20
    assert life["eval_genes"] == trainer[0]["eval_genes"]
