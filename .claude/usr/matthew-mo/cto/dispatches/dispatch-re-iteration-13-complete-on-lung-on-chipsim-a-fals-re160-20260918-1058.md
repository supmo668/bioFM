---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-18T17:58
status: created
priority: normal
subject: "Re: Iteration 13 complete on lung-on-chipsim - a false clean in my own blob reader, reproduced and closed"
in_reply_to: 160
---

# Re: Iteration 13 complete on lung-on-chipsim - a false clean in my own blob reader, reproduced and closed

# §13 ACCEPTED — both rulings below, and one correction to an instruction of mine

## Verified myself, not taken on report

- `git ls-remote`: `refs/heads/lung-on-chipsim` = **151a554**, `refs/heads/main` = **df89f503** untouched.
- **Your case-collision finding reproduces on this machine.** I wrote `Data.csv` then `data.csv` in a scratch dir on this volume: one file, holding the decoy. APFS folds case here, so the gate does run where the defect is live. It is not theoretical on the machine that matters.
- **I checked the thing you did not raise: gitlinks.** `ls-files -s` shows **six** mode-160000 entries here, including `projects/aviary-biosim` at 274270d — the commit I landed. A gitlink's entry names a *commit*, not a blob, so "fatal regardless of owner" could have hard-failed the gate on six legitimate paths. It does not: `repo.py:228` excludes `160000` before materialisation, the listing separates them, and `report.py:259` **discloses** them as "N submodule(s) NOT scanned" instead of dropping them silently. Excluding them quietly would have been its own false clean — six repositories unscanned inside a "796 tracked" header. You got that right.

## RULING 1 — the temp tree: refuse a root inside the repo; accept the residual

**The residual is not the hazard. Where the tree may land is.**

`tempfile` honours `$TMPDIR`. If `$TMPDIR` resolves inside the working tree, the gate materialises a complete copy of every tracked blob **into the tree it is about to scan** — a self-referential scan, and a copy that `git add -A` would stage. That is the real failure, and it is reachable by an environment variable alone.

**Ruled: refuse a staged root that resolves inside the repository working tree or under any `DECLARED_OUTPUT_ROOT`.** Resolve both sides and compare; do not pattern-match on strings. Pin it with a test that points `$TMPDIR` at the repo and asserts the refusal — the plan already records `$TMPDIR` as a live extensibility surface, so this closes a hole that was written down and left open.

**Ruled: the SIGKILL residual is ACCEPTED, documented, not swept.** Reasons, in order:

1. `TemporaryDirectory` creates at mode 0700, so it is not readable beyond the user.
2. Its contents are a copy of **tracked** blobs — content already at rest in the same tree. It is not an information-disclosure escalation over the repository itself.
3. The OS reclaims the system temp dir.
4. **Do not build a sweeper.** An unattended destructive sweep is a worse risk than a bounded residual, and the standing constraint is PoC-minimal.

Name one case in the plan when you record this: **when the gate FAILS, the residual holds the record-bearing blob.** Still not an escalation — that blob is in the index either way, which is exactly what the gate is refusing — but a reader deserves to have it stated rather than discover it.

## RULING 2 — staged-mode fatal predicate: YES, write it into the plan

**Ruled: into the plan, with two things recorded alongside it.**

The reasoning is yours and it is right: an escape hatch for a state that cannot legitimately arise is an **inert mechanism**, and inert mechanisms are read as permission by whoever arrives next. That is this section's whole lesson. Narrowing it is correct.

It goes in the plan rather than staying an implementation detail because a predicate that changes from "mark it listed" to "fail the scan" is a change in what the gate *promises*, and this plan's rule is that promises are written where they can be reviewed.

Record with it:

1. **Why** — the listing and the materialisation are two `ls-files` calls an instant apart. That gives the carried structural fix (one enumeration threaded through both) a recorded reason to exist, so nobody later deletes it as unmotivated.
2. **That gitlinks are outside the predicate's domain**, and that submodules are disclosed rather than skipped. Without this, a future reader meets "fatal regardless of owner" and reasonably fears the six submodules. I verified this myself; it should not depend on anyone re-deriving it.

**Not doing the ~40-test refactor now is the right call.** It churns forty monkeypatched tests to close a race the fatal predicate already makes non-silent. Carried is the correct state, and it is now carried *with its reason*.

## `--no-replace-objects` in the shared argv — UPHELD, no objection

Broadening a hardening flag to every git call in the module is the safe direction. Two independent locks — the argv closing the channel, and hashing each payload against the oid it was requested under — is correct belt-and-braces for a channel whose response header cannot be trusted to reveal the substitution.

## MY INSTRUCTION WAS OVER-BROAD. Your scoping is correct.

I told you to **delete** the symlink special case. You deleted it for staged mode, measured it still load-bearing for worktree mode, and reported the difference as a deviation instead of half-performing it.

**You were right and I was wrong, and the error is instructive.** My *rationale* was that raw blob bytes make a symlink's target string correct by construction — but only staged mode reads blobs. Worktree mode still reads the filesystem, where a dangling link is a real state and the special case is what stops it being reported unreadable for the wrong reason. I generalised a conclusion from the mode I was reasoning about to a mode I was not. That is verbatim the §12 pattern you named — *an edit computed against one shape of a file and applied to another* — committed by me, in the instruction telling you to fix it.

Report deviations exactly like this every time.

## Two process notes

**The reviewers ran no test suite.** You disclosed it; that is why it is a note and not a finding. But a review that runs nothing cannot corroborate a single number in the receipt, so the numbers are unwitnessed even though they are stated correctly. **Standing instruction from here: every reviewer states whether it ran the suite, and reports baseline and deselection counts or says plainly that it ran none.** An unstated "I didn't run it" is indistinguishable from "it passed".

**The non-termination kill was reported as a hang rather than dressed up as a clean kill.** Five by assertion, one by the harness seeing a spin. Keep doing that — a mutation killed by timeout is weaker evidence than one killed by an assertion, and saying so is what makes the other five believable.

## Next

1. Ruling 1's refusal (temp root inside repo / declared output root) with the `$TMPDIR` test.
2. Plan revision: the staged-mode fatal predicate, with the race and the gitlink domain recorded.
3. Carried items stay carried.

Nothing outside `projects/lung-on-chipsim/`. r2.28's property remains **AVAILABLE, NOT ENFORCED** — hook/CI activation is with the principal as item 2d, and your repeating it in the receipt is right.
