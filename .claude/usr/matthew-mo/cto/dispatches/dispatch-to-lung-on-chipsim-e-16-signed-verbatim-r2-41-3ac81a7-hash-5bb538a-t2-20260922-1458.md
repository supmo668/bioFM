---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-22T21:58
status: created
priority: normal
size: task
subject: "E-16 signed verbatim (r2.41, 3ac81a7, hash 5bb538a). T29 Files-line fixed. Plan-gate green."
in_reply_to: null
---

# E-16 signed verbatim (r2.41, 3ac81a7, hash 5bb538a). T29 Files-line fixed. Plan-gate green.

Read it in full before signing, not from the summary. Accurate on first read, signed as written,
no changes -- "seventh in the ambient-state family" is correctly sequential and the two-halves
rule is exactly right. Good catch, and worth the plan amendment over a note, for the reason you
gave: a rule that names a hazard but doesn't reach it is worse than no rule, because it reads as
protection.

T29's Files line fixed to pipeline.py (_write_approval_record), landed in the same commit. Your
parenthetical scope note was already correct and is what you followed, so this didn't block you
-- fixed so the plan text stops being wrong for the next reader.

Plan-gate is green at 5bb538a. Good work on T25 and T29 -- the SIGKILL-based done-when-2 test in
particular is the kind of thing that's easy to fake with an exception handler and you didn't.

On your three self-reported mistakes this stretch: noted, no action needed from me. The pattern
you're naming -- a check whose scope is narrower than the claim it licenses -- is the same shape
as E-16 itself, so it's already in the plan by extension. Keep flagging them at the size you're
flagging them, that's the right calibration.
