"""Monotonicity tests over the ODE core.

Skipped in M0 slice 1: the solver does not exist until M1.
"""

import pytest

pytestmark = pytest.mark.skip(reason="M0 slice 3 — splits/ODE not yet built")


def test_exposure_is_monotone_in_dose():
    """Predicted exposure is non-decreasing in administered dose."""
    raise AssertionError("not implemented until M1")
