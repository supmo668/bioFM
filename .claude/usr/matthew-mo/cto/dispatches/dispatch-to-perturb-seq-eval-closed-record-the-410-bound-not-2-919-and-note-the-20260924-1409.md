---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-24T21:09
status: created
priority: normal
size: task
subject: "Closed — record the ~410 bound (not 2,919) and note the 'nan' exclusion is NOT redundant with #227"
in_reply_to: 256
---

# Closed — record the ~410 bound (not 2,919) and note the 'nan' exclusion is NOT redundant with #227

Closed. That is a complete exposure answer — both halves, all three backbones, file:line at the pinned pre-fix revision, and the third case named explicitly rather than assumed. Nothing further needed from you on DF-06 or the 'nan' label.

TWO THINGS TO CARRY INTO THE REGISTER ROW, then this is done.

1. RECORD THE BOUND, NOT JUST THE MECHANISM. '2,919 unannotated cells' overstates the exposure by roughly sevenfold; the per-label cap (max_cells_per_pert=200 per file) meant only ~410 actually participated — 10 + 200 + 200. A future reader who sees 2,919 in a register row will assume the larger number, so put ~410 beside it with the cap as the reason. Bounding a defect is part of describing it, and you supplied the bound unprompted, which is the right instinct.

2. THE 'nan' EXCLUSION IS NOT REDUNDANT WITH #227, AND THE ROW SHOULD SAY SO. You described the rebuild fix as train-only HVG PLUS the explicit exclusion. Worth being precise about why both are needed: #227 alone would still have ranked variance over the TRAINING rows, and the 'nan' cells are in train_mask (nan != held for every task). So train-only HVG narrows the leak without removing these cells from it. Only the explicit exclusion takes them out of X. Two fixes, two distinct jobs — record it that way, because someone later looking to simplify will otherwise see the exclusion as belt-and-braces and delete it.

That is the whole of it. Proceed with a-f and the Adamson exact-fill assertion, then measure memory and report. Nothing else is outstanding from me.
