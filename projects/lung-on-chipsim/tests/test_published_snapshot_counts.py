"""The PUBLISHED snapshot counts — pinned against the REAL parquet.

What this module is for
-----------------------
Several numbers are published about the pinned snapshot and, until this module existed, **none
of them was pinned against the real artifact**:

- "6,802 compounds, 9 attributes" (the product-cut walkthrough);
- "the 6,610-key snapshot" (the T18 candidate-list hand-off);
- "the snapshot's 42 relative-stereo compounds" (the relative-stereo ruling, CTO #122 §0, and
  the evidence ledger's §3.1).

Every existing `relative_stereo_keys` test runs on a synthetic three-row frame (`"K-A"`), and no
test in the suite reads the real parquet at all. So the published figures rested on commands run
once, exactly as the P-gp counts did before ``test_published_pgp_result``.

6,802 and 6,610 ARE NOT THE SAME CLAIM — that is the point of this module
--------------------------------------------------------------------------
They are both true and they are about **different subjects**: 6,802 is the ROW count, 6,610 is
the count of DISTINCT ``canonical_inchikey`` values. The 192-row difference is the stereo-free
re-key pooling members the source never distinguished, which is the predicted consequence of the
relative-stereo ruling rather than a defect. Both are pinned here, side by side, **because a
reader who takes one for the other has made precisely this project's recurring error: a correct
reading of real evidence attributed to the wrong subject.**

What CANNOT be promoted from `cited` to `derived`, and why
----------------------------------------------------------
§3.1 also cites "**13** of the 42 came out as the MIRROR IMAGE, classified by InChI layers
against PubChem". **That 13 is NOT pinned here and cannot be**, by me, on purpose:

- it rests on an EXTERNAL per-compound comparison against PubChem, not on anything in the tree;
- the project's standing constraints forbid this agent from looking up whether an identifier is
  assigned, and from pairing an identifier with a substance.

So the 42 becomes `derived` and the 13 stays irreducibly `cited`. Stating which half moved is
the honest result; silently pinning only what is easy and calling §3.1 "measured" would not be.

Byte availability, and why a skip here is not a pass
----------------------------------------------------
The parquet is a build output (`.gitignore: data/processed/**`) and its bytes live on a
DVC remote that is **machine-local**, so CI cannot pull them. When the bytes are absent these
tests SKIP **with the reason stated in the skip message** — they never silently pass. The
byte-independent half (pointer coverage, manifest/digest consistency) is already covered by
``test_provenance``; this module covers what only the bytes can answer, which is the environment
where the published numbers are actually produced and therefore where drift would occur.

**If one of these fails, do NOT edit the literal.** It means the snapshot or the keying changed,
and every surface quoting these numbers has to change with it.

No identifier, accession, name or key is written into this file or into any failure message —
only counts. The frame itself carries `name` and `drugbank_id`, which is why it is gitignored.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from chipsim.harmonize.ids import relative_stereo_keys

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
    """Indirection with a purpose: it makes every pin below FALSIFIABLE.

    A default argument binds at definition time, so a pin wired straight to the real path could
    never be pointed at a doctored copy — and a pin that cannot be pointed at a wrong tree
    cannot be SHOWN to fail on one. That exact vacuity was caught in the first draft of
    ``test_published_pgp_result``; this module is built to avoid repeating it.
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
    """Load the snapshot, asserting its subject before any count is taken.

    An absent file SKIPS with its reason stated. An absent column FAILS — a missing column must
    never read as "nothing there", which is the defect family this suite keeps catching.
    """
    path = snapshot_parquet_path()
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
    for column in (KEY_COLUMN, FLAG_COLUMN):
        assert column in frame.columns, (
            f"the snapshot has no {column!r} column; its columns are {list(frame.columns)}. "
            "Refusing to count a column that does not exist."
        )
    _assert_snapshot_is_the_pinned_artifact(path)
    return frame


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


def test_the_loader_refuses_a_snapshot_whose_flag_column_is_absent(tmp_path, monkeypatch):
    """THE PROBE. Without it, every pin above could be decorative.

    A frame built before the re-key must not read as "no relative-stereo compounds" — that is
    exactly how a dropped flag passes every downstream check.

    Built on a SYNTHETIC frame so it runs where the bytes are absent, which is the only
    environment where it runs unattended. See `_synthetic_frame`.
    """
    doctored = tmp_path / "drugbank_compounds.parquet"
    _synthetic_frame().drop(columns=[FLAG_COLUMN]).to_parquet(doctored)
    monkeypatch.setattr(sys.modules[__name__], "snapshot_parquet_path", lambda: doctored)

    with pytest.raises(AssertionError) as excinfo:
        _load_snapshot_or_skip()
    assert FLAG_COLUMN in str(excinfo.value)


def test_an_absent_snapshot_skips_with_a_stated_reason_rather_than_passing(tmp_path, monkeypatch):
    """The skip must be legible. A silent skip is indistinguishable from a verified pass."""
    monkeypatch.setattr(
        sys.modules[__name__],
        "snapshot_parquet_path",
        lambda: tmp_path / "absent.parquet",
    )
    with pytest.raises(pytest.skip.Exception) as excinfo:
        _load_snapshot_or_skip()
    message = str(excinfo.value)
    assert "MACHINE-LOCAL" in message
    assert "not a pass" in message
