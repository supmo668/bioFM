---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-24T06:07
status: created
priority: high
size: project
subject: "SUPERSEDES #200 scope — code audit: artifacts cannot be from one run; 7 verified defects"
in_reply_to: 200
---

# SUPERSEDES #200 scope — code audit: artifacts cannot be from one run; 7 verified defects

SUPERSEDES the scope in #200. Read #200 first, then this.

A read-only code + workflow audit ran after #200 was written. It found defects more severe than anything in that dispatch, and it supplies the mechanisms for the two blocking findings there. Addendum appended to the same file:

  workstreams/perturb-seq-eval/qa/_adhoc/2026-09-23-publication-rigor-review.md  (§ "Addendum")

I re-verified every finding below myself against the committed code and artifacts. Do not take my word for the ones I have marked unverified — confirm before acting on them.

THE SCOPE CHANGE: #200 asked you to price fixes to the manuscript's claims. That is now premature. The v0.5.0 artifact set CANNOT HAVE COME FROM ONE RUN, so no joined statistic in the paper currently means anything. Artifacts must be regenerated before any claim is adjudicated.

VERIFIED, in the order they must be worked:

A6 -> A1 (do these first, together). app_v05.py:217,224 compute strata as `hash(s) % 3` on Python str. str.__hash__ is salted per process, so which tasks stratified_subsample(seed=2026) draws changes on every invocation — the seed is cosmetic. Consequence, measured: the trainer file's 36 tasks and the lifecycle file's 36 tasks SHARE EXACTLY 2 (SRP72, SAMD1_ZBTB1). app_v05.py:234-240,334-338 iterate the same tasks list in one process, so one run cannot produce this. provenance.json still reports both under one wall-clock window and one cost. analyse_v05_run then JOINS them. So 'Across 108 lifecycle runs spanning 36 held-out tasks' is a join across two nearly-disjoint samples. Fix: crc32 instead of hash; regenerate both files from one process; make analyse_v05_run HARD-FAIL when the task sets differ.

A2. app_v05.py:340-357 records the loop seed into each record but never passes it to run_agentic_lifecycle, which has no seed parameter; the LLM cache key omits it too. Measured: 36 of 36 tasks have byte-identical final_msd_topk across seeds 2026/2027/2028. So 108 runs are 36 counted three times and '138 Architect picks' is 46. Any SE on 108 is sqrt(3) too narrow.

A4. norman.py:119-120 substitutes `int(rng.integers(0, len(gene_names)))` — A RANDOM GENE — as the perturbation target when the target is not in the HVG vocab, with no error, in a branch commented 'deterministic fallback'. It fires because the doublet guard is the wrong delimiter: norman.py:110 and app_v05.py:211 test for '+' but the committed labels use '_' (CBL_UBASH3A, KLF1_MAP2K6, ... — 8 of 15). So the doublet stratum is empty (this is why the '15 singletons + 5 doublets' design degenerated to 15) and those 8 combos got random target genes, then trained and scored as normal tasks. THEY CONTRIBUTE TO median_msd_norman = 0.131 AND TO GATE_NORMAN = PASS. That gate is not currently interpretable. Same fallback at e2_adamson.py:209-212; loop.py:222-226 maps a missing target to index 0. Fix: raise, do not substitute; make the delimiter configurable and assert the expected doublet count.

A3. Over all 690 committed lifecycle steps (138 per role): DataCurator, Literature, Trainer and Validator each emitted exactly ONE distinct proposal_content, equal to its Pydantic schema default. Architect emitted 13. So §4.2's 'agents are not role-rigid executors' is refuted by the project's own trace file, and the widened space in §3.3 is pinned at defaults throughout. Fingerprint is _rule_based_fallback (llm_agent_pool.py:90-109), and LifecycleStep has NO field distinguishing LLM output from fallback, so this is unrecoverable from the artifact rather than merely unreported. Fix: add source: Literal['llm','fallback'] to LifecycleStep; refuse to compute entropy over fallback rows; report per-role entropy.

  CORRECTION you should not propagate: the audit claimed rationale=='' for 138/138 and llm_confidence==0.7 for 138/138, and inferred that ACE is identically 1.0 and CSD identically 0 so TDI cannot correlate with anything. THE PREMISE IS WRONG. Measured: 651 empty rationales of 690, 39 with genuine LLM text; 684 x 0.7 with 6 exceptions (3 x 0.82, 3 x 0.68). Confidence is 99.1% constant, not constant. That inference does not carry. The mechanism for #200's R1 stands independently: tdi_vs_held_out_msd is never called and its default feature path names a field in no schema.

A5. optimizers/base.py:34 — the backbone one-hot is keyed on {scGPT, scPRINT-2, scFoundation} while every experiment uses {linear, mlp, scgpt_small}. None is a key, so .get(...,0) maps all three to index 0: 27 configs collapse to 9 distinct embeddings, nearest_config's argmin always returns linear, and the ES cannot propose mlp or scgpt_small. The retracted 7.6x equals 0.075/0.00989 — it measured this bug. Already retracted, BUT the same embedding feeds every published gamma_T, and tests/test_optimizers.py:22-26 builds its space from the only two names the dict recognises, so no test can catch it. Fix: derive the one-hot from sorted(set(c.backbone for c in config_space)); add `assert len({tuple(config_to_vec(c)) for c in space}) == len(space)`.

A7. data/download.py:34 — sha256 is None for every DatasetSpec; _fetch logs 'already present (no SHA pin) — trust it'. Only a min_bytes floor guards integrity. Paper §3.1 and §9 both claim SHA256-gated fetchers. Pin the three Adamson subset digests and the Norman digest; fail closed.

UNVERIFIED BY ME — leads, confirm before acting: the contextual GP may be non-contextual in every experiment (fresh optimizer per (task,seed) + constant ctx makes the context kernel all-ones, so no routing is possible even in principle — if true, 'probe-conditioned routing' is unsupported outright); the bootstrap resamples pseudo-replicates i.i.d. so CIs are ~4.5x too narrow; load_grid_jsonl discards trainer seeds last-writer-wins, destroying the variance REVIEWER_CRITIQUE MC1 asked to retain; HVG selection runs on the full matrix including held-out cells; temperature is hardcoded 0.3 with no seed and the reproducibility cache is uncommitted; documented entry points scripts/modal/app.py and paper/experiments/ do not exist; orphaned paper/tables/tab1-5.tex and figures/fig1-5.pdf still ship retracted synthetic results with no generator.

WHAT I WANT BACK, still scoping only:

1. A6+A1+A2+A4 as one work item — the seed/determinism/target-substitution cluster. Price it, and tell me the Modal cost of regenerating both JSONLs from one process. The prior sweep was $4.04 / 3.06 GPU-hours against a $28 cap, so it is affordable; it is still the principal's spend and I am not authorising it.
2. A3 and A5 — both are small code changes plus a test. Confirm the fix shape.
3. For each of the seven unverified leads: verified or not, in one line. Do not fix them yet.
4. Your own read on whether #200's R1 route (a) — computing the five correlations from committed traces — is even meaningful once A1 is known. My current view is that it is NOT, because the traces join disjoint task sets, so R1 may collapse into 'regenerate first, then ask'. Tell me if I am wrong.

STILL NOT AUTHORISED TO EXECUTE. Standing constraints hold: log and save the exact config for every run, a new config copy per run, check resource availability first, PoC-minimal. And the language pass stays LAST — it is now several steps further back than #200 implied.
