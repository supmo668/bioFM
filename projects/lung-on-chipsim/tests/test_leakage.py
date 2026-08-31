"""Leakage tests over the four §1.3 generalization splits.

Skipped in M0 slice 1: the splits do not exist until M0 slice 3.
"""

import pytest

pytestmark = pytest.mark.skip(reason="M0 slice 3 — splits/ODE not yet built")


def test_no_record_appears_in_two_buckets():
    """The sealed allocation is disjoint across all four buckets."""
    raise AssertionError("not implemented until M0 slice 3")
