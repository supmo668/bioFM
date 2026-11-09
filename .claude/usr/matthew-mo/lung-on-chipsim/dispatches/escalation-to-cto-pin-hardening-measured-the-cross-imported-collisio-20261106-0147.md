---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-11-06T01:47
status: created
priority: normal
size: task
subject: "Pin-hardening measured: the cross-imported collision is NOT the one the handoff named — fix needs authorization (touches pipeline.py)"
in_reply_to: null
---

# Pin-hardening measured: the cross-imported collision is NOT the one the handoff named — fix needs authorization (touches pipeline.py)

Agent: lung-on-chipsim
Finding: workstreams/lung-on-chipsim/findings-staging/2026-11-06-duplicate-public-constants-seam.md
Branch: lung-on-chipsim-staging @ 217112c8 (PUSHED, VERIFIED a250f60f..217112c8). Never a PR head.
Code changed: NONE. projects/lung-on-chipsim subtree still 89b5c94d on origin/main AND on HEAD.

WHY THIS IS NOT THE NOTE I WAS HANDED
The inherited pin-hardening queue named ONE latent gap: "ENTRY_KEYS in two modules, latent, nothing
imports it across modules today." Both halves are true of ENTRY_KEYS. Neither is true of the class.
An AST sweep of every public module-level constant in chipsim/ found TWO colliding names, and the
second one IS cross-imported:

  ENTRY_KEYS        theta.py:58 ("value","unit","citation","assumed")
                    prior.py:36 ("mean_log","sigma_log","citation","assumed")    never imported
  SCAFFOLD_RELPATH  theta.py:49 configs/templates/theta_priors.scaffold.yaml
                    prior.py:30 configs/templates/transport_prior.scaffold.yaml  imported from BOTH

  pipeline.py:361  from chipsim.transport.theta import SCAFFOLD_RELPATH, write_scaffold
  pipeline.py:373  from chipsim.transport.prior import SCAFFOLD_RELPATH, write_scaffold

write_scaffold collides too: two names per site, not one. The name I was handed was the harmless one.

WHAT IS TRUE TODAY, BEFORE WHAT COULD GO WRONG
Behaviour is CORRECT and the suite is green. Both imports are function-local (_cmd_theta_scaffold
:360, _cmd_transport_prior_scaffold :372), so neither shadows the other. I am NOT reporting a bug.
I am reporting WHERE the correctness lives: in the PLACEMENT of two import statements. No type,
name, test or comment records that the placement is load-bearing. Hoist them to module level - the
ordinary tidy-up someone eventually does to two function-local imports - and the second binding wins
module-wide, so _cmd_theta_scaffold writes the PRIOR's template path. It would not raise. It would
report success and write the wrong file. Stated as the consequence of a refactor that has NOT
happened, not as an observed defect.

WHY I DID NOT JUST ADD THE GUARD (the pre-authorized move)
The cross-file pin is sound and non-noisy - proven, zero false positives in chipsim/. I did not add
it because IT WOULD GO RED AND I CANNOT CLOSE IT: its only two violations are the rows above, and
closing SCAFFOLD_RELPATH means renaming live call sites in pipeline.py. A pin whose fix is not
authorized leaves the suite red, which is worse than leaving the hazard latent. This session already
catalogued two unsound instruments of my own; I am not shipping a third.

THE ASK - one authorization, three bounded gated steps
1. ENTRY_KEYS -> _ENTRY_KEYS in both modules. In-repo precedent: label_reference.py:37
   _REQUIRED_ENTRY_KEYS. No call sites outside the two modules. Zero blast radius.
2. SCAFFOLD_RELPATH -> THETA_SCAFFOLD_RELPATH / PRIOR_SCAFFOLD_RELPATH, updating pipeline.py
   :361,:363,:373,:375 and tests/test_m1_inputs.py:151,246. Private is not available - it is
   legitimately module surface. Whether write_scaffold gets the same treatment I am NOT pre-deciding.
3. Then the cross-file guard, green at that point, closing the class.
Steps 1+3 alone are defensible as pure pin-hardening if 2 is unwanted. STEP 3 MUST NOT LAND WITHOUT
STEP 2, or the suite goes red.

Scope note so the count is not misread: chipsim/ only. Test files excluded deliberately - they
legitimately share ROOT and CONFIGS, so including them would have produced a noisy instrument and a
misleading number.

UNCHANGED AND STILL BLOCKING (re-measured this turn, trunk 600e510b, fetch-VERIFIED)
- Row 107 strike: HELD on the fork. (a) takes the roster to 24, makes the ratified "6 of 26" stale,
  and FAILS the suite - test_published_snapshot_claims.py:553 asserts 39 - ROSTER_SIZE == 13, and
  39-24=15. So (a) is a gated code change, not a config edit. Row 108 is blocked by the SAME fork,
  because writing "6 of 24" vs "6 of 26" is what the fork decides. One word and I execute either.
- Row 110: d30891e3 is STILL NOT on origin/main (merge-base --is-ancestor false), and
  origin/main:CLAUDE.md:144 still carries the wording you told me not to cite. I cannot cite wording
  that is not published.
- Row 105's authorisation contradiction and row 109's "42" correction remain open with you.

next_handoff: biofm/matthew-mo/lung-on-chipsim
