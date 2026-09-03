---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-08-31T18:51
status: created
priority: normal
size: task
subject: "Iteration P0.2 complete on lung-on-chipsim — E-1..E-5 applied+falsified; 27 QG findings; agent-side slice-1 work exhausted"
in_reply_to: null
---

# Iteration P0.2 complete on lung-on-chipsim — E-1..E-5 applied+falsified; 27 QG findings; agent-side slice-1 work exhausted

event: iteration-complete
workstream: lung-on-chipsim
iteration: P0.2
phase: P0
branch: lung-on-chipsim
commit_hash: fd945cc
qgr_receipt: workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-bioFM-qgr-iteration-complete-20260831-1148-b7d4221.md
plan_gate: green at b79a5e4 (r2.1, merged with trunk)
tests: 284 passed / 6 skipped; 15 network passed; ruff clean

summary: |
  RULINGS E-1..E-5 ALL APPLIED — and each falsified rather than assumed.

  E-5 (data-loss fix) — .dvc/config now url = /Users/mo/.aiadlc/biofm/dvc-storage.
  Verified empirically: 'git -C <store> rev-parse' returns 'fatal: not a git
  repository', i.e. it is inside NO git tree, beside the ISCP state files. Three S9
  guards added; re-introducing the r2 relative path fails all three. Plan S9 carries
  the four-point rationale so nobody simplifies it back. F-02 belt-and-braces
  .dvc-storage/ ignore retained; widened test_drugbank_not_vendored kept.

  E-4 — nested probe set; the r2 top-level-only .gitignore fails 4 probes. Worth
  noting: the top-level data/raw/drugbank.dvc probe STILL PASSED under the broken
  rules, which is precisely your point that a top-level probe does not test the rule.

  E-1/E-2/E-3 — ratified wording folded into plan and code. E-1's conditional contract
  is in chipsim/harmonize/contracts.py and asserts BOTH directions; T11 signed off
  against fixtures per your note.

  TASKS BUILT: T5, T5a, T5b, T6, T7, T9, T10, T11, T12, T13, T15, T16, T17, T19, S11a.
  T4a/T4 remain blocked on T2 — their legs were changed from an unconditional skip to
  a skipif KEYED ON THE ARTIFACT, so they self-lift when T2 lands rather than staying
  silently green forever.

  QUALITY GATE: 27 findings fixed (15 correctness, 12 test-validity), 1 accepted-as-is.
  The biggest catch was a data-loss bug in the module that exists to prevent data loss:
  the never-clobber guard keyed on adjudicated_label alone, so a row with only
  evidence_doi/adjudicated_by filled — the exact mid-session human state, because
  reviewers collect DOIs first and enter verdicts last — was invisible and silently
  dropped. Reproduced, fixed, and the worksheet write is now atomic too.
  Three tests were satisfied by provably wrong implementations (a no-op merge, a
  reversed verdict column, a closed tautology that imported no production code).
  All 7 reviewer mutations that previously passed now FAIL.

  HUMAN BLOCKERS: T1/T2/T8/T14/T18 all still absent. Nothing fabricated — no
  provenance file, commit SHA, UniProt ratification, roster entry or evidence DOI.
  configs/barrier_panel.yaml ships ratified: false. T19 did confirm all seven DRAFT
  accessions resolve at UniProt as human with matching gene symbols — mechanical
  groundwork for T8, explicitly NOT a ratification.

process_note: |
  Two things for you, both about the hash-locked plan.
  1) Before your directive arrived I had already amended build-plan.md on the
     principal's explicit instruction and re-signed at b79a5e4 — the same hash you
     independently landed. I have merged trunk and taken YOUR signature on conflict.
     Standing rule understood and recorded in the QG report header: from here I
     report needed amendments and you land + re-sign in one move.
  2) receipt-sign --project: P0.1 used 'bioFM', I first signed P0.2 with
     'lung-on-chipsim', and git-safe-commit --boundary then could not find a matching
     receipt (it looks up by project). Re-signed with bioFM and it passed. Flagging in
     case that field should be derived rather than passed by hand.

blocked_on: |
  No agent-side M0 slice-1 tasks remain executable against fixtures. Everything left
  needs one of the five human artifacts.

next_handoff: cto — decide: (a) /pr-cto-land this branch, (b) authorize M0 slice 2, or
  (c) hold until the human artifacts land. Standing by; I will not open a PR.
