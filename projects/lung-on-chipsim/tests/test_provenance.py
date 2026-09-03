"""Provenance contract tests — build-plan T11.

Distinct from test_contracts.py: §4.4 reserves that module for the §1.2 *data*
contract test, which arrives with the ChEMBL plan (defect 29).

The contract under test is the one ratified by **CTO ruling E-1**: nine keys
present, eight always non-empty, `commit_change_rationale` non-empty IFF
`source_commit != audited_commit`.

**T1/T2's real artifacts are ABSENT** (human-owned, not yet delivered). Per E-1's
sign-off note, T11 signs off against fixtures regardless, because the conditional
contract is testable in both directions from fixtures alone. Nothing here
fabricates a provenance file: the live-file tests skip explicitly when the human
artifact is missing, and say so.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest
import yaml

from chipsim.harmonize.contracts import (
    CONDITIONAL_KEY,
    REQUIRED_KEYS,
    REQUIRED_NON_EMPTY_KEYS,
    ProvenanceContractError,
    check_provenance,
    load_provenance,
)
from chipsim.ingest.drugbank_snapshot import (
    MANIFEST_NAME,
    vendored_offenders,
    verify_snapshot,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "drugbank"

#: The live, human-authored artifact from T1/T2. Absent until H delivers it.
LIVE_PROVENANCE = RAW_DIR / "provenance.yaml"

_requires_live_provenance = pytest.mark.skipif(
    not LIVE_PROVENANCE.exists(),
    reason="T1/T2 human artifact absent — data/raw/drugbank/provenance.yaml not delivered",
)


# --------------------------------------------------------------------------- #
# The five T11 interfaces
# --------------------------------------------------------------------------- #


def test_provenance_complete(provenance_fixture_path):
    """provenance.yaml parses and carries all NINE keys present, with the eight
    unconditional keys non-empty; source_commit matches ^[0-9a-f]{40}$;
    attribution has three entries. (CTO ruling E-1.)"""
    doc = load_provenance(provenance_fixture_path)

    assert set(REQUIRED_KEYS) <= set(doc), f"missing: {sorted(set(REQUIRED_KEYS) - set(doc))}"
    assert len(REQUIRED_KEYS) == 9
    assert len(REQUIRED_NON_EMPTY_KEYS) == 8
    assert CONDITIONAL_KEY in doc, "the ninth key must be PRESENT even when empty"

    check_provenance(doc)


@pytest.mark.parametrize("missing_key", REQUIRED_KEYS)
def test_provenance_complete_rejects_a_missing_key(provenance_fixture_path, tmp_path, missing_key):
    """Every one of the nine keys is load-bearing — including the conditional one,
    whose ABSENCE is a violation even though its emptiness may not be."""
    doc = load_provenance(provenance_fixture_path)
    del doc[missing_key]
    path = tmp_path / "p.yaml"
    path.write_text(yaml.safe_dump(doc))

    with pytest.raises(ProvenanceContractError, match="missing required key"):
        check_provenance(load_provenance(path))


@pytest.mark.parametrize("blanked_key", REQUIRED_NON_EMPTY_KEYS)
def test_provenance_complete_rejects_an_empty_unconditional_key(
    provenance_fixture_path, tmp_path, blanked_key
):
    """The eight unconditional keys are non-empty in every case. This is the half
    of E-1 that did NOT change; it is asserted so the conditional half cannot be
    over-applied to keys it does not govern."""
    doc = load_provenance(provenance_fixture_path)
    doc[blanked_key] = [] if blanked_key == "attribution" else "   "
    path = tmp_path / "p.yaml"
    path.write_text(yaml.safe_dump(doc))

    with pytest.raises(ProvenanceContractError):
        check_provenance(load_provenance(path))


@pytest.mark.parametrize(
    "bad_commit",
    ["main", "DEADBEEF" * 5, "deadbeef" * 4 + "deadbee", "", "not-a-sha"],
)
def test_provenance_rejects_a_non_40_hex_commit(provenance_fixture_path, tmp_path, bad_commit):
    """The 40-hex check was dead code with respect to the suite — deleting it passed.

    A passing positive case asserts nothing about a rejection rule. Both commit
    fields are set together so the E-1 biconditional does not raise first and mask
    the check under test.
    """
    doc = load_provenance(provenance_fixture_path)
    doc["source_commit"] = bad_commit
    doc["audited_commit"] = bad_commit
    path = tmp_path / "p.yaml"
    path.write_text(yaml.safe_dump(doc))

    with pytest.raises(ProvenanceContractError):
        check_provenance(load_provenance(path))


@pytest.mark.parametrize("count", [0, 1, 2, 4])
def test_provenance_rejects_a_wrong_attribution_count(provenance_fixture_path, tmp_path, count):
    """The attribution-count check was also dead code — deleting it passed."""
    doc = load_provenance(provenance_fixture_path)
    doc["attribution"] = [f"entry {i}" for i in range(count)]
    path = tmp_path / "p.yaml"
    path.write_text(yaml.safe_dump(doc))

    with pytest.raises(ProvenanceContractError):
        check_provenance(load_provenance(path))


def test_provenance_rejects_a_non_list_attribution(provenance_fixture_path, tmp_path):
    doc = load_provenance(provenance_fixture_path)
    doc["attribution"] = "Wishart et al.; Himmelstein et al.; Licence discussion"
    path = tmp_path / "p.yaml"
    path.write_text(yaml.safe_dump(doc))

    with pytest.raises(ProvenanceContractError, match="must be a list"):
        check_provenance(load_provenance(path))


def test_provenance_commit_substitution_is_justified(fixture_dir):
    """The conditional contract, ratified E-1: commit_change_rationale is
    non-empty IFF source_commit != audited_commit. Both directions assert —
    a silent snapshot swap fails (rationale missing), AND a rationale offered
    for an unchanged commit fails too (defect 17)."""
    # (1) commits EQUAL + rationale EMPTY -> valid.
    check_provenance(load_provenance(fixture_dir / "provenance.yaml"))

    # (2) commits DIFFER + rationale NON-EMPTY -> valid.
    check_provenance(load_provenance(fixture_dir / "provenance_justified_swap.yaml"))

    # (3) commits DIFFER + rationale EMPTY -> the silent swap. Must raise.
    with pytest.raises(ProvenanceContractError, match="silent snapshot swap"):
        check_provenance(load_provenance(fixture_dir / "provenance_unjustified_swap.yaml"))


def test_provenance_rejects_rationale_for_an_unchanged_commit(provenance_fixture_path, tmp_path):
    """The direction r2's wording could not express. A rationale describing a swap
    that never happened is a contract violation, not a harmless extra: it is the
    difference between the conditional contract and a mere 'at least one of' rule.
    """
    doc = load_provenance(provenance_fixture_path)
    assert doc["source_commit"] == doc["audited_commit"]
    doc[CONDITIONAL_KEY] = "explains a substitution that did not occur"
    path = tmp_path / "p.yaml"
    path.write_text(yaml.safe_dump(doc))

    with pytest.raises(ProvenanceContractError, match="did not happen"):
        check_provenance(load_provenance(path))


def test_provenance_rejects_whitespace_only_rationale(fixture_dir, tmp_path):
    """A spacebar is not a justification."""
    doc = load_provenance(fixture_dir / "provenance_justified_swap.yaml")
    doc[CONDITIONAL_KEY] = "   \n\t "
    path = tmp_path / "p.yaml"
    path.write_text(yaml.safe_dump(doc))

    with pytest.raises(ProvenanceContractError, match="silent snapshot swap"):
        check_provenance(load_provenance(path))


@_requires_live_provenance
def test_snapshot_hashes_match_manifest():
    """Recomputed sha256 of each fetched file equals SHA256SUMS.json (defect 2).
    Fails if any fetched file is mutated after fetch.

    Skips while T2/T4a are outstanding — there is no snapshot on disk to hash,
    and hashing a fabricated one would assert nothing.
    """
    manifest_path = RAW_DIR / MANIFEST_NAME
    assert manifest_path.is_file(), f"{MANIFEST_NAME} missing beside the snapshot"
    recorded = json.loads(manifest_path.read_text())

    verified = verify_snapshot(RAW_DIR)
    assert verified == recorded

    for name, digest in recorded.items():
        actual = hashlib.sha256((RAW_DIR / name).read_bytes()).hexdigest()
        assert actual == digest, f"{name} mutated after fetch"


def test_drugbank_not_vendored():
    """`git ls-files` matches no payload under data/raw/ — recursive, so a nested
    layout cannot hide one (defect 7).

    Widened past `*.tsv` deliberately (CTO ruling E-5): the DVC store holds the
    snapshot as EXTENSIONLESS md5 blobs, which a `*.tsv` glob would never catch.
    """
    tracked = subprocess.run(
        ["git", "ls-files", "data/raw/"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()

    offenders = vendored_offenders(tracked)
    assert offenders == [], f"DrugBank payload is vendored into git: {offenders}"


@pytest.mark.parametrize(
    "path",
    [
        "data/raw/drugbank/drugbank.tsv",
        "data/raw/drugbank/nested/deeper/proteins.tsv",
        # the extensionless md5 blob form ruling E-5 calls out — a *.tsv glob misses it
        "data/raw/files/md5/ab/cdef0123456789",
        "data/raw/drugbank.parquet",
    ],
)
def test_drugbank_not_vendored_catches_payload(path):
    """The falsification, driven through the SAME production rule as the test above.

    This was previously a closed tautology: it re-declared the allow-list inline and
    rebuilt the comprehension, so it exercised a Python list comprehension and
    nothing else. Widening `vendored_offenders`'s allow-list to permit `.tsv` would
    have left it passing. Now both call `chipsim.ingest.drugbank_snapshot.
    vendored_offenders`, so the falsification breaks when the rule does.
    """
    assert vendored_offenders([path, "data/raw/.gitkeep"]) == [path]


@pytest.mark.parametrize(
    "path",
    [
        "data/raw/drugbank.dvc",
        "data/raw/drugbank/proteins.tsv.dvc",
        "data/raw/.gitkeep",
        "data/raw/drugbank/SHA256SUMS.json",
        "data/raw/drugbank/provenance.yaml",
        "data/raw/drugbank/PROVENANCE.md",
    ],
)
def test_vendoring_rule_allows_what_must_stay_tracked(path):
    """The other direction: the rule must not reject the files that make the
    snapshot recoverable and auditable."""
    assert vendored_offenders([path]) == []


def test_dvc_pointer_is_tracked():
    """data/raw/drugbank.dvc IS tracked by git — the blanket ignore must not
    swallow the one file that makes the snapshot recoverable (defect 10c).

    T4 has not generated the pointer yet (blocked on T2), so this asserts the
    reachable half: git must not IGNORE the path. An ignored path could never be
    tracked once it does exist, which is the failure mode defect 10c describes.
    """
    ignored = subprocess.run(
        ["git", "check-ignore", "-q", "data/raw/drugbank.dvc"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        check=False,
    )
    assert ignored.returncode == 1, (
        "data/raw/drugbank.dvc is git-ignored — the pointer could never be tracked"
    )

    pointer = PROJECT_ROOT / "data" / "raw" / "drugbank.dvc"
    if pointer.exists():
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "data/raw/drugbank.dvc"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            check=False,
        )
        assert tracked.returncode == 0, "pointer exists but is untracked"


# --- the card states the seal's limits, and cannot overstate them -----------


def test_card_reports_an_unratified_panel_as_not_ratified(tmp_path):
    """The live panel ships `ratified: false`. The card must say so plainly —
    silence would let a reader assume a human checked the accessions."""
    import yaml as _yaml

    from chipsim.eval.provenance_block import render_panel_ratification

    panel = tmp_path / "panel.yaml"
    panel.write_text(_yaml.safe_dump({"ratified": False, "ratified_by": "", "panel": []}))

    # Case-insensitive: the status must be reported, and rewording the emphasis
    # to "Not ratified." is a harmless edit that must not fail the suite. The
    # SEMANTIC pair is what matters — the status token plus the reason.
    text = "\n".join(render_panel_ratification(panel)).lower()
    assert "not ratified" in text
    assert "no human has verified" in text


def test_card_never_claims_the_seal_proves_authorship(tmp_path):
    """The card is where an overclaim does the most damage: a reader meets the
    seal here, not in the source. `ratified` plus a digest reads as proof a human
    checked the accessions unless the text says otherwise.

    THE PREVIOUS VERSION OF THIS TEST DID NOT DETECT OVERCLAIMING. It asserted
    four disclaimer substrings were PRESENT, and a card asserting the exact
    opposite contains all four: "it **does** establish who ratified it" contains
    `establish who`; "**not authentication** in the pedantic sense" contains
    `not authentication`; "cannot be **deliberately circumvented**" — the precise
    inversion of the bound — contains `deliberately circumvented`. A reviewer
    rewrote the card to claim the seal proves a human checked every accession and
    the whole suite stayed green.

    Its docstring defended this by delegating the negative half to the source
    scan in test_journal.py. That scan's file list did not include this module.
    Each half was documented as covered by the other; neither covered it.

    So: presence AND polarity, both on the RENDERED text, sharing one scanner
    with the source test.
    """
    import yaml as _yaml
    from honesty_scan import assert_no_unqualified_claims, normalize

    from chipsim.eval.provenance_block import render_panel_ratification
    from chipsim.harmonize.pgp_label import seal_panel

    panel = tmp_path / "panel.yaml"
    panel.write_text(
        _yaml.safe_dump(
            {
                "ratified": True,
                "ratified_by": "A Human",
                "ratified_on": "2026-09-03",
                "ratified_panel_sha256": "",
                "panel": [{"symbol": "ABCB1", "uniprot": "P08183", "alias": "x", "face": "apical"}],
            }
        )
    )
    # Seal it for real, so this exercises the ratified-AND-verified branch — the
    # one that renders the most confident wording and therefore needs the check
    # most. A placeholder digest renders the FAILS-VERIFICATION branch instead,
    # which is not the text under test.
    seal_panel(panel)

    rendered = "\n".join(render_panel_ratification(panel))

    # 1. POLARITY: no forbidden claim without a negation preceding it. This is
    #    what the old assertions could not do.
    inspected = assert_no_unqualified_claims(rendered, "the rendered card")
    assert inspected > 0, (
        "the card no longer discusses authorship at all — the limits it is "
        "required to state appear to have been dropped rather than qualified"
    )

    # 2. PRESENCE: the limits must be STATED, not merely not-contradicted, or an
    #    empty section would pass the polarity check trivially.
    text = normalize(rendered)
    assert "establish who" in text, "the card must say authorship is not established"
    assert "unkeyed" in text, "the card must say WHY authorship cannot be established"
    assert "deliberately circumvented" in text, (
        "the card must bound the TTY/confirmation gate rather than implying it authenticates"
    )
    assert "not authentication" in text


def test_omitting_the_panel_renders_a_visible_gap_not_a_silent_one(provenance_fixture_path):
    """`panel=None` must SAY the panel is missing, not quietly render nothing.

    The argument lost its `None` default so a caller has to decide — but that
    alone is not enough, and a mutation proved it: replacing the not-supplied
    notice with an empty string left every test green. A card that simply omits
    the ratification heading is not read as "incomplete"; it is read as a card
    about a system where ratification is not a concern. That is the more
    dangerous of the two failures, because it looks finished.

    There is still no production caller of `render_data_provenance` with a panel
    (build-plan M0c owns the wiring). This test is what stands in for that
    absence: whichever way M0c goes, the card cannot end up silent about it.
    """
    import pandas as pd

    from chipsim.eval.provenance_block import render_data_provenance

    labels = pd.Series(["yes", "no", "unknown"])
    text = render_data_provenance(provenance_fixture_path, labels, panel=None)

    assert "Barrier panel ratification" in text, (
        "the heading vanished — a reader cannot notice a section that is not there"
    )
    assert "Not supplied" in text
    assert "the card is wrong" in text, (
        "the notice must say what it means for the card, not merely note an absence"
    )


@pytest.mark.parametrize(
    ("seal", "why"),
    [
        (True, "a YAML boolean renders as `True…`, which reads as a truncated digest"),
        ("abc", "a 3-character value renders as `abc…` — the ellipsis invents 61 characters"),
        ("Z" * 64, "right length, not hex"),
        ("a" * 63, "one character short of a digest"),
    ],
)
def test_a_malformed_seal_is_named_malformed_not_dressed_as_a_digest(tmp_path, seal, why):
    """A value that is not a sha256 must not be rendered in digest costume.

    The trailing ellipsis is the specific harm: ``abc…`` announces the truncation
    of a 64-hex digest that was never there, so a reader who knows what a digest
    looks like sees one and stops checking. Verification alone does not fix this
    — a malformed seal fails verification and the failure branch STILL printed
    `sealed[:16]…`, so the card reported a mismatch between two things only one
    of which existed.
    """
    import yaml as _yaml

    from chipsim.eval.provenance_block import render_panel_ratification

    panel = tmp_path / "panel.yaml"
    panel.write_text(
        _yaml.safe_dump(
            {
                "ratified": True,
                "ratified_by": "A Human",
                "ratified_panel_sha256": seal,
                "panel": [{"symbol": "ABCB1", "uniprot": "P08183", "alias": "x", "face": "apical"}],
            }
        )
    )

    text = "\n".join(render_panel_ratification(panel))

    assert "MALFORMED" in text, why
    assert "…" not in text, "a malformed seal must not be rendered with a truncation ellipsis"
    assert "treat this panel as unsealed" in text
