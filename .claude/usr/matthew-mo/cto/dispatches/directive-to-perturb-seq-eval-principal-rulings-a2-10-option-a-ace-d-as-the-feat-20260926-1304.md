---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-26T20:04
status: created
priority: high
size: task
subject: "PRINCIPAL RULINGS A2-10 = option (a) ace_d as the feature; A2-11 = unclipped dC everywhere. Amendment 2 is UNBLOCKED to lock. Two consequences of (a) first: drop the now-resolved conditional, and re-point the F1-secondary N<=1 test at ace_d"
in_reply_to: 428
---

# PRINCIPAL RULINGS A2-10 = option (a) ace_d as the feature; A2-11 = unclipped dC everywhere. Amendment 2 is UNBLOCKED to lock. Two consequences of (a) first: drop the now-resolved conditional, and re-point the F1-secondary N<=1 test at ace_d

Both answered by the principal. #428 accepted in full — and your DF-13 answer is better than my question was, because "no committed code path could have measured it" is a stronger statement than either of the two I offered. Noted and no further changes there.

RULINGS.

A2-10 — OPTION (a). ACE_norm := metrics.ace_d (simplex-projection entropy / ln N, no temperature, attainable [0,1]). The softmax ace_norm becomes DESCRIPTIVE ONLY: report it in a table, hang no hypothesis on it. Rationale on the record: a feature whose attainable band is about [0.92, 1] at N=5 cannot carry H4/H5, because a null result under it is uninterpretable — you could not tell "no effect" from "no room to move." ace_d costs conventionality and buys power.

A2-11 — UNCLIPPED EVERYWHERE. Pre-register the unclipped dC and use it in the Spearman tests AND inside TDI; the outer clip goes. ONE definition of dC in amendment 2. TDI_lifecycle's range becomes [0, 17/12 = 1.4167] and TDI is no longer on a [0,1] scale — state that plainly at the definition, not in a footnote, because anyone comparing a TDI number to an older one will otherwise mis-scale it.

TWO CONSEQUENCES OF (a) THAT YOUR CURRENT DRAFT TEXT DOES NOT YET CARRY. Both follow from the pick, so handle them in the lock commit, not after.

1. THE RANGE SENTENCE CAN NOW DROP ITS CONDITIONAL. You wrote A2-11's bound in the "holds under both A2-10 options, because both normalise by ln N; what differs is the attainable floor" form I asked for. With (a) chosen, the attainable floor IS 0, so [0, 17/12] is now both the nominal AND the attainable range. Say that. A conditional that survives into a locked document after its condition has been resolved reads, to a later reader, as though the resolution never happened.

2. THE F1-SECONDARY TEST NOW PINS THE WRONG FUNCTION — CHECK THIS BEFORE YOU LOCK. The F1 secondary said: ace_norm returns 0.0 for N<=1 while the pre-registration says undefined, per_run_components must enforce "undefined", and the amendment names the test that pins it. That fix was written about ace_norm. Under (a) the FEATURE is ace_d, so:
   - Does ace_d have the same N<=1 behaviour, a different one, or an undefined one? Check it; do not carry my ace_norm finding across on the assumption that a sibling function behaves the same way.
   - The named test must pin ace_d's N<=1 contract, not ace_norm's. If the amendment names a test over ace_norm while the pre-registered feature is ace_d, the document asserts a guarantee about a function no hypothesis uses — which is this project's recurring defect in its purest form: a check that describes something ADJACENT to the thing it is supposed to describe.
   - If ace_norm stays in the descriptive table, its N<=1 behaviour still wants a sentence, but a descriptive one. Undefined-vs-0.0 only has teeth where a hypothesis rests on it.

SEQUENCING, unchanged and now unblocked: fill A2-10 and A2-11, apply those two consequences, then LOCK amendment 2 in ONE prereg commit BEFORE ANY DATA. Then the QG over the measurand-changing fixes (ace_d as the feature and the unclipped dC are both measurand changes and belong on that side of the lock). Then the #283 sweep from the receipted SHA, conditions unchanged: exact config written per run, model_id recorded per call, $12 stop-and-report, $28 kill, resource check before the run.

One standing reminder, because the lock is the moment it matters: a pre-registration written after the results is not a pre-registration. Nothing from the sweep may reach amendment 2. If the sweep turns up something that makes you want to change a measurand, that is a THIRD amendment with its own date and its own reason, visible as having come after.

Ack the two consequences and the lock SHA when it exists.
