"""Snapshot parse + identity + persistence — build-plan T5, T5a, T5b, T6.

Runs against tests/fixtures/snapshot/, which mimics the dhimmel/drugbank SCHEMA
and carries no DrugBank content. The real snapshot is blocked on T2 (the pinned
commit) and T4a (the fetch), so the row-count floor is exercised by asserting that
it RAISES rather than by shipping 1000 fixture rows.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from chipsim.harmonize.ids import (
    CanonicalizationError,
    add_canonical_identity,
    canonical_inchikey,
    canonicalization_disagreements,
)
from chipsim.ingest.drugbank_snapshot import (
    EDGE_CATEGORIES,
    HUMAN_ORGANISM,
    MIN_COMPOUND_ROWS,
    PERSISTED_COMPOUND_COLUMNS,
    _split_list_cell,
    load_compounds,
    load_protein_edges,
    read_digest_sidecar,
    write_compounds,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = PROJECT_ROOT / "tests" / "fixtures" / "snapshot"


@pytest.fixture
def compounds() -> pd.DataFrame:
    return load_compounds(SNAPSHOT_DIR, min_rows=0)


@pytest.fixture
def canonical(compounds) -> pd.DataFrame:
    return add_canonical_identity(compounds)


# --------------------------------------------------------------------------- #
# T5 · compound table
# --------------------------------------------------------------------------- #


def test_t5_inchikey_is_never_null(compounds):
    assert compounds["inchikey"].notna().all()
    assert (compounds["inchikey"].str.strip() != "").all()


def test_t5_drops_rows_without_a_structure(compounds):
    """DB90006 is a biotech entry with no InChIKey — nothing downstream can join
    on it, so T5 drops it rather than carrying a null key."""
    assert "DB90006" not in set(compounds["drugbank_id"])


def test_t5_groups_is_a_list_not_a_pipe_joined_string(compounds):
    row = compounds[compounds["drugbank_id"] == "DB90001"].iloc[0]
    assert isinstance(row["groups"], list)
    assert row["groups"] == ["approved", "investigational"]
    assert isinstance(row["atc_codes"], list)


def test_t5_atc_codes_splits_multiple_values(compounds):
    row = compounds[compounds["drugbank_id"] == "DB90002"].iloc[0]
    assert row["atc_codes"] == ["B01AC06", "N02BA01"]


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("", []),
        ("   ", []),
        (None, []),
        ("A", ["A"]),
        ("A|B", ["A", "B"]),
        ("A||B", ["A", "B"]),
        (" A | B ", ["A", "B"]),
    ],
)
def test_t5_split_list_cell(raw, expected):
    """Direct unit coverage of the splitter.

    The previous test asserted `[] not in [[""]]` — a constant Python expression,
    true regardless of the implementation — and its frame-level check was vacuous
    because the only fixture row with an empty ATC cell (DB90006) is dropped for
    having no InChIKey before the splitting code ever runs. A naive
    `str(value).split("|")`, which returns `[""]` for an empty cell, passed.
    """
    assert _split_list_cell(raw) == expected


def test_t5_empty_list_cell_becomes_empty_list(compounds):
    """And the same branch reached through the real loader.

    DB90009 is a small molecule WITH an InChIKey and an EMPTY atc_codes cell, so it
    survives the InChIKey filter and actually exercises the empty branch.
    """
    row = compounds[compounds["drugbank_id"] == "DB90009"].iloc[0]
    assert row["atc_codes"] == []
    assert row["groups"] == ["approved"]
    assert all(isinstance(v, list) for v in compounds["atc_codes"])
    assert all("" not in v for v in compounds["atc_codes"])


def test_t5_row_count_floor_is_enforced():
    """The floor is what makes T5's done-condition non-vacuous (defect 9): a
    column-only assertion passes trivially on a near-empty frame."""
    with pytest.raises(ValueError, match="below the floor"):
        load_compounds(SNAPSHOT_DIR)  # default min_rows = MIN_COMPOUND_ROWS


def test_t5_row_count_floor_default_is_the_real_snapshot_floor():
    assert MIN_COMPOUND_ROWS == 1000


def test_t5_missing_snapshot_raises_a_pointing_error(tmp_path):
    with pytest.raises(FileNotFoundError, match="T4a"):
        load_compounds(tmp_path, min_rows=0)


# --------------------------------------------------------------------------- #
# T5b · canonical identity
# --------------------------------------------------------------------------- #


def test_t5b_salt_and_free_base_collapse_to_one_key(canonical):
    """The done-condition. Verapamil (DB90004) and verapamil HCl (DB90005) carry
    DIFFERENT raw InChIKeys and MUST collapse to one canonical key — joining on
    the raw key silently splits one compound into two."""
    pair = canonical[canonical["drugbank_id"].isin(["DB90004", "DB90005"])]
    assert pair["inchikey"].nunique() == 2
    assert pair["canonical_inchikey"].nunique() == 1


def test_t5b_sodium_salt_collapses_to_the_free_acid(canonical):
    """Diclofenac sodium strips to diclofenac."""
    row = canonical[canonical["drugbank_id"] == "DB90008"].iloc[0]
    assert row["canonical_inchikey"] != row["inchikey"]


def test_t5b_canonical_key_is_non_null_on_every_row(canonical):
    assert canonical["canonical_inchikey"].notna().all()
    assert (canonical["canonical_inchikey"].str.len() > 0).all()


def test_t5b_reports_a_disagreement_count(canonical):
    """A nonzero count is the HEALTHY case — it is the salts collapsing. Zero on a
    real snapshot would mean canonicalization is a no-op.

    This count stays 2 because the FIXTURE stores bare InChIKeys. The real snapshot
    stores them prefixed, and that difference hid a defect for the life of the
    project — see the prefix test below.
    """
    disagreements = canonicalization_disagreements(canonical)
    assert len(disagreements) == 2
    assert set(disagreements["drugbank_id"]) == {"DB90005", "DB90008"}


def test_t5b_disagreement_ignores_the_inchikey_prefix():
    """A row differing ONLY by the `InChIKey=` prefix is NOT a disagreement.

    The real DrugBank snapshot writes `InChIKey=ABC…`; RDKit returns `ABC…`. A
    naive `!=` therefore reported 6,802 of 6,802 real compounds as disagreeing,
    when the substantive count is 2,251 — a metric that was 100% by construction
    and so carried no information, while T5b's done-condition asked for it to be
    reported.

    It survived because the fixture uses bare keys, so the fixture-based test above
    reads a correct 2 and can never fail on this. Pinned here with a PREFIXED row,
    which is the shape the real data actually has.
    """
    import pandas as pd

    frame = pd.DataFrame(
        [
            # identical apart from the prefix -> NOT a disagreement
            {
                "drugbank_id": "DB1",
                "inchikey": "InChIKey=AAAAAAAAAAAAAA-BBBBBBBBBB-N",
                "canonical_inchikey": "AAAAAAAAAAAAAA-BBBBBBBBBB-N",
            },
            # genuinely different second block -> IS a disagreement
            {
                "drugbank_id": "DB2",
                "inchikey": "InChIKey=CCCCCCCCCCCCCC-DDDDDDDDDD-N",
                "canonical_inchikey": "CCCCCCCCCCCCCC-UHFFFAOYSA-N",
            },
        ]
    )
    out = canonicalization_disagreements(frame)
    assert list(out["drugbank_id"]) == ["DB2"], (
        "a prefix-only difference must not count as a disagreement, and a real "
        "stereo-block difference must"
    )


def test_t5b_unparseable_inchi_raises(compounds):
    bad = compounds.copy()
    bad.loc[bad.index[0], "inchi"] = "InChI=1S/NOT-A-REAL-STRUCTURE"
    with pytest.raises(CanonicalizationError):
        add_canonical_identity(bad)


def test_t5b_empty_inchi_raises():
    with pytest.raises(CanonicalizationError, match="empty or non-string"):
        canonical_inchikey("")


def test_t5b_is_deterministic():
    inchi = "InChI=1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)"
    assert canonical_inchikey(inchi) == canonical_inchikey(inchi)


#: GOLDEN canonical InChIKeys, recorded from rdkit 2026.3.5.
#:
#: pyproject pins rdkit precisely because "tautomer canonicalization and the bundled
#: InChI toolkit both change across releases, so an unpinned rdkit can silently
#: repartition the splits while every recorded sha256 and every test stays green."
#: Without a golden value that was a literally accurate description of this suite:
#: `test_t5b_is_deterministic` is satisfied by `return "X"`, and nothing else
#: asserted an actual key.
#:
#: If one of these changes, the rdkit pin has MOVED and any sealed allocation
#: derived from these keys must be re-derived. Do not simply update the literal.
GOLDEN_CANONICAL_KEYS = {
    # aspirin — plain case, no salt, no charge
    "InChI=1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N",
    # verapamil HYDROCHLORIDE — exercises the salt-strip path; must land on the
    # FREE BASE key, not its own
    "InChI=1S/C27H38N2O4.ClH/c1-20(2)27(19-28,22-10-12-24(31-5)26(18-22)33-7)"
    "14-8-15-29(3)16-13-21-9-11-23(30-4)25(17-21)32-6;/h9-12,17-18,20H,8,13-16H2,1-7H3;1H": "SGTNSNPWRIOYBX-UHFFFAOYSA-N",
    # diclofenac SODIUM — salt strip to the free acid
    "InChI=1S/C14H11Cl2NO2.Na/c15-10-5-3-6-11(16)14(10)17-12-7-2-1-4-9(12)8-13(18)19;"
    "/h1-7,17H,8H2,(H,18,19);": "DCOPUUMXTXDBNB-UHFFFAOYSA-N",
}


@pytest.mark.parametrize("inchi,expected", sorted(GOLDEN_CANONICAL_KEYS.items()))
def test_t5b_golden_canonical_keys(inchi, expected):
    """Pins the rdkit pin's EFFECT, not just the pin string in pyproject."""
    assert canonical_inchikey(inchi) == expected


def test_t5b_salt_strips_to_the_free_base_key():
    """Stated as an explicit relation, so the intent survives a key update."""
    free_base = (
        "InChI=1S/C27H38N2O4/c1-20(2)27(19-28,22-10-12-24(31-5)26(18-22)33-7)"
        "14-8-15-29(3)16-13-21-9-11-23(30-4)25(17-21)32-6/h9-12,17-18,20H,8,13-16H2,1-7H3"
    )
    hcl = (
        free_base.replace("C27H38N2O4/", "C27H38N2O4.ClH/")
        .replace("1-7H3", "1-7H3;1H")
        .replace("32-6/h", "32-6;/h")
    )
    assert canonical_inchikey(hcl) == canonical_inchikey(free_base)


# --------------------------------------------------------------------------- #
# T5b · stereo guard — principal ruling 2026-09-15 (CTO #106): compare {/t, /m, /s} ONLY
# --------------------------------------------------------------------------- #
#
# Real snapshot InChIs, NOT hand-written SMILES: the first stage-by-stage probe of
# rolipram used a stand-in structure and concluded the R/S pair survived every
# stage. It was not rolipram, and the conclusion was worthless (#97). Every
# structure below is copied verbatim from data/raw/drugbank/drugbank.tsv and is
# named by compound name only — no accession numbers in tracked test code.
#
# Ruling: reject any canonicalisation step that alters stereo. If the tautomer
# step changes or erases a /t, /m or /s layer of the pre-tautomer InChI, return the
# PRE-tautomer InChIKey. **/b (double-bond geometry) is NOT compared** — a /b change
# alone must not trigger the fallback (#106 supersedes #98's four-layer wording;
# 56186's per-layer table showed /b split true tautomers). Compare InChI stereo
# LAYERS, not InChIKey blocks — the tautomer step legitimately moves the H-layer,
# which lives in the first key block, so key-block comparison cannot isolate stereo.

#: (snapshot InChI, InChIKey of the pre-tautomer structure) — the key the guard
#: must return. Pinned literals (rdkit 2026.3.5), same rule as
#: GOLDEN_CANONICAL_KEYS: if one moves, the rdkit pin moved.
STEREO_PAIRS = {
    "threonine": (
        # L-Threonine — a NON-standard `InChI=1/` at source, `/s2`
        (
            "InChI=1/C4H9NO3/c1-2(6)3(5)4(7)8/h2-3,6H,5H2,1H3,(H,7,8)/t2-,3+/s2",
            # Stereo-free since the relative-stereo re-key (principal ruling 2026-09-15,
            # CTO #122 §0): this string is `/s2` (RELATIVE), so it is keyed without sp3
            # stereo — PubChem CID 205's key. It USED to pin AYFVYJQAPQTCCC-STHAYSLISA-N,
            # which is PubChem D-threonine (CID 69435): RDKit read /s2 as absolute /m0.
            # Test and label wording are HELD unchanged until the re-key lands (#122 §6).
            "AYFVYJQAPQTCCC-UHFFFAOYSA-N",
        ),
        # D-Threonine
        (
            "InChI=1S/C4H9NO3/c1-2(6)3(5)4(7)8/h2-3,6H,5H2,1H3,(H,7,8)/t2-,3-/m1/s1",
            "AYFVYJQAPQTCCC-PWNYCUMCSA-N",
        ),
    ),
    "isoleucine": (
        # L-Isoleucine
        (
            "InChI=1S/C6H13NO2/c1-3-4(2)5(7)6(8)9/h4-5H,3,7H2,1-2H3,(H,8,9)/t4-,5-/m0/s1",
            "AGPKZVBTJJNPAG-WHFBIAKZSA-N",
        ),
        # Allo-Isoleucine
        (
            "InChI=1S/C6H13NO2/c1-3-4(2)5(7)6(8)9/h4-5H,3,7H2,1-2H3,(H,8,9)/t4-,5+/m1/s1",
            "AGPKZVBTJJNPAG-UHNVWZDZSA-N",
        ),
    ),
    "aspartate": (
        # L-Aspartic Acid — `/m0`; the CTO's confirmed pipeline collapse (#97)
        (
            "InChI=1S/C4H7NO4/c5-2(4(8)9)1-3(6)7/h2H,1,5H2,(H,6,7)(H,8,9)/t2-/m0/s1",
            "CKLJMWTZIZZHCS-REOHCLBHSA-N",
        ),
        # D-Aspartic Acid — `/m1`
        (
            "InChI=1S/C4H7NO4/c5-2(4(8)9)1-3(6)7/h2H,1,5H2,(H,6,7)(H,8,9)/t2-/m1/s1",
            "CKLJMWTZIZZHCS-UWTATZPHSA-N",
        ),
    ),
    "phenylalanine": (
        # L-Phenylalanine — the alpha-carbon centre the tautomer step drops (#106)
        (
            "InChI=1S/C9H11NO2/c10-8(9(11)12)6-7-4-2-1-3-5-7/h1-5,8H,6,10H2,(H,11,12)/t8-/m0/s1",
            "COLNVLDHVKWLRT-QMMMGPOBSA-N",
        ),
        # D-Phenylalanine
        (
            "InChI=1S/C9H11NO2/c10-8(9(11)12)6-7-4-2-1-3-5-7/h1-5,8H,6,10H2,(H,11,12)/t8-/m1/s1",
            "COLNVLDHVKWLRT-MRVPVSSYSA-N",
        ),
    ),
}


@pytest.mark.parametrize("pair", sorted(STEREO_PAIRS))
def test_t5b_stereo_guard_keeps_enantiomers_and_diastereomers_distinct(pair):
    """L-/D-threonine, L-/allo-isoleucine, L-/D-aspartate and L-/D-phenylalanine
    are DIFFERENT compounds. Before the guard all three pairs collapsed to one key at the
    tautomer step (46 of the 48 tautomer-stage merge groups on the real snapshot
    had stereo before that step)."""
    (a, _), (b, _) = STEREO_PAIRS[pair]
    assert canonical_inchikey(a) != canonical_inchikey(b)


@pytest.mark.parametrize(
    "inchi,expected",
    sorted(v for pair in STEREO_PAIRS.values() for v in pair),
)
def test_t5b_stereo_guard_returns_the_pre_tautomer_key(inchi, expected):
    """When the guard fires it returns the PRE-tautomer InChIKey — the key of the
    salt-stripped, neutralised structure with its stereo intact — not some third
    value. Pinned so `!=` above cannot be satisfied by returning garbage."""
    assert canonical_inchikey(inchi) == expected


#: Nitisinone and its enol tautomer — byte-DIFFERENT source InChIs
#: (`/h4-6,12H` vs `/h4-6,21H`), no stereo layer on either. One of exactly two
#: stereo-free tautomer-stage merge groups on the real snapshot.
NITISINONE_KETO = (
    "InChI=1S/C14H10F3NO5/c15-14(16,17)7-4-5-8(9(6-7)18(22)23)13(21)12-10(19)2-1-3-11(12)20"
    "/h4-6,12H,1-3H2"
)
NITISINONE_ENOL = (
    "InChI=1S/C14H10F3NO5/c15-14(16,17)7-4-5-8(9(6-7)18(22)23)13(21)12-10(19)2-1-3-11(12)20"
    "/h4-6,21H,1-3H2"
)


def test_t5b_stereo_free_tautomer_pair_still_merges():
    """The guard must not disable tautomer canonicalisation: a pair that differs
    ONLY in tautomeric form, with no stereo to lose, still collapses to one key."""
    assert canonical_inchikey(NITISINONE_KETO) == canonical_inchikey(NITISINONE_ENOL)


#: 2-(2-hydroxyphenyl)-3H-benzimidazole-5-carboximidamide in three forms: the
#: protonated 1H tautomer, the protonated 3H tautomer, and the NEUTRAL species.
#: The 1H form carries `/b14-9-` — a double-bond geometry layer the tautomer step
#: removes, which is why this trio is the regression test for excluding /b.
#:
#: Sources (PubChem, retrieved 2026-09-15): the protonated forms are CID 1505,
#: `URJKRCBBKTXOHS-UHFFFAOYSA-O`; the neutral form is CID 1506,
#: `URJKRCBBKTXOHS-UHFFFAOYSA-N`, IUPAC name
#: `2-(2-hydroxyphenyl)-3H-benzimidazole-5-carboximidamide`.
#:
#: The neutral constant was named `CRA_1144` here, after the snapshot's title for it
#: (CTO #122 §1: DrugBank-coined titles are record content). PubChem's own Title for
#: CID 1506 is also "Cra_1144" — a depositor code echoed by the database, not a
#: chemical name — so the IUPAC name is used instead.
BENZIMIDAZOLE_1H_PROTONATED = (
    "InChI=1S/C14H12N4O/c15-13(16)8-5-6-10-11(7-8)18-14(17-10)9-3-1-2-4-12(9)19"
    "/h1-7,17-18H,(H3,15,16)/p+1/b14-9-"
)
BENZIMIDAZOLE_3H_PROTONATED = (
    "InChI=1S/C14H12N4O/c15-13(16)8-5-6-10-11(7-8)18-14(17-10)9-3-1-2-4-12(9)19"
    "/h1-7,19H,(H3,15,16)(H,17,18)/p+1"
)
BENZIMIDAZOLE_NEUTRAL = (
    "InChI=1S/C14H12N4O/c15-13(16)8-5-6-10-11(7-8)18-14(17-10)9-3-1-2-4-12(9)19"
    "/h1-7,19H,(H3,15,16)(H,17,18)"
)


def test_t5b_benzimidazole_tautomers_still_merge_because_b_is_not_compared():
    """The regression test for the ruling's scope (#106): the 1H form's only
    stereo-ish layer is `/b14-9-`, which the tautomer step erases. A guard that
    compared /b would fire here and split three forms of one compound; the ruled
    {t,m,s} guard does not, and the trio stays one canonical key."""
    keys = {
        canonical_inchikey(BENZIMIDAZOLE_1H_PROTONATED),
        canonical_inchikey(BENZIMIDAZOLE_3H_PROTONATED),
        canonical_inchikey(BENZIMIDAZOLE_NEUTRAL),
    }
    assert len(keys) == 1, keys


#: Two charged malate species from the snapshot: the MONOANION (`/p-1`) and a DIANION
#: tautomer (`/p-2`) whose hydrogen layer differs at source. Both carry `/t2-/m1/s1`,
#: which the tautomer step erases.
#:
#: Named by charge state and identified by InChIKey, not by the snapshot's titles for
#: them (CTO #122 §1 — DrugBank-coined titles are record content). Neither exact
#: structure has a PubChem record (checked by exact-InChI lookup, 2026-09-15), so there
#: is no public name to cite: the pre-tautomer keys below are the identification.
MALATE_MONOANION = "InChI=1S/C4H6O5/c5-2(4(8)9)1-3(6)7/h2,5H,1H2,(H,6,7)(H,8,9)/p-1/t2-/m1/s1"
MALATE_DIANION_TAUTOMER = (
    "InChI=1S/C4H6O5/c5-2(4(8)9)1-3(6)7/h1-2,5-7H,(H,8,9)/p-2/t2-/m1/s1"
)


def test_malate_pair_splits_known_accepted_loss():
    """DELIBERATE and ACCEPTED (principal ruling 2026-09-15, CTO #106): this pair
    SPLITS under the guard, and that is a recorded limit, not a bug to fix.

    The monoanion (`/p-1`) and the dianion tautomer (`/p-2`) are two charge states of
    one compound whose pre-tautomer skeletons already differ (first InChIKey blocks
    BJEPYKJPYRNKOW vs QFBHYOKSQPPXHZ — the H layer and the protonation differ at
    source). Both carry `/t2-/m1/s1`; the tautomer step erases it; the guard fires for
    each and returns two different pre-tautomer keys. The guard cannot keep them
    together without also re-merging true stereoisomers. A known loss with a test is a
    recorded limit; a known loss without one is a latent surprise.
    """
    assert canonical_inchikey(MALATE_MONOANION) != canonical_inchikey(MALATE_DIANION_TAUTOMER)
    assert canonical_inchikey(MALATE_MONOANION).startswith("BJEPYKJPYRNKOW-")
    assert canonical_inchikey(MALATE_DIANION_TAUTOMER).startswith("QFBHYOKSQPPXHZ-")


# --------------------------------------------------------------------------- #
# T5a · persistence
# --------------------------------------------------------------------------- #


def test_t5a_parquet_round_trips_identically(canonical, tmp_path):
    out = tmp_path / "drugbank_compounds.parquet"
    write_compounds(canonical, out)

    written = pd.read_parquet(out, engine="pyarrow")
    expected = (
        canonical.loc[:, list(PERSISTED_COMPOUND_COLUMNS)]
        .sort_values("canonical_inchikey", kind="mergesort")
        .reset_index(drop=True)
    )
    pd.testing.assert_frame_equal(written, expected)


def test_t5a_is_sorted_by_canonical_inchikey(canonical, tmp_path):
    out = tmp_path / "c.parquet"
    write_compounds(canonical, out)
    written = pd.read_parquet(out, engine="pyarrow")
    assert written["canonical_inchikey"].is_monotonic_increasing


def test_t5a_column_order_is_declared(canonical, tmp_path):
    out = tmp_path / "c.parquet"
    write_compounds(canonical, out)
    written = pd.read_parquet(out, engine="pyarrow")
    assert tuple(written.columns) == PERSISTED_COMPOUND_COLUMNS


def test_t5a_writes_a_git_trackable_digest_sidecar(canonical, tmp_path):
    import hashlib

    out = tmp_path / "drugbank_compounds.parquet"
    write_compounds(canonical, out)

    sidecar = out.with_suffix(".sha256")
    assert sidecar.is_file()
    assert read_digest_sidecar(out) == hashlib.sha256(out.read_bytes()).hexdigest()


def test_t5a_refuses_a_frame_without_canonical_identity(compounds, tmp_path):
    with pytest.raises(ValueError, match="T5b"):
        write_compounds(compounds, tmp_path / "c.parquet")


# --------------------------------------------------------------------------- #
# T6 · protein edges
# --------------------------------------------------------------------------- #


def test_t6_frame_is_non_empty():
    assert len(load_protein_edges(SNAPSHOT_DIR, min_rows=0)) > 0


def test_t6_category_set_equality_not_subset():
    """EQUALITY, not subset (defect 9). A subset check passes on a frame that lost
    three of the four categories to a bad filter."""
    edges = load_protein_edges(SNAPSHOT_DIR, min_rows=0)
    assert set(edges["category"]) == set(EDGE_CATEGORIES)


def test_t6_filters_to_human():
    edges = load_protein_edges(SNAPSHOT_DIR, min_rows=0)
    assert set(edges["organism"]) == {HUMAN_ORGANISM}


def test_t6_drops_the_non_human_edge():
    """The rat ABCB1 edge on DB90002 must not survive the species filter."""
    edges = load_protein_edges(SNAPSHOT_DIR, min_rows=0)
    rat = edges[(edges["drugbank_id"] == "DB90002") & (edges["uniprot_id"] == "P08183")]
    assert rat.empty


def test_t6_golden_row_is_present():
    """The golden-row assertion: a named reference drug with a known ABCB1
    transporter edge. This is what catches a silent species-filter mismatch that
    empties the frame — an empty frame passes every column-shape assertion."""
    edges = load_protein_edges(SNAPSHOT_DIR, min_rows=0)
    golden = edges[
        (edges["drugbank_id"] == "DB90004")
        & (edges["uniprot_id"] == "P08183")
        & (edges["category"] == "transporter")
    ]
    assert len(golden) == 1, "the ABCB1 transporter golden row is missing"


def test_t6_raises_when_a_category_is_lost_to_the_organism_filter(tmp_path):
    """Set-EQUALITY asserted inside the loader, not only in the tests.

    Keeping the equality check in the test suite means it runs only against a
    hand-built fixture and can never fail on real data: a snapshot that lost three
    of four categories to a bad filter would sail through `load_protein_edges`.
    Here the carrier/enzyme/target edges are non-human, so only `transporter`
    survives the filter — a table shaped exactly like a species-filter mismatch.
    """
    (tmp_path / "proteins.tsv").write_text(
        "drugbank_id\tuniprot_id\tcategory\torganism\n"
        "DB1\tP1\ttransporter\tHomo sapiens\n"
        "DB2\tP2\tenzyme\tRattus norvegicus\n"
        "DB3\tP3\tcarrier\tRattus norvegicus\n"
        "DB4\tP4\ttarget\tRattus norvegicus\n"
    )
    with pytest.raises(ValueError, match="expected exactly"):
        load_protein_edges(tmp_path, min_rows=0)

    # ...and it is the equality check doing the work, not the floor
    relaxed = load_protein_edges(tmp_path, min_rows=0, require_all_categories=False)
    assert set(relaxed["category"]) == {"transporter"}


def test_t6_row_count_floor_is_enforced():
    """Mirrors load_compounds' floor. Without it an organism-label drift yields
    ZERO edges silently, and every compound then labels 'unknown'."""
    with pytest.raises(ValueError, match="below the floor"):
        load_protein_edges(SNAPSHOT_DIR)


def test_t6_organism_drift_yields_an_error_not_an_empty_frame(tmp_path):
    """'Human' instead of 'Homo sapiens' must not return 0 rows quietly."""
    (tmp_path / "proteins.tsv").write_text(
        "drugbank_id\tuniprot_id\tcategory\torganism\n"
        "DB1\tP1\ttransporter\tHuman\n"
        "DB2\tP2\tenzyme\tHuman\n"
    )
    with pytest.raises(ValueError, match="organism filter|below the floor|expected exactly"):
        load_protein_edges(tmp_path, min_rows=1)


def test_t6_unexpected_category_raises(tmp_path):
    (tmp_path / "proteins.tsv").write_text(
        "drugbank_id\tuniprot_id\tcategory\torganism\nDB1\tP1\tnot-a-category\tHomo sapiens\n"
    )
    with pytest.raises(ValueError, match="unexpected edge category"):
        load_protein_edges(tmp_path, min_rows=0)
