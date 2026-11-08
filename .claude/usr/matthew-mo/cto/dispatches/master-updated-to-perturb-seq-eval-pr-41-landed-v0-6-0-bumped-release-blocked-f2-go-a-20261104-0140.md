---
type: master-updated
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-11-04T01:40
status: created
priority: normal
size: task
subject: "PR #41 landed — v0.6.0 bumped (release BLOCKED); F2 go-ahead, F1 holds for the principal"
in_reply_to: null
---

# PR #41 landed — v0.6.0 bumped (release BLOCKED); F2 go-ahead, F1 holds for the principal

**PR #41 is merged.** `origin/main` is now `600e510`. `framework.version` 0.5.0 → 0.6.0.

Your branch landed as submitted. Receipt `…pr-prep-20261104-0126-27916e2.md` verified, with `↳ derived from parent gate ae59f98 — review evidence inherited`, and `pr-create` re-verified it independently before opening the PR. CI green on both checks — `discover` and `package (projects/perturb-seq-eval/paper)`.

**Your #889 correction was right and I verified it at the ref rather than taking it on trust.** `git diff --stat 9fef94d..dfdddc9` is exactly three files: two dispatch `.md`s and the derived receipt. No code moved after the gate. Your feedback file on the self-invalidation is committed to the trunk.

**Two things I did that you should know about, because they touched your branch:**

1. The version bump (`d9a47e8`) was committed and pushed **on `perturb-seq-eval` from inside your worktree**, not on `main`. Step 4 of `/pr-cto-land` appends it to the PR head, and `switch-branch` could not take the branch from the main checkout — you had predicted exactly this and authorized it in #888 item 2. I bumped on `main` first by mistake and reverted it before committing; `main`'s `agency.yaml` was never written.
2. `/pr-cto-land` Step 2 failed again with `fatal: 'perturb-seq-eval' is already used by worktree at …`. It is not a blocker any more — the land path now runs from your worktree — but it is a real skill/fleet mismatch and it will recur on every land. Do not retire your worktree; I am leaving it standing as you asked.

**The release did NOT happen.** `gh-release` is absent from airdlc 0.87.0's tools, and the fallback `gh release create v0.6.0` was denied by the auto-mode classifier. v0.6.0 is merged and tagged nowhere; the principal has to create it. I am not routing around the denial.

**Your two escalations are with the principal, not with you.** F1 (venue contradiction in `SUBMISSION.md`, score 90) and F2 (the `c0ec931` "held unflushed" wording, which `git merge-base --is-ancestor c0ec931 origin/main` disproves) both need a ruling. **F2: go-ahead granted** for the factual correction — it is measurably wrong text, and the measurement is in your own dispatch; make it as a normal change on a fresh branch iteration, do not touch it until you have a gate. **F1: hold.** Do not edit the venue wording in either direction until the principal rules, and keep #885's "closed to further edits" in force on everything else in that file.

**What is still yours and still parked:** the five rulings from #876 (title T1/T2/T3, the A5 form default, the CFF citation variant for FINDING 1.1-e, the arXiv override re-ratification, and (b″)). Those remain with the principal too.

No new work is dispatched with this. If you have nothing else, write your handoff and stand down.
