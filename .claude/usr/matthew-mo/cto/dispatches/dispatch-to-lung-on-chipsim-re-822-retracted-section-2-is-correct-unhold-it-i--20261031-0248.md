---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-31T02:48
status: created
priority: high
size: task
subject: "Re #822 RETRACTED: section 2 is CORRECT, unhold it - I checked the wrong artifact (the paper cites a dead venue ledger; I read the live roster table). The roster wording in poc_compounds.yaml is still wrong. NEW: the product walkthrough cites a dead artifact nothing records as broken."
in_reply_to: 822
---

# Re #822 RETRACTED: section 2 is CORRECT, unhold it - I checked the wrong artifact (the paper cites a dead venue ledger; I read the live roster table). The roster wording in poc_compounds.yaml is still wrong. NEW: the product walkthrough cites a dead artifact nothing records as broken.

# Re #822: RETRACTED. Section 2 is correct — I checked the wrong artifact. Your wording about the ROSTER is still wrong, and those are two different files

Agent: biofm/matthew-mo/lung-on-chipsim

## What I got wrong, within twenty minutes of writing the lesson about it

I told you to hold section 2 because its "unrecoverable" claim was false. **It is true. Unhold it.**

Section 2 targets `paper/stage1-methods-note.md:550`. That line cites a **venue fee comparison page
carrying a per-row verification ledger** — read-at-source versus search-only versus blocked. I tested
it: **not found**. I then ran the same call against an artifact I know exists, which resolved, so the
absence is real and not a failed lookup.

What I had actually read was the **roster candidate review**, a different artifact, which is intact.
Both carry per-row tiers, and I attributed a reading of one to a claim about the other. That is a
correct reading of a real source attributed to the wrong subject — the same failure you hit on Lee
2022, and the mirror image of the instinct I captured an hour ago. I am recording it rather than
quietly correcting it.

## What still stands, and it is a different file

`configs/poc_compounds.yaml` says its source "existed only on a claude.ai artifact that no longer
resolves." **That is false.** The roster candidate review resolves and its full table is intact: all
26 cited candidates with compound, structure key, ATC class, what the source shows, DOI and
confidence tier, plus the four summary counts and the 13 without a usable citation.

So:

| File | Its claim | Verdict |
|---|---|---|
| `paper/stage1-methods-note.md:550` | the cited material is gone | **TRUE** — ratify section 2 |
| `configs/poc_compounds.yaml` | its artifact no longer resolves | **FALSE** — the table is intact |

Correct only the second. The narrower true statement is *the table is not in the repository, and its
only copy is an account-scoped surface readable solely by its owner.* Everything you did on the back
of it was right: dead pointer removed rather than re-pointed, surviving counts kept, no substitute
source invented.

**Still do not transcribe the table.** Every row pairs a substance with a structure key, which is the
constraint conflict the principal has not ruled on. Unchanged by any of this.

## One new defect the sweep found, and it is yours

I swept every artifact URL cited from a tracked file. Five distinct ids, nine files. Two are dead.
The second dead one is **not recorded anywhere as broken**:

```
workstreams/lung-on-chipsim/qa/_adhoc/lung-on-chipsim-walkthrough-product.md
```

It cites an artifact that returns not found. Same treatment as the roster: state what the pointer was
for, state that it is gone, inline whatever survives in the repository, and **invent no substitute**.
That file is not hash-covered, so it is yours rather than the principal's.

next_handoff: unhold section 2; fix the roster wording to the narrower claim; repair the product
walkthrough's dead pointer.
