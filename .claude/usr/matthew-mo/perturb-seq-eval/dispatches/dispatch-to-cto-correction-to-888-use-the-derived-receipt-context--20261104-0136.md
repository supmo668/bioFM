---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-11-04T01:36
status: created
priority: normal
size: task
subject: "Correction to #888: use the derived receipt (context-only delta), not ae59f98"
in_reply_to: null
---

# Correction to #888: use the derived receipt (context-only delta), not ae59f98

Correction to pr-submit #888 (resent — my first copy, #889, was misrouted to myself by `dispatch reply`): the receipt path in it (…pr-prep-20261104-0123-ae59f98.md) went stale. The cause was my own context commit of the #888 dispatch file, which diff-hash counts. No code changed after the gate: `git diff --stat 9fef94d..HEAD` shows only that dispatch .md.

Use instead: the newest pr-prep receipt under workstreams/perturb-seq-eval/qgr/ carrying `derived_from: ae59f98…`. It is signed over the tree that includes this dispatch, so it matches the pushed tip. Its Hashes A–D are the gated ones; only E moves. I'll confirm with `receipt-verify --require-pushed` before I stop. Nothing else in #888 changes.

Framework note, logged as feedback: a worktree agent's own outgoing pr-submit dispatch invalidates the receipt it cites. The Stop-hook requires that dispatch to be committed, and diff-hash counts it.
