---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-09-26T18:23
status: created
priority: high
size: project
subject: "PRINCIPAL: white-paper spec APPROVED, start #272 now; authorship + ORCID + Slack channel; NEW: HACP documentation floor (docs/hacp/) for Aviary-BioSim"
in_reply_to: null
---

# PRINCIPAL: white-paper spec APPROVED, start #272 now; authorship + ORCID + Slack channel; NEW: HACP documentation floor (docs/hacp/) for Aviary-BioSim

PRINCIPAL DECISIONS, 2026-09-26, that change your plan:

1. THE WHITE-PAPER SPEC IS APPROVED (docs/superpowers/specs/2026-09-25-v2r-biosim-whitepaper-design.md, as amended). Start #272 NOW: do not wait for F08 to land. F08 stays gated and receipted (64e74db) and its pr-submit still waits on the principal's /aiadlc:sync, which I am asking for again today. Plan #272, send me the plan for the /grill-me gate, then build. The plan-gate is a human gate; I will get the principal's answer promptly.

2. AUTHORSHIP for publish.yml (P1): author "Matt Mo", ORCID 0009-0009-5233-3142 (public identifier, supplied by the principal today), affiliation as the principal states it in SUBMISSION.md. Slack notification channel: #research-approvals. The Zenodo SANDBOX deposit is pre-approved once the pipeline (#203, perturb-seq-eval) exists; a LIVE deposit still needs an explicit go.

3. NEW WORK ITEM, from the principal: "clear project documentation for aviary-biosim following HACP instructions". HACP is the framework's documentation protocol: /Users/mo/github/aiadlc/reference/REFERENCE-HACP.md (read sections 0, 1, 2, 2a, 2b, 3, 4 before you write anything; the aiadlc project's own docs/hacp/ in that repo is a worked example of the shape). Your part is the LOCAL FLOOR in the Aviary-BioSim repo, which is a separate Project namespace (its own repo, its own L0):
   docs/hacp/index.md          L0, one screen, fixed order: header card (with ALIGNMENT vs spec.md/plan.md), index of the six tags with state+count, TL;DR (2 sentences max), WHERE IT SITS (a system-context mermaid diagram, whole system quiet, the loop's trust boundary highlighted, one-sentence caption), DECISIONS TAKEN (table: Decision, Chosen, Alternatives considered, Why this one, Impact; each row linking to its ADR), DECISIONS NEEDED (or "_none pending_"), SECTIONS (one line each with state and last-updated date).
   docs/hacp/vision.md design.md build.md eval.md risk.md decision.md   L1, one per tag, each a compact illustrated reading of one lifecycle document and a LINK DOWN to it (vision -> demo-spec/README problem statement; design -> spec.md + the four ADRs; build -> plan.md + the register/drain-1 history; eval -> drain-1-notes, the 117/265-test suites, receipts; risk -> the seeded .v2r fixture incident, the instinct-pin ambiguity, budget enforcement never run end to end, F31; decision -> what the principal owns: the instinct-pin fix, drain 2, BIOSIM_USD_PER_1M_TOKENS).
   Rules: local source first, links relative, no workspace URLs or page ids in the files; plain language (no drain/register/park vocabulary on a page a stranger reads: pass, worklist, task, setting work aside, independent test); every number on a page names the artifact it comes from or is absent; a link that does not resolve is a finding. Commit under a coord commit. I mirror the pages to the HACP Index in Notion (CTO-only write) once the principal's plugin update lands; you never write Notion.

4. SEQUENCE: HACP floor first (it is small and mostly re-reads docs you own), then the #272 plan. Report the HACP commit and the plan in one dispatch.

Scan every dispatch by shape before sending, as before.
