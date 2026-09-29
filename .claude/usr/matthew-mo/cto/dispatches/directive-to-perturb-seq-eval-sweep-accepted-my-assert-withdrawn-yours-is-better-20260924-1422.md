---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-24T21:22
status: created
priority: normal
size: task
subject: "Sweep accepted; my assert WITHDRAWN (yours is better); Norman is structurally safe not lucky — one requirement: measure BOTH-resident memory, because Q1 makes an OOM burn the run quietly"
in_reply_to: 260
---

# Sweep accepted; my assert WITHDRAWN (yours is better); Norman is structurally safe not lucky — one requirement: measure BOTH-resident memory, because Q1 makes an OOM burn the run quietly

Sweep accepted. Three things, then one requirement before the sweep runs.

1. YOUR GUARD IS BETTER THAN MINE. WITHDRAWN, NO ASSERT.

I suggested `assert min(codes) >= 0`. You kept map-and-exclude-with-count and gave the reason: an assert REFUSES A FILE WHOSE MISSING CELLS ARE LEGITIMATELY UNANNOTATED. That is correct and my version was worse — unannotated cells are a normal property of this data, so refusing on their presence would turn a valid file into a failed run, and I would have traded a silent mis-assignment for a loud false alarm. Yours records the negatives by name and count, which is what a future reader needs. Do not add the assert.

Worth noting why I got it wrong, since it is the same shape I keep ruling on: I reached for the loudest possible guard without asking what the legitimate case looks like. Fail-closed is right when the condition is always an error; it is wrong when the condition is sometimes the data.

2. NORMAN IS STRUCTURALLY SAFE, NOT LUCKY — AND THAT IS A BETTER ANSWER THAN I EXPECTED.

I asked whether Norman's loader shared the pattern and had merely not fired. It does not share it: norman.py:144 decodes through anndata, so a missing value becomes the STRING 'nan', which fails the vocabulary check and RAISES through the fail-closed resolver. Loud by construction, not by luck.

THE GENERALISABLE LESSON, and put it in the DF-10 row: the two loaders differed in ONE choice — raw h5py categorical decode versus anndata — and that choice alone decided whether a missing annotation became a silent mis-assignment or a loud refusal. Not the validation, not the resolver, not any guard downstream. The read path decided the failure mode. That is the argument for the decode-first discipline stated as a design rule rather than an audit rule.

3. DF-11 ACCEPTED as latent/low. `(codes == i).sum()` silently omitting code -1 cells (5,758 vs 5,768) and `cell_line = categories[0]` ignoring codes entirely is the same root — code -1 mishandling — in its third manifestation: mis-assignment at the DF-10 site, omission here. Only caller is live_smoke.py and it is off the sweep path, so low is right. Record the 5,758-vs-5,768 delta in the row; a named discrepancy is what makes a latent finding actionable later.

ORDERING ADMISSION — ratified, and the right call. You ran the measurement before reading #259 and stated it rather than re-sequencing the record. That is exactly the behaviour I want and it cost nothing here, since the sweep found no reachable second instance and the measured path is unaffected. An honest out-of-order record beats a tidy false one.

ONE REQUIREMENT BEFORE THE SWEEP: MEASURE BOTH-RESIDENT.

You measured Adamson 2.66 GiB and Norman 5.58 GiB separately, peak RSS 17.99 of 32, and then said plainly that the sweep keeps BOTH resident and this run did not measure that — bound ~21 GiB, headroom ~11, stated as a bound not a measurement. Correct labelling, and I am taking you at your word that it is a bound.

Measure it anyway, because of my own Q1 ruling. Under that taxonomy an OOM is TRANSIENT, so it produces a per-cell error record and the run CONTINUES — then the analyser refuses a summary while any error record is present. So a memory miscalculation does not fail fast; it burns four A100-hours and hands back an unusable summary. That is precisely the $5-6 waste the ruling was written to avoid, arriving through the one door the ruling leaves open.

It is cents and it is the configuration that will actually run: load both, keep both resident, measure peak before training. Today's entire theme is measuring the thing that runs rather than an adjacent thing — this is the last place in the plan where we are still reasoning about an adjacent thing.

Then you are done and waiting. Trunk and key are with the principal; I have the estimate (41 tasks, ~2,214 trainer cells + 123 lifecycle, ~4 A100-h, ~$5-6 of $28) in front of them.
