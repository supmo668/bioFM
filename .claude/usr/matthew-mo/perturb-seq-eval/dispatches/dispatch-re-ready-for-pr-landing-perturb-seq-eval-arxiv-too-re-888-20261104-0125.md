---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-11-04T01:25
status: created
priority: normal
subject: "Re: Ready for PR landing: perturb-seq-eval — arXiv tooling + SUBMISSION.md Part 7 (receipt ae59f98; F1/F2 escalated)"
in_reply_to: 888
---

# Re: Ready for PR landing: perturb-seq-eval — arXiv tooling + SUBMISSION.md Part 7 (receipt ae59f98; F1/F2 escalated)

Correction to #888: the receipt path in it (…pr-prep-20261104-0123-ae59f98.md) went stale. The cause was my own context commit of the #888 dispatch file, which diff-hash counts. No code changed after the gate: `git diff --stat 9fef94d..HEAD` shows only that dispatch .md.

Use instead: the newest pr-prep receipt under workstreams/perturb-seq-eval/qgr/ carrying `derived_from: ae59f98…`. It is signed over the tree that includes this reply, so it matches the pushed tip. Its Hashes A–D are the gated ones; only E moves. I'll confirm with `receipt-verify --require-pushed` before I stop. Nothing else in #888 changes.

Framework note, logged as feedback: a worktree agent's own outgoing pr-submit dispatch invalidates the receipt it cites. The Stop-hook requires that dispatch to be committed, and diff-hash counts it.
