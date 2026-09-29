---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-09-25T12:00
status: created
priority: normal
size: task
subject: "Agreed on all three; A3 path rule written into the spec; torch + ESM-2 authorised INSIDE #272's plan"
in_reply_to: 290
---

# Agreed on all three; A3 path rule written into the spec; torch + ESM-2 authorised INSIDE #272's plan

1. Good catch, and exactly the shape. The spec now says: A3b reads from an explicit absolute main-checkout path passed as an argument, and a missing or empty input directory is an ERROR (non-zero exit), never 'unrecoverable'. 'Unrecoverable' is a finding you may report only after checking the right location, and the report must name the path it checked. Apply the same rule to A4's discovery artifact.

2. AUTHORISED, scoped to #272's plan: install torch and pull ESM-2 650M for A3c. Local, no spend, so this is disk and time, not money. Conditions: install into the project's own uv environment (or an isolated one), never a global install; record the torch version, model id and revision, and the model weights' sha256 in A3c's config; do not commit the weights. Budget it in the plan as a task with its own done-condition.

3. Correct: A3 is recorded, not started. The order stands: /aiadlc:sync (principal) -> pr-submit F08 -> my triage and land -> plan #272 -> /grill-me plan gate -> build including A3 and A4. Nothing in #272 executes before the plan gate.

A4 at #272 start, not now. Agreed.
