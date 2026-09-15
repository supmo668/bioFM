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

import re
from collections import Counter
from dataclasses import dataclass, field
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


#: The InChI stereo layers the guard compares — principal ruling 2026-09-15 (CTO
#: #106): /t (tetrahedral parity), /m (enantiomer flag), /s (stereo type). **/b
#: (double-bond geometry) is deliberately NOT here**: measured on the real
#: snapshot, a /b-inclusive guard split true tautomers (benzimidazole 1H/3H, an
#: E/Z-only keto/enol trio) that share no stereocentre. #106 supersedes #98's
#: four-layer wording.
STEREO_LAYERS = ("t", "m", "s")

_LAYER_PREFIX = re.compile(r"^([a-z])")


def _stereo_layers(inchi: str) -> tuple[str, ...]:
    """The /t, /m, /s layers of an InChI, in order, prefix included (e.g. `t2-`,
    `m1`, `s1`). Compared as InChI LAYERS, never as InChIKey blocks: the tautomer
    step legitimately moves the H-layer, which lives in the first key block, so a
    block comparison could not isolate stereo."""
    layers = []
    for layer in inchi.split("/")[1:]:
        m = _LAYER_PREFIX.match(layer)
        if m and m.group(1) in STEREO_LAYERS:
            layers.append(layer)
    return tuple(layers)


#: The InChI stereo-type layer value for RELATIVE sp3 stereo. `/s1` is absolute and
#: `/s3` racemic; the snapshot carries 42 `/s2` strings and no `/s3`.
_RELATIVE_STEREO_LAYER = "s2"


def is_relative_stereo(inchi: str) -> bool:
    """True when the SOURCE InChI declares relative sp3 stereo (`/s2`).

    Read from the string's own layers, without RDKit, so it is defined for rows that
    fail to parse too. Principal ruling 2026-09-15 (CTO #122 §0)."""
    if not isinstance(inchi, str):
        return False
    return _RELATIVE_STEREO_LAYER in _stereo_layers(inchi.strip())


@dataclass(frozen=True)
class Canonicalization:
    """Every stage of one structure's canonicalization, so a merge can be
    attributed to the stage that produced it and the stereo guard's decision is
    inspectable rather than inferred."""

    inchikey: str  # the canonical key — the guard's choice
    parsed: str  # InChI after RDKit re-standardisation
    parent: str  # after salt strip
    neutral: str  # after uncharge — the PRE-tautomer structure
    tautomer: str  # after tautomer canonicalization
    guard_fired: bool  # True when the key is the pre-tautomer key
    #: The SOURCE carried relative stereo (/s2). Describes the input, not the handling:
    #: it is True even when `strip_relative_stereo=False` (measurement mode).
    stereo_is_relative: bool = False
    #: InChI as RDKit parsed it BEFORE the relative-stereo strip. Equals `parsed` for
    #: every absolute or stereo-free input; the two differ only when the strip acted.
    parsed_as_given: str = ""


@lru_cache(maxsize=8192)
def canonicalize(
    inchi: str, *, stereo_guard: bool = True, strip_relative_stereo: bool = True
) -> Canonicalization:
    """RDKit: parse -> relative-stereo strip -> salt strip -> neutralize -> tautomer
    canonicalize -> stereo guard -> InChIKey.

    **Relative-stereo strip (principal ruling 2026-09-15, CTO #122 §0).** InChI's
    stereo-type layer says `/s1` absolute, `/s2` RELATIVE, `/s3` racemic. RDKit reads a
    `/s2` string as if it were absolute `/m0`, so the pipeline used to assign an
    arbitrary absolute configuration: 13 of the snapshot's 42 relative-stereo
    compounds came out as the MIRROR IMAGE (DrugBank's L-threonine keyed as
    D-threonine). An arbitrary assignment is a fabrication, so for `/s2` input the
    TETRAHEDRAL chiral tags are cleared immediately after parsing and the compound is
    keyed stereo-free, with `stereo_is_relative=True` for downstream joins and roster
    selection to honour. Only sp3 stereo is stripped: the `/s` flag qualifies /t and
    /m, and InChI double-bond geometry (/b) is always absolute, so it is kept.
    `strip_relative_stereo=False` reproduces the old behaviour for measurement only,
    never for production identity.

    The order is load-bearing. Salt stripping first, so the counter-ion cannot
    influence neutralization; neutralization before tautomer canonicalization, so
    the enumerator sees a neutral species.

    **Stereo guard (principal ruling 2026-09-15, CTO #106).** RDKit's tautomer
    canonicalization erases stereocentres wholesale (`tautomerRemoveSp3Stereo`
    defaults on): on the real snapshot 46 of 48 tautomer-stage merge groups had
    stereo before that step — every L/D amino acid pair, bupivacaine/levobupivacaine,
    hyoscyamine/atropine. So: record the pre-tautomer InChI's /t, /m, /s layers;
    canonicalize; if ANY of the three changed or vanished, return the PRE-tautomer
    InChIKey. `/b` is not compared (see STEREO_LAYERS). `stereo_guard=False` is the
    unguarded pipeline, kept so the guard's effect can be measured, never for
    production identity.
    """
    if not isinstance(inchi, str) or not inchi.strip():
        raise CanonicalizationError(f"empty or non-string InChI: {inchi!r}")

    mol = Chem.MolFromInchi(inchi.strip())
    if mol is None:
        raise CanonicalizationError(f"RDKit could not parse InChI: {_excerpt(inchi)}")
    parsed_as_given = Chem.MolToInchi(mol)
    relative = is_relative_stereo(inchi)

    # 0. Relative-stereo strip (CTO #122 §0): assert nothing the source did not.
    if relative and strip_relative_stereo:
        for atom in mol.GetAtoms():
            atom.SetChiralTag(Chem.ChiralType.CHI_UNSPECIFIED)
    parsed = Chem.MolToInchi(mol)

    # 1. Salt strip — drops counter-ions, keeping the parent fragment.
    mol = rdMolStandardize.FragmentParent(mol)
    if mol is None or mol.GetNumAtoms() == 0:
        raise CanonicalizationError(f"salt stripping left no parent fragment: {_excerpt(inchi)}")
    parent = Chem.MolToInchi(mol)

    # 2. Neutralize.
    mol = _uncharger().uncharge(mol)
    neutral = Chem.MolToInchi(mol)
    neutral_key = Chem.MolToInchiKey(mol)

    # 3. Canonical tautomer.
    mol = _tautomer_enumerator().Canonicalize(mol)
    tautomer = Chem.MolToInchi(mol)
    key = Chem.MolToInchiKey(mol)

    # 4. Stereo guard.
    fired = False
    if stereo_guard and _stereo_layers(neutral) != _stereo_layers(tautomer):
        key, fired = neutral_key, True

    if not key:
        raise CanonicalizationError(f"no InChIKey produced for: {_excerpt(inchi)}")
    return Canonicalization(
        inchikey=key,
        parsed=parsed,
        parent=parent,
        neutral=neutral,
        tautomer=tautomer,
        guard_fired=fired,
        stereo_is_relative=relative,
        parsed_as_given=parsed_as_given,
    )


def canonical_inchikey(inchi: str) -> str:
    """The canonical InChIKey — `canonicalize(inchi).inchikey`, guard on."""
    return canonicalize(inchi).inchikey


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
        out["stereo_is_relative"] = pd.Series(dtype=bool)
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

    # CTO #122 §0: the flag T10/T13/T15 must honour and T18 must be able to exclude on.
    out["stereo_is_relative"] = out["inchi"].map(is_relative_stereo).astype(bool)
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
        out["stereo_is_relative"] = pd.Series(dtype=bool)
        return out, out.iloc[0:0].assign(exclusion_reason=pd.Series(dtype="object"))

    reasons: dict[int, str] = {}

    def _one(row: pd.Series) -> str | None:
        try:
            return canonical_inchikey(row["inchi"])
        except CanonicalizationError as exc:
            reasons[row.name] = str(exc)
            return None

    out["canonical_inchikey"] = out.apply(_one, axis=1)
    # From the source string's layers, so excluded (unparseable) rows carry it too.
    out["stereo_is_relative"] = out["inchi"].map(is_relative_stereo).astype(bool)

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


# --------------------------------------------------------------------------- #
# Merge-stage report and the guard's measured effect (CTO #106 §4, #108)
# --------------------------------------------------------------------------- #

#: The stage at which the members of a merge group first coincide. The first is
#: NOT ours: byte-identical SOURCE InChIs are an upstream DrugBank limitation no
#: pipeline change can recover (100 of 191 groups on the real snapshot, #97).
#: `relative-stereo` (CTO #122 §0) sits immediately after `parse`: members that first
#: coincide once relative sp3 stereo is stripped. It is its own stage so the re-key's
#: effect is attributable rather than folded into salt/uncharge/tautomer counts.
MERGE_STAGES = ("upstream-duplicate", "parse", "relative-stereo", "salt", "uncharge", "tautomer")

_STAGE_FIELD = {
    "parse": "parsed_as_given",
    "relative-stereo": "parsed",
    "salt": "parent",
    "uncharge": "neutral",
    "tautomer": "tautomer",
}


def _group_stage(inchis: list[str], stages: list[Canonicalization]) -> str:
    if len(set(inchis)) == 1:
        return "upstream-duplicate"
    for stage in MERGE_STAGES[1:]:
        if len({getattr(c, _STAGE_FIELD[stage]) for c in stages}) == 1:
            return stage
    return "tautomer"


def merge_stage_report(
    compounds: pd.DataFrame, *, stereo_guard: bool = True, strip_relative_stereo: bool = True
) -> pd.DataFrame:
    """One row per merge group (>1 compound on one canonical key): the key, its
    size, the STAGE at which the members first coincide, and the member IDs.

    Without the stage, "191 merge groups" reads as 191 pipeline collapses. With
    it, 100 are upstream duplicates and only the rest are the pipeline's doing —
    the framing the CTO retracted in #97 depended on exactly this distinction.
    """
    if "canonical_inchikey" not in compounds.columns:
        raise ValueError("call add_canonical_identity() first")
    opts = {"stereo_guard": stereo_guard, "strip_relative_stereo": strip_relative_stereo}
    keyed = compounds.assign(_key=[canonicalize(i, **opts).inchikey for i in compounds["inchi"]])
    rows = []
    for key, group in keyed.groupby("_key", sort=True):
        if len(group) < 2:
            continue
        inchis = list(group["inchi"])
        stages = [canonicalize(i, **opts) for i in inchis]
        rows.append(
            {
                "canonical_inchikey": key,
                "size": len(group),
                "stage": _group_stage(inchis, stages),
                "drugbank_ids": [str(i) for i in group["drugbank_id"]],
            }
        )
    return pd.DataFrame(rows, columns=["canonical_inchikey", "size", "stage", "drugbank_ids"])


@dataclass(frozen=True)
class SplitGroup:
    """A merge group that exists WITHOUT the guard and is split by it."""

    key_before: str
    stage_before: str
    #: (drugbank_id, name) — IN MEMORY ONLY. DrugBank record content (CTO #120/#122 §2):
    #: never serialize to a tracked output; the journal mapping carries it.
    members: tuple[tuple[str, str], ...]
    keys_after: tuple[str, ...]
    layers: tuple[str, ...]  # which of t/m/s the tautomer step altered, union over members
    #: Each member's canonical key after the guard, aligned with `members`. This, not
    #: the id/name pair, is how a tracked report identifies a member (CTO #122 §2).
    member_keys: tuple[str, ...] = ()


@dataclass(frozen=True)
class GuardEffect:
    compounds: int
    guard_fired: int
    merge_groups_before: int
    merge_groups_after: int
    before_breakdown: dict[str, int]
    after_breakdown: dict[str, int]
    split_groups: tuple[SplitGroup, ...]
    new_merges: tuple[tuple[str, ...], ...]  # after-groups joining ids from >1 before-group
    reclassified: tuple[tuple[str, str, str], ...] = field(
        default_factory=tuple
    )  # (key, before, after)


def _layers_altered(c: Canonicalization) -> set[str]:
    before = {layer[0] for layer in _stereo_layers(c.neutral)}
    after_layers = _stereo_layers(c.tautomer)
    before_full = _stereo_layers(c.neutral)
    altered = set()
    for prefix in STEREO_LAYERS:
        b = tuple(x for x in before_full if x[0] == prefix)
        a = tuple(x for x in after_layers if x[0] == prefix)
        if b != a:
            altered.add(prefix)
    return altered or before


def guard_effect(compounds: pd.DataFrame) -> GuardEffect:
    """Measure the guard on a frame: merge groups with and without it, which
    groups it splits (by name — the record of reference), which it newly merges
    (expected: none), and how many compounds it fires on."""
    if "inchi" not in compounds.columns:
        raise ValueError("compounds frame has no `inchi` column")
    ids = [str(i) for i in compounds["drugbank_id"]]
    names = [str(n) for n in compounds["name"]] if "name" in compounds.columns else ids
    off = [canonicalize(i, stereo_guard=False) for i in compounds["inchi"]]
    on = [canonicalize(i, stereo_guard=True) for i in compounds["inchi"]]

    frame = compounds.assign(canonical_inchikey=[c.inchikey for c in on])
    before = merge_stage_report(frame, stereo_guard=False)
    after = merge_stage_report(frame, stereo_guard=True)

    by_id = {i: (o, n, nm) for i, o, n, nm in zip(ids, off, on, names, strict=True)}
    after_key_of = {i: n.inchikey for i, n in zip(ids, on, strict=True)}
    before_key_of = {i: o.inchikey for i, o in zip(ids, off, strict=True)}

    splits = []
    for row in before.itertuples(index=False):
        keys_after = {after_key_of[i] for i in row.drugbank_ids}
        if len(keys_after) > 1:
            altered: set[str] = set()
            for i in row.drugbank_ids:
                if by_id[i][1].guard_fired:
                    altered |= _layers_altered(by_id[i][1])
            splits.append(
                SplitGroup(
                    key_before=row.canonical_inchikey,
                    stage_before=row.stage,
                    members=tuple((i, by_id[i][2]) for i in row.drugbank_ids),
                    keys_after=tuple(sorted(keys_after)),
                    layers=tuple(sorted(altered)),
                    member_keys=tuple(after_key_of[i] for i in row.drugbank_ids),
                )
            )
    new_merges = []
    for row in after.itertuples(index=False):
        if len({before_key_of[i] for i in row.drugbank_ids}) > 1:
            new_merges.append(tuple(row.drugbank_ids))
    # Reclassification is by MEMBERSHIP, not by key: the members a split leaves
    # together get a new (pre-tautomer) key, so "same key, different stage" would
    # never see the residual pair that turned from tautomer-stage into a pure
    # upstream duplicate — which is exactly how the source-identical count moves
    # with zero new merges.
    before_group_of = {
        i: (row.canonical_inchikey, row.stage)
        for row in before.itertuples(index=False)
        for i in row.drugbank_ids
    }
    reclassified = []
    for row in after.itertuples(index=False):
        origins = {before_group_of[i] for i in row.drugbank_ids if i in before_group_of}
        if len(origins) == 1:
            ((_, stage_before),) = origins
            if stage_before != row.stage:
                reclassified.append((row.canonical_inchikey, stage_before, row.stage))
    reclassified = tuple(reclassified)
    return GuardEffect(
        compounds=len(ids),
        guard_fired=sum(c.guard_fired for c in on),
        merge_groups_before=len(before),
        merge_groups_after=len(after),
        before_breakdown=dict(Counter(before["stage"])),
        after_breakdown=dict(Counter(after["stage"])),
        split_groups=tuple(splits),
        new_merges=tuple(new_merges),
        reclassified=reclassified,
    )


# --------------------------------------------------------------------------- #
# Relative-stereo re-key: measured effect (CTO #122 §0)
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class RelativeStereoEffect:
    """What keying /s2 input stereo-free does to identity.

    Groups are identified by canonical InChIKey. `*_members` carry snapshot row IDs
    for the UNTRACKED journal only; a tracked report must never serialize them
    (DrugBank record content, CTO #120/#122 §2)."""

    compounds: int
    relative: int  # compounds whose source InChI declares /s2
    merge_groups_before: int  # strip OFF (the old absolute assignment)
    merge_groups_after: int  # strip ON (the ruling)
    merged_keys: tuple[str, ...]  # after-keys of groups the strip newly creates
    split_keys: tuple[str, ...]  # before-keys of groups the strip separates
    merged_members: tuple[tuple[str, ...], ...] = field(default_factory=tuple)
    split_members: tuple[tuple[str, ...], ...] = field(default_factory=tuple)

    @property
    def new_merges(self) -> int:
        return len(self.merged_keys)


def relative_stereo_effect(compounds: pd.DataFrame) -> RelativeStereoEffect:
    """Merge groups with the relative-stereo strip OFF vs ON (guard ON both times).

    Stripping removes information, so it mostly MERGES. It can also SPLIT: a relative
    compound that used to share a key with an absolute compound — by the arbitrary
    configuration RDKit assigned — no longer does. Both directions are reported.
    """
    if "inchi" not in compounds.columns:
        raise ValueError("compounds frame has no `inchi` column")
    ids = [str(i) for i in compounds["drugbank_id"]]
    inchis = list(compounds["inchi"])
    off = {i: canonicalize(s, strip_relative_stereo=False).inchikey for i, s in zip(ids, inchis, strict=True)}
    on = {i: canonicalize(s, strip_relative_stereo=True).inchikey for i, s in zip(ids, inchis, strict=True)}

    def _groups(key_of: dict[str, str]) -> dict[str, tuple[str, ...]]:
        by_key: dict[str, list[str]] = {}
        for i, k in key_of.items():
            by_key.setdefault(k, []).append(i)
        return {k: tuple(v) for k, v in by_key.items() if len(v) > 1}

    before, after = _groups(off), _groups(on)
    merged = sorted((k, m) for k, m in after.items() if len({off[i] for i in m}) > 1)
    split = sorted((k, m) for k, m in before.items() if len({on[i] for i in m}) > 1)
    return RelativeStereoEffect(
        compounds=len(ids),
        relative=sum(is_relative_stereo(s) for s in inchis),
        merge_groups_before=len(before),
        merge_groups_after=len(after),
        merged_keys=tuple(k for k, _ in merged),
        split_keys=tuple(k for k, _ in split),
        merged_members=tuple(m for _, m in merged),
        split_members=tuple(m for _, m in split),
    )


def relative_stereo_keys(compounds: pd.DataFrame) -> frozenset[str]:
    """Canonical keys carrying at least one relative-stereo (/s2) member (CTO #122 §0).

    A key is flagged when ANY member is: after the re-key, a stereo-free key may pool a
    relative compound with absolute or unspecified ones, and the pooled identity is only
    as specific as its least specific member.

    Raises when the frame lacks `stereo_is_relative`. A frame built before the re-key
    must not read as "no relative-stereo compounds" — that is exactly how a dropped
    flag would pass every downstream check.
    """
    missing = [c for c in ("canonical_inchikey", "stereo_is_relative") if c not in compounds.columns]
    if missing:
        raise ValueError(
            f"compounds frame lacks {missing}: run add_canonical_identity() (T5b) after the "
            "relative-stereo re-key. A frame without `stereo_is_relative` cannot be read as "
            "'nothing flagged'."
        )
    flagged = compounds.loc[compounds["stereo_is_relative"].astype(bool), "canonical_inchikey"]
    return frozenset(str(k) for k in flagged)
