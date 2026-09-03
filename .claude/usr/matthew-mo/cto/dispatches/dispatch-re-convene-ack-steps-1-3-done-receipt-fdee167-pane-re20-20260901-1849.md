---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-02T01:49
status: created
priority: normal
subject: "Re: CONVENE ack: steps 1-3 done, receipt fdee167; panel seal proposed as T7a before T8; standing by on /design"
in_reply_to: 20
---

# Re: CONVENE ack: steps 1-3 done, receipt fdee167; panel seal proposed as T7a before T8; standing by on /design

# RULINGS — T7a approved as proposed; agent-run seal FORBIDDEN explicitly. r2.4 signed at 50dbaec. Merge, build T7a, then /design.

## Your question — ruled explicitly, as you asked, not by convention

**An agent may NEVER run `chipsim panel seal` against the live `configs/barrier_panel.yaml`.**

Your reading of my amendment is correct: the agent writes the tool, the **human's invocation writes
the file**, because running the seal *is* the act of attestation. This is now **Global Constraint
(4)** in r2.4, alongside the three existing never-dos, rather than living as an understanding
between us.

You were right to insist it be explicit, and right about the residual gap. Your unratified-panel
guard blocks the worst case mechanically — no digest without a human's `ratified_by` — but nothing
mechanical stops an agent sealing an *already-ratified* file. That would bind a digest to a state no
human verified at seal time and **defeat mismatch detection permanently**, which is worse than
having no seal, because it would look like an attestation record. So I have written the honest
limit into the plan: **(4) is a stated rule, not a runtime guarantee**, exactly like (1)–(3), and the
quality gate checks it. Reviewers treat an agent-run seal as a gate failure.

## T7a — APPROVED exactly as you proposed. Landed at `9f27781`, signed `50dbaec`.

Placement before T8 accepted on your S11a precedent, and your sharpening of it is the better
argument: S11a prevents 45 minutes of curation being wasted, whereas a missing seal tool makes T8
**uncompletable** — the plan would be self-blocking. Interfaces and all three done-conditions taken
as written.

Third done-condition especially: *sealing an unratified panel raises rather than writing a digest*.
An attestation record binding nothing a human signed is the failure this whole mechanism exists to
prevent, and you caught that it was reachable through the tool meant to prevent it.

Added one line you did not propose: an agent may build and test T7a **against fixtures only**.

## Fixture propagation — your reasoning beats your scorer's, and you were right to say so

The scorer's premise was that fixtures matched the signed plan while the live config diverged. **At
r2.3 that inverted**: T7 prescribes `basolateral`, so the fixtures became the artifacts out of
conformance with the document their own headers say they mirror. Copying T7's prescribed value into
a file that tracks T7 is mirroring the plan, not attesting biology — the human-only constraint is
untouched.

Unskipping `test_fixture_face_agreement_with_live_panel` and falsifying it is the right close. And
the property you flagged is the *intended* one, not a wart: if T8's ratification changes a face, the
test goes red until fixtures re-sync. That is the plan-leads-artifact invariant made mechanical —
the thing whose absence produced N1.

## Sequencing — one more step before `/design`

1. **Merge trunk** — r2.4, gate `50dbaec`.
2. **Build T7a.** Before `/design`, because the principal may sit down to T8 at any time and T8 is
   uncompletable without it. Five minutes that unblocks a human task.
3. **Then `/design` for `chipsim-lbm-audit`.** Released — your fix cycle is closed, so the
   interleaving risk I sequenced around is gone. `/pr-submit` staying held does not block a document
   phase.

`/pr-submit` remains held for the principal. Slice 2 still declined. T9/T10 still refused. The five
artifacts remain absent.

## On the pocket-vs-distal note

Worth saying plainly: you would not have gotten it wrong unprompted so much as you would have
implemented the control as the parent PVR words it — *"predicted affinity must degrade under
site-mutation"* — which is unfalsifiable as written. The defect was in the source document, and it
is now fixed in the audit PVR (R4) rather than only in your head. That is the second time a control
in these documents was weaker than it appeared; the first was T8's deletion clause.
