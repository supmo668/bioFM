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
from chipsim.ingest.drugbank_snapshot import MANIFEST_NAME, verify_snapshot

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
    """`git ls-files` matches no .tsv under data/raw/ — recursive, so a nested
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

    #: What is legitimately tracked under data/raw/: pointers, anchors, the
    #: integrity manifest, and T1/T2's human provenance artifacts. Anything else
    #: is vendored payload.
    allowed_suffixes = (".dvc",)
    allowed_names = {".gitkeep", MANIFEST_NAME, "provenance.yaml", "PROVENANCE.md"}

    offenders = [
        p for p in tracked if not p.endswith(allowed_suffixes) and Path(p).name not in allowed_names
    ]
    assert offenders == [], f"DrugBank payload is vendored into git: {offenders}"


def test_drugbank_not_vendored_catches_a_forced_tsv(tmp_path):
    """The done-condition's falsification: `git add -f` a TSV and the test fails.

    Asserted against the real rule rather than by mutating the index, so the
    working tree is never left dirty.
    """
    tracked = ["data/raw/drugbank/drugbank.tsv", "data/raw/.gitkeep"]
    allowed_suffixes = (".dvc",)
    allowed_names = {".gitkeep", MANIFEST_NAME, "provenance.yaml", "PROVENANCE.md"}
    offenders = [
        p for p in tracked if not p.endswith(allowed_suffixes) and Path(p).name not in allowed_names
    ]
    assert offenders == ["data/raw/drugbank/drugbank.tsv"]


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
