"""Unit tests for model.py (MockPredictor only — scGPT integration is a smoke stub)."""

from __future__ import annotations

import pytest

from perturb_eval.model import MockPredictor, PredictedResponse


@pytest.mark.unit
def test_mock_predictor_known_gene() -> None:
    p = MockPredictor().predict_response("GSK3B knockout")
    assert isinstance(p, PredictedResponse)
    assert "AXIN2" in p.predicted_up
    assert "CTNNB1" in p.predicted_down
    assert p.confidence > 0.5


@pytest.mark.unit
def test_mock_predictor_unknown_gene_low_confidence() -> None:
    p = MockPredictor().predict_response("made_up_gene_xyz")
    assert p.confidence < 0.5
    assert p.predicted_up == ()
    assert p.predicted_down == ()


@pytest.mark.unit
def test_mock_predictor_deterministic() -> None:
    m = MockPredictor()
    a = m.predict_response("TP53 knockout")
    b = m.predict_response("TP53 knockout")
    assert a == b
