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

import re
from pathlib import Path

import pandas as pd
import yaml

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


def render_data_provenance(provenance: Path, labels: pd.Series, panel: Path | None) -> str:
    """Composes the display string FROM upstream_version + snapshot_date —
    never hard-coded (defect 14). Renders source, commit, licence, the three
    label counts, and pgp_groups_usable computed from those counts (defect 24).

    `panel` has **no default, on purpose.** It used to default to None, which
    dropped the entire ratification section from the card — heading included —
    whenever a caller simply forgot it. The resulting card was not merely
    incomplete: it was a card with nothing to say about ratification, which is
    indistinguishable to a reader from a card about a system that has no such
    concern. There is no production caller yet, so the first one is still to be
    written; a default that makes forgetting invisible is worst precisely then.

    Passing None is still allowed and now RENDERS — as an explicit statement that
    no panel was supplied. Omission has to be visible in the output, or the
    argument is back to being optional in everything but name.
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

    if panel is not None:
        lines += ["", *render_panel_ratification(Path(panel))]
    else:
        lines += [
            "",
            "### Barrier panel ratification",
            "",
            _PANEL_NOT_SUPPLIED,
        ]

    return "\n".join(lines)


# The three NOT-RATIFIED headlines and their shared consequence line. Named
# rather than repeated inline: the consequence sentence was previously written
# out three times, and a sentence maintained in triplicate is a sentence that
# will eventually disagree with itself in one of the three branches.
_NOT_RATIFIED_ABSENT = (
    "- **Status: NOT RATIFIED.** The panel states no ratification at all — the "
    "`ratified` key is absent, which is treated exactly like `false`."
)
_NOT_RATIFIED_UNATTRIBUTED = (
    "- **Status: NOT RATIFIED.** The panel claims `ratified: true` but records no "
    "ratifier. An unattributable ratification is not a ratification, and every "
    "other component refuses it."
)
_NOT_RATIFIED_FALSE = (
    "- **Status: NOT RATIFIED.** The panel ships `ratified: false`; no human has "
    "verified the accessions or the membrane faces."
)
#: A sha256 digest, rendered lowercase-hex by `panel_digest`.
_SHA256_HEX = re.compile(r"[0-9a-f]{64}")

_PANEL_NOT_SUPPLIED = (
    "- **Not supplied.** This card was rendered without a barrier panel, so it "
    "makes no claim about ratification either way. If the analysis behind this "
    "card used a panel, this section is missing and the card is wrong."
)
_DOWNSTREAM_REFUSES = (
    "- Downstream joins refuse to run against it, so no result in this card "
    "depends on the panel's contents."
)


def render_panel_ratification(panel: Path) -> list[str]:
    """The barrier panel's ratification status **and the exact limits of its seal**.

    This section exists because the card is where an overclaim would do the most
    damage: a reader meets the seal here, not in the source, and "ratified" plus a
    digest reads as proof a human checked the accessions unless the card says
    otherwise. It does not prove that, and every sentence here is bounded on
    purpose. **Do not let this wording grow.**

    What the seal does: detects modification of the panel or its ratification
    fields after sealing.

    What it does not do, and cannot: establish WHO ratified or sealed. The digest
    is unkeyed over public content, so anything able to write the panel can
    recompute it. Removing the seal line is refused by `load_ratified_panel`, but
    that is a check on the reader's side, not evidence about the writer's.

    The TTY gate and the confirmation read raise the floor from *accidentally
    reachable* to *deliberately circumvented* — an agent that allocates a pty and
    writes to it defeats both, which is neither hard nor exotic. That is the whole
    claim; real signing with a human-held key is a v2 decision and is not in force.
    """
    from chipsim.harmonize.pgp_label import load_ratified_panel

    panel = Path(panel)
    try:
        doc = yaml.safe_load(panel.read_text(encoding="utf-8"))
    except OSError as exc:
        raise RuntimeError(f"panel {panel} could not be read: {exc}") from exc
    if not isinstance(doc, dict):
        # RuntimeError, matching load_ratified_panel's family, so a caller can
        # catch one exception type for "this panel is unusable".
        raise RuntimeError(  # noqa: TRY004
            f"panel {panel} did not parse to a mapping (got {type(doc).__name__})"
        )

    states_ratification = "ratified" in doc
    by = str(doc.get("ratified_by") or "").strip()
    sealed = str(doc.get("ratified_panel_sha256") or "").strip()

    # An unattributable ratification is not a ratification — `load_ratified_panel`
    # refuses one and `seal_panel` will not seal one, so the card must not print
    # the word "ratified" for a panel every other component rejects. Rendering it
    # as ratified-with-a-caveat put the strongest word in the section on the
    # weakest evidence.
    ratified = doc.get("ratified") is True and bool(by)

    out = ["### Barrier panel ratification", ""]
    if not ratified:
        if not states_ratification:
            # Absence is not consent: report what the file does, rather than
            # asserting it "ships ratified: false" when it ships no such key.
            return out + [
                _NOT_RATIFIED_ABSENT,
                _DOWNSTREAM_REFUSES,
            ]
        if doc.get("ratified") is True and not by:
            return out + [
                _NOT_RATIFIED_UNATTRIBUTED,
                _DOWNSTREAM_REFUSES,
            ]
        return out + [
            _NOT_RATIFIED_FALSE,
            _DOWNSTREAM_REFUSES,
        ]

    # *** VERIFY THE SEAL. DO NOT MERELY PRINT IT. ***
    #
    # This section previously read `ratified_panel_sha256` as a string and
    # truncated it for display without ever checking it. A panel with one `face`
    # flipped AFTER sealing — precisely the tamper the seal exists to detect —
    # rendered a BYTE-IDENTICAL card, four lines above the sentence claiming the
    # seal detects modification. The loader refused that same file. A rendered
    # digest under a heading promising detection is a claim; printing one you have
    # not checked makes the section most misleading exactly where it is most
    # emphatic.
    safe_by = by.replace("`", "'")
    out += [f"- **Status: ratified** by `{safe_by}`"]

    if not sealed:
        out.append(
            "- **Seal: ABSENT** — a ratified panel must be sealed; treat this as unratified."
        )
    elif not _SHA256_HEX.fullmatch(sealed):
        # A seal that is not a sha256 digest is not a digest, and must not be
        # rendered as one. `str(doc.get(...))` on `ratified_panel_sha256: true`
        # produced `- **Seal:** \`True…\``, and on a 3-character value `\`abc…\`` —
        # the trailing ellipsis is the tell, because it announces the truncation
        # of a 64-hex digest that was never there. A reader who sees a plausible
        # digest stops checking. Show the value's SHAPE instead of dressing it up
        # as the thing it failed to be.
        out.append(
            f"- **Seal: MALFORMED** — `ratified_panel_sha256` is not a 64-character "
            f"hex digest (got {len(sealed)} characters). Nothing was verified; treat "
            "this panel as unsealed."
        )
    else:
        try:
            load_ratified_panel(panel)
            out.append(f"- **Seal: verified** — `{sealed[:16]}…`")
        except RuntimeError:
            out.append(
                f"- **Seal: PRESENT BUT FAILS VERIFICATION** — recorded `{sealed[:16]}…`, "
                "which does not match the panel's current contents. The panel was edited "
                "after it was sealed; do not rely on anything below that depends on it."
            )
    out += [
        "",
        (
            "**What the seal establishes, exactly.** It detects modification of the "
            "panel or its ratification fields after sealing. It does **not** establish "
            "who ratified or sealed it: the digest is unkeyed over public content, so "
            "anything able to write the panel can recompute it."
        ),
        "",
        (
            "**The sealing command requires an interactive terminal and a typed "
            "confirmation.** This raises the floor from accidentally reachable to "
            "deliberately circumvented — an agent that allocates a pty and writes to "
            "it defeats both. It is not authentication and is not evidence a human "
            "sealed anything. Signing with a human-held key is deferred."
        ),
    ]
    return out
