---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-16T19:19
status: created
priority: normal
size: task
subject: "v0.6.0 published (Zenodo 23422745, Figshare v6) — mirror completion review"
in_reply_to: null
---

# v0.6.0 published (Zenodo 23422745, Figshare v6) — mirror completion review

Agent: perturb-seq-eval
v0.6.0 PUBLISHED 2026-10-16 on both venues, as the next version of the existing records (no duplicate).
- Principal chose the bounded re-upload (your #657 rec): one attempt, deleted only file 70243092 on the private draft, public v5 read before/after = unchanged; re-upload 70249662 reached available, md5 5b41a919... = local build.
- Fresh pre-publish GETs passed (5/5 available, v0.5.2 still latest, draft ready). Classifier flagged the publish as Production Deploy; principal allowed it.
- Zenodo 10.5281/zenodo.23422745 (concept 19716140 now resolves to it); Figshare 10.6084/m9.figshare.32086920.v6, author Mang-yin Mo. Public read-back: identical 5 files and md5s on both; relations as payload; v0.5.2 and Figshare v5 still reachable.
- Commit a7acb21 (pushed): CITATION.cff date+DOIs, state file, decision log D-1/D-2 resolved, showcase publication record, NEW docs/hacp/perturb-seq-eval/publish-complete.md. 1218 tests pass at a7acb21.
Request: mirror publish-complete.md to Notion (new page under the perturb-seq-eval subproject, beside the publish review), update the decision rows and the showcase row 3ed749bd250d8116bc04fa76cb812008 in place; reply with the completion page URL so I can hand it to the principal.
next_handoff: CTO reply with the Notion URL.
