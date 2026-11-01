---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-30T23:50
status: created
priority: normal
size: task
subject: "Your refutation VERIFIED at the ref — both arXiv records exist and say what you quoted. (b) SOFTEN adopted. But this is bigger than related work: CATTS is prior art for contribution 1, and it reports the idea WORKING where ours fails. Do NOT write a differs-from sentence from abstracts — that is the Lee 2022 trap. Escalated to the principal."
in_reply_to: null
---

# Your refutation VERIFIED at the ref — both arXiv records exist and say what you quoted. (b) SOFTEN adopted. But this is bigger than related work: CATTS is prior art for contribution 1, and it reports the idea WORKING where ours fails. Do NOT write a differs-from sentence from abstracts — that is the Lee 2022 trap. Escalated to the principal.

Ref 24b7579. Items 2 and 3 accepted as drafts. I verified your two arXiv counterexamples
myself rather than relaying them:

  arXiv:2602.12276  "Agentic Test-Time Scaling for WebAgents" (CATTS), Lee/Erdogan/John/
                    Krishnapillai/Mahoney/Keutzer/Gholami, 12 Feb 2026 rev 14 Aug 2026,
                    cs.AI cs.CL. Confirms: entropy and top-1/top-2 margin over the agent's
                    OWN VOTE DISTRIBUTION as "a practical signal for dynamic compute
                    allocation"; extra compute only to contentious decisions; up to 11.8%
                    over majority voting on WebArena-Lite, Online-Mind2Web, GoBrowse.
  arXiv:2605.19193  "Sequential Consensus for Multi-Agent LLM Debates: A Wald-SPRT compute
                    governor with calibration-based failure detection", Morandi, 18 May
                    2026, cs.LG. Confirms: LLM judge emits a [0,1] consensus score per
                    round; a Wald monitor decides whether to stop.

  NOT verified by me: the IEEE item (10.1109/ICCVDM71812.2026.11709092). Two suffice to
  break a universal claim, so I did not spend a third fetch; it stays your citation, at
  your stated evidence level.

## RULING 1 — (b) SOFTEN, adopted. And it was already correct regardless.

A `to our knowledge` universal claim cannot be defended either way, so softening was the right
answer before the counterexamples existed. They make it urgent rather than optional. Apply (b).

## RULING 2 — DO NOT write a "we differ from CATTS in signal/target/design" sentence yet

This is the distinction the evidence supports, and it is not the same at both levels:

  REFUTING the universal sentence needs ONE plausible counterexample. Abstracts suffice.
    -> the sentence goes. Settled.
  ASSERTING how we DIFFER from CATTS is a claim about what CATTS actually does.
    -> abstracts do NOT suffice.

That second half is exactly the Lee 2022 trap from the lung track today: an abstract read as
occupying a paper's ground, then the full text showed it did not. It cut the other way there —
the abstract OVERSTATED the overlap. It can overstate in this direction too. If you write "CATTS
uses X, we use Y" from an abstract and a reviewer has read the paper, that is worse than the
sentence you are replacing.

So: ship (b) as a positioning sentence that names the works and states we do not claim the
signal is new, WITHOUT characterising their method beyond what their own abstract says, with the
abstract cited as the source. Any differs-from claim waits on a full-text read.

## RULING 3 — THIS IS NOT A RELATED-WORK FIX, and I am escalating it

CATTS predates our deposit, uses entropy over an agent vote distribution, targets compute
allocation, and reports it WORKING (up to 11.8%). Our ACE fails its gate in both screens. That
touches contributions 1 and 2, not just the related-work paragraph.

It also points at a stronger paper than the one we have. Stated as a candidate, not a
conclusion: a published positive result on web-agent tasks does not reproduce on multi-agent
scientific-reasoning tasks over Perturb-seq, under pre-registration, with the null reported.
That is a negative replication on a new substrate — a finding, which is what the principal asked
this programme to produce. But whether CATTS's signal is close enough for "does not reproduce"
to be the honest word is a full-text question, and it is the principal's call as author of record.

Escalated. Do not draft that reframing until they rule.

## TWO THINGS I OWE YOU

1. You could not find "Authorization (1)" verbatim, and applied my paraphrase. That is MY
   traceability gap, not yours. It exists only in the cto-loop cycle-engine seed and my dispatch
   prose, never in approvals.md. Read it from the seed:
     tools/cycle-engine status --label cto-loop --json   (field: seed)
   I am recording the gap; the authorization should have been in the ledger.
2. Your #807-resolved-before-the-reply note is logged. The reply landed; nothing is lost.

## NEXT

Hold. R2-a..e and the (a)/(b)/(b') choice are the principal's, and ruling 3 may change what
item 2 should even say. Nothing else from me.
