---
type: findings-staging
status: "UNRATIFIED. A literature list, not a claim. Nothing here is in paper/, the bib, or any deposit."
authorization: >-
  principal instruction 2026-11-22 (perturb-seq-eval approvals row 37, "perform a ML / comp. bio literature review").
agent: biofm/matthew-mo/perturb-seq-eval
---

# Literature review, ML and computational biology — UNRATIFIED, 2026-11-22

> **Status (2026-11-22): UNRATIFIED.** No approvals row rules on any entry below. The 0.6.1 manuscript was
> published without it and is unchanged by it.
>
> **How it was made.** Two research agents searched and opened one primary page per entry (an arXiv abstract page,
> a publisher or proceedings page). **Abstract level only: no full text was read.** Quotes were returned through a
> fetch tool that can paraphrase, so each must be checked character by character at its source before it is cited.
> No sentence here relates any work to this paper's method or claim; the thread labels are navigation.
>
> **Flag for the principal, not a finding.** Part 1 thread 3 lists works whose signal is computed over a group of
> agents (for example arXiv:2606.13197, arXiv:2510.12697, arXiv:2603.20975). The paper's narrowed contribution is
> the multi-agent case (approvals rows 11 and 13). Whether any of these bears on that wording needs a full-text
> read of the kind done for CATTS and Morandi, and then a ruling. None has been made.
>
> **Not covered.** Part 2 thread 5 (large Perturb-seq resources) has no verified entry: bioRxiv returned HTTP 429
> and cell.com HTTP 403, reported and not retried. Unverified leads are listed at the end of each part.

# Part 1 — Machine learning

## Literature review (ML side): related work not yet cited

Paper: "Does a Multi-Agent Group's Confidence Distribution Predict Task Difficulty?"
Already cited, so excluded here: CATTS (2602.12276), Morandi 2026 (2605.19193), Snell et al. 2024, AutoGen, MassGen, Archon, MAV (Lifshitz 2025), CellForge.

How each entry was checked: I opened the arXiv abstract page (`https://arxiv.org/abs/<id>`) on 2026-11-22. Authors, date and title come from the page's `citation_*` meta tags. The quote is copied from the page's abstract block. "Venue" is shown only when the arXiv Comments field states one; otherwise it is "—". Affiliations are left out on purpose. Each "Signal over" cell says only what the abstract says about whether the signal comes from one model or from a group of agents.

Rows are ordered closest first within each table. Across all tables, the closest work is in Thread 3, where the signal is computed over a group of agents.

## Thread 3: Multi-agent debate (agreement or confidence as a signal, adaptive stopping, when debate helps)

| # | Authors (year) | Title | ID / URL | Venue | Verbatim quote (abstract) | Signal over |
|---|---|---|---|---|---|---|
| 3.1 | Eo, Moon, Zi, Park, Lim (2025) | Debate Only When Necessary: Adaptive Multiagent Collaboration for Efficient LLM Reasoning | arXiv:2504.05047 https://arxiv.org/abs/2504.05047 | — | "an adaptive multiagent debate framework that selectively activates debate based on the confidence score of the agent's initial response" | One agent's initial confidence gates whether a group debate runs |
| 3.2 | Niu, Zhang (2026) | ARMOR-MAD: Adaptive Routing for Heterogeneous Multi-Agent Debate in Large Language Model Reasoning | arXiv:2606.13197 https://arxiv.org/abs/2606.13197 | — | "Pre-debate Agreement Routing (PAR) decides whether independently generated Round-0 answers require debate; Early Agreement Stopping Evaluator (EASE) stops debate after convergence" | Agreement across a group of heterogeneous agents |
| 3.3 | Hu, Tan, Wang, Qu, Chen (2025) | Multi-Agent Debate for LLM Judges with Adaptive Stability Detection | arXiv:2510.12697 https://arxiv.org/abs/2510.12697 | — | "models judge consensus dynamics via a time-varying Beta-Binomial mixture, with adaptive stopping based on distributional similarity (Kolmogorov-Smirnov test)" | Consensus distribution over a group of judge agents, tracked across rounds |
| 3.4 | Hu, Shen, Lakshmipathi (2026) | Statistical Scouting Finds Debate-Safe but Not Debate-Useful Cases: A Matched-Ceiling Study of Open-Weight LLM Reasoning Protocols | arXiv:2605.09618 https://arxiv.org/abs/2605.09618 | Technical report / preprint (Comments) | "This headroom is hard to recover from cheap ex-ante signals. A vote-entropy threshold is the only controller that directionally beats the best fixed protocol" | Vote entropy over samples, used to route between direct, vote and two-agent debate |
| 3.5 | Fan, Yoon, Ji (2025) | iMAD: Intelligent Multi-Agent Debate for Efficient and Accurate LLM Inference | arXiv:2511.11306 https://arxiv.org/abs/2511.11306 | AAAI 2026 (Oral) | "a token-efficient framework that selectively triggers MAD only when it is likely to be beneficial (i.e., correcting an initially wrong answer)" | One agent's self-critique (41 hesitation features) gates whether a group debate runs |
| 3.6 | Wang, Xie, Wang, Zhang, Woo (2026) | Budgeted Act-or-Defer Multi-Agent LLM Deliberation with Local Reliability Bounds | arXiv:2606.29654 https://arxiv.org/abs/2606.29654 | — | "maps the debate prefix to a low-dimensional state, computes a k-nearest-neighbor lower confidence bound on state-conditional correctness" | Group debate state at each round |
| 3.7 | Yoa, Sim, Yoon, Yoon, Kim, Lee, Kim, Lee (2026) | Efficient Multi-Agent Reasoning via Confidence-Guided Adaptive Debate | arXiv:2610.16343 https://arxiv.org/abs/2610.16343 | ICML 2026 | "a leader-centric multi-agent debate framework that selectively engages interaction only in non-neutral regimes" | Group of agents (leader and supporters) |
| 3.8 | Chen, Song, Ji, Gao, Zhu (2025) | Self-signals Driven Multi-LLM Debate for Efficient and Accurate Reasoning | arXiv:2510.06843 https://arxiv.org/abs/2510.06843 | — | "Our approach enables high-confidence agents to exit early at the model level and compress the redundant debate contents" | Each agent's model-level confidence, inside a multi-LLM debate |
| 3.9 | Liu, Yao, Liu, Zhang (2026) | EMS: Multi-Agent Voting via Efficient Majority-then-Stopping | arXiv:2604.02863 https://arxiv.org/abs/2604.02863 | — | "terminates the process once the current leading answer cannot be overturned by any possible votes from the remaining agents" | Votes across a group of agents |
| 3.10 | Chang, Chang (2025) | Multi-Agent Collaborative Intelligence: Dual-Dial Control for Reliable LLM Reasoning | arXiv:2510.04488 https://arxiv.org/abs/2510.04488 | — | "A moderator tracks disagreement, overlap, evidence quality, and argument quality, and halts when gains plateau." | Disagreement across a group of agents |
| 3.11 | Chen, Saha, Bansal (2023) | ReConcile: Round-Table Conference Improves Reasoning via Consensus among Diverse LLMs | arXiv:2309.13007 https://arxiv.org/abs/2309.13007 | ACL 2024 | "employing a confidence-weighted voting mechanism that leads to a better consensus" | Confidences stated by a group of diverse LLM agents |
| 3.12 | Lin, Hooi (2025) | Enhancing Multi-Agent Debate System Performance via Confidence Expression | arXiv:2509.14034 https://arxiv.org/abs/2509.14034 | EMNLP 2025 Findings | "we propose incorporating confidence expression into MAD systems to allow LLMs to explicitly communicate their confidence levels" | Stated confidences inside a group debate |
| 3.13 | Tang, Meng, Costa, Zhang, Ye, Xi (2026) | The Value of Variance: Mitigating Debate Collapse in Multi-Agent Systems via Uncertainty-Driven Policy Optimization | arXiv:2602.07186 https://arxiv.org/abs/2602.07186 | — | "quantifies behavioral uncertainty at three levels: intra-agent (individual reasoning uncertainty), inter-agent (interactive uncertainty), and system-level (output uncertainty)" | Single agent, between agents, and whole system |
| 3.14 | Choi, Zhu, Li (2025) | Debate or Vote: Which Yields Better Decisions in Multi-Agent Large Language Models? | arXiv:2508.17536 https://arxiv.org/abs/2508.17536 | NeurIPS 2025 Spotlight | "we find that Majority Voting alone accounts for most of the performance gains typically attributed to MAD" | Group of agents (voting compared with debate) |
| 3.15 | Zhang, Cui, Chen, Wang, Zhang, Wang, Wu, Hu (2025) | Stop Overvaluing Multi-Agent Debate -- We Must Rethink Evaluation and Embrace Model Heterogeneity | arXiv:2502.08788 https://arxiv.org/abs/2502.08788 | — (position paper, per Comments) | "MAD often fail to outperform simple single-agent baselines such as Chain-of-Thought and Self-Consistency, even when consuming significantly more inference-time computation" | Group of agents compared with a single agent |
| 3.16 | Smit, Duckworth, Grinsztajn, Barrett, Pretorius (2023) | Should we be going MAD? A Look at Multi-Agent Debate Strategies for LLMs | arXiv:2311.17371 https://arxiv.org/abs/2311.17371 | — | "multi-agent debating systems, in their current form, do not reliably outperform other proposed prompting strategies, such as self-consistency" | Group of agents; adjusts how often agents agree |
| 3.17 | Wang, Wang, Su, Tong, Song (2024) | Rethinking the Bounds of LLM Reasoning: Are Multi-Agent Discussions the Key? | arXiv:2402.18272 https://arxiv.org/abs/2402.18272 | — | "a single-agent LLM with strong prompts can achieve almost the same performance as the best existing discussion approach" | Group of agents compared with a single agent |
| 3.18 | Du, Li, Torralba, Tenenbaum, Mordatch (2023) | Improving Factuality and Reasoning in Language Models through Multiagent Debate | arXiv:2305.14325 https://arxiv.org/abs/2305.14325 | — | "multiple language model instances propose and debate their individual responses and reasoning processes over multiple rounds to arrive at a common final answer" | Group of model instances (the original debate setup) |
| 3.19 | Liang, He, Jiao, Wang, Wang, Wang, Yang, Shi, Tu (2023) | Encouraging Divergent Thinking in Large Language Models through Multi-Agent Debate | arXiv:2305.19118 https://arxiv.org/abs/2305.19118 | EMNLP 2024 | "multiple agents express their arguments in the state of 'tit for tat' and a judge manages the debate process" | Group of agents with a judge |

## Thread 2: Confidence and calibration as a signal of correctness or difficulty (incl. multi-agent uncertainty)

| # | Authors (year) | Title | ID / URL | Venue | Verbatim quote (abstract) | Signal over |
|---|---|---|---|---|---|---|
| 2.1 | Jiang (2026) | DiscoUQ: Structured Disagreement Analysis for Uncertainty Quantification in LLM Agent Ensembles | arXiv:2603.20975 https://arxiv.org/abs/2603.20975 | — | "extracts and leverages the structure of inter-agent disagreement ... to produce well-calibrated confidence estimates" | Group of agents (5-agent ensemble) |
| 2.2 | Yang, Rajagopal, Hayati, Hu, Kang (2024) | Confidence Calibration and Rationalization for LLMs via Multi-Agent Deliberation | arXiv:2404.09127 https://arxiv.org/abs/2404.09127 | ICLR 2024 Workshop on Reliable and Responsible Foundation Models | "leverages the collaborative and expressive capabilities of multiple tool-augmented LLM agents in a simulated group deliberation process" | Group of agents |
| 2.3 | Sun, Wu, Li, Guo, Che, Huang (2026) | CoE: Collaborative Entropy for Uncertainty Quantification in Agentic Multi-LLM Systems | arXiv:2603.28360 https://arxiv.org/abs/2603.28360 | ICLR workshop "Agentic AI in the Wild" (per Comments) | "combines two components: intra-model semantic entropy and inter-model divergence to the ensemble mean" | Several LLMs (between models and within each model) |
| 2.4 | Feng, Htut, Qi, Xiao, Mager, Pappas, Halder, Li, Benajiba, Roth (2024) | Rethinking LLM Uncertainty: A Multi-Agent Approach to Estimating Black-Box Model Uncertainty | arXiv:2412.09572 https://arxiv.org/abs/2412.09572 | EMNLP 2025 Findings | "employing multi-agent interaction across diverse query variations for uncertainty estimation of black-box LLMs" | Multi-agent interaction, used to estimate one model's uncertainty |
| 2.5 | Wang, Zhang (2026) | A Systematic Evaluation of Black-Box Uncertainty Estimation Methods for Large Language Models | arXiv:2606.19868 https://arxiv.org/abs/2606.19868 | — | "organize them into five categories: verbalization-based, sampling-based, explanation-based, multi-agent, and hybrid methods" | Benchmark of 24 methods, single-model and multi-agent |
| 2.6 | Xiong, Hu, Lu, Li, Fu, He, Hooi (2023) | Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs | arXiv:2306.13063 https://arxiv.org/abs/2306.13063 | ICLR 2024 | "LLMs, when verbalizing their confidence, tend to be overconfident, potentially imitating human patterns of expressing confidence" | Single model (verbalized confidence and sampling consistency) |
| 2.7 | Tian, Mitchell, Zhou, Sharma, Rafailov, Yao, Finn, Manning (2023) | Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback | arXiv:2305.14975 https://arxiv.org/abs/2305.14975 | EMNLP 2023 | "verbalized confidences emitted as output tokens are typically better-calibrated than the model's conditional probabilities" | Single model |
| 2.8 | Kuhn, Gal, Farquhar (2023) | Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in Natural Language Generation | arXiv:2302.09664 https://arxiv.org/abs/2302.09664 | ICLR 2023 (Spotlight) | "Our method is unsupervised, uses only a single model, and requires no modifications to off-the-shelf language models." | Single model (samples) |
| 2.9 | Geng, Cai, Wang, Koeppl, Nakov, Gurevych (2023) | A Survey of Confidence Estimation and Calibration in Large Language Models | arXiv:2311.08298 https://arxiv.org/abs/2311.08298 | — | "we outline the challenges and we summarize recent technical advancements for LLM confidence estimation and calibration" | Survey (single model) |

## Thread 1: Adaptive or difficulty-aware test-time compute allocation (early stopping, adaptive self-consistency, routing)

| # | Authors (year) | Title | ID / URL | Venue | Verbatim quote (abstract) | Signal over |
|---|---|---|---|---|---|---|
| 1.1 | Aggarwal, Madaan, Yang, Mausam (2023) | Let's Sample Step by Step: Adaptive-Consistency for Efficient Reasoning and Coding with LLMs | arXiv:2305.11860 https://arxiv.org/abs/2305.11860 | EMNLP 2023 | "non-uniformly distribute the available budget based on the amount of agreement in the samples generated so far" | Samples from a single model |
| 1.2 | Wang, Feng, Li, Yuan, Zhang, Tan, Pan, Hu, Li (2024) | Make Every Penny Count: Difficulty-Adaptive Self-Consistency for Cost-Efficient Reasoning | arXiv:2408.13457 https://arxiv.org/abs/2408.13457 | NAACL 2025 Findings | "leverages the difficulty information of batch queries from both prior and posterior perspectives to adaptively allocate inference resources" | Single model |
| 1.3 | Taubenfeld, Sheffer, Ofek, Feder, Goldstein, Gekhman, Yona (2025) | Confidence Improves Self-Consistency in LLMs | arXiv:2502.06233 https://arxiv.org/abs/2502.06233 | — | "CISC performs a weighted majority vote based on confidence scores obtained directly from the model." | Single model (samples weighted by confidence) |
| 1.4 | Li, Yuan, Feng, Pan, Wang, Sun, Wang, Li (2024) | Escape Sky-high Cost: Early-stopping Self-Consistency for Multi-step Reasoning | arXiv:2401.10480 https://arxiv.org/abs/2401.10480 | ICLR 2024 | "we propose a simple and scalable sampling process, Early-Stopping Self-Consistency (ESC), to greatly reduce the cost of SC" | Samples from a single model |
| 1.5 | Damani, Shenfeld, Peng, Bobu, Andreas (2024) | Learning How Hard to Think: Input-Adaptive Allocation of LM Computation | arXiv:2410.04707 https://arxiv.org/abs/2410.04707 | — | "predicts the distribution of rewards given an input and computation budget, then allocates additional computation to inputs for which it is predicted to be most useful" | Single model (learned predictor) |
| 1.6 | Lugoloobi, Foster, Bankes, Russell (2026) | LLMs Encode Their Failures: Predicting Success from Pre-Generation Activations | arXiv:2602.09924 https://arxiv.org/abs/2602.09924 | COLM 2026 | "models encode a model-specific notion of difficulty that is distinct from human difficulty" | Single model's activations, used to route across a pool of models |
| 1.7 | Zhu, Liu, Lin, Tong, Zhong, Shao (2025) | The LLM Already Knows: Estimating LLM-Perceived Question Difficulty via Hidden Representations | arXiv:2509.12886 https://arxiv.org/abs/2509.12886 | — | "efficient and accurate difficulty estimation based solely on the initial hidden state, without generating any output tokens" | Single model |
| 1.8 | Liu, Hu, Chu, Choi (2025) | DiffAdapt: Difficulty-Adaptive Reasoning for Token-Efficient LLM Inference | arXiv:2510.19669 https://arxiv.org/abs/2510.19669 | ICLR 2026 (Comments: "ICLR 26") | "selects Easy/Normal/Hard inference strategies per question based on their difficulty and reasoning trace entropy" | Single model |
| 1.9 | Yoon, Jeong, Park, Yeom, Kim (2026) | Breaking the Pre-Sampling Barrier: Activation-Informed Difficulty-Aware Self-Consistency | arXiv:2602.09438 https://arxiv.org/abs/2602.09438 | — | "leverages internal difficulty signals reflected in the feed-forward network neuron activations to construct a lightweight difficulty estimation probe" | Single model |
| 1.10 | Manvi, Singh, Ermon (2024) | Adaptive Inference-Time Compute: LLMs Can Predict if They Can Do Better, Even Mid-Generation | arXiv:2410.02725 https://arxiv.org/abs/2410.02725 | — | "allowing the LLM to predict mid-generation the probability that restarting the generation will yield a better response" | Single model |
| 1.11 | Fu, Wang, Tian, Zhao (2025) | Deep Think with Confidence | arXiv:2508.15260 https://arxiv.org/abs/2508.15260 | — | "leverages model-internal confidence signals to dynamically filter out low-quality reasoning traces during or after generation" | Single model (traces) |
| 1.12 | Wan, Wu, Chen, Li (2024) | Reasoning Aware Self-Consistency: Leveraging Reasoning Paths for Efficient LLM Sampling | arXiv:2408.17017 https://arxiv.org/abs/2408.17017 | NAACL 2025 | "using these assessments to guide early stopping decisions and rationale selection" | Single model (samples) |
| 1.13 | Zhang, Zhou, Wang, Wang, Li (2024) | Scaling LLM Inference with Optimized Sample Compute Allocation | arXiv:2410.22480 https://arxiv.org/abs/2410.22480 | — | "propose OSCA, an algorithm that Optimizes Sample Compute Allocation by finding an optimal mix of different inference configurations" | Inference configurations (model, temperature, etc.) |
| 1.14 | Ong, Almahairi, Wu, Chiang, Wu, Gonzalez, Kadous, Stoica (2024) | RouteLLM: Learning to Route LLMs with Preference Data | arXiv:2406.18665 https://arxiv.org/abs/2406.18665 | — | "efficient router models that dynamically select between a stronger and a weaker LLM during inference" | Router choosing between two models |
| 1.15 | Chen, Zaharia, Zou (2023) | FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance | arXiv:2305.05176 https://arxiv.org/abs/2305.05176 | — | "an LLM cascade which learns which combinations of LLMs to use for different queries" | Cascade over several LLMs |

## Thread 4: Item difficulty estimation for LLM benchmarks (IRT-style)

| # | Authors (year) | Title | ID / URL | Venue | Verbatim quote (abstract) | Signal over |
|---|---|---|---|---|---|---|
| 4.1 | Ding, Deng, Choo, Wu, Agrawal, Schwarzschild, Zhou, Goldstein, Langford, Anandkumar, Huang (2024) | Easy2Hard-Bench: Standardized Difficulty Labels for Profiling LLM Performance and Generalization | arXiv:2409.18433 https://arxiv.org/abs/2409.18433 | NeurIPS 2024 Datasets and Benchmarks | "we apply well-established difficulty ranking systems, such as Item Response Theory (IRT) and Glicko-2 models, to uniformly assign numerical difficulty scores" | Performance data from humans or from many LLMs |
| 4.2 | Hofmann, Heineman, Magnusson, Lo, Dodge, Sap, Koh, Wang, Hajishirzi, Smith (2025) | Fluid Language Model Benchmarking | arXiv:2509.11106 https://arxiv.org/abs/2509.11106 | COLM 2025 | "estimates an item response model based on existing LM evaluation results and uses the inferred quantities to select evaluation items dynamically" | Evaluation results from many LMs |
| 4.3 | Zhou, Huang, Zhao, Han, Wang, Chen, Yang, Bao, Dong, Xu, Zhu, Cao, Zhao (2025) | Lost in Benchmarks? Rethinking Large Language Model Benchmarking with Item Response Theory | arXiv:2505.15055 https://arxiv.org/abs/2505.15055 | AAAI 2026 (Oral) | "PSN-IRT can be utilized for accurate and reliable estimations of item characteristics and model abilities" | Results from many models |
| 4.4 | Polo, Weber, Choshen, Sun, Xu, Yurochkin (2024) | tinyBenchmarks: evaluating LLMs with fewer examples | arXiv:2402.14992 https://arxiv.org/abs/2402.14992 | ICML 2024 | "to accurately estimate the performance of an LLM on MMLU ... it is sufficient to evaluate this LLM on 100 curated examples" | Results from many models |
| 4.5 | Kipnis, Voudouris, Buschoff, Schulz (2024) | metabench -- A Sparse Benchmark of Reasoning and Knowledge in Large Language Models | arXiv:2407.12844 https://arxiv.org/abs/2407.12844 | ICLR 2025 | "We use data from n > 5000 LLMs to identify the most informative items of six benchmarks" | Results from more than 5000 LLMs |
| 4.6 | Qu, Heng, Zeng, Liu (2026) | An Interpretable and Scalable Framework for Evaluating Large Language Models | arXiv:2605.07046 https://arxiv.org/abs/2605.07046 | — | "Item Response Theory (IRT) offers a principled framework for modeling latent model abilities and item characteristics" | Results from many models |

## Thread 5: Pre-registration and negative results in ML evaluation

| # | Authors (year) | Title | ID / URL | Venue | Verbatim quote (abstract) | Signal over |
|---|---|---|---|---|---|---|
| 5.1 | Vaccaro (2026) | Preregistration for Experiments with AI Agents | arXiv:2606.11217 https://arxiv.org/abs/2606.11217 | ICML 2026 Spotlight Position Paper | "this paper argues that preregistration practices ... should now be extended to experiments with AI agents" | n/a (methodology) |
| 5.2 | Hofman, Chatzimparmpas, Sharma, Watts, Hullman (2023) | Pre-registration for Predictive Modeling | arXiv:2311.18807 https://arxiv.org/abs/2311.18807 | — | "we propose adapting pre-registration practices from explanatory modeling to predictive modeling" | n/a (methodology) |
| 5.3 | Leech, Vazquez, Kupper, Yagudin, Aitchison (2024) | Questionable practices in machine learning | arXiv:2407.12220 https://arxiv.org/abs/2407.12220 | — | "We describe 44 such practices which can undermine reported results ... Our list emphasises the evaluation of large language models (LLMs)" | n/a (methodology) |
| 5.4 | Lu (2026) | Pre-registered tests of solid-state-physics-inspired LLM compression: a cluster-level negative result at small-language-model scale | arXiv:2609.34292 https://arxiv.org/abs/2609.34292 | — | "with predictions committed to git before any pilot data and a 3-sigma gate deciding PASS or SHELVE" | n/a (example of a pre-registered negative result) |
| 5.5 | Chen (2026) | Sensitive-Topic Leakage Through LLM Routing Metadata: Measurement and Mitigation | arXiv:2610.09981 https://arxiv.org/abs/2610.09981 | — | "exploratory and below the pre-registered primary endpoint's 0.75" | n/a (example of reporting a missed pre-registered endpoint, in an LLM-routing setting) |

Note on 3.4 (2605.09618): it is both a routing study and a mostly null result. Its abstract reports paired-bootstrap CIs that include zero and a meta-analysis with p=0.125. So it also belongs under Thread 5 as an example of reporting a negative result.

## Unverified leads (primary page not opened, or not used)

- Farquhar, Kossen, Kuhn, Gal (2024), "Detecting hallucinations in large language models using semantic entropy", Nature, DOI 10.1038/s41586-024-07421-0. I did not open the publisher page in this session, so this is unverified. Kuhn et al. 2023 (2.8) is the verified preprint in the same line.
- Kadavath et al. (2022), "Language Models (Mostly) Know What They Know", arXiv:2207.05221. Left out because it is from 2022, outside the 2023–2026 window. Not opened.
- Chen et al. (2025), "IrtNet", arXiv:2510.00844. Seen only in a search snippet, which said it is about routing and performance prediction rather than item difficulty. Not opened.
- AlignVQA, arXiv:2511.11169 (calibration in multi-agent visual QA). Seen only in a search snippet. Not opened.
- Other pre-registered LLM studies seen only as search snippets, not opened: arXiv:2610.34379, 2609.09899, 2604.07709 (IatroBench), 2608.09942, 2610.05533.
- Zhuang et al. (2025) and Truong et al. (2025), on adaptive testing and IRT item selection. Named in a search summary without identifiers. Not located.

## Search log

1. arXiv abstract pages fetched directly for candidates known in advance: 2305.11860, 2401.10480, 2502.06233, 2508.15260, 2410.04707, 2408.13457, 2410.02725, 2406.18665, 2305.05176, 2408.17017, 2306.13063, 2305.14975, 2302.09664, 2311.08298, 2309.13007, 2305.14325, 2305.19118, 2311.17371, 2508.17536, 2412.09572, 2502.08788, 2402.18272, 2402.14992, 2407.12844, 2509.11106, 2409.18433, 2311.18807, 2407.12220, 2410.22480.
2. Web search: "arXiv adaptive stopping multi-agent debate rounds consensus early termination LLM 2025". Led to 2510.12697, 2606.13197, 2606.29654 and 2604.02863. The search also returned Morandi 2605.19193, which is already cited.
3. Web search: "arXiv multi-agent LLM disagreement predicts question difficulty uncertainty adaptive compute 2025". Led to 2603.20975, 2605.09618, 2510.06843, 2510.04488, 2603.28360 and 2606.19868.
4. Web search: "arXiv LLM predict problem difficulty before solving adaptive test-time compute probe 2025". Led to 2602.09924, 2510.19669, 2509.12886 and 2602.09438.
5. Web search: "\"Debate Only When Necessary\" adaptive multiagent collaboration arXiv". Led to 2504.05047, 2511.11306 and 2610.16343.
6. Web search: "Confidence Calibration and Rationalization for LLMs via Multi-Agent Deliberation arXiv". Led to 2404.09127.
7. Web search: "pre-registered study large language models negative result benchmark evaluation arXiv preregistration 2024 2025". Led to 2606.11217, 2609.34292 and 2610.09981. The other hits are listed under unverified leads.
8. Web search: "arXiv item response theory LLM benchmark item difficulty prediction 2025 \"item difficulty\"". Led to 2505.15055 and 2605.07046.
9. Web search: "arXiv uncertainty-aware multi-agent debate confidence expression agents calibration 2025". Led to 2509.14034 and 2602.07186.
Every entry in the tables above was then confirmed against its own arXiv abstract page. No table entry was written from a search snippet.


# Part 2 — Computational biology

## Literature review, computational-biology side

Paper: "Does a Multi-Agent Group's Confidence Distribution Predict Task Difficulty?"
Compiled 2026-11-22 by a researcher subagent. **Unratified. This is a draft for review, not a delivered bibliography.**

## Overview

The question: which 2022–2026 work, not already cited (Norman 2019, Adamson 2016, Replogle 2022, scGPT, Geneformer, CellForge), comes closest to the paper's threads. In brief, the closest work falls into three groups. (a) Benchmarks reporting that simple, mean or linear baselines match or beat deep and foundation models (Ahlmann-Eltze 2025, Wong 2025, PertEval-scFM, PerturBench, Systema). (b) LLM and agent systems for perturbation biology (PerturbQA/SUMMER, BioDiscoveryAgent, PerTurboAgent, LangPert, MechPert, SynthPert). (c) A small, recent body of work on calibrated uncertainty for perturbation prediction (PRESCRIBE, selective conformal inference). Thread 5 (large resources released 2023–2026) has **no verified entry**: every candidate's primary page was bioRxiv (HTTP 429) or Cell (HTTP 403).

## Key Concepts

- A **verified** entry means its primary page was opened in this session: a journal DOI page, an arXiv abstract page, a PMLR proceedings page or a conference virtual page.
- **Quotes were extracted by the fetch tool's summarising model**, not copied from raw HTML. Each one should be checked character by character against the page before it goes into the paper.
- The "Thread" column is a neutral label only. It makes no claim about how the work relates to ours.

## Implementation (tables, closest first within each thread)

### Thread 1: perturbation-response methods and benchmarks, including simple-baseline findings

| # | Authors, year | Title | Identifier | Venue | Verbatim abstract fragment | Thread |
|---|---|---|---|---|---|---|
| 1.1 | Ahlmann-Eltze C, Huber W, Anders S, 2025 | Deep-learning-based gene perturbation effect prediction does not yet outperform simple linear baselines | doi:10.1038/s41592-025-02772-6 | Nature Methods 22:1657–1661 | "None outperformed the baselines, which highlights the importance of critical benchmarking in directing and evaluating method development." | simple baselines vs deep/FM |
| 1.2 | Wong DR, Hill AS, Moccia R, 2025 | Simple controls exceed best deep learning algorithms and reveal foundation model effectiveness for predicting genetic perturbations | doi:10.1093/bioinformatics/btaf317 | Bioinformatics 41(6) | "Here, we present a simple baseline method that outperforms both state of the art (SOTA) in DL" | simple baselines vs deep/FM |
| 1.3 | Wenteler A, Occhetta M, Branson N, et al., 2025 | PertEval-scFM: Benchmarking Single-Cell Foundation Models for Perturbation Effect Prediction | https://proceedings.mlr.press/v267/wenteler25a.html | ICML 2025, PMLR 267 | "Our results show that scFM embeddings offer limited improvement over simple baseline models in the zero-shot setting" | FM benchmark |
| 1.4 | Wu Y, Wershof E, Schmon SM, ... Graepel T, 2024 | PerturBench: Benchmarking Machine Learning Models for Cellular Perturbation Analysis | arXiv:2408.10609 | arXiv (cs.LG); v4 Oct 2025 | "simpler architectures are generally competitive and scale well with larger datasets." | benchmark |
| 1.5 | Bendidi I, Whitfield S, Kenyon-Dean K, ... Denton AK, 2024 | Benchmarking Transcriptomics Foundation Models for Perturbation Analysis: one PCA still rules them all | arXiv:2410.13956 | NeurIPS 2024 AIDrugX workshop | "Our approach identifies scVI and PCA to be far better suited models for understanding biological perturbations" | FM benchmark |
| 1.6 | Roohani Y, Huang K, Leskovec J, 2024 (online 2023) | Predicting transcriptional outcomes of novel multigene perturbations with GEARS | doi:10.1038/s41587-023-01905-6 | Nature Biotechnology 42:927–935 | "GEARS can predict phenotypically distinct effects of multigene perturbations" | method |
| 1.7 | Hao M, Gong J, Zeng X, ... Song L, 2024 | Large-scale foundation model on single-cell transcriptomics (scFoundation) | doi:10.1038/s41592-024-02305-7 | Nature Methods 21:1481–1491 | "Developing foundation models for deciphering the 'languages' of cells and facilitating biomedical research is promising yet challenging." | foundation model |
| 1.8 | Fawkes J, Hodgson L, Hartford J, 2026 | Knowledge Graphs and Reasoning LLMs for Finding Simple Yet Effective Transcriptomic Perturbation Predictors | arXiv:2606.08816 | arXiv (cs.LG) | "the K-nearest neighbour approach beats almost all methods on out-of-distribution perturbation prediction" | simple baselines / LLM |
| 1.9 | Mao X, Zhang S, Wen Q, ... Gao Z, 2026 | Benchmarking virtual cell models for in-the-wild perturbation response | arXiv:2604.27646 | arXiv (q-bio.CB) | "Here, we introduce a standardized and modular benchmarking framework for virtual cell prediction." | benchmark |
| 1.10 | Wenkel F, Tu W, Masschelein C, Shirzad H, ... Denton AK, 2025 | TxPert: Leveraging Biochemical Relationships for Out-of-Distribution Transcriptomic Perturbation Prediction | arXiv:2505.14919 | arXiv (cs.LG) | "TxPert, a new state-of-the-art method that leverages multiple biological knowledge networks" | method (OOD) |
| 1.11 | Miladinovic D, Höppe T, Chevalley M, ... Schwab P, 2025 | In-silico biological discovery with large perturbation models | arXiv:2503.23535 | arXiv (cs.LG) | "LPM outperforms existing methods across multiple biological discovery tasks" | method |
| 1.12 | Di Francesco AG, Rubbi A, Jain R, Liò P, 2026 | Differentiable Retrieval-Augmented Generation for Predicting Cellular Responses to Gene Perturbation | arXiv:2603.07233 | arXiv; comments state NeurIPS 2026 main track | "PT-RAG consistently improves distributional similarity and often overall predictive quality" | method |

### Thread 2: LLM- and agent-based systems for single-cell or perturbation biology

| # | Authors, year | Title | Identifier | Venue | Verbatim abstract fragment | Thread |
|---|---|---|---|---|---|---|
| 2.1 | Wu M, Littman R, Levine J, Qiu L, Biancalani T, Richmond D, Huetter J-C, 2025 | Contextualizing biological perturbation experiments through language (PerturbQA / SUMMER) | arXiv:2502.21290 | ICLR 2025 | "We propose PerturbQA, a benchmark for structured reasoning over perturbation experiments." | LLM perturbation reasoning |
| 2.2 | Roohani Y, Lee A, Huang Q, Vora J, Steinhart Z, Huang K, Marson A, Liang P, Leskovec J, 2024 | BioDiscoveryAgent: An AI Agent for Designing Genetic Perturbation Experiments | arXiv:2405.17631 | arXiv (cs.AI); rev. Mar 2025 | "Agents based on large language models have shown great potential in accelerating scientific discovery" | agent, experiment design |
| 2.3 | Hao M, Lee Y, Wang H, Scalia G, Regev A, 2025 | PerTurboAgent: An LLM-based Agent for Designing Iterative Perturb-Seq Experiments | https://proceedings.mlr.press/v311/hao25b.html | MLCB 2025, PMLR 311:44–64 | "We developed PerTurboAgent, an LLM-based agent for designing iterative Perturb-seq experiments." | agent, experiment design |
| 2.4 | Yuan X, Liu X, Zhao J, Zhang Y, Guo H, Tang J, 2026 | Plausibility Is Not Prediction: Contrastive Evidence for LLM-Based Cellular Perturbation Reasoning | arXiv:2606.01042 | arXiv (cs.LG) | "existing methods evaluate perturbation-gene pairs in isolation, without exposing how related perturbations differ" | LLM perturbation reasoning |
| 2.5 | Märtens K, Boubnovski Martell M, Prada-Medina CA, Donovan-Maiye R, 2025 | LangPert: LLM-Driven Contextual Synthesis for Unseen Perturbation Prediction | https://mlanthology.org/iclrw/2025/martens2025iclrw-langpert/ | ICLR 2025 MLGenX workshop | "Systematic genetic perturbation provides critical insights into cell functioning" | LLM perturbation prediction |
| 2.6 | Boubnovski Martell M, Stoisser JL, Phillips L, ... Märtens K, 2026 | MechPert: Mechanistic Consensus as an Inductive Bias for Unseen Perturbation Prediction | arXiv:2602.13791 | arXiv (cs.LG) | "encourages LLM agents to generate directed regulatory hypotheses rather than relying solely on functional similarity" | LLM agents, prediction |
| 2.7 | Phillips L, Boubnovski Martell M, Misra A, Stoisser JL, Prada-Medina CA, Donovan-Maiye R, Märtens K, 2025 | SynthPert: Enhancing LLM Biological Reasoning via Synthetic Reasoning Traces for Cellular Perturbation Prediction | arXiv:2509.25346 | arXiv (cs.AI) | "Synthetic reasoning traces effectively distill biological knowledge even when partially inaccurate" | LLM perturbation reasoning |
| 2.8 | Xiong B, Huetter J-C, Scalia G, Biancalani T, Maleki S, 2026 | LLM-Guided Retrieval for Prediction of Molecular Perturbation Responses | arXiv:2608.01734 | MLGenX @ ICLR 2026 (per arXiv comments) | "LLMs can provide a useful biological prior when used as constrained retrieval modules." | LLM + retrieval |
| 2.9 | Sun J, Zhu O, Chen Y, 2026 | Rethinking Perturbation Prediction Baselines | https://iclr.cc/virtual/2026/10013723 (OpenReview ItrvtNAvof) | ICLR 2026 Gen^2 workshop | "On the same unfiltered data, a nearest-neighbor classifier matches LLM-based methods" | LLM vs simple baseline |
| 2.10 | Chen Y, Zou J, 2024 (online Dec 2024) | Simple and effective embedding model for single-cell biology built from ChatGPT (GenePT) | doi:10.1038/s41551-024-01284-6 | Nature Biomedical Engineering | "Large-scale gene-expression data are being leveraged to pretrain models that implicitly learn gene and cellular functions." | LLM gene embeddings |
| 2.11 | Li M, Li B, Wang J, ... Zang Z, 2026 | CellScientist: From Execution Feedback to Auditable Model-Revision Trajectories for Cellular Perturbation Prediction | arXiv:2605.07335 | arXiv (cs.LG) | "CellScientist produces both a selected predictor and an inspectable record of its development." | agent, model building |
| 2.12 | Zhang F, Liu T, Zhu Z, ... Heng P-A, 2025 | CellVerse: Do Large Language Models Really Understand Cell Biology? | arXiv:2505.07865 | arXiv (q-bio.QM); NeurIPS 2025 poster page seen in search only | "a comprehensive evaluation of LLMs' performance on language-driven single-cell analysis tasks still remains unexplored" | LLM single-cell benchmark |
| 2.13 | Qu Y, Huang K, Yin M, ... Cong L, 2025 | CRISPR-GPT for agentic automation of gene-editing experiments | doi:10.1038/s41551-025-01463-z | Nature Biomedical Engineering 10:245–258 | "CRISPR-GPT leverages the reasoning capabilities of LLMs for complex task decomposition, decision-making" | agent, experiment design (gene editing) |

### Thread 3: what makes a perturbation hard to predict (difficulty, effect heterogeneity, metric pitfalls)

| # | Authors, year | Title | Identifier | Venue | Verbatim abstract fragment | Thread |
|---|---|---|---|---|---|---|
| 3.1 | Viñas Torné R, Wiatrak M, Piran Z, Fan S, ... Brbić M, 2025 | Systema: a framework for evaluating genetic perturbation response prediction beyond systematic variation | doi:10.1038/s41587-025-02777-8 | Nature Biotechnology | "Predicting transcriptional responses to genetic perturbations is challenging in functional genomics." | metric pitfalls, systematic variation |
| 3.2 | Kalygina A, Theus A, Esteban-Medina M, Boeva V, 2026 | Where Simple Baselines Fail: Mapping the Modeling Frontier of Perturbation Prediction | https://icml.cc/virtual/2026/70787 (OpenReview U5Gq071xcI) | ICML 2026 workshop (Generative and Agentic AI for Biology) | "simple baselines define the solved regime, and their failures map the frontier" | per-perturbation difficulty |
| 3.3 | Mejia GM, Miller HE, Leblanc FJA, Wang B, Swain B, de Lima Camillo LP, 2025 | Diversity by Design: Addressing Mode Collapse Improves scRNA-seq Perturbation Modeling on Well-Calibrated Metrics | arXiv:2506.22641 | arXiv (q-bio.GN) | "control-referenced deltas and unweighted error metrics reward mode collapse" | metric pitfalls |
| 3.4 | Huang S, Yang Z, Yu K, Chen J, Li SZ, 2026 | AmbiModBench: Benchmarking Gene Perturbation Prediction Beyond Shared Responses | arXiv:2609.32527 | arXiv (cs.AI) | "strong absolute scores largely reflect shared background rather than target-specific learning" | metric pitfalls |
| 3.5 | Nadig A, Replogle JM, Pogson AN, Murthy M, McCarroll SA, Weissman JS, Robinson EB, ... O'Connor LJ, 2025 | Transcriptome-wide analysis of differential expression in perturbation atlases | doi:10.1038/s41588-025-02169-3 | Nature Genetics 57:1228–1237 | "Single-cell CRISPR screens such as Perturb-seq enable transcriptomic profiling of genetic perturbations at scale." | effect-size heterogeneity |
| 3.6 | Gao Z, 2026 | Do Perturbation Predictors Learn Gene Interactions? Diagnosing Extrapolation in Agentic Screening | arXiv:2610.18880 | NeurIPS 2026 ML4Molecules workshop (per arXiv comments) | "A difficult case arises when both genes in a test pair were seen individually during training" | combinatorial difficulty |

### Thread 4: uncertainty or confidence estimation in perturbation prediction

| # | Authors, year | Title | Identifier | Venue | Verbatim abstract fragment | Thread |
|---|---|---|---|---|---|---|
| 4.1 | Cheng J, Chi C, Zhou J, Xin H, Xia J, 2025 | PRESCRIBE: Predicting Single-Cell Responses with Bayesian Estimation | arXiv:2510.07964 | NeurIPS 2025 (per arXiv comments) | "a multivariate deep evidential regression framework designed to measure both sources of uncertainty jointly" | uncertainty |
| 4.2 | Asiaee A, Aryan K, Long JP, 2026 | Partial Causal Structure Learning for Valid Selective Conformal Inference under Interventions | arXiv:2603.02204 | UAI 2026 (per arXiv comments) | "exchangeability often holds only within subsets of interventions that leave a target variable \"unaffected\"" | conformal uncertainty |

(GEARS, 1.6, also reports an uncertainty output. That comes from prior knowledge and was not checked on the page this session.)

### Thread 5: large Perturb-seq resources released 2023–2026

**No verified entries.** All candidates are listed under unverified leads.

## Examples

These are the 8 entries closest to the paper, chosen across threads: 1.1 Ahlmann-Eltze 2025; 2.1 PerturbQA/SUMMER; 3.1 Systema; 4.1 PRESCRIBE; 1.3 PertEval-scFM; 2.2 BioDiscoveryAgent; 3.2 Where Simple Baselines Fail; 2.3 PerTurboAgent.

## Caveats

- **Quote fidelity.** Every fragment came back through the fetch tool's summariser. Re-check each one character by character on the primary page before citing it.
- **LangPert (2.5)** was verified on mlanthology.org, an anthology mirror, not on the OpenReview or workshop page. Confirm it at OpenReview.
- **Systema and CRISPR-GPT DOIs** were taken from the article URL. The fetched page did not print the DOI.
- **Venue claims marked "per arXiv comments"** (NeurIPS 2026, UAI 2026, MLGenX 2026, NeurIPS 2025) are author-stated. They were not checked on the venue's page.
- **Gap in thread 5.** The paper's resource thread has no verified support. Tahoe-100M, X-Atlas/Orion, the Virtual Cell Challenge commentary and the genome-scale primary CD4+ T-cell screen all need a reader who can open bioRxiv and Cell.
- Nature pages were reached through Nature's cookie-check redirect (`?error=cookies_not_supported`), a normal redirect chain. No block was involved.

## Unverified leads (primary page not opened; do not cite from this list)

| Lead | Identifier | Reason not verified |
|---|---|---|
| Lotfollahi M et al., CPA (compositional perturbation autoencoder), Mol Syst Biol 2023 | doi:10.15252/msb.202211517 | EMBO redirected to link.springer.com. The fetch was denied by the session's permission classifier. Not retried. |
| Kernfeld EM et al., A systematic comparison of computational methods for expression forecasting (PEREGGRN) | bioRxiv 10.1101/2023.07.28.551039; possible Genome Biology doi:10.1186/s13059-025-03840-y | Genome Biology redirects to link.springer.com (denied, see CPA). bioRxiv rate-limited (HTTP 429). |
| Csendes G, Sanz G, Szalay KZ, Szalai B, Benchmarking foundation cell models for post-perturbation RNA-seq prediction, BMC Genomics 2025 | doi:10.1186/s12864-025-11600-2 | BMC/Springer domain, denied as above. Not attempted. Details from search snippet only. |
| Wenteler et al., PertEval-scFM preprint | bioRxiv 10.1101/2024.10.02.616248 | HTTP 429. The ICML version (1.3) is verified instead. |
| Zhang J et al., Tahoe-100M: A Giga-Scale Single-Cell Perturbation Atlas | bioRxiv 10.1101/2025.02.20.639398 | HTTP 429 (second bioRxiv 429). All bioRxiv fetches stopped after this. |
| Roohani Y et al., Virtual Cell Challenge: Toward a Turing test for the virtual cell, Cell 2025 | cell.com S0092-8674(25)00675-0; PMID 40578317 | HTTP 403 from cell.com. Not retried. |
| X-Atlas/Orion: Genome-wide Perturb-seq Datasets via a Scalable Fix-Cryopreserve Platform | bioRxiv 10.1101/2025.06.11.659105 | bioRxiv (429 policy). |
| Genome-scale perturb-seq in primary human CD4+ T cells maps context-specific regulators | bioRxiv 10.64898/2025.12.23.696273 | bioRxiv (429 policy). |
| Istrate A-M et al., scGenePT: Is language all you need for modeling single-cell perturbations? | bioRxiv 10.1101/2024.10.23.619972 | bioRxiv (429 policy). |
| GenePert: Leveraging GenePT Embeddings for Gene Perturbation Prediction | bioRxiv 10.1101/2024.10.27.620513 | bioRxiv (429 policy). |
| Littman R et al., PRESAGE gene-embedding-based prediction | bioRxiv 10.1101/2025.06.03.657653 | bioRxiv (429 policy). |
| Deep Learning-Based Genetic Perturbation Models *Do* Outperform Uninformative Baselines on Well-Calibrated Metrics | bioRxiv 10.1101/2025.10.20.683304 | bioRxiv (429 policy). Same thread as 3.3. |
| Zhu & Jerby, gene-level perturbation predictability (PrtR) | bioRxiv, via PMC12621900 | Only the search snippet was seen. |
| Adduri et al., STATE | bioRxiv | Not attempted (429 policy). |
| Biomni (general biomedical agent) | bioRxiv | Not attempted (429 policy). |
| scPerturBench (Wei/Li et al.) | bioRxiv 2024.12.20.629581 (as recalled) | Not found in search. Identifier unconfirmed. |
| GeneAgent (Nature Methods 2025) | unknown | Search returned nothing. |
| Genome-scale CRISPRi map in hPSCs, Cell Genomics 2026 | unknown | Search snippet only. Cell Press likely 403. |
| PerturbAI in vivo atlas (2026) | bioRxiv / Hugging Face | Press release only. |
| Souza H, Mehta P, Simple models outperform single-cell foundation models on downstream benchmarks | arXiv:2602.16696 | Page opened. The abstract fragment did not confirm that perturbation tasks are in scope, so it is held here. |
| Palayew S, Wang B, Bader G, Towards Applying LLMs to Complement Single-Cell Foundation Models | arXiv:2507.10039 | Page opened. The abstract does not name perturbation prediction. Off-thread. |
| GenePT Revisited (ICLR 2026) | iclr.cc/virtual/2026/10021585 | Not opened. |

## Search log

1. Nature DOI pages for Ahlmann-Eltze and GEARS. These first hit Nature's idp cookie redirect; passing `?error=cookies_not_supported` loaded the pages. Used the same way for scFoundation, Systema, Nadig, GenePT and CRISPR-GPT.
2. arXiv abstract pages opened: 2408.10609, 2405.17631, 2502.21290, 2410.13956, 2606.08816, 2608.01734, 2606.01042, 2505.14919, 2506.22641, 2510.07964, 2610.18880, 2503.23535, 2603.07233, 2605.07335, 2602.13791, 2602.16696, 2509.25346, 2505.07865, 2507.10039, 2609.32527, 2604.27646, 2603.02204.
3. Proceedings and venue pages opened: PMLR v267 (PertEval-scFM), PMLR v311 (PerTurboAgent), icml.cc 2026/70787, iclr.cc 2026/10013723, mlanthology (LangPert), academic.oup.com (Wong 2025).
4. Blocks, reported and not retried: bioRxiv 429 on PertEval-scFM and on Tahoe-100M, after which bioRxiv was not used again; cell.com 403 (VCC); link.springer.com fetch denied by the permission classifier (CPA), after which no Springer/BMC page was attempted.
5. Web searches used for discovery only (no entry is written from them): LangPert; Systema; Virtual Cell Challenge; TxPert/Diversity by Design/PRESAGE; PertEval-scFM ICML; Tahoe-100M; scGenePT/GenePT; Nadig TRADE; Kernfeld PEREGGRN; LLM agent perturbation design; uncertainty in perturbation prediction; scFoundation DOI; CRISPR-GPT/GeneAgent; scPerturBench; "Simple controls exceed"; Csendes BMC; CellVerse/SynthPert; GenePT journal; X-Atlas/primary T-cell Perturb-seq; conformal perturbation; T-cell genome-wide Perturb-seq; perturbation predictability; large Perturb-seq atlases 2025–2026.

## Sources

Every URL in the tables and in search-log items 1–3 was opened this session. Search-engine result pages were used for discovery only.
