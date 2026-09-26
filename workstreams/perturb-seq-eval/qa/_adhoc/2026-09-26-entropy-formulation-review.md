# Mathematical re-check of the agentic entropy formulations (perturb-seq-eval)

_CTO review, 2026-09-26, on the principal's instruction. Read against `paper/PREREGISTRATION.md`
(H3, H4/H5 definitions), `src/perturb_eval/metrics.py` (`ace`, `ace_norm`, `ace_d`),
`src/perturb_eval/agentic_lifecycle/freedom_probe.py` (`choice_entropy`), and
`src/perturb_eval/experiments/preregistered.py` (`h3`). Every number below is computed in this
review (pure-Python replica of the code's formulas), not copied from any run. Shapes, not values._

## Verdict in one line

The formulas are implemented as documented and are internally consistent. **One of them is
badly conditioned by construction (ACE_norm at τ = 1), one carries an unstated assumption
(the H3 ceiling), and one discards information the hypothesis needs (the clip on ΔC).**
None is wrong as arithmetic; two should change **before** amendment 2 locks, because after
data exist they cannot.

## F1 — ACE_norm at τ = 1 has almost no dynamic range (BLOCKING for H4/H5 as pre-registered)

`ace()` takes the softmax of confidences in [0, 1] and normalises the entropy by ln N.
Because the logits live in a unit interval, no two softmax probabilities can differ by more
than a factor of e. The most concentrated confidence vector possible, (1, 0, …, 0), therefore
still yields near-uniform probabilities. Minimum attainable ACE_norm over the whole cube
[0, 1]^N (analytic at the corner, confirmed by 60,000 random draws per N):

| N (LLM-sourced steps in the round) | min ACE_norm, τ = 1 (corner) | random-search min | ace_d at the same corner |
|---|---|---|---|
| 2 | 0.840 | 0.840 | -0.0 |
| 3 | 0.888 | 0.888 | -0.0 |
| 5 | 0.932 | 0.925 | -0.0 |

So for a five-role round the pre-registered feature occupies **[0.93, 1.00]**: seven percent of
its nominal range. The pre-registration already notes "a narrow band just below 1" and says
rank statistics are unaffected. That is true only if the confidences carry no noise: with a
band this narrow, reported-confidence rounding (LLMs emit 0.7, 0.8, 0.9) produces ties and
near-ties, and Spearman ρ over 20 tasks is then decided by the tie-breaking of a
quantisation artefact rather than by the signal. The H4 test on ACE_norm is under-powered by
design, and H5 fits ridge weights to a feature with no spread.

The repository already contains the fix: `metrics.ace_d` (direct simplex projection, no
temperature) has full range [0, 1] on the same inputs, and its docstring says why it exists.
**Recommendation (A2-10):** pre-register `ace_d` as the ACE_norm feature for H4/H5, report the
softmax version as descriptive only, and state the reason in the amendment. This is a
measurand change and is the principal's to approve; it must happen before the lock, which is
why it is raised now and not after the sweep.

Secondary: `ace_norm` returns 0.0 for N ≤ 1, while the pre-registration says a round with
fewer than two LLM-sourced steps is *undefined*. `preregistered.per_run_components` must be the
one that enforces "undefined", never the metric's 0.0; the test that pins this should be
named in the amendment.

## F2 — H3: plug-in entropy is fine at this N; the ceiling assumes a fixed 3-option menu

`choice_entropy` is the maximum-likelihood (plug-in) estimator, biased low by about
(K − 1)/(2N) nats (Miller–Madow). At the earlier artifact's scale (138 picks, K = 3) that is
≈ 0.0072 nats: negligible against a 0.5-nat gate. Replica of the earlier headline (91 % of
138 picks on one backbone, remainder split): H ≈ 0.356 nats, consistent with the reported
figure, so the arithmetic in the code matches the prose. Per-`model_id` and per-task
breakdowns, however, will have small N and the bias is then not negligible; report the
Miller–Madow-corrected value beside the plug-in one for any breakdown with N < 50.

`h3()` hard-codes `ceiling_nats = ln 3`. That is only the ceiling if the Architect is offered
exactly three backbones on every step. Under the principal's 2c ruling (gate on the *stated*
backbone, exclude omissions), the support is whatever the prompt's menu is: pin the menu (its
size and members) in amendment 2 and derive the ceiling from it rather than from a literal.
For reference, the 0.5-nat gate corresponds to a split between (80/10/10 → 0.639 nats)
and (70/15/15 → 0.819 nats); state that interpretation next to the threshold.

Pooling across tasks, seeds and rounds is a design choice, not an error, but it makes H3 a
statement about the *pool*, not about any task; say so in the hypothesis sentence.

## F3 — 1 − ΔC clips away the sign of the confidence change

ΔC = mean C(last) − mean C(first), then 1 − min(max(ΔC, 0), 1). Every run whose confidence
**fell** across rounds maps to exactly 1.0 (the "no convergence" ceiling), tied with every
run whose confidence stayed flat. A falling confidence is arguably the strongest difficulty
signal the trace can carry, and the clip erases it while creating a tie block at the top of the
ranking. **Recommendation:** pre-register the unclipped ΔC alongside (or 1 − ΔC over the
achievable range with no lower clip), and use the unclipped value in the Spearman tests. The
single-round exclusion already ruled (C3: fixed three rounds) removes the other tie source.

## F4 — TDI_lifecycle weights

(7/12)·ACE_norm + (5/12)·(1 − ΔC), clipped to [0, 1], are the hand-set v0.4 coefficients
renormalised over two components. Arbitrary but pre-registered and monotone in both inputs;
acceptable. Note that if F1 is adopted (ace_d), the weights were tuned on a different feature
and the amendment should say they are carried over unchanged, not re-fitted.

## F5 — H4 multiplicity and H5

Six Spearman tests at ρ > 0.5 with n = 21/20 per dataset; the FWER wording is being fixed under
C20 with a permutation bound (ruled 2g(a)). H5's ridge (α = 1) on 21 tasks with two features is
fine as a pre-registered procedure; report the fitted weights and their sign.

## What this review does not establish

It checks the formulas against their stated definitions and their own numerical behaviour. It
does not check the run records (none exist for v0.6.0 yet) and it does not re-derive C1's
finding that confidence was near-constant in the earlier artifact: that is an input-data
defect, ruled and being fixed, orthogonal to F1.
