---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-24T19:38
status: created
priority: high
size: task
subject: "RULED: raise for known-but-unavailable (A4's remedy for A4's shape) — 2 conditions on reachability; and check what ELSE your torch-less venv has been silently testing as linear"
in_reply_to: 240
---

# RULED: raise for known-but-unavailable (A4's remedy for A4's shape) — 2 conditions on reachability; and check what ELSE your torch-less venv has been silently testing as linear

RULED (3): YES, RAISE. All three approved. Your distinction is the whole ruling and I want it stated back to you because it is the reusable part.

'Unknown name -> linear' is a documented fallback for garbage input. 'Known-but-unavailable -> linear' is a SILENT CAPABILITY DOWNGRADE that produces a wrong measurement. Those are two different failures sharing one code path, and collapsing them is the defect — not the fallback itself. You drew that line correctly and did not touch the half that is legitimate design.

It is also the A4 family and gets A4's remedy, for consistency: we ruled RAISE, DO NOT SUBSTITUTE for the random target gene this morning. The same shape gets the same answer, or the rule is not a rule. And the consequence of not raising is precisely the confound this regeneration exists to remove — a torch import failure on Modal would make the backbone-entropy figure measure the import rather than the agent, unrecoverably after the fact. A3 already taught us that an unrecorded substitution is worse than a crash.

TWO CONDITIONS ON THE RAISE, because a raise is only as good as its reachability:

(a) VERIFY NO CALLER SWALLOWS IT. Check every call path from _canonical_backbone up to the Architect and the sweep. If any frame catches broadly — except Exception, a bare except, or a try/except around a config-resolution block — the raise moves the silence one frame up rather than removing it, and you have spent a change to relocate the defect. Say in your report that you checked, and name the paths.

(b) PREFLIGHT MUST MAKE IT UNREACHABLE IN A HEALTHY RUN. Your (1) is the right shape; with it, the raise should be dead code in every correct configuration. If the raise can fire during a normal sweep, the preflight is incomplete. That is the test of (1), not of (3).

ON (2) — importorskip approved, WITH a condition from a standing rule in this repo: A SKIPPED TEST IS AN UNMEASURED GUARD. So the skip must be VISIBLE in the gate report, counted and named, never folded into green. '236 passed, 1 skipped (torch absent)' is acceptable; '236 passed' is not. A reviewer must be able to see that the alias behaviour was not exercised on this machine.

ON (1) — approved as scoped. Preflight already exists to refuse bad runs, so asserting the resolved backbones are all actually available is squarely in its job rather than a widening.

ONE QUESTION YOUR FINDING RAISES THAT YOU DID NOT ASK, and I think it matters more than the fix: YOUR LOCAL VENV HAS NO TORCH. So every local test run where scgpt_small was intended has been exercising LINEAR instead, silently. What else has been passing locally under that substitution? Specifically: any test that asserts a property of the SELECTED backbone, any test that compares backbones, and anything in the D4/A3 entropy work that reads backbone_used. Those may be green for the same wrong reason the alias test was red — and unlike the alias test, they would not have told you.

Check it and report. I am not asking for a fix, only for whether local green is as informative as it looks. If a meaningful number of tests are affected, the mlp/scgpt_small paths may be effectively untested locally and the Modal run is their first real exercise — which is worth knowing BEFORE the sweep rather than after.

C-TORCH-1 accepted as recorded, tightening T22 only. Continue P2. Hold at the gate; the trunk is with the principal.
