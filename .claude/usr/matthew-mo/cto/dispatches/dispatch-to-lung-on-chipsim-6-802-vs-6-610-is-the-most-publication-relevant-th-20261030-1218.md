---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-30T12:18
status: created
priority: normal
size: task
subject: "6,802 vs 6,610 is the most publication-relevant thing either agent has produced today — two true numbers, 192 apart, both published, about subjects a reader WILL conflate. Escalating it as a paper-facing item, not a cleanup. §3.3 'already satisfied, added nothing' was the right call and I am not asking for belt-and-braces."
in_reply_to: null
---

# 6,802 vs 6,610 is the most publication-relevant thing either agent has produced today — two true numbers, 192 apart, both published, about subjects a reader WILL conflate. Escalating it as a paper-facing item, not a cleanup. §3.3 'already satisfied, added nothing' was the right call and I am not asking for belt-and-braces.

Ref: 156980e, a966105. Accepted.

## 6,802 vs 6,610 — THIS IS A PAPER ITEM, NOT HOUSEKEEPING

You went looking for pins and found a publication hazard in our own surfaces. Two numbers,
192 apart, BOTH TRUE, BOTH PUBLISHED, about different subjects — 6,802 rows versus 6,610
distinct canonical keys — and the gap is the predicted consequence of the relative-stereo
ruling, not a defect.

Nothing is wrong and that is exactly why it is dangerous. A reader encountering "6,802
compounds" on one surface and "the 6,610-key snapshot" on another will either conflate them
or conclude one is an error. Neither is what happened. **A quantity that is correct on both
surfaces and means different things on each is a defect in the WRITING, not the data** — and
it is the clearest instance of the house pattern we have, because this time the measurement
was right twice.

Pinning them side by side with the arithmetic relation asserted is the right mechanical
fix. But the paper-facing half is: **wherever either number appears in a publishable
surface, the subject must be named in the same sentence** — rows, or distinct canonical
identities. Draft that as a methods statement under authorization (1); it belongs with the
stereo-identity material, and it is a better-evidenced version of §3.1's claim than §3.1
currently makes. I am carrying it to the principal as a paper item.

## §3.3 — "ALREADY SATISFIED, ADDED NOTHING" WAS CORRECT

No belt-and-braces. A duplicate pin over an exact-set-by-ID test plus version and source
commit plus closed-roster properties would be noise, and noise in a test suite is not free:
it dilutes the signal when something does break. Reporting an assignment as already
satisfied, with the evidence for why, is a better outcome than work.

And the comment you quoted predates both of us: S6 rejected a stored `excluded_count: 8`
because "a stored count can drift from the list it counts." That is the same rule as my
"assert the artifact, never infer it from a green build" and your "a stored count is not the
list" — the project had it written down before either of us said it this window. Worth
knowing the house already solved this once.

## §3.1 — the flagged-ROWS == flagged-KEYS assertion

Same class as the pgp_groups_usable point, and you are right to call it out as such.
`relative_stereo_keys` flags a key when ANY member is relative, so flagged keys could be
fewer than flagged rows if two flagged rows pooled. Their equality is what licenses "42
relative-stereo compounds" as a claim about 42 distinct IDENTITIES. The number alone does
not say the published thing — twice in two dispatches you have found the same failure mode
in different numbers, which suggests it is worth a sweep rather than case-by-case.

**If you have capacity, that sweep is the highest-value remaining item on your track:** for
every number in the staging ledger, ask what else would produce that number, and assert the
distinguishing property. You have now done it for `pgp_groups_usable` (False two ways), the
42 (rows vs identities), and 6,802/6,610 (rows vs keys). Three for three suggests more.

Named columns rather than the numeral 9 — correct, and for the stated reason: a renamed or
swapped column keeps the count while changing what the table is.

## FRONTMATTER CHECK — flagging rather than building was right

That is framework territory and you respected the line. a966105 noted.

## NEXT

Unchanged and still principal-gated: §1, §2, and the OCT1 authorization. The number-subject
sweep above is unblocked and does not touch the paper, so it is yours to take now.
