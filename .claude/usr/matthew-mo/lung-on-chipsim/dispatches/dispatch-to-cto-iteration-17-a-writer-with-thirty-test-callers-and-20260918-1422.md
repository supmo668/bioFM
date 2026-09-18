---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-18T21:22
status: created
priority: normal
size: task
subject: "Iteration 17 - a writer with thirty test callers and none in production, and T6s done-condition never met the real snapshot"
in_reply_to: null
---

# Iteration 17 - a writer with thirty test callers and none in production, and T6s done-condition never met the real snapshot

event: iteration-complete
workstream: lung-on-chipsim
iteration: "§17"
branch: lung-on-chipsim
commit_hash: 2d1e283
qgr_receipt: workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-bioFM-qgr-iteration-complete-20260918-1421-4efd773.md
hashes: "A == E == 4efd773, base 660d600, 3 files, --project bioFM"
remote_refs_observed:
  origin/lung-on-chipsim: 2d1e283e976ddbb484e1d7ac7f04842ebc0deebb
  origin/main: df89f5039be4449aa3f7246ee496b28edb708cfe (untouched)

closing_at_the_boundary: |
  Last time I pushed two boundaries before returning to you and you said "close the loop at the
  boundary next time and we are square". This is that.

r2_33_applied_from_the_start: |
  Your clause said: a done-condition naming a path is checked against that path, BY READING THE
  PLAN, before the step is called complete. I applied it before touching anything this iteration
  rather than after, and it is what found both gaps. Neither was visible from the test suite.

finding_1_a_writer_with_thirty_test_callers_and_none_in_production: |
  `write_adjudication_worksheet` had ~30 call sites and EVERY ONE WAS A TEST. No CLI subcommand, no
  script, and T16's n8n export is descoped — so there was never going to be another invocation path.
  r2.28's defect again, and this one sits directly between the principal and a 60-90 MINUTE HUMAN
  TASK.

  `adjudication-worksheet` is the caller. It REFUSES when no roster exists rather than emitting a
  worksheet over whatever the snapshot happened to contain: T13's done-condition is "exactly one row
  per T18 roster entry", T18 is human-owned, and `load_poc_roster` validates a roster a human wrote
  and NEVER generates one. Handing the principal the wrong rows would cost the 60-90 minutes that
  T13's never-clobber rule already exists to protect. It also refuses when the roster names a key
  the labeller did not produce — two human-ratified inputs disagreeing must surface, not become a
  silently shorter sheet.

finding_2_t6s_done_condition_never_met_the_real_snapshot: |
  T6's done-condition — INCLUDING THE GOLDEN ROW r2.10 CALLS "WHY WE KNOW" — was verified only
  against `tests/fixtures/snapshot`, whose ids are the synthetic DB9xxxx range. `test_parse.py`
  carries no `integration` mark.

  I proved the gap by PUTTING THE DEFECT BACK. With `HUMAN_ORGANISM_LABELS` accepting only
  `Homo sapiens` — which the pinned snapshot never says:

      fixture golden-row test : GREEN
      REAL-snapshot test      : RED

  The fixture test cannot see the defect it was written about. That is r2.10's own class — green
  tests, correct about the fixture, wrong about the world — INSIDE THE GUARD r2.10 INSTALLED.

  NO DRUGBANK ACCESSION IS IN IT. The golden ROW needs an identifier; the golden PROPERTY does not.
  It asserts at least one transporter edge to the panel's ABCB1 accession survives the species
  filter, RESOLVING that accession from the ratified panel — composition is configuration, not code
  (defect 4 / AM-2), which is exactly why `pgp_substrate_label` refuses to hard-code it. It SKIPS
  when the snapshot is absent, so a clone without DVC data is not told it has a defect it does not
  have.

a_test_that_cannot_exist_reported_not_worked_around: |
  T13's happy path needs a valid roster: 20-40 entries all present in the snapshot. The fixture
  snapshot holds EIGHT compounds; a roster is `canonical_inchikey` + `name` + `evidence_doi`, a
  NAME-BESIDE-STRUCTURE table which may not be committed; and editing the fixture TSVs is barred. No
  tracked fixture can cover it under this project's own compliance rules.

  The roster LOADER is substituted instead — the validator has its own tests — and the keys are read
  from the fixture snapshot at run time rather than written down. The row FLOOR is relaxed in the
  TEST and NEVER in the command: a `--min-rows` flag would be precisely the escape the floor exists
  to prevent (defect 9).

the_registry_caught_me_twice_more: |
  I registered the subparser BEFORE `fetch` — which would have declared T13 the FIRST ETL stage —
  and I declared the command in NEITHER category tuple. Both caught by assertions that already
  existed. Second and third time this session a registry has caught me; that is the property working,
  and I would rather report it than let the diff read as though I got it right first.

  CATEGORY, and I want your view if you disagree: the test states why `panel-seal` is non-ETL —
  Global Constraint 4 RESERVES RUNNING IT TO A HUMAN, and keeping it out of the workflow is "the
  only mechanical support the rule gets: an unattended pipeline must not be able to invoke it". T13
  is NOT human-reserved; it is CA work producing a draft FOR a human, reading the snapshot and
  writing a derived artifact. So I declared it ETL, which also earns it the per-run config snapshot
  and the §16 approval prompt. The tuple does conflate "is an ETL run" with "is an n8n node", and
  T13 is the first command where those come apart — it should not be a node in an unattended chain
  that could regenerate a sheet mid-adjudication, even though it is an ETL stage.

verification:
  suite: "1028 -> 1033 passed / 5 skipped, 0 DESELECTED (delta = the 5 tests added)"
  mutation: "r2.10 defect restored (fixture GREEN / real RED); T13 roster refusal KILLED; both modules restored byte-for-byte"
  gates: "both exit 0, 758 tracked, run immediately before the push"
  format_lint: "read AFTER the last edit"

m0a_status_the_part_that_matters: |
  THE CRITICAL PATH IS BLOCKED ON THE PRINCIPAL, NOT ON ME. T8 is done (`ratified: true`). T18 —
  human-owned, 30-45 min — has NO ROSTER ON DISK, and `roster.py` only validates one a human wrote.
  T13 cannot emit until it lands; T14 cannot start until T13 does. Building the caller before the
  input exists is the point: when the roster lands, T13 runs, instead of someone discovering at that
  moment that it cannot be invoked.

standing: |
  r2.28's property remains AVAILABLE, NOT ENFORCED. Nothing here touches it.

next_handoff: cto — no ruling required unless you disagree with declaring T13 an ETL stage.
