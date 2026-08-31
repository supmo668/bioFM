"""Label-safety tests — build-plan T9, T10, T12.

r1's two tests were both satisfied by `return pd.Series("unknown", index=...)`,
which is precisely how defect 4's silent degradation went unnoticed (defect 20).
The positive case below is the test a constant-'unknown' implementation fails,
and `test_pgp_label_is_not_satisfied_by_a_constant_implementation` states that
adversarial property directly.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from chipsim.harmonize.ids import add_canonical_identity
from chipsim.harmonize.pgp_label import (
    PRE_ADJUDICATION_LABELS,
    barrier_panel_edges,
    pgp_substrate_label,
    resolve_panel_accession,
)
from chipsim.ingest.drugbank_snapshot import load_compounds, load_protein_edges

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = PROJECT_ROOT / "tests" / "fixtures" / "snapshot"


@pytest.fixture
def compounds() -> pd.DataFrame:
    return add_canonical_identity(load_compounds(SNAPSHOT_DIR, min_rows=0))


@pytest.fixture
def edges() -> pd.DataFrame:
    return load_protein_edges(SNAPSHOT_DIR)


@pytest.fixture
def panel_edges(edges, panel_ratified_path) -> pd.DataFrame:
    return barrier_panel_edges(edges, panel_ratified_path)


# --------------------------------------------------------------------------- #
# T9 · the join refuses an unratified panel
# --------------------------------------------------------------------------- #


def test_t9_returns_non_empty_against_the_ratified_fixture(panel_edges):
    assert not panel_edges.empty
    assert list(panel_edges.columns) == [
        "drugbank_id",
        "uniprot_id",
        "symbol",
        "category",
        "face",
    ]


def test_t9_raises_on_ratified_false(edges, panel_unratified_path):
    with pytest.raises(RuntimeError, match="not ratified"):
        barrier_panel_edges(edges, panel_unratified_path)


def test_t9_raises_when_the_ratified_key_is_absent(edges, fixture_dir):
    """Absence is not consent (defect 1)."""
    with pytest.raises(RuntimeError, match="no `ratified` key"):
        barrier_panel_edges(edges, fixture_dir / "barrier_panel_missing_ratified.yaml")


def test_t9_raises_on_ratified_true_with_empty_ratified_by(edges, fixture_dir):
    with pytest.raises(RuntimeError, match="ratified_by` is empty"):
        barrier_panel_edges(edges, fixture_dir / "barrier_panel_ratified_no_ratifier.yaml")


def test_t9_join_drops_off_panel_accessions(panel_edges):
    """The join is an INNER join onto the panel — a target edge to a protein that
    is not in the panel must not appear."""
    assert "P29274" not in set(panel_edges["uniprot_id"])


# --------------------------------------------------------------------------- #
# T10/T12 · label safety
# --------------------------------------------------------------------------- #


def test_pgp_label_never_infers_negative(compounds, panel_edges, panel_ratified_path):
    """A compound with zero protein edges is 'unknown', not 'no'."""
    labels = pgp_substrate_label(compounds, panel_edges, panel_ratified_path)

    # DB90006 has no structure and is dropped by T5; DB90008 (diclofenac) has no
    # edge at all in the fixture, so it is the zero-edge case.
    key = compounds.loc[compounds["drugbank_id"] == "DB90008", "canonical_inchikey"].iloc[0]
    assert labels[key] == "unknown"
    assert "no" not in set(labels)


def test_pgp_label_domain(compounds, panel_edges, panel_ratified_path):
    """set(labels) <= {'yes', 'unknown'} before adjudication."""
    labels = pgp_substrate_label(compounds, panel_edges, panel_ratified_path)
    assert set(labels) <= PRE_ADJUDICATION_LABELS


def test_pgp_label_positive_case(compounds, panel_edges, panel_ratified_path):
    """A compound with an (ABCB1, transporter) edge is labelled 'yes'.
    This is the test a constant-'unknown' implementation fails."""
    labels = pgp_substrate_label(compounds, panel_edges, panel_ratified_path)
    key = compounds.loc[compounds["drugbank_id"] == "DB90004", "canonical_inchikey"].iloc[0]
    assert labels[key] == "yes"


def test_pgp_label_is_not_satisfied_by_a_constant_implementation(
    compounds, panel_edges, panel_ratified_path
):
    """The adversarial property, stated directly (defect 20): the label set must
    contain BOTH values on the fixture. A frame that comes back all-'unknown' — the
    exact shape of defect 4's silent degradation — fails here."""
    labels = pgp_substrate_label(compounds, panel_edges, panel_ratified_path)
    assert set(labels) == {"yes", "unknown"}, (
        f"expected both labels present; got {sorted(set(labels))}. An all-'unknown' "
        "result is what a hard-coded/degraded ABCB1 lookup produces."
    )


def test_pgp_label_ignores_non_transporter_edges(compounds, panel_edges, panel_ratified_path):
    """An ABCB1 edge of category 'enzyme' yields 'unknown'."""
    labels = pgp_substrate_label(compounds, panel_edges, panel_ratified_path)

    # DB90007 (paracetamol) has an ABCB1 edge, but categorised 'enzyme'.
    assert "P08183" in set(panel_edges.loc[panel_edges["drugbank_id"] == "DB90007", "uniprot_id"])
    key = compounds.loc[compounds["drugbank_id"] == "DB90007", "canonical_inchikey"].iloc[0]
    assert labels[key] == "unknown"


def test_pgp_label_requires_abcb1_in_panel(compounds, panel_edges, fixture_dir):
    """A ratified panel with ABCB1 removed raises RuntimeError."""
    with pytest.raises(RuntimeError, match="no ABCB1 entry"):
        pgp_substrate_label(compounds, panel_edges, fixture_dir / "barrier_panel_no_abcb1.yaml")


def test_pgp_label_resolves_accession_from_the_panel_not_a_constant(fixture_dir, tmp_path):
    """AM-2: composition is configuration, not code. Re-accessioning ABCB1 in the
    panel must change what the label resolves against — a hard-coded P08183 would
    ignore the edit and keep working, which is the failure defect 4 describes."""
    import yaml

    doc = yaml.safe_load((fixture_dir / "barrier_panel_ratified.yaml").read_text())
    for entry in doc["panel"]:
        if entry["symbol"] == "ABCB1":
            entry["uniprot"] = "P99999"
    path = tmp_path / "repanel.yaml"
    path.write_text(yaml.safe_dump(doc))

    assert resolve_panel_accession(path, "ABCB1") == "P99999"


def test_pgp_label_requires_canonical_identity(compounds, panel_edges, panel_ratified_path):
    """Labelling on the raw snapshot key would split salts from free bases."""
    raw = compounds.drop(columns=["canonical_inchikey"])
    with pytest.raises(ValueError, match="canonical_inchikey"):
        pgp_substrate_label(raw, panel_edges, panel_ratified_path)


def test_pgp_label_collapses_a_salt_onto_its_free_base(compounds, panel_edges, panel_ratified_path):
    """Verapamil and verapamil HCl are one compound. They carry different raw
    InChIKeys and must produce ONE labelled row, not two."""
    labels = pgp_substrate_label(compounds, panel_edges, panel_ratified_path)

    pair = compounds[compounds["drugbank_id"].isin(["DB90004", "DB90005"])]
    assert pair["inchikey"].nunique() == 2, "fixture must carry two distinct raw keys"
    assert pair["canonical_inchikey"].nunique() == 1, "they must collapse to one"

    key = pair["canonical_inchikey"].iloc[0]
    assert labels[key] == "yes"
    assert (labels.index == key).sum() == 1
