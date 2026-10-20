"""The pre-registered unparseable-compound exclusion — principal's ruling 2026-09-14.

8 of 6,810 compounds (0.117%) in the audited 2015 snapshot carry InChI strings the
pinned RDKit refuses. The ruling was to exclude them **recorded by ID**, and the
design consequence is that the roster must be CLOSED: a list that can silently
grow when something new breaks, or silently rot when the toolchain improves, is not
a pre-registration but a place to hide data loss.

Tests are pinned to literal IDs and literal counts, not to relations derived from
the function's own output. That is the defect mutation testing found in the
halt-rule suite, where the whole simulation could be replaced by a constant.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from chipsim.harmonize.ids import (
    CanonicalizationError,
    add_canonical_identity_excluding,
    load_preregistered_exclusions,
)

ROSTER = Path(__file__).resolve().parents[1] / "configs" / "unparseable_compounds.yaml"

# Aspirin — parses cleanly on the pinned toolchain.
GOOD = "InChI=1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)"
BAD = "InChI=1S/NOT-A-REAL-STRUCTURE"


def _frame(rows: list[tuple[str, str]]) -> pd.DataFrame:
    return pd.DataFrame([{"drugbank_id": i, "inchi": s} for i, s in rows])


# --- the real roster, pinned so it cannot drift unnoticed ---------------------


def test_the_shipped_roster_is_exactly_the_eight_adjudicated_compounds() -> None:
    """Pinned by ID. The roster is a pre-registration, so a change is a decision.

    If this test fails, someone altered an adjudicated exclusion list — which is a
    change to what the study's cohort IS, and it needs the principal, not a commit.
    """
    assert load_preregistered_exclusions(ROSTER) == {
        "DB01929",
        "DB02177",
        "DB02223",
        "DB02377",
        "DB02912",
        "DB03245",
        "DB03304",
        "DB03907",
    }


def test_the_roster_records_its_own_provenance() -> None:
    """A roster of RDKit refusals is only meaningful against a stated RDKit.

    Unpin the toolchain and the list must be re-derived, so the version it was
    determined against is part of the artifact rather than folk memory.
    """
    import yaml

    doc = yaml.safe_load(ROSTER.read_text(encoding="utf-8"))
    prov = doc["provenance"]
    assert prov["rdkit_version"] == "2026.3.5"
    assert prov["source_commit"] == "3e87872db5fca5ac427ce27464ab945c0ceb4ec6"
    # The count is asserted against the LIST, never against a stored duplicate.
    # An earlier draft carried `excluded_count: 8` in the YAML, which S6 rejected
    # as a bare numeric — and S6 was right for a second reason: a stored count can
    # drift from the list it counts.
    assert len(doc["compounds"]) == 8
    assert "provenance" in doc and "reason" in doc


# --- the closed-roster property, which is the whole design -------------------


def test_a_listed_failure_is_excluded_and_returned_not_dropped() -> None:
    """The kept frame loses it; the excluded frame carries it WITH its reason."""
    df = _frame([("DB01929", BAD), ("DB90945", GOOD)])
    kept, excluded = add_canonical_identity_excluding(df, preregistered={"DB01929"})

    assert list(kept["drugbank_id"]) == ["DB90945"]
    assert kept["canonical_inchikey"].notna().all()
    assert list(excluded["drugbank_id"]) == ["DB01929"]
    # The reason is its OWN categorical value, per the CTO's binding ruling: a
    # parse failure is a fact about our tooling, `unknown` is a fact about the
    # evidence, and folding one into the other would corrupt the three-way P-gp
    # label whose whole content is that distinction.
    assert excluded["exclusion_reason"].iloc[0] == "unparseable_inchi"
    assert excluded["exclusion_reason"].iloc[0] != "unknown"
    # The free-text detail lives in its own column so the code stays categorical.
    assert "InChI" in excluded["exclusion_detail"].iloc[0]


def test_an_UNLISTED_failure_raises_rather_than_growing_the_roster() -> None:
    """A ninth failure is new information, not an entry to append.

    This is the guard that keeps the exclusion a pre-registration. Without it the
    roster absorbs every future breakage and the recorded 0.117% quietly becomes
    whatever the data happens to do.
    """
    df = _frame([("DB99999", BAD), ("DB90945", GOOD)])
    with pytest.raises(CanonicalizationError, match="NOT in the pre-registered"):
        add_canonical_identity_excluding(df, preregistered={"DB01929"})


def test_a_listed_compound_that_now_PARSES_raises_as_stale() -> None:
    """The other direction, and it is the one people forget.

    If a listed compound canonicalizes, the snapshot or the RDKit pin moved.
    Continuing would over-exclude a compound the toolchain can now handle — data
    loss that looks like compliance.
    """
    df = _frame([("DB01929", GOOD), ("DB90945", GOOD)])
    with pytest.raises(CanonicalizationError, match="now parse successfully"):
        add_canonical_identity_excluding(df, preregistered={"DB01929"})


def test_a_listed_compound_absent_from_the_frame_is_not_an_error() -> None:
    """Upstream filters legitimately remove rows; that is not roster staleness."""
    df = _frame([("DB90945", GOOD)])
    kept, excluded = add_canonical_identity_excluding(df, preregistered={"DB01929"})
    assert len(kept) == 1
    assert excluded.empty


def test_returns_a_TUPLE_so_the_exclusion_cannot_be_ignored() -> None:
    """The exclusion is visible in the TYPE, not in a docstring.

    A caller writing `df = f(...)` gets a tuple and breaks loudly downstream,
    rather than silently proceeding on a frame whose dropped rows they never saw.
    """
    out = add_canonical_identity_excluding(_frame([("DB90945", GOOD)]), preregistered=set())
    assert isinstance(out, tuple) and len(out) == 2
    assert isinstance(out[0], pd.DataFrame) and isinstance(out[1], pd.DataFrame)


def test_empty_frame_returns_two_empty_frames() -> None:
    df = pd.DataFrame({"drugbank_id": pd.Series(dtype=str), "inchi": pd.Series(dtype=str)})
    kept, excluded = add_canonical_identity_excluding(df, preregistered=set())
    assert kept.empty and excluded.empty
    assert "canonical_inchikey" in kept.columns


def test_no_inchi_column_raises() -> None:
    with pytest.raises(ValueError, match="no `inchi` column"):
        add_canonical_identity_excluding(
            pd.DataFrame({"drugbank_id": ["DB90945"]}), preregistered=set()
        )


# --- the loader: an unreadable roster must never read as "nothing excluded" ---


def test_a_missing_roster_raises_rather_than_excluding_nothing() -> None:
    """Absence is not consent — the house rule, applied to the roster itself.

    Returning an empty set for a missing file would make every real failure look
    like an unlisted defect, and the pipeline would refuse for the wrong reason.
    """
    with pytest.raises(OSError):
        load_preregistered_exclusions(Path("/nonexistent/roster.yaml"))


@pytest.mark.parametrize(
    "body",
    ["[]", "just-a-string", "provenance: {}\n"],
    ids=["a-list", "a-scalar", "mapping-without-compounds"],
)
def test_a_malformed_roster_raises(tmp_path: Path, body: str) -> None:
    p = tmp_path / "roster.yaml"
    p.write_text(body, encoding="utf-8")
    with pytest.raises(ValueError, match="exclusion roster|must be a list"):
        load_preregistered_exclusions(p)


def test_a_roster_whose_compounds_key_is_not_a_list_raises(tmp_path: Path) -> None:
    """TypeError, not ValueError — a wrong TYPE is not a wrong value.

    The distinction is not pedantry here: a caller catching ValueError to handle a
    malformed roster would otherwise also swallow a plain programming error in the
    file's shape. Ruff's TRY004 flagged it and it was right.
    """
    p = tmp_path / "roster.yaml"
    p.write_text("compounds: DB01929\n", encoding="utf-8")
    with pytest.raises(TypeError, match="must be a list"):
        load_preregistered_exclusions(p)
