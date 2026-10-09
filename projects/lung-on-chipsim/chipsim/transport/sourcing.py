"""Literature-sourcing worksheet for the M1 inputs — the intake path for T20, T28, T21.

The principal's instruction of 2026-10-08 amended Global Constraint #1 for the M1 inputs:
they may be drafted from cited sources rather than hand-written, under one condition stated
in the principal's own words — *"Unbacked data cannot be used and reference must be cited in
the experimental design."* This module is that condition, mechanized.

A worksheet row names a field the model needs and the source a value should come from. It
carries the value, the DOI and the **verbatim quote** the value was read out of. The rule it
enforces is one-directional and blunt:

> **A row may be empty. A row may not carry a value without the quote that backs it.**

That asymmetry is the whole design. An empty row is honest work-in-progress; a filled row
with no quote is an unbacked number, and an unbacked number is indistinguishable from a
measured one by the time it reaches the fit. This is the same shape as T13's adjudication
worksheet, for the same reason: the expensive failure is not a missing value, it is a present
one nobody can trace.

`provenance` records HOW the value was obtained, because "cited" and "computed from cited
values" are different claims and a reader is owed the difference:

- `cited` — read verbatim out of the source. Requires `quote` and `doi`.
- `derived` — computed from quoted values by a stated formula. Requires `quote`, `doi` and
  `derivation`; the quote must be of the inputs, since the derived number appears nowhere.
- `assumed` — no citable value was found. Requires `assumed_width` and forbids a `quote`,
  because quoting something for a value you are admitting is unsourced is worse than silence.

Nothing in this module writes a value. It reads a worksheet and refuses the inadmissible.
"""

from __future__ import annotations

from pathlib import Path

import yaml

#: The provenance classes a filled row may declare.
PROVENANCE_CLASSES = ("cited", "derived", "assumed")

#: Keys a row may carry. `target` and `locate` are the fetch queue: which document, and where
#: inside it the number lives. They are bibliographic, so an agent may write them.
ROW_KEYS = (
    "field",
    "needs",
    "unit",
    "value",
    "provenance",
    "doi",
    "doi_confirmed",
    "quote",
    "derivation",
    "assumed_width",
    "source",
    "target",
    "locate",
    "note",
)

#: Rows must declare which input they feed, so a worksheet cannot drift from the schema it
#: serves without the mismatch being visible.
GROUPS = ("theta", "transport_prior", "reference_compounds")


class SourcingError(RuntimeError):
    """A sourcing worksheet carries a value that is not backed as it claims to be."""


def _blank(value: object) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _check_row(group: str, index: int, row: object) -> dict:
    where = f"{group}[{index}]"
    if not isinstance(row, dict):
        raise SourcingError(f"{where} is not a mapping; got {type(row).__name__}.")

    unknown = sorted(set(row) - set(ROW_KEYS))
    if unknown:
        raise SourcingError(
            f"{where} carries unknown key(s) {unknown}. Permitted: {list(ROW_KEYS)}."
        )
    if _blank(row.get("field")):
        raise SourcingError(f"{where} has no `field`: a row that names nothing cannot be filled.")

    field = str(row["field"]).strip()
    if _blank(row.get("value")):
        # An empty row is the honest state of unfinished work. It is not an error, and it
        # carries no claim, so nothing below applies to it.
        return dict(row)

    provenance = str(row.get("provenance") or "").strip()
    if provenance not in PROVENANCE_CLASSES:
        raise SourcingError(
            f"{where} (`{field}`) carries a value with `provenance: {provenance or 'missing'}`. "
            f"A filled row must declare one of {list(PROVENANCE_CLASSES)}: how a number was "
            "obtained is part of the number."
        )

    if provenance == "assumed":
        if _blank(row.get("assumed_width")):
            raise SourcingError(
                f"{where} (`{field}`) is `assumed` with no `assumed_width`. An assumption whose "
                "width is not stated cannot be propagated, so it is a guess, not an assumption."
            )
        if not _blank(row.get("quote")):
            raise SourcingError(
                f"{where} (`{field}`) is `assumed` but carries a `quote`. If there is a quote the "
                "value is `cited` or `derived`; quoting a source for a value you are calling "
                "unsourced misrepresents both."
            )
        return dict(row)

    # cited | derived — both are claims ON a source, so both need the source and the words.
    if _blank(row.get("quote")):
        raise SourcingError(
            f"{where} (`{field}`) is `{provenance}` with an empty `quote`. Unbacked data cannot "
            "be used (principal, 2026-10-08): paste the sentence or table cell the value was "
            "read out of, so a reader can check the number against its source rather than "
            "against this file."
        )
    if _blank(row.get("doi")):
        raise SourcingError(
            f"{where} (`{field}`) is `{provenance}` with an empty `doi`. A quote with no "
            "locator cannot be resolved, and an unresolvable citation passes every schema "
            "check ever written."
        )
    if row.get("doi_confirmed") is not True:
        raise SourcingError(
            f"{where} (`{field}`) has `doi_confirmed` unset. Set it true only after resolving "
            "the DOI against a fetched page: a DOI copied from a search summary or from memory "
            "is exactly the fabricated citation this project is built to refuse."
        )
    if provenance == "derived" and _blank(row.get("derivation")):
        raise SourcingError(
            f"{where} (`{field}`) is `derived` with no `derivation`. State the formula and the "
            "quoted inputs: the derived number appears in no source, so the arithmetic is the "
            "only thing a reader can check."
        )
    return dict(row)


def load_sourcing_worksheet(path: Path) -> dict[str, list[dict]]:
    """Parse and validate a sourcing worksheet, or raise.

    Returns the rows grouped by the input they feed. Rows with an empty `value` are returned
    as-is: the worksheet is designed to be committed half-finished, because the alternative is
    somebody filling it in one sitting from whatever is to hand.
    """
    path = Path(path)
    doc = yaml.safe_load(path.read_text())
    if not isinstance(doc, dict) or "worksheet" not in doc:
        raise SourcingError(f"{path} has no top-level `worksheet` mapping.")

    raw = doc["worksheet"]
    if not isinstance(raw, dict):
        raise SourcingError(f"{path}: `worksheet` is not a mapping.")
    unknown = sorted(set(raw) - set(GROUPS))
    if unknown:
        raise SourcingError(
            f"{path} declares unknown group(s) {unknown}. Permitted: {list(GROUPS)}."
        )

    out: dict[str, list[dict]] = {}
    for group in GROUPS:
        rows = raw.get(group) or []
        if not isinstance(rows, list):
            raise SourcingError(f"{path}: `worksheet.{group}` is not a list.")
        out[group] = [_check_row(group, i, r) for i, r in enumerate(rows)]
    return out


def completion_report(worksheet: dict[str, list[dict]]) -> dict[str, dict[str, int]]:
    """Per group: how many rows are filled, and under which provenance class.

    Reported, never gated. A worksheet that is mostly empty is the honest state of a set-up
    whose sources could not be reached; turning that into a failure would only encourage
    filling it.
    """
    report: dict[str, dict[str, int]] = {}
    for group, rows in worksheet.items():
        counts = {"rows": len(rows), "filled": 0, "empty": 0}
        counts.update({c: 0 for c in PROVENANCE_CLASSES})
        for row in rows:
            if _blank(row.get("value")):
                counts["empty"] += 1
                continue
            counts["filled"] += 1
            counts[str(row["provenance"]).strip()] += 1
        report[group] = counts
    return report
