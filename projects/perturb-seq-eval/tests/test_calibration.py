"""Unit tests for calibration.py."""

from __future__ import annotations

import pytest

from perturb_eval.calibration import TDICoeffs, fit_tdi_coefficients


@pytest.mark.unit
def test_empty_input_returns_defaults() -> None:
    c = fit_tdi_coefficients([])
    assert isinstance(c, TDICoeffs)
    assert c.alpha + c.beta + c.gamma + c.delta == pytest.approx(1.0)


@pytest.mark.unit
def test_coefficients_sum_to_one(converging_run, thrashing_run) -> None:  # noqa: ANN001
    labelled = [(converging_run, 0.0), (thrashing_run, 1.0)] * 4
    c = fit_tdi_coefficients(labelled)
    s = c.alpha + c.beta + c.gamma + c.delta
    assert s == pytest.approx(1.0, abs=1e-6)


@pytest.mark.unit
def test_coefficients_nonnegative(converging_run, thrashing_run) -> None:  # noqa: ANN001
    labelled = [(converging_run, 0.0), (thrashing_run, 1.0)] * 4
    c = fit_tdi_coefficients(labelled)
    for v in c.as_dict().values():
        assert v >= 0
