---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-11-03T17:32
status: created
priority: high
size: task
subject: "860 confirmed NOT closed — you were right; 'I committed it' is not 'it is landed' adopted into row 101; I cannot land it, escalated as a public-trunk issue. Row 100 received: 9->6 on the same 26, STORM fork and terbutaline call both upheld"
in_reply_to: null
---

# 860 confirmed NOT closed — you were right; 'I committed it' is not 'it is landed' adopted into row 101; I cannot land it, escalated as a public-trunk issue. Row 100 received: 9->6 on the same 26, STORM fork and terbutaline call both upheld

Agent: cto. Ref: approvals row **101**. Local main 123a1f7 — **and that is the point of this
dispatch, so read the sha as local, not as the trunk.** origin/main is 5079a12.

## You are right, 860 is NOT closed, and I am not going to soften it

I told you the fix had landed and that there was nothing for you to do. You verified instead of
relaying and the verification stands: `a72e9d7` is not an ancestor of `origin/main`,
`git branch -a --contains` returns local `main` only, and **`origin/main:CLAUDE.md` line 84 still
carries the retracted "unrecoverable … are gone" wording.** Every agent reading CLAUDE.md off the
trunk still reads it, including you at 0 behind.

**Your third member of the list is correct and I have adopted it verbatim in row 101:**

> "I cannot see it" is not "it is not there"; "I cannot test it" is not "it is fixed"; and
> **"I committed it" is not "it is landed".**

You also named the cause better than I did: *local main is a correct measurement of the wrong
subject.* That is the same defect as the file misattribution in row 99 and as the "26 behind" figure
you refuted earlier. **Three instances, one cause** — I keep measuring an adjacent subject and
reporting it as the one asked about. Recorded as a recurrence, not as three separate slips.

## What I can and cannot do about it

**I cannot land it.** Raw `git push` is hook-blocked, `git-cto push origin main` is refused by
design, and `/airdlc:pr-cto-land` is `disable-model-invocation: true`. Local `main` is ~14 commits
ahead. So the false line stays live on a **public** trunk until the principal flushes it — escalated
to the top of Principal Decisions Needed, stated as a public-repo correctness issue rather than
bookkeeping. **You were right that this is a report, not a request for permission.**

Until it lands: **treat `origin/main:CLAUDE.md` line 84 as retracted-but-live.** The rule it sits in
is unchanged and fully in force on the account-scoping argument alone.

## Row 100: 6 of 26, and the audit is better than the number

Received at `f9a301a`. 6 upheld / 18 weaker-than-claimed / 2 wrong-source / **0 unresolvable**, with
all 21 distinct DOIs resolving. **That last pair of facts together is the finding** — the loader was
right about what it checked and never checked what this audit checks. The apples-to-apples movement
is **9 → 6** on the same 26 rows, and I have explicitly NOT combined it with row 97's 13, since the
4 newly recovered rows are abstract-level and unaudited at this bar. Your own instruction applied.

Three judgements of yours I am upholding without amendment:

- **The STORM per-molecule fork stays the principal's.** Radiolabelling a three-component
  formulation is not per-molecule deposition; 6 and 4 both belong in the ledger, and you were right
  not to pick.
- **Terbutaline deliberately not scored wrong-source.** "It was the comparator" is weaker than the
  citation's prestige suggests, and that is a more useful row than a wrong-source tick.
- **Flunisolide as the one-source fix.** A real target-site finding that is somebody else's
  measurement, inside a paper PubMed types `Review`. Chasing the primary study behind it is the best
  value in the audit — but it is a new citation, so it is drafted for the principal, not adopted.

**The concentration risk is going up as a fact, not a defect:** `10.1111/bph.15621` carries three of
the six. The principal should see that half the surviving evidence rests on one paper.

next_handoff: none requested. Do not start the flunisolide primary-source chase or touch
`poc_compounds.yaml` — both wait on the principal.
