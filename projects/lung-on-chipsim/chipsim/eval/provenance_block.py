"""Data-provenance display block — build-plan T17.

Changed from (edit) to (new) in r2: `chipsim/eval/card.py` did not exist and no
plan creates it; M0c owns the card (defect 13). This module builds the block and
unit-tests it; wiring it into the card moves to M0c.

**The version string is COMPOSED from `upstream_version` + `snapshot_date`, never
hard-coded (defect 14).** A hard-coded "DrugBank 4.2 (2015-03-19 snapshot)" keeps
rendering the old value after the snapshot is re-pinned, which turns the card into
a confident false statement. T17's done-condition falsifies exactly that: changing
`upstream_version` in the fixture must change the rendered string.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from chipsim.harmonize.adjudication import ADJUDICATED_LABELS
from chipsim.harmonize.contracts import check_provenance, load_provenance


def format_source_version(upstream_version: str, snapshot_date: str) -> str:
    """`DrugBank <version> (<date> snapshot)` — composed, never a literal."""
    return f"DrugBank {upstream_version} ({snapshot_date} snapshot)"


def label_counts(labels: pd.Series) -> dict[str, int]:
    """Counts for every label in the domain, including zeros.

    Missing keys would make the caller's formatting branch on presence; an
    explicit zero keeps `pgp_groups_usable` honest.

    REFUSES anything outside the domain rather than projecting onto it. Projecting
    silently discards NaN, casing variants ('Yes') and stray verdicts, so the card
    — the audit surface — would render counts summing to less than the cohort and
    state them with total confidence.
    """
    outside = sorted({str(v) for v in labels.dropna().unique()} - ADJUDICATED_LABELS)
    if outside:
        raise ValueError(
            f"labels carry value(s) outside {sorted(ADJUDICATED_LABELS)}: {outside}. "
            "Refusing to render a provenance block whose counts would silently omit them."
        )
    if labels.isna().any():
        raise ValueError(
            f"labels carry {int(labels.isna().sum())} null value(s); a null is neither "
            "a verdict nor an 'unknown' and must not vanish from the counts."
        )

    counts = labels.value_counts().to_dict()
    resolved = {label: int(counts.get(label, 0)) for label in sorted(ADJUDICATED_LABELS)}
    if sum(resolved.values()) != len(labels):
        raise ValueError(
            f"label counts sum to {sum(resolved.values())} but the cohort has {len(labels)} rows"
        )
    return resolved


def pgp_groups_usable(counts: dict[str, int]) -> bool:
    """The M5 grouping variable needs BOTH contrast groups populated (defect 24).

    Computed from the counts rather than asserted separately, so the rendered
    flag can never disagree with the rendered numbers.
    """
    return counts.get("yes", 0) > 0 and counts.get("no", 0) > 0


def render_data_provenance(provenance: Path, labels: pd.Series) -> str:
    """Composes the display string FROM upstream_version + snapshot_date —
    never hard-coded (defect 14). Renders source, commit, licence, the three
    label counts, and pgp_groups_usable computed from those counts (defect 24).
    """
    doc = load_provenance(Path(provenance))
    check_provenance(doc)

    counts = label_counts(labels)
    usable = pgp_groups_usable(counts)

    lines = [
        "## Data provenance",
        "",
        f"- **Source:** {format_source_version(doc['upstream_version'], doc['snapshot_date'])}",
        f"- **Repository:** {doc['source_repo']}",
        f"- **Commit:** {doc['source_commit']}",
        f"- **Licence:** {doc['licence']}",
        "- **Attribution:**",
    ]
    lines += [f"    - {entry}" for entry in doc["attribution"]]

    if doc["source_commit"] != doc["audited_commit"]:
        lines += [
            f"- **Audited commit:** {doc['audited_commit']}",
            f"- **Commit substitution rationale:** {doc['commit_change_rationale']}",
        ]

    lines += [
        "",
        "### P-gp label coverage",
        "",
        f"- yes: {counts['yes']}",
        f"- no: {counts['no']}",
        f"- unknown: {counts['unknown']}",
        f"- pgp_groups_usable: {str(usable).lower()}",
    ]
    if not usable:
        lines.append(
            "- _Both the 'yes' and 'no' groups must be populated for the M5 "
            "grouping variable to be usable._"
        )
    return "\n".join(lines)
