"""Provenance / data contracts — build-plan T11 support.

The provenance contract is the one ratified by **CTO ruling E-1**:

    nine keys present; eight always non-empty;
    `commit_change_rationale` non-empty IFF `source_commit != audited_commit`.

That is a *conditional-presence* contract, not a weaker one. It is strictly more
checkable than "all nine non-empty", because it makes the EMPTY case an assertion
rather than an exemption: a rationale offered for an unchanged commit is just as
much a contract violation as a rationale missing for a changed one.

r2 worded T1 as "all eight keys non-empty" against a nine-key interface while T2
*required* the rationale to be empty on an unchanged commit — a genuine
self-contradiction. E-1 resolved it in favour of the conditional.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

#: The one key whose emptiness is CONDITIONAL on the two commit fields.
CONDITIONAL_KEY = "commit_change_rationale"

#: The eight keys that must ALWAYS be present and non-empty.
REQUIRED_NON_EMPTY_KEYS = (
    "source_commit",
    "audited_commit",
    "source_repo",
    "upstream_version",
    "snapshot_date",
    "licence",
    "attribution",
    "non_commercial_commitment",
)

#: All nine keys that must be PRESENT. Presence and non-emptiness are different
#: assertions here — that distinction is the whole content of E-1.
REQUIRED_KEYS = (*REQUIRED_NON_EMPTY_KEYS, CONDITIONAL_KEY)

#: T1 requires exactly these three attribution entries.
EXPECTED_ATTRIBUTION_COUNT = 3

_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


class ProvenanceContractError(RuntimeError):
    """A provenance document violates the E-1 contract."""


def _is_empty(value: object) -> bool:
    """Empty means: absent, None, blank/whitespace-only string, or empty collection.

    A whitespace-only rationale is empty. Treating "   " as a justification would
    let a silent snapshot swap through on a spacebar.
    """
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, list | tuple | dict | set):
        return len(value) == 0
    return False


def load_provenance(path: Path) -> dict:
    """Parse a provenance YAML. Does not validate — call check_provenance."""
    data = yaml.safe_load(Path(path).read_text())
    if not isinstance(data, dict):
        raise ProvenanceContractError(
            f"{path} did not parse to a mapping (got {type(data).__name__})"
        )
    return data


def check_provenance(doc: dict) -> None:
    """Assert the full E-1 contract. Raises ProvenanceContractError on violation."""
    missing = [k for k in REQUIRED_KEYS if k not in doc]
    if missing:
        raise ProvenanceContractError(
            f"provenance is missing required key(s): {sorted(missing)}. "
            f"All {len(REQUIRED_KEYS)} keys must be PRESENT, including "
            f"{CONDITIONAL_KEY!r} (which may be empty — see check_commit_substitution)."
        )

    empty = [k for k in REQUIRED_NON_EMPTY_KEYS if _is_empty(doc.get(k))]
    if empty:
        raise ProvenanceContractError(
            f"provenance key(s) present but empty: {sorted(empty)}. "
            f"These {len(REQUIRED_NON_EMPTY_KEYS)} keys are unconditionally non-empty."
        )

    for key in ("source_commit", "audited_commit"):
        value = doc[key]
        if not isinstance(value, str) or not _COMMIT_RE.match(value):
            raise ProvenanceContractError(
                f"{key} must match ^[0-9a-f]{{40}}$ (a full, lowercase git SHA); got {value!r}"
            )

    attribution = doc["attribution"]
    if not isinstance(attribution, list):
        raise ProvenanceContractError(
            f"attribution must be a list so it parses (defect 14); got {type(attribution).__name__}"
        )
    if len(attribution) != EXPECTED_ATTRIBUTION_COUNT:
        raise ProvenanceContractError(
            f"attribution must have exactly {EXPECTED_ATTRIBUTION_COUNT} entries; "
            f"got {len(attribution)}"
        )

    check_commit_substitution(doc)


def check_commit_substitution(doc: dict) -> None:
    """The E-1 biconditional, asserted in BOTH directions.

    - `source_commit != audited_commit` and the rationale is empty -> a silent
      snapshot swap. Raises.
    - `source_commit == audited_commit` and the rationale is non-empty -> a
      rationale for a substitution that did not happen. Also raises: T2 requires
      the rationale to be empty in this case, and accepting it would make the
      field meaningless as evidence.
    """
    swapped = doc["source_commit"] != doc["audited_commit"]
    justified = not _is_empty(doc.get(CONDITIONAL_KEY))

    if swapped and not justified:
        raise ProvenanceContractError(
            "source_commit != audited_commit but commit_change_rationale is empty — "
            "a silent snapshot swap (defect 17). The rationale is REQUIRED when the "
            "audited commit is not the commit actually fetched."
        )
    if not swapped and justified:
        raise ProvenanceContractError(
            "source_commit == audited_commit but commit_change_rationale is non-empty. "
            "T2 requires an EMPTY rationale when no substitution occurred; a rationale "
            "here describes a swap that did not happen."
        )
