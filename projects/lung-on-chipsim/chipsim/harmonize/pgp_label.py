"""Barrier-panel join and the three-way P-gp label — build-plan T9, T10.

Two invariants carry this module, and both exist because their absence fails
SILENTLY rather than loudly:

1. **Absence is not consent (defect 1).** The panel is usable only when a human
   has ratified it. A MISSING `ratified` key raises, exactly like `ratified:
   false` — an unratified panel and a panel that forgot to say are the same thing.

2. **Absence of evidence is not evidence of absence (defect 4).** A compound with
   no ABCB1 edge is `'unknown'`, never `'no'`. `'no'` is a positive claim and is
   assignable only by `adjudicate_pgp_labels()` (T15) with a citation.

The ABCB1 accession is resolved FROM the ratified panel by symbol. It is never
hard-coded (AM-2: composition is configuration, not code) — hard-coding P08183
is how defect 4's silent degradation survived review.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

#: The symbol T10 resolves out of the panel. The SYMBOL is the constant here;
#: the accession deliberately is not.
ABCB1_SYMBOL = "ABCB1"

#: Only a transporter-category edge supports a substrate claim. An ABCB1 *enzyme*
#: edge says something different and must not read as substrate evidence.
SUBSTRATE_CATEGORY = "transporter"

#: The pre-adjudication label domain. 'no' is absent BY CONSTRUCTION.
PRE_ADJUDICATION_LABELS = frozenset({"yes", "unknown"})

PANEL_EDGE_COLUMNS = ("drugbank_id", "uniprot_id", "symbol", "category", "face")


def load_ratified_panel(panel_path: Path) -> dict:
    """Parse a barrier panel and REFUSE it unless a human ratified it.

    Raises RuntimeError unless `ratified` is present AND True AND `ratified_by`
    is non-empty. A missing key raises — absence is not consent (defect 1).
    """
    panel_path = Path(panel_path)
    doc = yaml.safe_load(panel_path.read_text())
    if not isinstance(doc, dict):
        # RuntimeError, not TypeError: every "this panel is unusable" failure in
        # this module is a RuntimeError so callers can catch one family. A panel
        # that does not parse is unusable for the same reason an unratified one is.
        raise RuntimeError(  # noqa: TRY004
            f"{panel_path} did not parse to a mapping (got {type(doc).__name__})"
        )

    if "ratified" not in doc:
        raise RuntimeError(
            f"{panel_path} has no `ratified` key. Absence is not consent (defect 1): "
            "a panel that does not say it was ratified is treated exactly like one "
            "that says it was not."
        )
    if doc["ratified"] is not True:
        raise RuntimeError(
            f"{panel_path} is not ratified (ratified={doc['ratified']!r}). "
            "A human must verify the accessions in T8 before any join uses them; a "
            "wrong accession empties the join and yields an empty, not a wrong, result."
        )

    ratified_by = doc.get("ratified_by") or ""
    if not str(ratified_by).strip():
        raise RuntimeError(
            f"{panel_path} claims ratified: true but `ratified_by` is empty. "
            "An unattributable ratification is not a ratification."
        )

    panel = doc.get("panel") or []
    if not panel:
        raise RuntimeError(f"{panel_path} has an empty panel")
    return doc


def barrier_panel_edges(edges: pd.DataFrame, panel_path: Path) -> pd.DataFrame:
    """Inner-join protein edges onto the ratified panel.

    Raises RuntimeError unless ratified is True AND ratified_by is non-empty.
    A MISSING `ratified` key raises — absence is not consent (defect 1).
    Columns: drugbank_id, uniprot_id, symbol, category, face.
    """
    doc = load_ratified_panel(panel_path)
    panel = pd.DataFrame(doc["panel"]).rename(columns={"uniprot": "uniprot_id"})

    joined = edges.merge(
        panel.loc[:, ["uniprot_id", "symbol", "face"]], on="uniprot_id", how="inner"
    )
    return joined.loc[:, list(PANEL_EDGE_COLUMNS)].reset_index(drop=True)


def resolve_panel_accession(panel_path: Path, symbol: str) -> str:
    """Look up an accession in the ratified panel BY SYMBOL.

    Raises RuntimeError if the symbol is absent. T8 explicitly permits a human to
    delete or re-accession an entry, so this must raise rather than fall back to a
    hard-coded accession — otherwise a deleted ABCB1 silently labels everything
    'unknown' and the degradation is invisible (defect 4).
    """
    doc = load_ratified_panel(panel_path)
    for entry in doc["panel"]:
        if entry.get("symbol") == symbol:
            accession = str(entry.get("uniprot") or "").strip()
            if not accession:
                raise RuntimeError(f"panel entry {symbol} has an empty `uniprot`")
            return accession
    raise RuntimeError(
        f"the ratified panel at {panel_path} has no {symbol} entry. "
        "Refusing to label: without it every compound would come back 'unknown', "
        "which is indistinguishable from a genuine absence of evidence (defect 4)."
    )


def pgp_substrate_label(
    compounds: pd.DataFrame,
    panel_edges: pd.DataFrame,
    panel_path: Path,
) -> pd.Series:
    """Index: canonical_inchikey. Values: 'yes' | 'unknown'.

    Resolves the ABCB1 accession FROM THE RATIFIED PANEL by symbol == 'ABCB1'.
    Never hard-codes P08183 (defect 4 / AM-2: composition is configuration, not code).
    Raises RuntimeError if the ratified panel has no ABCB1 entry.

    'yes'      -> an ABCB1 edge of category 'transporter' exists in the snapshot.
    'unknown'  -> no such edge. NEVER returns 'no' from absence of evidence.

    'no' is assignable only by adjudicate_pgp_labels() with a citation.
    """
    if "canonical_inchikey" not in compounds.columns:
        raise ValueError(
            "compounds must carry `canonical_inchikey` — run add_canonical_identity() "
            "(T5b) first. Labelling on the raw snapshot key splits salts from their "
            "free bases and undercounts silently."
        )

    accession = resolve_panel_accession(panel_path, ABCB1_SYMBOL)

    substrate_edges = panel_edges[
        (panel_edges["uniprot_id"] == accession) & (panel_edges["category"] == SUBSTRATE_CATEGORY)
    ]
    substrate_ids = set(substrate_edges["drugbank_id"])

    frame = compounds.loc[:, ["canonical_inchikey", "drugbank_id"]].copy()
    frame["is_substrate"] = frame["drugbank_id"].isin(substrate_ids)

    # A canonical key may map to several drugbank_ids (a salt and its free base).
    # Evidence on ANY of them is evidence for the compound, so aggregate with any().
    collapsed = frame.groupby("canonical_inchikey")["is_substrate"].any()

    labels = collapsed.map(lambda hit: "yes" if hit else "unknown")
    labels.name = "snapshot_label"
    labels.index.name = "canonical_inchikey"

    # Structural guarantee, not a hopeful comment: 'no' cannot be produced here.
    assert set(labels.unique()) <= PRE_ADJUDICATION_LABELS, (
        f"pre-adjudication labels escaped their domain: {sorted(set(labels.unique()))}"
    )
    return labels
