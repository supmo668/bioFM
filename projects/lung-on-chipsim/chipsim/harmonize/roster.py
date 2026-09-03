"""PoC compound roster validation — build-plan S11a (paired with T18).

T18 is human-owned: which 20-40 compounds are "lung-relevant with published
exposure" is a CLAIM, so an auto-filter of drugbank-slim.tsv is not a substitute.
This module only VALIDATES a roster a human wrote. It never generates one.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

MIN_ROSTER_ENTRIES = 20
MAX_ROSTER_ENTRIES = 40

ROSTER_COLUMNS = ("canonical_inchikey", "name", "evidence_doi")


class RosterValidationError(ValueError):
    """A PoC roster violates S11a's contract."""


def load_poc_roster(path: Path, snapshot_keys: set[str] | None = None) -> pd.DataFrame:
    """Parse and validate the roster. Identity and citation only — no biology.

    Rejects a roster outside 20-40 entries, any entry with an empty
    `canonical_inchikey` or `evidence_doi`, and (when `snapshot_keys` is given)
    any key absent from the snapshot.

    `snapshot_keys` is optional so the size/emptiness rules stay testable while
    T2/T4a are outstanding and there is no snapshot to resolve against.
    """
    path = Path(path)
    doc = yaml.safe_load(path.read_text())
    if not isinstance(doc, dict) or "compounds" not in doc:
        raise RosterValidationError(f"{path} has no top-level `compounds` list")

    entries = doc["compounds"] or []
    if not (MIN_ROSTER_ENTRIES <= len(entries) <= MAX_ROSTER_ENTRIES):
        raise RosterValidationError(
            f"{path} has {len(entries)} entries; S11a requires "
            f"{MIN_ROSTER_ENTRIES}-{MAX_ROSTER_ENTRIES}."
        )

    for index, entry in enumerate(entries):
        for column in ROSTER_COLUMNS:
            value = str((entry or {}).get(column) or "").strip()
            if not value:
                raise RosterValidationError(
                    f"{path} entry {index} has an empty `{column}`. "
                    "Identity and citation are both mandatory: an uncited roster entry "
                    "cannot be audited, and an unkeyed one cannot be joined."
                )

    # Built from STRIPPED values. Validating the stripped form but keeping the raw
    # one lets " AAA" pass validation, evade the duplicate check against "AAA", and
    # then silently fail every downstream join.
    frame = pd.DataFrame(
        [{c: str(e.get(c) or "").strip() for c in ROSTER_COLUMNS} for e in entries]
    )

    duplicates = frame["canonical_inchikey"][frame["canonical_inchikey"].duplicated()]
    if not duplicates.empty:
        raise RosterValidationError(
            f"{path} repeats canonical_inchikey: {sorted(set(duplicates))}. "
            "A duplicated key double-weights one compound in the PoC."
        )

    if snapshot_keys is not None:
        absent = sorted(set(frame["canonical_inchikey"]) - set(snapshot_keys))
        if absent:
            raise RosterValidationError(
                f"{path} names {len(absent)} canonical_inchikey(s) absent from the "
                f"parsed snapshot: {absent[:5]}" + (" ..." if len(absent) > 5 else "")
            )

    return frame.reset_index(drop=True)
