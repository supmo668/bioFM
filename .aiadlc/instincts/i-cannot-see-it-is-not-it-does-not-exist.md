---
name: i-cannot-see-it-is-not-it-does-not-exist
confidence: 0.800
created: 2026-10-31T02:45:36Z
last_reinforced: 2026-10-31T02:45:36Z
ttl_days: 30
triggers: [artifact, account-scoped, not recoverable, no longer resolves, behind, origin/main, IDLE, parked, monitor, unrecoverable]
tags: []
---

Three times in one window, an absence measured from one vantage point was written down as an absence in the world. Each was wrong, and each looked like a finding.

1. A tracked config stated a provenance table "existed only on a claude.ai artifact that no longer resolves." It resolves. The artifact is ACCOUNT-SCOPED, so it reads for its owner and nobody else; the agent could not read it and reported it as gone. The full table was intact.
2. I told an agent its branch was 26 commits behind. I had measured my own UNPUSHED local main. Measured against origin/main it was 0 behind.
3. A dispatch was parked as "recipient IDLE" while a dispatch-monitor process for that agent was running, and separately agent-wake called a session LIVE when nothing was polling its inbox.

**Why:** the two claims have different evidence. "I cannot see it" needs only my own failed lookup. "It does not exist" needs a vantage point that would have seen it. Writing the second on the evidence for the first produces a confident, checkable-looking falsehood - and because it reads as a measurement, the next person ratifies it instead of re-checking. I ratified instance 1 myself after verifying that the diff was comment-only and never verifying that the new comment was true.

**How to apply:** write the claim you actually measured, and name the vantage point in it. "Not in the repository" not "lost". "Unreadable from this worktree" not "not armed". "0 behind origin/main" not "behind". Before asserting a thing is gone, ask who WOULD be able to see it and check from there - the owner for an account-scoped surface, origin for a branch, the process table for a liveness claim. A review that confirms which lines changed has not confirmed that the new lines are true.
