"""Relative-stereo (/s2) input is keyed STEREO-FREE and flagged — principal ruling
2026-09-15 (CTO #122 §0).

The defect this pins: the InChI stereo-type flag says `/s1` = absolute, `/s2` =
RELATIVE, `/s3` = racemic. RDKit reads a `/s2` string as if it were absolute `/m0`,
so the pipeline gave every one of the snapshot's 42 relative-stereo compounds an
ABSOLUTE canonical key. Classified by InChI LAYERS against PubChem, 13 of the 42 came
out as the MIRROR IMAGE — among them DrugBank's L-threonine row, keyed as D-threonine.
An arbitrary absolute assignment is a fabrication, so the ruling is: strip stereo
before keying, and carry `stereo_is_relative` so downstream joins and roster
selection can honour it. Enantiomers DrugBank never distinguished will merge; that
is what the source actually says.

Scope of the strip: TETRAHEDRAL (sp3) stereo only. The InChI `/s` flag qualifies the
sp3 layers (/t, /m); double-bond geometry (/b) is always absolute in InChI and is
kept.

Structure provenance (every structure cites a public source — CTO #120 §1):
  - THREONINE_RELATIVE has NO public record: it is a non-standard `InChI=1/` string
    with relative stereo, cited from the pinned DrugBank snapshot as its source of
    record (CTO #120 §7). It is named here by its generic chemical name only.
  - THREONINE_UNSPECIFIED: PubChem CID 205, "2-amino-3-hydroxybutanoic acid",
    retrieved 2026-09-15 (InChIKey AYFVYJQAPQTCCC-UHFFFAOYSA-N).
  - D-threonine for the defect pin: PubChem CID 69435, InChIKey
    AYFVYJQAPQTCCC-STHAYSLISA-N, retrieved 2026-09-15.
  - L_ASPARTIC_ACID: PubChem CID 5960, retrieved 2026-09-15.
  - ABSCISIC_ACID: PubChem CID 5280896, "(2Z,4E)-5-[(1S)-1-hydroxy-2,6,6-trimethyl-4-
    oxocyclohex-2-en-1-yl]-3-methylpenta-2,4-dienoic acid", retrieved 2026-09-16.
    ABSCISIC_ACID_RELATIVE is DERIVED from it here (the /m1/s1 layers replaced by /s2), so
    it is a constructed test input, not any record's string.
"""

from __future__ import annotations

import pandas as pd

from chipsim.harmonize.ids import (
    MERGE_STAGES,
    add_canonical_identity,
    canonicalize,
    merge_stage_report,
    relative_stereo_effect,
)

#: Source of record: the pinned DrugBank snapshot (no public record — non-standard,
#: relative stereo). Relative `/t2-,3+` with `/s2`: threo configuration, absolute
#: configuration NOT stated.
THREONINE_RELATIVE = "InChI=1/C4H9NO3/c1-2(6)3(5)4(7)8/h2-3,6H,5H2,1H3,(H,7,8)/t2-,3+/s2"

#: PubChem CID 205 (retrieved 2026-09-15) — threonine with no stereo specified.
THREONINE_UNSPECIFIED = "InChI=1S/C4H9NO3/c1-2(6)3(5)4(7)8/h2-3,6H,5H2,1H3,(H,7,8)"
THREONINE_STEREO_FREE_KEY = "AYFVYJQAPQTCCC-UHFFFAOYSA-N"  # CID 205's InChIKey

#: PubChem CID 69435 (D-threonine), retrieved 2026-09-15 — the key the defect produced.
D_THREONINE_KEY = "AYFVYJQAPQTCCC-STHAYSLISA-N"

#: PubChem CID 5960 (L-aspartic acid), retrieved 2026-09-15 — ABSOLUTE stereo (/s1).
L_ASPARTIC_ACID = "InChI=1S/C4H7NO4/c5-2(4(8)9)1-3(6)7/h2H,1,5H2,(H,6,7)(H,8,9)/t2-/m0/s1"
L_ASPARTIC_ACID_KEY = "CKLJMWTZIZZHCS-REOHCLBHSA-N"


#: PubChem CID 5280896 (retrieved 2026-09-16): two double bonds (/b) AND one stereocentre.
ABSCISIC_ACID = (
    "InChI=1S/C15H20O4/c1-10(7-13(17)18)5-6-15(19)11(2)8-12(16)9-14(15,3)4"
    "/h5-8,19H,9H2,1-4H3,(H,17,18)/b6-5+,10-7-/t15-/m1/s1"
)
ABSCISIC_ACID_KEY = "JLIDBLDQVAYHNE-YKALOCIXSA-N"  # CID 5280896's InChIKey
#: Derived: the same string with its absolute stereo layers replaced by relative (/s2).
ABSCISIC_ACID_RELATIVE = ABSCISIC_ACID.replace("InChI=1S/", "InChI=1/").replace(
    "/t15-/m1/s1", "/t15-/s2"
)
#: The stereo-free key of the WHOLE molecule — what an over-broad strip would produce.
ABSCISIC_ACID_ALL_STEREO_FREE_KEY = "JLIDBLDQVAYHNE-UHFFFAOYSA-N"


def test_relative_stereo_input_is_flagged_and_keyed_stereo_free():
    """The pipeline asserts nothing the source did not: a relative string gets the
    stereo-free key, which is exactly PubChem CID 205's key."""
    result = canonicalize(THREONINE_RELATIVE)
    assert result.stereo_is_relative is True
    assert result.inchikey == THREONINE_STEREO_FREE_KEY


def test_without_the_strip_the_relative_string_gets_d_threonines_key():
    """The defect, pinned so it cannot silently return: read as absolute, DrugBank's
    L-threonine string keys to PubChem's D-threonine (CID 69435). The flag is still
    reported in measurement mode — it describes the SOURCE, not the handling."""
    result = canonicalize(THREONINE_RELATIVE, strip_relative_stereo=False)
    assert result.inchikey == D_THREONINE_KEY
    assert result.stereo_is_relative is True


def test_absolute_stereo_input_is_not_flagged_and_keeps_its_stereo():
    result = canonicalize(L_ASPARTIC_ACID)
    assert result.stereo_is_relative is False
    assert result.inchikey == L_ASPARTIC_ACID_KEY


def test_the_strip_clears_tetrahedral_stereo_but_keeps_double_bond_geometry():
    """QG F-04. Every other strip test uses a structure with no double-bond stereo, so an
    over-broad strip (e.g. `Chem.RemoveStereochemistry`, which also erases E/Z) passed them
    all. InChI /b geometry is always absolute and is NOT qualified by /s2: it must survive."""
    result = canonicalize(ABSCISIC_ACID_RELATIVE)
    assert result.stereo_is_relative is True
    assert "/b6-5+,10-7-" in result.parsed
    assert "/t" not in result.parsed and "/m" not in result.parsed
    assert result.inchikey != ABSCISIC_ACID_ALL_STEREO_FREE_KEY
    assert result.inchikey != ABSCISIC_ACID_KEY
    assert result.inchikey.split("-")[0] == ABSCISIC_ACID_KEY.split("-")[0]


def test_stereo_free_input_is_not_flagged():
    assert canonicalize(THREONINE_UNSPECIFIED).stereo_is_relative is False


def test_relative_stereo_is_its_own_merge_stage_immediately_after_parse():
    """The re-key's effect must be attributable, not folded into existing counts."""
    assert "relative-stereo" in MERGE_STAGES
    assert MERGE_STAGES.index("relative-stereo") == MERGE_STAGES.index("parse") + 1


def test_relative_and_unspecified_threonine_merge_at_the_relative_stereo_stage():
    frame = pd.DataFrame(
        [("R", THREONINE_RELATIVE), ("U", THREONINE_UNSPECIFIED)],
        columns=["drugbank_id", "inchi"],
    ).assign(inchikey="x")
    report = merge_stage_report(add_canonical_identity(frame))
    assert report["stage"].tolist() == ["relative-stereo"]
    assert report["canonical_inchikey"].tolist() == [THREONINE_STEREO_FREE_KEY]


def test_add_canonical_identity_emits_the_stereo_is_relative_flag():
    frame = pd.DataFrame(
        [("R", THREONINE_RELATIVE), ("A", L_ASPARTIC_ACID), ("U", THREONINE_UNSPECIFIED)],
        columns=["drugbank_id", "inchi"],
    ).assign(inchikey="x")
    out = add_canonical_identity(frame)
    assert out["stereo_is_relative"].tolist() == [True, False, False]
    assert out["stereo_is_relative"].dtype == bool


def test_the_pipeline_path_emits_the_flag_on_kept_and_excluded_rows():
    """QG F-02. `add_canonical_identity_excluding` is what the pipeline actually calls, and no
    test asserted its flag: hardcoding `stereo_is_relative = False` there left the suite green,
    which would silently switch off T10/T13/T15 and the T18 rejection for every relative-stereo
    compound.

    The excluded row is an UNPARSEABLE string that nonetheless declares relative stereo (`/s2`):
    the flag is read from the source string's own layers, so it must survive exclusion.
    """
    from chipsim.harmonize.ids import add_canonical_identity_excluding

    frame = pd.DataFrame(
        [
            ("DB90701", THREONINE_RELATIVE),
            ("DB90702", L_ASPARTIC_ACID),
            ("DB90703", THREONINE_UNSPECIFIED),
            ("DB90704", "InChI=1S/NOT-A-REAL-STRUCTURE/t2-/s2"),
        ],
        columns=["drugbank_id", "inchi"],
    ).assign(inchikey="x")
    kept, excluded = add_canonical_identity_excluding(frame, preregistered={"DB90704"})
    assert kept["stereo_is_relative"].dtype == bool
    assert kept["stereo_is_relative"].tolist() == [True, False, False]
    assert excluded["drugbank_id"].tolist() == ["DB90704"]
    assert excluded["stereo_is_relative"].tolist() == [True]


def test_relative_stereo_effect_reports_which_relative_compounds_merge():
    """CTO #122 §0: report how many relative-stereo compounds merge with another
    compound, and which — identified by canonical InChIKey, never by accession."""
    frame = pd.DataFrame(
        [("R", THREONINE_RELATIVE), ("U", THREONINE_UNSPECIFIED), ("A", L_ASPARTIC_ACID)],
        columns=["drugbank_id", "inchi"],
    ).assign(inchikey="x")
    effect = relative_stereo_effect(frame)
    assert effect.relative == 1
    assert effect.merge_groups_before == 0
    assert effect.merge_groups_after == 1
    assert effect.merged_keys == (THREONINE_STEREO_FREE_KEY,)
    assert effect.new_merges == 1
