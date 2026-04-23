"""Unit tests for verifiers."""

from __future__ import annotations

import math

import pytest

from ttc.scoring import (
    GCContentVerifier,
    KmerConsensusVerifier,
    _clean,
    _kmers,
    build_verifier,
)


@pytest.mark.unit
class TestHelpers:
    def test_clean_filters_non_bases(self) -> None:
        # Both lowercase 'n' and uppercase 'N' are valid IUPAC unknowns.
        assert _clean("acgt XyZ nN") == "ACGTNN"

    def test_clean_empty_returns_empty(self) -> None:
        assert _clean("1234") == ""

    def test_kmers_window(self) -> None:
        assert _kmers("ACGTA", 3) == ["ACG", "CGT", "GTA"]

    def test_kmers_too_short(self) -> None:
        assert _kmers("AC", 3) == []


@pytest.mark.unit
class TestGCContentVerifier:
    def test_balanced_is_max_score(self) -> None:
        v = GCContentVerifier(target=0.5, tolerance=0.1)
        assert v("ACGTACGT") == pytest.approx(1.0)

    def test_pure_at_is_worst(self) -> None:
        v = GCContentVerifier(target=0.5, tolerance=0.1)
        assert v("AAAATTTT") < 0

    def test_pure_gc_is_worst(self) -> None:
        v = GCContentVerifier(target=0.5, tolerance=0.1)
        assert v("GGCCGGCC") < 0

    def test_empty_is_minus_inf(self) -> None:
        v = GCContentVerifier()
        assert v("") == -math.inf


@pytest.mark.unit
class TestKmerConsensusVerifier:
    def test_fit_returns_self(self, tiny_pool: list[str]) -> None:
        v = KmerConsensusVerifier(k=3).fit(tiny_pool)
        assert isinstance(v, KmerConsensusVerifier)

    def test_majority_scores_higher(self, tiny_pool: list[str]) -> None:
        v = KmerConsensusVerifier(k=3).fit(tiny_pool)
        majority = v("ACGTACGT")
        outlier = v("AAAAGGGG")
        assert majority > outlier

    def test_empty_reference_returns_zero(self) -> None:
        v = KmerConsensusVerifier(k=3)
        assert v("ACGTACGT") == 0.0


@pytest.mark.unit
class TestBuildVerifier:
    def test_builds_gc(self) -> None:
        v = build_verifier("gc_content")
        assert v.name == "gc_content"

    def test_unknown_raises(self) -> None:
        with pytest.raises(KeyError):
            build_verifier("not_a_real_verifier")
