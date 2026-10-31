"""The PUBLISHED P-gp result — pinned against the REAL tracked file.

What this module is for
-----------------------
The evidence ledger states a result: over a 26-compound ATC R03 roster, a pre-registered
(then principal-amended) P-glycoprotein substrate bar yields ``yes=3, no=0, unknown=23``, so
the pre-registered grouping variable is UNPOPULATABLE and ``pgp_groups_usable`` is False.

Until this module existed, **nothing in the suite pinned any of that.** The counts rested on
commands run once in a session. The only test that read the real tracked file at all was
``test_the_real_tracked_adjudication_file_if_present_carries_no_name_column`` — it checks one
column's absence, and it is conditional on the file being present. So the published numbers
could drift from the tree in total silence.

These tests close that gap: they re-derive the result from the tracked file through the
project's OWN derivers and fail when the tree and the published claim disagree.

Provenance of the literals below
--------------------------------
``PUBLISHED_*`` is NOT a biological value authored by an agent. The verdicts were typed by the
principal into the tracked file; these are the counts ``label_counts`` derives from them,
recorded here so that a change to the tree must be a deliberate publication decision instead
of a silent one.

**If one of these tests fails, do NOT edit the literal to make it pass.** A failure means the
tracked verdicts changed. The published claim then changes too — that is the principal's call,
and the ledger and everything downstream must move in lockstep.

Why every subject is asserted before it is counted
--------------------------------------------------
This workstream produced the defect twice in one session: a count read a column that did not
exist, got ``None`` for all 26 rows, and reported "0 typed" while asserting nothing — the
number was right by coincidence. So every reader here asserts its column is present and names
it on failure, and ``test_the_reader_refuses_a_file_whose_label_column_is_absent`` is the probe
that proves the assertion actually fires rather than being decorative.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd
import pytest

from chipsim.eval.provenance_block import label_counts, pgp_groups_usable
from chipsim.harmonize.adjudication import ADJUDICATED_LABELS, CITED_LABELS
from chipsim.harmonize.roster import load_poc_roster

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRACKED_ADJUDICATION = PROJECT_ROOT / "configs" / "pgp_adjudication.csv"
TRACKED_ROSTER = PROJECT_ROOT / "configs" / "poc_compounds.yaml"

LABEL_COLUMN = "adjudicated_label"
DOI_COLUMN = "evidence_doi"
KEY_COLUMN = "canonical_inchikey"

# The principal's ratified verdicts, as `label_counts` derives them. See the module docstring:
# a failure here is a publication decision, never a literal to edit.
PUBLISHED_ROSTER_SIZE = 26
PUBLISHED_COUNTS = {"yes": 3, "no": 0, "unknown": 23}
PUBLISHED_GROUPS_USABLE = False


def tracked_adjudication_path() -> Path:
    """Indirection with a purpose: it makes every pin below FALSIFIABLE.

    A default argument binds at definition time, so with `path=TRACKED_ADJUDICATION` in the
    signature nothing could redirect these tests at a doctored copy — and a pin that cannot be
    pointed at a wrong tree cannot be shown to fail on one. That is the vacuous-green shape
    this workstream keeps finding. Through this getter, a falsification harness (or a future
    test) can substitute a perturbed file WITHOUT writing to the principal's ratified verdicts.
    """
    return TRACKED_ADJUDICATION


def _read_tracked_frame(path: Path | None = None) -> pd.DataFrame:
    """Read the tracked adjudication file, asserting its subject exists first.

    Fails CLOSED and names the missing thing. An absent file or an absent column must never
    read as "nothing there" — that equivalence is the defect this module exists to prevent.
    """
    path = Path(path) if path is not None else tracked_adjudication_path()
    assert path.is_file(), f"the tracked adjudication file is absent: {path}"
    frame = pd.read_csv(path, dtype=str)
    for column in (KEY_COLUMN, LABEL_COLUMN, DOI_COLUMN):
        assert column in frame.columns, (
            f"{path.name} has no {column!r} column; its columns are "
            f"{list(frame.columns)}. Refusing to count a column that does not exist."
        )
    return frame


def _labels(frame: pd.DataFrame) -> pd.Series:
    return frame[LABEL_COLUMN]


def test_the_tracked_adjudication_file_is_tracked_by_git_not_merely_present():
    """A published result may not rest on an untracked local file."""
    assert TRACKED_ADJUDICATION.is_file(), f"absent: {TRACKED_ADJUDICATION}"
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(TRACKED_ADJUDICATION)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"{TRACKED_ADJUDICATION} is present but NOT tracked by git "
        f"(git ls-files exit {result.returncode}): {result.stderr.strip()}"
    )


def test_the_published_roster_size_matches_the_tracked_file():
    # Bound before the assert: pytest prints every subexpression, so a frame operand would emit a
    # repr carrying structure keys. Counts only, in every assertion in this module.
    rows = len(_read_tracked_frame())
    assert rows == PUBLISHED_ROSTER_SIZE


def test_the_published_counts_are_what_the_projects_own_deriver_returns():
    """The headline result, re-derived — not re-implemented."""
    counts = label_counts(_labels(_read_tracked_frame()))
    assert counts == PUBLISHED_COUNTS


def test_label_counts_returns_the_WHOLE_domain__a_LIBRARY_contract_not_a_data_check():
    """Labelled for what it is, after review showed it reads as more than it is.

    `label_counts` builds its result as `{label: ... for label in sorted(ADJUDICATED_LABELS)}`, so
    its key set can never be wrong and **this cannot fail on any tree**. Review measured it: the
    assertion survived six of seven verdict mutations, firing only on row deletion, where a
    sibling already covers it.

    It is kept, not deleted, because the published result depends on the zeros being PRESENT — an
    absent `no` key would let a caller branch on presence and lose the empty group, which is the
    whole finding. But it is contract coverage, not evidence about the verdicts, and the name and
    this docstring now say so rather than letting a reader count it as data coverage.
    """
    counts = label_counts(_labels(_read_tracked_frame()))
    domain = sorted(ADJUDICATED_LABELS)
    total = sum(counts.values())
    assert sorted(counts) == domain
    assert total == PUBLISHED_ROSTER_SIZE


def test_the_grouping_variable_is_unusable_AND_for_the_published_reason():
    """False is not enough: it must be false because the NEGATIVE group is empty.

    `pgp_groups_usable` is also false when BOTH groups are empty, which would be a different
    result with a different meaning (nothing adjudicated, versus adjudicated and one-sided).
    Pinning only the boolean would let those two states swap without a failure.
    """
    counts = label_counts(_labels(_read_tracked_frame()))
    assert pgp_groups_usable(counts) is PUBLISHED_GROUPS_USABLE
    assert counts["no"] == 0, "the published result is that the NEGATIVE group is empty"
    assert counts["yes"] > 0, (
        "the published result is a populated POSITIVE group against an empty negative one; "
        "an empty positive group would be a different result entirely"
    )


def test_every_cited_verdict_carries_a_doi_and_no_uncited_one_does():
    """Derived from CITED_LABELS, so the invariant cannot drift from the module that owns it."""
    frame = _read_tracked_frame()
    has_doi = frame[DOI_COLUMN].notna() & (frame[DOI_COLUMN].str.strip() != "")
    for label in sorted(ADJUDICATED_LABELS):
        rows = frame[LABEL_COLUMN] == label
        if not rows.any():
            continue
        if label in CITED_LABELS:
            assert has_doi[rows].all(), (
                f"{int((~has_doi & rows).sum())} row(s) labelled {label!r} carry no "
                f"{DOI_COLUMN}; a cited verdict without its citation is unbacked data"
            )
        else:
            assert not has_doi[rows].any(), (
                f"{int((has_doi & rows).sum())} row(s) labelled {label!r} carry a "
                f"{DOI_COLUMN}; only {sorted(CITED_LABELS)} may"
            )


def test_the_adjudication_file_and_the_roster_describe_THE_SAME_26_compounds():
    """Two tracked files each claim to be the roster. Divergence would publish a mismatch.

    Compares key SETS only — no identifier is written into this file or any message.
    """
    frame = _read_tracked_frame()
    roster = load_poc_roster(TRACKED_ROSTER)
    # FAIL CLOSED. The old form fell back to `set(roster.index)`, which for a 26-row frame is
    # {0..25} — that SATISFIES the size check below and then fails downstream with "26 roster
    # key(s) are NOT in the derived pool", blaming the published provenance for a missing column.
    # An absent column must name itself, not mutate into a different defect.
    assert KEY_COLUMN in roster.columns, (
        f"the roster frame has no {KEY_COLUMN!r} column; its columns are {list(roster.columns)}"
    )
    roster_keys = set(roster[KEY_COLUMN])
    adjudicated_keys = set(frame[KEY_COLUMN])

    n_adjudicated, n_rows, n_roster = len(adjudicated_keys), len(frame), len(roster_keys)
    assert n_adjudicated == n_rows, "the adjudication file repeats a key"
    assert n_roster == PUBLISHED_ROSTER_SIZE
    # NOT `assert adjudicated_keys == roster_keys`: a set-vs-set compare makes pytest print BOTH
    # SETS of structure keys. This was the one operand my first binding pass missed, and an
    # empirical leak check over a real failing run is what caught it — not reading the code.
    # Symmetric difference, as two counts.
    n_adj_only = len(adjudicated_keys - roster_keys)
    n_roster_only = len(roster_keys - adjudicated_keys)
    assert (n_adj_only, n_roster_only) == (0, 0), (
        f"{n_adj_only} adjudicated key(s) are absent from the roster and {n_roster_only} "
        "roster key(s) were never adjudicated (counts only; keys deliberately not printed)"
    )


def test_the_reader_refuses_a_file_whose_label_column_is_absent(tmp_path):
    """THE PROBE. Without this, every assertion above could be decorative.

    Reproduces the exact session defect — the label column renamed, so a naive reader gets a
    column of nothing and happily reports zeros — and requires the reader to fail and NAME the
    missing column instead.
    """
    doctored = tmp_path / "pgp_adjudication.csv"
    frame = _read_tracked_frame()
    frame.rename(columns={LABEL_COLUMN: "human_verdict"}).to_csv(doctored, index=False)

    with pytest.raises(AssertionError) as excinfo:
        _read_tracked_frame(doctored)
    assert LABEL_COLUMN in str(excinfo.value)


def test_the_reader_refuses_an_absent_file_rather_than_reporting_nothing(tmp_path):
    with pytest.raises(AssertionError, match="absent"):
        _read_tracked_frame(tmp_path / "does-not-exist.csv")
