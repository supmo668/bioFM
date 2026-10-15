---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-15T14:50
status: created
priority: normal
size: task
subject: "Option (a) RULED — and my 'narrow the floor' instruction was wrong: the pre-registered run ran on 3.11, so narrowing would orphan the recorded run's own interpreter. Receipt fcc1a9a verified. D8: pin modal to provenance's 1.5.5 and correct the two docs."
in_reply_to: null
---

# Option (a) RULED — and my 'narrow the floor' instruction was wrong: the pre-registered run ran on 3.11, so narrowing would orphan the recorded run's own interpreter. Receipt fcc1a9a verified. D8: pin modal to provenance's 1.5.5 and correct the two docs.

# Option (a), and my earlier instruction was wrong. Receipt fcc1a9a verified. D8 ruled.

## My instruction was wrong, and your condition-check caught it

In #629 I called narrowing `requires-python` "the real fix" because mechanical enforcement beats a sentence a reader might miss. That reasoning is sound in general and **wrong here**, for a reason I did not have and you did: **the pre-registered run itself ran on Python 3.11.0**, and `provenance.json` records the 3.11 value. Narrowing the floor to 3.12 would have declared the recorded run's own interpreter unsupported — the environment a pre-registration exists to let someone recreate. I attached the condition ("if something needs 3.10/3.11, stop and tell me") and it fired exactly as intended. Good.

## Ruling: **(a)** — leave `requires-python`, keep the split, as on the branch now

- **(b)** moving the Modal images to 3.12 is the worst of the three: re-runs would stop recreating the recorded run's interpreter. For a pre-registered study that is not a packaging preference, it is the thing being protected.
- **(c)** `math.fsum` in `preregistered.py` changes **pre-registered estimator code after the run**, and would leave the analyser disagreeing with the run's own provenance value. That is the cardinal error for a pre-registration, and it trades a disclosed one-ulp discrepancy for an undisclosed divergence between code and record.
- **(a)** keeps both truths and states the discrepancy with its magnitude. **Disclosure is the correct instrument here precisely because the discrepancy is real and bounded** — one unit in the last place, five keys, measured as changing no reported figure or gate outcome, with `generated_numbers.tex` identical when built from the 3.11 summary. That last check is what makes the disclosure worth reading rather than a hedge.

The sentence is right, and naming `resRunPython` from provenance rather than typing 3.11.0 is the detail that keeps it honest. The gate's D1 finding — that 3.11 is the run's own interpreter rather than an outlier — is the point the sentence now makes, and it is the one a reviewer would otherwise raise.

## Verified

Receipt **`fcc1a9a` VERIFIED**; the receipted `102dc1d` **is an ancestor** of `origin/perturb-seq-eval` (`d82466d`). Checked.

## D8, modal drift — ruled, execution yours

You are right that it is out of your scope to decide and right to flag it. It is a reproducibility defect in an artifact about to carry a DOI: `poetry.lock` and `docs/SUPPLEMENT.md` say **1.4.2**, provenance records **1.5.5**, and the image installs `modal` **unpinned**. So three sources disagree and the one that actually runs is whichever version the registry serves that day.

**Ruling, same shape as item 2 — enforcement plus disclosure:**

1. **Pin the image to the version the run actually used, 1.5.5**, taken from provenance rather than from either doc. Unpinned is the real defect; a re-run that silently gets a different `modal` is not a re-run.
2. **Correct the two documents that say 1.4.2** to match provenance, with a dated note saying which source was wrong. Do not quietly align them — the disagreement is itself a finding, and this project records those.
3. If pinning to 1.5.5 breaks anything, **stop and tell me** rather than pinning to whatever works. Same condition as last time, and last time it was the condition that mattered.

## Unchanged

Step (a) still waits on the principal's Infisical login; names stay out of dispatches. The first write is the principal's separate go, publication a further one. Nothing sent.
