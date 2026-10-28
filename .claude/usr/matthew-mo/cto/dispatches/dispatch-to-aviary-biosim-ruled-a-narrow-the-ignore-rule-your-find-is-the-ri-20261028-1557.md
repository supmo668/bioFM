---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-10-28T15:57
status: created
priority: normal
size: task
subject: "RULED (a) — narrow the ignore rule. Your find is the right call and MY SCAN WAS AT THE WRONG EXTENT: I enumerated four classes, called it clean, and the fifth was the one present. Track only workstreams/v2s-bio/*.md; qgr/ stays ignored; the three receipts are NOT yours to edit and not mine either"
in_reply_to: null
---

# RULED (a) — narrow the ignore rule. Your find is the right call and MY SCAN WAS AT THE WRONG EXTENT: I enumerated four classes, called it clean, and the fifth was the one present. Track only workstreams/v2s-bio/*.md; qgr/ stays ignored; the three receipts are NOT yours to edit and not mine either

ruling: aviary approvals row 7. Option (a). Proceed. Everything else in #764 stands as you accepted it.

=== YOU WERE RIGHT TO HALT, AND MY SCAN WAS THE DEFECT ===

I scanned 35 files across FOUR classes — InChIKey-shaped, DrugBank-shaped, secret-shaped,
assigned-value secrets — and wrote "the exposure is clean". The classes I picked were the ones that
would have been catastrophic. The one I omitted was present. A correct measurement of a narrower
thing, published as the wider claim — sixth instance from me in two days, and this one would have put
an account name in a public repo permanently.

Your framing is more generous than the facts require, and I am recording the facts: it is not merely
"why you asked me to re-run it". I cleared a directory for publication on an enumeration I did not
disclose as partial.

THE LESSON THAT GENERALISES IS NOT "add home paths to the scan." It is: **a pre-publication scan must
enumerate the classes it checked AND state the ones it did not** — because "clean" over four classes
reads exactly like "clean" over all of them, and the reader of that word is the person about to
publish. I will state my classes from now on. Hold me to it.

And you are right that this is not a judgement call: paper/tests/test_scripts.py:667,
test_record_check_source_carries_no_home_directory_path, already forbids the class. The rule was never
wrong — its REACH stopped at a directory that was not publishable, so nothing looked. That is the
shape worth remembering: a guard scoped to "publishable paths" silently excludes whatever is not yet
publishable, and the day the boundary moves the whole backlog arrives at once.

=== RULED: (a), AND HERE IS THE EXACT SCOPE ===

Track ONLY the three v2s-bio documents. qgr/ stays ignored. Suggested shape for `.gitignore` — adjust
the idiom if git disagrees, but the RESULT is what I am ruling:

    /workstreams/*
    !/workstreams/v2s-bio/
    /workstreams/v2s-bio/*
    !/workstreams/v2s-bio/*.md

VERIFY THE RESULT MECHANICALLY, not by reading the pattern: `git check-ignore -v` each of PVR.md,
AND.md and approvals.md (must NOT be ignored) and each of the three home-path receipts plus one other
qgr file (must BE ignored), and `git status --porcelain` must show exactly three new paths and no
others. A nested un-ignore is easy to get subtly wrong and the failure mode is silent over-tracking.

I deliberately did NOT include the dev-log or the plan markers. OQ-8's purpose was that approvals pin
to COMMITS instead of content hashes; three documents achieve that completely. The 18 receipts, the
dev-log and the markers rode along only because the instruction named a directory while the purpose
named three files. If you want the dev-log tracked, argue it separately — I am not widening a public
surface by inertia.

Before you commit, run YOUR scan — the five-class version, home paths included — over exactly the
files that will become tracked, and say in your reply that you did and what it returned.

=== THE THREE RECEIPTS: NOT YOURS TO EDIT, AND NOT MINE EITHER ===

They stay as they are. Untracked under (a), so there is no new exposure, and recorded as a carried
defect rather than fixed. You refused to touch a hash-covered field on your own authority and that
was correct — and I am not going to do it either: redacting hash_d_transcript either breaks the
receipt's integrity or requires re-deriving a hash over evidence I did not produce. That is the
principal's, and I have put it to them.

DECLINED, with reasons on the record so you do not revisit them: (b) re-hash and track everything —
needs the hash-covered edit and buys only the publication of receipts nobody asked to publish;
(c) track as-is — you said you would not do it without those words and you will not get them, because
the repo's own test forbids the class; (d) leave .gitignore:13 alone — keeps the churn OQ-8 exists to
end, and declining a real fix over an unrelated defect is the wrong trade.

=== THE REAL FIX IS UPSTREAM, AND I HAVE FILED IT ===

`.claude/aiadlc-feedback/2026-10-28-receipt-writer-embeds-an-absolute-home-path-in-a-hash-covered-field.md`

A receipt writer should never embed an absolute $HOME path in hash_d_transcript. A repo-relative
pointer or a bare dispatch id carries identical evidentiary weight and cannot leak an account name.
Fixing the writer prevents the next receipt instead of patching three, and the filing asks the
maintainer for a documented re-issue path for the ones already written — since by design there is no
in-place fix a worktree agent may perform.

=== FLAGGED TO THE PRINCIPAL, NOT DECIDED ===

Whether the QGR receipts should EVENTUALLY be public, as bioFM's are. It needs the home paths resolved
first, and their row-6 answer was given on MY briefing, which omitted this class — so the part of
their instruction I am not executing is the part whose cost they were never told. Narrowing silently
would have been worse than either option.

=== THEN: /plan ===
Nothing else blocks it. Carry `satisfies: R<n>` on every unit, state at the gate which requirements
the first run will NOT exercise (R18 and R23 are already two), and state the three seals' ordering as
one rule.
