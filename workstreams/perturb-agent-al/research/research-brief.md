# Research brief — perturb-agent-al (UNRATIFIED, 2026-11-27)

> **UNRATIFIED.** No approvals row rules on these findings. They come from two research notes in this folder,
> both written by agents from primary sources through a fetch tool that summarises pages. Every number and quote
> must be checked at its source before it is cited in a manuscript or a pre-registration.

Source notes:
- [`agent-active-learning-prior-work.md`](agent-active-learning-prior-work.md) — LLM-agent and non-LLM active learning for perturbation screens.
- [`novelty-feedback-conditioned-confidence.md`](novelty-feedback-conditioned-confidence.md) — whether confidence given after shown feedback is a known confound.

## Findings

1. **LLM agents that choose which genes to perturb next already exist.** BioDiscoveryAgent (arXiv:2405.17631),
   PerTurboAgent (PMLR 311), and AssayLoop (arXiv:2609.11877) each report beating random selection and older
   acquisition rules.
2. **Their evidence has four common weaknesses.**
   - No one masks gene names, so knowledge memorised in pretraining cannot be separated from reasoning.
   - Baselines are weak or mismatched: GeneDisco's model-improvement acquisitions rather than hit-targeted
     methods, no BALD, and in one case a one-line heuristic beat a published agent.
   - Five to ten runs, no significance tests, no pre-registration.
   - In PerTurboAgent's own table, genes given to the agent as input overlap the hit lists.
3. **The strongest non-LLM methods have never been compared with an LLM agent.** These are
   Probability-of-Hit (arXiv:2605.10196), TDAL (arXiv:2610.22122) and learned cross-screen policies.
4. **Field practice, not a fixed standard:** a retrospective pool-based simulation; hits defined as the top 5% by
   effect (from GeneDisco); batches of 32–200 genes over 5–10 rounds; cumulative hits or hit enrichment over random
   as the metric; 5–20 seeds.
5. **Withholding outcomes lowers every LLM tested in AssayLoop**, so in-loop feedback matters; whether it helps
   through reasoning or through something like the reactive confidence seen in v0.6.x is untested.
6. **No work found uses an agent's stated confidence to choose experiments**, in any domain, or tests whether it
   adds anything beyond the outcomes the agent was shown.
7. **The confound itself appears unnamed.** Shown information is known to move stated confidence
   (arXiv:2507.03120), and confidence after an attempt is known to track correctness better than before it
   (arXiv:2605.14186). No paper found names feedback leaking into a confidence-change feature that is then used as
   a difficulty or allocation signal.

## Open questions

- IterPert (bioRxiv 10.1101/2023.12.12.571389) returned HTTP 429 and was not read; its results are unverified.
- AssayLoop's model names are as the fetch tool rendered them and need confirming.
- The tails of the Probability-of-Hit and TDAL papers, and TDAL's batch and round table, were not read.
- Several related works were read as abstracts only (listed in each note).
- Whether masking gene names plus withholding outcomes is enough to separate prior knowledge from in-loop
  learning is itself a design question for `/design`.

## Sources

Listed in full in each source note.
