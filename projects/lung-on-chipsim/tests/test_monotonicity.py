"""Monotonicity tests over the ODE core.

Skipped in M0 slice 1: the solver does not exist until M1.
"""

import pytest

# The skip names its OWN blocker: the M1 ODE solver, not slice-3 splits.
# RATIFIED as CTO ruling E-3 (dispatch #11) and now specified in build-plan S4 —
# a skip reason that misnames its blocker sends the next reader to the wrong
# milestone.
pytestmark = pytest.mark.skip(reason="M1 — ODE solver not yet built")


def test_exposure_is_monotone_in_dose():
    """Predicted exposure is non-decreasing in administered dose."""
    raise AssertionError("not implemented until M1")
