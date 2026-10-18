# Stage 1 closure decision 2026-10-18 — one figure, one venue, one ratification

<!-- HACP L1 · Kind = Decision · Section = decision · Indexed by "ChipSim (bioFM) — Index".
     SOURCE OF TRUTH: the Notion row. This file mirrors it; see notion-map.json.
     Carries the three asks that close ruling A4 (approval-log row 65), plus two
     principal rulings recorded on 2026-10-18 (worktree drive point; retirement deferred).
     No identifier, biological number or chemical key appears on this page by design. -->

**Kind:** Decision · **Layer:** L1 · **Holds:** the three decisions that close Stage 1, and the two already ruled · **Reaches:** [the A4 draft](../../../workstreams/lung-on-chipsim/paper/stage1-methods-note.md), [the closure record](../../../workstreams/lung-on-chipsim/qgr/stage1-closure.md), [the retirement record](../../../workstreams/lung-on-chipsim/reports/2026-10-18-stage1-worktree-retirement.md)

## TL;DR — Stage 1 is one deliverable from closed, and it needs three answers

There is **no receipt to sign and no branch to land** — rows 58 and 61 ruled that. Row 59 closed the
last security referral. Exactly one deliverable is open: **ruling A4 (row 65)**, the standalone short
methods note. It is drafted. Three answers publish it.

| # | Decision | Status | Who |
|---|---|---|---|
| **D1** | The repair-attribution **predicate** — three sources give three counts for the same thing | **OPEN — blocks publication** | author of record |
| **D2** | **Venue** for the methods note (row 65: chosen *on the draft*) | **OPEN** | author of record |
| **D3** | **T8 ratification** of the draft | **OPEN** | author of record |
| D4 | Human drives lung work **only at `worktrees/lung-on-chipsim`**; `-stage2` kept, not human-driven | RULED 2026-10-18 | principal |
| D5 | Stage 1 worktree retirement **deferred until Stage 1 closes** | RULED 2026-10-18 | principal |
| D6 | Protection for the adjudication worksheet | OPEN, **re-dated — not urgent** | principal |

## D1 — the count does not reconcile, and this note must not publish it unreconciled

Row 65 ruled the note publishes "nine dated instances with **six** introduced by repair." Re-deriving
that from the per-instance attributions rather than copying it, **it does not reconcile:**

| Source | Figure it states | Strict reading of the instance rows |
|---|---|---|
| Ruling A4 / row 65 | **six** of nine "introduced by repair" | — |
| `qgr/stage1-closure.md` | **six** of nine "introduced by **the repair of a previous instance**" | only **2** of instances 1–6 qualify (5 and 6) |
| `paper/stage1-limitations.md:220` | **four** of the six "introduced by those very repairs" | **5** of instances 1–6 qualify (all but 1) |

The divergence is **definitional, not arithmetic.** Two different predicates are used
interchangeably, and instance 1 is attributed to a *creation*, not a repair, under either one.

**Why this is on a decision surface instead of fixed quietly.** The note's own contribution is the
rule that *an artifact measuring the process which approves it must pin its measurements to a revision
and re-derive them at approval.* Publishing an unreconciled count would commit the documented defect
inside the document — and `stage1-limitations.md` already records that the paragraph *about* drifting
counts "carried three mutually inconsistent counts of its own." So the draft leaves the figure
**derived from the instance table, not asserted.**

**The ask.** Rule the predicate:

- **(a) "introduced by *a* repair"** → 5 of instances 1–6. Widest, matches what the rows literally say.
- **(b) "introduced by the repair of a *previous instance*"** → 2 of instances 1–6. Narrowest, matches
  the closure record's wording but not its figure.
- **(c) Keep "six of nine"** and amend the two source records to agree — heavier, and it edits
  committed Stage 1 records.

Under (a) or (b), instances 7–9 are then classified under the chosen predicate **at ratification**, and
the published figure is whatever the table sums to. No figure is carried forward by memory.

## D2 — venue

Row 65 reserved the venue choice for the draft. The draft exists. The note is ~2 pages, methods-only,
with no biological result and no identifier content — so it is publishable as a standalone methods or
process note. Row 65 already **declined** folding it into the Stage 2 paper (it would wait on a result
that has nothing to do with it) and **declined** not publishing (it is the only publishable thing the
branch produced).

## D3 — ratification

The principal is **author of record** and ratifies under the T8 pattern. Ratification closes A4 and
with it Stage 1.

## D4 / D5 — ruled 2026-10-18

**D4 — the drive point.** Human-driven lung work happens **only in `worktrees/lung-on-chipsim`**. The
`lung-on-chipsim-stage2` worktree may be kept, but it is not a human drive point. Consequence worth
stating: dispatches #608 and #622 are Stage 2 directives sitting unread, and the Stage 2 agent is
**not** being woken while Stage 1 is open — they stay parked deliberately, not by neglect.

**D5 — retirement deferred.** The Stage 1 worktree stays until Stage 1 closes. The reason is
substantive: A4 is drafted *from* the Stage 1 record, so retiring the tree holding that record before
the deliverable is ratified puts source and draft on opposite sides of a destructive step. The
retirement record's §4 is marked deferred, and its measurements must be re-verified before it runs.

## D6 — the adjudication worksheet, re-dated

Measured 2026-10-18: the worksheet is a **blank 26-row scaffold** — 0 of 26 rows carry a verdict, an
evidence DOI, or an adjudicator. It is regenerable, so **today its loss costs a regeneration, not human
work.** I had previously described it as "the only critical-path human input"; that overstated it.

It becomes irreplaceable the moment a verdict is entered, and at that point it still has no git
tracking, no DVC entry (unlike the raw sources, which have one each), and no tracked export. The
project's own code anticipates exactly this: *"the tracked file … IS the surviving copy of that work:
keep it. There is no automatic recovery."* **Decide before entering verdicts, not after.**

---

**Provenance.** Rulings D4/D5 from the principal, 2026-10-18, verbatim: *"I will pick-up lung chip
worktree work only on lung-on-chipsim (not '-stage2', although it can be kept but human drives only at
the main worktree session)"* and *"can we approve stage1 first so worktree stays at lung-on-chipsim."*
D1 derived by the CTO from the committed records named above. Pinned to bioFM `main` `ef3a8ae`;
per the note's own rule, every figure is re-derived at ratification.
