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

import hashlib
import json
from pathlib import Path

import pandas as pd
import yaml

#: The key holding the seal. Written ONLY by a human running `chipsim panel seal`
#: (Global Constraint 4) — running the seal IS the act of attestation.
SEAL_KEY = "ratified_panel_sha256"

#: The symbol T10 resolves out of the panel. The SYMBOL is the constant here;
#: the accession deliberately is not.
ABCB1_SYMBOL = "ABCB1"

#: Only a transporter-category edge supports a substrate claim. An ABCB1 *enzyme*
#: edge says something different and must not read as substrate evidence.
SUBSTRATE_CATEGORY = "transporter"

#: The pre-adjudication label domain. 'no' is absent BY CONSTRUCTION.
PRE_ADJUDICATION_LABELS = frozenset({"yes", "unknown"})

PANEL_EDGE_COLUMNS = ("drugbank_id", "uniprot_id", "symbol", "category", "face")

#: Legal membrane faces. The binary is a PoC modelling choice, not biology: FcRn
#: transcytoses bidirectionally and UniProt gives SLCO2B1 as basal, basolateral
#: AND apical. M1 may widen this when directional transport actually consumes the
#: field; until a consumer exists, widening a tested schema buys nothing.
FACES = frozenset({"apical", "basolateral"})


def panel_digest(panel: list[dict]) -> str:
    """sha256 over the canonically-serialized panel list — build-plan T7a.

    Canonical means: entry keys sorted, entries ordered by `symbol`, compact
    separators, UTF-8. Serialization must not depend on YAML formatting, key order
    or comment churn, or the digest would change when nothing attested changed and
    a human would learn to ignore the mismatch.

    Only the panel LIST is hashed, deliberately. The attestation fields
    (`ratified`, `ratified_by`, `ratified_on`) and the seal itself are excluded:
    hashing them would make the digest depend on its own value, and re-attributing
    a ratification must not read as tampering with the accessions.
    """
    canonical = sorted(
        ({str(k): entry[k] for k in sorted(entry)} for entry in panel),
        key=lambda e: str(e.get("symbol", "")),
    )
    blob = json.dumps(canonical, separators=(",", ":"), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def seal_panel(panel_path: Path) -> str:
    """Write `ratified_panel_sha256` into a RATIFIED panel and return it — T7a.

    *** A HUMAN RUNS THIS. Global Constraint (4): running the seal is the act of
    attestation, so an agent must never invoke it against the live
    configs/barrier_panel.yaml. Agents build and test it against fixtures only. ***

    Raises RuntimeError if the panel is not ratified (done-condition 3). Without
    that refusal a digest could be produced while `ratified: false`, yielding an
    attestation record that binds nothing a human signed — which is worse than no
    seal at all, because it LOOKS like one.

    Idempotent: sealing an already-sealed, unmodified panel rewrites the same
    digest (done-condition 2).
    """
    panel_path = Path(panel_path)
    doc = yaml.safe_load(panel_path.read_text())
    if not isinstance(doc, dict):
        raise RuntimeError(  # noqa: TRY004
            f"{panel_path} did not parse to a mapping (got {type(doc).__name__})"
        )
    if doc.get("ratified") is not True or not str(doc.get("ratified_by") or "").strip():
        raise RuntimeError(
            f"refusing to seal {panel_path}: it is not ratified "
            f"(ratified={doc.get('ratified')!r}, ratified_by="
            f"{doc.get('ratified_by')!r}). The seal records an attestation; sealing "
            "an unratified panel would bind a digest to something no human signed."
        )

    digest = panel_digest(doc.get("panel") or [])

    # Rewrite the seal line in place rather than re-dumping the document: the file
    # carries the human-facing T8 instructions as comments, and yaml.safe_dump
    # would silently delete every one of them.
    text = panel_path.read_text()
    line = f"{SEAL_KEY}: {digest}"
    if f"{SEAL_KEY}:" in text:
        out = "\n".join(
            line if ln.startswith(f"{SEAL_KEY}:") else ln for ln in text.splitlines()
        )
        out += "\n" if text.endswith("\n") else ""
    else:
        # Insert immediately after ratified_on so the attestation block stays together.
        lines = text.splitlines()
        for i, ln in enumerate(lines):
            if ln.startswith("ratified_on:"):
                lines.insert(i + 1, line)
                break
        else:
            lines.append(line)
        out = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    panel_path.write_text(out)
    return digest


def load_ratified_panel(panel_path: Path) -> dict:
    """Parse a barrier panel and REFUSE it unless a human ratified it.

    Raises RuntimeError unless `ratified` is present AND True AND `ratified_by`
    is non-empty. A missing key raises — absence is not consent (defect 1).
    If a seal is present it must MATCH: a post-ratification edit to any entry
    invalidates the attestation (T7a done-condition 1).
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

    # Per-entry schema validation. Without this, a SINGLE entry missing `face`
    # does not raise: pd.DataFrame over a list of dicts fills the missing key
    # with NaN, and that NaN flows out through PANEL_EDGE_COLUMNS into the joined
    # frame with no error. Only an ALL-entries-missing key raises KeyError. A
    # human editing this file at T8 is exactly who would drop one key from one
    # row, and the failure would surface far downstream as a missing membrane
    # face rather than here as a malformed panel.
    required = ("symbol", "uniprot", "alias", "face")
    seen: dict[str, int] = {}
    for i, entry in enumerate(panel):
        if not isinstance(entry, dict):
            # RuntimeError, not TypeError, for the same reason as the parse check
            # above: every "this panel is unusable" failure in this module is one
            # family so callers can catch one exception type.
            raise RuntimeError(  # noqa: TRY004
                f"{panel_path} panel[{i}] is {type(entry).__name__}, not a mapping"
            )
        missing = [k for k in required if not str(entry.get(k, "")).strip()]
        if missing:
            raise RuntimeError(
                f"{panel_path} panel[{i}] ({entry.get('symbol', '?')}) is missing or has "
                f"an empty {', '.join(missing)}. Every entry needs all of {required}."
            )
        # .get(), not [] — this check must not depend on `face` staying in
        # `required` above. A mutation dropping it should surface as this clean
        # RuntimeError, not as a KeyError from the domain check itself.
        if entry.get("face") not in FACES:
            raise RuntimeError(
                f"{panel_path} panel[{i}] ({entry.get('symbol', '?')}) has face="
                f"{entry.get('face')!r}; expected one of {sorted(FACES)}."
            )
        # Duplicate symbols make resolve_panel_accession() silently return the
        # first match, so a second ABCB1 row would be unreachable and its
        # accession never used — an edit that looks applied but is not.
        if entry["symbol"] in seen:
            raise RuntimeError(
                f"{panel_path} has duplicate symbol {entry['symbol']!r} at panel"
                f"[{seen[entry['symbol']]}] and panel[{i}]; symbol must be unique "
                "because accessions are resolved by symbol."
            )
        seen[entry["symbol"]] = i

    # Seal check LAST: a malformed panel should report the specific malformation,
    # not a digest mismatch that says only "something changed".
    sealed = str(doc.get(SEAL_KEY) or "").strip()
    if sealed:
        actual = panel_digest(panel)
        if actual != sealed:
            raise RuntimeError(
                f"{panel_path} FAILS ITS SEAL. Recorded {sealed[:12]}…, computed "
                f"{actual[:12]}…. The panel was edited after a human ratified it, so "
                "the attestation no longer covers its contents. Either revert the edit "
                "or have a human re-verify and re-run `chipsim panel seal`. An agent "
                "must not re-seal (Global Constraint 4)."
            )

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

    # A ratified panel whose accessions match NOTHING in the snapshot is a broken
    # panel, not an empty result. Returning the empty frame makes every compound
    # label 'unknown', which is indistinguishable from a genuine absence of
    # evidence — the exact failure load_ratified_panel's docstring names.
    if joined.empty:
        raise RuntimeError(
            f"the ratified panel at {panel_path} matched ZERO protein edges "
            f"({len(panel)} panel accessions vs {len(edges)} edges). This is a broken "
            "panel or a mis-parsed edge table, not an empty result: downstream every "
            "compound would come back 'unknown', which reads as a genuine absence of "
            "evidence. Check the accessions and the organism filter."
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

    keys = compounds["canonical_inchikey"]
    if keys.isna().any() or (keys.astype(str).str.strip() == "").any():
        raise ValueError(
            "compounds carries null/blank `canonical_inchikey`. groupby would drop the "
            "null rows silently and keep the blank ones as a legitimate group, so the "
            "label set would be quietly missing compounds."
        )
    if compounds.empty:
        raise ValueError("compounds is empty — refusing to emit an empty label set")

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
    # A bare `assert` would be the ONE check that vanishes under `python -O` /
    # PYTHONOPTIMIZE=1 — and it is the check that keeps 'no' (a positive claim
    # requiring a citation) out of a pre-adjudication label set.
    escaped = sorted(set(labels.unique()) - PRE_ADJUDICATION_LABELS)
    if escaped:
        raise RuntimeError(f"pre-adjudication labels escaped their domain: {escaped}")
    return labels
