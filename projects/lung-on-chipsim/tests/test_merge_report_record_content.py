"""The tracked merge report carries NO DrugBank record content — CTO #122 §2.

The principal's invariant (#120 §1, #122): the project does not redistribute DrugBank
RECORD CONTENT — accessions, DrugBank-coined names, and above all the association of
either with a structure. The first generator wrote every split group's members as
`[accession, DrugBank name]` pairs into a TRACKED `merge_report.json` — 89 accessions on
the real snapshot. A generator that re-creates forbidden content on every run is worse
than the content, because it returns (#122 §2), so the fix is in the generator:

  - tracked outputs (`merge_report.json`, `merge_report.md`) identify members by
    canonical InChIKey only;
  - the id/name/key mapping is written to the UNTRACKED journal run directory, beside
    the licensed data, and nowhere else.

#108's "list all 41 split groups by name" requirement is RETIRED by #122 §2.

IDs and names here are SYNTHETIC (DB9nnnn range, invented names) so a leak is greppable.
Structures cite PubChem: L-aspartic acid CID 5960, D-aspartic acid CID 83887 (retrieved
2026-09-15).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

from chipsim.harmonize.ids import canonicalize, guard_effect
from chipsim.harmonize.merge_report import main, members_mapping, render_markdown, report_payload

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = PROJECT_ROOT / "tests" / "fixtures" / "snapshot"

#: PubChem CID 5960 / 83887, retrieved 2026-09-15.
L_ASP = "InChI=1S/C4H7NO4/c5-2(4(8)9)1-3(6)7/h2H,1,5H2,(H,6,7)(H,8,9)/t2-/m0/s1"
D_ASP = "InChI=1S/C4H7NO4/c5-2(4(8)9)1-3(6)7/h2H,1,5H2,(H,6,7)(H,8,9)/t2-/m1/s1"

SYNTHETIC_IDS = ("DB90901", "DB90902")
SYNTHETIC_NAMES = ("Synthetic Name Alpha", "Synthetic Name Beta")
INCHIKEY = re.compile(r"^[A-Z]{14}-[A-Z]{10}-[A-Z]$")


def _effect():
    frame = pd.DataFrame(
        [
            (SYNTHETIC_IDS[0], SYNTHETIC_NAMES[0], L_ASP),
            (SYNTHETIC_IDS[1], SYNTHETIC_NAMES[1], D_ASP),
        ],
        columns=["drugbank_id", "name", "inchi"],
    ).assign(inchikey="x")
    return guard_effect(frame)


def _assert_no_record_content(text: str) -> None:
    for token in (*SYNTHETIC_IDS, *SYNTHETIC_NAMES):
        assert token not in text, f"tracked report output leaks {token!r}"


def test_split_group_carries_each_members_canonical_key():
    (group,) = _effect().split_groups
    assert group.member_keys == (canonicalize(L_ASP).inchikey, canonicalize(D_ASP).inchikey)
    assert all(INCHIKEY.match(k) for k in group.member_keys)


def test_report_payload_identifies_members_by_inchikey_only():
    payload = report_payload(_effect(), raw_dir="raw", run_dir="run", excluded=0)
    text = json.dumps(payload)
    _assert_no_record_content(text)
    (group,) = payload["split_groups"]
    assert "members" not in group
    assert group["member_keys"] == [canonicalize(L_ASP).inchikey, canonicalize(D_ASP).inchikey]


def test_rendered_markdown_carries_no_ids_or_names():
    md = render_markdown(_effect(), raw_dir="raw", run_dir="run")
    _assert_no_record_content(md)
    assert canonicalize(L_ASP).inchikey in md


def test_members_mapping_holds_the_association_for_the_journal_only():
    rows = members_mapping(_effect())
    assert {(r["drugbank_id"], r["name"], r["canonical_inchikey"]) for r in rows} == {
        (SYNTHETIC_IDS[0], SYNTHETIC_NAMES[0], canonicalize(L_ASP).inchikey),
        (SYNTHETIC_IDS[1], SYNTHETIC_NAMES[1], canonicalize(D_ASP).inchikey),
    }


def test_main_writes_the_mapping_into_the_journal_run_and_not_the_tracked_out_dir(tmp_path):
    root = tmp_path / "proj"
    (root / "configs").mkdir(parents=True)
    (root / "configs" / "x.yaml").write_text("a: 1\n")
    out = tmp_path / "out"
    assert (
        main(
            [
                "--raw-dir", str(SNAPSHOT_DIR),
                "--out", str(out),
                "--project-root", str(root),
                "--min-rows", "0",
                "--no-exclusions",
            ]
        )
        == 0
    )
    runs = [d for d in (root / "journal").iterdir() if d.is_dir() and d.name != "invocations"]
    assert len(runs) == 1
    assert (runs[0] / "merge_report_members.json").exists()
    assert sorted(p.name for p in out.iterdir()) == ["merge_report.json", "merge_report.md"]
