"""M1 reference compounds — build-plan T21 validator (schema mirrors S11a's roster).

T21 is human-owned: which compounds have an *independently published on-chip transport
measurement* is a claim about the literature, so this module only validates a file a
human wrote. It never generates one, and it never writes a transport value.

**T21's set is not T18's PoC roster.** T18 was curated for lung relevance and P-gp
evidence; T21 needs compounds whose transport was measured on a chip by somebody else,
because that measurement is what T27's gate checks the model against. Some overlap is
plausible, none is assumed — so `load_reference_compounds` takes the roster keys only
as an OPTIONAL cross-check and never requires membership. Requiring it would quietly
convert the gate's independent yardstick into a subset of the thing being tested.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

MIN_REFERENCE_ENTRIES = 3
MAX_REFERENCE_ENTRIES = 8

REFERENCE_COLUMNS = (
    "canonical_inchikey",
    "name",
    "published_transport_value",
    "evidence_doi",
)


class ReferenceCompoundError(ValueError):
    """An M1 reference-compound file violates T21's contract."""


def load_reference_compounds(
    path: Path,
    roster_keys: set[str] | None = None,
    *,
    require_in_roster: bool = False,
) -> pd.DataFrame:
    """Parse and validate the reference set. Identity, citation and the published value.

    Rejects a file outside 3-8 entries, any entry with an empty cell in any of the four
    columns, and any duplicated `canonical_inchikey`.

    `roster_keys` enables a REPORTED cross-check against T18's roster; with
    `require_in_roster=False` (the default) a key outside the roster is legitimate and
    recorded in the frame's `in_roster` column rather than refused. Pass
    `require_in_roster=True` only if the principal has ruled that the reference set must
    be a roster subset — the plan's scope note says it must not be assumed.
    """
    path = Path(path)
    doc = yaml.safe_load(path.read_text())
    if not isinstance(doc, dict) or "compounds" not in doc:
        raise ReferenceCompoundError(f"{path} has no top-level `compounds` list")

    entries = doc["compounds"] or []
    if not (MIN_REFERENCE_ENTRIES <= len(entries) <= MAX_REFERENCE_ENTRIES):
        raise ReferenceCompoundError(
            f"{path} has {len(entries)} entries; T21 requires "
            f"{MIN_REFERENCE_ENTRIES}-{MAX_REFERENCE_ENTRIES}. Below the floor the M1 "
            "gate has too little to discriminate against, and the reported "
            "(alpha, k_sink) is substantially prior-determined (Finding E)."
        )

    for index, entry in enumerate(entries):
        for column in REFERENCE_COLUMNS:
            value = str((entry or {}).get(column) or "").strip()
            if not value:
                raise ReferenceCompoundError(
                    f"{path} entry {index} has an empty `{column}`. The published value "
                    "and the citation are both mandatory: an uncited transport "
                    "measurement cannot serve as an independent yardstick, and an "
                    "unkeyed entry cannot be joined."
                )

    # Built from STRIPPED values, for the reason S11a gives: validating the stripped
    # form while keeping the raw one lets " AAA" evade the duplicate check against
    # "AAA" and then fail every downstream join.
    frame = pd.DataFrame(
        [{c: str(e.get(c) or "").strip() for c in REFERENCE_COLUMNS} for e in entries]
    )

    duplicates = frame["canonical_inchikey"][frame["canonical_inchikey"].duplicated()]
    if not duplicates.empty:
        raise ReferenceCompoundError(
            f"{path} repeats canonical_inchikey: {sorted(set(duplicates))}. A duplicated "
            "key double-weights one compound in a set of at most eight."
        )

    if roster_keys is not None:
        frame["in_roster"] = frame["canonical_inchikey"].isin(set(roster_keys))
        if require_in_roster:
            outside = sorted(frame.loc[~frame["in_roster"], "canonical_inchikey"])
            if outside:
                raise ReferenceCompoundError(
                    f"{path} names {len(outside)} key(s) outside T18's roster while "
                    f"require_in_roster=True: {outside[:5]}" + (" ..." if len(outside) > 5 else "")
                )

    return frame.reset_index(drop=True)
