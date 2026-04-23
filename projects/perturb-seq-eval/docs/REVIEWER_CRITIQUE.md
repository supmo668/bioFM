# Reviewer Critique — Journal Readiness Assessment

> Harsh-but-fair reviewer pass on the supplement as committed 2026-04-21.
> Reviewer persona: senior ML + computational-biology reviewer who has
> refereed for *Nature Methods*, *Nature Machine Intelligence*, NeurIPS,
> and ICML. Emphasis on statistical rigour and honest framing.

Verdict headline:

> **Weak accept with major revisions required.** The framework is sound
> and the three-regime comparison is genuinely novel. The real-data
> claims need statistical discipline before publication: bootstrap
> confidence intervals, per-seed per-task decomposition, and a clearer
> separation between "infrastructure works" (solid) and "probe informs
> routing on real data" (not yet shown rigorously).

## Strengths

1. **Falsifiable three-regime design.** The juxtaposition of (E3
   shared-optimum → CMA-ES wins, E3-Adamson shallow → contextual edges,
   E3b task-conditional → contextual dominates 7.6×) is a cleanly
   falsifiable experimental design. Most agentic-HPO papers run one
   optimizer on one regime; running three regimes with the same code
   actually tests the hypothesis.
2. **Pre-registered metric-drop rule.** The ρ ≥ 0.95 gate for dropping
   redundant metrics is rare and appreciated. TDI₂ dropping on its own
   evidence is good practice.
3. **Full reproducibility.** `modal run … --step all` reproduces every
   number. The `/artifacts/modal_run/` tree is plain JSON/JSONL, no
   proprietary formats.
4. **Honest limitations section.** §6.3 says "we deliberately do *not*
   claim a contextual-GP advantage over random on Adamson" — that kind
   of epistemic humility is exactly what reviewers look for.

## Major concerns (must address before publication)

### MC1. Zero confidence intervals on every headline number.

Every MSD, AULC, and "% better" quoted in §5 is a point estimate.
Reviewers will reject any claim of the form "contextual GP is 2.6 %
better" without confidence intervals.

**What is needed.** Re-run E3-Adamson with **per-seed trajectories saved**
(current code averages across seeds before serialisation, destroying the
variance). Compute bootstrap 95 % CIs over tasks and seeds. Report as
`final_MSD = 0.0572 [CI 0.054, 0.061]` so that the reader can see whether
the claimed 2.6 % advantage survives the noise floor.

**Expected outcome.** On the Adamson pilot I strongly suspect the
CMA-ES vs contextual-GP CIs will overlap at the 95 % level. The honest
Modal-run headline will shift from "contextual GP beats CMA-ES by 2.6 %"
to "contextual GP matches CMA-ES at 20 seeds; a larger trace set would
be needed to resolve the sign of the effect." That is a publishable
result — just not the one currently claimed.

### MC2. The "scgpt_small wins 5/7 tasks" claim is unstable across seeds.

Per-seed decomposition of winners on Adamson (from
`e2_grid_adamson.jsonl`):

| Seed | scgpt_small | mlp | linear |
|---|---|---|---|
| 2026 | 5 | 1 | 1 |
| 2027 | 4 | 3 | 0 |
| 2028 | 3 | 2 | 2 |

Only seed 2026 produces the "5 / 2 / 0" split quoted in §5.2. The
aggregate number across all three seeds is 12/6/3 (not 5/2/0).

The per-task MSD spreads show that linear / mlp / scgpt_small are
frequently within 5–10 % of each other and well within the per-seed
variance. For example:

- **BHLHE40** — linear 0.0743 (deterministic); mlp 0.0755 ± 0.0023;
  scgpt_small 0.0747 ± 0.0033. **All three overlap.**
- **CREB1** — linear 0.0052; mlp 0.0047 ± 0.0006; scgpt_small 0.0047 ± 0.0010.
  **All three overlap.**
- **DDIT3** — linear 0.0071; mlp 0.0060 ± 0.0009; scgpt_small 0.0067 ± 0.0029.
  **mlp beats linear by 0.001 MSD; scgpt_small is noisier than linear.**

**Recommended correction.** Re-frame §5.2 and §6.2 as:

> On Adamson pilot data the three backbones are statistically
> indistinguishable per task (all 95 % CIs overlap). The mean MSD
> difference between the best and worst backbone per task ranges from
> 0.0004 to 0.010; the per-seed variance is comparable. **No single
> backbone dominates real Adamson, in contrast to the synthetic DGP
> where linear wins every task by 10×.**

That is a more defensible statement, and it preserves the scientific
point (linear's synthetic dominance doesn't transfer) without
overclaiming scgpt_small's real-data advantage.

### MC3. The "probe signature" on real Adamson is *synthesised*, not measured.

This is the most serious issue. The probe signature `x_T` used by the
contextual GP on real Adamson data is **not** harvested from a real
CellForge run. It is synthesised by `_probe_for_task()` in
`scripts/modal/app.py::_run_e3_on_grid`, which draws confidences and
severities from a random distribution keyed only on task-name hash and
a hardcoded task-difficulty assignment.

In other words: the "contextual GP on real Adamson data" result in §5.3
is really "contextual GP on real Adamson grid MSDs + simulated probe
signatures." If the simulated probes happen to correlate with the real
backbone-per-task winners, the contextual GP looks good; if they don't,
it looks the same as random. This is a **confound that needs to be
disclosed or resolved** before publication.

**Recommended corrections, pick one.**

1. **Disclose in §5.3 preamble and the abstract.** Add: "Probe
   signatures for Adamson tasks were simulated from a difficulty-keyed
   DGP rather than harvested from a live agent trace; the probe→route
   linkage on real data is therefore a lower bound on what a live
   trace-collection run would achieve." This is the minimum for an
   honest paper.
2. **Collect real traces and rerun.** Run the full CellForge orchestrator
   on each Adamson task once, harvest the round-0 confidence +
   critique-severity tuple, feed those to the contextual GP. The
   existing `scripts/modal/collect_traces.py` skeleton is ready; the LLM
   call cost on OpenRouter free tier is ~$0. This is what the thesis
   actually claims to have done.

I would require option 2 for a strong accept. Option 1 makes the paper
publishable with a clear scope limit.

### MC4. n = 7 tasks is too small for the "real data" claim.

Adamson pilot has only 9 perturbations (7 after dropping two controls).
Any optimizer's "final MSD" is averaged over 7 tasks × 20 seeds = 140
samples, but the task-to-task variance dominates and with 7 tasks the
degrees of freedom are tiny.

**Recommended correction.** Add a Norman 2019 grid fill (≈ 200
perturbations, combinatorial) as either a second supplement experiment
or as an explicit deferred future-work item. The code already supports
arbitrary h5ad inputs via `load_adamson_matrix`-shaped loaders.

## Minor concerns

### mc5. AULC is an odd primary metric for minimisation.

The paper reports AULC = Σ (best-so-far). That penalises slow
convergence but also penalises late-iteration noise. **Cumulative
regret** Σ (y_t − y_min) is the standard BO metric and is
directly comparable to the Krause–Ong bound cited in §6.4.

**Fix.** Switch headline metric to cumulative regret; keep AULC as a
secondary.

### mc6. The "2.1 M parameters, no pretraining, wins 5/7" claim is tempting but unsound.

A transformer trained on 6 perturbations with no pretraining is not a
"foundation model"; it is a small tied-gene-embedding regressor. The
supplement already acknowledges this in §6.2 ("would strengthen
considerably with (a) pretrained weights …") but the §5.2 prose and §7
conclusion #3 still read as "scgpt_small wins." Tone down.

**Fix.** Replace "scgpt_small wins 5/7 tasks" with "a small transformer
baseline with a gene-token embedding inductive bias is competitive with
the ridge baseline on real data despite lacking pretraining." Nobody
will object to that phrasing.

### mc7. CMA-ES implementation is a (1+λ)-ES, not CMA-ES.

§2.4 is honest about this but the function name is still `cma_es`. A
reviewer from the evolutionary-computation community would flag that
naming. Rename to `one_plus_lambda_es` or similar; add a clear
docstring note.

### mc8. The "Krause & Ong regret bound" interpretation in §6.4 is handwave.

The paper points at the O(√(T γ_T)) bound and asserts it's consistent
with the empirical behaviour, but γ_T is never estimated. Without a
numerical γ_T per regime this is metaphor, not analysis.

**Fix.** Either (a) compute γ_T for each kernel on each regime via the
standard greedy information-gain estimator (Krause et al. 2008) —
~20 lines of code — or (b) remove the bound-interpretation paragraph
and replace with a qualitative one-liner.

### mc9. Colour palette in figures isn't colourblind-safe.

Plotly default is OK for red/blue heatmap but the trajectory lines use
three default colours that can be hard to distinguish for deuteranopia.
Switch to `plotly.colors.qualitative.Set2` or the Wong palette.

### mc10. The `max_genes` grow-to-match workaround (§9) hides a real issue.

The scgpt_small embedding now scales with vocabulary size (2 000 on
Adamson, 40 on synthetic). That inflates parameter count from 130 k on
synthetic to 520 k on Adamson, which is a confound in the synthetic-vs-
Adamson comparison: we're comparing different-sized models across grids.

**Fix.** Fix `n_genes_used` at a constant 2 000 on both grids (pad
synthetic gene-space to 2 000). Rerun E2-synthetic. If the conclusions
change, report honestly. Estimated Modal cost: <$2.

## Summary of required revisions

| # | Severity | Fix | Estimated effort | Modal cost |
|---|---|---|---|---|
| MC1 | Blocker | Emit per-seed trajectories + bootstrap CIs | 4 h | $0.50 |
| MC2 | Blocker | Reframe §5.2/§6.2 with within-seed-variance framing | 1 h | $0 |
| MC3 | Blocker | Add probe-simulation disclosure OR run real-trace collection | 2 h (disclosure) / 1 day (real traces) | $0 |
| MC4 | Major | Add Norman 2019 grid or defer-explicitly | 4 h + fetch | $5–10 |
| mc5 | Minor | Switch headline metric to cumulative regret | 1 h | $0 |
| mc6 | Minor | Tone down "wins 5/7" claim | 30 min | $0 |
| mc7 | Minor | Rename `cma_es` → `one_plus_lambda_es` | 30 min | $0 |
| mc8 | Minor | Estimate γ_T numerically or remove bound-interpretation | 3 h or 15 min | $0 |
| mc9 | Cosmetic | Colourblind-safe palette in Plotly | 30 min | $0 |
| mc10 | Minor | Fix vocab size across grids; rerun synthetic | 2 h + rerun | $2 |

**Total revision cost estimate: 1 engineer-day + $5–10 Modal spend.**

## Post-revision venue fit

- **First choice: Nature Methods or Nature Machine Intelligence as a
  Brief Communications / Software Tool submission.** The framework +
  three-regime evidence is compelling; the wet-lab audience will
  appreciate the MSD-on-held-out-perturbations framing.
- **Second choice: ICLR or NeurIPS (Agent Workshop / FM4LS track) as a
  short paper.** Machine-learning audience will want the regret-bound
  formalisation (mc8) and a real-trace collection (MC3 option 2) — but
  the three-regime comparison is the ML story.
- **Third choice: bioRxiv preprint + MassGen skill contribution.** If
  revisions exceed effort budget, the preprint route lets the
  community consume the framework while the real-trace work is ongoing.

## Reviewer recommendation

> Weak accept conditional on MC1, MC2, MC3. The core contribution — a
> contextual BO infrastructure that falsifies itself cleanly on
> non-routable DGPs and dominates on routable DGPs — is genuinely novel
> and worth publishing. What's blocking a stronger accept is the gap
> between "infrastructure" (shown) and "probe-based routing on real
> data" (simulated). Close that gap, add CIs, and this is a clean
> accept.
