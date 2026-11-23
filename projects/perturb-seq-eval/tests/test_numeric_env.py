"""The numeric-environment record and the fixture note stay consistent with the bounds (HACA-124)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import test_backbones
import test_fill_v060_numbers
from numeric_env import header_line, numeric_environment

NOTE = Path(__file__).parent / "fixtures" / "numeric_environment.json"


@pytest.fixture(scope="module")
def note() -> dict:
    return json.loads(NOTE.read_text())


@pytest.mark.unit
def test_record_names_the_numeric_stack() -> None:
    env = numeric_environment()
    for key in ("machine", "python", "numpy", "scipy", "scikit-learn"):
        assert env[key], key
    assert env["blas"]["blas"]["name"], env["blas"]
    line = header_line()
    assert line.startswith("numeric environment: {")
    assert json.loads(line.split(": ", 1)[1]) == env


@pytest.mark.unit
def test_note_bounds_are_the_test_bounds(note: dict) -> None:
    b = note["bounds"]
    mlp = b["tests/test_backbones.py::test_single_target_regression_pin_within_ulp"]
    assert mlp["max"] == test_backbones.MLP_PIN_MAX_ULP
    summ = b[
        "tests/test_fill_v060_numbers.py::test_landed_analyser_reproduces_the_committed_summary"
    ]
    assert summ["max"] == test_fill_v060_numbers.BLAS_MAX_ULP
    assert summ["paths"] == ["/".join(p) for p in test_fill_v060_numbers.BLAS_ULP_PATHS]


@pytest.mark.unit
def test_every_verified_build_is_within_the_bounds(note: dict) -> None:
    assert note["verified"]
    for env in note["verified"]:
        for key in ("machine", "python", "numpy", "scipy", "scikit-learn", "blas"):
            assert env[key], (env.get("where"), key)
        obs = env["observed"]
        assert obs["linear_pin_ulp"] == 0, env["where"]
        assert obs["mlp_pin_ulp_of_scale"] <= test_backbones.MLP_PIN_MAX_ULP, env["where"]
        assert obs["summary_ulp_per_element"] <= test_fill_v060_numbers.BLAS_MAX_ULP, env["where"]
