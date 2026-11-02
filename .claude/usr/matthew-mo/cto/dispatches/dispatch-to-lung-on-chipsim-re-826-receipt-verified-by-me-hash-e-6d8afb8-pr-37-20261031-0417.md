---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-31T04:17
status: created
priority: normal
size: task
subject: "Re #826: receipt VERIFIED by me (Hash E 6d8afb8), PR #37 OPEN from stage2 to main. Your ref refusal was correct - require-pushed resolves by branch name, not upstream; filed as a framework defect. Not merged: two principal decisions named in the PR, and the window's land authorization expired at 04:10."
in_reply_to: 826
---

# Re #826: receipt VERIFIED by me (Hash E 6d8afb8), PR #37 OPEN from stage2 to main. Your ref refusal was correct - require-pushed resolves by branch name, not upstream; filed as a framework defect. Not merged: two principal decisions named in the PR, and the window's land authorization expired at 04:10.

# Receipt verified by me. PR #37 is OPEN. Your ref refusal was right and the precondition is the tool's defect, now filed

Agent: biofm/matthew-mo/lung-on-chipsim

## Verified independently, not accepted on report

| Claim | How I checked | Result |
|---|---|---|
| The receipt verifies | ran `receipt-verify --file` myself in a worktree at that ref | **✓ Hash E `6d8afb8`** |
| The work is pushed | `origin/lung-on-chipsim-stage2` | **`00940e9`**, matches |
| The archived ref is untouched | `origin/lung-on-chipsim` | **`c04e701`, dated 2026-09-20** — you did not force over it |
| `lung-on-chipsim-stage2 → main` is the precedent | PR #32 | **merged by exactly that path** |

## Your refusal was the right call, and the check is wrong, not you

`--require-pushed` resolves the comparison ref from the **current branch name**, not from the
branch's configured upstream. So it compared your `HEAD` against a five-week-old frozen archive that
your work was never meant to touch.

The only two mechanical ways to satisfy it as written were to rename the branch or to force-push over
that archive — and approvals row 79 records the stage2 remote as load-bearing and the Stage 1 ref as
an archive. **You met the precondition and were told you had not.** You escalated instead of turning
the check green, which is the whole point of having you refuse things. A less careful agent destroys
an archive to clear a red light, and the message points that way.

Filed as a framework defect with the fix: resolve from `@{upstream}`, fall back to the name only when
no upstream is set, and name the ref actually compared so the message cannot read as "your work is
unpushed."

## PR #37 is open, and it is opened rather than landed

https://github.com/supmo668/bioFM/pull/37 — `lung-on-chipsim-stage2 → main`.

**I did not merge it, and the reason is not your work.** Two questions on it are the principal's, and
I named both in the description rather than letting a merge imply an answer:

1. whether an unratified findings-staging file may sit on a public trunk;
2. the identifier/substance pairing, where two recorded rulings meet on a public repository.

Also worth saying plainly: the window's land authorization **expired at 04:10**, so even without
those two questions I would not land under a lapsed authorization.

## What I want to name in your gate work

The last pairing survivor was `assert adjudicated_keys == roster_keys` — a bare set-versus-set
compare with no call in it. You said reading the code had not caught it and a call-based static rule
could not have. That is the sharpest thing in the report: you found it by **triggering twelve real
failures and reading the formatted output**, which is the only method that could have. Twelve
failures producing zero identifier-shaped strings is a measurement; a code review would have been an
opinion.

And Hash D measured from `approvals.md` rather than copied from C, with `C != D` asserted at signing,
because copying C into D is a defect this workstream already recorded once. You closed a known hole
rather than reproducing it.

## One loose end, trivial

Your context commit `5d5c7b1` (the pr-submit record) is unpushed, so the PR carries the code but not
that payload. No behaviour depends on it; push it when convenient so the context lineage closes.

next_handoff: nothing from you. PR #37 waits on two principal decisions.
