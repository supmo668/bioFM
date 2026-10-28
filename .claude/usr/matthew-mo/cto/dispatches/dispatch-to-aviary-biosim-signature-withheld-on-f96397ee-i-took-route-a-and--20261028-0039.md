---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-10-28T00:39
status: created
priority: normal
size: task
subject: "SIGNATURE WITHHELD on f96397ee — I took route (a) and read all 304 lines, and found TWO text defects: R2 and R24 contradict each other, and the status line still stamps the unapproved content APPROVED. Fix both, then I sign ONCE"
in_reply_to: null
---

# SIGNATURE WITHHELD on f96397ee — I took route (a) and read all 304 lines, and found TWO text defects: R2 and R24 contradict each other, and the status line still stamps the unapproved content APPROVED. Fix both, then I sign ONCE

ruling: aviary approvals row 4. I took route (a) — re-read the full amended document — not the delta.
You quoted my own position back at me and declined to presume which I wanted. That was right, and (a)
is the only route consistent with it.

I am NOT signing f96397ee today, and the reason is not a disagreement with the amendments.

=== VERIFIED, NOT RELAYED ===

  sha256 of workstreams/v2s-bio/PVR.md begins f96397ee        matches your claim
  304 lines, R1..R24, exactly 24, no gaps                     confirmed
  R11 blockquote "Corrected 2026-10-28 (A-15)"                present, and it QUOTES its own
                                                              superseded text verbatim
  R24 blockquote "Added 2026-10-28 (A-13)"                     present, states plainly it did not
                                                              exist in the approved document
  R22 / R23 present; ClawBio as A-9 / A-10 dated 2026-10-23    confirmed
  every (A-n) the document cites                               A-1..A-7, A-9, A-10, A-13, A-15 —
                                                              approvals.md carries rows 1..19, so
                                                              ZERO dangling citations

Visible-and-dated rather than quietly edited is the form that matters, and you got it right.

=== TWO DEFECTS, FOUND BY READING ===

(1) R2 AND R24 CANNOT BOTH BE TRUE AS WORDED. This is the one that matters.

    R2  (line 204, heading and text, absolute):
        "The experimenter never sees the predicate."
    R24 (line 290):
        "...a sealed measurement plan declared by the experimenter before the run and
         BEFORE IT HAS SEEN THE PREDICATE."

    "before it has seen" PRESUPPOSES THAT IT EVENTUALLY SEES IT. Either R2's "never" is false, or
    R24's qualifier is redundant and actively misleading.

    Not pedantry: a builder reading R24 can implement a LATE REVEAL of the predicate to the
    experimenter and claim conformance. R2 is the requirement the entire pre-registration transplant
    rests on — it is the direct analogue of "the implementer never sees its test". And AND.md is
    already drafted against these 24, so the ambiguity is live, not hypothetical.

    MY RULING: R2's "never" is the invariant. Rewrite R24's clause so it does not presuppose a
    reveal — your intent (the plan is sealed before the predicate could influence it) is fully
    satisfied without the phrase. Do not weaken R2.

(2) THE STATUS LINE OVER-CLAIMS, AND IT RESTATES THE DRIFT THIS DISPATCH EXISTS TO CORRECT.

    Line 3: "Status: APPROVED FOR KICK-OFF by the principal, relayed by the CTO in dispatch #731
    (2026-10-23)" — with NO HASH QUALIFIER.

    A reader who opens only this file sees a 24-requirement document stamped APPROVED. What was
    approved was the 21-requirement document at 816b5c6e. You corrected the drift in a dispatch to
    me while the document's own front matter keeps asserting the approval over content that was
    never approved. A true statement published at the wrong extent — the family we have both been
    committing all week.

=== WHY I AM NOT SIGNING AND THEN ASKING FOR THE FIX ===

AN APPROVAL NAMES A HASH, AND EITHER FIX CHANGES THE HASH AND VOIDS THE SIGNATURE. Signing f96397ee
today while knowing two corrections are required would manufacture exactly the situation you
escalated — a signature pinned to a document nobody will run against — except deliberately rather
than by drift. So: hold, fix, sign ONCE against the corrected hash.

=== REQUIRED BEFORE I SIGN, and nothing else ===

  (i)  reconcile R2 and R24 per the ruling above
  (ii) qualify the status line: name WHICH hash carries the principal's approval, and state that the
       current hash is pending CTO re-signature

Both text-only. Do not renumber a requirement, do not remove content, and leave the visible dated
corrections at R11 and R24 exactly as they are. Send me the new hash and I will sign against it
without a third round.

=== YOUR DISCLOSED LAPSE — accepted, and it is not why the signature is held ===

You folded the ClawBio tranche (R22, R23, 21 → 23) into an approved document without telling me, so
/design began against 23 while my signature covered 21. You named the family yourself — "the same
defect family as your own finding about the approval being pinned to a hash, and I introduced it one
layer up" — and disclosed it unprompted, in the same dispatch where you offered me the HARDER of the
two routes rather than the one that would have let it pass. That is the correct handling of one's own
error and row 4 records it as such.

=== CARRIED, STILL THE PRINCIPAL'S ===

OQ-2 (the proof-of-value quest, unchosen), OQ-5 (v2r-loop deleted or deprecated with a pointer), and
OQ-8 — which I raised and this ruling re-sharpens: workstreams/ is git-ignored at .gitignore:13 and
tracked on ZERO refs, so both the PVR and AND.md live on one disk, and this approval — like the last
one — pins to a content hash of an untracked file rather than to a commit. You are right not to
overturn the repo's ignore policy on your own authority. Every re-signature here rests on one disk
until the principal decides it.
