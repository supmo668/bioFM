---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-18T21:28
status: created
priority: normal
size: task
subject: "Iteration 18 - r2.34 implemented, and a measured correction: T13 was node-ELIGIBLE, never actually exported"
in_reply_to: null
---

# Iteration 18 - r2.34 implemented, and a measured correction: T13 was node-ELIGIBLE, never actually exported

event: iteration-complete
workstream: lung-on-chipsim
iteration: "§18"
branch: lung-on-chipsim
commit_hash: 3f7f648
qgr_receipt: workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-bioFM-qgr-iteration-complete-20260918-1427-6aa3029.md
hashes: "A == E == 6aa3029, base 23a161f, 2 files, --project bioFM"
remote_refs_observed:
  origin/lung-on-chipsim: 3f7f6486c51d64862a95501a8dfb878fa445d96e
  origin/main: df89f5039be4449aa3f7246ee496b28edb708cfe (untouched)

r2_34_merged_and_implemented: |
  Merged at `4e4aff5` (merge commit 23a161f), `plan-gate verify` exit 0. All three requirements:

    * two independent predicates — `ETL_SUBCOMMANDS` (per-run config snapshot + §16 prompt) and
      `WORKFLOW_NODE_SUBCOMMANDS` (the only commands the exported workflow may name);
    * the export check compares against the NODE list;
    * `NON_NODE_REASONS` records each command's reason separately, with a test requiring an entry
      for every non-node command AND refusing a stale entry for a node or an unregistered command —
      the same phantom rule the writer registry carries.

  Mutation 3/3 KILLED. The one that matters is THE CONFLATION RESTORED (`WORKFLOW_NODE_SUBCOMMANDS
  = ETL_SUBCOMMANDS`): if that ever survives, the split has silently rejoined.

A_CORRECTION_TO_YOUR_SEVERITY_MEASURED_NOT_ARGUED: |
  r2.34 says: "T13 ships in the ETL list, so it IS currently exported as a node today."

  **It is not.** `orchestration/n8n/etl_drugbank.json` names exactly five commands — fetch,
  hash-verify, parse, provenance-tests, write. `adjudication-worksheet` is NOT among them.

  The conflated tuple made it node-ELIGIBLE, and no test forced the JSON to carry a node per ETL
  command — `test_t16_has_the_five_nodes_in_order` pins the JSON to its own constant. So the hazard
  was LATENT, waiting for the next regeneration from the conflated list, rather than live.

  I am reporting this for the same reason I report my own: the difference changes urgency, and your
  own instruction — "fix it in the next iteration; it is not an emergency" — matches the LATENT
  reading rather than the live one the clause asserts. **A ruling can be right about a defect and
  wrong about whether it has fired.** Accepting the uncomfortable-sounding version without checking
  is the same failure as accepting the comfortable one, and this session has now had both of us
  overstate something we had not measured.

  Worth saying plainly: the FIX is unchanged either way, and your reasoning for it was correct.

your_framing_that_stands_and_is_better_than_mine: |
  "Never-clobber (defect 22) preserves any non-empty verdict, so a guard written for a DIFFERENT
  purpose was the only thing standing between an automated chain and the human's work. That is
  defence by coincidence, and the accidental save is not a reason to keep the classification."

  That is now written into `NON_NODE_REASONS` for T13, rather than living in a dispatch nobody will
  re-read. The reason a command is excluded is exactly the thing tuple membership cannot carry.

audit_of_what_my_own_change_invalidated: |
  The module docstring claimed `SUBCOMMANDS` "is the single source of truth" for node validation. My
  split falsified that sentence. Updated rather than left standing one screen above the code that
  contradicts it — the rule that has caught the guards package charter three times.

verification:
  suite: "1033 -> 1036 passed / 5 skipped, 0 DESELECTED (delta = the 3 tests added)"
  mutation: "3/3 KILLED, pipeline.py restored byte-for-byte"
  gates: "both exit 0, 761 tracked, run immediately before the push"
  format_lint: "read AFTER the last edit; every removed line in the test diff is my own SUBCOMMANDS -> ETL_SUBCOMMANDS rename, checked because `ruff --fix` once deleted a re-export here"

m0a_unchanged: |
  §18 changes how T13 is CLASSIFIED, not whether it can run. NO WORKSHEET EXISTS and none can until
  the principal writes the T18 roster — 20-40 entries, human-owned, `roster.py` only validates one a
  human wrote. T8 is done. The critical path is blocked on the principal, not on me.

standing: |
  r2.28's property remains AVAILABLE, NOT ENFORCED.

next_handoff: cto — no ruling required. Flagging the severity correction for the record, not for a decision.
