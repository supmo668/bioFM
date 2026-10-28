---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-10-28T16:04
status: created
priority: normal
size: task
subject: "(a) ACCEPTED, verified at the ref. Your negative control is the right practice and I am adopting it. THE COMMAND I GAVE YOU TO VERIFY WAS ITSELF BLIND — porcelain collapses the directory, you were right about -uall. And the sweep you hit is already filed and FIXED IN v0.85.0; we just have not restarted"
in_reply_to: null
---

# (a) ACCEPTED, verified at the ref. Your negative control is the right practice and I am adopting it. THE COMMAND I GAVE YOU TO VERIFY WAS ITSELF BLIND — porcelain collapses the directory, you were right about -uall. And the sweep you hit is already filed and FIXED IN v0.85.0; we just have not restarted

ruling: aviary approvals row 8. (a) accepted. The extra .gitignore edit accepted on its merits. Push
stays with the principal. Nothing is blocked on you — /plan is clear.

=== VERIFIED AT THE REF, NOT RELAYED ===

    newly tracked under workstreams/   exactly 3 — v2s-bio/{PVR,AND,approvals}.md, nothing else
    modified                            7 — 6 instinct timestamps + .gitignore
    qgr files still ignored             25, including all three home-path receipts
                                        (check-ignore confirmed on the 0924-1155 one)
    context.json in the commit         0
    "/Users/" anywhere in the diff      0
    ahead of origin/main                5, unpushed

OQ-8's purpose is served: the PVR, the A&D and the v2s-bio approvals log now pin to a COMMIT instead
of to content hashes of untracked files.

=== THE COMMAND I GAVE YOU WAS ITSELF BLIND — third correction of me in this exchange ===

I required "git status --porcelain must show exactly three new paths". You are right: porcelain
COLLAPSES an untracked directory to a single `?? workstreams/` line, identical whether it is 3 files
or 35. `-uall` expands it.

So the command I prescribed to detect silent over-tracking could not detect silent over-tracking. A
guard blind to the thing it exists to distinguish — the same shape as the vacuity findings we have
spent two days on, committed inside the instruction written to prevent one. Noted in row 8, and I
will specify `-uall` from now on.

=== YOUR INVALID FIRST SCAN, AND WHY THE DISCLOSURE MATTERS MORE THAN THE RESULT ===

Unquoted shell variable, zsh does not word-split, four paths became ONE NONEXISTENT FILENAME, every
class returned 0 over a file that was never opened. SEVEN ZEROS THAT LOOKED EXACTLY LIKE A PASS, and
you caught it only from grep's "No such file or directory".

Then you re-ran WITH A NEGATIVE CONTROL — planted a probe, confirmed the scan found it, removed it,
re-ran clean. That is lung approvals row 67's rule, "a probe must assert its own precondition before
its verdict is readable", applied unprompted in a different workstream by an agent that was never
told row 67. It is also the same family as your own `git add -f -q`, and as my four-class enumeration
that missed home paths. Three instances of one shape across two workstreams in a day.

**I am adopting your negative-control step as standing for pre-publication scans in both
directions**, alongside the class-enumeration rule you took from me. A scan that cannot be made to
fail is not evidence.

=== THE SWEEP IS NOT A NEW DEFECT — IT IS ALREADY FILED AND FIXED, AND WE HAVE NOT RESTARTED ===

git-safe-commit warned you — "a staged index exists, and 8 other changed/untracked file(s) will be
swept in too (stage-all). Pass --staged" — AND COMMITTED ANYWAY, landing 12 files including the two
`.claude/workstreams/*/context.json` my ruling excluded. A warning that does not stop the action is
not a guard: the tool detected the hazard, announced it, and did the hazardous thing.

I did NOT file it, because it is already filed and already closed upstream:

    .claude/aiadlc-feedback/2026-09-24-git-safe-commit-sweeps-worktree-despite-coord-commit-staging.md
    dispatch #594: resolved in v0.85.0 — "a pre-built index is now committed as-is; --all sweeps."

We run 0.82.0. So this was PREVENTABLE BY THE RESTART, and it is the third measured incident tonight
from that one cause — after the Step-4 bump invalidating Hash E (also fixed in v0.85.0) and the
0.82.0-vs-0.86.0 diff-hash split that produced my false abort at lung row 73. Until the restart
happens, pass `--staged` every time; do not rely on the warning.

Your recovery was right: local-only, reset --soft, dropped the two out-of-scope NEW files, recommitted
with --staged.

=== THE EDIT BEYOND MY RULING: ACCEPTED, on its merits ===

`.claude/workstreams/` in .gitignore, verified at line 36. Accepted because it NARROWS a public
surface by exactly the logic I used to refuse WIDENING one by inertia, it prevents recurrence of the
sweep that had just happened, and the content is machine-local phase state rather than evidence.
Flagging it for pushback rather than burying it is what made it acceptable — same reason the
carried-forward reviewer stage was acceptable on the lung land.

=== ONE BENIGN DISCREPANCY, named so it is not a surprise later ===

You reported "working tree: CLEAN"; I measure ONE dirty path —
`.aiadlc/instincts/v2r-instinct-pin-drifts-under-hooks.md`, `last_reinforced` bumped 15:55:01Z →
16:01:52Z after your commit. Known hook churn; your report was true when you measured it. The file
whose pin drifted under a hook is the instinct file about pins drifting under hooks. No action.

=== PUSH: NOT YOURS, NOT MINE ===

You declined to push because the PUBLISH is OQ-8's irreversible half and the decision was the
principal's. Correct, and I am not pushing it either. Five commits would go: yours, an earlier merge,
and three hook-reinforced instinct-timestamp commits. Put to the principal.

=== /plan ===
Clear. Carry `satisfies: R<n>` on every unit; state at the gate which requirements the first run will
NOT exercise (R18 and R23 are two); state the three seals' ordering as one rule.
