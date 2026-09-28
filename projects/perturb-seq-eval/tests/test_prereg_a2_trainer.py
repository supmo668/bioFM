"""Amendment 2 (PREREGISTRATION.md, prereg_version v0.6.0-a3): trainer-side rules.

* A2-4 — N is removed from the trainer sweep; the H1/H2 oracle is the best over
  the distinct backbone x R configurations actually run, and the distinct count
  plus the seeds are stated (``heldout.trainer_grid``), never assumed.
* A2-5 — the 20 evaluation genes are selected ONCE per task on the dataset's full
  post-QC gene axis (convention-2 ranking), force-included in the model's feature
  set, and carried on every trainer record.
* A2-7 — text only; the one code property the amended text names (the per-pool
  total is checked by an explicit ``raise``, not ``assert``) is pinned here.

Fixture: a small deterministic in-memory ``ds`` (no random draws). 4 groups x 8
cells (``ctrl``, ``A``, ``B``, ``C``); 30 genes, values already in log space.

* genes 0, 1, 2 — targets of A, B, C (2.0 everywhere, 0.0 in their own cells);
* gene 3 — 1.0 everywhere, 4.0 in ``A`` cells: the largest |shift| for A, and
  CONSTANT on A's training cells, so a train-only HVG ranking never picks it;
* genes 4..29 — a parity pattern of amplitude 0.05*j in every group (training
  variance grows with j) plus a shift of 0.01*j in ``A`` cells only.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import numpy as np
import pytest

from perturb_eval.backbones import BackboneTrainConfig
from perturb_eval.data import hvg
from perturb_eval.experiments import heldout

N_PER = 8
N_GENES = 30
GROUPS = ("ctrl", "A", "B", "C")


def _ds() -> dict:
    labels = np.repeat(np.array(GROUPS), N_PER)
    n = len(labels)
    X = np.zeros((n, N_GENES), dtype=np.float32)
    for col, grp in ((0, "A"), (1, "B"), (2, "C")):
        X[:, col] = np.where(labels == grp, 0.0, 2.0)
    X[:, 3] = np.where(labels == "A", 4.0, 1.0)
    parity = (np.arange(n) % 2).astype(np.float32)
    for j in range(4, N_GENES):
        X[:, j] = parity * 0.05 * j + np.where(labels == "A", 0.01 * j, 0.0)
    return {
        "X": X,
        "labels": labels,
        "control_mask": labels == "ctrl",
        "target_gene_idx": {"A": 0, "B": 1, "C": 2},
        "gene_names": tuple(f"G{j}" for j in range(N_GENES)),
        "hvg_n_top": 3,
    }


def _full_axis_top20(ds: dict, held: str) -> list[int]:
    """Convention 2 written out independently: |mean(held) - mean(ctrl)| on ALL genes."""
    X = np.asarray(ds["X"], dtype=np.float64)
    truth = X[ds["labels"] == held].mean(axis=0) - X[ds["control_mask"]].mean(axis=0)
    return [int(i) for i in np.argsort(-np.abs(truth), kind="stable")[:20]]


# ---------------------------------------------------------------------------
# A2-5: one gene universe for the top-20 DEGs
# ---------------------------------------------------------------------------


class TestA25EvalGenesOnFullAxis:
    def test_top_deg_columns_ranks_full_gene_axis(self) -> None:
        ds = _ds()
        got = hvg.top_deg_columns(ds["X"], ds["labels"], ds["control_mask"], "A")
        assert [int(i) for i in got] == _full_axis_top20(ds, "A")
        assert len(got) == 20 and hvg.N_EVAL_DEGS == 20
        # Gene 3 is A's largest shift, and the target gene 0 is next.
        assert int(got[0]) == 3 and int(got[1]) == 0

    def test_task_eval_genes_are_independent_of_the_hvg_count(self) -> None:
        ds = _ds()
        want = _full_axis_top20(ds, "A")
        for n_hvg in (3, 10, 30):
            sel = heldout.select_for_task(ds, "A", n_hvg=n_hvg)
            view = heldout.build_view(ds, "A", sel)
            assert [int(i) for i in view.eval_genes] == want
            # The eval columns map back to exactly those full-axis genes.
            assert [int(sel.indices[c]) for c in view.eval_cols] == want

    def test_eval_genes_are_force_included_in_the_feature_set(self) -> None:
        ds = _ds()
        sel = heldout.select_for_task(ds, "A", n_hvg=3)
        # Gene 3 has zero training variance: only force-inclusion can put it in.
        assert 3 in set(sel.indices.tolist())
        assert set(_full_axis_top20(ds, "A")) <= set(sel.indices.tolist())
        # Targets stay forced in as before (convention 1).
        assert {0, 1, 2} <= set(sel.indices.tolist())

    def test_msd_is_scored_on_the_task_eval_genes(self, monkeypatch) -> None:
        ds = _ds()
        seen: list[np.ndarray] = []
        original = heldout.mean_squared_deviation

        def spy(pred, truth, top_k):
            seen.append(np.asarray(top_k))
            return original(pred, truth, top_k)

        monkeypatch.setattr(heldout, "mean_squared_deviation", spy)
        sel = heldout.select_for_task(ds, "A", n_hvg=3)
        view = heldout.build_view(ds, "A", sel)
        heldout.fit_and_score(view, "linear", BackboneTrainConfig(seed=0))
        assert len(seen) == 1
        assert [int(sel.indices[c]) for c in seen[0]] == _full_axis_top20(ds, "A")

    def test_trainer_records_carry_the_task_eval_gene_list(self) -> None:
        ds = _ds()
        recs = list(
            heldout.iter_trainer_records(
                dataset_name="toy",
                ds=ds,
                tasks=["A", "B"],
                backbones=("linear",),
                r_sweep=(1,),
                seeds=(0,),
            )
        )
        assert len(recs) == 2
        for r in recs:
            want = _full_axis_top20(ds, r["task"])
            assert r["eval_gene_idx"] == want
            assert r["eval_genes"] == [f"G{i}" for i in want]
            assert r["n_eval_genes"] == 20

    def test_build_view_refuses_a_selection_missing_an_eval_gene(self) -> None:
        ds = _ds()
        # A selection built WITHOUT the eval genes (targets only) must not be
        # silently scored on a narrower gene set.
        bare = hvg.select_hvg_train_only(ds["X"], ds["labels"] != "A", 3, force_include=[0, 1, 2])
        with pytest.raises(ValueError, match="evaluation gene"):
            heldout.build_view(ds, "A", bare)


# ---------------------------------------------------------------------------
# A2-4: N removed; distinct configurations counted and stated
# ---------------------------------------------------------------------------


class TestA24GridWithoutN:
    def test_iter_trainer_records_has_no_n_axis(self) -> None:
        params = inspect.signature(heldout.iter_trainer_records).parameters
        assert "n_sweep" not in params
        assert {"backbones", "r_sweep", "seeds"} <= set(params)

    def test_records_are_backbone_x_r_x_seed_and_carry_no_n(self) -> None:
        ds = _ds()
        recs = list(
            heldout.iter_trainer_records(
                dataset_name="toy",
                ds=ds,
                tasks=["A", "B"],
                backbones=("linear", "mlp"),
                r_sweep=(1, 2),
                seeds=(0, 1),
            )
        )
        assert len(recs) == 2 * 2 * 2 * 2
        assert all("N" not in r for r in recs)
        cells = {(r["task"], r["backbone"], r["R"], r["seed"]) for r in recs}
        assert len(cells) == len(recs)

    def test_linear_is_r_and_seed_invariant_and_mlp_is_not(self) -> None:
        """Pins the fact trainer_grid's distinct count relies on."""
        ds = _ds()
        recs = list(
            heldout.iter_trainer_records(
                dataset_name="toy",
                ds=ds,
                tasks=["A"],
                backbones=("linear", "mlp"),
                r_sweep=(1, 3),
                seeds=(0, 1),
            )
        )
        lin = {r["msd_topk"] for r in recs if r["backbone"] == "linear"}
        mlp = {(r["R"], r["seed"]): r["msd_topk"] for r in recs if r["backbone"] == "mlp"}
        assert len(lin) == 1
        assert len(set(mlp.values())) == len(mlp) == 4
        assert heldout.R_SEED_INVARIANT_BACKBONES == frozenset({"linear"})

    def test_trainer_grid_states_distinct_count_and_seeds(self) -> None:
        grid = heldout.trainer_grid(
            backbones=("linear", "mlp", "scgpt_small"),
            r_sweep=(1, 2, 3),
            seeds=(2026, 2027, 2028),
        )
        assert grid == {
            "backbones": ["linear", "mlp", "scgpt_small"],
            "r_sweep": [1, 2, 3],
            "seeds": [2026, 2027, 2028],
            "n_records_per_task": 27,
            "n_distinct_per_task": 19,
            "distinct_by_backbone": {"linear": 1, "mlp": 9, "scgpt_small": 9},
            "r_seed_invariant_backbones": ["linear"],
        }

    def test_trainer_grid_rejects_an_n_axis(self) -> None:
        with pytest.raises(TypeError):
            heldout.trainer_grid(  # type: ignore[call-arg]
                backbones=("linear",), n_sweep=(3, 5), r_sweep=(1,), seeds=(0,)
            )


# ---------------------------------------------------------------------------
# A2-7: text only — the per-pool total check is an explicit raise
# ---------------------------------------------------------------------------


def test_a27_task_count_check_is_an_explicit_raise_not_assert() -> None:
    from perturb_eval.experiments import v05_tasks

    tree = ast.parse(Path(v05_tasks.__file__).read_text(encoding="utf-8"))
    assert not any(isinstance(n, ast.Assert) for n in ast.walk(tree))
    check = next(
        n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_check_counts"
    )
    assert any(isinstance(n, ast.Raise) for n in ast.walk(check))
