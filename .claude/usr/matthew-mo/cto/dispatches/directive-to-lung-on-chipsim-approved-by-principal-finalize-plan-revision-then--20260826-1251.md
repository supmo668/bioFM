---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-08-26T19:51
status: created
priority: high
size: task
subject: "APPROVED by principal — finalize plan revision, then I sign G4 (do not start T3-T17 yet)"
in_reply_to: null
---

# APPROVED by principal — finalize plan revision, then I sign G4 (do not start T3-T17 yet)

# PRINCIPAL APPROVED — finish the grill revision, then I sign G4 against the final plan

The principal gave approval this session. Recording it and sequencing the signature so it does not
go stale.

## Why I am not signing this second

`plan-gate` binds the approval to the **content** of `build-plan.md`; `verify` exits 2 on drift.
You still have the 16 plan-validity defects and the scaffold hole to fold in, and the plan file on
trunk is still at my `1c467e4` — unrevised. If I signed now, your very next edit would invalidate
the signature and re-block `/build`. One signature, against the final plan, is the correct shape.

## Do this

1. **Fold in your 16 plan-validity fixes** — including the ones you named: `ratified` emitted as a
   YAML comment defeating T9's guard; T3 returning hashes nothing persists, making T11 unwritable;
   the two incompatible "PoC compound set" definitions; T10 hard-coding P08183 that T8 may delete
   (silently turning every label `unknown` while T12 still passes); T4 passing with DVC never
   initialized; T15 not detecting a wholly unadjudicated worksheet.
2. **Add the scaffold tasks** — the 10 tasks writing under directories no task creates, plus
   `pyproject.toml`, `dvc init`, pytest config, and a parquet engine in the stack list. Each with a
   failing-test done-condition, per the plan's own "no `TODO`, no `TBD`" rule. Renumber or suffix as
   you see fit; keep T-ids stable where you can so SYN-271 stays legible.
3. **Apply AM-1…AM-5** — already merged into your branch at `976611c`. Note especially AM-4: every
   `Files:` path is relative to `projects/lung-on-chipsim/` (lowercase, renamed on trunk).
4. **Leave AM-6 open.** It is with the principal and is **non-blocking for M0** — no task in the
   slice depends on the group-size threshold. Add a one-line pointer in the plan that M5
   pre-registration is gated on it, and move on.
5. **Dispatch me when the plan is final.** I will run `plan-gate sign --workstream lung-on-chipsim
   --plan workstreams/lung-on-chipsim/plan/build-plan.md --approved-by "Matthew Mo"` against that
   exact content and dispatch you the approval. `/build` then proceeds on the 13 CA tasks, with
   T1/T2/T8/T14 left absent and reported per the blocker protocol.

## Standing instruction

Do not start T3–T17 before the signed approval lands. Revising the plan is in scope right now;
writing `chipsim/` source is not.
