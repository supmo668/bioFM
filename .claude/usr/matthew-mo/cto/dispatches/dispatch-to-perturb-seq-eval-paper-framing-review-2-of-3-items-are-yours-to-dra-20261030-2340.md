---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-30T23:40
status: created
priority: normal
size: task
subject: "Paper framing review: 2 of 3 items are yours to DRAFT now (reorder the contributions, fix the to-our-knowledge claim). The retitle is HELD — the deposited CFF title and paper.tex title are the same string, so changing it would make the arXiv record disagree with Zenodo and undercut the isIdenticalTo relation. Your worktree did not exist; I created it."
in_reply_to: null
---

# Paper framing review: 2 of 3 items are yours to DRAFT now (reorder the contributions, fix the to-our-knowledge claim). The retitle is HELD — the deposited CFF title and paper.tex title are the same string, so changing it would make the arXiv record disagree with Zenodo and undercut the isIdenticalTo relation. Your worktree did not exist; I created it.

Your worktree was missing — `worktrees/perturb-seq-eval` was a plain directory holding only
`.aiadlc-agent` and an October hook log, so `agent-wake` reported no worktree while
`worktree-create` reported one already existed. The shell is preserved in the session scratchpad;
the worktree is now registered on branch `perturb-seq-eval` from `origin/main` (69ae988, 1477
tracked files).

## WHY THIS DISPATCH EXISTS

The principal asked for a final review of the paper on innovation and application category, and
approved three framing changes. The review's finding, from `paper/sections/results.tex` rather
than from the abstract:

**The paper is titled for the one hypothesis it refutes.** ACE fails its one-sided gate in BOTH
screens and its point estimates run against the pre-registered direction; results.tex says the
H4 pass is carried by the confidence-drop component and the composite. The abstract discloses
this correctly. The title does not.

## ITEM 2 — REORDER THE CONTRIBUTIONS (yours, draft now)

`paper.tex:117` lists four contributions in an order that does not match what survived the gates.
Ranked by standing: (3) the pre-registered design with gates where both outcomes are reported,
(4) the provenance-complete run record, (1) the metrics — ACE failed, the confidence drop and the
composite passed within-screen, nothing transferred, (2) the probe and recommender, whose value
rests on a sufficiency H5 undercuts.

Draft a reordering that leads with pre-registration and provenance. **Do not restate any gate
outcome from memory** — every claim about what a gate showed must come from results.tex or the
generated macros, quoted. No new numbers, and no number typed by hand.

## ITEM 3 — THE NOVELTY CLAIM (yours, draft now)

`paper.tex:170`: *"None of these works, to our knowledge, use the group's internal
confidence/critique distribution as an explicit difficulty signal."*

That is a `to our knowledge` claim, and the standing method rule in this fleet is that **a
sampled probe of the literature can REFUTE a novelty claim but can never ESTABLISH one** —
absence in a sample says nothing about the corpus. My own prior-art tool caps at 3 results per
search, which is a sample, not a search.

Two acceptable drafts, your call which, with the reasoning stated:
  (a) SUBSTANTIATE — state the search strategy, the corpora, and the date, so the claim is
      bounded by a described method rather than by an assertion about everything.
  (b) SOFTEN — say what you searched and found, not what does not exist.
One found counterexample damages the whole paper's credibility, and that asymmetry is not worth
the stronger sentence.

## ITEM 1 — THE RETITLE IS HELD, AND HERE IS WHY

Measured: `projects/perturb-seq-eval/CITATION.cff` and `paper/paper.tex` carry the SAME title
string (modulo a `\\` line break). The work is deposited at a Zenodo concept DOI, and the
submission runbook recommends asserting `isIdenticalTo` between the arXiv and Zenodo records.

So a retitle is not a prose fix. It forks:
  (a) retitle on arXiv only — the two records then disagree on title, and `isIdenticalTo`
      becomes a claim I would not want to defend;
  (b) retitle and cut a new Zenodo version — both agree, at the cost of a new version DOI and a
      moved label date;
  (c) keep the title — the framing liability stands and the abstract carries the correction.

**That is the principal's decision as author of record, and it is escalated.** Do NOT draft a new
title until they rule. If you want to help it along, the useful artifact is a short note stating
what the title would have to claim to match the surviving result — not a candidate title.

## NOT DISPATCHED

The figures question (the paper references zero `\includegraphics`; `graphicx` is loaded and
unused; the five figure PDFs are v0.5-era orphans) is an authorial call and changes the arXiv
bundle. The principal owns it.

## CONSTRAINTS

Authorization (1) applies: DRAFT into a staging file, marked unratified, outside `paper/`.
Nothing reaches `paper.tex` or any public surface until the principal ratifies. No biological
number, no identifier paired with a substance. Report what you did NOT establish.
