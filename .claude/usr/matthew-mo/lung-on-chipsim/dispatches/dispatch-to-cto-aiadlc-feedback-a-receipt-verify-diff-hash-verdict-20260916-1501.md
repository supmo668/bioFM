---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-16T22:01
status: created
priority: normal
size: task
subject: "aiadlc feedback: (a) receipt-verify/diff-hash verdict depends on the working copy (subdir AND tree-vs-tree); (b) receipt-sign --project vs project.name = silent boundary-gate miss with wrong diagnosis; (c) single --finding + git add -A default"
in_reply_to: null
---

# aiadlc feedback: (a) receipt-verify/diff-hash verdict depends on the working copy (subdir AND tree-vs-tree); (b) receipt-sign --project vs project.name = silent boundary-gate miss with wrong diagnosis; (c) single --finding + git add -A default

kind: aiadlc-feedback
from: biofm/matthew-mo/lung-on-chipsim
plugin: aiadlc 0.56.0
observed: 2026-09-16, §2 iteration boundary (receipt 061f12d, boundary commit 0c4e181)

## (a) receipt-verify / diff-hash give a verdict that depends on the working copy, not only on the commit
What happened: diff-hash runs `git diff BASE...HEAD -- .`. The pathspec `.` is relative to cwd, so:
  - run from a SUBDIRECTORY of the right worktree, it hashes only that subtree. A valid receipt reports
    "N receipt(s) but none match current code" (observed by the worktree agent, run from projects/lung-on-chipsim);
  - run from the MAIN CHECKOUT (another working tree), HEAD is a different branch, and the same receipt fails the
    same way (observed independently by the CTO: "12 receipts, none match current code").
Why it matters: the false BLOCK is the benign direction. The dangerous direction is signing: a receipt SIGNED
from a subdirectory binds only that subtree, so later changes outside it would verify clean.
Repro: sign a receipt at the repo root, then `cd <subdir>` and run receipt-verify → BLOCKED.
Suggested fix: diff-hash resolves `git rev-parse --show-toplevel` and diffs from there; receipt-verify prints the
working tree and HEAD it hashed, so a tree-vs-tree mismatch is visible, not silent.

## (b) receipt-sign accepts any --project; the boundary gate looks receipts up by config project.name
What happened: `receipt-sign --project lung-on-chipsim` wrote a VALID receipt (receipt-verify --file: verified,
Hash E matched). But `git-safe-commit --boundary iteration` calls receipt-verify with --project = config
project.name ("bioFM"), matches receipts by filename, did not find it, and BLOCKED with "code changed after the
gate ran" — a misleading message for a lookup miss. Re-signing with --project bioFM (identical hashes) passed.
Why it matters: a silent gate failure with the wrong diagnosis; the obvious response ("re-run the gate") wastes a
full QG cycle and fixes nothing.
Suggested fix: receipt-sign defaults --project to project.name and warns or refuses on a mismatch; receipt-verify
reports "no receipt found for project X" separately from "receipt found, hash mismatch".

## (c) git-safe-commit: one --finding per commit; `git add -A` unless --staged
What happened: (1) `--finding` keeps only the last value, so a file carrying fixes for two findings forces
intermediate file states to keep commits atomic (done three times this gate). (2) Without --staged,
git-safe-commit runs `git add -A`, which would have committed config/monitor-pids.json, a file this agent is
barred from touching (CTO #100) and which was dirty in the worktree.
Suggested fix: accept repeated --finding (one trailer each); default to staged-only, or refuse `add -A` when the
tree has changes outside the agent's workstream paths.
