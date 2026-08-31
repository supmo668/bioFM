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

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem.MolStandardize import rdMolStandardize

#: RDKit is loud on the malformed structures real snapshots contain. Errors are
#: surfaced as exceptions by this module, so the console noise adds nothing.
RDLogger.DisableLog("rdApp.*")


class CanonicalizationError(ValueError):
    """A structure could not be canonicalized to an InChIKey."""


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
        raise CanonicalizationError(f"RDKit could not parse InChI: {inchi[:80]!r}")

    # 1. Salt strip — drops counter-ions, keeping the parent fragment.
    mol = rdMolStandardize.FragmentParent(mol)
    if mol is None or mol.GetNumAtoms() == 0:
        raise CanonicalizationError(f"salt stripping left no parent fragment: {inchi[:80]!r}")

    # 2. Neutralize.
    mol = _uncharger().uncharge(mol)

    # 3. Canonical tautomer.
    mol = _tautomer_enumerator().Canonicalize(mol)

    key = Chem.MolToInchiKey(mol)
    if not key:
        raise CanonicalizationError(f"no InChIKey produced for: {inchi[:80]!r}")
    return key


def add_canonical_identity(compounds: pd.DataFrame) -> pd.DataFrame:
    """Adds `canonical_inchikey`. Raises if any value is null."""
    if "inchi" not in compounds.columns:
        raise ValueError("compounds frame has no `inchi` column to canonicalize from")

    out = compounds.copy()

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


def canonicalization_disagreements(compounds: pd.DataFrame) -> pd.DataFrame:
    """Rows where the canonical key differs from the raw snapshot key.

    T5b's done-condition asks for this count to be REPORTED, not zero. A nonzero
    count is the expected, healthy case — it is the salts collapsing onto their
    free bases. A count of zero on a real snapshot means canonicalization is a
    no-op and the identity layer is not doing its job.
    """
    if "canonical_inchikey" not in compounds.columns:
        raise ValueError("call add_canonical_identity() first")
    return compounds[compounds["inchikey"] != compounds["canonical_inchikey"]]
