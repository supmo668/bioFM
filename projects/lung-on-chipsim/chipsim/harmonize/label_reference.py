"""Label/structure agreement — does a compound's NAME agree with its STRUCTURE?

Principal ruling via CTO #126. The snapshot carries rows whose D-/L- name prefix
contradicts the structure the row actually holds: measured across the 134 D-/L- prefixed
rows, **11 are genuine label errors on absolute rows** (ten "D-" amino acids carrying L
structures, plus one "L-" boronic-acid alanine keying as D). Those key identically before
and after the relative-stereo re-key, so the pipeline can only REPORT them.

The person exposed is the reviewer doing 60-90 minutes of P-gp adjudication while the
worksheet prints "D-Proline" beside an L structure. So the agreement verdict is a column
in the sheet they read, not a sentence in a limits document.

**Tri-state, never two-state.** 75 of those 134 rows cannot be resolved either way; forcing
them into "agrees" would be the silent-default failure this project keeps finding.

**Committed reference, never a live lookup.** A worksheet must regenerate identically
offline, and a network call inside human-artefact generation is a reproducibility hazard.
The table (`configs/label_structure_reference.yaml`) carries its retrieval date and the
admission rule that built it.

**It gates nothing.** Nothing is filtered, rejected or excluded on this verdict; the key is
right and the name is wrong, which is the opposite of a relative-stereo flag.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

#: The verdict domain, in the order the ruling names it (CTO #126 §2).
LABEL_AGREEMENT = ("disagrees", "agrees", "unresolved")

#: Required per entry. A partial entry is rejected rather than half-used: an entry missing
#: `d_inchikey` would silently make every D- row "unresolved" while looking populated.
_REQUIRED_ENTRY_KEYS = ("base_name", "l_inchikey", "d_inchikey")

_PREFIXES = {"l": "l_inchikey", "d": "d_inchikey"}


class LabelReferenceError(ValueError):
    """The label/structure reference table is missing, malformed, or undated."""


@dataclass(frozen=True)
class LabelReference:
    """Base name -> the two enantiomers' InChIKeys, with the provenance of the lookup."""

    retrieved_on: str
    source: str
    entries: dict[str, dict[str, str]]

    def keys_for(self, base_name: str) -> dict[str, str] | None:
        return self.entries.get(base_name.strip().lower())


def load_label_reference(path: str | Path) -> LabelReference:
    """Parse and validate the committed reference table.

    Raises rather than degrading: an undated table cannot be audited, and a table read as
    empty would report every row "unresolved" while looking like it had been consulted.
    """
    path = Path(path)
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise LabelReferenceError(f"{path} does not exist") from exc

    if not isinstance(doc, dict) or "entries" not in doc:
        raise LabelReferenceError(f"{path} is not a mapping with an `entries` list")

    retrieved_on = str(doc.get("retrieved_on") or "").strip()
    if not retrieved_on:
        raise LabelReferenceError(
            f"{path} has no `retrieved_on`. A structure reference without a retrieval date "
            "cannot be audited: the source moves, and a verdict computed from it would be "
            "uncheckable afterwards."
        )

    entries: dict[str, dict[str, str]] = {}
    for index, entry in enumerate(doc["entries"] or []):
        missing = [k for k in _REQUIRED_ENTRY_KEYS if not str((entry or {}).get(k) or "").strip()]
        if missing:
            raise LabelReferenceError(
                f"{path} entry {index} is missing {missing}. A partial entry would make its "
                "rows report `unresolved` while the table looked populated."
            )
        base = str(entry["base_name"]).strip().lower()
        l_key = str(entry["l_inchikey"]).strip()
        d_key = str(entry["d_inchikey"]).strip()
        if base in entries:
            raise LabelReferenceError(
                f"{path} lists base name {base!r} twice. The later entry would silently "
                "overwrite the earlier one."
            )
        if l_key == d_key:
            raise LabelReferenceError(
                f"{path} entry {base!r} has equal L and D keys. Every row on that base name "
                "would read `agrees`, the one verdict this column must never produce falsely."
            )
        charged = [k for k in (l_key, d_key) if not k.endswith("-N")]
        if charged:
            raise LabelReferenceError(
                f"{path} entry {base!r} carries charged-form key(s) {charged}. Pipeline keys "
                "are neutralised (-N), so a charged key can never match and the entry would "
                "report only `unresolved` while looking populated."
            )
        entries[base] = {"l_inchikey": l_key, "d_inchikey": d_key}

    return LabelReference(
        retrieved_on=retrieved_on,
        source=str(doc.get("source") or "").strip(),
        entries=entries,
    )


def label_agreement(name: str, canonical_inchikey: str, reference: LabelReference | None) -> str:
    """`disagrees` | `agrees` | `unresolved` for one row's name against its key.

    `unresolved` — never a false `agrees` — when: there is no reference; the name carries no
    D-/L- prefix (it asserts no configuration); the base name is not in the table; or the key
    matches NEITHER enantiomer (a salt, a different form, or a structure the table cannot
    speak to).
    """
    if reference is None or not isinstance(name, str) or not isinstance(canonical_inchikey, str):
        return "unresolved"

    text = name.strip()
    if len(text) < 3 or text[1] != "-" or text[0].lower() not in _PREFIXES:
        return "unresolved"

    claimed = _PREFIXES[text[0].lower()]
    keys = reference.keys_for(text[2:])
    if not keys:
        return "unresolved"

    key = canonical_inchikey.strip()
    other = "d_inchikey" if claimed == "l_inchikey" else "l_inchikey"
    if key == keys[claimed]:
        return "agrees"
    if key == keys[other]:
        return "disagrees"
    return "unresolved"


def aggregate_label_agreement(verdicts) -> str:
    """One verdict for a key from its member rows' verdicts (QG F-01).

    Several snapshot rows can share one canonical key. Judging only the first name let a
    correctly-named row hide a mislabelled one, and which one "won" depended on row order.
    `disagrees` if ANY member disagrees; `agrees` only if at least one agrees and none
    disagrees; otherwise `unresolved`.
    """
    seen = set(verdicts)
    unknown = seen - set(LABEL_AGREEMENT)
    if unknown:
        raise ValueError(f"not label-agreement verdicts: {sorted(unknown)}")
    if "disagrees" in seen:
        return "disagrees"
    if "agrees" in seen:
        return "agrees"
    return "unresolved"
