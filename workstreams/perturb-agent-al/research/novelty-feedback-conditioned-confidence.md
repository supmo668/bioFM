# Novelty check: feedback-conditioned confidence. UNRATIFIED research note, 2026-11-25

## Overview
**Verdict: partly known.** Precedent exists that shown information moves stated confidence, and that post-attempt confidence tracks correctness better than pre-attempt confidence. No paper found names or measures the confound (confidence change as a difficulty/compute signal contaminated by shown feedback), in multi-agent systems or otherwise.

## Key Concepts
- **Prospective confidence (feeling of knowing, FOK):** given before the attempt.
- **Retrospective confidence (judgement of learning, JOL):** given after the agent's own attempt.
- **Feedback-conditioned confidence:** given after an external signal (error, verdict, peer answer, challenge).

## Implementation: closest works
| # | ID | Shows | Differs | Read |
|---|---|---|---|---|
| 1 | arXiv:2507.03120 (Kumaran, Fleming et al. 2025) | Crosses three factors: the initial answer is shown or hidden; advice is same, opposite or neutral; stated advice accuracy is 50–100%. Confidence is read at both turns. Showing the answer inflates confidence. Opposing advice is weighted about 2.6× the Bayesian update. | Single model; logit confidence. Fictitious advice. Difficulty is held fixed (about 75% accuracy), not predicted. No compute allocation. | Full HTML, first 100k of 135k chars |
| 2 | arXiv:2605.14186 (Cao et al. 2026) | Uses pre-solve FOK and post-solve JOL to decide whether to retry. JOL "usually show[s] a cleaner trend" with accuracy. Ablation accuracy: FOK+JOL 47%, JOL-only 45%, FOK-only 42% (CIs overlap; n=100). | JOL follows the model's own attempt, with no external feedback. Single model. No leakage framing. | Full HTML, first 100k of 133k chars |
| 3 | arXiv:2601.07264 (Xuan et al. 2026) | Verification tools with deterministic feedback (code interpreters) mitigate miscalibration. Evidence tools (web search) induce overconfidence. | Closest to "confidence after a verdict tracks the verdict", but framed as a benefit, not a leak. The abstract does not say when confidence is elicited. | Abstract |
| 4 | arXiv:2311.08596 (Laban et al., FlipFlop) | An "Are you sure?" challenge flips answers 46% of the time and costs 17% accuracy. | Answers, not confidence. | Abstract |
| 5 | arXiv:2606.03437 (Sanz-Guerrero et al. 2026) | Models give up to 26% more confidence to their own answer than to the identical answer framed as the user's. | Framing, with no outcome signal. | Abstract |
| 6 | arXiv:2510.12697 (Hu et al. 2025) | Stops debate when the per-round count of correct agents stabilises (KS test). Assumption 4.4: independence "may be violated if agents copy or reference one another". | Uses agreement, not confidence. Does not analyse whether shown peer outputs shape the stopping statistic. | Full HTML, first 100k of 165k chars |
| 7 | arXiv:2602.12276 (CATTS) | Gates compute on vote entropy and the top-1/top-2 margin. | No feedback in the loop. | Abstract |
| 8 | arXiv:2306.13063 (Xiong); arXiv:2305.14975 (Tian) | Verbal confidence is overconfident (Xiong) yet often better calibrated than token probabilities (Tian). | No feedback condition. Both report some discriminative signal. | Abstract (prior ledger) |
| 9 | arXiv:2610.33029 (Nakayashiki 2026) | Lessons written after a chance failure lead to the worse tool in 11.6% of next runs, against 0.4% for controls. | Outcome leaks into decisions, not confidence. | Abstract |

**By area:**
- **(1) Verbalised calibration (#8):** no.
- **(2) Debate:** partly. Confidence escalation exists, but no paper frames it as leakage. ReConcile (2309.13007), ARMOR-MAD (2606.13197) and DiscoUQ (2603.20975) abstracts are silent on post-feedback confidence.
- **(3) Sycophancy and anchoring (#1, #4, #5):** partly. I found no LLM hindsight-bias study of the model's own confidence.
- **(4) Adaptive compute (#6, #7):** no. These gate on votes or agreement.
- **(5) Metacognition (#2):** partly. Cacioli (2604.15702, abstract) reports retrospective monitoring and prospective regulation "appear dissociable" (r=.17, 20 models).
- **(6) Leakage in uncertainty evaluation:** nothing found.

## Examples: what would be new
**The sharpest defensible statement:**

> In a multi-agent loop, confidence asked after a shown outcome signal predicts that signal, not difficulty as defined independently of it. Confidence asked before feedback does not predict difficulty on the measured tasks. A confidence-change feature therefore adds no difficulty information once the shown signal is a covariate, so a compute gate built on it re-reads the outcome rather than estimating difficulty.

**What is new:**
- the leakage framing;
- the multi-agent, compute-allocation setting;
- the incremental-information test.

**Closest design.** #1 is a controlled-feedback manipulation: it crosses display, advice and accuracy, with confidence read before and after. To serve as a prospective-vs-retrospective test it still needs:
- real, randomised outcome signals (true, false, none);
- verbal confidence;
- a difficulty target independent of the shown signal.

#2 supplies the FOK/JOL split but has no external-feedback arm.

## Caveats
- **"Little or no information" needs scoping.** Xiong, Tian and Kadavath-style results show pre-feedback verbal confidence is partly discriminative. Scope the claim to the tasks and models actually measured.
- **Quotes are unverified.** They came through a summarising fetch tool. Check each one character by character before citing it.
- **Read depth.** Partial full text for #1, #2, #6 (truncated at 100k chars); the rest abstracts only. ReConcile, ARMOR-MAD and DiscoUQ full texts unread.
- **Snell et al. (arXiv:2408.03314).** Abstract only. It does not say whether difficulty is oracle or predicted.
- **Unopened leads, not citable:**
  - arXiv:2505.19184 (Prasad & Nguyen, "When Two LLMs Debate, Both Think They'll Win"; confidence escalation across rounds);
  - PARROT (2511.17220);
  - HindsightBench (2607.18867);
  - the Cash & Trent SJDM 2024 poster;
  - Fleming et al. on human prospective vs retrospective confidence (PMC6192381, PMC4759291).
- **Access.** No 403, 429 or egress block was encountered.

## Sources
- **arXiv pages opened:** 2507.03120, 2605.14186, 2510.12697 (HTML); 2601.07264, 2604.15702, 2311.08596, 2606.03437, 2610.33029, 2602.12276, 2603.20975, 2408.03314, 2606.29490 (abstracts). 2606.29490 was off-question.
- **Prior ledger (not modified):** /Users/mo/github/personal/bioFM/worktrees/perturb-seq-eval/workstreams/perturb-seq-eval/findings-staging/2026-11-22-literature-review.md.
