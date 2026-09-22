---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-22T08:26
status: created
priority: normal
size: task
subject: "r2.36 landed: build M1 (S13, T22-T27) against fixtures; also run T13 for real (T18 is resolved)"
in_reply_to: null
---

# r2.36 landed: build M1 (S13, T22-T27) against fixtures; also run T13 for real (T18 is resolved)

Two independent pieces of work, neither blocking the other.

## 1. T13 — run it for real, T18 is resolved

T18's roster is finalized at 26 entries (configs/poc_compounds.yaml, e59cb3d..HEAD on this
branch, content verified byte-identical). T13 (write_adjudication_worksheet) is CA and its
gate has cleared. Run it for real against the live roster, not a fixture.

Use the approve-on-execute gate honestly: `--yes` (recorded as flag-approved, not human --
tests/test_run_approval.py already asserts this distinction). Produce
data/interim/pgp_adjudication.csv so it's ready for the principal's T14 review (60-90 min,
cannot be delegated -- don't attempt it, don't pre-fill anything beyond the generated columns
T13 itself computes).

## 2. M1 scaffold -- r2.36, build-plan.md Sec 6a (commit 39e188e on main, hash 7f57023)

New plan section: S13, T22-T27 (7 CA tasks) for the ODE core. T20/T21 (H -- literature theta
priors and published-on-chip reference compounds) are new human blockers, same shape as
T1/T2/T8/T14/T18 -- escalate them, don't simulate them, same as always.

S13/T22-T27 do NOT need T20/T21's real values to proceed -- same "Every CA done-condition must
be evaluable without a human artifact" rule as the rest of this plan. Build and test against
fixtures; the live-data check is a separate deferred integration condition, reported at the
T20/T21 boundary same as any other H-gated task.

Read Sec 6a in full before starting -- it's a first pass (same standing as M0's own r1), written
from the A&D spec before any M1 implementation exists to push back against it. I expect it to
earn defects the way M0 earned 33. Say so at the boundary rather than silently working around
anything that doesn't hold up once you're actually building it.

One scope note already in the plan text, repeating it here because it's exactly the shape of
mistake this plan's revision log (defect 3) already made once: T21's reference-compound set is
NOT T18's roster. T18 is lung-relevance/P-gp evidence; T21 needs compounds with an independently
published on-chip transport measurement. Don't default T21 to a subset of T18 without checking
each one actually has that literature backing.

M2-M6 are intentionally NOT in scope -- Sec 6b stubs them, blocked behind the ChEMBL/BindingDB/
TDC ingestion plan and M0b curation per the plan's own standing Sec 8 ruling. Don't get ahead of
that ruling.
