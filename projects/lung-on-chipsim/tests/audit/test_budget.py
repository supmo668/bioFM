"""R9 pre-emptive budget tests — pinned to hand-computed dollars.

Every numeric assertion is arithmetic done independently of the implementation, so
a constant-returning version fails. That is the defect mutation testing found in
the halt-rule suite, where `evaluate_halt`'s entire simulation could be replaced
by a constant with all 60 tests passing.
"""

from __future__ import annotations

import pytest

from chipsim.audit.budget import BudgetBreach, authorize_batch, project_from_measurement


def test_the_whole_reason_this_exists_slow_batch_one_predicts_the_breach() -> None:
    """The scenario the principal accepted the risk on, caught BEFORE the spend.

    1,240 complexes at the planned 90/GPU-h costs $26.87 and fits. At 80/GPU-h it
    costs $30.22 and breaches. If batch 1 reveals 80, this must halt while 1,140
    complexes are still undispatched — not after.

    Hand-computed: 100 complexes in 1.25 GPU-h = 80/h, spent 1.25 x 1.95 = $2.4375.
    Remaining 1,140 / 80 = 14.25 h x 1.95 = $27.7875. Total $30.225.
    """
    p = project_from_measurement(complexes_done=100, gpu_hours_used=1.25, complexes_remaining=1140)
    assert p.measured_rate == pytest.approx(80.0)
    assert p.spent_usd == pytest.approx(2.4375)
    assert p.projected_total_usd == pytest.approx(30.225, abs=1e-3)
    assert p.breaches is True

    with pytest.raises(BudgetBreach, match="refusing to dispatch"):
        authorize_batch(p, batch_complexes=200)


def test_throughput_at_the_planned_rate_fits_with_the_stated_headroom() -> None:
    """At the ruled 90/GPU-h the plan costs $26.87 — pinned, not derived.

    100 in 1.1111 h = 90/h; 1,140 / 90 = 12.667 h; total 13.778 h x 1.95 = $26.87.
    """
    p = project_from_measurement(
        complexes_done=100, gpu_hours_used=100 / 90, complexes_remaining=1140
    )
    assert p.measured_rate == pytest.approx(90.0)
    assert p.projected_total_usd == pytest.approx(26.87, abs=0.01)
    assert p.breaches is False
    authorize_batch(p, batch_complexes=200)  # must not raise


def test_the_projection_uses_MEASURED_throughput_not_the_plan() -> None:
    """Projecting at the planned rate would re-assert the assumption under test.

    Same remaining work, two different measured rates, must give different totals.
    If they agree, the measurement is being ignored.
    """
    slow = project_from_measurement(
        complexes_done=100, gpu_hours_used=1.25, complexes_remaining=1140
    )
    fast = project_from_measurement(
        complexes_done=100, gpu_hours_used=1.0, complexes_remaining=1140
    )
    assert slow.projected_total_usd > fast.projected_total_usd + 3.0
    assert slow.rate_ratio == pytest.approx(80 / 90, abs=1e-3)
    assert fast.rate_ratio == pytest.approx(100 / 90, abs=1e-3)


def test_a_healthy_spent_so_far_does_not_authorise_a_breaching_projection() -> None:
    """The defect a spent-only ledger has: every step affordable, the total not.

    $2.44 spent against a $30 ceiling looks entirely healthy. The projection is
    what refuses, and it refuses while the money is still unspent.
    """
    p = project_from_measurement(complexes_done=100, gpu_hours_used=1.25, complexes_remaining=1140)
    assert p.spent_usd < 3.0
    assert p.ceiling_usd - p.spent_usd > 27.0, "spend-so-far looks healthy"
    assert p.breaches is True, "and the projection still refuses"


def test_breaches_is_derived_so_it_cannot_contradict_its_own_numbers() -> None:
    """A stored verdict can disagree with the figures printed to justify it.

    That is exactly what HaltDecision allowed before `proceed` became a property —
    proceed=True beside worst_power=0.11, with its own reason() announcing PROCEED.
    """
    p = project_from_measurement(complexes_done=100, gpu_hours_used=1.25, complexes_remaining=1140)
    assert p.breaches == (p.projected_total_usd > p.ceiling_usd)
    assert "HALT" in p.reason()
    assert "80.0 complexes/GPU-h" in p.reason()
    assert "30.22" in p.reason() or "30.23" in p.reason()


def test_reason_always_names_measured_rate_against_plan() -> None:
    """The 90 assumption must be auditable against what actually happened."""
    p = project_from_measurement(
        complexes_done=100, gpu_hours_used=100 / 90, complexes_remaining=1140
    )
    r = p.reason()
    assert "planned 90.0" in r
    assert "REALISED throughput" in r
    assert "CONTINUE" in r


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        ({"complexes_done": 0}, "at least one completed complex"),
        ({"complexes_remaining": -5}, "negative"),
        ({"gpu_hours_used": 0.0}, "gpu_hours_used"),
        ({"gpu_hours_used": float("nan")}, "gpu_hours_used"),
        ({"gpu_hours_used": float("inf")}, "gpu_hours_used"),
        ({"planned_rate": float("nan")}, "planned_rate"),
        ({"ceiling_usd": 0.0}, "ceiling_usd"),
        ({"ceiling_usd": float("nan")}, "ceiling_usd"),
        ({"usd_per_gpu_hour": -1.0}, "usd_per_gpu_hour"),
    ],
)
def test_refuses_input_it_cannot_project_from(kwargs, match) -> None:
    """NaN is in every guard deliberately: `nan > ceiling` is False.

    A NaN projection would pass the breach check and authorise the spend — the
    failure mode that has already appeared twice in this package.
    """
    base = {"complexes_done": 100, "gpu_hours_used": 1.25, "complexes_remaining": 1140}
    with pytest.raises(ValueError, match=match):
        project_from_measurement(**{**base, **kwargs})


def test_zero_remaining_work_projects_exactly_what_was_spent() -> None:
    """Boundary: nothing left to dispatch means the projection is the spend."""
    p = project_from_measurement(complexes_done=1240, gpu_hours_used=13.78, complexes_remaining=0)
    assert p.projected_total_usd == pytest.approx(p.spent_usd)
    assert p.projected_total_usd == pytest.approx(26.87, abs=0.02)
    assert p.breaches is False


def test_authorize_refuses_an_empty_batch() -> None:
    p = project_from_measurement(
        complexes_done=100, gpu_hours_used=100 / 90, complexes_remaining=1140
    )
    with pytest.raises(ValueError, match="nothing to authorize"):
        authorize_batch(p, batch_complexes=0)
