---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-11T09:25
status: created
priority: normal
size: task
subject: "A&D r1.7 at aec3b54 — ADR-0004 reconciled, both card limits paired, five-discordant floor stated as structural. Dispatching this time"
in_reply_to: null
---

# A&D r1.7 at aec3b54 — ADR-0004 reconciled, both card limits paired, five-discordant floor stated as structural. Dispatching this time

# A&D r1.7 — ADR-0004 reconciled, card limits paired, at `aec3b54`

Dispatching this time. Your note was fair: the R5 curve landed as a commit with no
dispatch, and a result you have to discover is one you might not. Both deliverables
below are pushed and this is the report, not the record of it.

## 1. A&D R5 amended to the curated stratum

The discovery language is gone. In its place: curated toward ~50 pairs, **0.87** at
a 25-point gain, the same 0.80 floor the sign test clears, with a pointer to
ADR-0004.

Your rejection reasoning is carried verbatim because it is the part that will be
questioned later — **the diversity stratum selects FOR structural distinctness and
an MMP is a near-duplicate by construction**, so harvesting pairs from the diversity
roster is close to the worst available source, and R5 would then report low power
*by construction rather than by discovery*. That is a different and less honest
claim than the fallback sentence makes, which is exactly why the two documents
disagreeing mattered.

The fallback is kept **verbatim** as you asked, now labelled a pre-registration
rather than an expectation: *"it does not loosen the criterion to fill the
stratum."*

## 2. The card carries both limits, side by side

Not in separate sections — separating them lets a reader assume one covers the
other:

- **R3 / sign test** — can demonstrate moiety-sensitivity but **never its absence**.
- **R5 / cliff test** — detects only a **large** effect: **0.46 at a 15-point gain
  with 60 pairs**, and no feasible pair count rescues it.
- **R5's structural limit** — fewer than **five discordant** pairs can never reach
  `α = 0.05`. At 10 pairs the median discordance sits *exactly* on that floor.

And the binding sentence: **the card must not report a null from either arm without
the matching limit beside it.** Your framing is the one I used — a reader told
"underpowered" assumes a bigger roster fixes it, and here it does not.

## 3. Two opposing biases, recorded as not-netting

Independent-errors construction is **conservative** (shared difficulty *raises*
power, 0.70 → 0.98 at 40 pairs, by stripping symmetric noise out of the discordant
split). A2 pushes the other way. **Two errors in opposite directions widen the
interval; they do not cancel** — recorded in those terms so nobody later reports a
single point estimate as though the two had been reconciled.

## 4. Merged trunk — and ADR-0004 was unpushed again

`worktree-sync` reported "already up to date" because it merges `origin/main`, and
**`96f6e75` (ADR-0004 + the CONTEXT.md glossary) was on local `main` only**. Merged
it explicitly. Fourth occurrence of this shape — the artifact is reported as landed
while sitting in an unpushed local commit, and the sanctioned sync path cannot see
it. Not re-deriving the glossary, as instructed.

Also noting the plugin moved to **0.54.0** mid-session and its `block-raw-tools`
hook now refuses compound commands containing `git checkout`, including
`git checkout -- <file>` on an unrelated path. Not a complaint — the rule is right —
but it blocked a merge that had nothing to do with trunk, so the matcher may be
wider than intended.

## Standing

81 tests, ruff clean. Signing hold stands. The gate is still **NOT CLEAN** — 57
findings from the three-reviewer pass, and the two that need decisions rather than
code are unchanged: the budget priced at 90/GPU-h against a mandated 80
(**$30.22** against a $30 ceiling), and **ADR-0003's floor halting the study
unconditionally when applied per tier** (cross-family n=20 tops out at 0.664).

Five human artifacts absent, `ratified: false`, A&D not approved, nothing sealed,
no GPU batch.
