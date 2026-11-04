---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-30T23:48
status: created
priority: normal
size: task
subject: "Re #807: items 2+3 DRAFTED (unratified, outside paper/) at 24b7579, pushed. Item 3 finding: the novelty claim is REFUTED at corpus level — three 2026 works gate compute on a group/vote confidence signal; recommend SOFTEN. Item 1 held; title note included, no candidate title."
in_reply_to: 807
---

# Re #807: items 2+3 DRAFTED (unratified, outside paper/) at 24b7579, pushed. Item 3 finding: the novelty claim is REFUTED at corpus level — three 2026 works gate compute on a group/vote confidence signal; recommend SOFTEN. Item 1 held; title note included, no candidate title.

Agent: biofm/matthew-mo/perturb-seq-eval
Branch: perturb-seq-eval @ 24b7579 (base 69ae988 = origin/main), pushed to origin/perturb-seq-eval via /sync.
File: workstreams/perturb-seq-eval/qa/_adhoc/2026-10-30-paper-framing-drafts.md — marked UNRATIFIED; nothing in paper/, CITATION.cff, bib, Zenodo, Figshare or HACP was touched.

ITEM 2 (reorder) — drafted as a drop-in for paper.tex:117–140, order: pre-registration (with \resGateSummary inline) → provenance record → metrics with outcome stated → probe/recommender with the H5 caveat. Every gate claim is a macro name or a verbatim results.tex quote with line cited; the hand-typed $41$ becomes \resNTasks{} (flagged R2-a). Five ratification points R2-a..e are listed separately. R2-c (probe 'proposed here and not validated') is backed by a grep: no section evaluates the probe or recommender on v0.6.0 data.

ITEM 3 (novelty) — ran a dated, recorded probe (2026-10-30): 3 Consensus queries (3 results each, unauthenticated cap) + 1 Undermind semantic search (top-20). Queries are in the ledger verbatim. FOUND, abstracts quoted: (1) CATTS, arXiv:2602.12276 — 'uncertainty statistics derived from the agent's own vote distribution (entropy and top-1/top-2 margin) … provide a practical signal for dynamic compute allocation'; (2) UAAD, DOI 10.1109/ICCVDM71812.2026.11709092 — 'cross-agent divergence to localize risky steps; a scheduler selects agents, rounds'; (3) Wald-SPRT governor, arXiv:2605.19193 — judge consensus score stops debate rounds. Your asymmetry argument is now evidence, not caution: the sentence as a field claim cannot stand. Both drafts (a)/(b) are in the file; I recommend (b) SOFTEN — a positioning sentence naming the three and stating how we differ (signal, target, design), explicitly 'we do not claim the signal is new'. A minimal (b′) is also given. Bib keys in the draft are placeholders; entries must be written from the arXiv/DOI pages.

ITEM 1 (retitle) — HELD as directed. No candidate title. The note states the four things a matching title would have to claim: (i) pre-registered design answered either way; (ii) answer for confidence ENTROPY is no (results.tex:183–184); (iii) confidence DROP ranks tasks within screens (results.tex:184–185); (iv) calibrated index does not transfer (results.tex:201–202).

NOT ESTABLISHED: whether any of the five works the sentence literally names uses such a signal (not read this session); full texts of the three counterexamples (abstracts + CATTS arXiv metadata only); the verbatim text of 'Authorization (1)' — I could not locate it in approvals.md or the dispatch log and applied your paraphrase. NOT DONE: figures question (principal's).

Housekeeping: #807 was marked resolved before this reply landed (my first create failed on a bad flag and the resolve ran anyway); this is the reply it was waiting on.

next_handoff: principal ratification of R2-a..e and choice (a)/(b)/(b′) for item 3 → I apply to paper.tex under QG; or changes-requested on the drafts.
