"""T8b (CTO #227): highly-variable genes are ranked on TRAINING cells only.

Property pinned here (not a line): the feature set a model is trained on for a
held-out perturbation must not depend on that perturbation's own cells.

Fixture design (fully deterministic, no random draws). Cells: 10 controls,
10 ``TFA`` cells, 10 ``TFB`` cells. Genes:

* ``TFA`` / ``TFB`` — the perturbation targets (knocked to 0 in their own cells).
* ``GA`` — a NON-target gene with a huge shift only in ``TFA`` cells;
  ``GB`` likewise only in ``TFB`` cells.
* ``M0..M5`` — moderate variance in every group (distinct amplitudes).
* ``L0..L2`` — constant (zero variance).

With ``n = 6``: ranking on ALL cells keeps ``GA`` whichever task is held out;
ranking on training cells drops ``GA`` when ``TFA`` is held out (its column
is constant on the remaining cells) and keeps it when ``TFB`` is held out.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("anndata")
pytest.importorskip("scipy")

GENES = ["TFA", "TFB", "GA", "GB", "M0", "M1", "M2", "M3", "M4", "M5", "L0", "L1", "L2"]
N_PER_GROUP = 10
N_HVG = 6


def _counts() -> tuple[np.ndarray, np.ndarray]:
    """(counts, group) with group in {"CTRL", "TFA", "TFB"}; rows grouped in that order."""
    group = np.repeat(np.array(["CTRL", "TFA", "TFB"]), N_PER_GROUP)
    n = len(group)
    col = {g: i for i, g in enumerate(GENES)}
    X = np.zeros((n, len(GENES)), dtype=np.float32)
    X[:, col["TFA"]] = np.where(group == "TFA", 0.0, 50.0)
    X[:, col["TFB"]] = np.where(group == "TFB", 0.0, 50.0)
    X[:, col["GA"]] = np.where(group == "TFA", 1000.0, 1.0)
    X[:, col["GB"]] = np.where(group == "TFB", 1000.0, 1.0)
    parity = np.arange(n) % 2
    for k in range(6):
        X[:, col[f"M{k}"]] = parity * (k + 2)
    for j in range(3):
        X[:, col[f"L{j}"]] = j + 2
    return X, group


def _log_matrix() -> np.ndarray:
    counts, _ = _counts()
    return np.log1p(counts).astype(np.float64)


def _write_h5ad(path: Path, labels: list[str]) -> None:
    import anndata as ad
    from scipy.sparse import csr_matrix

    counts, _ = _counts()
    adata = ad.AnnData(
        X=csr_matrix(counts),
        obs={"perturbation": np.array(labels)},
        var={"gene_symbol": np.array(GENES)},
    )
    adata.obs["perturbation"] = adata.obs["perturbation"].astype("category")
    adata.write_h5ad(path)


def _write_adamson(path: Path) -> None:
    _, group = _counts()
    raw = {"CTRL": "*", "TFA": "TFA_pDS263", "TFB": "TFB_pDS263"}
    _write_h5ad(path, [raw[g] for g in group])


def _write_norman(path: Path) -> None:
    _, group = _counts()
    raw = {"CTRL": "non-targeting", "TFA": "TFA", "TFB": "TFB"}
    _write_h5ad(path, [raw[g] for g in group])


class _FitRecorder:
    """Spy on LinearBackbone.fit: records the expression matrix each fit sees."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from perturb_eval.backbones.linear import LinearBackbone

        self.expressions: list[np.ndarray] = []
        original = LinearBackbone.fit
        recorder = self

        def spy(self_bb, expression, *args, **kwargs):
            recorder.expressions.append(np.array(expression, copy=True))
            return original(self_bb, expression, *args, **kwargs)

        monkeypatch.setattr(LinearBackbone, "fit", spy)


def _genes_in_fit(expression: np.ndarray, held: str) -> set[str]:
    """Identify each fitted column by matching it to a fixture gene on the training rows."""
    _, group = _counts()
    train_rows = _log_matrix()[group != held]
    assert expression.shape[0] == train_rows.shape[0]
    found: set[str] = set()
    for c in range(expression.shape[1]):
        hits = [
            g for gi, g in enumerate(GENES)
            if np.allclose(expression[:, c], train_rows[:, gi], atol=1e-6)
        ]
        assert len(hits) == 1, f"fitted column {c} matches {hits}"
        found.add(hits[0])
    return found


def _phi():
    from perturb_eval.types import Config

    return Config(n_agents=3, n_rounds=1, backbone="linear")


# --------------------------------------------------------------------------- (a)
class TestTrainOnlyPropertyThroughRealPaths:
    def test_adamson_single_file_grid_cell(self, tmp_path: Path, monkeypatch) -> None:
        from perturb_eval.experiments.e2_adamson import (
            load_adamson_matrix,
            train_grid_cell_adamson,
        )

        path = tmp_path / "adamson.h5ad"
        _write_adamson(path)
        ds = load_adamson_matrix(path, n_top_hvg=N_HVG, max_cells_per_pert=400)
        rec = _FitRecorder(monkeypatch)

        train_grid_cell_adamson(_phi(), "TFA", 0, h5ad_path=path, dataset_cache=ds)
        held_a = _genes_in_fit(rec.expressions[-1], "TFA")
        train_grid_cell_adamson(_phi(), "TFB", 0, h5ad_path=path, dataset_cache=ds)
        held_b = _genes_in_fit(rec.expressions[-1], "TFB")

        assert "GA" not in held_a, f"held-out TFA's own shift leaked into features: {held_a}"
        assert "GA" in held_b
        assert "GB" not in held_b, f"held-out TFB's own shift leaked into features: {held_b}"
        assert "GB" in held_a
        # Targets are always kept (identity from the label, not held-out expression).
        assert {"TFA", "TFB"} <= held_a and {"TFA", "TFB"} <= held_b

    def test_adamson_combined_trainer_sweep(self, tmp_path: Path, monkeypatch) -> None:
        from perturb_eval.experiments.e2_adamson import load_adamson_combined
        from perturb_eval.experiments.heldout import iter_trainer_records

        path = tmp_path / "adamson.h5ad"
        _write_adamson(path)
        ds = load_adamson_combined([path], n_top_hvg=N_HVG, max_cells_per_pert=400)
        rec = _FitRecorder(monkeypatch)
        records = list(iter_trainer_records(
            dataset_name="adamson_full", ds=ds, tasks=["TFA", "TFB"],
            backbones=("linear",), n_sweep=(3,), r_sweep=(1,), seeds=(0,),
        ))
        assert all("error" not in r for r in records), records
        assert "GA" not in _genes_in_fit(rec.expressions[0], "TFA")
        assert "GA" in _genes_in_fit(rec.expressions[1], "TFB")

    def test_norman_trainer_sweep(self, tmp_path: Path, monkeypatch) -> None:
        from perturb_eval.experiments.heldout import iter_trainer_records
        from perturb_eval.experiments.norman import load_norman_matrix

        path = tmp_path / "norman.h5ad"
        _write_norman(path)
        ds = load_norman_matrix(path, n_top_hvg=N_HVG, max_cells_per_pert=400)
        rec = _FitRecorder(monkeypatch)
        records = list(iter_trainer_records(
            dataset_name="norman", ds=ds, tasks=["TFA", "TFB"],
            backbones=("linear",), n_sweep=(3,), r_sweep=(1,), seeds=(0,),
        ))
        assert all("error" not in r for r in records), records
        assert "GA" not in _genes_in_fit(rec.expressions[0], "TFA")
        assert "GA" in _genes_in_fit(rec.expressions[1], "TFB")

    def test_lifecycle_loop(self, monkeypatch) -> None:
        from perturb_eval.agentic_lifecycle.loop import MockAgentPool, run_agentic_lifecycle

        class _SmallHvgPool(MockAgentPool):
            def propose(self, role, round_index, task_id, context, *, seed, dataset):
                out = super().propose(role, round_index, task_id, context, seed=seed, dataset=dataset)
                if role == "DataCurator":
                    out = {**out, "content": {**out["content"], "n_top_hvg": N_HVG}}
                return out

        _, group = _counts()
        X = _log_matrix()
        labels = np.where(group == "CTRL", "CTRL", group)
        targets = {"TFA": (0,), "TFB": (1,)}
        rec = _FitRecorder(monkeypatch)
        for held in ("TFA", "TFB"):
            run_agentic_lifecycle(
                task_id=f"hold_{held}", X=X, labels=labels,
                control_mask=group == "CTRL", target_gene_idx=targets,
                held_out=held, agent_pool=_SmallHvgPool(seed=0), seed=0,
                max_rounds=1, backbone_override="linear",
                dataset="adamson_full",
            )
        assert "GA" not in _genes_in_fit(rec.expressions[0], "TFA")
        assert "GA" in _genes_in_fit(rec.expressions[1], "TFB")


# --------------------------------------------------------------------------- (b)
class TestVarianceIsTrainingRowsOnly:
    def test_helper_gene_var_equals_training_rows_var(self) -> None:
        from perturb_eval.data.hvg import select_hvg_train_only

        X = _log_matrix()
        _, group = _counts()
        mask = group != "TFA"
        sel = select_hvg_train_only(X, mask, N_HVG, force_include=(0, 1))
        assert np.array_equal(sel.gene_var, X[mask].var(axis=0))
        assert sel.mode == "train_only"
        assert list(sel.indices) == sorted(set(sel.indices.tolist()))
        assert {0, 1} <= set(sel.indices.tolist())
        assert len(sel.indices) == sel.n_by_variance + sel.n_forced

    def test_real_path_passes_training_mask(self, tmp_path: Path, monkeypatch) -> None:
        from perturb_eval.data import hvg
        from perturb_eval.experiments.e2_adamson import (
            load_adamson_matrix,
            train_grid_cell_adamson,
        )

        path = tmp_path / "adamson.h5ad"
        _write_adamson(path)
        ds = load_adamson_matrix(path, n_top_hvg=N_HVG, max_cells_per_pert=400)
        seen: list[tuple[np.ndarray, object]] = []
        original = hvg.select_hvg_train_only

        def spy(X, train_mask, n, **kw):
            sel = original(X, train_mask, n, **kw)
            seen.append((np.asarray(train_mask).copy(), sel))
            return sel

        monkeypatch.setattr(hvg, "select_hvg_train_only", spy)
        train_grid_cell_adamson(_phi(), "TFA", 0, h5ad_path=path, dataset_cache=ds)
        assert len(seen) == 1
        mask, sel = seen[0]
        np.testing.assert_array_equal(mask, ds["labels"] != "TFA")
        assert np.array_equal(sel.gene_var, ds["X"][mask].astype(np.float64).var(axis=0))


# --------------------------------------------------------------------------- (c)
class _SelectSpy:
    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from perturb_eval.data import hvg

        self.calls = 0
        original = hvg.select_hvg_train_only

        def spy(*a, **kw):
            self.calls += 1
            return original(*a, **kw)

        monkeypatch.setattr(hvg, "select_hvg_train_only", spy)


class TestEveryPathRoutesThroughHelper:
    @pytest.mark.parametrize("dataset", ["adamson_full", "norman"])
    def test_trainer_sweep_selects_once_per_held_out_task(
        self, dataset: str, tmp_path: Path, monkeypatch
    ) -> None:
        from perturb_eval.experiments.e2_adamson import load_adamson_combined
        from perturb_eval.experiments.heldout import iter_trainer_records
        from perturb_eval.experiments.norman import load_norman_matrix

        path = tmp_path / f"{dataset}.h5ad"
        if dataset == "norman":
            _write_norman(path)
            ds = load_norman_matrix(path, n_top_hvg=N_HVG, max_cells_per_pert=400)
        else:
            _write_adamson(path)
            ds = load_adamson_combined([path], n_top_hvg=N_HVG, max_cells_per_pert=400)
        spy = _SelectSpy(monkeypatch)
        records = list(iter_trainer_records(
            dataset_name=dataset, ds=ds, tasks=["TFA", "TFB"],
            backbones=("linear", "mlp"), n_sweep=(3, 5), r_sweep=(1,), seeds=(0, 1),
        ))
        assert len(records) == 2 * 2 * 2 * 2
        assert spy.calls == 2  # once per held-out task, not per cell
        for r in records:
            assert r["hvg_mode"] == "train_only"
            assert r["hvg_n"] == 7 and r["hvg_n_forced"] == 1
            assert isinstance(r["n_params"], int) and r["n_params"] > 0

    def test_adamson_grid_cell_selects_once_per_call(self, tmp_path: Path, monkeypatch) -> None:
        from perturb_eval.experiments.e2_adamson import (
            load_adamson_matrix,
            train_grid_cell_adamson,
        )

        path = tmp_path / "adamson.h5ad"
        _write_adamson(path)
        ds = load_adamson_matrix(path, n_top_hvg=N_HVG, max_cells_per_pert=400)
        spy = _SelectSpy(monkeypatch)
        res = train_grid_cell_adamson(_phi(), "TFA", 0, h5ad_path=path, dataset_cache=ds)
        assert spy.calls == 1
        assert res.hvg_mode == "train_only"
        assert res.hvg_n == 7 and res.hvg_n_forced == 1
        assert res.n_params is not None and res.n_params > 0

    def test_lifecycle_selects_once_per_round(self, monkeypatch) -> None:
        from perturb_eval.agentic_lifecycle.loop import MockAgentPool, run_agentic_lifecycle

        _, group = _counts()
        spy = _SelectSpy(monkeypatch)
        run = run_agentic_lifecycle(
            task_id="hold_TFA", X=_log_matrix(), labels=group,
            control_mask=group == "CTRL", target_gene_idx={"TFA": (0,), "TFB": (1,)},
            held_out="TFA", agent_pool=MockAgentPool(seed=0), seed=0,
            max_rounds=2, backbone_override="linear", validator_threshold_override=-1.0,
            dataset="adamson_full",
        )
        assert run.n_rounds == 2
        assert spy.calls == 2
        assert run.hvg_mode == "train_only"
        assert len(run.hvg_n_per_round) == 2


# --------------------------------------------------------------------------- (d)
class TestCombinedLoaderResolvesTargets:
    def test_target_missing_from_shared_vocab_raises(self, tmp_path: Path) -> None:
        import anndata as ad
        from scipy.sparse import csr_matrix

        from perturb_eval.experiments.e2_adamson import load_adamson_combined

        counts, group = _counts()
        # File 1 has TFB in its vocabulary; file 2 renames that column, so
        # TFB is absent from the shared (intersected) vocabulary.
        p1, p2 = tmp_path / "one.h5ad", tmp_path / "two.h5ad"
        _write_adamson(p1)
        genes2 = list(GENES)
        genes2[1] = "OTHER"
        keep = group != "TFB"
        raw = np.where(group == "CTRL", "*", np.char.add(group, "_pDS263"))[keep]
        adata = ad.AnnData(
            X=csr_matrix(counts[keep]),
            obs={"perturbation": raw},
            var={"gene_symbol": np.array(genes2)},
        )
        adata.obs["perturbation"] = adata.obs["perturbation"].astype("category")
        adata.write_h5ad(p2)

        with pytest.raises(ValueError, match="TFB"):
            load_adamson_combined([p1, p2], n_top_hvg=N_HVG, max_cells_per_pert=400)

    def test_combined_targets_are_tuples_over_full_vocab(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.e2_adamson import load_adamson_combined

        path = tmp_path / "adamson.h5ad"
        _write_adamson(path)
        ds = load_adamson_combined([path], n_top_hvg=N_HVG, max_cells_per_pert=400)
        col = {g: i for i, g in enumerate(ds["gene_names"])}
        assert ds["target_gene_idx"] == {"TFA": (col["TFA"],), "TFB": (col["TFB"],)}
        # The loader keeps the full shared vocabulary: no feature selection.
        assert set(ds["gene_names"]) == set(GENES)
