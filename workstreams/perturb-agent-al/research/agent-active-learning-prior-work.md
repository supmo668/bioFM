# Agent-based active learning for perturbation screens: prior work. UNRATIFIED, 2026-11-27

> **UNRATIFIED.** No approvals row rules on this note. All numbers came through a summarising fetch tool. Check each one at its source before citing it. Neither input file was modified.

## Overview
**Question.** What is the state of the art for LLM-agent active learning in perturbation screens, and what would a foundational positive-result paper need?

**Answer in brief.**
- BioDiscoveryAgent and PerTurboAgent beat random and the GeneDisco acquisitions. Both used 5–10 runs, no pre-registration and no tested leakage control.
- By late 2026 the strongest results come from hybrid or learned policies: AssayLoop, Probability-of-Hit and TDAL.
- I found no work that uses LLM verbalised confidence as an acquisition signal.

## Key Concepts
- **Hit ratio / CHR.** Cumulative hits found ÷ all hits. A hit is usually the top 5% by absolute effect, following GeneDisco.
- **EF.** Hits found relative to random selection.
- **Pool-based batch active learning.** Choose *b* genes per round for *K* rounds. Outcomes are read back from an existing screen, so the evaluation is retrospective.
- **Label-free ablation.** Outcomes withheld; separates prior from in-loop learning.

## Implementation: protocol and baselines
**There is no single standard protocol.** Common practice:
- the whole screen as the pool (1k–200k genes);
- hits defined as the top 5%;
- batches of 32–200 genes over 5–10 rounds (GeneDisco went up to 40);
- cumulative hits or AUC as the metric;
- 5–20 seeds.

GeneDisco: rankings depend "on several confounding factors"; model improvement trades off against hit finding.

**Baselines a new paper must beat.** Beating random plus the GeneDisco MLP acquisitions is no longer enough. The full set:
- random;
- Coreset and BADGE;
- Probability-of-Hit and Thompson sampling;
- TDAL;
- a learned cross-screen policy (AssayFormer, or BPMF);
- a bare LLM prior with no agent harness. In #3, standalone Gemini-3.1-Pro reached EF 4.71; a Haiku coding agent reached 3.20.

## Examples: closest works
| # | Work | Shows | Read |
|---|---|---|---|
| 1 | BioDiscoveryAgent, arXiv:2405.17631 (ICLR 2025) | Six single-gene screens plus Horlbeck pairs, 128 genes × 5 rounds. Claims "21% more hits" than baselines and 46% more on non-essential genes. Baselines were random, a human heuristic, and GeneDisco acquisitions plus DiscoBAX; no BALD. Results are means of 10 runs with std and no significance tests. Nine Claude and OpenAI models; not pre-registered. Leakage control is only an assertion that the CAR-T set is unseen. At round 30 on Schmidt1, Coreset beat Sonnet (0.303 vs 0.293). | Full HTML (v3) |
| 2 | PerTurboAgent, PMLR 311:44–64 (MLCB 2025) | Replogle K562, 11 phenotypes, a 9,867-gene pool, 64 genes × 10 rounds, 5 replicates, GPT-4o. Hit ratio 0.440, against BioDiscoveryAgent 0.240, Random+Enrichment 0.255 and Random 0.057. Table 1 shows input genes overlapping the hit lists (up to 14), which "could thus be leaked". | Full PDF text |
| 3 | AssayLoop, arXiv:2609.11877 | 1,389 screens with a temporal split; 10 rounds × 100 genes. EF 5.67 and 27.7% of hits at about 5% coverage, against AssayFormer 4.83. Removing labels lowers every LLM's EF (e.g. GLM-5.1 4.00 → 3.65). Seed count not given. Screens were selected where an LLM already shows signal. | Full HTML |
| 4 | GeneDisco, arXiv:2110.11875 | Nine acquisitions, six batch sizes, four assays, five seeds. Diversity methods improve the model but find fewer hits. | Full PDF text |
| 5 | Probability-of-Hit, arXiv:2605.10196 (ICML 2026) | Batches of 200 × 10 cycles on five GeneDisco screens, five seeds. Best on IL-2 but not on NK or SARS-CoV-2. No LLM baseline. | HTML, 100k of 111k chars |
| 6 | TDAL, arXiv:2610.22122 | Learns the acquisition function online. Eight screens, five seeds; average rank 1.63 of 11 methods. No LLM baseline. Notes "Our evaluation is retrospective." | HTML, 100k of 188k chars |
| 7 | AssayBench, arXiv:2605.10876 | 1,920 screens framed as ranking tasks. Zero-shot generalist LLMs beat biology-specific LLMs and trainable baselines. | Abstract |
| 8 | Krishnamurthy et al., arXiv:2403.15371 (NeurIPS 2024) | In bandit tasks, LLMs "do not robustly engage in exploration without substantial interventions". | Abstract |
| 9 | BED-LLM, arXiv:2508.21184 (ICLR 2026) | Expected information gain computed from the LLM's predictive distributions beats prompt-only selection. | Abstract |
| 10 | Gao, arXiv:2610.18880 (workshop) | Output- and embedding-based confidence signals are inconsistent. Proposes "additive disagreement" for agentic screening. | Abstract |

**Verbalised confidence as an acquisition signal (Q3).** I found no primary source testing it in any domain. The closest works:
- **ActiveLLM** (arXiv:2405.10808): an LLM selects which instances to label. The abstract does not describe how it selects.
- **Generative Active Testing** (arXiv:2603.19264): uses LLM-surrogate uncertainty to pick samples, for evaluation rather than learning.

The evidence that outcome feedback could confound the signal is indirect:
- In #3, every LLM tested does better when it can see outcomes.
- The novelty note's sources (arXiv:2507.03120, 2605.14186) show that showing a model information moves its stated confidence.

## Caveats
**(c) The open gap.** No work found shows an LLM agent beating Probability-of-Hit, TDAL or a learned cross-screen policy on Perturb-seq hit discovery under pre-registered, multi-seed, multi-family conditions with gene-name masking and a temporal holdout, or tests whether the agent's verbalised confidence adds acquisition value beyond the outcomes it was shown.

**(d) Why such claims fail review.**
1. **Pretraining leakage.** Published screens and well-known hits are probably in the training data. Defences so far:
   - #1 asserts its CAR-T set is unseen;
   - #3 uses a temporal split, but chose its screens where LLMs already score well;
   - no one has masked gene symbols.
2. **Weak or mismatched baselines.**
   - #1 and #2 compare only against GeneDisco MLP/BNN acquisitions, not hit-targeted methods, and leave out BALD.
   - #2 ran BioDiscoveryAgent with its literature tool switched off.
   - In #2, a one-line Random+Enrichment heuristic beat BioDiscoveryAgent.
3. **Statistics.**
   - 5–10 runs, std only, no significance tests;
   - #3 gives no seed count;
   - gains are concentrated in early rounds (#1).
4. **Overlap between inputs and labels**, as in #2's Table 1.
5. **Retrospective simulation only**, in #1–#6.
6. **Narrow model coverage.** Few model families were tried, and open-model results are mixed (#2: Qwen2.5-72B did about as well as GPT-4; Llama-3.3-70B failed to follow the output format).

**Open for /define.** Is a label-free ablation plus gene masking enough to separate prior knowledge from in-loop learning? Which hit threshold and metric should be fixed in advance?

**(e) Not accessed.**
- **IterPert** (bioRxiv 10.1101/2023.12.12.571389): HTTP 429. Reported, not retried. Its results are unverified.
- **#3 model names** ("GPT-5.6 Sol", "Claude Opus-4.8") are as the fetch tool rendered them. Confirm at source.
- **Partial reads:** the tails of #5 and #6 were not read. TDAL's batch and round table (C2) was not read.
- **Abstract only:** #7–#10, ActiveLLM, LLAMBO (arXiv:2402.03921), LLM-AL (arXiv:2511.19730) and Virtual CRISPR (ACL BioNLP 2025).

## Sources
- HTML: arxiv.org/html/2405.17631, /2609.11877, /2605.10196, /2610.22122
- PDF (text extracted locally): arxiv.org/pdf/2110.11875; proceedings.mlr.press/v311/hao25b.html (PDF via github.com/mlresearch/v311)
- arXiv abstract pages: 2605.10876, 2610.18880, 2403.15371, 2508.21184, 2405.10808, 2603.19264, 2402.03921, 2511.19730
- ACL Anthology: aclanthology.org/2025.bionlp-1.30
- Blocked (HTTP 429): biorxiv.org/content/10.1101/2023.12.12.571389v1.full
- Read, not modified: findings-staging/2026-11-22-literature-review.md; scratchpad/novelty-feedback-conditioned-confidence.md
