"""Unit tests for the biology tool belts."""

from __future__ import annotations

import pytest

from cellforge.tools import (
    BioFMCatalog,
    LiteratureTool,
    OmicsTool,
    PathwayTool,
    TrainerTool,
)


@pytest.mark.unit
class TestOmicsTool:
    def test_fetch_returns_deterministic_id(self) -> None:
        t = OmicsTool()
        assert t.fetch("scRNA-seq", "GSK3B") == "CXG::scRNA-seq::GSK3B"

    def test_qc_produces_valid_report(self) -> None:
        report = OmicsTool().qc("dataset_x")
        assert report.n_cells > 0
        assert 0 <= report.doublet_rate <= 1
        assert report.dataset_id == "dataset_x"


@pytest.mark.unit
class TestLiteratureTool:
    def test_known_gene_hits_pathways(self) -> None:
        mech = LiteratureTool().mechanism("gsk3b kd")
        assert "Wnt/beta-catenin" in mech["pathways"]

    def test_unknown_returns_unknown(self) -> None:
        mech = LiteratureTool().mechanism("made_up_drug")
        assert mech["pathways"] == ["unknown"]

    def test_search_returns_requested_hits(self) -> None:
        hits = LiteratureTool().search("GSK3B", max_hits=3)
        assert len(hits) == 3


@pytest.mark.unit
class TestBioFMCatalog:
    def test_scrna_has_scgpt(self) -> None:
        sugg = BioFMCatalog().suggest("scRNA-seq")
        assert any(s.name == "scGPT" for s in sugg)

    def test_unknown_modality_empty(self) -> None:
        assert BioFMCatalog().suggest("lidar") == []


@pytest.mark.unit
class TestTrainerTool:
    def test_big_dataset_smaller_batch(self) -> None:
        recipe = TrainerTool().build(n_cells=500_000, backbone="scGPT", budget_seconds=120)
        assert recipe.batch_size == 64
        assert recipe.grad_accum == 2

    def test_small_dataset_defaults(self) -> None:
        recipe = TrainerTool().build(n_cells=5_000, backbone="scGPT", budget_seconds=120)
        assert recipe.batch_size == 128
        assert recipe.grad_accum == 1


@pytest.mark.unit
class TestPathwayTool:
    def test_perfect_overlap_scores_one(self) -> None:
        r = PathwayTool().validate(["A", "B"], ["C"], ["A", "B"], ["C"])
        assert r.deg_overlap_at_k == 1.0
        assert r.held_out_auroc > 0.75

    def test_negative_control_always_chance(self) -> None:
        r = PathwayTool().validate([], [], [], [])
        assert r.negative_control_auroc == 0.5
