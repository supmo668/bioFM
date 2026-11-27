# PVR — perturb-agent-al: what does an LLM agent contribute to active learning in perturbation screens?

Status: **draft for principal review** (autonomy gate for the PVR: `block` — principal approval required).
Workstream: `perturb-agent-al`. Origin: the perturb-seq-eval study (archive versions 0.6.0–0.6.3).
Review surface: a Notion row under the HACP Index is required by the repository's rules and has **not been created
yet**; this file is its repository copy until then.

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
  4. "Nothing runs or spends until the PVR, design and pre-registration are approved" (row 46).
- Standing rulings that carry over: no coding agent writes a biological number (`CLAUDE.md`); unratified findings are
  labelled in place (`CLAUDE.md`); publishing needs a separate explicit go after a dry run (perturb-seq-eval rows
  2–3); API keys only through the principal's `infisical run` invocation (row 3; row 44 did not replace it).

## Agent assumptions

Each is a claim the principal can reject; each stays an open question until confirmed.

1. A new workstream, `perturb-agent-al`, holds this study; the perturb-seq-eval workstream stays the record of the
   archived paper.
2. The study reuses the perturb-seq-eval module's data loaders, agent roles, provenance, generated-number and
   pre-registration tooling, rather than starting a new code base. Where the code lives is decided in `/design`.
3. The evaluation is retrospective: outcomes are read from existing screens, as in every prior work found. No wet-lab
   loop.
4. "Gene names masked" means the perturbed gene cannot be re-identified from anything shown to the model — its
   identifier, its features, or its outcomes (including its own transcript in the readout) — and that this is
   measured, not assumed (R15).
5. The study is pre-registered before any data run, as v0.6.0 was.
6. The confidence-leakage methods note is a separate deliverable and is not part of this PVR's requirements.
7. Stated confidence is elicited and logged in every agent arm, before each round's outcomes are revealed, so the
   separate methods note can reuse the runs; it is **not analysed in this study**.
8. The baseline set in R4 is the agent's reading of "the strongest non-LLM acquisition methods", taken from the
   unratified research brief. It leaves out learned cross-screen policies (AssayFormer, BPMF) because they need
   training on many screens. The principal can add or drop baselines.
9. "One preprint server" (perturb-seq-eval rows 32–34) was ruled for the archived paper; it is assumed to carry over
   to this study.

## Vision

Several published LLM agents choose which genes to perturb next and report beating random selection. An unratified
literature review (`research/research-brief.md`, 2026-11-27, not checked against every source) found none that
separates what the model already knows from what it works out in the loop, none compared with the strongest current
non-LLM acquisition methods, and none pre-registered.

This study answers one question: **when an LLM agent helps choose perturbation experiments, is the gain from
knowledge acquired in pretraining, from reasoning over measured outcomes, or from reacting to the feedback it is
shown — and how do these interact?** It does so with pre-registered contrasts between arms that differ in one
information condition at a time (gene identity visible or masked; outcomes shown, hidden or shuffled), in single-agent
and multi-agent set-ups and two model families, and compares every arm with a bare LLM and with strong non-LLM
acquisition methods on the same pools, features, budgets and seeds. Whatever the answer, it is a reusable finding
about where agent gains come from, and the controls are reusable by others.

## Goals & success metrics

- **G1 — The decomposition is answered by pre-registered contrasts.** Success: the locked analysis reports, with
  intervals on paired seeds at every pre-registered budget:
  - (a) the knowledge contrast — names visible minus masked, with outcomes hidden;
  - (b) the outcome-use contrast — outcomes shown minus hidden, at each name condition;
  - (c) the content contrast — outcomes shown minus shuffled;
  - (d) the feedback-reaction contrast — outcomes shuffled minus hidden;
  - (e) each agent arm against the bare LLM and against the comparator defined in R4.

  The mapping from each contrast to a claim, including how an interaction between (a) and (b) is reported, is fixed
  in the pre-registration.
- **G2 — The comparison is fair.** Success: every method sees the same pool, gene features, batch size, rounds, seeds
  and hit definition; baselines are run with their published or documented settings; any tuning budget is equal
  across methods and fixed in advance.
- **G3 — The result is checked beyond one screen and one model.** Success: the primary analysis is repeated on a
  screen held out by publication date and on a second model family, and both are reported whatever they show.
- **G4 — The work is publishable.** Success: a reviewed dry run of the Zenodo and Figshare deposits and of the one
  preprint server's submission, with every number generated from run files. Posting needs a separate explicit go.

## Out of scope

- Wet-lab or prospective experiments.
- Training or fine-tuning any language model; training new single-cell foundation models.
- Gating test-time compute, and the v0.6.x trace metrics (ACE, CSD, WFR, TDI, the probe, the recommender).
- Analysis of stated confidence (the separate methods note; see Assumption 7).
- Screens beyond the two named in scope for the first study.
- Any claim about clinical or drug-discovery value.

## Constraints

- **Gate:** nothing runs on screen data and nothing spends until this PVR, the design and the pre-registration are
  each approved (perturb-seq-eval approvals row 46). This includes any pilot (Open question 12).
- **Data:** public screens only, with licences that allow redistribution of derived results. Source of the Replogle
  K562 genome-wide data: Open question 7.
- **Held-out screen:** chosen by a rule fixed before any agent run — its data were first public (repository deposit
  or preprint, whichever is earlier) after the later of the two models' stated training cut-offs; its readout supports
  the same hit definition; it is not chosen on any LLM's performance on it. An undisclosed cut-off is reported as a
  limitation.
- **Hit definition and outcome format:** fixed together, both computed by script from the screen data and not from
  any arm's results.
- **Numbers:** no biological value is written by hand or by an agent; every reported number is generated from run
  files.
- **Models:** two model families, each pinned, with the served model recorded and asserted per call.
- **Secrets:** API keys only through the principal's `infisical run` invocation; no agent reads, prints or stores a
  value.
- **Budget:** a spend cap and a compute estimate are set and approved before pre-registration; a run refuses to start
  above the cap. If the estimate exceeds the cap, the arms to drop are chosen by the principal before
  pre-registration and listed as not run; no arm is dropped after any data run.
- **Publication:** a separate explicit go after a reviewed dry run; one preprint server (Assumption 9).

## Failure modes (what must not happen)

1. **Pretraining knowledge read as reasoning, or the reverse.** Gains are attributed only through the pre-registered
   contrasts of G1. A gain that needs both visible names and shown outcomes is reported as an interaction, not as
   either component alone.
2. **Label leakage through prompts.** No prompt may contain an outcome, or hit-list membership, for a gene that has
   not been selected and revealed; no gene list or example in the initial context may overlap the hit set beyond what
   the pre-registration declares.
3. **Re-identification under masking.** A masked arm whose genes the model can re-identify (R15) must not be reported
   as masked.
4. **Unequal baselines.** A baseline must not be run with fewer seeds, a smaller tuning budget, a different pool or
   different gene features than the agent arms.
5. **Choosing the metric or comparator after seeing results.** Hit definition, budgets, the single primary statistic,
   the comparator rule and the tests are fixed before any data run.
6. **Cost overrun or partial runs reported as complete.** A run that stops early is recorded as incomplete, never
   silently shortened.
7. **Reporting only favourable arms.** Every pre-registered arm is reported.
8. **Detectable shuffling.** The shuffled arm is interpreted only if a pre-registered check does not show that the
   model detected the shuffle; otherwise the shuffled contrast is reported for the masked condition only.

## Requirements (each with test criteria)

| ID | Requirement | Test criterion |
|---|---|---|
| R1 | A retrospective pool-based active-learning harness: a pool of unmeasured perturbations, a batch size and a number of rounds; after each round only the selected perturbations' outcomes are revealed. | A unit test on a toy pool asserts that a method can read outcomes only for perturbations it has selected and that batch size and round budget are enforced. For non-LLM methods, the same seed gives the same selections. For LLM arms, a seed fixes the pool order, the masking map and the shuffle, every model response is stored, and a test replays a stored toy run from the cache and gets identical selections. |
| R2 | A hit definition fixed before any data run, computed by a script from the screen data. | The hit set is produced by a script whose output hash is recorded in the pre-registration; a test fails if the script's output differs from the recorded hash. |
| R3 | One primary hit-discovery statistic named in the pre-registration. Secondary: enrichment over random at each budget, and held-out prediction error of a model fixed in the pre-registration, trained on the acquired data. | Metric functions return known values on hand-built toy pools. The pre-registration names exactly one primary statistic; the analysis script fails if more than one is tagged primary. |
| R4 | Baselines (from the unratified research brief; Assumption 8): random; a random-plus-enrichment heuristic; Coreset; BADGE; BALD with an ensemble; Thompson sampling; Probability-of-Hit; TDAL (Open question 6); and a bare LLM that ranks the pool from its prior with no tools, roles or feedback, at the same budget, under both name conditions. The comparator for G1(e) is either designated in the pre-registration or defined as the best baseline per budget on the same seeds, reported as such. | Each baseline runs end to end on a toy pool with a fixed seed and gives identical selections on rerun; any baseline that cannot be implemented is listed with the reason before pre-registration. The pre-registration names the comparator rule, and the analysis script applies it without data-dependent overrides. |
| R5 | Agent information conditions: gene identity visible or masked (Assumption 4); outcomes shown, hidden, or shuffled. | A test asserts that masked prompts contain no gene symbol or alias from a reference vocabulary. A test asserts that the shuffle is a derangement of gene-to-outcome assignments (no gene keeps its own record), applied as fixed in the pre-registration, and that the multiset of shown values is unchanged. |
| R6 | Single-agent and multi-agent set-ups, crossed with the information conditions. Tokens and calls per run are recorded. | Both set-ups run from configuration on a toy pool and each run records its set-up, tokens and calls. The single- versus multi-agent comparison is reported both raw and per unit of compute. |
| R7 | Two model families, each pinned; the served model is recorded and asserted per call. | A call whose served model differs from the requested one aborts the run (as in perturb-seq-eval). |
| R8 | Stated confidence is logged in every agent arm before that round's outcomes are revealed, and is not analysed in this study (Assumption 7). | Run logs show each confidence's timestamp precedes the reveal of that round's outcomes. |
| R9 | A leakage audit on every run: no prompt contains outcome or hit information for an unrevealed perturbation, and no gene list, pathway list or example in the system or task prompt overlaps the hit set beyond what the pre-registration declares. | An automated audit over the stored prompts of every run passes before any analysis; planted violations of both kinds in a test fixture are caught. |
| R10 | Pre-registration before any data run: hypotheses, the G1 contrasts and their claim mapping, primary and secondary metrics, hit definition, budgets, arms, seeds, comparator rule, tests and multiple-comparison handling. | The run refuses to start unless the locked pre-registration's hash is present in its configuration. |
| R11 | Full provenance per run. | A test on a toy run fails if any field in the provenance schema — code revision, configuration hash, library lockfile hash, dataset digests, pool hash, hit-set hash, feature-table hash, requested and served model per call — is missing or empty. |
| R12 | A cost preflight and a hard spend cap. | The preflight estimate is printed before any paid call; a test run with a cap below the estimate refuses to start. |
| R13 | Statistics: the pre-registered number of seeds per arm (ten, row 46); paired comparisons on shared seeds with intervals; every arm reported. | The analysis script fails if any pre-registered arm is missing, if any arm has fewer than the pre-registered number of seeds, or if any comparison pairs runs that do not share a seed. |
| R14 | Every reported number is generated from run files, with a freshness check. | A `--check` mode fails when a generated file is stale, as in perturb-seq-eval. |
| R15 | A re-identification probe: in the masked condition, each model family is asked to name masked genes from exactly what it is shown; the pre-registration fixes the acceptance rule against a chance-level comparison. | The probe runs on every masked configuration before any analysis; masked arms are reported as masked only if it passes, and the probe's result is part of the generated tables. |
| R16 | Every method sees the same gene feature set, fixed in the pre-registration, with its source and whether it encodes prior knowledge declared. | A test asserts that all arms in a run read the same feature-table hash. |

## Open questions

1. **Budget:** the spend cap and compute budget for the first study.
2. **Second model family:** which one, and through which provider.
3. **Held-out screen:** which screen meets the selection rule in Constraints.
4. **What counts as a hit in a transcriptomic readout, and in what form outcomes are shown.** Prior work defines hits
   on fitness or marker phenotypes; to be settled in `/design` from the data, with no number written from memory.
5. **Batch size and number of rounds**, within the range the field uses.
6. **Availability of TDAL and Probability-of-Hit implementations.**
7. **Whether the Replogle K562 genome-wide data is in the scPerturb record already used**, or needs a new source. The
   current download module does not load it.
8. **IterPert**, a closely related method, was not read (HTTP 429); it may be a required baseline.
9. **Engineering owner** of the build.
10. **Gene features** shared by all arms (R16): which representation, and whether it encodes prior knowledge.
11. **Candidate sampling for agents:** a genome-wide pool does not fit in a prompt, so agents see a sample of
    candidates each round; how it is drawn must be identical across agent arms and is settled in `/design`.
12. **Pilot and staging.** Whether to run a gated pilot before pre-registration, used only to estimate cost, calls per
    run and seed-to-seed variance (and so whether ten seeds can resolve the G1 contrasts), on data outside the
    evaluation pools. And whether, if the estimate exceeds the cap, the first study runs a reduced factorial —
    single-agent, both name conditions, all three feedback conditions, one model family — with multi-agent and the
    second family as a stated second stage under the same pre-registration.
13. Every item under *Agent assumptions* until confirmed.

Research grounding: [`research/research-brief.md`](research/research-brief.md) (unratified).
Review record: the design review of the first draft (2026-11-27) scored it 62/100; every finding is applied in this
version, with the choices on stated confidence and baselines recorded as Assumptions 7 and 8.
