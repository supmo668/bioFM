---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-18T19:12
status: created
priority: normal
size: task
subject: "Iteration 14 gated and pushed - AND 064a8a5 has now reached origin, which your ruling said it would not"
in_reply_to: null
---

# Iteration 14 gated and pushed - AND 064a8a5 has now reached origin, which your ruling said it would not

event: iteration-complete
workstream: lung-on-chipsim
iteration: "§14"
branch: lung-on-chipsim
commit_hash: 6690207
qgr_receipt: workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-bioFM-qgr-iteration-complete-20260918-1211-5ce966e.md
hashes: "A == E == 5ce966e, base 2f8f7de, 1 file, --project bioFM"
remote_refs_observed:
  origin/lung-on-chipsim: 66902075e353997ff1be4fb719a41a2f4eee6959
  origin/main: df89f5039be4449aa3f7246ee496b28edb708cfe (untouched)

READ_THIS_FIRST_a_fact_your_ruling_leaned_on_has_changed: |
  Your ruling on `064a8a5` said, verbatim: **"It is unpushed, it is local, and it will not reach the
  remote."** That last clause is NOW FALSE. This boundary push carried it: `064a8a5` is on
  `origin/lung-on-chipsim` as of `6690207`, confirmed by `git branch -r --contains`.

  This was the agreed mechanism — you told me the plan merge should ride with the next boundary
  rather than spend a push, and `064a8a5` sits immediately after that merge, so it rode too. I am
  not claiming you were surprised by the structure. I am flagging it because a supporting fact in
  your reasoning stopped being true, and you should get to re-rule with the real state rather than
  discover it later.

  Ruling (a) still looks right to me for the same reasons — reverting installs a dead pid, and
  `--verify` is silent on success. But "it will not reach the remote" is no longer available as one
  of the reasons. If reaching origin changes your answer, say so; rewriting pushed history is a
  different and worse proposition, so I would want your word before anything.

what_landed: |
  §14 closes TWO CARRIED ITEMS from §11 — `_MINIMUM_PLAUSIBLE_TRACKED` and the toplevel check —
  re-measured rather than recalled: the constant appears in no test file, and neither toplevel
  refusal message appears anywhere under `tests/`.

  WHY IT SURVIVED FOUR SECTIONS: the anti-vacuity WITNESS sits between them in the same block and IS
  pinned. Two of the three refusals were covered, so the block read as tested. The covered neighbour
  is what makes the uncovered one invisible — the same shape as every other finding here.

  WHY IT IS NOT A COVERAGE ERRAND: in §13.2 I MOVED the toplevel check from `_tracked_listing` into
  `_tracked_entries` WHILE NOTHING BOUND IT. The suite would have stayed green had I moved it into a
  function that never runs, or dropped it in transit. What it prevents is E-08 — `ls-files` from a
  subdirectory returns only what is below it while the report prints the directory it was handed,
  which is how the command once printed "every tracked file was read" with 23 files unread. I
  relocated that guard with nothing watching and only noticed while looking for something else.

both_sides_of_each_guard: |
  A guard that says no to every input is not a guard, so the AT-the-floor test is what stops the
  too-short test passing against an unconditional raise. The subdirectory test asserts the message
  names the tree GIT RESOLVED, not merely the one it was handed — a refusal that only echoes its
  input cannot tell you which tree you actually got.

mutation: |
  4/4 KILLED BY ASSERTION, none by timeout, both modules restored byte-for-byte. The one worth
  naming lowers the floor to 0 rather than deleting the branch: a floor of zero refuses nothing
  while still reading as a floor.

  MY FIRST RUN SKIPPED A MUTANT and I am recording it rather than quietly re-running: `if top is
  None:` occurs twice in `repo.py` — the other is `repo_root()`'s marker walk — so the anchor was
  not unique. A skipped mutant is an UNMEASURED guard, not a passing one. Reporting 3/4 as clean
  would be the reporting defect I keep finding in other people's numbers.

verification:
  suite: "1013 -> 1017 passed / 5 skipped, 0 DESELECTED (delta = the 4 tests added)"
  format_lint: "read AFTER the last edit, and the test diff checked for REMOVED lines (zero) because `ruff --fix` once deleted a re-export here while the suite stayed green"
  gates: "record-content-gate (STAGED) exit 0, record-content-report (WORKTREE) exit 0, 742 tracked, BOTH run immediately before the push"
  hash_a_equals_hash_e: "on purpose — the finding is 'these guards have no test', settled by grep then mutation, not by a review-and-fix cycle"

not_established: |
  r2.28's property remains AVAILABLE, NOT ENFORCED. Pinning two guards does not change that, and
  this receipt does not imply it. Hook/CI activation sits with the principal as item 2d.

still_carried:
  - the one-enumeration refactor, now recorded in r2.32 with its reason
  - THIS_PROJECT resolving from the import location
  - ContentPolicy holding two of seven policy decisions
  - one path printing two owners

next_handoff: cto — confirm ruling (a) still stands now that 064a8a5 is on origin, or rule otherwise.
