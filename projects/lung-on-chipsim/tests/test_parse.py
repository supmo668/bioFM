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


def test_t5_empty_list_cell_becomes_empty_list(compounds):
    """An absent ATC code is [], not [''] — a one-element list of the empty string
    would count as 'has an ATC code' in every downstream length check."""
    assert all(isinstance(v, list) for v in compounds["atc_codes"])
    assert [] not in [[""]]
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
    assert len(load_protein_edges(SNAPSHOT_DIR)) > 0


def test_t6_category_set_equality_not_subset():
    """EQUALITY, not subset (defect 9). A subset check passes on a frame that lost
    three of the four categories to a bad filter."""
    edges = load_protein_edges(SNAPSHOT_DIR)
    assert set(edges["category"]) == set(EDGE_CATEGORIES)


def test_t6_filters_to_human():
    edges = load_protein_edges(SNAPSHOT_DIR)
    assert set(edges["organism"]) == {HUMAN_ORGANISM}


def test_t6_drops_the_non_human_edge():
    """The rat ABCB1 edge on DB90002 must not survive the species filter."""
    edges = load_protein_edges(SNAPSHOT_DIR)
    rat = edges[(edges["drugbank_id"] == "DB90002") & (edges["uniprot_id"] == "P08183")]
    assert rat.empty


def test_t6_golden_row_is_present():
    """The golden-row assertion: a named reference drug with a known ABCB1
    transporter edge. This is what catches a silent species-filter mismatch that
    empties the frame — an empty frame passes every column-shape assertion."""
    edges = load_protein_edges(SNAPSHOT_DIR)
    golden = edges[
        (edges["drugbank_id"] == "DB90004")
        & (edges["uniprot_id"] == "P08183")
        & (edges["category"] == "transporter")
    ]
    assert len(golden) == 1, "the ABCB1 transporter golden row is missing"


def test_t6_unexpected_category_raises(tmp_path):
    (tmp_path / "proteins.tsv").write_text(
        "drugbank_id\tuniprot_id\tcategory\torganism\nDB1\tP1\tnot-a-category\tHomo sapiens\n"
    )
    with pytest.raises(ValueError, match="unexpected edge category"):
        load_protein_edges(tmp_path)
