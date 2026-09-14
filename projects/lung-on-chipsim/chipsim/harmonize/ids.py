"""Compound identity canonicalization — build-plan T5b.

A&D §1.2 requires a "canonical InChIKey from RDKit after salt stripping,
neutralization, tautomer canonicalization. **Never join on name or raw SMILES.**"

r1 declared RDKit in the stack and used it nowhere, so the plan's own Goal —
"through the compound-identity layer" — was unmet while all 17 done-conditions
passed (defect 31). This module is that layer.

Why it matters concretely: a salt and its free base are the SAME compound for
every purpose downstream, but carry DIFFERENT raw InChIKeys. Verapamil and
verapamil hydrochloride are `SGTNSNPWRIOYBX-...` and `DOQPXTMNIUCOSY-...`
respectively. Joining on the raw key silently splits one compound into two, which
halves an apparent label count without erroring.

**T10, T13 and T15 index on `canonical_inchikey`, not the raw snapshot key.**
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem.MolStandardize import rdMolStandardize

#: RDKit is loud on the malformed structures real snapshots contain. Errors are
#: surfaced as exceptions by this module, so the console noise adds nothing.
RDLogger.DisableLog("rdApp.*")


class CanonicalizationError(ValueError):
    """A structure could not be canonicalized to an InChIKey."""


#: The categorical exclusion code. **NEVER the string "unknown"** — CTO ruling
#: 2026-09-14. A parse failure is a fact about our toolchain; `unknown` is a fact
#: about the evidence, and the three-way P-gp label exists to keep those apart.
EXCLUSION_UNPARSEABLE = "unparseable_inchi"

#: How much of an InChI to show in an error message.
_EXCERPT = 80


def _excerpt(inchi: str) -> str:
    """An InChI fragment for an error message, MARKED when it is truncated.

    Truncation is fine; **unmarked** truncation is not. The first real blocker
    printed an 80-character fragment ending mid-token — it read as corrupt source
    data, and cost an hour chasing a transmission problem that did not exist. The
    strings were intact in the snapshot. An error that misrepresents its own cause
    costs the next reader the same hour.
    """
    text = str(inchi)
    if len(text) <= _EXCERPT:
        return repr(text)
    return f"{text[:_EXCERPT]!r} (truncated at {_EXCERPT} of {len(text)} chars)"


@lru_cache(maxsize=1)
def _uncharger() -> rdMolStandardize.Uncharger:
    return rdMolStandardize.Uncharger()


@lru_cache(maxsize=1)
def _tautomer_enumerator() -> rdMolStandardize.TautomerEnumerator:
    return rdMolStandardize.TautomerEnumerator()


@lru_cache(maxsize=4096)
def canonical_inchikey(inchi: str) -> str:
    """RDKit: salt strip -> neutralize -> tautomer canonicalize -> InChIKey.

    The order is load-bearing. Salt stripping first, so the counter-ion cannot
    influence neutralization; neutralization before tautomer canonicalization, so
    the enumerator sees a neutral species.
    """
    if not isinstance(inchi, str) or not inchi.strip():
        raise CanonicalizationError(f"empty or non-string InChI: {inchi!r}")

    mol = Chem.MolFromInchi(inchi.strip())
    if mol is None:
        raise CanonicalizationError(f"RDKit could not parse InChI: {_excerpt(inchi)}")

    # 1. Salt strip — drops counter-ions, keeping the parent fragment.
    mol = rdMolStandardize.FragmentParent(mol)
    if mol is None or mol.GetNumAtoms() == 0:
        raise CanonicalizationError(f"salt stripping left no parent fragment: {_excerpt(inchi)}")

    # 2. Neutralize.
    mol = _uncharger().uncharge(mol)

    # 3. Canonical tautomer.
    mol = _tautomer_enumerator().Canonicalize(mol)

    key = Chem.MolToInchiKey(mol)
    if not key:
        raise CanonicalizationError(f"no InChIKey produced for: {_excerpt(inchi)}")
    return key


def add_canonical_identity(compounds: pd.DataFrame) -> pd.DataFrame:
    """Adds `canonical_inchikey`. Raises if any value is null."""
    if "inchi" not in compounds.columns:
        raise ValueError("compounds frame has no `inchi` column to canonicalize from")

    out = compounds.copy()

    if out.empty:
        # pandas invokes the callable once on a synthetic all-NaN row for dtype
        # inference, which would raise "1 compound(s) failed canonicalization: nan"
        # for a frame containing zero compounds and point a debugger at a
        # structure that does not exist.
        out["canonical_inchikey"] = pd.Series(dtype="object")
        return out

    failures: list[tuple[str, str]] = []

    def _one(row: pd.Series) -> str | None:
        try:
            return canonical_inchikey(row["inchi"])
        except CanonicalizationError as exc:
            failures.append((str(row.get("drugbank_id", "?")), str(exc)))
            return None

    out["canonical_inchikey"] = out.apply(_one, axis=1)

    if failures:
        shown = "; ".join(f"{i}: {m}" for i, m in failures[:5])
        raise CanonicalizationError(
            f"{len(failures)} compound(s) failed canonicalization: {shown}"
            + (" ..." if len(failures) > 5 else "")
        )

    if out["canonical_inchikey"].isna().any():
        raise CanonicalizationError("canonical_inchikey is null on at least one row")

    return out


def load_preregistered_exclusions(path) -> set[str]:
    """The closed roster of compounds the pinned RDKit cannot canonicalize.

    Raises rather than returning an empty set when the file is missing: an absent
    exclusion roster is not the same as an empty one, and treating it as empty
    would make every real failure look like an unlisted defect.
    """
    import yaml

    doc = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or "compounds" not in doc:
        raise ValueError(
            f"{path} is not a valid exclusion roster — it must be a mapping with a "
            "`compounds` key. An unreadable roster must not be read as 'nothing is "
            "excluded'."
        )
    listed = doc["compounds"] or []
    if not isinstance(listed, list):
        raise TypeError(f"{path}: `compounds` must be a list, got {type(listed).__name__}")
    return {str(c) for c in listed}


def add_canonical_identity_excluding(
    compounds: pd.DataFrame,
    *,
    preregistered: set[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Canonicalize, dropping ONLY the pre-registered unparseable compounds.

    Returns `(kept, excluded)` — **a tuple, deliberately.** A caller cannot obtain
    the kept rows without also receiving the dropped ones, so the exclusion is
    visible in the type rather than in a docstring somebody may not read. That is
    this design's standing rule applied to its own API: an absent result must be
    visible where the result would have been.

    `add_canonical_identity` keeps raising and remains the default. This is the
    opt-in path, and the pipeline opts in explicitly.

    **Two ways this raises, and both are the point.** The roster is CLOSED:

    - a compound fails that is **not listed** → raise. A ninth failure is new
      information about the snapshot and needs adjudication, not absorption into a
      list that grows whenever something breaks.
    - a **listed** compound now parses → raise. The snapshot or the toolchain
      moved, so the pre-registration is stale and must be re-derived rather than
      quietly over-excluding.

    An exclusion list that can silently grow or rot is not a pre-registration; it
    is a place to hide data loss.
    """
    if "inchi" not in compounds.columns:
        raise ValueError("compounds frame has no `inchi` column to canonicalize from")

    out = compounds.copy()
    if out.empty:
        out["canonical_inchikey"] = pd.Series(dtype="object")
        return out, out.iloc[0:0].assign(exclusion_reason=pd.Series(dtype="object"))

    reasons: dict[int, str] = {}

    def _one(row: pd.Series) -> str | None:
        try:
            return canonical_inchikey(row["inchi"])
        except CanonicalizationError as exc:
            reasons[row.name] = str(exc)
            return None

    out["canonical_inchikey"] = out.apply(_one, axis=1)

    failed_mask = out["canonical_inchikey"].isna()
    failed_ids = {str(i) for i in out.loc[failed_mask, "drugbank_id"]}

    unlisted = sorted(failed_ids - preregistered)
    if unlisted:
        raise CanonicalizationError(
            f"{len(unlisted)} compound(s) failed canonicalization but are NOT in the "
            f"pre-registered exclusion roster: {', '.join(unlisted)}. "
            "This is new information about the snapshot — adjudicate it rather than "
            "adding it to the roster reflexively."
        )

    present_ids = {str(i) for i in out["drugbank_id"]}
    stale = sorted((preregistered & present_ids) - failed_ids)
    if stale:
        raise CanonicalizationError(
            f"{len(stale)} pre-registered exclusion(s) now parse successfully: "
            f"{', '.join(stale)}. The snapshot or the RDKit pin has moved, so the "
            "roster is stale and must be re-derived — continuing would over-exclude "
            "compounds the toolchain can now handle."
        )

    excluded = out.loc[failed_mask].copy()
    # `exclusion_reason` is a CATEGORICAL CODE and is never the string "unknown"
    # (CTO ruling, 2026-09-14). A parse failure is a fact about our toolchain;
    # `unknown` is a fact about the evidence. The three-way P-gp label exists to
    # keep those apart, so folding a parse failure into `unknown` would corrupt
    # the one distinction the label carries. The free-text message goes in its own
    # column rather than overloading the code.
    excluded["exclusion_reason"] = EXCLUSION_UNPARSEABLE
    excluded["exclusion_detail"] = [reasons.get(i, "") for i in excluded.index]
    kept = out.loc[~failed_mask].copy()
    return kept, excluded


def canonicalization_disagreements(compounds: pd.DataFrame) -> pd.DataFrame:
    """Rows where the canonical key differs from the raw snapshot key.

    T5b's done-condition asks for this count to be REPORTED, not zero. A nonzero
    count is the expected, healthy case — it is the salts collapsing onto their
    free bases. A count of zero on a real snapshot means canonicalization is a
    no-op and the identity layer is not doing its job.
    """
    if "canonical_inchikey" not in compounds.columns:
        raise ValueError("call add_canonical_identity() first")

    # *** STRIP THE `InChIKey=` PREFIX BEFORE COMPARING. ***
    #
    # The real DrugBank snapshot stores the raw key PREFIXED
    # (`InChIKey=BLCLNMBMMGCOAS-URPVMXJPSA-N`) while RDKit returns it bare, so a
    # naive `!=` called EVERY row a disagreement: 6,802 of 6,802 on the real
    # snapshot, against a true substantive count of 2,251 (33.1%). T5b's
    # done-condition asks for this count to be REPORTED, and it was reporting a
    # number that carried no information at all — 100% by construction.
    #
    # Why it survived: the FIXTURES store bare keys, so the fixture count is a
    # correct 2 and the test could not see it. That is the third instance of this
    # exact pattern today — after the unparseable InChIs and the `Human` vs
    # `Homo sapiens` organism label — where a done-condition was evaluated against
    # a fixture that does not share the real snapshot's vocabulary.
    #
    # `removeprefix` is a no-op on an already-bare key, so this does not move the
    # fixture count; it only stops the real count being meaningless.
    raw = compounds["inchikey"].astype(str).str.removeprefix("InChIKey=")
    return compounds[raw != compounds["canonical_inchikey"].astype(str)]
