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

import hashlib
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from chipsim.harmonize.roster import load_poc_roster

#: Declared in pyproject.toml as "requires a human-gated artifact OR THE FETCHED SNAPSHOT ON
#: DISK" — this module's exact situation, with precedent in `test_parse.py`. Without it,
#: `-m "not integration"` deselected none of these, so a selector that exists to avoid
#: snapshot-dependent tests silently kept them.
pytestmark = pytest.mark.integration

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_PARQUET = PROJECT_ROOT / "data" / "processed" / "drugbank_compounds.parquet"
#: The TRACKED digest of the pinned artifact. Both modules' titles say "pinned against the REAL
#: parquet"; without this check that was not true — they would pass against any locally rebuilt
#: parquet, which is a different artifact from the one the published numbers describe.
SNAPSHOT_DIGEST = PROJECT_ROOT / "data" / "processed" / "drugbank_compounds.sha256"
TRACKED_ROSTER = PROJECT_ROOT / "configs" / "poc_compounds.yaml"

KEY_COLUMN = "canonical_inchikey"
ATC_COLUMN = "atc_codes"
#: Present only so the synthetic probe frame carries the same column names as the real one.
FLAG_COLUMN = "stereo_is_relative"
INCHI_COLUMN = "inchi"
R03_PREFIX = "R03"

# Derived at 156980e from the pinned snapshot. A failure is a change to what the cohort IS.
PUBLISHED_R03_CANDIDATES = 39
PUBLISHED_ROSTER_SIZE = 26
PUBLISHED_UNSELECTED = 13
PREREGISTERED_BAND = (20, 40)


def _synthetic_frame() -> pd.DataFrame:
    """A 2-row stand-in with the real COLUMN NAMES and no real content.

    The probes used to doctor a copy of the real snapshot, which had two costs. They SKIPPED
    wherever the bytes are absent — i.e. in CI, the one environment where these guards run
    unattended and are the only thing left — so the machinery proving the pins are not decorative
    was itself inert exactly there. And they wrote a 6,802-row frame carrying `name` and
    `drugbank_id` into pytest's shared temp root, which is retained across runs: a derivative of
    the gitignored, pairing-bearing artifact, outside `data/`.

    A probe only needs column NAMES to prove a column-absence guard fires. Synthetic keys are
    shaped like keys but are not identifiers of anything.
    """
    return pd.DataFrame(
        {
            KEY_COLUMN: ["SYNTHETICKEYAAA-SYNTHETICAA-N", "SYNTHETICKEYBBB-SYNTHETICBB-N"],
            FLAG_COLUMN: [True, False],
            INCHI_COLUMN: ["InChI=1S/SYNTH/s2", "InChI=1S/SYNTH"],
            ATC_COLUMN: [np.array(["R03AA01"], dtype=object), np.array([], dtype=object)],
        }
    )


def snapshot_parquet_path() -> Path:
    """Indirection that keeps the pins FALSIFIABLE — see test_published_pgp_result for why.

    A loader wired to a module constant through a default argument cannot be redirected at a
    doctored copy, and a pin that cannot be pointed at a wrong tree cannot be shown to fail on
    one. This module is deliberately self-contained rather than importing the sibling module's
    loader: a cross-test import would couple two suites' collection order for three lines.
    """
    return SNAPSHOT_PARQUET


def _assert_snapshot_is_the_pinned_artifact(path: Path) -> None:
    """Tie the bytes being read to the digest tracked beside them.

    The sidecar `drugbank_compounds.sha256` is tracked in git; the parquet is not. Nothing in the
    suite compared them, so a locally re-derived parquet — same shape, different artifact — would
    have satisfied every published-number pin in this file. Skipped, not failed, when the sidecar
    is absent, since that is a different defect with its own owner (`test_provenance`).
    """
    if path != SNAPSHOT_PARQUET:
        # A redirected path is a probe's deliberately doctored input, which by construction is NOT
        # the pinned artifact. The pin is a claim about the real path only; applying it to a
        # synthetic frame would make every column-absence probe fail for the wrong reason.
        return
    if not SNAPSHOT_DIGEST.is_file():
        pytest.skip(f"the tracked digest sidecar is absent at {SNAPSHOT_DIGEST.name}")
    recorded = SNAPSHOT_DIGEST.read_text(encoding="utf-8").split()[0].strip().lower()
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    assert actual == recorded, (
        "the snapshot on disk is NOT the pinned artifact: its sha256 does not match the tracked "
        f"digest in {SNAPSHOT_DIGEST.name} (recorded ...{recorded[-8:]}, actual ...{actual[-8:]}). "
        "Every published figure in this module describes the pinned artifact, so none of them is "
        "verified against these bytes."
    )


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
    _assert_snapshot_is_the_pinned_artifact(path)
    return frame


def _atc_codes(value: object) -> list[str]:
    """Normalise one row's ATC cell to a list of upper-case codes.

    Handles the ndarray case EXPLICITLY. Omitting `np.ndarray` here is what made the first
    derivation of this count return a confident 0.
    """
    # A float NaN is NOT None, so without this it falls through to the string branch and
    # `str(float("nan")).upper()` yields the code "NAN". Today's snapshot stores missing ATC as an
    # empty ndarray, so nothing is wrong now — but if a future build stored a NaN scalar instead,
    # the instrument-health check below would count thousands of "codes" and certify a BLIND
    # extractor as healthy, which is the exact misattribution that check exists to prevent.
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return []
    if isinstance(value, (list, tuple, np.ndarray)):
        return [
            str(item).strip().upper()
            for item in value
            if item is not None and not (isinstance(item, float) and math.isnan(item))
        ]
    return [
        part.strip().upper() for part in str(value).replace(";", ",").split(",") if part.strip()
    ]


def _assert_instrument_finds_codes(frame: pd.DataFrame) -> None:
    """The instrument precondition, extracted so the probe does not call a test function.

    Calling one test from another breaks the moment the callee gains a fixture and double-counts
    it in the report; no other module in this suite does it.
    """
    per_row = frame[ATC_COLUMN].apply(lambda cell: len(_atc_codes(cell)))
    total = int(per_row.sum())
    rows_with_any = int((per_row > 0).sum())
    assert total > 0, (
        "the ATC extractor found NO codes anywhere in the snapshot. Every count below would be a "
        "confident zero from a broken instrument — fix the extractor before reading any result."
    )
    assert rows_with_any > 0


def _rows_with_prefix(frame: pd.DataFrame, prefix: str) -> pd.Series:
    return frame[ATC_COLUMN].apply(lambda cell: any(c.startswith(prefix) for c in _atc_codes(cell)))


def test_the_instrument_finds_atc_codes_at_all_before_any_count_is_trusted():
    """FIRST, and the reason the rest is readable: a 0 from a broken extractor is not an absence.

    The obvious implementation returns 0 for every prefix because the cells are ndarrays. That 0
    is indistinguishable from "this snapshot contains no respiratory drugs", which is false.
    """
    _assert_instrument_finds_codes(_load_snapshot_or_skip())


def test_a_nonsense_atc_prefix_finds_nothing():
    """The negative control. Without it, an extractor that matched EVERYTHING would also pass."""
    # Bound before the assert: pytest prints every subexpression, and a frame operand would emit
    # `canonical_inchikey` beside `name` — a PAIRING, which is forbidden on a public surface.
    n_nonsense = int(_rows_with_prefix(_load_snapshot_or_skip(), "ZZZ").sum())
    assert n_nonsense == 0


def test_the_extractor_finds_the_R03_class_inside_a_populated_R_class():
    """Only the FIRST half of this is substantive, and the docstring now says so.

    `r03 <= r_any` is true by construction — every code starting with "R03" starts with "R", and
    both sides call the same extractor — so it tests the prefix operator, not the data. The
    substantive half is that both are non-zero: an extractor returning nothing would make every
    count below a confident zero.
    """
    frame = _load_snapshot_or_skip()
    r03 = int(_rows_with_prefix(frame, R03_PREFIX).sum())
    r_any = int(_rows_with_prefix(frame, "R").sum())
    assert r03 > 0
    assert r_any > 0
    assert r03 <= r_any  # structural, not a data check


def test_the_published_candidate_count_is_derivable_from_the_snapshot():
    """§2's 39, promoted from `cited` to `derived`."""
    pool = int(_rows_with_prefix(_load_snapshot_or_skip(), R03_PREFIX).sum())
    assert pool == PUBLISHED_R03_CANDIDATES


def test_the_39_candidates_are_39_IDENTITIES_not_39_rows():
    """Same class as flagged-rows-vs-flagged-keys: the count alone does not say the claim.

    If two candidate rows pooled onto one canonical key, "39 candidates" would be a row count
    and the pre-registered band of 20-40 would be counting something other than compounds.
    """
    frame = _load_snapshot_or_skip()
    rows = _rows_with_prefix(frame, R03_PREFIX)
    n_rows = int(rows.sum())
    n_identities = int(frame.loc[rows, KEY_COLUMN].nunique())
    assert n_rows == PUBLISHED_R03_CANDIDATES
    assert n_identities == PUBLISHED_R03_CANDIDATES


def test_the_candidate_pool_sits_inside_the_preregistered_band():
    """The band checked against the DERIVED pool, not against a literal.

    The previous version asserted `low <= PUBLISHED_R03_CANDIDATES <= high` — two literals
    declared in this same file — and read nothing from the tree. Review pushed the derived pool to
    41, OUTSIDE the pre-registered 20-40 band, and this test still passed: the single event it
    names was the single event it could not detect. Worse, because it never loaded the snapshot it
    was the only test here that RAN in the byte-less CI environment, so one green beside nine
    skips read as "the band was checked against the data".
    """
    low, high = PREREGISTERED_BAND
    pool = int(_rows_with_prefix(_load_snapshot_or_skip(), R03_PREFIX).sum())
    assert low <= pool <= high, (
        f"the derived ATC R03 pool is {pool}, outside the pre-registered band of {low}-{high}; "
        "the pre-registration no longer describes the cohort"
    )
    # Literal-vs-literal, kept deliberately as an EDITOR's guard on the recorded figure, not as a
    # check against the tree. Labelled so no reader counts it as data coverage.
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
    # FAIL CLOSED. The old form fell back to `set(roster.index)`, which for a 26-row frame is
    # {0..25} — that SATISFIES the size check below and then fails downstream with "26 roster
    # key(s) are NOT in the derived pool", blaming the published provenance for a missing column.
    # An absent column must name itself, not mutate into a different defect.
    assert KEY_COLUMN in roster.columns, (
        f"the roster frame has no {KEY_COLUMN!r} column; its columns are {list(roster.columns)}"
    )
    roster_keys = set(roster[KEY_COLUMN])

    n_roster = len(roster_keys)
    n_outside = len(roster_keys - candidates)
    assert n_roster == PUBLISHED_ROSTER_SIZE
    assert n_outside == 0, (
        f"{n_outside} roster key(s) are NOT in the derived ATC R03 candidate pool, so the "
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
    # FAIL CLOSED. The old form fell back to `set(roster.index)`, which for a 26-row frame is
    # {0..25} — that SATISFIES the size check below and then fails downstream with "26 roster
    # key(s) are NOT in the derived pool", blaming the published provenance for a missing column.
    # An absent column must name itself, not mutate into a different defect.
    assert KEY_COLUMN in roster.columns, (
        f"the roster frame has no {KEY_COLUMN!r} column; its columns are {list(roster.columns)}"
    )
    roster_keys = set(roster[KEY_COLUMN])

    n_candidates = len(candidates)
    n_roster = len(roster_keys)
    n_selected = len(roster_keys & candidates)
    n_unselected = len(candidates - roster_keys)
    assert n_candidates == PUBLISHED_R03_CANDIDATES, (
        f"the derived pool is {n_candidates}, not {PUBLISHED_R03_CANDIDATES}; the complement "
        "below would be arithmetic about the wrong pool"
    )
    assert n_roster == PUBLISHED_ROSTER_SIZE
    assert n_selected == PUBLISHED_ROSTER_SIZE, (
        "a roster key left the derived pool; the complement is insensitive to this on its own"
    )
    assert n_unselected == PUBLISHED_UNSELECTED
    assert PUBLISHED_R03_CANDIDATES - PUBLISHED_ROSTER_SIZE == PUBLISHED_UNSELECTED


def test_the_loader_refuses_a_snapshot_whose_atc_column_is_absent(tmp_path, monkeypatch):
    """THE PROBE. An absent ATC column must not read as "no candidates".

    Synthetic frame, so it runs where the bytes are absent. See `_synthetic_frame`.
    """
    doctored = tmp_path / "drugbank_compounds.parquet"
    _synthetic_frame().drop(columns=[ATC_COLUMN]).to_parquet(doctored)
    monkeypatch.setattr(sys.modules[__name__], "snapshot_parquet_path", lambda: doctored)

    with pytest.raises(AssertionError) as excinfo:
        _load_snapshot_or_skip()
    assert ATC_COLUMN in str(excinfo.value)


def test_the_instrument_check_FIRES_when_the_extractor_is_blinded(tmp_path, monkeypatch):
    """Proves the instrument precondition is not decorative.

    Blanks every ATC cell, which is what a broken extractor looks like from the inside, and
    requires the precondition to fail rather than the counts to report zeros.
    """
    blinded = _synthetic_frame()
    blinded[ATC_COLUMN] = [np.array([], dtype=object) for _ in range(len(blinded))]
    doctored = tmp_path / "blinded.parquet"
    blinded.to_parquet(doctored)
    monkeypatch.setattr(sys.modules[__name__], "snapshot_parquet_path", lambda: doctored)

    with pytest.raises(AssertionError, match="found NO codes anywhere"):
        _assert_instrument_finds_codes(_load_snapshot_or_skip())
