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
