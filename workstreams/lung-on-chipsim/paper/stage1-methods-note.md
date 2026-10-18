# A fix is verified against the thing that was changed, not against the property the claim names

**Short methods note — Stage 1 closure, lung-on-chipsim (ruling A4, approval-log row 65)**

**Author of record:** the principal (ratifies under the T8 pattern).
**Drafted by:** biofm/matthew-mo/cto, from `workstreams/lung-on-chipsim/qgr/stage1-closure.md`.
**Status:** DRAFT 1 — **not ratified. One figure is unresolved (§3.1) and needs the author's ruling.**
**Draft due:** 2026-10-17 (row 65). **This draft: 2026-10-18 — one day late.**

**Pinned to:** `3a7f186` (bioFM `main`) for this note's own text; the measured claims below are pinned
to the revisions named beside each one. Per §4, **every figure in this note must be re-derived at the
moment of ratification, and the pin updated**, or the note commits the defect it documents.

---

## 1. The claim

> **A fix is verified against the thing that was changed, not against the property the claim names.**

Nine instances were recorded, dated, with named authorship, over four quality-gate rounds on one
branch between 2026-09-29 and 2026-10-02. The interesting property is not the count. It is that
**repair is one of the mechanism's vectors**: fixing an instance is itself an occasion for the next
one, because the fix is naturally verified against the thing the fixer just touched.

This note publishes the mechanism and its instances. It deliberately publishes **no claim that the
mechanism was solved**, because it was not: the branch closed at the scope reached, with no quality-gate
receipt, nothing pushed, and the branch not landed (approval-log rows 58 and 61).

## 2. Why this is a mechanism and not a list of mistakes

Three properties distinguish them.

**It survives its own repair.** Instances 5 and 6 were both introduced by the repair of instance 4 —
6 on the same day, caught before commit.

**It is indifferent to who is reasoning.** It was committed by the implementing agent, by its
reviewers, and by the coordinator who wrote the rule against it. Two instances were authored *while
their author was describing the mechanism in the same document*.

**Instruments barely catch it.** Of the nine, **one** was first caught by an instrument, and that one
only during the final gate, when `claims-vs-records.py` refused two numbers the author had just
written that no record emits. Every other instance was found by a **reader** — a reviewer, or the
author re-reading their own work. A 1,257-test suite was green across nineteen independent findings.

## 3. The instances

Each row states what was verified and what the claim named. The gap between those two columns *is* the
mechanism.

| # | date | introduced by | what was verified | what the claim names | disposition |
|---|---|---|---|---|---|
| 1 | 2026-09-29 | the **creation** of `redact-records.py` | that a refusal happened | *which* refusal | repaired 2026-09-30 (C-2) |
| 2 | 2026-09-29 | the **repair** of blocker 4 | that the marker carried `raises=` | that only the *registered divergence* is accepted | repaired 2026-09-30 (C-3) |
| 3 | 2026-09-29 | the **repair** of the round-1 scope finding | that `differences()` still reported a change | that each entry *is the digest of its own line* | deferred (R-05) |
| 4 | 2026-09-29 | the **repair** of the round-1 H4 finding | that the glob reached more files | that the measured surface covers *the classified scope* | repaired 2026-09-30 (C-1) |
| 5 | 2026-09-30 | the **repair of instance 4** | that H4 now cites the current record | that claims cite current records | repaired 2026-09-30 (H-7) |
| 6 | 2026-09-30 | the **repair of instance 4** (same day, pre-commit) | that the globs reached the classified roots | that the surface *equals* the scope | repaired same day |
| 7 | gate 9 | the repair H-10, for this exact error | that the figure was "recomputed from the log" | that it is recomputed *per run*, not once | re-broke itself |
| 8 | gate 9 | the repair C-3 | that a bare `assert` can no longer impersonate the divergence | that **nothing** can — a subclass or alias still can | class open (S-09) |
| 9 | gate 9 | — | `exit=0` after a pipe to `tail` | the exit status of the *suite*, which had been killed at 82% | reproduced one message later |

Instances 1–6 are quoted from `paper/stage1-limitations.md` (pinned `ae894db`, measured 2026-09-29);
7–9 from `qgr/stage1-closure.md` (pinned `af17cd2`).

### 3.1 UNRESOLVED — the repair-attribution count needs the author's ruling

Row 65 ruled that this note publishes "nine dated instances with **six** introduced by repair." I
re-derived that figure from the per-instance attributions rather than copying it, and **it does not
reconcile.** Three counts exist for the same attribution:

| source | figure | strict reading of the rows |
|---|---|---|
| ruling A4 / row 65 | **six** of nine "introduced by repair" | — |
| `qgr/stage1-closure.md` | **six** of nine "introduced by **the repair of a previous instance**" | only **2** of instances 1–6 are repairs of a previous *instance* (5 and 6) |
| `paper/stage1-limitations.md:220` | **four** of the six "introduced by those very repairs" | **5** of instances 1–6 are introduced by *a* repair (all but 1) |

The divergence is a **definitional** one, not arithmetic: "introduced by a repair" (5 of the first six)
and "introduced by the repair of a previous *instance*" (2 of the first six) are different predicates,
and the records use them interchangeably. Instance 1 is attributed to a *creation*, not a repair, under
either reading.

**I am not choosing the number.** Publishing an unreconciled count in this note would commit the
mechanism in the artifact documenting the mechanism — and `stage1-limitations.md` already records that
"the paragraph in this section *about* counts that drift carried three mutually inconsistent counts of
its own." The author of record rules the predicate; the figure is then **derived from the table in §3**,
not asserted, and re-derived at ratification per §4.

## 4. The contribution: an artifact that measures its own approval process must pin and re-derive

Stage 1's declared novel contribution was a measurement **of its own approval log** — the route
distribution over a contemporaneous, append-only, hash-locked revision table. It published 59
revisions / 63 rows / 46 standing-delegation. Re-derived with its own instrument at `af17cd2`:
**61 / 65 / 47**.

The two extra rows were written **by the adjudication of the report itself**: the scope ruling the
final gate requested, and the ruling *"Stop; the mechanism is the result."* Deciding whether to accept
the report changed the quantity the report published.

An earlier draft of the closure called this a fixed point — a claim that could not simultaneously be
true and approved. **That was an overstatement and was withdrawn**, and the withdrawal is part of the
finding. A claim pinned to a *commit* is stable against any number of later rulings. The real defect is
narrower and more useful: the figure was pinned to the **plan hash** `ae894db`, and rows 58–61 all
carry that same hash "(unchanged)", so **the pin could not discriminate.**

> **The rule:** an artifact that measures the process which approves it must pin its measurements to a
> revision **of that process**, and must re-derive them at the moment of approval. Choose an identifier
> that moves when the measured thing moves.

Stage 1 did neither, which is why its headline figure was two rows stale at the moment of its own
closure. §3.1 of this note is the same hazard, caught before publication rather than after.

## 5. What a reader should not conclude

- **Not** evidence that the Stage 1 mechanisms work. Instances were introduced by the very repairs
  those mechanisms authorise.
- **Not** evidence that the content guard is sound: its headline is qualified by ruling, two of three
  prohibitions are measured by nothing, the citation predicate is positively correlated with the
  violation it exists to expose, and the certifying gate can report `PASS` over a 69-file blind spot.
- **Not** a negative result about the people or the tooling. The same mechanism was committed by
  implementer, reviewers and coordinator alike.

What it **is** evidence of: *the family is open, it survives repair, and repair is one of its vectors* —
supported by nine dated instances with named authorship, obtained at the cost of not shipping.

## 6. Inheritance

Thirty-six registered findings stand. A successor should **not** begin by repairing them: on this
branch's record, repair is how most instances arrived. Read first: **S-01, S-02** (they make the newest
instrument's verdict unreproducible from the repository), **S-06, S-07** (they let a failing run publish
a clean record), and **S-20** (R-10's deferral was taken at a smaller extent than now exists).

## 7. Open items for the author of record

1. **§3.1 — rule the repair-attribution predicate.** Then the count is derived from §3, not asserted.
2. **Venue.** Row 65 ruled the venue is chosen *on the draft*; this is the draft.
3. **Ratification** under T8, which makes the note publishable and closes A4 — the last open Stage 1
   deliverable.

**Sources (all committed):** `qgr/stage1-closure.md`; `paper/stage1-limitations.md`;
`paper/stage1-methods.md`; `paper/stage1-claims-list.md` (41 rows / 35 supported / 6 CUT);
`paper/stage1-short-form.md`; `plan/plan-approval-log.md` rows 58, 59, 61, 65.
