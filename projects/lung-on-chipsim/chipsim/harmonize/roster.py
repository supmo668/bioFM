"""PoC compound roster validation — build-plan S11a (paired with T18).

T18 is human-owned: which 20-40 compounds are "lung-relevant with published
exposure" is a CLAIM, so an auto-filter of drugbank-slim.tsv is not a substitute.
This module only VALIDATES a roster a human wrote. It never generates one.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from chipsim.harmonize.label_reference import LabelReference, label_agreement

MIN_ROSTER_ENTRIES = 20
MAX_ROSTER_ENTRIES = 40

ROSTER_COLUMNS = ("canonical_inchikey", "name", "evidence_doi")


class RosterValidationError(ValueError):
    """A PoC roster violates S11a's contract."""


def load_poc_roster(
    path: Path,
    snapshot_keys: set[str] | None = None,
    *,
    relative_stereo_keys: set[str] | frozenset[str] | None = None,
    allow_relative_stereo: bool = False,
) -> pd.DataFrame:
    """Parse and validate the roster. Identity and citation only — no biology.

    Rejects a roster outside 20-40 entries, any entry with an empty
    `canonical_inchikey` or `evidence_doi`, and (when `snapshot_keys` is given)
    any key absent from the snapshot.

    `snapshot_keys` is optional so the size/emptiness rules stay testable while
    T2/T4a are outstanding and there is no snapshot to resolve against.

    **Relative-stereo keys (principal ruling 2026-09-15, CTO #122 §0).** When
    `relative_stereo_keys` is given (see `chipsim.harmonize.ids.relative_stereo_keys`),
    a roster naming any of them is REJECTED, listing the offending keys, unless
    `allow_relative_stereo=True`. "A diversity stratum cannot rest on identities the
    source leaves unspecified." Rejected, never silently filtered: the roster is a
    human claim, and this module validates it — it never rewrites it.
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

    if relative_stereo_keys is not None and not allow_relative_stereo:
        flagged = sorted(set(frame["canonical_inchikey"]) & set(relative_stereo_keys))
        if flagged:
            raise RosterValidationError(
                f"{path} names {len(flagged)} canonical_inchikey(s) whose identity rests on "
                f"relative-stereo source structures: {flagged[:5]}"
                + (" ..." if len(flagged) > 5 else "")
                + ". Their absolute configuration is unspecified at source, so they are keyed "
                "stereo-free (principal ruling 2026-09-15, CTO #122 §0) and a diversity "
                "stratum cannot rest on them. Remove them, or pass "
                "allow_relative_stereo=True to accept that deliberately."
            )

    return frame.reset_index(drop=True)


def roster_label_disagreements(
    roster: pd.DataFrame, reference: LabelReference | None
) -> list[tuple[str, str]]:
    """`(canonical_inchikey, name)` for every roster entry whose D-/L- name contradicts its key.

    CTO #126 §3: REPORTED, never rejected. Unlike a relative-stereo key, a label disagreement
    leaves the identity right (the key is right and the name is wrong), so validation lists
    it for the human who wrote the roster and does not refuse the roster. With no reference
    there is nothing to judge against, so nothing is reported rather than guessed.
    """
    if reference is None:
        return []
    return [
        (key, name)
        for key, name in zip(roster["canonical_inchikey"], roster["name"], strict=True)
        if label_agreement(name, key, reference) == "disagrees"
    ]
