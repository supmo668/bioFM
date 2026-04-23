"""Unit tests for each of the 5 agents."""

from __future__ import annotations

import pytest

from cellforge.agents import (
    ArchitectAgent,
    DataCuratorAgent,
    LiteratureAgent,
    TrainerAgent,
    ValidatorAgent,
    build_default_team,
)
from cellforge.problem import Context, Modality, Problem, Proposal


@pytest.fixture
def problem() -> Problem:
    return Problem(perturbation="GSK3B knockout", modality=Modality.SCRNA)


@pytest.fixture
def ctx(problem: Problem) -> Context:
    return Context(problem=problem)


@pytest.mark.unit
class TestDefaultTeam:
    def test_team_has_five_agents(self) -> None:
        team = build_default_team()
        assert len(team) == 5

    def test_team_roles_are_distinct(self) -> None:
        names = {a.name for a in build_default_team()}
        assert names == {"DataCurator", "Literature", "Architect", "Trainer", "Validator"}


@pytest.mark.unit
class TestDataCurator:
    def test_proposal_includes_qc_metrics(self, ctx: Context) -> None:
        prop = DataCuratorAgent().propose(ctx)
        assert prop.agent == "DataCurator"
        assert "n_cells" in prop.content
        assert prop.content["passes_qc"] is True
        assert "omics.qc" in prop.tools_used

    def test_vetoes_oversized_architecture(self, ctx: Context) -> None:
        curator = DataCuratorAgent()
        big = Proposal(
            agent="Architect",
            content={"d_model": 4096},
            rationale="too big",
            confidence=0.9,
        )
        critique = curator.critique(ctx, big)
        assert critique.severity >= 0.5


@pytest.mark.unit
class TestLiterature:
    def test_known_perturbation_has_pathways(self, ctx: Context) -> None:
        prop = LiteratureAgent().propose(ctx)
        assert "Wnt/beta-catenin" in prop.content["pathways"]
        assert prop.confidence > 0.5

    def test_unknown_perturbation_has_low_confidence(self) -> None:
        prob = Problem(perturbation="unknown_compound_XYZ", modality=Modality.SCRNA)
        prop = LiteratureAgent().propose(Context(problem=prob))
        assert prop.confidence < 0.5


@pytest.mark.unit
class TestArchitect:
    def test_default_scrna_backbone_is_scgpt(self, ctx: Context) -> None:
        prop = ArchitectAgent().propose(ctx)
        assert prop.content["backbone"] == "scGPT"
        assert "head" in prop.content

    def test_unsupported_modality_returns_none_backbone(self) -> None:
        class FakeCatalog:
            name = "fake"
            def suggest(self, modality: str) -> list:  # noqa: ARG002
                return []
        agent = ArchitectAgent(catalog=FakeCatalog())  # type: ignore[arg-type]
        prop = agent.propose(Context(problem=Problem(perturbation="x", modality=Modality.SCRNA)))
        assert prop.content["backbone"] is None
        assert prop.confidence < 0.2


@pytest.mark.unit
class TestTrainer:
    def test_recipe_has_all_fields(self, ctx: Context) -> None:
        prop = TrainerAgent().propose(ctx)
        for key in ("optimizer", "lr", "epochs", "batch_size", "cv_split"):
            assert key in prop.content

    def test_reads_prior_proposals(self, problem: Problem) -> None:
        curator_prop = Proposal(
            agent="DataCurator", content={"n_cells": 250_000}, rationale="", confidence=0.9
        )
        ctx = Context(problem=problem, prior_proposals=(curator_prop,))
        prop = TrainerAgent().propose(ctx)
        # With 250k cells, trainer should downgrade batch_size.
        assert prop.content["batch_size"] == 64


@pytest.mark.unit
class TestValidator:
    def test_validator_consumes_literature_expected_genes(self, problem: Problem) -> None:
        lit_prop = Proposal(
            agent="Literature",
            content={"expected_up": ["AXIN2", "MYC"], "expected_down": ["CTNNB1"]},
            rationale="",
            confidence=0.8,
        )
        ctx = Context(problem=problem, prior_proposals=(lit_prop,))
        prop = ValidatorAgent().propose(ctx)
        assert set(prop.content["checked_genes"]) == {"AXIN2", "MYC", "CTNNB1"}
        assert prop.content["deg_overlap_at_k"] > 0.9
