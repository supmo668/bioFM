"""Schema tests for the five-agent proposal contracts.

The schemas widen the Architect's choice space and give the Validator a
structured critique that feeds back into the next round. A round-tripable
JSON schema is the provenance surface for the paper's §5 freedom analysis.
"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from perturb_eval.agentic_lifecycle.proposal_schema import (
    ArchitectProposal,
    DataCuratorProposal,
    LiteratureProposal,
    StructuredCritique,
    TrainerProposal,
    ValidatorProposal,
    parse_proposal,
)


class TestDataCuratorProposal:
    def test_defaults_are_valid(self) -> None:
        p = DataCuratorProposal(confidence=0.5)
        assert p.hvg_method in {"seurat", "scanpy"}
        assert p.hvg_count in {500, 1000, 2000, 5000}
        assert 0 < p.qc_mito_max <= 100
        assert p.split_strategy in {"per_pert_holdout", "unseen_gene"}
        assert p.batch_correction in {"none", "combat", "harmony"}

    def test_rejects_invalid_hvg_method(self) -> None:
        with pytest.raises(ValueError):
            DataCuratorProposal(confidence=0.5, hvg_method="invalid")  # type: ignore[arg-type]

    def test_rejects_invalid_hvg_count(self) -> None:
        with pytest.raises(ValueError):
            DataCuratorProposal(confidence=0.5, hvg_count=123)  # type: ignore[arg-type]


class TestLiteratureProposal:
    def test_pathway_prior_normalises_gene_keys(self) -> None:
        p = LiteratureProposal(
            confidence=0.5,
            pathway_prior={"TP53": 0.8, "MYC": 0.6},
            ppi_neighbors=["JUN", "FOS"],
            tool_calls=["pubmed", "biogpt"],
        )
        assert p.pathway_prior == {"TP53": 0.8, "MYC": 0.6}

    def test_rejects_weight_outside_unit_interval(self) -> None:
        with pytest.raises(ValueError):
            LiteratureProposal(confidence=0.5, pathway_prior={"X": 1.5})


class TestArchitectProposal:
    def test_full_config_space(self) -> None:
        p = ArchitectProposal(
            confidence=0.5,
            backbone="scgpt_small",
            n_agents=5,
            n_rounds=3,
            hvg_count=2000,
            learning_rate=1e-3,
            ridge_lambda=1.0,
            epochs=40,
        )
        assert p.backbone == "scgpt_small"
        assert p.n_agents == 5

    def test_backbone_restricted_to_known_set(self) -> None:
        with pytest.raises(ValueError):
            ArchitectProposal(confidence=0.5, backbone="gpt4")  # type: ignore[arg-type]

    def test_n_agents_bounds(self) -> None:
        with pytest.raises(ValueError):
            ArchitectProposal(confidence=0.5, backbone="linear", n_agents=1)  # below 2
        with pytest.raises(ValueError):
            ArchitectProposal(confidence=0.5, backbone="linear", n_agents=9)  # above 8

    def test_n_rounds_bounds(self) -> None:
        with pytest.raises(ValueError):
            ArchitectProposal(confidence=0.5, backbone="linear", n_rounds=0)
        with pytest.raises(ValueError):
            ArchitectProposal(confidence=0.5, backbone="linear", n_rounds=6)

    def test_learning_rate_positive(self) -> None:
        with pytest.raises(ValueError):
            ArchitectProposal(confidence=0.5, backbone="linear", learning_rate=0.0)
        with pytest.raises(ValueError):
            ArchitectProposal(confidence=0.5, backbone="linear", learning_rate=-1e-3)


class TestTrainerProposal:
    def test_valid(self) -> None:
        p = TrainerProposal(confidence=0.5, lr=1e-2, epochs=50, ridge_lambda=0.5)
        assert p.lr == 1e-2

    def test_lr_must_be_positive(self) -> None:
        with pytest.raises(ValueError):
            TrainerProposal(confidence=0.5, lr=0.0, epochs=10, ridge_lambda=1.0)


class TestStructuredCritique:
    def test_defaults_empty(self) -> None:
        c = StructuredCritique()
        assert c.which_genes_failed == ()
        assert c.suggested_next_config_delta == {}
        assert c.accept_reason == ""

    def test_delta_round_trip(self) -> None:
        c = StructuredCritique(
            which_genes_failed=("TP53", "MYC"),
            suggested_next_config_delta={"learning_rate": 1e-4, "backbone": "mlp"},
            accept_reason="MSD above threshold",
        )
        assert c.suggested_next_config_delta["learning_rate"] == 1e-4


class TestValidatorProposal:
    def test_threshold_is_required_not_defaulted(self) -> None:
        # Amendment 3 (QG-9): no default -- an unstated threshold is a schema failure.
        with pytest.raises(ValueError):
            ValidatorProposal(confidence=0.5)
        v = ValidatorProposal(confidence=0.5, dynamic_threshold_msd=0.1)
        assert 0.02 <= v.dynamic_threshold_msd <= 0.3

    def test_threshold_clamped(self) -> None:
        with pytest.raises(ValueError):
            ValidatorProposal(confidence=0.5, dynamic_threshold_msd=0.5)  # above clamp
        with pytest.raises(ValueError):
            ValidatorProposal(confidence=0.5, dynamic_threshold_msd=0.01)  # below clamp


class TestParseProposal:
    def test_parses_valid_architect(self) -> None:
        out = parse_proposal("Architect", {"backbone": "linear", "n_agents": 4, "confidence": 0.5})
        assert isinstance(out, ArchitectProposal)
        assert out.backbone == "linear"

    def test_parses_validator_with_critique(self) -> None:
        raw = {
            "confidence": 0.5,
            "dynamic_threshold_msd": 0.1,
            "critique": {
                "which_genes_failed": ["TP53"],
                "suggested_next_config_delta": {"backbone": "mlp"},
                "accept_reason": "",
            },
        }
        out = parse_proposal("Validator", raw)
        assert isinstance(out, ValidatorProposal)
        assert out.critique.which_genes_failed == ("TP53",)

    def test_unknown_role_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_proposal("Unknown", {})

    def test_extra_fields_tolerated(self) -> None:
        # Free-tier LLMs sometimes add commentary fields; we tolerate them.
        out = parse_proposal(
            "DataCurator", {"hvg_method": "seurat", "extra": "hi", "confidence": 0.5}
        )
        assert isinstance(out, DataCuratorProposal)


# --------------------------------------------------------------------------- QG-5
# JSON ``Infinity`` / ``NaN`` and absurd magnitudes (1e308) must be a schema
# failure on every numeric hyper-parameter, not just ``confidence``: otherwise
# they parse, ``resolve_applied_config`` applies them as stated, and the fit
# runs on a non-finite learning rate / ridge λ.
_NUMERIC_FIELDS = [
    ("Architect", "learning_rate"),
    ("Architect", "ridge_lambda"),
    ("Trainer", "lr"),
    ("Trainer", "ridge_lambda"),
    ("DataCurator", "qc_mito_max"),
]
_BAD_NUMBERS = [
    pytest.param(json.loads("Infinity"), id="Infinity"),
    pytest.param(json.loads("-Infinity"), id="-Infinity"),
    pytest.param(json.loads("NaN"), id="NaN"),
    pytest.param(1e308, id="1e308"),
]


class TestNonFiniteHyperparameters:
    @pytest.mark.parametrize("role,field", _NUMERIC_FIELDS)
    @pytest.mark.parametrize("bad", _BAD_NUMBERS)
    def test_non_finite_or_absurd_value_is_schema_failure(self, role, field, bad) -> None:
        base = {"backbone": "linear", "confidence": 0.5}
        with pytest.raises(ValidationError):
            parse_proposal(role, {**base, field: bad})

    @pytest.mark.parametrize("role,field", _NUMERIC_FIELDS)
    @pytest.mark.parametrize("bad", _BAD_NUMBERS)
    def test_pool_takes_the_fallback_path(self, role, field, bad, tmp_path) -> None:
        """Through the real LLMAgentPool: the step is a fallback (run invalid, C-KEY-2),
        and the non-finite value never reaches ``content``."""
        from perturb_eval.agentic_lifecycle.llm_agent_pool import LLMAgentPool
        from perturb_eval.llm.openrouter_client import ChatResult

        class Client:
            def chat_json(self, *, role, task_id, round_index, prompt, seed, dataset):
                return ChatResult(
                    content={"backbone": "linear", "confidence": 0.5, field: bad},
                    model_id="fake/m",
                )

        out = LLMAgentPool(client=Client(), cache_dir=tmp_path).propose(
            role, 0, "t", {}, seed=0, dataset="adamson_full"
        )
        assert out["source"] == "fallback" and out["model_id"] is None
        assert out["content"].get(field) != bad

    def test_epochs_upper_bound(self) -> None:
        with pytest.raises(ValidationError):
            parse_proposal("Trainer", {"confidence": 0.5, "epochs": 10**9})
        with pytest.raises(ValidationError):
            parse_proposal("Architect", {"backbone": "linear", "confidence": 0.5, "epochs": 10**9})

    def test_sane_values_still_parse(self) -> None:
        a = parse_proposal(
            "Architect",
            {"backbone": "linear", "confidence": 0.5, "learning_rate": 1.0, "ridge_lambda": 1e6},
        )
        assert a.learning_rate == 1.0 and a.ridge_lambda == 1e6
        t = parse_proposal("Trainer", {"confidence": 0.5, "lr": 1e-6, "ridge_lambda": 0.0})
        assert t.lr == 1e-6 and t.ridge_lambda == 0.0


class TestQG9ValidatorThresholdRequired:
    """Amendment 3 (QG-9, principal 2026-09-28): an unstated Validator threshold is
    a schema failure, never the old default 0.1 acting as the chosen threshold."""

    def test_missing_threshold_is_a_schema_failure(self) -> None:
        import pytest
        from pydantic import ValidationError

        from perturb_eval.agentic_lifecycle.proposal_schema import parse_proposal

        with pytest.raises(ValidationError):
            parse_proposal("Validator", {"confidence": 0.9, "critique": {}})

    def test_stated_threshold_is_the_recorded_one(self) -> None:
        from perturb_eval.agentic_lifecycle.proposal_schema import parse_proposal

        m = parse_proposal("Validator", {"confidence": 0.9, "dynamic_threshold_msd": 0.25})
        assert m.dynamic_threshold_msd == 0.25 and "dynamic_threshold_msd" in m.model_fields_set

    def test_pool_falls_back_when_threshold_unstated(self, tmp_path) -> None:
        from perturb_eval.agentic_lifecycle.llm_agent_pool import LLMAgentPool
        from perturb_eval.llm.openrouter_client import ChatResult

        class _NoThreshold:
            def chat_json(self, **kw):
                return ChatResult(content={"confidence": 0.9, "critique": {}}, model_id="m")

        pool = LLMAgentPool(client=_NoThreshold(), cache_dir=tmp_path)
        out = pool.propose("Validator", 0, "TFA", {}, seed=0, dataset="adamson_full")
        assert out["source"] != "llm" and out["confidence"] is None
