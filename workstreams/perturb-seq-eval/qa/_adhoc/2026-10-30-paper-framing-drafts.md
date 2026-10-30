# Paper framing drafts — UNRATIFIED (dispatch #807)

**Status: UNRATIFIED DRAFT. Nothing here has been applied to `paper/` or any public surface.**
Drafted 2026-10-30 by the perturb-seq-eval worktree agent in reply to CTO dispatch #807 (principal-approved
framing review). The principal ratifies or rejects each item; only then does any text move into
`projects/perturb-seq-eval/paper/paper.tex`. No biological number appears here. No identifier is paired
with a substance. No result number is typed by hand: every gate claim below is either a macro name from
`paper/sections/generated_numbers.tex` or a verbatim quote from `paper/sections/results.tex`, with the line cited.

**CTO #809 (2026-10-30 23:50):** items 2+3 accepted as drafts; CATTS and the SPRT governor VERIFIED at the arXiv ref by the CTO; ruling 1: (b)-type soften adopted; ruling 2: no differs-from sentence from abstracts (draft (b) superseded by (b″) below); ruling 3: CATTS is prior art for contributions 1–2 and reports the idea working where ours fails — ESCALATED to the principal; a 'negative replication on a new substrate' reframing is a candidate only and is NOT drafted here. **HOLD.**

Source state: branch `perturb-seq-eval` at `69ae988` (= `origin/main`, PR #35 merged). Line numbers refer to that revision.

---

## Item 2 — Reorder the contributions (`paper.tex:117–140`)

### Why this order

The dispatch ranks the four contributions by what survived the gates: pre-registered design first, provenance
record second, the metrics third, the probe/recommender last. The evidence for that ranking, quoted from the
paper's own result surface rather than from memory:

| Standing | Quote (verbatim) | Source |
|---|---|---|
| Overall tally | `\resGateSummary` = "4 of 5 gates pass; H5 fails (0 unevaluated)" | `generated_numbers.tex:37` |
| ACE | "both tests fail the one-sided gate. The H4 pass is carried by the confidence-drop component and by the composite that inherits it" | `results.tex:184–185` |
| ACE direction | "The two $\mathrm{ACE}_{\mathrm{norm}}$ point estimates are negative … against the pre-registered positive direction" | `results.tex:181–183` |
| CSD, WFR | "structurally undefined for the lifecycle (not evaluated)" | `results.tex:172` |
| Four-component TDI | "The four-component TDI of equation~(\ref{eq:tdi}) is \emph{not evaluated}" | `results.tex:126–127` |
| Transfer (H5) | "The calibrated index does not transfer at the pre-registered level; no re-fit, threshold or sign change is applied." | `results.tex:201–202` |
| H5 verdict | `\resHFiveVerdict` = `\textbf{FAIL}` | `generated_numbers.tex:49` |
| H4 verdict | `\resHFourVerdict` = `\textbf{PASS}`; `\resHFourNPassing` of `\resHFourNTests` | `generated_numbers.tex:105, 75, 76` |

### Current text (for reference; `paper.tex:117–140`)

Order today: (1) metrics + TDI, (2) preflight probe + recommender, (3) pre-registration + test, (4) provenance record.

### Proposed replacement (LaTeX, drop-in for `paper.tex:117–140`)

```latex
\paragraph{Contributions.} We make four contributions, all within the
empirical frame of Perturb-seq response prediction~\citep{norman2019perturbseq,%
adamson2016perturbseq} but generalising to any propose-critique-vote system.
They are listed in the order of what the evidence supports.

\begin{enumerate}[leftmargin=*]
  \item We pre-register five hypotheses and their gates
        (\S\ref{sec:results}; \texttt{paper/PREREGISTRATION.md}), each locked
        before any data existed, and test them on \resNTasks{} held-out K562
        tasks from \textsc{Adamson 2016} and \textsc{Norman 2019}, with a
        trainer sweep and an agentic lifecycle run over the identical task set
        in one process. Both outcomes are reported: \resGateSummary.
  \item We release a provenance-complete run record --- git revision,
        resolved configuration, resolved library versions, dataset digests,
        task plan, label contract, and the serving model of every agent step
        --- together with the calibration harness and the
        \textsc{MassGen}-installable evaluation skill
        (\S\ref{sec:reproducibility}).
  \item We formalise four easy-to-compute observables of a multi-agent run ---
        ACE, CSD, $\Delta C$/$\Delta$ACE, and WFR --- and combine them into a
        scalar Task Difficulty Index (TDI). Of these, the lifecycle traces
        supply two: the confidence-drop component and the composite that
        inherits it rank tasks by held-out error within both screens, while
        ACE fails its one-sided gate in both (\S\ref{sec:tdi-real}); CSD and
        WFR are structurally undefined for the lifecycle and are not
        evaluated.
  \item We introduce a \emph{preflight probe}: a single shallow round whose
        four-dimensional signature is intended to serve as a sufficient
        statistic for a Bayesian recommender over orchestration
        hyperparameters $\varphi = (N, R, \textrm{backbone})$. The
        cross-dataset transfer such a recommender would rely on did not reach
        the pre-registered level (H5, \S\ref{subsec:h5}), so the probe is
        proposed here and not validated.
\end{enumerate}
```

### What changed beyond the order (each is a separate ratification point)

- **R2-a.** The hand-typed `$41$` in the old item 3 is replaced by the macro `\resNTasks{}` (`generated_numbers.tex:179`). Same value; the point is that no number is typed by hand in the contributions either.
- **R2-b.** Item 3 (metrics) now carries its outcome inline. Wording is a paraphrase of `results.tex:172`, `:184–185` and `tab:tdi-real`'s caption (`:175–177`); it introduces no claim those lines do not make. The cross-reference `\S\ref{sec:tdi-real}` already exists (`results.tex:124`).
- **R2-c.** Item 4 (probe) now states that the probe is "proposed here and not validated" and ties that to H5. **This is the one sentence that goes beyond quoting**: it is my inference that a recommender over $\varphi$ relies on transfer. If the principal reads the probe's value as independent of H5, strike the last sentence and keep the rest. Supporting check: `grep -n -i 'preflight probe|recommender|sufficient statistic'` over `paper.tex` and `sections/*.tex` finds the probe only in the contributions (`paper.tex:125–127`), its own section (`paper.tex:265–`, definitions and a MAP recommender) and a limitations paragraph (`paper.tex:524–526`: "Our Bayesian recommender is also a MAP estimator; full posterior sampling would expose uncertainty currently swept into point predictions"); `results.tex` mentions "preflight probes" only as a spend line (`results.tex:222`). No section reports an evaluation of the probe or recommender on v0.6.0 data, so "not validated" is a statement about what the paper contains, not an inference.
- **R2-d.** The lead-in sentence "They are listed in the order of what the evidence supports." is new. Optional; it tells the reader why the order is what it is.
- **R2-e.** Scope paragraph (`paper.tex:142–147`) is untouched.

---

## Item 3 — The novelty claim (`paper.tex:169–171`)

### The sentence today

> "None of these works, to our knowledge, use the group's internal confidence/critique distribution as an explicit difficulty signal."

Read narrowly it is a claim about the five works cited in that paragraph (AutoGen, MassGen, Archon, MAV, CellForge). Read as a reader will read it, it is a novelty claim about the field. The standing method rule: a sampled probe can refute such a claim; it can never establish one.

### What I searched (the ledger)

Date: 2026-10-30. Two corpora, queries recorded verbatim. Result caps are the tools' caps, not a judgment of relevance.

| # | Corpus | Query (verbatim) | Returned |
|---|---|---|---|
| C1 | Consensus (Semantic Scholar / OpenAlex / PubMed index; capped at 3 results, unauthenticated) | "multi-agent LLM system agent confidence entropy as task difficulty signal for adaptive test-time compute allocation" | 3 |
| C2 | Consensus | "inter-agent disagreement or critique distribution in multi-agent debate predicts task difficulty and allocates inference compute" | 3 |
| C3 | Consensus | "self-consistency answer entropy estimates question difficulty for adaptive sampling and early stopping in LLM reasoning" | 3 |
| U1 | Undermind semantic search (global corpus, top-20) | sample abstract: "We use the distribution of confidence scores and critiques across a group of cooperating LLM agents as an explicit signal of task difficulty, and allocate test-time compute (number of agents, number of rounds) adaptively according to that signal in a multi-agent propose-critique-vote system." | 20 |

Primary-source checks: CATTS metadata read from `arxiv.org/abs/2602.12276` (title, authors, "[Submitted on 12 Feb 2026 (v1), last revised 14 Aug 2026 (this version, v2)]", cs.AI). The other abstracts below are quoted from the corpus records returned by the tools; I did not read their PDFs.

### What the probe found — the claim is refuted at the corpus level

Three returned works use a group-level or vote-level confidence signal to govern compute. Quotes are verbatim from the returned abstracts:

1. **CATTS** — Lee et al., "Agentic Test-Time Scaling for WebAgents", arXiv:2602.12276 (C1 #1): "uncertainty statistics derived from the agent's own vote distribution (entropy and top-1/top-2 margin) correlate with downstream success and provide a practical signal for dynamic compute allocation … uses vote-derived uncertainty to allocate compute only when decisions are genuinely contentious." — *Vote-distribution entropy of one agent's parallel samples, not a heterogeneous group's confidence/critique; but it is entropy-of-a-vote-distribution as an explicit compute-allocation signal.*
2. **UAAD** — Liu et al., "Uncertainty-Aware Adaptive Debate for Robust and Efficient Large Language Model Reasoning", ICCVDM 2026, DOI 10.1109/ICCVDM71812.2026.11709092 (U1): "combines normalized token entropy, answer-level self-consistency, and cross-agent divergence to localize risky steps; a scheduler selects agents, rounds, and rebuttal focus, while stable consensus terminates debate." — *Cross-agent divergence as a difficulty signal that selects agents and rounds. This is the closest match to our sentence. The abstract itself says the results "are simulation outputs from reconstructed transitions, not verified live gains".*
3. **SPRT governor** — Morandi, "Sequential Consensus for Multi-Agent LLM Debates: A Wald-SPRT compute governor…", arXiv:2605.19193 (U1): "most recipes pick a fixed round count, over-spending on easy items and under-spending on hard ones … an LLM judge emits a [0,1] consensus score on the latest agent positions; a Wald monitor … stops when either boundary is crossed." — *A group-consensus score governs round count; the signal is a judge's score on the group, not the agents' own confidences.*

Adjacent, not counterexamples, but they bound the claim: Zhu et al. 2026 (ACL; "confidence-modulated debate protocol in which agents express calibrated confidence and condition their updates on others' confidence" — confidence used for belief update, not compute); Elahi et al. 2026 ("confidence-aware routing and log-odds pooling" across agents); Jiang et al. 2026 (audit of "confidence-routed broadcast protocol"); Fang et al. 2026 (critique-and-routing controller that "decides whether to stop or continue"); DIAL, Li et al., arXiv:2605.06908 ("Existing methods typically use confidence-, uncertainty-, or difficulty-based gates" for adaptive agent compute); Adaptive-Consistency, Aggarwal et al. 2023, arXiv:2305.11860 (agreement-based adaptive sample count, single model).

**Dating.** All three counterexamples carry 2026 dates (Feb, May, Aug). Our v0.6.0 run is dated `\resRunId` = `20260929T035447Z-ce5f237` (`generated_numbers.tex:210`), and the arXiv submission would be dated after today, so they are prior art for the submission whatever the order of conception. I did NOT establish whether any of the five works the sentence literally names (AutoGen, MassGen, Archon, MAV, CellForge) uses such a signal — that would require reading those five papers, which I have not done in this session.

### Two drafts

**(a) SUBSTANTIATE** — bound the claim by a described method. Not recommended, because the method already found counterexamples; the only honest substantiated version is a claim about the five named works, and I have not verified even that.

```latex
Of the five systems above, none that we have read uses the group's internal
confidence/critique distribution as an explicit difficulty signal; we make no
claim beyond those five.
```
(Requires the author to confirm the five were read for this question. Unverified as of this draft.)

**(b) SOFTEN — say what was searched and found.** ~~Recommended~~ **SUPERSEDED by (b″) per CTO #809 ruling 2** (2026-10-30): this draft characterises the three works' methods ("vote-distribution entropy of a single agent's parallel samples", "cross-agent divergence scheduling the agents and rounds", "a judge's consensus score as a sequential stopping rule") and asserts "We differ in the signal … target … design". Those are claims about what the papers DO, made from abstracts only. An abstract suffices to refute a universal sentence; it does not suffice to assert how we differ. Kept here for traceability; do not apply.

```latex
Closest to our question are works that gate compute on a group-level
uncertainty signal: vote-distribution entropy of a single agent's parallel
samples~\citep{lee2026catts}, cross-agent divergence scheduling the agents and
rounds of a debate~\citep{liu2026uaad}, and a judge's consensus score as a
sequential stopping rule~\citep{morandi2026sprt}. We differ in the signal
(the agents' own stated confidences and their change across rounds, in a
heterogeneous role-specialised group), in the target (held-out prediction
error on a biological task rather than answer accuracy), and in the design
(pre-registered gates with both outcomes reported); we do not claim the
signal is new.
```

Reasoning: the asymmetry the dispatch names is real and the probe has already shown it — one found counterexample would have cost the whole paper's credibility, and the probe found three near ones in twenty-nine returned records across two corpora. Draft (b) converts an absence claim into a positioning statement that is true whatever else exists in the corpus. The three `\citep` keys are placeholders; the bib entries must be written from the arXiv/DOI pages (ids above), not from this file.

**(b″) SOFTEN without characterising the prior work — the form CTO #809 ruling 2 permits. Recommended.**

Names the works, cites their own abstracts as the source, and claims nothing about their methods beyond
that the works exist and gate compute on a confidence- or consensus-type signal in their own words. No
"we differ in…" sentence; that waits on a full-text read, which has not been done.

```latex
We do not claim the signal is new. Recent work reports gating test-time
compute on confidence- or consensus-type signals from an agent's own vote
distribution or from a group of agents~\citep{lee2026catts,morandi2026sprt,%
liu2026uaad}; we cite their abstracts and have not reproduced or re-derived
their methods, and we make no claim here about how our signal relates to
theirs.
```

Source for each \citep (abstract only, quoted in the ledger above): CATTS arXiv:2602.12276 (CTO-verified at the
ref, #809); Wald-SPRT governor arXiv:2605.19193 (CTO-verified at the ref, #809); UAAD DOI
10.1109/ICCVDM71812.2026.11709092 (NOT verified by the CTO; my corpus-record quote only — drop this key if the
principal wants only CTO-verified citations).

**(b′) Minimal variant** if the principal wants the smallest edit: replace the sentence with

```latex
Works that gate test-time compute on a confidence- or consensus-type signal
exist~\citep{lee2026catts,morandi2026sprt,liu2026uaad}; we do not claim the
signal is new.
```
(Amended 2026-10-30 per #809 ruling 2: the earlier form said "we differ in signal, target and design" — a differs-from claim from abstracts — and is withdrawn.)

---

## Item 1 — Retitle: HELD. A note on what the title would have to claim

No candidate title is offered. The dispatch asks only for what a title would have to claim to match the surviving result.

Today the title asks "Does Agent Confidence Entropy Predict Task Difficulty?" (`paper.tex:34–36`; identical string in `CITATION.cff:5–8`). The surviving result, quoted:

- ACE: "both tests fail the one-sided gate" (`results.tex:184`); point estimates "against the pre-registered positive direction" (`results.tex:183`).
- What passed: "The H4 pass is carried by the confidence-drop component and by the composite that inherits it" (`results.tex:184–185`).
- Transfer: "The calibrated index does not transfer at the pre-registered level" (`results.tex:201–202`).
- Tally: "4 of 5 gates pass; H5 fails (0 unevaluated)" (`generated_numbers.tex:37`).

So a title that matched the evidence would have to claim **(i)** that the question was asked under a pre-registered, provenance-complete design and answered either way; **(ii)** that the answer for confidence *entropy* is no (direction reversed, gate failed in both screens); **(iii)** that the confidence *drop* across rounds does rank tasks within each screen; and **(iv)** that the calibrated index does not transfer between screens. The current title's subtitle already carries (i); its headline question carries none of (ii)–(iv) and the reader must reach the abstract for the answer. A question-form title is not itself wrong — the paper does answer the question — but the answer is "no" for the named quantity and "yes" for a different one the title does not name.

Decision stays with the principal as author of record (fork (a)/(b)/(c) in #807). Nothing in this note changes the CFF, the Zenodo record or `isIdenticalTo`.

---

## Not established / not done

- Not established: whether any of the five works named in the novelty sentence uses such a signal (not read this session).
- Not established: the full text of the three counterexamples — abstracts only, from corpus records; CATTS metadata checked at the arXiv abstract page.
- Not established (and now the blocking question per #809 ruling 3): whether CATTS's vote-distribution signal is close enough to ACE for 'does not reproduce' to be the honest word. Full-text read of arXiv:2602.12276 required; not done; principal's call.
- Not done: any edit to `paper/`, `CITATION.cff`, the bib, Zenodo, Figshare, or any HACP surface.
- Not done: the figures question (`\includegraphics` count zero; `graphicx` loaded) — not dispatched; principal owns it.
- Not located: the verbatim text of "Authorization (1)" that #807 cites. I applied it as paraphrased in the dispatch (draft to a staging file, marked unratified, outside `paper/`). If the authorization says more, this file should be checked against it.
- Search caveat: Consensus returned 3 per query (unauthenticated cap); Undermind returned the top 20 of a bounded semantic match. Neither is a systematic review.
