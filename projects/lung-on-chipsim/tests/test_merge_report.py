"""Merge-stage report — which pipeline stage each canonical-key merge group
collapses at (dispatch #98: "re-run the real-data merge report and report the
stage breakdown before/after").

The stage matters because the groups are NOT all ours: a group whose members
carry byte-identical SOURCE InChIs is an upstream DrugBank limitation no pipeline
change can recover (100 of 191 on the real snapshot, #97). Only groups that merge
at a later stage are the pipeline's doing, and only those are a decision for the
principal. A report that cannot tell the two apart invites the "236/191 over-
merges" framing the CTO retracted.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from chipsim.harmonize.ids import (
    MERGE_STAGES,
    add_canonical_identity,
    canonicalize,
    guard_effect,
    merge_stage_report,
)
from chipsim.ingest.drugbank_snapshot import load_compounds

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = PROJECT_ROOT / "tests" / "fixtures" / "snapshot"

NITISINONE_KETO = (
    "InChI=1S/C14H10F3NO5/c15-14(16,17)7-4-5-8(9(6-7)18(22)23)13(21)12-10(19)2-1-3-11(12)20"
    "/h4-6,12H,1-3H2"
)
NITISINONE_ENOL = (
    "InChI=1S/C14H10F3NO5/c15-14(16,17)7-4-5-8(9(6-7)18(22)23)13(21)12-10(19)2-1-3-11(12)20"
    "/h4-6,21H,1-3H2"
)
ASPIRIN = "InChI=1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)"


def _frame(rows: list[tuple[str, str]]) -> pd.DataFrame:
    return add_canonical_identity(
        pd.DataFrame(rows, columns=["drugbank_id", "inchi"]).assign(inchikey="x")
    )


def test_stages_are_ordered_from_source_to_tautomer():
    assert MERGE_STAGES == ("upstream-duplicate", "parse", "salt", "uncharge", "tautomer")


def test_report_is_one_row_per_merge_group_and_names_the_stage():
    """Verapamil (DB90004) and verapamil HCl (DB90005) merge at the SALT stage."""
    canonical = add_canonical_identity(load_compounds(SNAPSHOT_DIR, min_rows=0))
    report = merge_stage_report(canonical)
    assert list(report.columns) == ["canonical_inchikey", "size", "stage", "drugbank_ids"]
    verapamil = report[report["drugbank_ids"].map(lambda ids: "DB90004" in ids)]
    assert len(verapamil) == 1
    assert verapamil.iloc[0]["stage"] == "salt"
    assert verapamil.iloc[0]["size"] == 2
    assert set(verapamil.iloc[0]["drugbank_ids"]) == {"DB90004", "DB90005"}


def test_byte_identical_source_inchis_are_an_upstream_duplicate():
    report = merge_stage_report(_frame([("A", ASPIRIN), ("B", ASPIRIN)]))
    assert report["stage"].tolist() == ["upstream-duplicate"]


def test_a_tautomer_only_difference_is_the_tautomer_stage():
    report = merge_stage_report(_frame([("K", NITISINONE_KETO), ("E", NITISINONE_ENOL)]))
    assert report["stage"].tolist() == ["tautomer"]


def test_no_merges_gives_an_empty_report_with_the_columns():
    report = merge_stage_report(_frame([("A", ASPIRIN), ("K", NITISINONE_KETO)]))
    assert report.empty
    assert list(report.columns) == ["canonical_inchikey", "size", "stage", "drugbank_ids"]


def test_report_requires_canonical_identity():
    import pytest

    with pytest.raises(ValueError, match="add_canonical_identity"):
        merge_stage_report(pd.DataFrame({"drugbank_id": ["A"], "inchi": [ASPIRIN]}))


# --- the guard's effect, before vs after (#106 §4 / #108) ------------------------

L_ASP = "InChI=1S/C4H7NO4/c5-2(4(8)9)1-3(6)7/h2H,1,5H2,(H,6,7)(H,8,9)/t2-/m0/s1"
D_ASP = "InChI=1S/C4H7NO4/c5-2(4(8)9)1-3(6)7/h2H,1,5H2,(H,6,7)(H,8,9)/t2-/m1/s1"


def test_canonicalize_reports_whether_the_guard_fired():
    assert canonicalize(L_ASP).guard_fired is True
    assert canonicalize(NITISINONE_KETO).guard_fired is False
    assert canonicalize(ASPIRIN).guard_fired is False


def test_canonicalize_with_the_guard_off_reproduces_the_unguarded_key():
    assert (
        canonicalize(L_ASP, stereo_guard=False).inchikey
        == canonicalize(D_ASP, stereo_guard=False).inchikey
    )
    assert canonicalize(L_ASP).inchikey != canonicalize(D_ASP).inchikey


def test_guard_effect_reports_splits_and_unchanged_merges_and_no_new_merges():
    frame = pd.DataFrame(
        [
            ("LA", "L-Aspartic Acid", L_ASP),
            ("DA", "D-Aspartic Acid", D_ASP),
            ("NK", "Nitisinone", NITISINONE_KETO),
            ("NE", "Nitisinone enol", NITISINONE_ENOL),
            ("AS", "Aspirin", ASPIRIN),
        ],
        columns=["drugbank_id", "name", "inchi"],
    ).assign(inchikey="x")
    effect = guard_effect(frame)
    assert effect.compounds == 5
    assert effect.guard_fired == 2
    assert effect.before_breakdown == {"tautomer": 2}
    assert effect.after_breakdown == {"tautomer": 1}
    assert effect.merge_groups_before == 2
    assert effect.merge_groups_after == 1
    assert [sorted(g.members) for g in effect.split_groups] == [
        [("DA", "D-Aspartic Acid"), ("LA", "L-Aspartic Acid")]
    ]
    assert effect.new_merges == ()


def test_guard_effect_split_group_records_the_layers_that_caused_it():
    frame = pd.DataFrame(
        [("LA", "L-Aspartic Acid", L_ASP), ("DA", "D-Aspartic Acid", D_ASP)],
        columns=["drugbank_id", "name", "inchi"],
    ).assign(inchikey="x")
    (group,) = guard_effect(frame).split_groups
    assert group.stage_before == "tautomer"
    assert set(group.layers) == {"t", "m", "s"}


# --- the report entry point (module-level, journaled; not a pipeline subcommand,
#     because T16 pins the CLI inventory to the ETL chain + the human-only seal) ----


def test_merge_report_main_writes_json_and_markdown_and_journals_the_run(tmp_path):
    import json

    from chipsim.harmonize.merge_report import main

    root = tmp_path / "proj"
    (root / "configs").mkdir(parents=True)
    (root / "configs" / "x.yaml").write_text("a: 1\n")
    out = tmp_path / "out"
    code = main(
        [
            "--raw-dir",
            str(SNAPSHOT_DIR),
            "--out",
            str(out),
            "--project-root",
            str(root),
            "--min-rows",
            "0",
            "--no-exclusions",
        ]
    )
    assert code == 0
    report = json.loads((out / "merge_report.json").read_text())
    assert report["compounds"] > 0
    assert set(report["before_breakdown"]) <= set(MERGE_STAGES)
    assert "split_groups" in report and "new_merges" in report and "guard_fired" in report
    md = (out / "merge_report.md").read_text()
    assert "## Split groups" in md and "## Stage breakdown" in md
    runs = [d for d in (root / "journal").iterdir() if d.is_dir() and d.name != "invocations"]
    assert len(runs) == 1
    assert (runs[0] / "outcome.json").exists()
    assert (runs[0] / "configs" / "x.yaml").exists(), "the run did not snapshot its configs"


def test_guard_effect_reclassifies_a_residual_pair_by_membership_not_by_key():
    """When the guard splits a stereo member away, the members that remain
    together get a NEW (pre-tautomer) key. Their stage can change — two copies of
    one source InChI that used to sit in a tautomer-stage group are now a pure
    upstream duplicate. That is how the source-identical count moves (100 → 101 on
    the real snapshot, #106 §5) with zero new merges; a definition keyed on the
    canonical key never sees it."""
    frame = pd.DataFrame(
        [
            ("LA1", "L-Aspartic Acid", L_ASP),
            ("LA2", "L-Aspartic Acid (dup)", L_ASP),
            ("DA", "D-Aspartic Acid", D_ASP),
        ],
        columns=["drugbank_id", "name", "inchi"],
    ).assign(inchikey="x")
    effect = guard_effect(frame)
    assert effect.before_breakdown == {"tautomer": 1}
    assert effect.after_breakdown == {"upstream-duplicate": 1}
    assert [(b, a) for _, b, a in effect.reclassified] == [("tautomer", "upstream-duplicate")]
    assert effect.new_merges == ()
