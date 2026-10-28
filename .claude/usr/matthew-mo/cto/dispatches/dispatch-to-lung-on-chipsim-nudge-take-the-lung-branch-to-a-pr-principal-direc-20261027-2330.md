---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-27T23:30
status: created
priority: normal
size: task
subject: "NUDGE: take the lung branch to a PR — principal directed it 2026-10-27; run /pr-prep then /pr-submit, do NOT land"
in_reply_to: null
---

# NUDGE: take the lung branch to a PR — principal directed it 2026-10-27; run /pr-prep then /pr-submit, do NOT land

principal_direction: 2026-10-27, verbatim answer to "the lung branch's route to the trunk" — "nudge pr".
So the route is decided: the branch goes to the trunk through a receipt-gated PR, not a merge and not
a long-lived divergence. You run /pr-prep then /pr-submit. The CTO lands it. Do NOT land it yourself.

state_at_dispatch (re-derive before acting, these move):
  lung-on-chipsim local tip: 166f834
  ahead of origin/lung-on-chipsim: 714
  bioFM main: 43332c2 (JUST LANDED and pushed via PR #29 — fetch before you gate)

what the branch carries that matters:
  - 9140d3c  the 26 published P-gp verdicts (T14). yes=3 / no=0 / unknown=23. pgp_groups_usable FALSE.
  - 104f7fb  the T15 ordering fix (approvals row 58) + its regression test at tests/test_adjudication.py:378
  - everything after

three things to get right, each of which has bitten this workstream already:

1. THE GATE FIGURE. The CONFIGURED quality command is `cd projects/lung-on-chipsim && uv run pytest -q`,
   UNSELECTED. That is the gate. The selected figure (-m "not network and not integration") answers a
   DIFFERENT question and its 31 deselected tests are INSIDE the configured gate. Report both, labelled,
   and say which one you gated on. My own standing rule said otherwise for two days and was wrong twice
   over — there is also no GitHub CI on main beyond hacp-docs.yml.

2. `ty` IS SCOPE-DEPENDENT. `ty check chipsim` 25, `ty check tests` 31, `ty check .` 56 at last
   measurement. Report the scope with the number. A figure that names the wrong subject is the defect
   itself, and I published one.

3. THE IDENTIFIER SURFACE IS THE BLOCKING RISK ON THIS PR, not the tests. supmo668/bioFM is PUBLIC.
   `projects/lung-on-chipsim/configs/pgp_adjudication.csv` is TRACKED and its first column is
   canonical_inchikey. It is already committed at 9140d3c so this PR does not create the exposure — but
   state the position explicitly in your /pr-submit body rather than leaving a reader to find it:
   - the tracked projection carries NO `name` column and NO `snapshot_label` by design, so the forbidden
     (name, structure) pairing is not created by the file;
   - `configs/*.csv` is OUTSIDE the identifier gate until row 39's build lands on main — say whether
     row 39 is built on this branch, and if it is, that the gate now covers this file;
   - do NOT type a compound name into any cell to "clarify" anything (T14 r2.19).

ordering: /pr-prep (quality gate -> receipt) THEN /pr-submit (dispatches me the receipt + tip sha).
A receipt binds a gate to an exact diff, so re-gate if the tip moves after you receipt it.

what I will do on receiving your pr-submit: verify-pushed, receipt-verify by workstream (reading its
output before writing "verified", including whether the receipt is DERIVED from a parent gate), then
land. If the receipt does not match the tip I will send it back rather than land it.

note on scope: this PR is the branch's route to the trunk. It is NOT the occasion to fix the empty-group
limitation, re-open the P-gp aptness finding (row 48 ruled: keep the pre-registered axis, carry it as a
cited limitation), or invent a `no` verdict. If you believe something on the branch should not reach the
trunk, say so in the pr-submit body and I will rule on it before landing.
