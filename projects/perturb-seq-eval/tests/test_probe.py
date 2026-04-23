"""Unit tests for probe.py."""

from __future__ import annotations

import pytest

from perturb_eval.probe import ProbeSignature, preflight, signature_from_round


@pytest.mark.unit
def test_signature_shape(easy_round) -> None:  # noqa: ANN001
    sig = signature_from_round(easy_round)
    assert isinstance(sig, ProbeSignature)
    v = sig.as_vector()
    assert len(v) == 4
    assert all(isinstance(x, float) for x in v)


@pytest.mark.unit
def test_hard_round_has_higher_csd(easy_round, hard_round) -> None:  # noqa: ANN001
    easy_sig = signature_from_round(easy_round)
    hard_sig = signature_from_round(hard_round)
    assert hard_sig.csd > easy_sig.csd


@pytest.mark.unit
def test_preflight_executes_callable(easy_round) -> None:  # noqa: ANN001
    sig = preflight(lambda: easy_round)
    assert sig.mean_conf == pytest.approx(sum(easy_round.confidences) / 5)


@pytest.mark.unit
def test_preflight_rejects_non_round_zero(hard_round) -> None:  # noqa: ANN001
    from dataclasses import replace

    r1 = replace(hard_round, round_index=1)
    with pytest.raises(ValueError):
        preflight(lambda: r1)
