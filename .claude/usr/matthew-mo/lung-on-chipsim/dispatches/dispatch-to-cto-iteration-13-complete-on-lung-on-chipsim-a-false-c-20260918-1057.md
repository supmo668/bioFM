---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-18T17:57
status: created
priority: normal
size: task
subject: "Iteration 13 complete on lung-on-chipsim - a false clean in my own blob reader, reproduced and closed"
in_reply_to: null
---

# Iteration 13 complete on lung-on-chipsim - a false clean in my own blob reader, reproduced and closed

event: iteration-complete
workstream: lung-on-chipsim
iteration: "§13"
branch: lung-on-chipsim
commit_hash: 151a554
qgr_receipt: workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-bioFM-qgr-iteration-complete-20260918-1055-b0a20cb.md
hashes: "A 74cbc26 -> E b0a20cb, base 514ff17, 5 files, --project bioFM"
remote_refs_observed:
  origin/lung-on-chipsim: 151a55420b72048372884e08dd5cd55d99375a09
  origin/main: df89f5039be4449aa3f7246ee496b28edb708cfe (untouched)

summary: |
  §13 implemented r2.32 — the staged gate now reads BLOB BYTES via `cat-file --batch` instead of
  `checkout-index`, which applied eol/filter conversions and so read the working-tree RENDERING of
  the index rather than the bytes a commit carries. That part landed in 7f19667 / 0d3b8f8.

  THE GATE THEN FOUND A FALSE CLEAN IN MY REPLACEMENT, and it is the kind this whole guard exists
  to prevent. Two tracked paths differing only in case are ONE FILE on APFS, which is where this
  gate runs. The second blob written discarded the first, the scan read the survivor twice, and the
  record in the discarded blob was never seen. Reproduced against the shipped function before I
  accepted it from either reviewer:

      Data.csv (carrying a synthetic DB9-range record) + data.csv (decoy)
        -> ONE file in the staged tree, holding the decoy
        -> written == 2 of 2, constraint-4 check PASSED, gate exit 0

  The counter I wrote for exactly this passed because it counted WRITES, and an overwrite is a
  successful write. It now counts the files the FILESYSTEM reports — something the loop did not
  produce, so it can disagree. The refusal itself asks `exists()` rather than comparing names,
  because the filesystem's own equivalence is what folds them together; that covers NFC/NFD pairs
  without this code having to enumerate which volumes fold what.

  Reachable from committed content alone: a contributor on Linux commits both spellings. Latent
  today — no colliding pair among the 796 tracked paths — which is the same status the eol=crlf
  finding had when you constructed it for me.

decisions_i_made_that_you_may_want_to_overturn:
  - E-10's ownership predicate is now FATAL IN STAGED MODE regardless of owner. A listed path with
    no materialised blob cannot arise legitimately under the new reader, so "another project owns
    it, mark it listed" was an escape hatch for a state that is always a scan defect. Both reviews
    demonstrated the route (the listing and the materialisation are two `ls-files` calls an instant
    apart). I did NOT thread the enumeration through instead: `_tracked_listing` is monkeypatched
    with a one-arg lambda in ~40 tests, so that refactor churns all of them while closing only the
    race. The structural change is carried, not done.
  - `--no-replace-objects` was added to the SHARED argv, so it now applies to every git call in the
    module, not only the reader. `refs/replace/*` substitutes content under the REQUESTED oid and
    the response header echoes it, so headers cannot see it; every payload is also hashed against
    the oid it was requested under. Two locks, mutation-tested independently.

two_findings_that_are_mine_not_the_reviewers:
  - Moving the write to `target.open("wb")` removed this project's MOST RECORD-BEARING WRITER from
    the record-bearing writer registry. The detector matched a bare `open(..., "w")` as an
    `ast.Name` call only, so `Path.open` was invisible. The writer left the registry silently — not
    by being new, which is the case that list was built for, but by changing HOW it writes. The
    only reason anything went red is that the entry left behind became a phantom.
  - My first fix for that STILL saw zero writers: `open(p,"w")` carries the mode at args[1] and
    `p.open("wb")` at args[0], and I checked args[1:] in both. An edit computed against one shape
    and applied to another, inside the fix for an edit computed against one shape and applied to
    another. Widening it properly then exposed `drugbank_snapshot._download` — PRE-EXISTING,
    undeclared since it was written, streaming the raw tables to disk through the same spelling.

what_this_receipt_does_not_claim: |
  r2.28's property is AVAILABLE, NOT ENFORCED. No CI job and no hook invokes `record-content-gate`.
  Your ruling was: install nothing, say exactly that, and carry hook/CI activation to the
  principal. Saying it again here because this section's worst finding was a ruling implemented as
  a mechanism nothing invoked, so a receipt that blurred the line would repeat that defect one
  level up.

  The reviewers also ran NO test suite — the correctness reviewer states this outright and reports
  no baseline or deselection count. Every number below is mine.

the_two_things_you_said_you_would_check:
  - The symlink special case is GONE for staged mode (the blob is ordinary content; a test asserts
    the staged copy is not a symlink and that the record in the target string is still found). It
    is measured still load-bearing for WORKTREE mode, where removing it reported a dangling link as
    unreadable for a wrong reason. Reported as a deviation rather than half-performed.
  - The unmerged refusal still fires in BOTH modes after the reader change. Verified. One
    production call site, and `_tracked_entries` is the reader's first statement, so there is no
    path to the bytes that bypasses it.

verification:
  suite: "baseline 1004 passed / 5 skipped -> 1010 passed / 5 skipped, 0 DESELECTED (delta = the 6 tests added)"
  mutation: "6/6 killed, module restored byte-for-byte. Honest qualifier: five died by assertion, one (truncated stream) by NON-TERMINATION — without the guard the loop spins forever, so the harness sees a hang. Reported as a hang, not dressed up as a clean kill."
  memory: "94.7 MiB -> 1.2 MiB peak on the real repo, measured. Constant bound, not the largest tracked file."
  gates: "record-content-gate (STAGED) exit 0 and record-content-report (WORKTREE) exit 0, 796 tracked, BOTH run immediately before the push, not recalled."
  format_lint: "read AFTER the last edit"

carried:
  - the temp tree holds every tracked blob and survives SIGKILL (registered, needs a ruling on where such a tree may live)
  - one enumeration threaded through both the listing and the materialisation (structural)
  - THIS_PROJECT resolving from the import location; ContentPolicy holding two of seven policy decisions; one path printing two owners; _MINIMUM_PLAUSIBLE_TRACKED and the toplevel check unpinned

next_handoff: cto review §13 boundary; rule on the temp-tree residual and on whether the staged-mode fatal predicate should be written into the plan
