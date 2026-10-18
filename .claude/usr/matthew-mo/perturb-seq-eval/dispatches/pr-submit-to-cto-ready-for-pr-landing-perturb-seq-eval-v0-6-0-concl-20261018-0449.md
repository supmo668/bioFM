---
type: pr-submit
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-18T03:49
status: created
priority: normal
size: task
subject: "Ready for PR landing: perturb-seq-eval — v0.6.0 conclusion (published records, tooling, HACP)"
in_reply_to: null
---

# Ready for PR landing: perturb-seq-eval — v0.6.0 conclusion (published records, tooling, HACP)

branch: perturb-seq-eval
sha: e27eeba (pushed; origin/perturb-seq-eval == HEAD; 0 behind origin/main)
diff-hash: 7ba0ff9 (vs origin/main)
receipt: workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-bioFM-qgr-pr-prep-20261018-0449-7ba0ff9.md (pr-prep, derived from AV-1 8795772; receipt-verify OK)
scope: perturb-seq-eval v0.6.0 conclusion — publication tooling (Zenodo/Figshare revision path, availability gate), published records (publish.state.v060.json, CITATION.cff with both DOIs, CHANGELOG [0.6.0] 2026-10-16), HACP pages (publish review, completion review, decision log) and the research showcase. 63+ commits.
draft: false
migrations_pending: []
tests: 1218 passed on 1ae73e4 (tip adds only the QGR/receipt); fill_v060_numbers --check matches.
disclosed: C3 (duplicate pre-registered version constant) declared as a known gap in CHANGELOG, principal 2026-10-18 (fixing would amend the land record); ruff 0.17 in the rebuilt venv reports pre-existing lint that main also fails, CI does not run ruff.
CTO action: /pr-cto-land perturb-seq-eval (principal types it in the main checkout; versioning per your call, prior lands used --no-release). After land, dispatch me to self-retire the worktree.
next_handoff: CTO master-updated dispatch.
