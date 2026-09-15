---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-15T23:00
status: created
priority: high
size: task
subject: "Principal grill 2026-09-15: nine decisions. Plan of record stays r2.14 d83fceb until r2.15 is folded+signed. Your sequence after the hold lifts: gate pass -> stereo guard -> T4 -> records. T11 waits on PROVENANCE ratification; roster hand-off only after the guard lands"
in_reply_to: null
---

# Principal grill 2026-09-15: nine decisions. Plan of record stays r2.14 d83fceb until r2.15 is folded+signed. Your sequence after the hold lifts: gate pass -> stereo guard -> T4 -> records. T11 waits on PROVENANCE ratification; roster hand-off only after the guard lands

# Nine decisions from the principal's structured grill (session biofm-14, 2026-09-15)

Full text: `workstreams/lung-on-chipsim/grill-2026-09-15-r2.15-draft.md` at trunk `5147281`. It is a DRAFT amendment — **not folded into build-plan.md and not signed**. The plan of record remains **r2.14 at `d83fceb`**. The CTO session that holds the trunk when the second CTO session is closed folds it in as r2.15 and signs. Nothing below contradicts r2.11–r2.14; it sequences them.

## What binds you now

1. **One interactive session per tree.** The bare session on your worktree (pid 56186, ttys003, since 2026-09-09) is being closed by the principal; you are the sole writer. Until it is gone, the signing hold stands — do not attempt a receipted landing.

2. **Sequence after the hold lifts, each through its own gated commit:**
   (i) the **gate pass** on the 57 findings, replacing the halt-rule tautologies over `evaluate_halt`'s return value with tests that can fail — FIRST, because building on checks-that-cannot-fail repeats the fixture-vs-reality class;
   (ii) the **stereo guard** as ruled in r2.12 and amended by r2.13/r2.14 (`/t /m /s` only; relative-stereo `/s2` keyed stereo-free with the flag persisted);
   (iii) **T4** as amended in r2.11 (`dvc add` ×3; the test updates at `test_snapshot_fetch.py`, `test_provenance.py`, `test_scaffold.py`; verify `.gitignore` negations reach nested `*.tsv.dvc`);
   (iv) the two records — the C4 third-site note in `T8-review-record.md`, and `airway_evidence:` into the panel schema.

3. **T11 waits.** `PROVENANCE.md` will be CTO-drafted and principal-ratified+sealed (T8 pattern). A draft exists at `workstreams/lung-on-chipsim/PROVENANCE.draft.md` — deliberately NOT at `data/raw/drugbank/`, so an unratified file cannot satisfy T1's "exists". Do not copy it there. Do not draft your own.

4. **Roster hand-off only after (ii) lands.** Regenerate the disagreement report on guarded keys, then hand the principal the candidate list (schema `roster-schema.md`, validator S11a, `drugbank_id` carried alongside the key). That hand-off starts the principal's window: roster by working day 2, P-gp adjudication by working day 3. A slip is reported in the dev-log, never back-filled.

5. **Panel signing is decided: minisign at the M1 re-ratification**, when the three provisional faces are re-checked. Until then the run journal's provenance block and any card carry verbatim: "digest-sealed, human-ratified, not cryptographically signed."

6. **Approval provenance** now lives in `workstreams/lung-on-chipsim/plan/plan-approval-log.md` (append-only, 12 signs reconstructed). Once r2.15 is signed, the gate checks the newest entry's hash equals `plan-approval.md`'s.

## Corrections to standing lines
- Human artifacts absent: **three** (PROVENANCE.md, roster, P-gp adjudication). `theta_priors.yaml` is required absent by S6 — its absence is a pass.
- AM-6: resolved by ADR-0002; the count-check waits for real M0b records.
- The TTY gate is already a confirmation read (E-4); no work there.

Reply with the gate-pass finding set location when (i) starts — no QGR currently records the 57.
