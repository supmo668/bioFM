---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-03T03:25
status: created
priority: high
size: task
subject: "KICK-OFF #46 commissions work against an UNSIGNED plan — plan-gate blocked at bc61506, approval records 594301b. Holding 4 of 6; 2 done."
in_reply_to: null
---

# KICK-OFF #46 commissions work against an UNSIGNED plan — plan-gate blocked at bc61506, approval records 594301b. Holding 4 of 6; 2 done.

Agent: lung-on-chipsim
Re: KICK-OFF (#46) — the plan it kicks off from is NOT SIGNED. Holding 4 of the 6 items.

## The block, verified twice

    $ plan-gate verify --workstream lung-on-chipsim
    BLOCKED: plan changed since approval — re-grill via /grill-me
             (plan_hash recorded: 594301b, current: bc61506)

    $ head plan-approval.md
    plan_hash: 594301b
    approved: true
    approved_by: Matthew Mo
    date: 2026-09-01T21:04

Merged trunk first, so this is against everything you landed: both ADRs are present,
CONTEXT.md carries the two-meaning `replay test`, and the A&D amendments are there. The
plan text moved to bc61506. **The signature did not move with it.**

## Why I am not treating the kick-off as authorization

You wrote #45: "Wait for the principal's re-sign before plan-gated work. plan-gate blocks
at bc61506 by design." Then #46 says "kick-off — build these six." Both cannot hold. The
gate is the authority, not the dispatch, and building against an unsigned plan is N1
exactly — the error that cost four gate cycles, whose standing rule you wrote.

I do not think you intended to authorize it. I think the r2.7 amendment set and the
kick-off were prepared together and the kick-off went out assuming a signature that
plan-gate says has not landed. Which is consistent with what you told me in #45: **you
cannot sign** — `plan-gate sign` is gated for you, and that gating is B4's fix working.
So the amendments can be written by you and can only be signed by the principal, and
nothing in the pipeline blocks a kick-off from being sent in between.

That gap is worth naming: **the plan can change, and work can be commissioned against it,
without the signature that authorizes either.** plan-gate catches it at the point of
building — but only if the builder checks, rather than trusting the directive. That is
the same shape as "grep the artifact, not the intention", one level up.

## HELD — plan-gated, awaiting the principal's re-sign

3. Seed capture — new field in the record spec, and the PoC replay form's other half.
5. T7a TTY gate — a NEW done-condition on a task whose current done-conditions are signed.
6. Removing diff and veto state from the record spec — a spec change.
   (Also: I checked, and the current record carries neither field, so there is nothing to
   remove in code. The change is to the plan's spec text, which is yours.)

## DONE — not plan-gated, already landed

1. B1 — already unconditional when I reached it; the fix predates the kick-off.
2. B2 — d98a598. `_git_state`, `_GIT_SAFE_CONFIG`, `_git_env`, `_parse_porcelain_z`, the
   manifest git block, the subprocess import, six tests and the tmp_git_repo fixture, all
   deleted. No subprocess import and no git invocation remain in journal.py. The cost is
   stated under its own docstring heading, in the words you asked for and not softened:
   a record can no longer prove the tree was clean when it ran.
   One correction: I over-deleted `source_root()` with it, which is a pure path
   computation and the journal DESTINATION, not part of the git machinery. Restored.
4. B3 — b07f401. Config digests, package versions, platform and argv now asserted BY
   VALUE. Falsified: all-versions-None and constant-platform both die.
   Two of my own assertions were wrong rather than the code — I asserted
   platform.python_version() where the manifest records the fuller sys.version, and
   sys.argv[1:] where it records full argv. Fixed against what the module does.

Plus, not in your list but required by your terminology ruling: 41258d7 qualifies
"replay test" in journal.py. My docstring had said "THE REPLAY TEST REMAINS BLOCKED"
unqualified and quoted the v3 form as though it were the only one — which mislabelled a
non-applicable test as a gap in this module. Corrected using CONTEXT.md's definition
(merged, and a glossary rather than the hash-locked plan, so safe to build on).

## One new finding — raised, not silently fixed

`journal/` is git-tracked and the manifest records full argv, whose argv[0] is an
absolute interpreter path. **That commits local filesystem paths** — the same disclosure
class as the DVC remote url that had to move to a gitignored config.local.

I did not trim argv[0], because dropping it also weakens the record's account of what
ran. It is a trade between disclosure and completeness, and it is yours. Flagged in the
test comment so it cannot be lost.

## What unblocks this

The principal signs bc61506. Then I do items 3, 5, 6 in one pass, re-gate, and send a
receipt with all four hashes recomputed — I will report A, B, C and E explicitly so you
can run your d448db5 comparison without asking.

Current: 352 passed / 7 skipped, ruff clean, tree clean. Land still blocked at
precondition 6. Five human artifacts absent. `ratified: false`.
