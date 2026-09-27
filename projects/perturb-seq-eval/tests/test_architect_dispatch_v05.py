"""v0.5.0 — Architect dispatch must now carry the full config, not just backbone."""

from __future__ import annotations

import pytest

from perturb_eval.agentic_lifecycle.architect_dispatch import (
    dispatch_architect,
    resolve_architect_config,
)


class TestResolveArchitectConfig:
    def test_returns_config_dict_from_full_proposal(self) -> None:
        proposal = {
            "backbone": "mlp",
            "hvg_count": 1000,
            "learning_rate": 5e-3,
            "ridge_lambda": 0.5,
            "epochs": 60,
            "n_agents": 5,
            "n_rounds": 3,
        }
        cfg = resolve_architect_config(proposal)
        assert cfg["backbone"] == "mlp"
        assert cfg["hvg_count"] == 1000
        assert cfg["learning_rate"] == 5e-3
        assert cfg["ridge_lambda"] == 0.5
        assert cfg["epochs"] == 60

    def test_defaults_fill_missing_keys(self) -> None:
        cfg = resolve_architect_config({"backbone": "linear"})
        assert cfg["backbone"] == "linear"
        assert cfg["hvg_count"] in {500, 1000, 2000, 5000}
        assert cfg["learning_rate"] > 0

    def test_alias_scgpt_to_scgpt_small(self) -> None:
        # C-TORCH-3: without torch, scgpt_small silently resolves to linear;
        # skip visibly rather than pass on the wrong backbone.
        pytest.importorskip("torch")
        cfg = resolve_architect_config({"backbone": "scgpt"})
        assert cfg["backbone"] == "scgpt_small"

    def test_unknown_backbone_falls_back_to_linear(self) -> None:
        cfg = resolve_architect_config({"backbone": "gpt4"})
        assert cfg["backbone"] == "linear"

    def test_applies_validator_critique_delta(self) -> None:
        proposal = {"backbone": "linear", "learning_rate": 1e-2}
        critique_delta = {"backbone": "mlp", "learning_rate": 1e-4}
        cfg = resolve_architect_config(proposal, critique_delta=critique_delta)
        assert cfg["backbone"] == "mlp"
        assert cfg["learning_rate"] == 1e-4

    def test_critique_delta_does_not_override_illegal_backbone(self) -> None:
        proposal = {"backbone": "linear"}
        # Validator tries to steer to a backbone we don't have
        cfg = resolve_architect_config(proposal, critique_delta={"backbone": "exotic"})
        assert cfg["backbone"] in {"linear", "mlp", "scgpt_small"}


class TestDispatchArchitectBackwardCompat:
    """The existing loop.py unpacks (backbone, name); keep that contract."""

    def test_returns_tuple_of_backbone_and_name(self) -> None:
        bb, name = dispatch_architect({"backbone": "linear"})
        assert name == "linear"
        assert bb is not None


# --------------------------------------------------------------------------- C-TORCH-2
# Known-but-unavailable backbone raises; unknown name keeps the documented
# ``linear`` fallback. Torch-independent: ``available_backbones`` is patched.
def _without_scgpt(monkeypatch) -> None:
    from perturb_eval.agentic_lifecycle import architect_dispatch as ad

    monkeypatch.setattr(ad, "available_backbones", lambda: ("linear", "mlp"))


class TestBackboneUnavailable:
    def test_unknown_backbone_still_falls_back_to_linear(self, monkeypatch) -> None:
        from perturb_eval.agentic_lifecycle.architect_dispatch import _canonical_backbone

        _without_scgpt(monkeypatch)
        assert _canonical_backbone("gpt4") == "linear"

    @pytest.mark.parametrize("name", ["scgpt_small", "scgpt", "SCGPT_Whole_Human"])
    def test_known_but_unavailable_raises(self, monkeypatch, name: str) -> None:
        from perturb_eval.agentic_lifecycle.architect_dispatch import (
            BackboneUnavailableError,
            _canonical_backbone,
        )

        _without_scgpt(monkeypatch)
        with pytest.raises(BackboneUnavailableError, match="scgpt_small"):
            _canonical_backbone(name)

    def test_error_is_runtime_error(self) -> None:
        from perturb_eval.agentic_lifecycle.architect_dispatch import BackboneUnavailableError

        assert issubclass(BackboneUnavailableError, RuntimeError)

    def test_resolve_config_raises_via_critique_delta(self, monkeypatch) -> None:
        from perturb_eval.agentic_lifecycle.architect_dispatch import BackboneUnavailableError

        _without_scgpt(monkeypatch)
        with pytest.raises(BackboneUnavailableError):
            resolve_architect_config({"backbone": "linear"}, critique_delta={"backbone": "scgpt"})

    def test_surfaces_through_lifecycle_record(self, monkeypatch) -> None:
        """C-TORCH-2(a): the raise is not swallowed between _canonical_backbone
        and the sweep's record function (loop.py → v05_sweep.lifecycle_record)."""
        import numpy as np

        from perturb_eval.agentic_lifecycle.architect_dispatch import BackboneUnavailableError
        from perturb_eval.agentic_lifecycle.loop import MockAgentPool
        from perturb_eval.experiments.v05_sweep import lifecycle_record

        _without_scgpt(monkeypatch)
        labels = np.repeat(np.array(["CTRL", "TFA", "TFB"]), 4)
        X = np.zeros((12, 5), dtype=np.float64)
        X[:, 0] = np.where(labels == "TFA", 0.0, 3.0)
        X[:, 1] = np.where(labels == "TFB", 0.0, 3.0)
        X[:, 2] = np.arange(12) % 3
        ds = {
            "X": X,
            "labels": labels,
            "control_mask": labels == "CTRL",
            "target_gene_idx": {"TFA": (0,), "TFB": (1,)},
        }
        with pytest.raises(BackboneUnavailableError, match="scgpt_small"):
            lifecycle_record(
                task="TFA", dataset_name="t", ds=ds, seed=0,
                pool=MockAgentPool(seed=0), backbone_override="scgpt_small",
            )

    def test_trainer_path_raises_not_records(self, monkeypatch) -> None:
        """Trainer path (heldout.iter_trainer_records): a known-but-unavailable
        backbone raises instead of becoming a per-cell ``error`` record."""
        from perturb_eval.agentic_lifecycle.architect_dispatch import BackboneUnavailableError
        from perturb_eval.experiments import heldout

        monkeypatch.setattr(heldout, "available_backbones", lambda: ("linear", "mlp"))
        import numpy as np

        labels = np.repeat(np.array(["CTRL", "TFA", "TFB"]), 4)
        X = np.zeros((12, 5), dtype=np.float64)
        X[:, 0] = np.where(labels == "TFA", 0.0, 3.0)
        X[:, 1] = np.where(labels == "TFB", 0.0, 3.0)
        X[:, 2] = np.arange(12) % 3
        ds = {
            "X": X, "labels": labels, "control_mask": labels == "CTRL",
            "target_gene_idx": {"TFA": (0,), "TFB": (1,)}, "hvg_n_top": 3,
        }
        with pytest.raises(BackboneUnavailableError):
            list(heldout.iter_trainer_records(
                dataset_name="t", ds=ds, tasks=["TFA"], backbones=("scgpt_small",),
                r_sweep=(1,), seeds=(0,),
            ))

    def test_trainer_path_unknown_task_raises(self) -> None:
        """No silent ``continue`` for a task outside target_gene_idx."""
        import numpy as np

        from perturb_eval.experiments.heldout import iter_trainer_records

        labels = np.array(["CTRL", "CTRL", "TFA", "TFA"])
        ds = {"X": np.zeros((4, 3)), "labels": labels, "control_mask": labels == "CTRL",
              "target_gene_idx": {"TFA": (0,)}}
        with pytest.raises(ValueError, match="NOPE"):
            list(iter_trainer_records(
                dataset_name="t", ds=ds, tasks=["NOPE"], backbones=("linear",),
                r_sweep=(1,), seeds=(0,),
            ))
