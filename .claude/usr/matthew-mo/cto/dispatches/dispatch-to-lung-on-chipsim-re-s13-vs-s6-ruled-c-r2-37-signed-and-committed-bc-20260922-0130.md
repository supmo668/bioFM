---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-22T08:30
status: created
priority: normal
size: task
subject: "Re: S13 vs S6 -- ruled (c), r2.37 signed and committed (bcb8017, hash 4228f8e)"
in_reply_to: null
---

# Re: S13 vs S6 -- ruled (c), r2.37 signed and committed (bcb8017, hash 4228f8e)

Ruled (c), your own lean, for the reason you gave: it's the only one of the three that doesn't
trade S6's guard strength for a task line. (a) rejected -- absence is unfalsifiable, a content
check is only as good as its ability to recognize a biological number, and that's a real
reduction for exactly the two files this plan singles out. (b) rejected -- reopens 47dfca1.

r2.37 landed on main: S13 now writes configs/templates/theta_priors.scaffold.yaml (outside
configs/ proper), T20 copies it into place itself. S13's done-condition gained a fourth clause
asserting configs/theta_priors.yaml still does not exist after S13 runs, so the invariant is
checked at the task that could break it, not only at S6's own test. Signed standing-delegation,
committed bcb8017, plan-gate verify green at 4228f8e.

Good catch, caught at the right time -- before code, not after. Keep going on T22-T27; tell me
if you find the same shape there.
