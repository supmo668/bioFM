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
import yaml

from chipsim.harmonize.ids import add_canonical_identity
from chipsim.harmonize.pgp_label import (
    PRE_ADJUDICATION_LABELS,
    barrier_panel_edges,
    load_ratified_panel,
    panel_digest,
    pgp_substrate_label,
    resolve_panel_accession,
    seal_panel,
)
from chipsim.ingest.drugbank_snapshot import load_compounds, load_protein_edges

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = PROJECT_ROOT / "tests" / "fixtures" / "snapshot"


@pytest.fixture
def compounds() -> pd.DataFrame:
    return add_canonical_identity(load_compounds(SNAPSHOT_DIR, min_rows=0))


@pytest.fixture
def edges() -> pd.DataFrame:
    return load_protein_edges(SNAPSHOT_DIR, min_rows=0)


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


# --------------------------------------------------------------------------- #
# Panel schema validation — a malformed entry must fail AT LOAD, not downstream
# --------------------------------------------------------------------------- #


def _panel_doc(panel_ratified_path):
    return yaml.safe_load(Path(panel_ratified_path).read_text())


def test_one_entry_missing_face_raises_rather_than_yielding_nan(tmp_path, panel_ratified_path):
    """The NaN trap: pd.DataFrame over a list of dicts fills a key missing from
    SOME rows with NaN instead of raising.

    Before load_ratified_panel validated entries, dropping `face` from ONE entry
    produced a joined frame carrying NaN in the `face` column and no error at all;
    only an ALL-entries-missing key raised KeyError. A human editing this file at
    T8 is precisely who drops one key from one row.
    """
    doc = _panel_doc(panel_ratified_path)
    del doc["panel"][1]["face"]
    p = tmp_path / "one_face_missing.yaml"
    p.write_text(yaml.safe_dump(doc))

    with pytest.raises(RuntimeError, match="face"):
        load_ratified_panel(p)


def test_an_out_of_domain_face_raises(tmp_path, panel_ratified_path):
    doc = _panel_doc(panel_ratified_path)
    doc["panel"][0]["face"] = "appical"
    p = tmp_path / "typo_face.yaml"
    p.write_text(yaml.safe_dump(doc))

    with pytest.raises(RuntimeError, match="appical"):
        load_ratified_panel(p)


def test_a_duplicate_symbol_raises(tmp_path, panel_ratified_path):
    """Accessions resolve BY SYMBOL, so a second row with the same symbol is
    unreachable — an edit that looks applied but never takes effect."""
    doc = _panel_doc(panel_ratified_path)
    dup = dict(doc["panel"][0])
    dup["uniprot"] = "Q00000"
    doc["panel"].append(dup)
    p = tmp_path / "dup_symbol.yaml"
    p.write_text(yaml.safe_dump(doc))

    with pytest.raises(RuntimeError, match="duplicate symbol"):
        load_ratified_panel(p)


def test_a_well_formed_panel_still_loads(panel_ratified_path):
    """Positive control — the validation above must not reject the real fixture."""
    doc = load_ratified_panel(panel_ratified_path)
    assert len(doc["panel"]) >= 1


def test_fixture_face_agreement_with_live_panel(panel_ratified_path):
    """Fixture faces must match the live panel, symbol by symbol.

    load_ratified_panel REFUSES the live config while `ratified: false`, so every
    offline consumer — including the first M1 transport test — is structurally
    forced onto this fixture. A fixture disagreeing with the authoritative panel
    would bake the wrong transport direction into M1 and make the real config look
    like the mistaken one. A comment in the fixture header cannot prevent that; a
    standing test that names the live config can.

    This was briefly skipped while T7 prescribed `apical` and the live config had
    already moved to `basolateral` — updating the fixtures then would have spread
    an un-authorized value into five more files. r2.3 amended T7 (CTO ruling N1),
    so the fixtures now mirror the plan and this enforces rather than announces.
    If T8's ratification changes any face, this goes red until the fixtures are
    re-synced — which is the point.
    """
    live_path = Path(__file__).resolve().parent.parent / "configs" / "barrier_panel.yaml"
    live_faces = {e["symbol"]: e["face"] for e in yaml.safe_load(live_path.read_text())["panel"]}
    fixture_doc = yaml.safe_load(Path(panel_ratified_path).read_text())
    fixture_faces = {e["symbol"]: e["face"] for e in fixture_doc["panel"]}

    shared = live_faces.keys() & fixture_faces.keys()
    assert shared, "fixture and live panel share no symbols — one of them is wrong"
    mismatched = {
        s: (fixture_faces[s], live_faces[s]) for s in shared if fixture_faces[s] != live_faces[s]
    }
    assert not mismatched, (
        "fixture face(s) disagree with the ratified panel {symbol: (fixture, live)}: "
        f"{mismatched}. configs/barrier_panel.yaml is authoritative."
    )


# --------------------------------------------------------------------------- #
# T7a · the panel seal — binds a ratification to the contents it attested
# --------------------------------------------------------------------------- #


def _sealed_copy(tmp_path, panel_ratified_path, name="sealed.yaml"):
    """A ratified fixture, copied and sealed. Fixtures only — Global Constraint 4
    forbids an agent sealing the live configs/barrier_panel.yaml."""
    p = tmp_path / name
    p.write_text(Path(panel_ratified_path).read_text())
    digest = seal_panel(p)
    return p, digest


def test_t7a_sealing_then_editing_a_face_makes_the_load_raise(tmp_path, panel_ratified_path):
    """Done-condition 1. This is the whole point: after T8, `ratified: true` must
    stop attesting the moment any entry changes. Before the seal, a post-
    ratification face flip was undetectable — T19 checks only accession, taxon and
    gene symbol."""
    p, _ = _sealed_copy(tmp_path, panel_ratified_path)
    assert load_ratified_panel(p)  # sealed and intact -> loads

    doc = yaml.safe_load(p.read_text())
    for entry in doc["panel"]:
        if entry["symbol"] == "TFRC":
            entry["face"] = "apical" if entry["face"] == "basolateral" else "basolateral"
    # Rewrite preserving the seal line, exactly as a hand-edit would.
    p.write_text(yaml.safe_dump(doc))

    with pytest.raises(RuntimeError, match="FAILS ITS SEAL"):
        load_ratified_panel(p)


def test_t7a_a_deleted_entry_also_breaks_the_seal(tmp_path, panel_ratified_path):
    """Deletion is the edit T8 explicitly permits, so it must be covered too."""
    p, _ = _sealed_copy(tmp_path, panel_ratified_path)
    doc = yaml.safe_load(p.read_text())
    doc["panel"] = [e for e in doc["panel"] if e["symbol"] != "ABCC1"]
    p.write_text(yaml.safe_dump(doc))

    with pytest.raises(RuntimeError, match="FAILS ITS SEAL"):
        load_ratified_panel(p)


def test_t7a_sealing_is_idempotent(tmp_path, panel_ratified_path):
    """Done-condition 2. A digest that churned on re-seal would train a human to
    ignore mismatches."""
    p, first = _sealed_copy(tmp_path, panel_ratified_path)
    second = seal_panel(p)
    assert first == second
    assert load_ratified_panel(p)


def test_t7a_sealing_an_unratified_panel_raises(tmp_path, panel_unratified_path):
    """Done-condition 3, and the sharpest one. A digest written while
    `ratified: false` would be an attestation record binding nothing a human
    signed — worse than no seal, because it LOOKS like one."""
    p = tmp_path / "unratified.yaml"
    p.write_text(Path(panel_unratified_path).read_text())

    with pytest.raises(RuntimeError, match="not ratified"):
        seal_panel(p)
    assert "ratified_panel_sha256" not in p.read_text(), (
        "seal_panel wrote a digest into an unratified panel"
    )


def test_t7a_sealing_a_ratified_panel_with_no_ratifier_raises(tmp_path, fixture_dir):
    """`ratified: true` with an empty ratified_by is not an attestation, so it
    must not be sealable either — otherwise the seal launders it into one."""
    p = tmp_path / "no_ratifier.yaml"
    p.write_text((fixture_dir / "barrier_panel_ratified_no_ratifier.yaml").read_text())

    with pytest.raises(RuntimeError, match="not ratified"):
        seal_panel(p)


def test_t7a_seal_ignores_attestation_fields_and_comments(tmp_path, panel_ratified_path):
    """The digest covers the PANEL, not the attribution or the file's comments.

    Re-attributing a ratification, or the comment churn that T8's human-facing
    instructions attract, must not read as tampering with the accessions — or the
    signal is lost in noise.
    """
    p, digest = _sealed_copy(tmp_path, panel_ratified_path)
    text = p.read_text()
    text = text.replace('ratified_by: "FIXTURE - not a real ratification"', 'ratified_by: "Someone Else"')
    p.write_text("# a new leading comment\n" + text)

    doc = yaml.safe_load(p.read_text())
    assert panel_digest(doc["panel"]) == digest


def test_t7a_seal_is_order_independent(tmp_path, panel_ratified_path):
    """Reordering entries is not a content change. Canonicalization sorts by
    symbol, so a human tidying the file does not trip the seal."""
    p, digest = _sealed_copy(tmp_path, panel_ratified_path)
    doc = yaml.safe_load(p.read_text())
    doc["panel"] = list(reversed(doc["panel"]))
    assert panel_digest(doc["panel"]) == digest


def test_t7a_seal_preserves_the_human_facing_comments(tmp_path, panel_ratified_path):
    """seal_panel must not re-dump the YAML: the live panel carries T8's
    instructions as comments, and yaml.safe_dump would delete every one."""
    p = tmp_path / "commented.yaml"
    p.write_text("# LOAD-BEARING COMMENT\n" + Path(panel_ratified_path).read_text())
    seal_panel(p)
    assert "# LOAD-BEARING COMMENT" in p.read_text()
