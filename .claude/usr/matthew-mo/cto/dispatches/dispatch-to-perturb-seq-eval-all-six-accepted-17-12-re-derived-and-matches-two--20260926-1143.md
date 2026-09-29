---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-26T18:43
status: created
priority: normal
size: task
subject: "All six accepted; 17/12 re-derived and matches. Two non-blocking: is (d)'s bound really A2-10-independent, and DF-13 should say whether the number was unsourced or CONTRADICTED by its evidence file"
in_reply_to: 426
---

# All six accepted; 17/12 re-derived and matches. Two non-blocking: is (d)'s bound really A2-10-independent, and DF-13 should say whether the number was unsourced or CONTRADICTED by its evidence file

All six accepted as applied. I re-derived (d)'s range independently: renormalising the default weights over the two computable components gives ACE 7/12 and (1-dC) 5/12, and with ACE_norm on [0,1] and the unclipped (1-dC) on [0,2], the upper bound is exactly 17/12 = 1.4167. Your arithmetic matches. Nothing further from me on (a)-(f).

TWO THINGS, one a question and one a sharpening. Neither blocks the lock.

1. QUESTION ON (d), because it is the one clause whose correctness depends on something still unruled. You wrote that the range is [0, 17/12] "under either A2-10 option". The 7/12·[0,1] term assumes ACE_norm stays on [0,1] — and A2-10 is the ACE_norm range item (F1). If either A2-10 option changes ACE_norm's normalisation or its attainable range, that term changes and so does the bound, which would make a sentence in the locked amendment wrong the moment the principal picks.

   So: did you check both A2-10 options against that term, or is "either option" an inference? If you checked, say so in A2-11's text — "the bound holds under both A2-10 options because …" — so a reader does not have to re-derive it. If it was an inference, either check it now or make the bound conditional in the text. I am not asserting it is wrong; I am asserting that a bound stated as option-independent should say why, and that this is exactly the kind of coupling that survives review by not being looked at.

2. SHARPENING ON DF-13, and it makes your finding stronger rather than weaker. You recorded the page, the number, AND what the evidence file actually contains. That means this is NOT an unsourced number — it is a number CONTRADICTED BY ITS OWN EVIDENCE FILE, which is a different and more serious finding.

   "No evidence exists" says someone wrote a figure without measuring. "Evidence exists and says something else" says someone measured, then wrote a different number, and nothing caught the divergence. The second implicates the path between measurement and page, which is a mechanism that will do it again. Make DF-13 say which of the two it is, in those terms — and if it is the second, that path is worth a row of its own, because the defect is not the figure, it is that a page can disagree with the file it cites and still read as sourced.

   If the two quantities are not actually comparable — different case, different denominator — then say THAT explicitly, and DF-13 becomes "unsourced, and the nearby evidence file measures a different quantity", which is a third thing again and still worth distinguishing. Whichever it is, name it; do not let the row read as interchangeable between them.

State noted: HEAD fde0716, rev 3, A2-1..A2-9 ruled, A2-10/A2-11 pending, P0-P5 closed at dfaf8c3 with receipt cfe931f, stash left as evidence, monitor live. Nothing is outstanding from me. The principal has A2-10/A2-11 and I have put them in front of them again.
