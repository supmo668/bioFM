## Stage 2 unblock — principal grill 2026-10-04 (twelve rulings, structured 1B1)

Decisions are the principal's; wording is the agent's. Route per the convention of approval-log
row 70: the grill ran as a structured 1B1 in Claude session
`session_0181c6Cgx1w4D61dgPg73r7f` (https://claude.ai/code/session_0181c6Cgx1w4D61dgPg73r7f) and
closed with the 1B1 lock, verbatim: **"Over and out"**. Each item records the option the principal
chose and the alternatives declined, so a third party can resolve the route without this session.

**This file is a DRAFT amendment. It is not folded into `build-plan.md` and not signed.** The plan
of record is unchanged. The lane-owning CTO session folds these as `r3` and signs; the rulings are
carried into `plan-approval-log.md` as numbered rows at that point. Nothing below adds or removes a
task, and nothing below writes a biological number.

Items marked *(ruling)* change what the plan requires; *(confirmation)* accepts a date or an
existing ruling without changing the plan text.

---

**A1 · Successor code base for Stage 2** *(ruling)*
Stage 2 builds on a **successor branch cut from `main`**, with the science-bearing files brought
over **by content** from `origin/lung-on-chipsim` (`c04e701`) and the archived tip: the roster, the
three DVC pointers and `SHA256SUMS.json`, the parquet sidecar, `label_structure_reference.yaml`,
`unparseable_compounds.yaml`, `harmonize/{label_reference,merge_report}.py`, `audit/`, the T13
worksheet CLI and its tests, the S13/S14 templates, and `transport/` once A2 makes it reachable.
`guards/`, `record_content.py`, `tests/shape_scan.py` and the E-21…E-23 evidence tooling are
**excluded**: that work item closed with 36 registered findings and the successor guidance is *do
not open by repairing the register*.
Declined: landing the whole archived branch (it carries the failed-gate machinery and the five
withheld files onto a public trunk); restarting from `main` alone (it loses 29 gated tasks).
The CTO cuts the branch on the r3 signature, after the read-only `scan-artifacts.py` pass.

**A2 · The archived tip is pushed** *(ruling)*
The principal pushes the archived Stage 1 tip to `archive/lung-on-chipsim-stage1` on `origin` by
**2026-10-06**. It holds the only copy of `transport/{ode,fit,prior,theta}.py` (~920 lines). Until
the ref resolves, A1 can take everything except `transport/`, and the M1 smoke run cannot be
scheduled.
Declined: cutting A1 first and adding `transport/` later (it moves the M1 fit by the delay);
leaving the tip on one disk (the Stage 1 code becomes unrecoverable).

**A3 · The five withheld record files** *(ruling)*
They **stay on the archived branch**; the gap stays recorded in `qgr/2026-10-01-cto-disposition.md`.
Nothing is redacted and nothing is published. The 78-of-83 record on `main` is the record.
Declined: redact-then-publish (it spends the principal's time on hash-covered evidence for no
reviewer benefit); deferring the decision past A2.

**A4 · The Stage 1 closure is published** *(ruling)*
Yes, as a **standalone short methods note**: the mechanism (*a fix is verified against the thing
that was changed, not against the property the claim names*), its nine dated instances with six
introduced by repair, and the pinning rule that an artifact measuring the process which approves it
must pin to a revision and re-derive at approval. The CTO drafts it from `qgr/stage1-closure.md`;
the **principal is the author of record** and ratifies under the T8 pattern. Draft by **2026-10-17**;
venue chosen on the draft.
Declined: folding it into the Stage 2 paper (it would wait on a result that has nothing to do with
it); not publishing (it is the only publishable thing the branch produced).

**B1 · T14 adjudication date** *(confirmation)*
**2026-10-14** accepted: 26 verdicts, each with an evidence DOI, over the approved roster. The
r2.15 item-7 window (three working days from hand-off) is superseded for this item by the fixed
date, so the week-1 exit condition is dated rather than relative.

**B2 / B3 / B4 · The remaining human entries** *(confirmation)*
**2026-10-14** accepted for all three: the six θ fields with citations (four citable now, two as
`assumed: true` with stated widths), the `(α, k_sink)` transport prior with its source, and 3–8
reference compounds with published on-chip ordering. The agent emits the typed templates and their
validators in week 1, immediately after A1; the principal fills them.
Declined: a later date for T21 alone; setting each date at template hand-off.

**B6 · M0b curation shape** *(ruling)*
The **principal curates alone**; no second curator is named. The record schema, its validator and
the sealed-allocation tool are written and gated **before the first record is curated**, and the
three-way allocation is sealed before any record is read (ADR-0002). The 3–4 week figure stays a
**planning assumption**; it is replaced by the measured minutes-per-record after the first ten.
Declined: a named second curator; deferring M0b behind the M1 smoke run.

**B8 · The evaluator freeze** *(unchanged)*
The signature comes before any fit on real records. No change.

**C1 · SLC15A1** *(ruling)*
**Kept** under the T8 deletion criterion: contested in the literature is not positive evidence of
absence. It is re-checked **with the three provisional faces at the M1 re-ratification**, with a
citation, before the panel is cryptographically signed (minisign at M1, per r2.15 item 5). The
ratified `barrier_panel.yaml` does not change before Stage 2 entry.
Declined: revisiting now with a citation; dropping it from the panel.

**C2 · The AM-6 residual** *(ruling)*
**Struck as superseded by ADR-0002.** The module README's recommendation to evaluate the two-group
veto only at ≥30 points per group goes in the C4 regeneration; the count check happens against real
M0b records, as r2.15 item 8 already states.
Declined: pre-registering the contingency; leaving it open until counts exist.

**C3 · Retroactive scope of the identifier constraint (item H)** *(ruling)*
**Row 59 closes item H.** No other pre-existing site needs a ruling: the CTO's read-only
`scan-artifacts.py` pass at the archived tip reported `shapes_on_audit_surface: 0`, and row 59
already ruled that PubChem citation of canonical chemistry is the sanctioned form.
Declined: a further per-site pass over `main`.

**Floor placement** *(ruling)*
The HACP floor under `docs/hacp/lung-on-chipsim/` is **merged to `main` by the CTO**; no pull
request is opened from an agent session. Every `Local path` on the ChipSim Notion rows resolves
once it lands. Until then the floor lives on `claude/inspiring-archimedes-h0we1b` and the weekly
sync routine falls back to that branch.

---

Recorded for completeness, not re-ruled: the T18 roster approval of 2026-10-03 (26 entries, final)
still owes its signed approval-log row; the CTO's clean suite re-measurement is still owed at A1 cut
time (453 s clean against 900 s killed under 23 concurrent pytest processes, not comparable); and
`PROVENANCE.md` stays human-authored, r2.15 item 1 having been declined by the principal.
