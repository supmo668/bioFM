---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-16T07:50
status: created
priority: normal
size: task
subject: "Principal: NO DUPLICATE research — delete v0.5.x or revise it as a new version; HACP page written (f43adc6), please mirror to Notion; #620 in question; nothing done on venues"
in_reply_to: null
---

# Principal: NO DUPLICATE research — delete v0.5.x or revise it as a new version; HACP page written (f43adc6), please mirror to Notion; #620 in question; nothing done on venues

PRINCIPAL INSTRUCTION in my session (2026-10-16), verbatim parts:
- "we must not produce duplicate research. Either fully delete the previous one, or remove the current and update the previous print and supercede it as a new revision"
- "provide on HACP review surface"
They also confirmed the v0.5.x records are untouched (gate 3, their word; I re-GET before any publish anyway).

This puts ruling #620 (new standalone records) back in question; a standalone v0.6.0 beside v0.5.x is exactly the duplicate. NOTHING done on any venue. Both drafts (Zenodo 23411021 unsubmitted, Figshare 34562538 private) are untouched.

HACP local source written (f43adc6):
- docs/hacp/perturb-seq-eval/deposit-review.md: facts, options A/B with venue-policy citations, what B changes, the D-1 decision table;
- docs/hacp/decision.md: Open row 3, linking to it.
PLEASE MIRROR to Notion (CTO-only write per docs.notion config). Worktree agents never write Notion, and I have not.

Facts, from the venues' docs (cited on the page):
- A ("fully delete") is not achievable as stated. Zenodo owner-deletion only within 30 days of publication, and ours are Apr-May 2026; after that it is a justified support request, and a tombstone with the DOI remains. Figshare personal accounts cannot unpublish; it is a support take-down ticket, again with a tombstone. Figshare itself advises a new version instead.
- B is the venues' normal path:
  - discard both unpublished drafts (permitted; their reserved DOIs were never registered);
  - Zenodo newversion from v0.5.2 20074427 under concept 19716140;
  - Figshare 32086920 edit plus file replacement, giving v6.
  - One record per venue, one chain, nothing that is cited gets deleted.

I recommend B. It needs:
- your record of reversing #620;
- a gated revision code path. SUPERSEDED_RECORDS / PublishedRecordError block it today, deliberately. The two-go rule stays: the dry run prepares the new version unpublished; publish is a separate go.
- the drafts discarded only after the principal picks B.
No action until the principal decides D-1 on the HACP page.
next_handoff: CTO: Notion mirror + #620 record; principal: D-1
