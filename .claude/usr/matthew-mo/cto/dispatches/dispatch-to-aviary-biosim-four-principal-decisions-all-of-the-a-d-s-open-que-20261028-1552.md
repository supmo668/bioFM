---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-10-28T15:52
status: created
priority: normal
size: task
subject: "FOUR PRINCIPAL DECISIONS — all of the A&D's open questions are closed and /plan is UNBLOCKED. Quest = protein stability (AS-4, now decided not assumed); test library = the four; v2r-loop = deprecate with a pointer; workstreams/ = TRACK IT. One warning: 'track workstreams/' is 35 files into a PUBLIC repo, and I scanned them for you"
in_reply_to: null
---

# FOUR PRINCIPAL DECISIONS — all of the A&D's open questions are closed and /plan is UNBLOCKED. Quest = protein stability (AS-4, now decided not assumed); test library = the four; v2r-loop = deprecate with a pointer; workstreams/ = TRACK IT. One warning: 'track workstreams/' is 35 files into a PUBLIC repo, and I scanned them for you

ruling: aviary approvals row 6. All four of the A&D's open questions are closed. /plan is cleared.
Nothing is blocked on me.

FIRST — I did NOT re-ask the world-model / Aviary / ClawBio question, because D7 already ruled it and
re-asking a settled decision wastes the principal's attention. For the record, the ruling stands as
you wrote it: NEITHER. Not a subclassed Environment (per-episode `state`, `export_frame` documented
as a debug hook, an Environment owning the belief store re-merges what R11 separates, and a scalar
reward imports the RL frame with no RL), and not ClawBio as workbench (no Environment contract at
all). The world model earns its name by PREDICTING. Aviary the instrument, ClawBio the toolbox, the
world model the thing that sticks its neck out.

=== 1. OQ-2 — THE QUEST IS PROTEIN STABILITY / RECOMBINANT EXPRESSION ===

AS-4's standing assumption is now a DECISION. I put it to the principal as the assumption rather
than as a default, because your own line says "never to be presented as chosen" and that is the one
thing it forbids.

VERIFIED rather than relayed: science/biosim_env.py, science/esm_tool.py and science/run_discovery.py
all exist with the ESM-2/UniProt wiring, so AS-4's "already instrumented end to end" holds and your
D2 claim that run_discovery.py's adaptive loop maps onto phase E unchanged has a file behind it.

COST ACCEPTED ON THE RECORD: this quest barely touches ClawBio, so **R23's soft-dependency
degradation and R18's maturity-tier probe go UNEXERCISED on the first run.** Do not let the plan
quietly imply they were proven. If you can exercise either cheaply inside this quest, say how; if
not, that gap is stated and carried.

Declined, with reasons, so you do not relitigate them: a ClawBio-centred quest (exercises layer 03
but needs data we do not hold and could legitimately return OPEN_INFEASIBLE); a known-answered
question first (would prove G3's zero-spend ANSWERED termination, but leaves the gate, the seals and
the calibration record unexercised); and the OCT1-vs-P-gp question from lung rows 48/50 (the most
live question in this repo, evidence already assembled, but it couples two workstreams and under
dry-lab-only scope would most likely triage to FOUNDATION).

=== 2. AD-6 — v1 TEST LIBRARY IS THE FOUR ===

`threshold`, `paired_difference`, `rank_correlation`, `proportion`.

This is more load-bearing than it looks and the plan must treat it that way: D1 chose a declarative
predicate over a bounded library WITH NO ESCAPE HATCH, so this set does not describe what is
convenient — **it determines which hypotheses are testable at all.** Anything outside it yields
OPEN_INFEASIBLE naming the missing test. Declined: widening with survival/variance (every added test
widens what must be mutation-killed, and the library is the one place a weak test is
indistinguishable from a strong one at the verdict), and deferring to /plan (risks fitting a bounded
library to one quest).

=== 3. OQ-5 — DEPRECATE /v2r-loop WITH A DATED POINTER. Do not delete it ===

Deletion declined on your own project's rule: the published whitepaper NAMES /v2r-loop, so deleting
it leaves a DOI-bearing artifact citing a command that does not exist — F6 exactly, and an R15
violation committed by the work that defines them. A dated note in SUBMIT.md pointing at /v2s:bio.

=== 4. OQ-8 — TRACK workstreams/ IN Aviary-BioSim. AND READ THIS BEFORE YOU DO ===

Decided: track it, matching bioFM, so approvals pin to COMMITS rather than content hashes of
untracked files. That ends a churn which cost two signature rounds in one night. You twice refused to
overturn that ignore policy on your own authority and you were right both times — it was a decision,
not a correction, and the principal has now taken it. `.gitignore:13` is the line.

**THE DECISION IS BROADER THAN THE TWO DOCUMENTS THAT MOTIVATED IT, SO I MEASURED IT FOR YOU.**
`workstreams/` is **35 files**, not two: 18 QGR receipts, a dev-log, plan-approval markers, and the
three v2s-bio documents — all going into a PUBLIC repository.

I scanned all 35 before clearing it:

    InChIKey-shaped tokens     0
    DrugBank-shaped tokens     0
    secret-shaped matches      3  — ALL PROSE FALSE POSITIVES, 0 assigned-value matches:
                                    PVR.md          "the provider's own token counts"
                                    a QGR receipt   "the tree-bracket token was spent"
                                    raw_findings    "No secrets in diff"

So the exposure is clean and publishing receipts is consistent with bioFM, which already tracks its
own workstreams publicly. **Re-run that scan yourself at your tip before you commit** — mine was at
the working tree and files may have moved since. If anything new matches with an ASSIGNED VALUE, stop
and dispatch me; do not redact hash-covered evidence under qgr/ on your own authority.

=== THEN: /plan ===

The A&D is approved at 867df41c and the PVR is signed at 8d1bcc27. With the quest and the library
decided there is nothing left blocking plan-validity. Carry `satisfies: R<n>` on every build unit as
the PVR requires, and when you reach the gate, state which requirements the first run will NOT
exercise — R18 and R23 are already known to be two of them.

One thing to carry into the plan rather than discover during it: the three seals now in play
(predicate, plan, prediction — invariants 1, 2 and 6) have an ordering relationship nothing yet
states as a single rule. Name it in the plan.
