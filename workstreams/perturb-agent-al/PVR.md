# PVR — perturb-agent-al: what does an LLM agent contribute to active learning in perturbation screens?

Status: **draft for principal review** (autonomy gate for the PVR: `block` — principal approval required).
Workstream: `perturb-agent-al`. Origin: the perturb-seq-eval study (archive versions 0.6.0–0.6.3).

## Human input

- 2026-11-25 — asked how the technique, framework and domain could be simplified or generalised "to deliver a more
  foundational insight" (perturb-seq-eval session, `/grill-me`).
- 2026-11-27 — asked whether the paper direction can give positive results, what has been tried and why, and what
  is needed "to achieve a foundational paper publication of agent based active learning".
- 2026-11-27 — answered "approve" to three decisions (perturb-seq-eval approvals row 46):
  1. Framing: what an LLM agent contributes to perturbation-screen active learning — knowledge from pretraining,
     reasoning, or reaction to feedback; the v0.6.x confidence-leakage result becomes a separate short methods note.
  2. Primary metric: hit discovery; held-out prediction error secondary.
  3. First-study scope: Replogle K562 genome-wide plus one screen held out by publication date; two model families;
     ten seeds per arm; cost and compute estimated before pre-registration.
- Standing rulings that carry over (perturb-seq-eval approvals and `CLAUDE.md`): no coding agent writes a
  biological number; unratified findings are labelled in place; publishing needs a separate explicit go after a dry
  run; secrets only through the principal's `infisical run` invocation; one preprint server.

## Agent assumptions

Each is a claim the principal can reject; each stays an open question until confirmed.

1. A new workstream, `perturb-agent-al`, holds this study; the perturb-seq-eval workstream stays the record of the
   archived paper.
2. The study reuses the perturb-seq-eval module's data loaders, agent roles, provenance, generated-number and
   pre-registration tooling, rather than starting a new code base. Where the code lives is decided in `/design`.
3. The evaluation is retrospective: outcomes are read from existing screens, as in every prior work found. No wet-lab
   loop.
4. "Gene names masked" means each gene is shown under a stable anonymous identifier, with no symbol, alias,
   description or literature text that could identify it.
5. The study is pre-registered before any data run, as v0.6.0 was.
6. The confidence-leakage methods note is a separate deliverable and is not part of this PVR's requirements.

## Vision

Several published LLM agents choose which genes to perturb next and report beating random selection. None of them
separates what the model already knows about the genes from what it works out in the loop, none is compared with
the strongest current non-LLM acquisition methods, and none is pre-registered. This study answers one question
cleanly: **when an LLM agent helps choose perturbation experiments, is the gain from memorised knowledge, from
reasoning over measured outcomes, or from reacting to the feedback it is shown?**

It does so by crossing the agent's information conditions (gene names visible or masked; outcomes shown, hidden or
shuffled) with single-agent and multi-agent set-ups and two model families, and comparing every arm with a bare LLM
and with the strongest non-LLM acquisition methods, on the same pools, budgets and seeds. Whatever the answer, it is
a positive, reusable finding about where agent gains come from, and the controls are reusable by others.

## Goals & success metrics

- **G1 — The decomposition question is answered under pre-registered tests.** Success: the locked analysis reports,
  for each information condition, the agent's hit discovery relative to the strongest non-LLM baseline and to the
  bare LLM, with intervals, at every pre-registered budget.
- **G2 — The comparison is fair.** Success: every method sees the same pool, batch size, rounds, seeds and hit
  definition; baselines are run with their published or documented settings, and any tuning budget is equal across
  methods and fixed in advance.
- **G3 — The result holds beyond one screen and one model.** Success: the primary analysis is repeated on a screen
  held out by publication date and on a second model family, and both are reported whatever they show.
- **G4 — The work is publishable and visible.** Success: archived (Zenodo and Figshare) and posted on the one
  preprint server, with every number generated from run files.

## Out of scope

- Wet-lab or prospective experiments.
- Training or fine-tuning any language model; training new single-cell foundation models.
- Gating test-time compute, and the v0.6.x trace metrics (ACE, CSD, WFR, TDI, the probe, the recommender).
- The confidence-leakage methods note (a separate deliverable).
- Screens beyond the two named in scope for the first study.
- Any claim about clinical or drug-discovery value.

## Constraints

- **Data:** public screens only, with licences that allow redistribution of derived results. Whether the Replogle
  K562 genome-wide data is in the scPerturb record the project already uses is not yet checked; the current
  download module does not load it.
- **Numbers:** no biological value is written by hand or by an agent; every reported number is generated from run
  files.
- **Models:** two model families, each pinned, with the served model recorded and asserted per call.
- **Secrets:** API keys only through the principal's `infisical run` invocation; no agent reads, prints or stores a
  value.
- **Budget:** a spend cap and a compute estimate are set and approved before pre-registration; a run refuses to start
  above the cap.
- **Publication:** a separate explicit go after a reviewed dry run; one preprint server.

## Failure modes (what must not happen)

1. **Pretraining leakage read as reasoning.** An agent gain that disappears when gene names are masked must not be
   reported as reasoning.
2. **Label leakage through prompts.** No prompt may contain an outcome, or a hit-list membership, for a gene that has
   not been selected and revealed.
3. **Unequal baselines.** A baseline must not be run with fewer seeds, a smaller tuning budget or a different pool
   than the agent arms.
4. **Choosing the metric after seeing results.** Hit definition, budgets, primary metric and tests are fixed before
   any data run.
5. **Feedback leakage into confidence.** If stated confidence is analysed, it is elicited before that round's
   outcomes are revealed, and its value is tested against the shown outcomes as a covariate.
6. **Cost overrun or partial runs reported as complete.** A run that stops early is recorded as incomplete, never
   silently shortened.
7. **Reporting only favourable arms.** Every pre-registered arm is reported.

## Requirements (each with test criteria)

| ID | Requirement | Test criterion |
|---|---|---|
| R1 | A retrospective pool-based active-learning harness: a pool of unmeasured perturbations, a batch size and a number of rounds; after each round only the selected perturbations' outcomes are revealed. | A unit test on a toy pool asserts that a method can read outcomes only for perturbations it has selected, that the batch size and round budget are enforced, and that the same seed gives the same selections. |
| R2 | A hit definition fixed before any data run, computed by a script from the screen data. | The hit set is produced by a script whose output hash is recorded in the pre-registration; a test fails if the script's output differs from the recorded hash. |
| R3 | Metrics: cumulative hit ratio by round, its area under the curve, and enrichment over random (primary); held-out prediction error of a model trained on acquired data (secondary). | Metric functions return known values on hand-built toy pools; the pre-registration names the primary metric and budget. |
| R4 | Baselines: random; a random-plus-enrichment heuristic; Coreset; BADGE; BALD with an ensemble; Thompson sampling; Probability-of-Hit; TDAL where its method can be implemented or obtained; a bare LLM with no agent set-up. | Each baseline runs end to end on a toy pool with a fixed seed and gives identical selections on rerun; any baseline that cannot be implemented is listed with the reason before pre-registration. |
| R5 | Agent information conditions: gene names visible or masked; outcomes shown, hidden, or shuffled (shown values permuted so they belong to other genes). | A test asserts that masked prompts contain no gene symbol or alias from a reference vocabulary; a test asserts that shuffled outcomes are a permutation of the true ones and differ from them for every gene. |
| R6 | Single-agent and multi-agent set-ups, crossed with the information conditions. | Both set-ups run from configuration on a toy pool, and each run records which set-up it used. |
| R7 | Two model families, each pinned; the served model is recorded and asserted per call. | A call whose served model differs from the requested one aborts the run (as in perturb-seq-eval). |
| R8 | If stated confidence is collected, it is elicited each round before that round's outcomes are revealed, and analysed for value beyond the shown outcomes. | Run logs show each confidence's timestamp precedes the reveal of that round's outcomes; the analysis plan names the covariate test. |
| R9 | A leakage audit on every run: no prompt contains outcome or hit information for an unrevealed perturbation. | An automated audit over the stored prompts of every run passes before any analysis; a planted violation in a test fixture is caught. |
| R10 | Pre-registration before any data run: hypotheses, primary and secondary metrics, hit definition, budgets, arms, seeds, tests and multiple-comparison handling. | The run refuses to start unless the locked pre-registration's hash is present in its configuration. |
| R11 | Full provenance per run: code revision, configuration, library versions, dataset digests, pool and hit set, model identities. | A completeness test on the provenance record of a toy run. |
| R12 | A cost preflight and a hard spend cap. | The preflight estimate is printed before any paid call; a test run with a cap below the estimate refuses to start. |
| R13 | Statistics: ten seeds per arm; paired comparisons on shared seeds with intervals; every arm reported. | The analysis script reports every arm, and a test fails if any pre-registered arm is missing from the generated tables. |
| R14 | Every reported number is generated from run files, with a freshness check. | A `--check` mode fails when a generated file is stale, as in perturb-seq-eval. |

## Open questions

1. **Budget:** the spend cap and compute budget for the first study.
2. **Second model family:** which one, and through which provider.
3. **Held-out screen:** which screen, published after the models' training cut-off, is used for the date holdout.
4. **What counts as a hit in a transcriptomic readout.** Prior work defines hits on fitness or marker phenotypes. A
   Perturb-seq readout needs a definition, for example strength of transcriptional effect; to be settled in
   `/design` from the data, with no number written from memory.
5. **Batch size and number of rounds**, within the range the field uses.
6. **Availability of TDAL and Probability-of-Hit implementations.**
7. **Whether the Replogle K562 genome-wide data is in the scPerturb record already used**, or needs a new source.
8. **IterPert**, a closely related method, was not read (HTTP 429); it may be a required baseline.
9. **Engineering owner** of the build.
10. Every item under *Agent assumptions* until confirmed.

Research grounding: [`research/research-brief.md`](research/research-brief.md) (unratified).
