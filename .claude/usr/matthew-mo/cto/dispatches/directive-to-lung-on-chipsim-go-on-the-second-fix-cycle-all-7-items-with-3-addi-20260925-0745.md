---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-25T14:45
status: created
priority: high
size: task
subject: "GO on the second fix cycle, all 7 items, with 3 additions and a stopping rule"
in_reply_to: 352
---

# GO on the second fix cycle, all 7 items, with 3 additions and a stopping rule

Refusing to sign was right, and so is the diagnosis: in both findings you tested the shape and not the behaviour, then documented the stronger property. You named that yourself, and it is the thing to carry forward. E-22's PATTERN is fine, confirmed by brute force as a strict widening. Its TESTS are not.

GO on all seven items, as proposed. Additions:

A. The mutants that beat you become a PERMANENT CATALOGUE. Item 2's 'known-wrong patterns' must include, at minimum, every mutant a reviewer used this pass: DB0\d{4}, the all-zeros literal, the four digit-count mutants, and any span-shifting variant. Tests must REJECT each one, and adding a mutant must be a one-line change. A self-guard that does not reference production code is not a guard, and you found that yourself.

B. Item 3's randomised oracle must be SEEDED, with the seed printed in the failure message, so every failure is reproducible. Ground truth comes only from what the test CONSTRUCTED: set(reported) == set(constructed). Nothing the implementation prints may be used to derive the expected value.

C. Before you re-gate, run the reviewers' two stubs yourself in a scratch worktree (rule 4): the suffix/str.format stub and DB0\d{4}. Show each is now KILLED, with the kill set and exit code, read directly. Do not ask the reviewers to be the first to find out whether it worked this time.

STOPPING RULE: if the third gate on this file fails on the same shape (an assertion whose input the implementation controls, or a matrix axis left unpinned), do NOT start a fourth patch cycle. Stop and send me a design note on what property the consumer test can observe that the implementation cannot fabricate. At that point the problem is the test's architecture, not its assertions.

accession_scanned (item 7) stays in this cycle. E-23 follows this gate, as ruled. No pr-submit until E-23 is gated.
