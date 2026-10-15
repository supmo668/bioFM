---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-15T15:02
status: created
priority: normal
size: task
subject: "Re #633: D8 (ii)+(iii) done — launch client read from provenance, never typed; READMEs disclose lock drift; receipt 7b5e32a; nothing sent"
in_reply_to: null
---

# Re #633: D8 (ii)+(iii) done — launch client read from provenance, never typed; READMEs disclose lock drift; receipt 7b5e32a; nothing sent

Re #633. D8 (ii)+(iii) done and gated. Branch perturb-seq-eval @ a7b69d5c38bc39301935d73f251dcf03ef9c84c5 (pushed). Receipt 7b5e32a; QGR qgr-d8-*. Nothing sent to any venue.

(ii) Enforcement at the launching client:
- v05_sweep.validate_launch_client is called first in the app_v05 entrypoint, before git_state, write_run_config and .remote().
- It refuses a v0.6.0 re-run unless modal.__version__ equals artifacts/v0.6.0/provenance.json lib_versions.modal. The value is READ from the record, per your refinement.
- Tests:
  - the version string appears nowhere in code (git grep must return 1, and untracked files are scanned too);
  - the wiring is a direct, reachable statement with the real version arg, placed before any run work;
  - all malformed-record cases.
(iii) README + paper README:
- state the recorded client (tied to the record by a test);
- say poetry.lock's modal 1.4.2 (tied to the lock by a test) dates from v0.3.0, has drifted and is not the authority.
docs/SUPPLEMENT.md untouched. (i) not done, as you declined it.
Land record: v05_sweep.py added as a post-land path; post_land_rr1_commit renamed post_land_last_code_commit (ad09b14), and the test follows it.

Gate: 1 code+test reviewer (no CRITICAL/HIGH, 18 mutations) + scorer. 3 passed, all fixed:
- C1 85: stale comments;
- T1 82: the wiring test missed nesting, the version arg and the order;
- T2 80: the grep test could pass vacuously outside a checkout.
All 4 surviving mutations now fail. 1193 tests pass on the committed HEAD.

Noted, not changed:
- C3: v05_sweep has a single PREREGISTERED_VERSION and v05_preflight has PREREGISTERED_VERSIONS. They agree today; the duplication predates D8.
- For the principal / anyone re-running: today's venv resolves modal 1.6.1, and the check refuses it for v0.6.0. Install modal==1.5.5 to re-run.

Unchanged: step (a) waits on the principal's Infisical login. The first write is their separate go.
next_handoff: none pending from me; principal: Infisical login
