---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-24T19:16
status: created
priority: high
size: task
subject: "STOP — two contradictory CTO rulings on the migration fork (a vs b) 3 min apart; act on NEITHER, continue #202"
in_reply_to: 229
---

# STOP — two contradictory CTO rulings on the migration fork (a vs b) 3 min apart; act on NEITHER, continue #202

STOP. DO NOT ACT ON EITHER #229 OR THE DISPATCH BEFORE IT. Two contradictory rulings are in your inbox, both signed biofm/matthew-mo/cto, three minutes apart. This is my error to resolve, not yours to adjudicate.

WHAT HAPPENED

  2026-09-24T19:11 — a dispatch to you: 'HOLD LIFTED on #203 — principal chose (a): consolidate Python, n8n orchestrates. #203 stands as written.'
  2026-09-24T19:14 — my #229 to you: 'SUPERSEDES #203 ... principal ruled (b) ... consolidation CANCELLED.'

These are mutually exclusive. Under (a) you build the consolidated Python CLI; under (b) that CLI is deleted. Acting on the wrong one wastes a build or deletes a needed one.

CAUSE, as far as I can establish it: more than one CTO session shares the address biofm/matthew-mo/cto and the same dispatches directory. The 19:11 dispatch was not written by this session. In THIS session I put the (a)/(b) fork to the principal explicitly and the literal reply was 'b', which is why #229 says what it says and why I then built the n8n workflow. I cannot see what question the other session asked or what it was told, so I am NOT going to declare my own ruling the winner by assertion — that is precisely how a coordination failure becomes a silent one.

WHAT YOU DO NOW: NOTHING on the publication pipeline. Not the consolidation, not the publish.yml generalisation, not adapters, not credentials, not venues. #202 — the artifact regeneration and the HVG fix ruled in #227 — is UNAFFECTED and remains your priority. Carry on with it.

I have put the conflict to the principal for disambiguation. When they rule I will send ONE dispatch that explicitly names which of the two is void.

WHAT IS ALREADY DONE, so you can weigh it but not act on it: I built the n8n workflow under (b) — '[bioFM] 03-PUBLISH: Academic Repositories', id t2SmnfD3VwVV11wx, 12 nodes, INACTIVE, nothing published, no credentials created. If (a) turns out to be the standing ruling, that workflow is wasted work, but it is inert and deletable, and its four documentation sticky notes (run variables, credential requirements, the arXiv human gap, failure semantics) are useful under either design. No harm has reached a venue and none can while it is inactive.

ONE THING FROM THE OTHER DISPATCH THAT IS TRUE UNDER EITHER RULING, and you should know it: a second project is coming through this pipeline — a white paper on the v2r-loop / BioSim work. That means a second real publish.yml to test against, which is good for keeping the contract general rather than shaped around perturb-seq-eval. It changes nothing you do today.

Also true under either ruling and unchanged: no live deposit to any venue; the first live contact is the Zenodo SANDBOX on the principal's explicit go; arXiv and bioRxiv report PREPARED, never published; no OpenAIRE adapter; n8n workflows are [bioFM]-prefixed and inactive; the Slack channel is still unnamed.

Acknowledge this and continue #202. Do not reply on the migration question.
