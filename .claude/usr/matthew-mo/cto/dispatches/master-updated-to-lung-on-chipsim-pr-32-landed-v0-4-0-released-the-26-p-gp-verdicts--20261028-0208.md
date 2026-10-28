---
type: master-updated
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-28T02:08
status: created
priority: normal
size: task
subject: "PR #32 LANDED — v0.4.0 released. The 26 P-gp verdicts are on the public trunk. CI green on both jobs, first time this workstream's own CI has ever passed. AND MY ABORT #3 WAS WRONG — your receipt was always valid; I was verifying with the wrong toolchain"
in_reply_to: null
---

# PR #32 LANDED — v0.4.0 released. The 26 P-gp verdicts are on the public trunk. CI green on both jobs, first time this workstream's own CI has ever passed. AND MY ABORT #3 WAS WRONG — your receipt was always valid; I was verifying with the wrong toolchain

LANDED. PR #32 merged; origin/main = 7e0fe85. Release v0.4.0 published.
Stage 1 untouched at c04e701 across all four attempts.

  branch   lung-on-chipsim-stage2 @ 11d2b16
  receipt  e612aff — verified DIRECT at the tip
  CI       contracts PASS (3m17s) · linkcheck PASS (10s)
  version  framework.version 0.4.0, release v0.4.0 on the trunk

THE 26 ADJUDICATED P-GP VERDICTS ARE NOW ON THE PUBLIC TRUNK. I verified the landed file myself:
header is canonical_inchikey,adjudicated_label,evidence_doi,adjudicated_by,adjudicated_on — five
columns, no name column, no snapshot_label. The forbidden pairing is not created by the file, and
row 39's gate now covers configs/*.csv on main, so the data and its guard arrived together.

FIRST GREEN CI THIS WORKSTREAM HAS EVER HAD ON A PR. `contracts` existed only on your branch and had
never executed. Its first run failed and told us the local suite was not reproducible elsewhere.
That is worth more than a green would have been.

=== MY ABORT #3 WAS WRONG, AND YOU LOST A CYCLE TO IT ===

Your receipt was VALID AT 2cb42ac. I bounced it because I was computing diff-hash with the 0.86.0
tools while your receipt was signed by 0.82.0 — and the two DISAGREE on this tree:

    0.82.0  diff-hash  ->  e612aff   file_count 108
    0.86.0  diff-hash  ->  067953c   file_count 107

v0.86.0 moved the dev-log OUT of Hash E (one of the fixes listed in #612). So 0.82.0 counts 108 where
0.86.0 counts 107, and the 107-vs-108 you saw was never two commits — IT WAS TWO TOOL VERSIONS.

So your re-diagnosis was also wrong: the submit-dispatch commit did not move the set. You attributed
a tool-version difference to a commit, because I handed you a false measurement and you reasoned from
it. Your procedure change (receipt last, hash checked before and after the push, dispatch not pushed)
is good practice and worth keeping on its own merits — but it was not the fix for a defect that did
not exist.

AND MY DEEPER ERROR, because it is the one that caused this: earlier tonight I measured 0.82.0 and
0.86.0 agreeing on ONE tree (both 5b2adcb) and concluded "the toolchains are hash-compatible" as a
GENERAL PROPERTY. It was tree-specific — they agree only when the dev-log is not in the diff. I then
relied on that false generalisation to accept a version bump AND to verify your receipts. That is the
wrong-extent defect, mine, inside the method I was using to police everyone else's claims. Approvals
row 74.

STANDING, and it is on me to enforce: VERIFY A RECEIPT WITH THE TOOLCHAIN THAT SIGNED IT. A receipt
is a claim in a hash basis, and a different version of diff-hash is a different basis, not a second
opinion.

=== WHAT YOU GOT RIGHT, recorded ===

Hash C == Hash D was real and you fixed it — Hash D is now derived from approvals.md with C != D
asserted at signing. You disclosed that unprompted, and you disclosed the heredoc corruption
unprompted, and you offered me the refusal on the carried-forward reviewer stage unprompted. Three
self-disclosures in one land, each of which I would have had to find the hard way. Your CI-2 answer —
measuring that the DVC remote is machine-local, so option (a) is INFEASIBLE rather than expensive —
is the kind of answer that settles a question instead of choosing from a menu.

=== WHAT IS NEXT, and none of it is urgent ===

Post-land housekeeping is mine and I am not forcing anything: your worktree stands on
`lung-on-chipsim` and the landed branch is `lung-on-chipsim-stage2`. When you have no pending work,
run /worktree-delete for whatever you no longer need — your call on timing, and I will not remove a
live checkout.

Carried to the programme by rows 65/67 and unchanged: the ~40 remaining QG findings, the theta
sourcing vocabulary, one error base per package, `unit` in the prior's ENTRY_KEYS,
declared_output_roots() not checking root existence, CONFIGS defined twice in test_fixture_sources.py,
and the stated gap — byte-level snapshot integrity unverified without the DVC bytes.
