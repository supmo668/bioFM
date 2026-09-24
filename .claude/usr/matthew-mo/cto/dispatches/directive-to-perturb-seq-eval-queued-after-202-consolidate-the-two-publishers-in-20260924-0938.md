---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-24T16:38
status: created
priority: normal
size: project
subject: "QUEUED after #202: consolidate the two publishers into one reusable publish/update CLI (n8n orchestrates, Python adapts)"
in_reply_to: null
---

# QUEUED after #202: consolidate the two publishers into one reusable publish/update CLI (n8n orchestrates, Python adapts)

QUEUED — DO NOT START THIS UNTIL YOU HAVE REPORTED #202. The artifact regeneration is higher priority and I do not want it sharing attention with a new build. Acknowledge this dispatch, finish #202, then come back.

Full design spec, approved by the principal today, is on main at:

  research/PUBLICATION_PIPELINE_SPEC.md

Read it before planning. This note carries only what you would otherwise get wrong.

WHAT THE PRINCIPAL ASKED FOR: one reusable pipeline that can both publish AND update a paper across as many academic services as have real APIs, starting with Zenodo, on n8n, with a Slack notification, saving assets under a run variable `bioML-publication` in a per-topic folder.

THREE THINGS THAT ARE NOT WHAT THEY SOUND LIKE:

1. THERE ARE ALREADY TWO PUBLISHERS, and they overlap. scripts/publish/submit.py (19 KB, + publish.yml.template) and projects/perturb-seq-eval/scripts/publish/submit_to_venues.py (30 KB) BOTH already cover zenodo, zenodo_sandbox, figshare, osf. Do not write a third. Consolidate the two into one CLI, and resolve their behavioural differences EXPLICITLY rather than picking whichever you read first — 49 KB of overlapping logic means the differences are where the bugs live. If a difference looks like a deliberate fix in one copy, say so in the report rather than silently discarding it.

2. THE ADAPTERS BELONG IN PYTHON, NOT IN n8n HTTP NODES. This is the load-bearing design decision and it comes from your own repo's precedent: projects/lung-on-chipsim/orchestration/n8n/etl_drugbank.json is five `n8n-nodes-base.executeCommand` nodes shelling out to a Python entrypoint, and lung-on-chipsim's README:83 calls pipeline.py 'the entrypoint the n8n ETL export invokes'. Follow that. n8n sequences, retries and notifies; Python does the work. Consequences: credentials stay in Infisical -> environment and are NEVER duplicated into n8n credential objects (one place to rotate); the venue logic is testable under pytest without an n8n instance; a diff on an adapter is reviewable where a diff on exported node JSON is not. So 'create connector and credentials' means a Python adapter plus an Infisical key — not an n8n credential record.

3. TWO OF THE REQUESTED VENUES CANNOT BE AUTOMATED, AND THE PIPELINE MUST SAY SO. arXiv's API is read/search only and submission is a web form; bioRxiv has no deposit API. The principal selected them anyway, so build `--mode prepare` for these: build the bundle, validate the metadata the venue demands, write a manual-upload checklist into the topic folder, and report status PREPARED (manual upload required) — NEVER 'published'. A run where only these two ran is NOT a successful publish and the Slack message must not read as one. Do not invent an endpoint to make them look uniform with the others.

ALSO: DO NOT BUILD AN OpenAIRE ADAPTER without coming back to me. OpenAIRE is principally an aggregator that harvests from repositories rather than being deposited into, and Zenodo is one of its sources — so a Zenodo deposit is expected to surface there with no connector at all. §3.1 of the spec has this. Verify the record appears; do not spend adapter effort on it.

VERIFY BEFORE YOU CODE: Dataverse (native REST vs SWORD differs per installation), Dryad (v2 surface), Software Heritage (SWORD flavour + metadata schema). The spec marks my confidence on each as medium and says to check live docs. Do not take my table as authority — it is a starting point, and I have written down that it is.

WHAT IS BLOCKED vs WHAT IS NOT. Blocked: the n8n workflow itself (no instance — this inherits lung-on-chipsim's deferred T16a, README:267), Slack posting (only authenticate/complete_authentication stubs exist, so no channel is reachable), and five of six venue tokens. NOT blocked, and therefore the whole of your first pass: the consolidated CLI, the six adapters behind tests with --dry-run, prepare mode, the asset archive + manifest, and the Slack FORMATTER (unit-test it against a FAILURE case, not only a success case). Build all of that without touching n8n.

MANIFEST — DO NOT REPEAT #202's DEFECT. manifest.json must record the git SHA and every resolved run variable. The reason this pipeline exists at all in reviewable form is that the perturb-seq-eval artifacts could not say what produced them. Same standing rule: log and save the exact config for every run, new config copy per run.

NOTHING PUBLISHES IN THIS PASS. Step 8 of the spec's build order — stand up n8n, import, end-to-end on ZENODO SANDBOX — is the first step that may touch a live repository, and it is not authorised. No live deposit to any venue without the principal's explicit go. Sandbox only, and only once n8n exists.

ONE CORRECTION YOU SHOULD NOT PROPAGATE: I earlier recorded ZENODO_TOKEN as absent from all three Infisical environments. That was WRONG. The local Infisical CLI is authenticated as a principal who is not a member of the bioFM project and returns 403 Forbidden; my exit-code check read that fetch failure as absence. Presence is UNVERIFIED, not absent. Do not design around the token being missing, and do not try to read it yourself — I will configure credentials through the Infisical MCP at that step so the value stays out of transcripts.

REPORT BACK: the consolidation decision record (what differed between the two publishers and what you did about each difference), the adapter test matrix, verified/not on the three medium-confidence venue APIs, and the Slack formatter's failure-case output. Then stop.
