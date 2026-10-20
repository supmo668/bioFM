"""S13 (r2.37) — the θ-priors TEMPLATE, and the S6 invariant it must not break.

S13 as first written (r2.36) targeted `configs/theta_priors.yaml` — the exact path S6's
done-condition asserts does NOT exist, enforced by `test_s6_human_owned_configs_are_absent`, green
at the time. Implementing it as written would have turned a Global Constraint's guard red. Ruled
(c): the scaffold lives outside `configs/`, absence stays the enforcement mechanism, and S13's
done-condition gained a fourth clause asserting that invariant HERE — at the task that could break
it, not only at S6's own test.

That fourth clause is the point of this file. A guard that only lives at the task it protects is a
guard nobody runs when a different task breaks the thing.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCAFFOLD = PROJECT_ROOT / "configs" / "templates" / "theta_priors.scaffold.yaml"

#: A&D §1 row-S5. Exactly these, no more: an extra field is a biological claim nobody sourced,
#: and a missing one silently drops a parameter the ODE core needs.
DECLARED_FIELDS = frozenset(
    {"flow_ul_min", "membrane_um", "porosity", "strain_pct", "area_mm2", "coating"}
)


@pytest.fixture
def scaffold() -> dict:
    return yaml.safe_load(SCAFFOLD.read_text())["theta"]


def test_s13_the_scaffold_parses():
    """Done-when clause 1."""
    assert isinstance(yaml.safe_load(SCAFFOLD.read_text()), dict)


def test_s13_declares_exactly_the_six_fields(scaffold):
    """Done-when clause 2 — EQUALITY, not containment.

    A superset means someone added a parameter without sourcing it; a subset means the ODE core
    will look for a θ the template never offered. Both are silent until much later.
    """
    assert set(scaffold) == DECLARED_FIELDS


def test_s13_every_field_starts_null_and_assumed(scaffold):
    """Done-when clause 3.

    `assumed: true` is the STARTING state (A&D §1.2), scaffolded up front rather than retrofitted
    once values arrive — the retrofit is where a field quietly keeps `assumed: false` it never
    earned.
    """
    for name, field in scaffold.items():
        assert field["value"] is None, f"{name} carries a value; T20 enters values, not S13"
        assert field["citation"] is None, f"{name} carries a citation; that is T20's to record"
        assert field["assumed"] is True, f"{name} does not start assumed"


def test_s13_declares_a_unit_for_every_field(scaffold):
    """Units are SCHEMA, which Global Constraint 1 explicitly permits the agent to write:
    *"The agent writes the schema and the validator that rejects an unsourced entry."*

    `coating` is categorical rather than numeric, and its unit says so, so an empty value cannot be
    misread as a missing number.
    """
    for name, field in scaffold.items():
        assert isinstance(field["unit"], str) and field["unit"], f"{name} has no unit"


def test_s13_does_NOT_create_the_human_owned_artifact():
    """Done-when clause 4 — the S6 invariant, asserted at the task that could break it.

    S6's own test already asserts this. It is repeated here because S13 is the task that would
    violate it, and a guard living only at the task it protects is not run when a DIFFERENT task
    does the damage. That is the shape r2.36's first defect had.
    """
    assert not (PROJECT_ROOT / "configs" / "theta_priors.yaml").exists(), (
        "configs/theta_priors.yaml exists — S13 scaffolds a TEMPLATE outside configs/; "
        "materialising it is T20's, and no agent performs that copy"
    )


def test_s13_scaffold_is_not_inside_configs_proper():
    """The ruling itself, pinned. If the template ever moves INTO `configs/`, S6's absence guard
    stops covering the path that matters and option (c) has been silently undone."""
    assert SCAFFOLD.parent.name == "templates"
    assert SCAFFOLD.parent.parent.name == "configs"
