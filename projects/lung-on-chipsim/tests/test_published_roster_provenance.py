"""The PUBLISHED roster provenance — the ATC R03 derivation, pinned against the real snapshot.

What this module is for
-----------------------
The methods-note provenance text (evidence ledger §2) publishes a chain:

    every compound in the pinned snapshot carrying an ATC R03 code gives **39 candidates**
    against a pre-registered band of 20-40; **26** carry a resolvable DOI and **13** do not;
    the 26 are the roster.

Until this module existed that whole chain was `cited` to a markdown hand-off file. It is in
fact **mechanically reproducible from the snapshot**, and the most load-bearing part of it —
that every roster key really is one of the mechanically derived candidates — was asserted
nowhere. A roster key outside the R03 pool would make the published provenance false.

WHY THE FIRST TEST IS ABOUT THE INSTRUMENT, NOT THE DATA
---------------------------------------------------------
Deriving this count the obvious way returns **0**, silently and wrongly. `atc_codes` holds a
numpy ndarray per row, so an `isinstance(v, (list, tuple))` check falls through to `str(v)` and
nothing can ever match a code prefix. **0 looked exactly like "this snapshot has no respiratory
drugs."**

That is the same shape as a nine-term ANDed PubMed query returning 0 records: *a 0 from a broken
instrument is not an absence.* So ``test_the_instrument_finds_atc_codes_at_all_before_any_count_
is_trusted`` runs first and asserts the extractor finds codes **somewhere** in the snapshot, and
a negative control asserts a nonsense prefix finds none. Without both, every count below could
be a confident zero.

WHAT IS DERIVED HERE, AND WHAT STAYS CITED — the distinction matters
--------------------------------------------------------------------
Derived (reproducible from the tree):

- 39 candidates carrying an ATC R03 code, and that those are 39 distinct IDENTITIES, not 39 rows;
- every roster key is one of the 39 — zero roster keys outside the mechanical pool;
- 39 - 26 = 13 candidates NOT selected into the roster.

**NOT derived, and not derivable here:** that those 13 lack a *resolvable DOI*. The tree records
which candidates were SELECTED; it does not record why each unselected one was rejected — that
rested on an external literature search whose per-row record died with an account-scoped surface
(see `configs/poc_compounds.yaml`). "13 unselected" and "13 without a resolvable DOI" are the
same SET only because selection was *defined* as "every candidate carrying a resolvable
citation". The numeral coincides; the predicates differ. This module pins the first and makes no
claim about the second.

**If one of these fails, do NOT edit the literal.** It means the snapshot, the ATC data or the
roster changed, and the published provenance changes with it.

Byte availability: the parquet is a build output (`.gitignore: data/processed/**`) on a
MACHINE-LOCAL DVC remote, so CI cannot pull it. Absent bytes SKIP with the reason stated in the
message, never pass. No identifier, accession, name or key is written here or into any failure
message — only counts.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from chipsim.harmonize.roster import load_poc_roster

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_PARQUET = PROJECT_ROOT / "data" / "processed" / "drugbank_compounds.parquet"
TRACKED_ROSTER = PROJECT_ROOT / "configs" / "poc_compounds.yaml"

KEY_COLUMN = "canonical_inchikey"
ATC_COLUMN = "atc_codes"
R03_PREFIX = "R03"

# Derived at 156980e from the pinned snapshot. A failure is a change to what the cohort IS.
PUBLISHED_R03_CANDIDATES = 39
PUBLISHED_ROSTER_SIZE = 26
PUBLISHED_UNSELECTED = 13
PREREGISTERED_BAND = (20, 40)


def snapshot_parquet_path() -> Path:
    """Indirection that keeps the pins FALSIFIABLE — see test_published_pgp_result for why.

    A loader wired to a module constant through a default argument cannot be redirected at a
    doctored copy, and a pin that cannot be pointed at a wrong tree cannot be shown to fail on
    one. This module is deliberately self-contained rather than importing the sibling module's
    loader: a cross-test import would couple two suites' collection order for three lines.
    """
    return SNAPSHOT_PARQUET


def _load_snapshot_or_skip() -> pd.DataFrame:
    path = snapshot_parquet_path()
    if not path.is_file():
        try:
            shown: Path | str = path.relative_to(PROJECT_ROOT)
        except ValueError:
            shown = path
        pytest.skip(
            f"snapshot bytes absent at {shown}: a build output (.gitignore: data/processed/**) "
            "whose bytes live on a MACHINE-LOCAL DVC remote, so CI cannot pull them. This is a "
            "SKIP with a stated reason, not a pass — the published provenance is unverified here."
        )
    frame = pd.read_parquet(path)
    for column in (KEY_COLUMN, ATC_COLUMN):
        assert column in frame.columns, (
            f"the snapshot has no {column!r} column; its columns are {list(frame.columns)}. "
            "Refusing to derive a provenance claim from a column that does not exist."
        )
    return frame


def _atc_codes(value: object) -> list[str]:
    """Normalise one row's ATC cell to a list of upper-case codes.

    Handles the ndarray case EXPLICITLY. Omitting `np.ndarray` here is what made the first
    derivation of this count return a confident 0.
    """
    if value is None:
        return []
    if isinstance(value, (list, tuple, np.ndarray)):
        return [str(item).strip().upper() for item in value if item is not None]
    return [
        part.strip().upper() for part in str(value).replace(";", ",").split(",") if part.strip()
    ]


def _rows_with_prefix(frame: pd.DataFrame, prefix: str) -> pd.Series:
    return frame[ATC_COLUMN].apply(lambda cell: any(c.startswith(prefix) for c in _atc_codes(cell)))


def test_the_instrument_finds_atc_codes_at_all_before_any_count_is_trusted():
    """FIRST, and the reason the rest is readable: a 0 from a broken extractor is not an absence.

    The obvious implementation returns 0 for every prefix because the cells are ndarrays. That 0
    is indistinguishable from "this snapshot contains no respiratory drugs", which is false.
    """
    frame = _load_snapshot_or_skip()
    per_row = frame[ATC_COLUMN].apply(lambda cell: len(_atc_codes(cell)))
    assert int(per_row.sum()) > 0, (
        "the ATC extractor found NO codes anywhere in the snapshot. Every count below would be a "
        "confident zero from a broken instrument — fix the extractor before reading any result."
    )
    assert int((per_row > 0).sum()) > 0


def test_a_nonsense_atc_prefix_finds_nothing():
    """The negative control. Without it, an extractor that matched EVERYTHING would also pass."""
    frame = _load_snapshot_or_skip()
    assert int(_rows_with_prefix(frame, "ZZZ").sum()) == 0


def test_the_r03_prefix_is_a_subset_of_the_broader_R_class():
    """A cheap consistency check on the extractor: R03 rows cannot exceed R rows."""
    frame = _load_snapshot_or_skip()
    r03 = int(_rows_with_prefix(frame, R03_PREFIX).sum())
    r_any = int(_rows_with_prefix(frame, "R").sum())
    assert 0 < r03 <= r_any


def test_the_published_candidate_count_is_derivable_from_the_snapshot():
    """§2's 39, promoted from `cited` to `derived`."""
    frame = _load_snapshot_or_skip()
    assert int(_rows_with_prefix(frame, R03_PREFIX).sum()) == PUBLISHED_R03_CANDIDATES


def test_the_39_candidates_are_39_IDENTITIES_not_39_rows():
    """Same class as flagged-rows-vs-flagged-keys: the count alone does not say the claim.

    If two candidate rows pooled onto one canonical key, "39 candidates" would be a row count
    and the pre-registered band of 20-40 would be counting something other than compounds.
    """
    frame = _load_snapshot_or_skip()
    rows = _rows_with_prefix(frame, R03_PREFIX)
    assert int(rows.sum()) == PUBLISHED_R03_CANDIDATES
    assert int(frame.loc[rows, KEY_COLUMN].nunique()) == PUBLISHED_R03_CANDIDATES


def test_the_candidate_pool_sits_inside_the_preregistered_band():
    low, high = PREREGISTERED_BAND
    assert low <= PUBLISHED_R03_CANDIDATES <= high


def test_EVERY_roster_key_is_one_of_the_mechanically_derived_candidates():
    """THE PROVENANCE CLAIM, and the one thing here that was asserted nowhere.

    The methods text says the roster was selected FROM the ATC R03 pool. A roster key outside
    that pool would make the published provenance false — a curation claim attributed to a
    mechanical derivation that did not produce it.
    """
    frame = _load_snapshot_or_skip()
    candidates = set(frame.loc[_rows_with_prefix(frame, R03_PREFIX), KEY_COLUMN])
    roster = load_poc_roster(TRACKED_ROSTER)
    roster_keys = set(roster[KEY_COLUMN]) if KEY_COLUMN in roster.columns else set(roster.index)

    assert len(roster_keys) == PUBLISHED_ROSTER_SIZE
    outside = roster_keys - candidates
    assert not outside, (
        f"{len(outside)} roster key(s) are NOT in the derived ATC R03 candidate pool, so the "
        "published provenance chain does not hold (keys deliberately not printed)"
    )


def test_the_unselected_count_is_the_arithmetic_complement_and_NOTHING_MORE():
    """13 = 39 - 26 is derived. '13 without a resolvable DOI' is NOT, and is not claimed.

    The tree records which candidates were SELECTED, never why each unselected one was rejected;
    that record died with an account-scoped surface. The two readings of 13 coincide only because
    selection was DEFINED as "carries a resolvable citation" — same numeral, different predicate.

    THE SUBJECT IS ASSERTED BEFORE THE COMPLEMENT, and falsification is why. A set difference is
    insensitive to a roster key LEAVING the pool: drop one roster compound out of the R03 set and
    the pool falls 39->38 while the difference stays 13, because both sides shrink together. The
    first draft of this test asserted only the difference and PASSED on exactly that broken tree.
    So the pool size and the roster size are pinned here too, and the complement is checked
    against them rather than on its own.
    """
    frame = _load_snapshot_or_skip()
    candidates = set(frame.loc[_rows_with_prefix(frame, R03_PREFIX), KEY_COLUMN])
    roster = load_poc_roster(TRACKED_ROSTER)
    roster_keys = set(roster[KEY_COLUMN]) if KEY_COLUMN in roster.columns else set(roster.index)

    assert len(candidates) == PUBLISHED_R03_CANDIDATES, (
        f"the derived pool is {len(candidates)}, not {PUBLISHED_R03_CANDIDATES}; the complement "
        "below would be arithmetic about the wrong pool"
    )
    assert len(roster_keys) == PUBLISHED_ROSTER_SIZE
    assert len(roster_keys & candidates) == PUBLISHED_ROSTER_SIZE, (
        "a roster key left the derived pool; the complement is insensitive to this on its own"
    )
    assert len(candidates - roster_keys) == PUBLISHED_UNSELECTED
    assert PUBLISHED_R03_CANDIDATES - PUBLISHED_ROSTER_SIZE == PUBLISHED_UNSELECTED


def test_the_loader_refuses_a_snapshot_whose_atc_column_is_absent(tmp_path, monkeypatch):
    """THE PROBE. An absent ATC column must not read as "no candidates"."""
    frame = _load_snapshot_or_skip()
    doctored = tmp_path / "drugbank_compounds.parquet"
    frame.drop(columns=[ATC_COLUMN]).to_parquet(doctored)
    monkeypatch.setattr(sys.modules[__name__], "snapshot_parquet_path", lambda: doctored)

    with pytest.raises(AssertionError) as excinfo:
        _load_snapshot_or_skip()
    assert ATC_COLUMN in str(excinfo.value)


def test_the_instrument_check_FIRES_when_the_extractor_is_blinded(tmp_path, monkeypatch):
    """Proves the instrument precondition is not decorative.

    Blanks every ATC cell, which is what a broken extractor looks like from the inside, and
    requires the precondition to fail rather than the counts to report zeros.
    """
    frame = _load_snapshot_or_skip().copy()
    frame[ATC_COLUMN] = [np.array([], dtype=object) for _ in range(len(frame))]
    doctored = tmp_path / "blinded.parquet"
    frame.to_parquet(doctored)
    monkeypatch.setattr(sys.modules[__name__], "snapshot_parquet_path", lambda: doctored)

    with pytest.raises(AssertionError, match="found NO codes anywhere"):
        test_the_instrument_finds_atc_codes_at_all_before_any_count_is_trusted()
