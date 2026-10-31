"""The PUBLISHED claims about the pinned snapshot — pinned against the REAL artifact.

This module covers two subjects that share one artifact, one loader and one byte-availability
caveat, in two sections:

- **A — the cohort's shape:** the row count, the attribute set, the distinct-key count and the
  relative-stereo count.
- **B — the roster's provenance:** the mechanically derived ATC R03 candidate pool, and that the
  26-entry roster is a subset of it.

WHY THEY ARE ONE MODULE, and what I got wrong. They began as two, each carrying its own copy of
the loader, the digest check, the synthetic probe frame and the path constants — about 35 lines —
with a docstring justifying the split as avoiding "coupling two suites' collection order for
three lines". **That justification was factually wrong on both counts:** a cross-module import
does not affect pytest collection order, and this house already does
`from tests.conftest import …` (pinned by `test_fixtures.py`). And the two copies had already
drifted — one carried the comment explaining the `relative_to` degradation and the other silently
inherited the code without it — while their skip messages diverged in wording. Repairing the gate
findings then made it worse: the digest check and the synthetic frame were added to BOTH.

`tests/conftest.py` would have been the house home for a shared helper, but its own docstring
states that its loaders read "ONLY from tests/fixtures/, never from configs/ or data/", and this
loader reads `data/processed/`. Putting it there would have contradicted that contract. So the
duplication is removed by merging rather than by sharing, which is also what the review
recommended.

6,802 AND 6,610 ARE NOT THE SAME CLAIM. Both are published and both are true, of **different
subjects**: 6,802 is the ROW count, 6,610 the count of DISTINCT `canonical_inchikey` values. The
192-row difference is the stereo-free re-key pooling members the source never distinguished — the
predicted consequence of the relative-stereo ruling, not a defect. Both are pinned here, side by
side, because a reader who takes one for the other has made this project's recurring error.

WHAT CANNOT BE PROMOTED FROM `cited` TO `derived`. The evidence ledger also cites "13 of the 42
came out as the MIRROR IMAGE, classified by InChI layers against PubChem". That 13 is **not**
pinned here and cannot be: it rests on an external per-compound comparison, and the standing
constraints forbid this agent from looking up whether an identifier is assigned or pairing an
identifier with a substance. The 42 is `derived`; the 13 stays `cited`.

Likewise in section B, **13 unselected is derived; "13 without a resolvable DOI" is not.** The
tree records which candidates were SELECTED, never why each unselected one was rejected — that
record died with an account-scoped surface. The two readings coincide only because selection was
*defined* as "carries a resolvable citation". Same numeral, different predicate.

NO ASSERTION HERE MAY TAKE THE FRAME OR A KEY SET AS AN OPERAND. The frame pairs
`canonical_inchikey` with `name` and `drugbank_id`, and pytest's assertion rewriting prints every
subexpression whatever a custom message says — so a frame operand emits an identifier PAIRED with
a substance, on a public surface, into CI logs. Every assertion below takes a pre-bound scalar.
`test_source_hygiene` enforces the shape; the empirical check is to break something deliberately
and grep the formatted report for the identifier pattern.

BYTE AVAILABILITY. The parquet is a build output (`.gitignore: data/processed/**`) whose bytes
live on a MACHINE-LOCAL DVC remote, so CI cannot pull them. The byte-dependent pins SKIP with the
reason stated in the message, never silently; the probes are built on a synthetic frame so they
run everywhere. The module is marked `integration` accordingly.

**If a pin here fails, do NOT edit the literal.** It means the snapshot, the ATC data or the
roster changed, and every surface quoting these numbers has to change with it.
"""

from __future__ import annotations

import hashlib
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from chipsim.harmonize.ids import relative_stereo_keys
from chipsim.harmonize.roster import load_poc_roster

#: `-m "not integration"` deselected none of these, so a selector that exists to avoid
#: snapshot-dependent tests silently kept them.
pytestmark = pytest.mark.integration

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_PARQUET = PROJECT_ROOT / "data" / "processed" / "drugbank_compounds.parquet"
#: The TRACKED digest of the pinned artifact. Both modules' titles say "pinned against the REAL
#: parquet"; without this check that was not true — they would pass against any locally rebuilt
#: parquet, which is a different artifact from the one the published numbers describe.
SNAPSHOT_DIGEST = PROJECT_ROOT / "data" / "processed" / "drugbank_compounds.sha256"

KEY_COLUMN = "canonical_inchikey"
FLAG_COLUMN = "stereo_is_relative"
#: The independent witness for the relative-stereo flag: InChI's `/s2` layer marks RELATIVE sp3
#: stereo in the structure string itself, so it is not derived from the flag it checks.
INCHI_COLUMN = "inchi"
#: Present only so the synthetic probe frame carries the same column names as the real one.
ATC_COLUMN = "atc_codes"

# Measured at 50c13b1 against the pinned snapshot. See the module docstring: a failure is a
# change to what the cohort IS, never a literal to edit.
PUBLISHED_ROWS = 6802
PUBLISHED_DISTINCT_KEYS = 6610
PUBLISHED_RELATIVE_STEREO = 42
PUBLISHED_COLUMNS = (
    "canonical_inchikey",
    "stereo_is_relative",
    "drugbank_id",
    "name",
    "type",
    "groups",
    "atc_codes",
    "inchi",
    "inchikey",
)

TRACKED_ROSTER = PROJECT_ROOT / "configs" / "poc_compounds.yaml"
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


def _load_snapshot_or_skip(
    path: Path | None = None,
    required: tuple[str, ...] = (KEY_COLUMN, FLAG_COLUMN, ATC_COLUMN),
) -> pd.DataFrame:
    """Load the snapshot, asserting its subject before any count is taken.

    An absent file SKIPS with its reason stated. An absent column FAILS — a missing column must
    never read as "nothing there", which is the defect family this suite keeps catching.

    `path` is an explicit parameter rather than a module-level getter the probes monkeypatch. Both
    mechanisms were in use across the two modules this one replaces, for the same stated purpose;
    this is the one already in the family (`test_published_pgp_result`) and it needs no `sys`
    import. It is what keeps the pins FALSIFIABLE: a pin wired straight to the real path could
    never be pointed at a doctored copy, and a pin that cannot be pointed at a wrong tree cannot
    be SHOWN to fail on one.
    """
    path = Path(path) if path is not None else SNAPSHOT_PARQUET
    if not path.is_file():
        # `relative_to` RAISES for a path outside the project, which would turn this skip into
        # a ValueError — the error path of the discovery is part of the check, so it degrades
        # to the absolute path instead of crashing. Found by the absent-snapshot probe below.
        try:
            shown: Path | str = path.relative_to(PROJECT_ROOT)
        except ValueError:
            shown = path
        pytest.skip(
            f"snapshot bytes absent at {shown}: it is a build output "
            "(.gitignore: data/processed/**) whose bytes live on a MACHINE-LOCAL DVC remote, so "
            "CI cannot pull them. This is a SKIP with a stated reason, not a pass: the published "
            "counts are unverified in this environment. Byte-independent pointer and manifest "
            "coverage lives in test_provenance."
        )
    frame = pd.read_parquet(path)
    for column in required:
        assert column in frame.columns, (
            f"the snapshot has no {column!r} column; its columns are {list(frame.columns)}. "
            "Refusing to count a column that does not exist."
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


# --- Section A: the cohort's shape ----------------------------------------------------------


def test_the_snapshot_carries_the_published_row_count():
    # The count is bound BEFORE the assert on purpose. pytest's assertion rewriting prints every
    # subexpression, so `assert len(frame) == N` emits a repr of the frame itself — and this frame
    # carries `canonical_inchikey` beside `name` and `drugbank_id`, i.e. an identifier PAIRED with
    # a substance, which this project forbids on a public surface. The message is not the fix; the
    # operand is. Every assertion in this module takes a scalar.
    rows = len(_load_snapshot_or_skip())
    assert rows == PUBLISHED_ROWS


def test_the_snapshot_carries_the_published_attribute_set():
    """'9 attributes' is pinned as the NAMED set, not as the numeral 9.

    A column renamed or swapped would keep the count at nine while changing what the table is.
    """
    frame = _load_snapshot_or_skip()
    assert tuple(frame.columns) == PUBLISHED_COLUMNS
    assert len(PUBLISHED_COLUMNS) == 9


def test_the_distinct_key_count_is_published_SEPARATELY_from_the_row_count():
    """6,802 rows and 6,610 keys are two claims about two subjects. Both pinned, together.

    Conflating them is this project's recurring defect in miniature, so the arithmetic relation
    is asserted here rather than left for a reader to assume.
    """
    frame = _load_snapshot_or_skip()
    rows = len(frame)
    distinct = int(frame[KEY_COLUMN].nunique(dropna=True))

    assert rows == PUBLISHED_ROWS
    assert distinct == PUBLISHED_DISTINCT_KEYS
    assert distinct < rows, (
        "the published numbers assert POOLING — distinct keys fewer than rows. Equality would "
        "mean the stereo-free re-key merged nothing, which contradicts the ruling that produced it"
    )
    assert rows - distinct == PUBLISHED_ROWS - PUBLISHED_DISTINCT_KEYS


def test_no_row_carries_a_null_canonical_key():
    """A null key would make `nunique(dropna=True)` quietly understate the cohort."""
    frame = _load_snapshot_or_skip()
    nulls = int(frame[KEY_COLUMN].isna().sum())
    assert nulls == 0, f"{nulls} row(s) carry a null {KEY_COLUMN}"


def test_the_published_relative_stereo_count_comes_from_the_projects_own_deriver():
    """§3.1's 42, re-derived through `relative_stereo_keys` — not re-implemented here."""
    frame = _load_snapshot_or_skip()
    n_keys = len(relative_stereo_keys(frame))
    assert n_keys == PUBLISHED_RELATIVE_STEREO


def test_the_flagged_rows_and_the_flagged_keys_agree_AND_why_that_matters():
    """42 flagged rows and 42 flagged keys — equal, and the equality is a claim.

    `relative_stereo_keys` flags a key when ANY member is relative, so flagged keys could be
    FEWER than flagged rows if two flagged rows pooled. That they are equal says no relative
    compound shares a key with another, which is what makes "the snapshot's 42 relative-stereo
    compounds" a statement about 42 distinct identities rather than 42 rows of unknown overlap.
    """
    frame = _load_snapshot_or_skip()
    flagged_rows = int(frame[FLAG_COLUMN].fillna(False).astype(bool).sum())
    flagged_keys = relative_stereo_keys(frame)

    n_flagged_keys = len(flagged_keys)
    assert flagged_rows == PUBLISHED_RELATIVE_STEREO
    assert n_flagged_keys == flagged_rows, (
        f"{flagged_rows} flagged row(s) pooled into {n_flagged_keys} key(s); the published "
        "figure would then be a row count, not a count of distinct relative-stereo identities"
    )


def test_the_flagged_set_matches_an_INDEPENDENT_witness_in_the_inchi_layer():
    """The 42 pinned against the CHEMISTRY, not against the same column twice.

    What this replaces, and why. The previous version compared a mask derived from
    `stereo_is_relative` against `relative_stereo_keys`, and called itself a membership guard. It
    was a **tautology**: `relative_stereo_keys` IS "keys whose `stereo_is_relative` is truthy", so
    the difference is empty by construction. Review proved it — flipping the flag OFF one
    genuinely relative row and ON one absolute row keeps the cardinality at 42, every count test
    passes, and the published "42 relative-stereo compounds" then names the WRONG 42.
    `load_poc_roster(relative_stereo_keys=...)` would have been fed the corrupted set.

    The fix is an outside witness. InChI marks relative sp3 stereo with the `/s2` layer, a
    property of the structure string rather than of the flag computed from it, so the flag can now
    be wrong in either direction and this test fails.
    """
    frame = _load_snapshot_or_skip()
    assert INCHI_COLUMN in frame.columns, f"the snapshot has no {INCHI_COLUMN!r} column"
    n_null_inchi = int(frame[INCHI_COLUMN].isna().sum())
    assert n_null_inchi == 0, "a null InChI would silently shrink the witness"

    witness = set(frame.loc[frame[INCHI_COLUMN].str.contains("/s2", regex=False), KEY_COLUMN])
    derived = set(relative_stereo_keys(frame))
    n_witness, n_derived = len(witness), len(derived)
    n_flag_not_witness, n_witness_not_flag = len(derived - witness), len(witness - derived)

    assert n_witness == PUBLISHED_RELATIVE_STEREO, (
        f"the independent /s2 witness finds {n_witness} relative-stereo identities, not "
        f"{PUBLISHED_RELATIVE_STEREO}; the published figure describes a different snapshot"
    )
    assert n_flag_not_witness == 0, (
        f"{n_flag_not_witness} key(s) flagged relative but carrying no /s2 layer (counts only)"
    )
    assert n_witness_not_flag == 0, (
        f"{n_witness_not_flag} key(s) carrying a /s2 layer but not flagged (counts only)"
    )
    assert n_derived == n_witness


def test_the_loader_refuses_a_snapshot_whose_flag_column_is_absent(tmp_path):
    """THE PROBE. Without it, every pin above could be decorative.

    A frame built before the re-key must not read as "no relative-stereo compounds" — that is
    exactly how a dropped flag passes every downstream check.

    Built on a SYNTHETIC frame so it runs where the bytes are absent, which is the only
    environment where it runs unattended. See `_synthetic_frame`.
    """
    doctored = tmp_path / "drugbank_compounds.parquet"
    _synthetic_frame().drop(columns=[FLAG_COLUMN]).to_parquet(doctored)

    with pytest.raises(AssertionError) as excinfo:
        _load_snapshot_or_skip(doctored)
    assert FLAG_COLUMN in str(excinfo.value)


def test_an_absent_snapshot_skips_with_a_stated_reason_rather_than_passing(tmp_path):
    """The skip must be legible. A silent skip is indistinguishable from a verified pass."""
    with pytest.raises(pytest.skip.Exception) as excinfo:
        _load_snapshot_or_skip(tmp_path / "absent.parquet")
    message = str(excinfo.value)
    assert "MACHINE-LOCAL" in message
    assert "not a pass" in message


# --- Section B: the roster's provenance -----------------------------------------------------


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


def test_the_loader_refuses_a_snapshot_whose_atc_column_is_absent(tmp_path):
    """THE PROBE. An absent ATC column must not read as "no candidates".

    Synthetic frame, so it runs where the bytes are absent. See `_synthetic_frame`.
    """
    doctored = tmp_path / "drugbank_compounds.parquet"
    _synthetic_frame().drop(columns=[ATC_COLUMN]).to_parquet(doctored)

    with pytest.raises(AssertionError) as excinfo:
        _load_snapshot_or_skip(doctored)
    assert ATC_COLUMN in str(excinfo.value)


def test_the_instrument_check_FIRES_when_the_extractor_is_blinded(tmp_path):
    """Proves the instrument precondition is not decorative.

    Blanks every ATC cell, which is what a broken extractor looks like from the inside, and
    requires the precondition to fail rather than the counts to report zeros.
    """
    blinded = _synthetic_frame()
    blinded[ATC_COLUMN] = [np.array([], dtype=object) for _ in range(len(blinded))]
    doctored = tmp_path / "blinded.parquet"
    blinded.to_parquet(doctored)

    with pytest.raises(AssertionError, match="found NO codes anywhere"):
        _assert_instrument_finds_codes(_load_snapshot_or_skip(doctored))
