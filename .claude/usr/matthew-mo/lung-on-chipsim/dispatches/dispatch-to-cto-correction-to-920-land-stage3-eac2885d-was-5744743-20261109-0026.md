---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-11-09T00:26
status: created
priority: normal
size: task
subject: "Correction to #920: land stage3 @ eac2885d (was 5744743d) — context-only commit, diff-hash unchanged at 3e56ccd"
in_reply_to: null
---

# Correction to #920: land stage3 @ eac2885d (was 5744743d) — context-only commit, diff-hash unchanged at 3e56ccd

Correction to #920's landing SHA. Small, but it is a SHA you were told to land, so it gets its own
message rather than a silent push.

LAND origin/lung-on-chipsim-stage3 = eac2885d, NOT 5744743d.

#920 named 5744743d. After sending it, the context-commit Stop-hook required the pr-submit dispatch
payload itself to be committed, which produced one more commit, and I pushed it so remote equals
local (precondition 4's actual property).

WHY THE RECEIPT STILL STANDS, measured rather than assumed:
- eac2885d touches exactly ONE file:
  .claude/usr/matthew-mo/lung-on-chipsim/dispatches/pr-submit-to-cto-...-20261109-0019.md
- diff-hash --base origin/main at eac2885d = 3e56ccd, file_count 14 — BYTE-IDENTICAL to the
  receipt's Hash E. diff-hash excludes the dispatch tree, so a context-only commit cannot move it.
- receipt-verify (plain) exits 0 at this HEAD.
- git merge-base --is-ancestor HEAD origin/lung-on-chipsim-stage3 -> TRUE;
  origin/lung-on-chipsim-stage3 = eac2885d = local HEAD.
- origin/lung-on-chipsim = c04e7019, still untouched. Do not land that one.

Everything else in #920 is unchanged: same 17/17 findings, same scope, draft: false, no migrations,
and precondition 4 still tool-blocked on the branch-name defect for the reason given there.

I am flagging this because "the SHA moved after I told you the SHA" is exactly the shape that makes
a landing step act on a stale ref, and because `git-push`'s ✓ cannot be used to tell whether it
moved. Verify with ancestry.

next_handoff: biofm/matthew-mo/cto
