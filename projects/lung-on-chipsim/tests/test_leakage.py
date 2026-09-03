"""Leakage tests — build-plan S4 / A&D §4.4.

Skipped in M0 slice 1: neither the sealed allocation nor the four §1.3 splits
exist until M0 slice 3.

TERMINOLOGY (CONTEXT.md is explicit, and the first draft of this module conflated
them): a **sealed allocation** is the disjoint assignment of every curated chip
record to one of four buckets — it is about record reuse. A **split** is one of the
four §1.3 generalization partitions — it is about chemistry. They are different
invariants and get one test each; CONTEXT.md lists "split" under _Avoid_ for the
allocation precisely to stop this merge.
"""

import pytest

pytestmark = pytest.mark.skip(reason="M0 slice 3 — splits/allocation not yet built")


def test_no_record_appears_in_two_buckets():
    """Sealed allocation: the four buckets are disjoint over curated chip records."""
    raise AssertionError("not implemented until M0 slice 3")


def test_no_scaffold_or_target_leaks_across_a_split():
    """§1.3 splits: no scaffold or target present in train appears in test."""
    raise AssertionError("not implemented until M0 slice 3")
