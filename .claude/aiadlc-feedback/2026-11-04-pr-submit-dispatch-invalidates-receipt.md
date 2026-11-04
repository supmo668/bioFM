---
type: plugin-feedback
target: airdlc plugin
plugin_version: 0.90.0
reporter: biofm/matthew-mo/perturb-seq-eval
date: 2026-11-04
scope: plugin / operating-system behavior — NOT repo/app work
---


## 🟠 1. Own pr-submit dispatch invalidates the receipt it cites
**File:** `tools/diff-hash` (Hash E input set) + `hooks/context-commit-check`; surfaces via `skills/pr-submit`
**Symptom:** `receipt-verify --require-pushed` reports "Code changed after the gate ran" immediately after a clean `/pr-prep` + `/pr-submit`, with no code edited in between. The receipt quoted in the pr-submit body is already stale by the time the CTO reads it.
**Root cause:** proven, not inferred. `context-commit-check` blocks turn-end until the outgoing dispatch `.md` under `.claude/usr/<p>/<agent>/dispatches/` is committed; `diff-hash` counts that file in Hash E. So the act of submitting moves the hash the submission cites. `git diff --stat 9fef94d..HEAD` showed only that dispatch `.md` — Hashes A-D unchanged.
**Fix:** exclude `.claude/usr/**` from `diff-hash`'s input set — context artifacts already never gate code. Alternatively, have `pr-submit` commit its own dispatch *before* it computes and cites the hash.
**Effect:** a receipt stays valid across its own submission, and the CTO stops having to distinguish a self-inflicted mismatch from a real one.
**Status:** open (filed against airdlc 0.90.0; CTO-confirmed at the ref 2026-11-04, landed in PR #41)

Observed 2026-11-04, perturb-seq-eval, airdlc 0.90.0. After `/pr-prep` signed receipt ae59f98 and `/pr-submit` sent dispatch #888, the `context-commit-check` Stop-hook requires the outgoing dispatch .md under `.claude/usr/<p>/<agent>/dispatches/` to be committed. diff-hash counts that file, so Hash E moved to 27916e2 and `receipt-verify --require-pushed` failed: "Code changed after the gate ran". The receipt quoted in the pr-submit body is stale by the time the CTO reads it. This is the same class of failure as the three failed lands on #863.
Workaround used: commit the context first, then sign a `--derived-from` receipt, then send a correction reply.
Suggested fix: have diff-hash exclude `.claude/usr/**` context artifacts, which already never gate code. Or have pr-submit commit its own dispatch before it computes and cites the hash.

## 🟠 2. /pr-cto-land Step 2 cannot switch to a branch a worktree holds — the land has no route in a worktree fleet
**File:** `skills/pr-cto-land/SKILL.md` Step 2 → `tools/git-cto switch-branch`
**Symptom:** `/pr-cto-land <branch>` run from the main checkout, as its own precondition 1 requires, fails at Step 2:
`fatal: '<branch>' is already used by worktree at '<repo>/worktrees/<branch>'`
Observed 2026-11-04 for `perturb-seq-eval`, airdlc 0.87.0. HEAD stays on the CTO branch, and the skill has no documented continuation.
**Root cause:** the two preconditions are mutually exclusive in a worktree fleet. Precondition 1 pins the CTO to the main checkout; a worktree agent's branch is checked out in its own worktree for the whole life of the agent. Git permits one checkout per branch, so `switch-branch` can never succeed while the owning agent exists. This is structural, not a race — it fails on every land, not occasionally.
**Consequence, and the reason this is 🟠 and not a nuisance:** the steps after Step 2 all assume the CTO is standing on the agent branch, and each one silently measures the wrong subject if it is not. `receipt-verify` run from the CTO branch reports `BLOCKED: found N receipt(s) but none match current code` — a **false negative that reads exactly like a real stale-receipt failure**, and it was taken as the verdict on two earlier attempts before being caught. `version-bump` writes `agency.yaml` on the CTO branch instead of appending to the PR head. `pr-create` refuses outright with `BLOCKED: Cannot create PR from main`, which is the only one of the three that fails loudly.
**Fix:** state in the skill that Steps 3-5 run with the agent branch's own tree as the subject, and that in a worktree fleet that means executing them from `worktrees/<branch>` rather than switching. Then either make Step 2 detect the worktree and set the working directory instead of switching, or drop Step 2 and have Steps 3-5 resolve the branch's checkout via `git worktree list --porcelain`. `receipt-verify` should also refuse to report a verdict when the current branch is not the `--workstream` branch, rather than silently measuring whatever is checked out.
**Effect:** the land becomes executable without a human noticing that a BLOCKED verdict was measured against the wrong tree. Removes the need for the CTO to choose between retiring a live worktree and hand-adapting the skill on every land.
**Status:** open (filed against airdlc 0.87.0; reproduced 4× on `perturb-seq-eval`, worked around on the 4th by running Steps 3-5 inside the worktree with the owning agent's written consent — pr-submit #888 item 2)

**Relationship to item 1.** These two compound. Item 1 moves the receipt's Hash E after the gate; item 2 makes the verification that would catch it run against the wrong tree. Together they produce a land that fails for a reason the operator cannot distinguish from a genuine gate failure — which is what three failed lands on #863 actually were.
