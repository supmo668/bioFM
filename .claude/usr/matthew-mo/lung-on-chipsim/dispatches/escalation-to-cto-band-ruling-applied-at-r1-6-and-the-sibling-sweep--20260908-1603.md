---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-08T23:03
status: created
priority: normal
size: task
subject: "Band ruling applied at r1.6 — and the sibling sweep found the halt rule: PROCEED was inherited from the exchangeable case, so it is now PROVISIONAL"
in_reply_to: null
---

# Band ruling applied at r1.6 — and the sibling sweep found the halt rule: PROCEED was inherited from the exchangeable case, so it is now PROVISIONAL

Principal ruled the band; all three directives actioned. Two of the three were already
standing — the third was not, and following it found the biggest item on the board.

(1) AND (2) — VERIFIED ALREADY STANDING, NOT RE-DONE
D3a keeps the sealed three-region definition with unreachability recorded beside it as a
measured empirical fact; the model-card sentence is written in the binding terms and
explicitly NOT softened to 'limited power'. I re-read both rather than assume, since the
ruling's whole point is that the wording is load-bearing. No edit needed.

(3) SIBLING SWEEP — r1.5's SWEEP WAS INCOMPLETE, AND SAID IT WAS COMPLETE
The R3 vacuity fix and its anti-vacuity guard were already in at r1.5. But that sweep
scoped itself to test ASSERTIONS, found two, and closed with 'recorded so the next reader
does not re-derive the sweep'. That sentence was the active harm.

  CROSS-FAMILY NEGATIVE CONTROL. Its designed outcome was specified (C12) as an
  'insensitive' render on that tier. P0 measured P(insensitive)=0.000 at every feasible n
  — and this tier runs on 20 ligands, so its CI is WIDER than the one that already cannot
  fit the band. The study's sanity floor could not report that the sanity check passed.
  Not an assertion, so a suite-scoped sweep structurally could not see it — yet it is what
  the assertions get written FROM. Sweep re-scoped: any claim that a result confirms the
  design is checked for reachability wherever it lives. Fix is the same shape as the halt
  rule's — the tier's conclusion rides the sign test on point estimates, which is why that
  statistic survived the width that killed 'insensitive'.

THE ONE THAT MATTERS — THE HALT RULE INHERITED 0.92
'Verdict: PROCEED' appears once and was never revisited after P7 measured 0.46-0.75. The
gate exists to fire PRE-HOC and was being evaluated on the single ligand-set assumption
guaranteed not to hold. The same rule reads PROCEED at 0.92 and HALT at 0.46.

This is the FOURTH instance of this document's own standing check, and it was introduced
BY the r1.5 correction to the second: fixing the rule's STATISTIC left its ASSUMPTION
unexamined. A number carried across an assumption boundary is the same error as one
carried across a units boundary. Table extended to four.

PROCEED is now PROVISIONAL. Realised-clustering measurement is a PRECONDITION of the halt
decision, not a refinement beside it — it is free and it gates spend, so it runs first.
No batch on a provisional PROCEED.

TWO MORE, FOUND BY BUILDING THE MACHINERY YOU ASKED FOR
- icc is NOT measurable from SMILES. r1.5 said it was, in a sentence that opens by
  correctly noting membership is what SMILES gives free and then slides to 'the measured
  icc'. Structure says WHICH compounds are analogs; icc says how correlated their (y,f)
  contributions are, and f is a Boltz-2 prediction that does not exist until the batch is
  spent. icc is now a sensitivity RANGE; the halt rule holds across it or it does not
  hold. Sizes ARE free, and that alone converts A7 from unbounded to bounded.
- power.effective_n assumes EQUAL cluster sizes. m_A = sum(m^2)/n >= mean(m) always, so
  the arithmetic form always understates the discount, never in the safe direction.
  MEASURED: one series of 12 among 28 singletons at icc 0.5 reads n_eff 33.6 arithmetic
  vs 15.1 correct — 2.2x overstatement on an entirely ordinary shape. P7's table is
  unaffected and effective_n_unequal([5]*8,0.5) reproduces its 13.3 exactly, so the new
  path is cross-checked against the old on the case where both are valid.

A7 REALISED VALUE — NOT MEASURED, AND I WILL NOT INVENT IT
You asked me to measure A7 locally with R5's MMP machinery. I built it
(chipsim/audit/series.py, 12 tests, RDKit 2026.03.5) but configs/poc_compounds.yaml (T18)
is absent and there are no SMILES anywhere in the repo. Realised icc and realised sizes
are UNKNOWN, not 0.92 and not anything else. The machinery runs the moment T18 lands.

A2's word is now carried into every power statement including the halt verdict. G5
downgrade already recorded in ASSUMPTIONS as 'general argument stands; specific claim did
not survive measurement' — matches your record.

447 passed (+12), ruff clean, commit c0b3d24. Still gating and unchanged: A&D not
approved, /design not complete, nothing sealed, five human artifacts absent, ratified
false, NO GPU batch.

next_handoff: rule on whether PROVISIONAL PROCEED is the right posture, or whether the
halt rule should hard-block until T18 lands.
