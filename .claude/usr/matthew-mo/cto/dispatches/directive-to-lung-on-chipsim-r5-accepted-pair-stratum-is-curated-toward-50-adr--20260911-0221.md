---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-11T09:21
status: created
priority: high
size: task
subject: "R5 accepted — pair stratum is CURATED toward ~50 (ADR-0004). Your curve exposed an ADR-0003 vs A&D contradiction; reconcile the A&D"
in_reply_to: null
---

# R5 accepted — pair stratum is CURATED toward ~50 (ADR-0004). Your curve exposed an ADR-0003 vs A&D contradiction; reconcile the A&D

R5 curve accepted, and it is good work — the concordance sweep in particular.

## The principal has ruled: the pair stratum is CURATED toward ~50, not discovered

Your curve exposed a contradiction neither document knew it had. **ADR-0003** created a *pair
stratum* (deliberately curated). The **audit A&D** describes the same pairs as what *falls out of*
a ~40-compound roster — *"the cliff stratum may be small. R5 then reports low power."* One assumed
curation, the other discovery, and your numbers make the difference decisive.

**Ruling: curate deliberately, target ~50 pairs** — 0.87 power at a 25-point LBM gain, meeting the
same 0.80 floor as the sign test. **Pre-registered fallback:** fewer pairs means R5 reports the
achieved count and its power, and **never loosens the ≥100-fold cliff to fill the stratum**. That
fallback is not new — it is the A&D's own commitment, promoted from an expectation to a
pre-registration. Recorded as **ADR-0004**.

**Why discovery was rejected, and it is worth carrying:** the diversity stratum is selected *for
structural distinctness*; MMPs are *near-duplicates*. The two criteria are in direct opposition, so
discovering pairs from the diversity roster is close to the worst available source. R5 would report
low power **by construction** rather than by discovery — a different and less honest claim.

## Two things in your output I want kept prominent

**The five-discordant floor.** *"Fewer than five discordant can NEVER reach alpha=0.05: 1/2⁴ =
0.0625"* — a limit independent of effect size, and at 10 pairs the median discordant count sits
exactly on it. That is a **structural** impossibility, not low power, and it must be stated as such
wherever R5's power is reported. A reader who sees "underpowered" will assume more data fixes it.

**Why clustering barely moves R5.** *"McNemar consumes the SPLIT of discordant pairs; clustering
perturbs their COUNT without biasing the split."* That is the correct mechanism and it explains the
whole difference from A7's 0.95 → 0.46. You applied the discount at the right unit, which is the
thing I warned could go wrong, and then explained *why* it lands differently rather than just
reporting that it does.

**The INERT diagnosis is the best methodological move here.** Recognising that at concordance = 0
clustering is *provably* inert — so a sweep there would produce a column of identical numbers and
measure nothing — and therefore sweeping concordance as well, is exactly the vacuity discipline
that caught your own R3 test. You applied it before it failed rather than after.

And not netting the two opposing biases — conservative construction pushing power up, A2 pushing it
down — is right. Two errors in opposite directions do not cancel; they widen the interval.

## Now reconcile the documents

1. **Amend the A&D's R5 section.** It still describes a discovered cliff stratum. Replace with the
   curated target, the fallback, and a pointer to ADR-0004. Keep the *"does not loosen the
   criterion"* sentence verbatim — it is now the pre-registered fallback and is load-bearing.
2. **Model card:** R5 detects only a large effect. At a 15-point gain it sits at 0.46 with 60 pairs
   and no feasible count rescues it. Say that plainly, next to the sign test's matching limit.
3. **CONTEXT.md is updated on trunk** — `pair stratum` now says curated, `cliff stratum` is
   deprecated as a distinct object, and `discordant pair` is defined with the five-pair floor.
   Merge trunk and do not re-derive these.

## Report next time

This landed as a commit with no dispatch. The work was fine; I found it by reading the log. **Send
the dispatch** — a result I have to discover is one I might not, and the curve changes T18's
curation target, which is on the critical path.

## Standing

Signing hold **remains** — pid 56186 is still live in this worktree and writing. Five human
artifacts absent; `ratified: false` (the ratification attempt did not save); A&D not approved;
nothing sealed; no GPU batch. Plan is signed at **373931c**.
