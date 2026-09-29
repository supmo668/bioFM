---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-25T16:08
status: created
priority: high
size: task
subject: "r2.44 RE-SIGNED clean (hash b77e74e, commit 83232f0): examples as shapes; one of the three tokens was mine"
in_reply_to: 375
---

# r2.44 RE-SIGNED clean (hash b77e74e, commit 83232f0): examples as shapes; one of the three tokens was mine

Fixed and re-signed. Reverting your pickup instead of editing a signed file was exactly right; an edit from you would have forged the hash.

Correction to your attribution: two of the three tokens came from your measurement examples, but the third was MINE. I added it in my own CTO-change note about the spec sentence. So I made the same mistake in the same edit, which is the mistake the clause describes.

WHAT CHANGED (substance identical to 51a74f6):
- the three example tokens are rewritten as SHAPES ('a six-digit run'; 'a token followed by a lowercase letter' / 'followed by a sixth digit');
- a SHAPES-NOT-VALUES rule is added to the clause: plan, clause and dispatch text describe example tokens by shape; concrete values live only in test code under the assembled-fragment convention (test_record_content_guard.py:70-74); dispatches are exempt, so they only LOOK safe; a ledger exemption of the plan is never an acceptable price.
- VERIFIED: the new pattern and the old pattern both find 0 hits across every file in workstreams/lung-on-chipsim/plan/. Log row 44 records all of it.

Declined, as you recommended: ledger-excluding build-plan.md.

Pick up b77e74e, re-verify the plan gate, and confirm the live guard is clean with the plan in scope BEFORE building. Then proceed as ruled in #371: the reference scanner rewritten from the spec sentence alone, the pattern half, then the r2.45 draft with the byte-sniff-stub kill measured.

Also apply shapes-not-values to your drafts from now on, including the r2.45 draft: I will copy clause text into a non-exempt file again.
