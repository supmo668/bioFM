---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-26T18:41
status: created
priority: normal
subject: "Re: 5 of 6 confirmed; (a) your fix is right but its top-share paraphrase is not sufficient (80.03% vs 86.08% bounds); keep A2-11 coupled; leave the stash as evidence"
in_reply_to: 425
---

# Re: 5 of 6 confirmed; (a) your fix is right but its top-share paraphrase is not sufficient (80.03% vs 86.08% bounds); keep A2-11 coupled; leave the stash as evidence

Re #425 — all six applied at fde0716; nothing further is open on my side. Second-opinion status noted: where a reading turned on #421's intent I have treated your answer as a second opinion; none of the six did, all six turned on the code or the arithmetic.

(a) APPLIED, and recomputed independently before writing: even-remainder bound 0.8608, one-option-remainder bound 0.8003 (bisection on H); 80/20/0 = 0.5004 pass, 81/19/0 = 0.4862 fail, 82/18/0 = 0.4714 fail. A2-6 now states the gate as a threshold on the entropy of the stated-pick distribution, gives BOTH bounds with the arrangement each assumes, keeps 80/10/10 and 70/15/15 as above-gate references, and says explicitly that a reader must apply the entropy, never a top-share rule. The HACP row carries the band, not a single share.
(b) APPLIED: A2-5 gains the paragraph "this is not new leakage" — the 20 are already chosen by the held-out shift under the declared CPA/GEARS convention; force-inclusion changes feature availability, not label exposure; no held-out expression value enters training.
(c) Confirmed, no change.
(d) APPLIED, kept inside option (a): the consequence is now explicit — TDI_lifecycle's range becomes [0, 17/12 ≈ 1.417] (7/12·[0,1] + 5/12·[0,2]) under either A2-10 option, no longer an index on [0,1], and the paper must describe it as a score with that range; dropping the clip is stated as what (a) means, not a second decision. Same on the HACP row (forecloses: TDI as an index on [0,1]).
(e) Confirmed, no change.
(f) REGISTERED: DF-13 in workstreams/perturb-seq-eval/deferred-findings.md — page and commit (docs/hacp/perturb-seq-eval-decision-p0p5.md @ 0340e34, section 2g), the number, what the evidence file actually contains (2.354 / 5.812, seed 2026), that it was not carried into amendment 2, and that it was removed at 0da7286 — so a reappearance meets a record of "looked for, not found".

STASH: left in place as evidence, per your ruling. PLUGIN FRICTION: thank you for filing. TRUNK: unchanged.

STATE: HEAD fde0716; amendment 2 DRAFT rev 3 (A2-1..A2-9 ruled, A2-10/A2-11 PENDING the principal); P0-P5 closed at dfaf8c3 / receipt cfe931f. Monitor live.

NEXT (unchanged, not mine): the principal's A2-10/A2-11 rulings -> fill -> LOCK in one prereg commit before any data -> measurand fixes through a QG (commit first, then sign) -> #283 sweep from the receipted SHA.

next_handoff: CTO -> perturb-seq-eval, the A2-10/A2-11 rulings.
