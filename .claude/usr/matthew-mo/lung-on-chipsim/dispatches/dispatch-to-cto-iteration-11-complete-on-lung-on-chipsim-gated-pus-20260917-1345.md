---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-17T20:45
status: created
priority: normal
size: task
subject: "Iteration §11 complete on lung-on-chipsim — gated, pushed, four escalations"
in_reply_to: null
---

# Iteration §11 complete on lung-on-chipsim — gated, pushed, four escalations

event: iteration-complete
workstream: lung-on-chipsim
iteration: §11
branch: lung-on-chipsim
commit_hash: 20e9edd
remote_ref: refs/heads/lung-on-chipsim = 20e9edd (was af0fc30); refs/heads/main = df89f503 UNTOUCHED
qgr_receipt: workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-bioFM-qgr-iteration-complete-20260917-1343-1ea4db8.md
hash_a: c810075 (artifact entering review, at 6ae181f)
hash_e: 1ea4db8
diff_base: 309b102
tests: 962 passed / 5 skipped
quality: ruff format --check and ruff check both verified by reading output
guard_preflight: run immediately before push — exit 0, 789 tracked, 0 failing, no accession section
summary: >
  Four-reviewer gate on the E-17/E-18 diff. Found and fixed a TRUE FALSE CLEAN (a link nested below
  the root group made an HDF5 container scan read-and-clean), E6-7 unmet (the shipped command never
  ran the accession half; its exit 0 had been cited upward as compliance evidence by BOTH this agent
  and the CTO), three contract escapes, a report forgery reachable from a structurally valid
  declaration, two unbounded reads, and the thirteenth vacuity — this agent's own shape test.
  owners:[] and the printable-ratio floor recorded as TEST GAPS, not defects. M1 recorded as an
  EQUIVALENT mutant. Merged trunk content disclosed, not claimed.
escalations:
  - index-vs-worktree (r2.28 ruled; proposed as §12, not folded here — was not in the proceed list)
  - error taxonomy: TWO classes not three, plus a leaf guards/errors.py; the rule I wrote about the
    exception belonging with the raising layer is false on the facts (repo 5 raises, record_content 20)
  - module split: fix interior signatures FIRST; policy.py ranks above the three I proposed
  - report grouping: WITHDRAWN by me on the reviewer's evidence
principal_item: test-constant compliance question — measure-first, untouched, not mine to resolve
next_handoff: cto ruling on the four escalations
