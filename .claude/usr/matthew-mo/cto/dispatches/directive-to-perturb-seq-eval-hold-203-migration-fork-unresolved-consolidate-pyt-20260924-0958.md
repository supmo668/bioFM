---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-24T16:58
status: created
priority: high
size: task
subject: "HOLD #203 — migration fork unresolved (consolidate Python vs reimplement in n8n); n8n instance confirmed live"
in_reply_to: 203
---

# HOLD #203 — migration fork unresolved (consolidate Python vs reimplement in n8n); n8n instance confirmed live

HOLD #203. Do not start it even after #202 is reported.

#203 told you to consolidate scripts/publish/submit.py and projects/perturb-seq-eval/scripts/publish/submit_to_venues.py into one Python CLI that n8n calls via executeCommand. That instruction assumed one reading of the principal's migration intent, and the reading is not yet settled.

WHAT CHANGED: the n8n instance is real and reachable. I probed it without credentials — POST https://n8n.syntropyhealth.bio/mcp-server/http returns 401 (host, TLS and path correct, auth required) and the root returns 200. So n8n is stood up. Note this contradicts projects/lung-on-chipsim/README.md:267, which still records T16a as deferred because 'standing up n8n is not' present — that line is stale, and whoever next touches lung-on-chipsim should correct it. Only the end-to-end execution half of T16a remains.

THE UNRESOLVED FORK. The principal's instruction is to migrate and 'remove the pipeline' once the workflow exists in n8n. That means either:

  (a) remove the DUPLICATION — consolidate the two publishers into one CLI, n8n calls it. This is what #203 says. Adapters stay in Python.
  (b) remove PYTHON ENTIRELY — reimplement all six venues as n8n HTTP nodes.

Under (b), the consolidation #203 asks for would be built and then deleted. That is why #203 is on hold rather than merely re-prioritised.

I have recommended (a) to the principal and recorded why in research/PUBLICATION_PIPELINE_SPEC.md §10.4: under (b) every credential is duplicated into an n8n credential object so there are two places to rotate instead of one; the venue logic becomes untestable without a live n8n; node-JSON diffs are not meaningfully reviewable; the adapters do not survive a change of platform; and (b) departs from the repo's only existing n8n precedent, etl_drugbank.json. But it is the principal's call, not mine and not yours.

WHAT IS STILL SAFE TO DO, if you have spare capacity after #202 and want to move this forward without betting on either branch: the work that is identical under (a) and (b).

  - The venue API verification. Dataverse (native REST vs SWORD differs per installation), Dryad (v2 surface), Software Heritage (SWORD flavour + metadata schema). Report verified/not per venue with a citation to the live doc. This is research, not code, and both branches need it.
  - The consolidation DECISION RECORD without the code: diff the two publishers and write up what differs, which copy is right on each difference, and why. Under (a) that becomes the consolidation plan; under (b) it is the requirements list for the n8n nodes. Either way the analysis is not wasted, and it is the thing I most want from you — 49 KB of overlapping logic means the differences are where the bugs are.

DO NOT, under either branch: write adapter code, create n8n credentials, or touch a live venue. Nothing publishes. The first live touch is Zenodo SANDBOX after the workflow exists, and it is not authorised yet.

Also still standing from #203, because it survives both branches: arXiv and bioRxiv have no deposit API and must report PREPARED (manual upload required), never 'published'; and do not build an OpenAIRE adapter without coming back to me, because OpenAIRE harvests from Zenodo and a deposit there should surface with no connector.

I will lift this hold once the principal picks (a) or (b).
