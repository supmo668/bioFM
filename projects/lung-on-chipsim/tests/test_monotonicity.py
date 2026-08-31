"""Monotonicity tests over the ODE core.

Skipped in M0 slice 1: the solver does not exist until M1.
"""

import pytest

# NOTE: build-plan S4 prescribes the string "M0 slice 3 — splits/ODE not yet built"
# for both this module and test_leakage.py. That reason is accurate for leakage and
# WRONG here — monotonicity waits on the M1 ODE solver, not on the slice-3 splits.
# Using the accurate reason so anyone triaging skips is not misdirected; flagged to
# the CTO as a plan wording defect rather than silently following it.
pytestmark = pytest.mark.skip(reason="M1 — ODE solver not yet built")


def test_exposure_is_monotone_in_dose():
    """Predicted exposure is non-decreasing in administered dose."""
    raise AssertionError("not implemented until M1")
