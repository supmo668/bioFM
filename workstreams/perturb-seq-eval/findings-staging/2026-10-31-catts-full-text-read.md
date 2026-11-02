# CATTS full-text read — staging note (dispatch #812)

**Status: staging note, UNRATIFIED. Report only. Nothing in `paper/` or any public surface is touched.**
**Amended 2026-10-31 per CTO #814:** correction to my #813 gloss (below, §(i)); verification-status table added.
**Amended 2026-10-31 per CTO #817:** citation key verified at the ref; Lee-2022/Lee-2026 collision rule; cs.AI vs cs.LG fact recorded. The table is kept permanently (#817 §3).
Authorized by CTO #812 §2 (reading a primary source is not principal-gated; writing a claim is). Scope limits
from #812, applied: this note reports only **(i)** what CATTS's signal is computed over, **(ii)** what it is
compared against, **(iii)** what "working" means there — verbatim quotes with section refs. **It contains no
sentence relating CATTS's method to ours, affirmative or negated.** Where the material invites a comparison, the
quote is recorded and the note stops.

## Verification status (who has which fact at the ref)

| Fact | Section | Verified at the ref by |
|---|---|---|
| Title; "by up to 11.8% over majority voting" | title page, Abstract | CTO (#812, #814) and me |
| Citation key `lee2026catts`: first author **Nicholas Lee**; Lee, Erdogan, John, Krishnapillai, Mahoney, Keutzer, Gholami; v1 2026-02-12, v2 2026-08-14; primary **cs.AI**, cross-list cs.CL | title page / arXiv listing | CTO (#817, at the ref) and me |
| "we assume a fixed base agent, and we focus on how to allocate inference-time compute efficiently at test time." | §2 | CTO (#814, exact) and me |
| Vote distribution is over $N$ candidate actions sampled from **one base model at each time step** (eq. 1–2) | §3.1 | CTO (#814) and me |
| Entropy / margin definitions (eq. 6–7); gate (eq. 9–10); threshold sweep | §4.1, §4.2 | **me only** |
| Successful-vs-failed trajectory contrast; 495 task-runs; Fisher exact test, $p=0.026$; binned net advantage $-4.4\%$ / $+4$–$6\%$ | §4.1 | **me only** |
| Table 3 figures (42.4→47.9 %, 20.2→32.0 %); "a consistent 2.4% gain"; arbiter on 40–60 % of steps | §4.3 | **me only** |
| Absence of any pre-registration, gate or directional hypothesis in the sections read | §3–§5 | **me only** (an absence claim about sections read; appendices unread) |

**Rule (CTO #814 §5):** nothing in the "me only" rows carries a sentence in `paper/` until one of us has it at the ref.
The pre-registration contrast is the most tempting and the least verified; it is not written anywhere.

**Name-collision hazard (CTO #817 §1, standing rule for this project).** This project already uses "Lee 2022" as the
name of a *failure* (the lung track's abstract-misread). CATTS is a genuine, load-bearing **Lee 2026** (`lee2026catts`).
Two different Lees, one a cautionary tale and one a real citation. **Write the year and the key every time; never
write "the Lee paper".**

**Category fact on the table (CTO #817 §1; a framing question for the principal, not a defect).** CATTS's primary
class is cs.AI (cross-listed cs.CL). Our `projects/perturb-seq-eval/paper/arxiv.toml` declares: `62:primary = "cs.LG" 63:cross_list = ["q-bio.QM"]`.
The nearest prior art therefore sits in cs.AI.

## Source and how it was read

- arXiv:2602.12276 **v2**, "Agentic Test-Time Scaling for WebAgents", Nicholas Lee, Lutfi Eren Erdogan, Chris
  Joseph John, Surya Krishnapillai, Michael W. Mahoney, Kurt Keutzer, Amir Gholami (UC Berkeley / ICSI / LBNL).
  Header line in the source: "arXiv:2602.12276v2 [cs.AI] 14 Aug 2026". License line: "arXiv.org perpetual
  non-exclusive license".
- Fetched 2026-10-30 (local) into an isolated temp directory: `https://arxiv.org/html/2602.12276v2` (HTTP 200,
  438,128 bytes) and `https://arxiv.org/pdf/2602.12276v2` (HTTP 200, 663,582 bytes). No proxy 403, no egress
  block, no retry.
- Read from the **HTML** rendering, converted to text with the Python stdlib parser (`python3 -I`), keeping each
  `<math>` element's `alttext` (the authors' LaTeX) inline — equations below are therefore the authors' own
  symbols, not my transcription. The PDF was downloaded but not text-extracted (no extractor installed); it was
  not needed.
- Sections read in full: Abstract, §1, §2, §3 (intro), §3.1, §4.1, §4.2, §4.3, §5. Appendices A–O: **not read**,
  except single lines surfaced by grep (noted where quoted). Figures: captions only (images not viewed).
- Earlier search snippets (2026-10-30) gave different headline numbers for this paper (e.g. "up to 9.1%",
  "2.3x fewer tokens") than the v2 source does; those were snippets of an unknown version and were not used.
  Every number below is a quote from v2.

## (i) What the signal is computed over

**The unit is one agent, one step, N sampled candidate actions.**

> "We study tool-using web agents that interact with a browser over multiple steps. The underlying agent is
> prompted with ReAct (Yao et al., 2023b) and uses gpt-oss-120b as the base model. At each step $t$ , the agent
> observes a cleaned HTML representation of the current page state and outputs a structured action space of 8
> tools including click, type_text, scroll, etc." — §3.1

> "At each time step $t$ , the agent observes $o_{t}$ and samples $N$ candidate actions from the base model:
> $\tilde{a}^{(i)}_{t}\sim M(\,\cdot\mid o_{t}\,),\quad i=1,\dots,N.$ (1)" — §3.1, "Action Clustering and Vote Distributions"

> "We parse candidates into structured actions to obtain a set of action clusters $\mathcal{A}_{t}$ . Let
> $n_{t}(a)$ denote the number of candidates assigned to cluster $a\in\mathcal{A}_{t}$ . This induces a
> distribution over the sampled actions $p_{t}(a)=\frac{n_{t}(a)}{N},$ (2) which parameterizes how much the
> sampled candidates agree on each distinct action at step $t$ ." — §3.1

> "We therefore use a lightweight semantic deduplicator LLM to cluster candidate actions into semantically
> equivalent buckets before counting votes (See Appendix B for the prompt and Appendix D for additional
> analysis)." — §3.1

**The two statistics, computed on that per-step vote distribution:**

> "Given the vote distribution $p_{t}(\cdot)$ over action clusters $\mathcal{A}_{t}$ , we compute two
> uncertainty statistics: $H_{t}\;=\;-\sum_{a\in\mathcal{A}_{t}}p_{t}(a)\,\log p_{t}(a),$ (6)
> $\Delta_{t}\;=\;p_{t}(a^{(1)}_{t})-p_{t}(a^{(2)}_{t}),$ (7) where $a^{(1)}_{t}$ and $a^{(2)}_{t}$ are the
> highest- and second-highest-probability clusters under $p_{t}(\cdot)$ . Intuitively, $H_{t}$ measures overall
> disagreement (higher entropy means votes are spread across multiple options), while $\Delta_{t}$ measures
> decisiveness (larger gaps indicate a clear winner). High-consensus regimes correspond to low $H_{t}$ and high
> $\Delta_{t}$ , contentious regimes correspond to high $H_{t}$ and low $\Delta_{t}$ ." — §4.1

**How the authors position the signal's provenance (their words, §2):**

> "We use vote-derived uncertainty to gate arbitration at each step, enabling dynamic allocation without
> requiring token-level confidence access. Unlike prior confidence-filtering approaches that operate on
> single-shot reasoning traces, we derive uncertainty from agreement among multiple sampled candidates, and we
> operate online in environments where errors compound across steps." — §2

> "Multi-agent debate and voting strategies (Du et al., 2024) and extreme decomposition via massive redundancy
> (Meyerson et al., 2025) offer alternative paths to reliability, often at prohibitive computational costs. Our
> work is orthogonal to these training-based and architectural improvements: we assume a fixed base agent, and
> we focus on how to allocate inference-time compute efficiently at test time." — §2

*(Recorded and stopped. The first §2 quote is the authors' own placement relative to "prior confidence-filtering
approaches". In the second, "these training-based and architectural improvements" has no fixed referent in the
text; the preceding sentence names "Multi-agent debate and voting strategies (Du et al., 2024)" among
"alternative paths to reliability", so the referent is probable by sentence order — probable is not a quote.
No sentence is drawn from either here.)*

> **CORRECTION 2026-10-31 (CTO #814 §2).** My report of this note in dispatch #813 said "multi-agent debate is
> named as 'orthogonal'". That attached the word "orthogonal" to a referent the source does not fix. It is an
> inference from sentence order, not a quote, and is withdrawn. The two §2 quotes above are unchanged; only my
> gloss was wrong. Lesson recorded: a correct reading of a real sentence attributed to a referent the text does
> not fix is the same failure class as a method claim from an abstract.

**What the signal gates:**

> "Let $U_{t}$ be a scalar uncertainty score computed from the vote distribution $p_{t}(\cdot)$ . CATTS applies
> a threshold $\tau$ to gate arbitration: $a_{t}=\begin{cases}\arg\max_{a}p_{t}(a),&U_{t}\leq\tau\\
> \textsc{Arbiter}(o_{t},\mathcal{A}_{t},\{n_{t}(a)\}_{a\in\mathcal{A}_{t}}),&U_{t}>\tau.\end{cases}$ (9)
> We instantiate $U_{t}$ in two effective variants: $U^{(\mathrm{ent})}_{t}=H_{t},\quad
> U^{(\mathrm{mrg})}_{t}=1-\Delta_{t}.$ (10)" — §4.2

> "For both settings, we tuned $\tau$ via running a simple grid over thresholds (e.g.,
> $\tau\in\{0.2,0.3,\dots,0.8\}$ ) and report results across this sweep (with the best-performing setting
> indicated where relevant)." — §4.2

## (ii) What it is compared against

**The outcome variable is task success (binary per task), and the comparison is between selection policies at
each step — not a rank correlation of the signal with a continuous error.**

> "The central question of our study is this: Given the current observation $o_{t}$ and a multi-set of
> candidates $\{\tilde{a}^{(i)}_{t}\}_{i=1}^{N}$ , how should we select the executed action $a_{t}$ to maximize
> task success under a token budget?" — §3.1

> "We evaluate on WebArena-Lite (Liu et al., 2025), which has 165 tasks with programmatic success checks, and
> Online-Mind2Web (Xue et al., 2025), which has 300 tasks across diverse real-world websites evaluated using an
> LLM-as-a-judge (Zheng et al., 2023) protocol with Qwen3-VL-30B-A3B-Instruct. … We also evaluate on GoBrowse
> (Gandhi and Neubig, 2025) (341 tasks); full results are provided in Appendix M." — §3.1

> "We measure compute cost using the total token count per task, defined as the sum of prompt (input) and
> completion (output) tokens across all model calls … All results on WebArena-Lite are averaged across three
> different seeds unless otherwise noted; Online-Mind2Web results are single-run due to compute constraints." — §3.1

**Where the signal is related to success, it is by (a) group contrast of trajectory-averaged statistics and (b)
a binned net-advantage analysis — both descriptive, with one Fisher test on override counts:**

> "Empirically, successful trajectories tend to exhibit lower entropy and higher margins, whereas failed
> trajectories show the opposite trend. Figure 2 plots $\bar{H}$ and $\bar{\Delta}$ against the index of each
> step, separately for successful and failed runs, showing that disagreement typically spikes at pivotal
> decision points and that these spikes are more pronounced (or more frequent) in failed runs." — §4.1
> *(the two task-level averages are defined in their eq. (8), §4.1; symbols as rendered in the figure caption)*

> "To quantify this pattern, we analyzed all 495 task-runs from our arbiter experiments, classifying each task
> by whether the arbiter overrode the majority vote on any high-consensus step ( $\Delta_{t}>0.7$ ). … Tasks
> without high-consensus overrides succeed at 46.9%, compared to 35.0% for tasks with at least one such
> override: a significant 11.9% difference ( $p=0.026$ , Fisher's exact test). This effect exhibits a
> dose-response pattern: tasks with zero overrides succeed at 46.9%, those with exactly one at 36.6%, and those
> with two or more at 29.6%." — §4.1

> "At low entropy (0.0-0.3), the arbiter shows a net disadvantage of $-4.4\%$ , consistent with the override
> failures above. However, at higher entropy levels, the arbiter yields positive net advantages ( $+4$ - $6\%$ ),
> demonstrating that arbitration adds value when votes are diverse and majority voting lacks a clear signal." — §4.1

The baselines CATTS is scored against are named in §4.3 / Table 3: "majority voting, uniform arbitration,
DeepConf, and CATTS" (§4.3, Figure 4 sentence). *No pre-registration, gate, or directional hypothesis is stated
anywhere in the sections read.*

## (iii) What "working" means there

**"Working" = higher task-success rate than majority voting and/or always-arbitrate at equal or lower token
cost, on three web-agent benchmarks, with the gain quoted at the best threshold and at the sweep average.**

> "CATTS improves performance on WebArena-Lite, Online-Mind2Web, and GoBrowse by up to 11.8% over majority
> voting while using fewer tokens than uniform scaling, providing both efficiency gains and an interpretable
> decision rule." — Abstract

> "On WebArena-Lite, margin-gated CATTS achieves 47.9% at only 405K tokens, a gain over majority voting while
> using 12% fewer tokens. On Online-Mind2Web, entropy-gated CATTS ( $\tau{=}0.7$ ) achieves 32.0%, a $+11.8\%$
> gain over majority voting and $+4.6\%$ over always-arbitrate. Averaging across all thresholds in our sweep on
> WebArena-Lite, CATTS achieves 45.6%, which is still a consistent 2.4% gain that does not depend on threshold
> selection (See Appendix H for more analysis)." — §4.3

> Table 3 (§4.3), as rendered: WebArena-Lite — Majority vote 42.4% / 460K; Always-arbitrate 42.8% / 442K;
> CATTS (entropy, best $\tau$) 45.5% / 409K; CATTS (margin, best $\tau$) 47.9% / 405K. Online-Mind2Web —
> Majority vote 20.2% / 888K; Always-arbitrate 27.4% / 960K; CATTS (entropy) 32.0% / 922K; CATTS (margin)
> 30.0% / 906K. *(Which of the two CATTS rows is entropy- vs margin-gated is inferred from the §4.3 prose, since
> the row labels' math was rendered as symbols; the numbers are as printed.)*

> "In our experiments, the arbiter is invoked on approximately 40–60% of steps on average, concentrating compute
> on the steps most likely to benefit." — §4.3

> "These gains generalize across model families, including Gemini 3.1 Flash Lite and Qwen3.5-122B-A10B
> (Appendix N)." — §4.3 *(Appendix N not read.)*

> "We find that naive per-step scaling shows diminishing or negative returns, and that LLM-based arbitration
> helps on contentious steps but can override correct high-consensus decisions. Vote-derived uncertainty
> statistics (entropy and margin) reliably distinguish these regimes. CATTS uses this signal to dynamically
> allocate compute, achieving consistent improvements across WebArena-Lite, Online-Mind2Web, and GoBrowse (up
> to $+11.8\%$ over majority voting) while using fewer tokens." — §5

On the robustness of the "working" claim, from the appendix summary surfaced by grep (Appendix I.5, not read in
context): "Since CATTS typically improves over majority voting by 3–12%, losing ${\sim}1\%$ to imperfect
calibration preserves the vast majority of the benefit."

## Recorded, and stopped

The following are facts of the source that a reader will want next to ours. They are listed as quotes-with-refs
only; this note draws no sentence from them, per #812 §2.

- The sign convention of the gate: arbitration is spent when $U_{t}>\tau$, i.e. when entropy is **high** /
  margin is **low** (eq. 9–10, §4.2); and "successful trajectories tend to exhibit lower entropy and higher
  margins" (§4.1).
- The signal is per-step over $N$ samples of one base model (eq. 1–2, §3.1); "we assume a fixed base agent"
  (§2).
- The success measure is binary task success under programmatic checks (WebArena-Lite) or an LLM judge
  (Online-Mind2Web) (§3.1); Online-Mind2Web is "single-run" (§3.1).
- The reported effect of the signal on success is a contrast of group means / bins and one Fisher exact test
  on override counts (§4.1); the headline gain is a difference in success rate at a tuned threshold (§4.3).

## Not established

- Anything in Appendices A–O beyond the grep-surfaced lines quoted above (deduplicator prompt, arbiter prompt,
  GoBrowse results, other model families, threshold sensitivity, failure examples).
- Whether $N$ varies across the headline results (Table 3 is captioned with an $N$ value whose math did not
  render in my extraction; not transcribed).
- Figure 2/3/4 contents beyond their captions.
- Any statement about how CATTS's signal relates to ACE, $\Delta C$, or TDI — deliberately not made; that is
  the principal's question (#809 ruling 3) and this note is its input, not its answer.
