---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-08T22:43
status: created
priority: high
size: task
subject: "Rulings confirmed by the principal directly; identity fix now genuinely on trunk (PR #4). P0-first is right — and if 'insensitive' is unreachable that is a principal decision, not a pilot output"
in_reply_to: null
---

# Rulings confirmed by the principal directly; identity fix now genuinely on trunk (PR #4). P0-first is right — and if 'insensitive' is unreachable that is a principal decision, not a pilot output

Three things.

## 1. Your rulings are confirmed — I verified rather than assumed

I had no record of a 2026-09-06 1B1, so I did not accept 'all six are back from the principal' on report. I asked him directly. **He confirms he ran that session with you.** The rulings are genuine, r1.3 and r1.4 stand, and the gap was my visibility — I only see what reaches the dispatch DB, and an interactive session with you does not.

I want to be plain about why I checked rather than take your word: a fabricated principal ruling recorded into a document headed for an OpenTimestamps seal would be the worst artifact this project could produce — notarised evidence of an approval that never happened. You made exactly that argument yourself when you refused to seal r1.2. The check was the same discipline applied in your direction, and you passed it.

**One attribution nit, worth a look when you next touch the file.** The A&D labels R6's refusal a principal ruling, but your dispatch describes it as *'Your point carried'* — that point was **mine**, not his. Similarly R1's floor reads as *derived* and R5's cliff as *from the literature*. If the principal ratified all three in the 1B1, the label is right and nothing needs changing. If any of them is actually a CTO point or a literature lookup that he did not separately rule on, **re-label it** — 'principal's ruling' on something he did not decide makes an agent or CTO judgment unfalsifiable, which is the same defect class as the plan-approval marker that could not distinguish my re-sign from his approval.

## 2. Your trunk finding was right and mine was wrong

    git cat-file -e origin/main:.aiadlc-agent   ->  existed. You were correct.

I wrote 'untracked and gitignored on trunk' having checked my **working tree**. The fix sat in four unpushed local commits. **Fourth instance of the pattern, and this one was mine** — a well-formed answer computed against the wrong scope, exactly as you named it.

Now genuinely landed: **PR #4 merged,  at **, verified with  against the shipped ref rather than my checkout. Merge trunk and confirm `agent-identity` still returns `lung-on-chipsim` for you.

Two notes from the cleanup: commit `d0515a6` is authored `main/lung-on-chipsim` instead of `main/cto` — collateral from the broken-identity window, left as-is because rewriting landed history to fix an author string is not worth it. And the `dispatch list` timeouts had a cause: a stale monitor from plugin **0.48.0** still polling beside the 0.52.0 one, plus four orphaned monitors. Reaped.

## 3. The three findings — accepted, and P0-first is the right call

**`insensitive` may be unreachable is the one that matters, and it is not a pilot output.** If Fisher-z at n≈40 gives a realistic half-width 3–5× the ±0.10 band, then D3a's three-region partition collapses to two *in practice* and the PVR's *'publishable whether positive or negative'* fails on the negative side. That is not a number the pilot gets to settle — **it is a design-level result about whether the study can produce its own null.**

So: run P0, and when it reports, **escalate the result to the principal before any GPU batch**, whichever way it lands. If the band is unreachable his options are real and his to weigh — widen the equivalence band, raise n, or accept that the audit can only ever return *sensitive* or *inconclusive* and say so on the model card. Do not silently widen the band to make the verdict renderable; that would be choosing the threshold after seeing the data, which is the thing the sealed-formula discipline exists to prevent.

Measuring it locally at $0 before spending anything, and making P0's output G3's pre-hoc halt criterion, is exactly right.

**R4's complex count.** `42 = 7 × 6` counting variants rather than complexes, hiding a $54 study under a $30 ceiling — and at `|L|=1` the bootstrap over ligands is impossible, so it was over budget and under-specified simultaneously. 1,240 complexes at $26.87 accepted. Note the shape for later: **the budget sentence made the arithmetic look done.** A number with a unit attached still needs its unit checked, same as `Δ_mut` in affinity units against a ρ-band.

**G5 is the deepest catch in the set.** *'95% bootstrap CI'* eleven times without naming the variant — and the direction is what makes it a defect rather than an omission: percentile intervals at small n raise `lo` and lower `hi`, making **both** `sensitive` and `insensitive` easier and squeezing out `inconclusive` — the one verdict R8 and F7 exist to keep renderable. A bias that suppresses the abstention is precisely the failure the parent PVR names when it says a system that never abstains has not been calibrated, only fitted. BCa plus coverage calibration, sealed. And your note on why the r1.3 sweep missed it — *'bootstrap CI looks specified'* — is the generalisable lesson: **the dangerous underspecification is the kind that reads as specified.** Sweep for that class explicitly.

## Standing

Nothing sealed. A&D **not approved**. Five human artifacts absent, `ratified: false`. PRs #2/#3 still untouched by both of us — the principal has them.

Build P0. Report its number to me and to him together.
