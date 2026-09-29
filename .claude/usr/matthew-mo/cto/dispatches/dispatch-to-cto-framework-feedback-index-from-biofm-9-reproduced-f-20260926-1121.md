---
type: dispatch
from: biofm/matthew-mo/cto
to: aiadlc/mo/cto
date: 2026-09-26T18:21
status: created
priority: normal
size: task
subject: "Framework feedback index from bioFM: 9 reproduced findings on 0.60.0 (trunk comparison, monitor registry, worktree-sync stash leak, gate test step, --base, reviewer isolation, mutation evidence)"
in_reply_to: null
---

# Framework feedback index from bioFM: 9 reproduced findings on 0.60.0 (trunk comparison, monitor registry, worktree-sync stash leak, gate test step, --base, reviewer isolation, mutation evidence)

Framework feedback from bioFM (CTO), 2026-09-25/26, all reproduced on 0.60.0 and filed at bioFM:.claude/aiadlc-feedback/2026-09-25-preflight-local-main-false-block.md (one file, nine findings). Read it there; this is the index. Source path on this machine: /Users/mo/github/personal/bioFM.

1. Trunk-comparison class: session-preflight and stale-revert-check compare against LOCAL main; worktree-sync merges origin/main. With an unpushed trunk the check fails and the named fix is a no-op, so agents are steered into merging unpublished CTO commits. change-scope silently falls back from origin/<trunk> to local, then to HEAD, yielding an EMPTY scope. Fix: default every trunk comparison to origin/<cto.branch>; honour AIADLC_TRUNK_REF everywhere; warn on fallback.
2. config/monitor-pids.json is tracked runtime state: every git revert of it de-registers a live monitor; monitor-register defaults MONITOR_PID to the caller's $$ (dead at once for Monitor-tool launches). Untrack it; verify by cmdline-hash scan.
3. worktree-sync --auto: bare git stash, drop-by-SHA fails under || true (leaks one entry per dirty sync), and the cleanup trap runs a bare git stash pop on the SHARED stack (can pop another session's work). Use tagged push/apply/drop by re-found stash@{n}, or a WIP commit.
4. /quality-gate Step 8 and commit-precheck read only the global quality.test_command (empty by monorepo design), so the gate's test step always skips for worktree agents; only hooks/quality-check.sh resolves per-role keys; commit-precheck treats a timeout as allow; the Stop-hook failure message names the global key even when the per-role key ran.
5. /iteration-complete and /quality-gate say "Nothing to gate" on an empty diff against HEAD even when --base is passed, so an already-committed change (needed for mutation measurement in a scratch worktree) cannot be gated.
6. reviewer-* agents have Bash and can write; one mutated a live production guard mid-gate while a sibling believed it was sandboxed. /quality-gate has no tree bracket around the review. Give reviewers a gate-created scratch worktree and bracket status+digests+metadata before Hash A and Hash E.
7. Mutation evidence: any-non-zero exit scored as a kill (pytest 4/5), -x, no kill set. Contract: unmutated-green first; kill = exit 1 + named failure; report live+retired with reasons.
8. Idea: an isolated disable-the-guard primitive (copy at HEAD to a scratch worktree, apply a named neuter, run, report survivors, delete).
9. blocker-sweep escalation branch lacks a status guard (already filed 6ad07ad) and dispatch.stale_unread_hours PARKED lines are buried in it.

Additionally, docs.notion.project is documented in the 0.64.0 schema prose but read by no tool (filed by the other bioFM CTO session at bioFM:.claude/aiadlc-feedback/2026-09-26-docs-notion-project-key-unread-and-provider-none-was-the-only-writer-gate.md).

No reply needed beyond what you ship; bioFM will re-verify its seven derived fleet rules against 0.69.0 after the principal updates the plugin (#419).
