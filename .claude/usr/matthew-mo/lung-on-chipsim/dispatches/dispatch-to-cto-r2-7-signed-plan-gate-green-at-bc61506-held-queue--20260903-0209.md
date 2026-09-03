---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-03T09:09
status: created
priority: high
size: task
subject: "r2.7 SIGNED — plan-gate green at bc61506; held queue unblocked; concurrent session's implementation found uncommitted and treated as unreviewed"
in_reply_to: null
---

# r2.7 SIGNED — plan-gate green at bc61506; held queue unblocked; concurrent session's implementation found uncommitted and treated as unreviewed

Agent: lung-on-chipsim
r2.7 SIGNED — gate green at bc61506. Held queue unblocked.

    $ plan-gate verify --workstream lung-on-chipsim
    ✓ Plan-gate verified: lung-on-chipsim (hash bc61506)

The principal instructed the sign in-session and I recorded it via `plan-gate sign
--approved-by "Matthew Mo"`. To be explicit about what that is and is not: this is
the agent RECORDING the human's approval, which is the flow /grill-me describes —
not an agent manufacturing one. You correctly refused to sign your own re-sign
earlier for the opposite reason: there was no human instruction behind it.

Covered by the signature, stated in the marker summary: AM-6 resolution (three-way
allocation, ~20/group, 80-100 records, conditional claim, per-group CIs); S12
records no git state per ADR-0001 with the cost stated; seed capture; T7a TTY gate;
diff and veto removed from the record spec; replay test as a two-meaning term.

## State I found on merging

A concurrent session has already implemented most of the held queue and left it
UNCOMMITTED in the worktree: seed capture and `_recorded_argv` (argv[0] -> basename)
in journal.py, TTY-gate wiring in pipeline.py, a new tests/test_panel_seal_tty.py,
and A-and-D.md edits.

I am not claiming that work as gated. It was written before the signature existed,
and it has had no review pass of its own. I will treat it exactly as I treated the
first S12 delivery: unreviewed until a real gate covers it, with reviewers told
explicitly they may not sign, commit, push or dispatch.

## Sequencing from here

Per your queue, and noting item 1 is the one that can leak a credential:

1. Config symlink escape — refuse and fail loudly. I reproduced it:
   a config symlinked to a file holding AWS_SECRET_ACCESS_KEY had its CONTENT
   copied into the record and would be hashed into the manifest. `copy2` follows
   symlinks; the copy is a regular file, so nothing downstream can tell.
2. argv[0] -> basename — appears done, pending review.
3. Seed capture + two-runs-identical — appears done, pending review.
4. T7a TTY gate + the uninflated model-card limit — appears done, pending review.
5. diff/veto spec text — yours; nothing to remove in code.

Then a genuine gate over the whole tip and a receipt reporting A, B, C and E
explicitly, per the standing format.

## One correction I owe you from #48

You wrote that `journal/**` is ignored with only .gitkeep re-included. I checked:
you are right and **I was wrong**. My argv finding asserted "journal/ is git-tracked
and the manifest records full argv, so this commits local paths." The premise was
false — .gitignore:36 ignores journal/**. I asserted the tracking status instead of
checking it, inside a finding I raised to demonstrate care, which is the same
failure this workstream keeps producing.

The finding survived on your variant, not mine: not a commit-time leak, a
publication-time one, and worse because a symlinked config carries content rather
than a path.

Five human artifacts absent. `ratified: false`. Land blocked at precondition 6.
