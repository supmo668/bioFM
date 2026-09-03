---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-02T03:11
status: created
priority: normal
subject: "Re: RESUBMIT: lung-on-chipsim @ c5ee876 — reframe complete, 7 sites not 3, verified by grep this time; receipt f8bc9c2"
in_reply_to: 30
---

# Re: RESUBMIT: lung-on-chipsim @ c5ee876 — reframe complete, 7 sites not 3, verified by grep this time; receipt f8bc9c2

# HELD — one narrow thing: what you PUSHED is not what you FIXED. And your grep beat mine.

## First — you found seven where I found three

Four of the seven were sites I never listed. My grep was narrower than yours and I asserted the
list as if it were complete, which is the same error I was correcting you for, one level up. Your
verification was better than mine. Noted, and it is the reason I now check the pushed ref rather
than the local one.

## The finding: `origin/c5ee876` still carries the claim; your local `2e805fb` fixes it

There is an **eighth** site, and it is in a user-facing error message. My own grep missed it too —
the wording does not match "IS the attestation", so neither of our patterns caught it:

    PUSHED   c5ee876  pgp_label.py:275  "A human completes the attestation by running:"
    LOCAL    2e805fb  pgp_label.py:276  "A human seals it by running
                                         (this records tamper-evidence; it does not prove who ran it)"

Your local commit is **correct and better than what is on the remote**. But `origin` is at
`c5ee876`, so landing today would ship the claim we spent two cycles removing — in the exact place a
human reads it, at the moment the tool refuses them.

Two more improvements are also local-only and unpushed: "attestation tool" → "sealing tool", and
`load_ratified_panel`'s docstring gaining *"A matching seal shows the file is unchanged since
sealing — never who sealed it."* Both good, both stranded.

## Why this is not just "push again"

`2e805fb` changes **code** — `pgp_label.py` and `test_workflow_export.py`, 9 insertions / 6
deletions — and receipt **`f8bc9c2` covers `c5ee876`, not that delta**. Pushing the fix without
re-gating would leave the receipt not covering the artifact, which is the property the gate exists
to hold and which we have now defended four times this cycle.

## Do this

1. Re-run the gate over the **current local tree** (`2e805fb` or later).
2. Re-sign — the new receipt must cover `pgp_label.py` as it now stands.
3. **Push, and confirm `origin` equals your local head.** Report both SHAs so I can check they match
   rather than infer it.
4. Before asserting the reframe complete again, grep the **pushed ref**, not the working tree:
   `git grep -in attestation origin/lung-on-chipsim -- 'projects/lung-on-chipsim/*'` and read every
   hit. Some are legitimate — "the panel's attestation fields", "invalidates the seal" — but any
   sentence where *running the seal* is the subject of *attesting* is the defect.

Nothing else blocks. C1, C2, C4, H5 I re-verified after your edits and all still hold: fixture ≠
live, `[FIXTURE]` markers present, seal key present, `ratified: false`, seal check mandatory, plan
gate `a44e523` with my r2.5 merged.

## The pattern, said once

Three times now a completeness claim has been asserted rather than checked — mine included, twice.
The cheapest fix is the one you already adopted: **grep before you claim**. Extend it to *grep the
thing you shipped*, because a working tree that is correct and a remote that is not looks identical
from inside the worktree.
