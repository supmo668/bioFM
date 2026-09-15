---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-15T09:38
status: created
priority: high
size: task
subject: "ITERATION-COMPLETE P0.4 on lung-on-chipsim — T4 (r2.11) gated, boundary ecda7b0, receipt 2e1937e; QG-11/QG-12 up; §2 next per #106/#108 (pid 49951)"
in_reply_to: null
---

# ITERATION-COMPLETE P0.4 on lung-on-chipsim — T4 (r2.11) gated, boundary ecda7b0, receipt 2e1937e; QG-11/QG-12 up; §2 next per #106/#108 (pid 49951)

event: iteration-complete   # sent as type 'dispatch': this tool build rejects the 'iteration-complete' type the skill prescribes (feedback filed)
workstream: lung-on-chipsim
iteration: P0.4
phase: P0
branch: lung-on-chipsim
commit_hash: ecda7b0
stage_hash: e1b57a3
files_changed: 6 in the fix cycle (chipsim/ingest/drugbank_snapshot.py, tests/test_provenance.py, tests/test_snapshot_fetch.py, tests/test_scaffold.py, tests/test_unparseable_exclusions.py, workstreams/lung-on-chipsim/parked/README.md) + 3 pointers and 3 tests in 6561963
summary: T4 done under r2.11 (gate verifies 26b7a4f after merging local main 3d8be06). QG: 14 findings kept, 12 fixed. As landed at 6561963, T4's four done-conditions were satisfiable by a STALE, MISMATCHED or UNPUSHED snapshot — (c) 'dvc status' has no exit-code contract without -q (the test PASSED with a stale md5, measured); check-ignore answered from the index; a deleted pointer passed T11; nothing bound a pointer to its own TSV; the payload had never been pushed (remote empty — now pushed, 3 files, '--cloud -q' exit 0). Every fix has a falsification (stale-md5; removed-negation fails 8 probes; moved-pointer fails its row; pre-push red). Vendoring rule now requires a pointer-shaped .dvc and scans the project tree for real accessions (two illustrative real IDs in tests moved to DB9xxxx). 567 pass / 0 fail / 4 skip; ruff clean.
qgr_receipt: workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-bioFM-qgr-iteration-complete-20260915-0231-2e1937e.md
history_note: an unshared tip cb85903 was replaced by reset --soft before any push (mis-generated message after a rejected work-item id); nothing pushed was touched. Boundary is ecda7b0 (receipt-verified at commit time); d434cda records the sha in context.json.
decisions_up: |
  QG-11 (you): T5b in build-plan.md carries no note of the stereo-guard ruling/hold; convention is an inline blockquote like T4's r2.11 note. Plan is hash-locked — yours to amend. Dev-log line added.
  QG-12 (principal, via you): the parked §2 patch carries six InChI strings + eight real DrugBank accessions 'copied verbatim from drugbank.tsv' — the first real DrugBank record content tracked in git (every other test uses synthetic DB9xxxx). InChI/InChIKey are public structure identifiers and six records is plausibly de minimis, but the project's stated invariant ('never redistributes DrugBank') now has an in-repo counterexample. The new real-accession scan WILL fail the moment the patch is applied into tests/ per #106; I will not allow-list it silently. Options: regenerate the InChIs from a public source (PubChem) and cite it, or record a de minimis licensing note. I need the principal's word before un-parking.
next: §2 stereo guard per #106 + #108 — starting now: un-park, retarget {t,m,s}, /b excluded; Thr/Ile/Asp/Phe distinct; Nitisinone + benzimidazole 1H/3H/CRA_1144 merged; malate named accepted loss; MODULE-measured before/after breakdown, all 41 splits listed by name, your numbers (1,599/6,802; 191→156; 48→7; 100→101) reproduced or the disagreement raised.
emitted_at: 2026-09-15T09:38Z
next_handoff: cto — ack; QG-11 plan amendment; QG-12 routed to the principal (blocks un-parking); then /pr-cto-land after §2's iteration + /pr-submit
iteration_linear_sync: false
