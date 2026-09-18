---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-18T20:11
status: created
priority: normal
size: task
subject: "Iterations 16 + T5a - approve-on-execute had one call site, and the pipeline produced its first artifact"
in_reply_to: null
---

# Iterations 16 + T5a - approve-on-execute had one call site, and the pipeline produced its first artifact

event: iteration-complete
workstream: lung-on-chipsim
iteration: "§16 + T5a"
branch: lung-on-chipsim
commit_hash: 4ee93af
qgr_receipts:
  - workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-bioFM-qgr-iteration-complete-20260918-1246-be385b0.md
  - workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-bioFM-qgr-iteration-complete-20260918-1309-c2074df.md
remote_refs_observed:
  origin/lung-on-chipsim: 4ee93af1c6b0dbe2677d25adf83e48f338130607
  origin/main: df89f5039be4449aa3f7246ee496b28edb708cfe (untouched)

late_dispatch_disclosed: |
  TWO BOUNDARIES IN ONE DISPATCH, and that is my error, not a batching decision. I pushed §16
  (83c5b01) and went straight to asking the principal for run approval without returning to you
  first. The loop should have closed at §16. Reporting it rather than letting the combined dispatch
  read as the plan.

the_scope_correction_that_produced_this: |
  I RAISED A CONCERN AGAINST MY OWN WORK AND THE PRINCIPAL RULED ON IT. Five gated iterations had
  gone into the record-content guard while the PoC's critical path had not moved: raw snapshot in
  and DVC-tracked, but `data/interim` and `data/processed` EMPTY with no DVC pipeline, so the
  human-owned tasks (T8, T18, T14) could not start.

  The guard work was legitimate, CTO-directed, and found five real false cleans. It had ALSO become
  the comfortable thing to keep improving. Same defect this workstream keeps finding, one level up:
  a green suite and a hardened gate are a MECHANISM; the artifacts are the COVERAGE.

  Principal ruled: advance M0a, and enforce the run-config requirement BEFORE the first run.

s16_approve_on_execute: |
  The standing instruction has THREE clauses and I measured each against CALL SITES, not docstrings:

    log/save the exact config    BUILT     journal.start_run snapshots configs before the stage
    new config copies per run    BUILT     14 run dirs on disk, each with its own configs/ + digests
    APPROVE ON EXECUTE           MISSING   ONE call site, inside panel-seal, for every ETL stage

  Two of three reads as satisfied. That is exactly why the check was against call sites — the same
  method that found r2.28's ruling implemented as a mechanism nothing invoked.

  Shaped like the seal gate INCLUDING its honesty bounds: converts an ACCIDENTAL run into a
  DELIBERATE one and makes the difference visible afterwards. Does NOT identify who approved.

  `--yes` is a RECORDED ESCAPE, not a bypass — an unrecorded escape would make an unattended run
  indistinguishable from an answered one, which is the false-clean shape we keep finding. The
  mutant recording `--yes` as "interactive" is one of six killed.

  SNAPSHOT -> ASK -> RUN, mirroring panel-seal. A declined run KEEPS its config snapshot and is
  written status="declined". Measured, not asserted:

      outcome=ok        approval=flag  configs=5
      outcome=declined  approval=NONE  configs=5

  THE READ-ONLY REPORTS ARE DELIBERATELY NOT GATED, pinned by a test: a prompt in front of
  `record-content-report` would make every gated boundary need a terminal, and the first person in
  a hurry would delete the gate. A control nobody can run is not a control — E-10, one level up.

  The writer registry caught `_write_approval_record` the moment it existed; classified beside
  `journal.start_run`. Five journal tests that drove ETL stages headlessly now pass `--yes`, which
  is those runs declaring in the record that no human approved them.

t5a_the_first_artifact: |
  6802 compounds x 9 columns persisted; 16299 protein edges read; 8 pre-registered unparseable
  compounds excluded via the ratified roster; 757 raw-vs-canonical identity disagreements surfaced
  as a NUMBER, not a verdict.

  I WROTE IT TO THE WRONG PATH FIRST. T5a specifies data/processed/drugbank_compounds.parquet and
  says in the same sentence "not compounds.parquet, which A&D §1 reserves for the harmonized
  multi-source S1 artifact (defect 30)". I wrote data/interim/compounds.parquet — wrong directory,
  and the exact filename the plan forbids. Found by going to check whether the step was complete.
  Removed and redone.

  THE OUTPUT-ROOT GUARD CORRECTLY ALLOWED IT, and this is the part worth your attention:
  `data/interim` IS a declared root. That guard answers WHERE a record-bearing payload may land,
  never WHICH artifact the plan asked for. "It passed the guard" is an inference that gets EASIER
  to make the more guards exist, and it was wrong here. I do not think this needs a new mechanism;
  I think it needs saying.

  I ALSO NEARLY REPORTED TWO DEFECTS THAT DID NOT EXIST, both in my own harness: the declared
  column ORDER (documented), and `groups` holding list-valued cells where a parquet round-trip
  returns ndarray. Every column compares equal once containers are normalised. Neither was reported
  as a defect.

  DONE-WHEN measured on the REAL artifact: round-trips identical by value; sidecar digest verified
  by RECOMPUTING sha256 over the bytes on disk, because a sidecar checked against itself proves
  nothing. Parquet stays git-ignored, only the digest sidecar is tracked, as T5a specifies.

verification:
  suite: "1021 -> 1028 passed / 5 skipped, 0 DESELECTED. The 5 skips are future-work gates (ChEMBL S1, M0 slice 3, M1 ODE, T14's human file which arms itself when it lands) — none was waiting on this artifact."
  mutation: "S16 6/6 KILLED BY ASSERTION, pipeline.py restored byte-for-byte"
  gates: "both exit 0 at every boundary, 749 tracked at the last push, BOTH run immediately before each push"
  hash_d: "PRINCIPAL DIRECTIVE via AskUserQuestion on both boundaries — not auto-approved"

accession_hygiene: |
  The excluded roster holds REAL DrugBank identifiers, not the synthetic DB9xxxx range. They appear
  in NO commit message, receipt, triage document or dispatch — including this one.

standing: |
  r2.28's property remains AVAILABLE, NOT ENFORCED. Producing an artifact does not touch that.

next: |
  M0a: T6 (protein-edge table), then T9/T10 toward T13's adjudication worksheet, which is what
  unblocks the principal's T14. T8 and T18 are human-owned and not blocked by any of this.

next_handoff: cto — no ruling required unless you disagree with the scope correction or with gating ETL runs.
