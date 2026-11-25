# CHANGELOG

All notable changes to the perturb-seq-eval supplement are documented here
in conventional-commits style. This file is the version-controlled mirror
of `docs/SUPPLEMENT.md` §9 Deviation Log.

## [Unreleased]

Repository changes that are in no archive deposit. An archive deposit (0.6.2, 0.6.3) holds the manuscript, its build log, the run artifacts and the superseded supplement, and no tests; the test change below is in the deposit commit `07a5e57b` but is not a deposited file.

### Changed

- **Zenodo ↔ Figshare `isIdenticalTo` links added to the 0.6.1, 0.6.2 and 0.6.3 records (HACA-141, 2026-11-25).** Zenodo `24430429` → Figshare v7, `24518637` → v8, `24519260` → v9, each a metadata-only edit published on the principal's go (card `1164ce4d`) and read back from the public API. No file md5 and no other metadata field changed, and no new version was minted. The three "Open" items below are closed by it.
- **Tests: the MLP regression pin and two `summary.json` keys compare within a bounded ulp instead of bit-exactly (HACA-124).** The numbers move by a few ulp with the numpy/BLAS build: numpy 2.4.4 and 2.5.5 on the same x86_64 CPU differ, and the aarch64 host and the x86_64 runner both miss the pins recorded 2026-09-24 (HACA-121). The MLP regression pin now matches within 4 ulp of its largest magnitude (the linear pin stays bit-exact). The reproduction check stays exact for every `summary.json` key except `preregistered.H5.weights.one_minus_delta_c` and `preregistered.H5.norman_tdi`, which match within 4 ulp per element, and every reported value must be identical. Every test run prints its numeric environment (python, numpy, scipy, scikit-learn, torch, BLAS build and runtime core); the checked builds are in `tests/fixtures/numeric_environment.json`. The paper's Reproducibility paragraph discloses the two keys. No result, macro or artifact changed.

## [0.6.3] — 2026-11-25 (manuscript wording revision; published)

Published as the next version of the existing records: Zenodo 10.5281/zenodo.24519260 (a new
version of 10.5281/zenodo.24518637, concept 10.5281/zenodo.19716140) and Figshare
10.6084/m9.figshare.32086920.v9 — the same five files, `paper.pdf` md5-identical on both
(`8264667ba840276071f631a962643e42`, read back from the public records and equal to the build),
built from the deposit commit `8f35d652` (git tag `v0.6.3`). The author decided that this
manuscript is archived as 0.6.3 and not as a second 0.6.2 (perturb-seq-eval approvals row 45,
2026-11-25, which covered the relabel and a dry run only), and then gave the separate go to
publish; the drafts were published as reviewed, with no rebuild. Version 0.6.3 revises the
wording of version 0.6.2 only. It reports the same pre-registered run as v0.6.0, 0.6.1 and
0.6.2, and no hypothesis, threshold, estimator, run or outcome changed;
`paper/PREREGISTRATION.md` is not changed by it.

### Changed

- **Self-contained wording (approvals row 42).** The hypotheses are named by what they claim
  and the amendments to the pre-registration by number, in words, instead of by the labels that
  version 0.6.2 still used in places (its hypotheses table and its table of amendments among
  them); abbreviations and symbols are defined where they are first used; and every table and
  figure caption defines what it shows. The same pass was made over the abstract for the
  preprint server, the deposit notes and descriptions, the citation file and the README.
- **Reference corrected: the CellForge preprint (arXiv:2508.02276).** Versions up to 0.6.2
  credited it to "Xiangru Chen and others" in the bibliography and to "Wei, Yi" under a
  different title in `CITATION.cff`. Its authors are Xiangru Tang, Jiapeng Chen, Daniel Shao,
  Zhuoyun Yu and others (15 authors); its version-1 title is "CellForge: Agentic Design of
  Virtual Cell Models" and its current (version 3) title is "AI Scientists for Building
  Virtual-Cell Models". The bibliography key is unchanged.
- **Deposit configuration.** `publish.yml` has version `0.6.3` and targets a new version of
  Zenodo record 24518637 and Figshare version 9, with the state file `publish.state.v063.json`.
  In `scripts/publish/submit_to_venues.py` the one permitted Zenodo revision moves to 24518637,
  record 24430429 (0.6.1) becomes an ordinary superseded record, `publish.state.v062.json`
  joins the lineage records, and the Figshare base version is 8.
- **Manuscript: one clause about earlier archived versions.** The two sentences that say the
  error feedback was not disclosed in "the versions of this paper archived before this one" now
  say "archived before version 0.6.2", because version 0.6.2 discloses it and, with 0.6.3, is
  itself an earlier archived version.

### Deposit note

- The Zenodo 0.6.3 record is deposit 24519260, a draft made from commit `c42ac57c` with the
  version field `0.6.2` before the version number was decided. The 0.6.3 dry run reused it as
  the open draft of the new version and replaced its files and metadata with the 0.6.3 set; it
  was published only after that, as reviewed.

### Follow-up

- The Zenodo 0.6.3 record carries `isIdenticalTo` the Figshare v9 DOI since 2026-11-25
  (`publish.yml` deposit-time step 5, done after publication under HACA-141).

## [0.6.2] — 2026-11-25 (manuscript revision; published)

Published as the next version of the existing records: Zenodo 10.5281/zenodo.24518637 (a new version of 10.5281/zenodo.24430429, concept 10.5281/zenodo.19716140) and Figshare 10.6084/m9.figshare.32086920.v8 — the same five files, `paper.pdf` md5-identical on both (`e605c293db3296b80adb3b835a50888d`, downloaded from the public records), built from commit `07a5e57b` (tag `v0.6.0-a6`). Principal's go: perturb-seq-eval approvals row 43 (2026-11-25), the separate go that row 41 required; the drafts were published as reviewed, with no rebuild. The deposited manuscript is the Amendment 6 one, not the plain-English-only manuscript of `main` at `db93576f` (row 41). It holds the manuscript as it read **before** the self-contained rewrite that was published as 0.6.3 (above). The git tag `v0.6.2` is on commit `07a5e57b`.

### Changed

- **Disclosure of error feedback in the agents' prompts.** A review made after the outcome was
  known found that from the second round on (round 1 in the run's zero-based numbering) every
  agent's prompt carries the previous round's held-out prediction error
  (`agentic_lifecycle/loop.py`, `llm_agent_pool.py`). Neither the pre-registration nor the
  manuscripts archived earlier (including v0.6.0 and 0.6.1, which report this run) stated
  this. The author decided to disclose it and to
  revise how the affected result is read. The manuscript now states, for each agent role, what
  its prompt carries; it does so in the experimental setup, at the ranking result and in the
  limitations.
- **Revised reading of one supported hypothesis.** The pre-registered trace-feature ranking
  hypothesis (that a feature of the agents' stated confidences ranks tasks by held-out error
  within each dataset) is still supported: its criterion is met through the drop in confidence
  across rounds and the composite that includes it. Because
  that drop is stated after an error has been shown, the manuscript now reads the outcome as
  consistent with confidence reacting to the shown error, and not as evidence that confidence
  predicts difficulty. The claims about prediction, about the single-round probe and about the
  configuration recommender (the class `BayesianRecommender`; specified, not evaluated) are
  reworded to what the tests show.
- **Exploratory subsection and two figures, added after the outcome.** The values are generated
  by `scripts/paper/fill_v060_exploratory.py` (into `paper/data/exploratory_v060.json` and the
  `\expl...` macros of `paper/sections/generated_exploratory.tex`), and the figures are drawn
  by `scripts/paper/make_v060_figures.py`. The exploratory values enter no criterion.
- **Sixth amendment to the pre-registration (Amendment 6 in `paper/PREREGISTRATION.md`).** It
  retitles the paper "Does Multi-Agent Confidence Predict Task Difficulty, or Only React to It?
  A Pre-registered Test on Perturb-seq" and records that the exploratory analyses were added
  after the outcome. A dated note of 2026-11-24 in that section corrects its description of
  what each role's prompt carries and records the figures. The annotated git tag `v0.6.0-a6`
  for this amendment exists: it was created on 2026-11-25 on the merge commit `07a5e57b`. It
  marks the amendment, not a release.
- **Plain academic English.** The manuscript is rewritten without project shorthand, and one
  sentence on reproducing two values across numerical libraries is added to the
  reproducibility section. Hypothesis and amendment labels still appear in places in this
  version; version 0.6.3 replaces them.
- **Deposit configuration, as it was for this release.** `publish.yml` targeted a new version of
  Zenodo record 24430429 and Figshare version 8, with the state file `publish.state.v062.json`,
  which now records the published ids.

### Follow-up

- The Zenodo 0.6.2 record carries `isIdenticalTo` the Figshare v8 DOI since 2026-11-25 (`publish.yml` deposit-time step 5, done after publication under HACA-141).

## [0.6.1] — 2026-11-22 (manuscript revision; published)

Published as the next version of the existing records: Zenodo 10.5281/zenodo.24430429 (concept 10.5281/zenodo.19716140) and Figshare 10.6084/m9.figshare.32086920.v7 — the same five files, `paper.pdf` md5-identical on both, built from commit `980fd099`. Principal's go: perturb-seq-eval approvals row 37.

### Changed

- **Manuscript only.** Amendment 5 of `paper/PREREGISTRATION.md` (tag `v0.6.0-a5`): the paper is retitled, its contribution is narrowed to the multi-agent case, and 'gate' is renamed 'pre-registered criterion'. One related-work sentence on Morandi (2026) is added and the prior-work disclaimer is narrowed to match.
- **No hypothesis, threshold, estimator, run or outcome changed.** The run artifacts are the v0.6.0 run's.

### Follow-up

- The Zenodo 0.6.1 record carries `isIdenticalTo` the Figshare v7 DOI since 2026-11-25 (HACA-141).

## [0.6.0] — 2026-10-16 (pre-registered sweep run; manuscript filled; published)

Published as the next version of the existing records: Zenodo 10.5281/zenodo.23422745 (concept 10.5281/zenodo.19716140) and Figshare 10.6084/m9.figshare.32086920.v6 — the same five files with identical md5s on both venues.

### Known gap: 0.5.1 and 0.5.2 are not documented here

Zenodo v0.5.1 (10.5281/zenodo.20060974, 2026-05-06) and v0.5.2 (10.5281/zenodo.20074427, 2026-05-07) are published, but this CHANGELOG has no entries for them. v0.5.2's record has empty notes and repeats the v0.5.0 abstract; by md5 comparison of the file lists only its `paper.pdf` differs from v0.5.1, and that file is identical to Figshare 32086920 v5's. No release note is reconstructed here (CTO #639). v0.6.0 is the next version of both records: a new Zenodo version from v0.5.2 under concept DOI 10.5281/zenodo.19716140, and the next version of Figshare 32086920 (principal D-1 = B, 2026-10-16; the earlier "new standalone record" ruling #620 was reversed so that no duplicate record exists).

### Known gap: the pre-registered version is defined twice (C3)

`experiments/v05_sweep.py` `PREREGISTERED_VERSION` and `experiments/v05_preflight.py` `PREREGISTERED_VERSIONS` both hold `"v0.6.0"`; they agree, so nothing the run or the record says is affected. Unifying them edits `v05_sweep.py`, which `paper/data/land_v060.json` pins as a post-land path (`post_land_last_code_commit` `ad09b14`), so it would need a land-record amendment. Left as a declared gap at the conclusion (principal, 2026-10-18); a future version should keep one constant.

### Added (amendments 3–4, the sweep, the filled manuscript)

- **Amendments 3 and 4** to `paper/PREREGISTRATION.md`, locked before any v0.6.0 data: A3-1 mito threshold recorded-only, A3-2 Trainer precedence tier, A3-3 Validator threshold required, A3-4 stated grid count = 7 distinct configurations; A4-1 Anthropic roster (Haiku 4.5 for four roles, Sonnet 5.5 Validator; structured outputs; ceilings; one `max_tokens` retry; refusal/served-model rules), A4-2 spend lines $12/$28/$30 on the total including $1.3548 carried in, A4-3 caveats.
- **`src/perturb_eval/llm/anthropic_client.py`**: the amendment-4 client; `openrouter_client.py` is legacy (shared types + `PREREG_VERSION`).
- **The pre-registered run** `20260929T035447Z-ce5f237` (git `ce5f237`, `prereg_version` v0.6.0-a4) under `artifacts/v0.6.0/` with its manifest in `configs/runs/`: 0 fallbacks, 0 cache hits, 0 served-model mismatches, 0 refusals; spend $8.93. Gates H1–H4 PASS, H5 FAIL (as pre-registered).
- **Manuscript filled from the artifacts**: `scripts/paper/fill_v060_numbers.py` writes `paper/sections/generated_numbers.tex` (every result value a `\res...` macro; `--check` is a test); results, methods, abstract, discussion, limitations, conclusion and the corrections appendix rewritten on the macros. LaTeX build products are no longer tracked.

### Removed (run-record amendment RR-1, 2026-10-08/10)

- `llm_key_source` (where the LLM key was stored: store, organisation project, environment, home project, cross-project flag; never the key) removed from the six v0.6.0 run files (RR-1, hashes in `paper/data/run_record_amendments.json`) and retired from the code: `provenance.llm_key_source`/`parse_key_source`, the `build_provenance` field, the preflight check C-KEY-SOURCE (removed, with a dated note, not left passing), and the `LLM_KEY_SOURCE` plumbing in `scripts/modal/app_v05.py`. A re-run no longer records it. Ruling: principal 2026-10-08 ("Remove it everywhere, amend the hash"), CTO #585.
- **RR-2** (2026-10-13, CTO #593/#598): a text-only entry in `paper/data/run_record_amendments.json` correcting three RR-1 text fields (`rerun_note`, `also_replaced_in_docs`, `out_of_scope`) made false by the code retirement. No file or hash rows; RR-1 is byte-identical.

### Fixed (post-run, non-measurand — paths the run never exercised; disclosed in the PR)

- `anthropic_client.py`: a served-model mismatch now raises `ServedModelMismatch` (no failover), as A4-1 requires; previously the base error was raised and the call failed over to the other roster model. The run recorded 0 mismatches and 0 failovers in 1846 calls.
- `provenance.py`: `"replay"` added to `STATUSES`, so a replay run finalises its provenance instead of raising at the end. The run's `replay` is false.
- Analyser (`e_v05_real_traces.py`): a provenance served-model mismatch count above 0 now withdraws the licence (`SERVED_MODEL_MISMATCH_DIAGNOSTIC_ONLY`); `summary.json` gains `served_mismatch_count`. Re-running the analyser on the committed run files on Python 3.12 reproduces the committed `summary.json` values (before Python 3.12, float `sum()` is not compensated and the backbone entropy, five keys, is one ulp higher; the run itself ran on Python 3.11.0) (the new field is 0).
- Docstrings/strings: `app_v05.py` no longer describes an OpenRouter free-tier condition; `architect_dispatch.NOT_APPLIED_FIELDS` cites A3-1 instead of "ruling pending" (the committed artifact carries the old string in `not_applied_reason`; erratum).

## [Superseded] — v0.6.0 regeneration (manuscript aligned before the sweep)

### Changed (title and framing)

- **Title** (principal's choice), propagated to `paper/paper.tex`, `docs/THESIS.md`, `publish.yml`, `CITATION.cff`, `README.md`, `paper/README.md`: *Does Agent Confidence Entropy Predict Task Difficulty? A Pre-registered, Provenance-Complete Test of Agentic Hyperparameter Tuning for Perturb-seq Response Prediction*. The question form makes a null result publishable; a null answer is not to be traded back into a claim title.
- **`paper/PREREGISTRATION.md` added**: five hypotheses and gates (Adamson oracle median < 0.20, Norman < 0.30, Architect backbone entropy ≥ 0.5 nats over LLM-sourced steps, TDI ρ > 0.5 for ≥ 1 component, cross-dataset ρ > 0.4), estimators, and the analysis-plan conventions. H4/H5 have no analyser estimator yet (flagged in the file).
- **Results were placeholders at this point** (since filled; see the entry above). Every result value in the manuscript was `\pending{...}`; `sections/v050_results_filled.tex` is no longer input. All v0.5.0 values are superseded; the new appendix `sections/corrections.tex` maps each to the register rows that supersede it (A1, A2, A3, A4, A7, DF-06, DF-07, DF-10, #227, R1–R3, R9).
- **Setup rewritten to the rebuilt experiment**: 41 tasks (21 Adamson = 3 bins × 7; Norman 15 singletons + 5 doublets) from one deterministic draw (CRC32 strata, seed 2026) in one process; structural Adamson label contract and Ensembl-ID Norman joins recorded in provenance; Norman described as CRISPR activation, Adamson as CRISPR interference; train-only HVG per task; top-20-DEG evaluation genes stated as the CPA/GEARS convention; best-of-54 relabelled an oracle; LLM condition stated at that time as a rotating OpenRouter pool with per-step `model_id` and `source` (superseded by amendment 4, Anthropic roster), fallback runs invalid; `scgpt_small` described once as a from-scratch 2.1 M-parameter transformer.
- **Removed** from the manuscript: the real/synthetic framing and its LaTeX comments, "Nemotron-30B" and "for demonstration purposes", the byte-equivalence claim (now "re-run at the recorded SHA and configuration"), and the claim that pretrained SCFMs are configurable backbones.
- `docs/REVIEWER_CRITIQUE.md` re-scoped to v0.4.1 (retracted line); `README.md` / `paper/README.md` entry points corrected to `scripts/modal/app_v05.py` and the `e_v05_real_traces` analyser.

## [0.5.0+layout] — 2026-04-24 (post-publish housekeeping)

### Repository structure

- **`libs/` directory introduced at the repo root.** `cellforge-agents` and `test-time-compute` moved out of `projects/` into `libs/`. Rationale: only `perturb-seq-eval` is the paper-bearing research project; the other two are reusable libraries (cellforge is imported via `cellforge_pool.py`; test-time-compute is referenced as related work).
- Path-sensitive code (`scripts/modal/app_lifecycle.py`, `app_lifecycle_optimizer.py`, `app_biofm.py`, `scripts/local/collect_real_probes.py`) updated with a `libs/`-first lookup that falls back to the legacy `projects/cellforge-agents/` location for older checkouts.
- All doc + paper refs swept to `libs/cellforge-agents/` / `libs/test-time-compute/`.
- Re-published Zenodo v3 metadata + Figshare references with the corrected `https://github.com/supmo668/bioFM` URL (the v0.4.x records had `mm-bconscious/bioFM` which never existed). DOIs unchanged: Zenodo `10.5281/zenodo.19748260`, Figshare `10.6084/m9.figshare.32086920`.

## [0.5.0] — 2026-04-24 (real-data headline rewrite)

### Changed (headline)

- **All synthetic experiments retracted.** The headline synthetic DGP and E1–E5 synthetic runs that grounded v0.4.1 are removed from the paper entirely. Every reported number in v0.5.0 comes from real Perturb-seq data. Lines 296–298 of v0.4.1's `paper/paper.tex` ("Because real multi-agent perturb-seq runs with scGPT are outside our compute envelope for this paper…") are deleted.
- **Adamson 2016 now uses all three scPerturb subsets** (pilot + 10X005 + 10X010), concatenated via `load_adamson_combined` with target-gene-aware HVG. 97 TFs total, stratified by mean |Δlog1p| on the target gene into 3 quantile bins × 7 TFs = 21 held-out tasks (`seed=2026`).
- **Norman 2019 added** — 15 singletons + 5 doublets, stratified by guide-count quartile (`seed=2026`).
- **Agentic lifecycle now has genuine configuration freedom**. The Architect picks from a widened Pydantic schema (backbone, `n_agents ∈ [2,8]`, `n_rounds ∈ [1,5]`, HVG count, learning rate, ridge λ, epochs) instead of a one-field backbone string. The Validator returns a `StructuredCritique` with `which_genes_failed` and `suggested_next_config_delta` — Architect applies the delta in the next round, closing a true refinement loop.
- **Free-tier OpenRouter rotation pool** drives all LLM calls: Nemotron-3 Super 120B, Ling 1T MoE, Hermes-3 405B, GPT-OSS 120B, Qwen3-Next 80B, Llama 3.3 70B, Gemma-4 31B, Gemma-3 27B. Role-preferred selection, 60s cooldowns, sha256 disk cache. **$0** LLM cost.
- **Single-stage Modal A100 sweep** with hard-kill watchdog at $28. Atomic JSONL append per run for resume safety. Total Modal spend: **$4.04** (well under cap).

### Phase-3 pre-registered gate outcomes

- Adamson median best-config MSD = 0.147 < 0.20: **PASS**
- Norman  median best-config MSD = 0.131 < 0.30: **PASS**
- Architect backbone choice entropy = 0.356 nats ≥ 0.5: **FAIL** (agents converge on `scgpt_small` 91% of the time — sensible for unseen K562 perturbations; gap is a stated future-work item once the backbone pool widens to a pretrained SCFM).

### Added (software)

- `src/perturb_eval/data/{download,subsample}.py` — idempotent SHA256-gated fetchers (Adamson 3 subsets + Norman) with truncation guard; stratified sampler + `mean_abs_logfc_per_target`.
- `src/perturb_eval/experiments/norman.py`, `experiments/e2_adamson.py::load_adamson_combined`.
- `src/perturb_eval/agentic_lifecycle/proposal_schema.py` — Pydantic v2 schemas for all five agents.
- `src/perturb_eval/agentic_lifecycle/freedom_probe.py` — choice entropy probe.
- `src/perturb_eval/agentic_lifecycle/llm_agent_pool.py` — LLMAgentPool over free-tier OpenRouter.
- `src/perturb_eval/llm/openrouter_client.py` — rotation client with weight-inclusive pool.
- `src/perturb_eval/experiments/e_v05_real_traces.py` — replays E1–E5 analysis on real-trace JSONLs.
- `scripts/modal/app_v05.py` + `scripts/modal/app_v05_lifecycle_only.py` — Modal entrypoints.
- `scripts/paper/fill_v050_numbers.py` — templated paper-number substitution.
- `paper/sections/v050_experimental_setup.tex` + `v050_results.tex` (templated).

### DOIs

- **Zenodo v3** (new-version on concept DOI `10.5281/zenodo.19716140`): _to be assigned on publish_.
- **Figshare** (DOI `10.6084/m9.figshare.32086920`, unchanged): paper + supplement updated in place.
- **OSF** (project `wmeuy`): paper + supplement updated in place.

### Deviations from the plan

- OSF preprint subjects PATCH: still unresolved from v0.4.1; retried this release.
- `scgpt_small` is not the Cui 2024 pretrained scGPT; the paper now says so explicitly in §3.2. Pretrained SCFM backbone integration remains future work.
- First Modal sweep (v3) wasted ~30 min on a Norman 404 (filename was `NormanWeissman2019_filtered.h5ad`, not the bare `NormanWeissman2019.h5ad` I pinned) and a sparse-to-dense OOM in the Norman loader. Both fixed before the productive v5 run.
- First lifecycle sweep had every LLM call return HTTP 404 — every model id in the original DEFAULT_POOL had been retired from OpenRouter's free tier between planning and execution. Fixed by querying `/api/v1/models` for the live free-tier roster on 2026-04-24, then re-running lifecycle-only against the trainer JSONL (~$1).

## [0.4.1] — 2026-04-23 (late, authorship patch)

### Fixed

- `paper/paper.tex` `\author{}` block carried `Anonymous Authors / Syntropy Health / {anonymous}@syntropyhealth.bio` from the template. Replaced with (name later ruled "Mang-yin Mo", 2026-10-02) `Mangyin Mo / Carnegie Mellon University / mangyinm@alumni.cmu.edu / ORCID 0009-0009-5233-3142`. Recompiled `paper.pdf` (md5 `e8eec5ba0a65531842fa14168b41b6b8`).
- Zenodo: created v2 record. Concept DOI `10.5281/zenodo.19716140` (canonical) now resolves to v2 `10.5281/zenodo.19721470`. v1 `10.5281/zenodo.19716141` retained for provenance.
- Figshare (DOI `10.6084/m9.figshare.32086920`, unchanged): replaced paper.pdf in place; still 3 files total.
- OSF (project `wmeuy`): replaced paper.pdf on the project's OSFStorage.

### Added

- Infisical secret `AUTHOR_EMAIL = mangyinm@alumni.cmu.edu` in the secret store (store location removed 2026-10-10, RR-1).
- `research/PUBLICATION_EVIDENCE.md` → "Authorship patch" section with the root-cause + remediation + new grep for the pre-flight checklist.

### Root-cause note

The §2.6 coherence audit's placeholder grep only scanned Markdown and YAML tokens (`Last, First`, `REPO/PATH`, `0000-0000`), not LaTeX author blocks. Added `grep -rn "Anonymous\\|Syntropy Health" paper/` to the checklist.

## [0.4.0] — 2026-04-23

### Published

- **Zenodo DOI**: [10.5281/zenodo.19716141](https://doi.org/10.5281/zenodo.19716141) — primary archival DOI for paper + supplement + artefacts bundle.
- **Figshare DOI**: [10.6084/m9.figshare.32086920](https://doi.org/10.6084/m9.figshare.32086920) — mirror of the supplement + artefacts bundle.
- **OSF BioHackrXiv**: deferred. Project `wmeuy` / preprint `dhu4z_v1` exist but OSF's subjects PATCH endpoint returned 502 Bad Gateway at publish time. State file retains all IDs; a single `python scripts/publish/submit_to_venues.py osf` resumes cleanly when OSF recovers.

### Added

- New `src/perturb_eval/agentic_lifecycle/` package (8 files): types, five per-agent executors (data curator, literature, architect, trainer, validator), multi-round loop with `backbone_override` + `validator_threshold_override`, and `CellForgeAgentPool` that wires the live CellForge agents + BioFM tools (BioGPT, Geneformer).
- Modal apps `scripts/modal/app_lifecycle.py` (end-to-end lifecycle sweep) and `scripts/modal/app_lifecycle_optimizer.py` (contextual-BO over live lifecycle evaluation).
- Local `scripts/local/run_lifecycle_dryrun.py`, `scripts/local/analyze_lifecycle_results.py`, `scripts/local/render_fig6_lifecycle.py`.
- `CITATION.cff` with both DOIs + all upstream references.
- `publish.yml` + `scripts/publish/submit_to_venues.py` with OSF/Zenodo/Figshare submitters, live category resolution, and idempotent resume.

### Results (Modal)

- **T11 v2** (`ap-wlIETcuaNPkJin8nScWi94`, A10G): 63 / 63 finite lifecycle runs across 3 backbones × 7 Adamson perturbations × 3 seeds. Mean final MSD = **0.117 [0.089, 0.146]** (bootstrap 95 % CI, n_boot = 2000). Multi-round refinement triggered on 48 / 63 runs (validator threshold = 0.05).
- **T13** (`ap-qqqInu3Fa4r9djbz1I3TvL`, A10G): contextual-BO vs random over the live lifecycle. Both reach MSD 0.056 at iter 1 and tie at AULC 0.445 (ΔAULC = 0.0003). The 2× drop from single-path 0.117 → optimizer 0.056 is the empirical value of the optimization layer.

### Changed

- SUPPLEMENT.md §5.5 (end-to-end agentic lifecycle) added; §7 conclusion now lists seven items including the lifecycle + live optimizer; §8 artifact index extended with `fig6_*`, `adamson_lifecycle_runs.json`, `adamson_live_optimizer.json`, `revision_stats_lifecycle.json`; §9 deviation log extended with five 2026-04-23 rows.
- `publish.yml` abstract now describes four regimes (was three) — adds the end-to-end lifecycle as regime (iv).
- `OptimizerTrajectory` gained `per_seed_trajectories` + `cum_regret_per_iter` (MC1 + mc5).
- Renamed `CMAESOptimizer` → `OnePlusLambdaES` with alias (mc7).
- Wong colourblind-safe palette + CI bands on Figs 2 / 3 / 4 (mc9).

### Fixed

- `57bac5b` — DataCurator HVG filter must preserve every target-gene index; otherwise Linear.fit raised IndexError on every Adamson call. Re-injects missing target-gene indices after the HVG cut.
- `b3a3cdd` — Trainer-failure guard: if `execute_trainer` raised, the Validator now skips scoring (previously called `predict_logfc` on an unfit backbone → RuntimeError).
- `c136bdb` — `.claude/` scratch directory added to repo `.gitignore`.

### Retracted / reframed (per REVIEWER_CRITIQUE.md MC1 – MC3)

- "scgpt_small wins 5 / 7 Adamson tasks" (unstable across seeds; per-seed decomposition 5/1/1, 4/3/0, 3/2/2).
- "Contextual GP beats CMA-ES by 2.6 % on real Adamson" (CIs overlap at 95 %; noise floor swallows the gap).
- The Adamson probe-signature disclosure is now explicit: the §5.3 E3 experiment uses simulated probes (MC3a). Live probes are harvested in §5.3b and the end-to-end §5.5 lifecycle.

## [0.3.0] — 2026-04-22

### Added

- E1 – E4 on synthetic + Adamson grids with bootstrap 95 % CIs, cumulative regret, numerical γ_T (Krause–Singh–Guestrin 2008).
- Five Plotly figures with Wong palette + CI bands.

### Changed

- `TDI₂` dropped from headline metrics per pre-registered ρ ≥ 0.95 rule.

## [0.2.0] — 2026-04-21

### Added

- Metric extensions: `ace_d` (simplex entropy), `csd_star` (excess severity), `tdi2` (with interactions).
- Poetry migration.
- Backbones (`linear`, `mlp`, `scgpt_small`) + optimizers (`random`, `one_plus_lambda_es`, `contextual_gp`).

## [0.1.0] — 2026-04-20

### Added

- Initial paper draft with synthetic DGP and three-regime design.
