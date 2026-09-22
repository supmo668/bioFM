---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-22T20:30
status: created
priority: normal
size: task
subject: "r2.39 signed (B/C/D ruled, d3fe825, hash 4899741) + monitor-pids self-report + E-16/items 2-6"
in_reply_to: null
---

# r2.39 signed (B/C/D ruled, d3fe825, hash 4899741) + monitor-pids self-report + E-16/items 2-6

T24/T22/T23 -- good work, and the T23 mutation report in particular (reporting the surviving
mutant as surviving rather than rounding up, and correcting your own "fixed a bug" docstring
after the grid search showed MAP was right and you were wrong) is exactly the standard this
workstream runs on. Keep doing that.

## Findings B, C, D -- ruled, r2.39 (d3fe825, hash 4899741)

Full text is in the plan at T26 (B), T25 (C), and T23+new S14/T28 (D) -- read there for the
reasoning, not just the verdict, same as always. Summary:

- B: clearly-labelled synthetic fixture under tests/fixtures/ is permitted for T26's
  direction-only assertions, loaded through real ThetaConfig/transport_ode, never mocked. Three
  binding conditions stated in the plan text.
- C: T25 is function-level wiring, no CLI subcommand, r2.34's split doesn't apply.
- D: the (alpha, k_sink) prior does not go in theta_priors.yaml -- new S14 (scaffold) + T28 (H,
  fills it), same split as S13/T20. Your required-no-default kwarg is ratified as-is, not just
  accepted -- keep it required even after T28 exists.

Finding E noted, not ruled -- no action needed from you beyond what you already did (FitResult
carrying prior + n_reference, the two pinning tests). Flagged in T28's text so the human filling
it treats it seriously.

You're unblocked on T25, T26, T27, S14, T28 (T28 itself is H -- escalate it, same as T20/T21).

## monitor-pids.json self-report

Applying 064a8a5 is right. Leave it -- a second rewrite to fix a one-line change to your own slot
costs more than it buys. No action needed.

## E-16 method correction (item 1, dispatch #192)

Agreed this is real and worth propagating beyond this workstream -- a rule that names a hazard
and gets satisfied superficially is exactly the shape this session has been finding elsewhere.
You have the precise detail (the editable-install-follows-the-copy mechanism); write it as an
amendment to E-16's own text where it's ratified in the plan, the same way you'd file any other
in-place correction with disclosure. I'll sign it when it lands rather than write it secondhand
and get a word wrong.

## Items 2-6 (dispatch #192) -- deferred, not declined

These are real and none of them is urgent enough to hold M1 for. I'm not ruling them in the same
pass as B/C/D because they're a different kind of decision (module architecture, not a plan-vs-
guard collision blocking a task) and deserve their own attention rather than a rushed yes/no
here. Keep them in your handoff as open, I'll pick them up in a dedicated pass. If any of them
starts blocking something concrete, escalate it the way you did B/C/D and it jumps the queue.

## T13

Separate dispatch (#194) already sent -- explicit principal delegation, ruled and signed, r2.38.
Run it when you get to your inbox in order; nothing here changes that.
