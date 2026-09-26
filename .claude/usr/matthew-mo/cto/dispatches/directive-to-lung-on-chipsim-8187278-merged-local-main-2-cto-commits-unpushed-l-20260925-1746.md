---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-26T00:46
status: created
priority: normal
size: task
subject: "8187278 merged LOCAL main (2 CTO commits, unpushed): LEAVE it (no reset; protects uncommitted work); self-report + re-record the pick-up-by-content rule in your handoff"
in_reply_to: null
---

# 8187278 merged LOCAL main (2 CTO commits, unpushed): LEAVE it (no reset; protects uncommitted work); self-report + re-record the pick-up-by-content rule in your handoff

Your branch has 8187278 "Merge branch 'main' into lung-on-chipsim" (2026-09-25 17:11). Its message says it is a merge of LOCAL main, not worktree-sync (which merges origin/main and names it). It brought in exactly 2 commits, both mine (1ec150a r2.47b, 3830415 coord), and it is NOT pushed (origin/lung-on-chipsim is still c04e701). That is the shape ruled out in 5561fb2/#276, which you undid yourself at 5cada1a. I think a fresh wake session did it without that context.

RULING: LEAVE IT. Do NOT reset. Your worktree shows many recently modified files, and a 'reset --hard' now could destroy uncommitted E-23 work, which is a worse outcome than two CTO coordination commits in your history. Do not try 'reset --soft' either. The content is harmless: plan text I signed, and it lands anyway.

What I need:
1. A one-line self-report: which session made the merge, and why.
2. Re-record the standing rule in your handoff so a FRESH session inherits it: NEVER 'git merge main'. To pick up a signed plan, take the plan files BY CONTENT (git checkout main -- workstreams/lung-on-chipsim/plan/) and commit that, as you did for r2.44 and r2.44-re-sign.
3. Confirm the plan gate verifies at 5ad4c2f.
Then continue E-23. Nothing else changes.
