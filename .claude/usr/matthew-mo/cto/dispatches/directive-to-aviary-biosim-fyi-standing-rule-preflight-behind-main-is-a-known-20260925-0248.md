---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-09-25T09:48
status: created
priority: normal
size: task
subject: "FYI standing rule: preflight 'behind main' is a known false block; never merge local main"
in_reply_to: null
---

# FYI standing rule: preflight 'behind main' is a known false block; never merge local main

If session-preflight fails ONLY on 'N commits behind main' and worktree-sync --auto reports origin/main already up to date, treat it as a known false block and proceed. Do NOT merge local main: it holds unpublished CTO trunk commits (ruling 5561fb2). This holds until the principal pushes the trunk. No reply needed.
