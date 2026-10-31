---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-31T15:44
status: created
priority: normal
subject: "Re: Row 81/82 DONE (a14de3c): 25 of 26 resolve, NOT 23 — Beclomethasone and Budesonide both resolve, so only ONE key needs attention. And a re-key is a SOURCE CONFLICT: none of the 4 PubChem candidates is in the pinned snapshot, while the current key is. Note path inside."
in_reply_to: 835
---

# Re: Row 81/82 DONE (a14de3c): 25 of 26 resolve, NOT 23 — Beclomethasone and Budesonide both resolve, so only ONE key needs attention. And a re-key is a SOURCE CONFLICT: none of the 4 PubChem candidates is in the pinned snapshot, while the current key is. Note path inside.

# Re #835: you were right and my lead was wrong. One consequence for #836 that neither of us had in view.

**Verified independently, 15:50.** PubChem inchikey→cids: Beclomethasone HTTP 200 (1 CID), Budesonide HTTP 200 (1 CID), Ipratropium bromide HTTP 404 on two attempts. **25/26 is the number, and #834's "3" was my measurement error.** I'm recording a correcting row against row 81, and the error is attributed to me, not you. Your multi-CID point is accepted too: "the CID for that exact key" isn't well formed when a key returns several CIDs, and listing all of them is the right shape.

Task B: accepted as reported (comment only, 115 passed in the three adjudication suites, 909 in the full suite).

## The consequence: `a14de3c` is on PR #37's head, so #836 now covers TWO files
`git branch -r --contains a14de3c` → `origin/lung-on-chipsim-stage2`. My #834 never said where the note should live, and rows 83-84 were ruled after you'd pushed. So this is a gap in my instruction, not a rule you broke. Under row 83, **both** `findings-staging/2026-10-30-evidence-assembly.md` **and** `findings-staging/2026-10-31-roster-public-provenance.md` leave the stage2 branch by a new commit and go to `lung-on-chipsim-staging`. The `adjudication.py` comment fix **stays** on stage2. It's code, ratified at row 82, and belongs in #37. Since the head moved, the fresh `/pr-prep` in #836 step 3 is now required regardless.

## The Ipratropium key: going to the principal now, with your evidence as written
I'm putting your framing to them unchanged: the current key IS in the pinned snapshot and the R03 pool, none of the 4 PubChem cation records is in the snapshot, and the difference is only in the stereo layer. That's a conflict between identity systems, not a substitution. You were right not to choose. I'll send the ruling when I have it.
