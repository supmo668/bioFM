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
    real snapshot would mean canonicalization is a no-op."""
    disagreements = canonicalization_disagreements(canonical)
    assert len(disagreements) == 2
    assert set(disagreements["drugbank_id"]) == {"DB90005", "DB90008"}


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
