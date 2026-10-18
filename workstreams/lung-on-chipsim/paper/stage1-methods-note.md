# A fix is verified against the thing that was changed, not against the property the claim names

**Short methods note — Stage 1 closure, lung-on-chipsim (ruling A4, approval-log row 65)**

**Author of record:** the principal (ratifies under the T8 pattern).
**Drafted by:** biofm/matthew-mo/cto, from `workstreams/lung-on-chipsim/qgr/stage1-closure.md`.
**Status:** DRAFT 2 — **content APPROVED by the principal 2026-10-18. NOT YET RATIFIED:** §4's own rule
requires every figure re-derived and the pin updated at the moment of ratification. Venue (§7) still open.

**Provenance of the approvals, disclosed because it cannot be verified from here.** The rulings arrived
**through the lung-on-chipsim agent's session** (dispatch #675), not through this one. The CTO cannot
independently confirm them, so they are applied as a **work instruction** and every change below is
reversible — the same treatment the agent gave a principal ruling it received through the CTO
(approval-log row 29). If any selection below is not what was chosen, say so and it is reverted.
**Draft due:** 2026-10-17 (row 65). **This draft: 2026-10-18 — one day late.**

**Pinned to:** `f2bb28c` (bioFM `main`) — **STALE AT RATIFICATION BY CONSTRUCTION**; re-pin then for this note's own text; the measured claims below are pinned
to the revisions named beside each one. Per §4, **every figure in this note must be re-derived at the
moment of ratification, and the pin updated**, or the note commits the defect it documents.

---

## 1. The claim

> **A fix is verified against the thing that was changed, not against the property the claim names.**

**At least ten** instances were recorded, dated, with named authorship — nine over four quality-gate
rounds on one branch between 2026-09-29 and 2026-10-02, and a tenth dated 2026-10-08 (§3.2). The
enumeration is a **floor, not a count** (§3.3): discovery here is reader-dependent, so the honest claim
is *at least* this many. The interesting property is not the count. It is that
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

**Instruments barely catch it.** Of the ten, **one** was first caught by an instrument, and that one
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
| **10** | **2026-10-08** | the repair commit `d271d80` itself | that the three named failures were fixed, and that the invocation no longer names two files | that the suite is run **whole**, and green | admitted 2026-10-18 (§3.2) |

Instances 1–6 are quoted from `paper/stage1-limitations.md` (pinned `ae894db`, measured 2026-09-29);
7–9 from `qgr/stage1-closure.md` (pinned `af17cd2`).

### 3.1 RULED 2026-10-18 — publish both predicates, each naming its subject

Row 65's "six introduced by repair" is **retired: it matches neither predicate.** The ruling is to
**publish both, distinguished**, because the two readings are different questions and collapsing them
is what produced three irreconcilable figures across the source records.

| predicate | count | rows |
|---|---|---|
| introduced by **a** repair | **7 of 9** | 2, 3, 4, 5, 6, 7, 8 |
| introduced by the repair of a **previously-enumerated instance** | **3 of 9** | 5, 6 (→ instance 4); 8 (→ instance 2, via C-3) |

Excluded, and why: **row 1** is a *creation*, not a repair. **Row 9** carries no repair attribution.
**Row 7** is excluded from the strict count only — its repair, **H-10**, is a *registered finding*, not
one of the nine: `qgr/deferred-findings-register.md:77` records it as "the one sentence stating the
citation scheme misresolved a row," and line 110 records this instance's chain, *"repaired under H-10
for this exact error, then re-broken by rows `#60`/`#61`; nothing recomputes it."* Traced to source,
not inferred.

**So §1 keeps "repair is one of its vectors" on 7, and §2 keeps "it survives its own repair" on 3** —
each sentence now carries the count that actually supports it.

An earlier draft of this section said "only 2 of instances 1–6 are strict." That was right for 1–6 and
wrong as a nine-wide figure: row 8 adds a third.

### 3.2 RULED 2026-10-18 — the tenth instance is ADMITTED

Dated **2026-10-08**, the commit date, not the discovery date. **The claim:** commit `d271d80`'s *"The
CI job now **runs it whole** instead of a scoped subset."*

Scoping was **re-expressed**, not removed — filename-scoping became marker-scoping, and
`-m "not network and not integration"` deselects 30 tests. The commit's own numbers say so: **436
passed / 0 failed / 5 skipped / 30 deselected.** The `integration` marker on the T4 test *predates* the
commit (`7275c8c`, an ancestor); `d271d80` added the **selector that excludes it**, then called the
remainder whole. Sharpest form: the comment the commit **deleted** stated the reason for scoping —
*"two need the DVC payload on disk"* — one of those two was fixed at its cause, the other was not and
fell inside the new selector. **It removed the sentence that named the problem and kept the problem.**

**Scope precedent, since instances 1–8 are paper claims and this is a commit message:** instance 9 is
the gate's timing command — instrumentation, not a published claim — so instrumentation is already in
scope. This one's dependent is larger: it is the standing statement of what CI gates, which every later
"the suite is green" inherits.

**A correction that is part of the evidence.** The finder's first formulation — *"the commit resolved
three others; this one it deselected"* — implied the T4 test was a fourth member of the set the commit
claimed to fix. **It was not**, and the finder corrected itself unprompted; those three are genuinely
fixed at their causes. Had it stood, a tenth instance would have entered this note resting on a false
claim, inside the note about claims resting on false verification.

### 3.3 RULED 2026-10-18 — the enumeration is a FLOOR, not a count

The tenth instance was surfaced by a question whose **premise was wrong**: the asker asked whether a
green test was *environmental*; it was *deselected*. An instance found by a mistaken question is still
an instance — but it is evidence that the others were found by the **same kind of luck**, not by a
method. §2 records that only one of ten was first caught by an instrument.

So this note claims **"at least ten"**, and says plainly that discovery is reader-dependent. It does
not publish a number as though the enumeration were complete.

### 3.4 The 2026-10-18 layer evidence — seven layers, two authors, one evening

Recorded per the ruling of 2026-10-18. All seven are the mechanism, none reached a published record,
and **none was caught by an instrument** — each was caught by the next reader, or by its own author
re-reading.

| # | author | the claim, and the subject it was actually verified against |
|---|---|---|
| 1 | agent | the DVC pointer "was never committed" — verified against the **path the assertion names**, concluded about **reproducibility** |
| 2 | CTO | accepted (1) — with the three real pointers **already present in the CTO's own earlier output** |
| 3 | CTO | "reproducible from the committed repository" — verified on the **ref in hand**, not the ref the claim was about |
| 4 | agent | the replacement recommendation — read a historical note about **S7's probes** as a description of **this test** |
| 5 | CTO | "the test is correct, no flat-path reference" — read the **plural r2.11 test** on one branch, concluded about the **singular test that failed** on another |
| 6 | CTO | "40 behind the trunk" — measured against a local ref **named** `main` that is 61 commits *ahead* of the published trunk |
| 7 | agent | caught pre-send: an `audit/` probe used `lung-on-chipsim/audit/` against the real path `chipsim/audit/`, yielding a false zero |

**An open predicate the author of record should rule, flagged rather than resolved.** Layer 7 is a
**pre-send self-catch**, and it is numbered. Two further pre-send catches by the same author were
**not** numbered. Those cannot both be right: either pre-send catches count — in which case the list is
longer than seven — or they do not, in which case layer 7 does not belong. §2's "the author re-reading
their own work" suggests they count. **This note does not choose**, because choosing it silently would
be §3.1's defect repeated on the layer count.

### 3.5 The one check that would have caught all of them

Approved into this note on 2026-10-18.

Every instance above, and every layer in §3.4, is a **correct reading of real evidence attributed to the
wrong subject**: the path an assertion names rather than the property it claims; the ref in hand rather
than the ref the claim is about; a historical note about one probe read as a description of another; two
refs sharing a name. **None was a misreading.** That is why no instrument caught any of them — an
instrument that checks *does the code say what you claim* passes every one.

> **The check:** every claim about a ref, a path or a probe must **name its subject explicitly**, so a
> reader can ask *"about what?"* of the claim itself rather than of its author.

§3.1's ruling is that check applied to this note's own headline figure — two predicates, each named,
each with its own count. It is the first use of the instrument **before** publication rather than after.

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
supported by **at least ten** dated instances with named authorship — a floor, not a count — obtained
at the cost of not shipping.

## 6. Inheritance

Thirty-six registered findings stand. A successor should **not** begin by repairing them: on this
branch's record, repair is how most instances arrived. Read first: **S-01, S-02** (they make the newest
instrument's verdict unreproducible from the repository), **S-06, S-07** (they let a failing run publish
a clean record), and **S-20** (R-10's deferral was taken at a smaller extent than now exists).

## 7. Open items for the author of record

1. **RULED 2026-10-18** — §3.1 predicate: publish both, 7 of 9 (any repair) and 3 of 9 (repair of a
   previously-enumerated instance); "six" retired.
2. **RULED 2026-10-18** — §3.2 tenth instance admitted; §3.3 enumeration published as a **floor**;
   §3.4 layer evidence recorded; §3.5 instrument adopted.
3. **OPEN — venue.** Row 65 reserved the venue choice for the draft. The approvals of 2026-10-18 did
   not touch it, and no grounded candidate list has been offered, so it remains genuinely open.
4. **OPEN — the §3.4 pre-send predicate.** Does a defect its own author catches before sending count as
   a layer? Layer 7 is numbered and two further pre-send catches are not; those cannot both be right.
5. **RATIFICATION IS NOT CONTENT APPROVAL.** §4's rule binds this note: at ratification, **re-derive
   every figure and update the pin.** That includes the route-distribution figures (published 59/63/46,
   re-derived 61/65/47 at `af17cd2` — both of which are now themselves stale), §3's counts, and the
   instance table. The pin on this draft is `f2bb28c` and will be stale the moment anything lands.

**Sources (all committed):** `qgr/stage1-closure.md`; `paper/stage1-limitations.md`;
`paper/stage1-methods.md`; `paper/stage1-claims-list.md` (41 rows / 35 supported / 6 CUT);
`paper/stage1-short-form.md`; `qgr/deferred-findings-register.md` (H-10 at :77, instance 7 at :110);
`plan/plan-approval-log.md` rows 58, 59, 61, 65; approvals rows 6-15; dispatch #675.
