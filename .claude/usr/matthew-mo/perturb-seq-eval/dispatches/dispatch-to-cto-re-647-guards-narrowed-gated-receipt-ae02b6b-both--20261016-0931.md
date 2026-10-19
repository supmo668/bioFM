---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-16T08:31
status: created
priority: normal
size: task
subject: "Re #647: guards narrowed + gated (receipt ae02b6b); both standalone drafts discarded (404); rebuilt; payload to the principal for the first write"
in_reply_to: null
---

# Re #647: guards narrowed + gated (receipt ae02b6b); both standalone drafts discarded (404); rebuilt; payload to the principal for the first write

Re #647. Steps 1-2 done, and the step-3 rebuild done locally. NOTHING written to any published record.
1. Guards NARROWED to exactly the two named operations, gated: receipt ae02b6b (QGR qgr-revB-*), boundary 54ea4d5.
   - Security review (7) and test review (42 mutations) folded in. Highlights:
     - newversion draft validated before any delete;
     - integer-only state ids;
     - inherited-file removal flagged and resumable;
     - publish requires a completed dry run, an exact file set and the expected author;
     - Figshare public baseline must be v5 and is re-checked at every step up to publish.
   - All 18 targeted mutations caught. 1214 tests pass.
   - The runbook recipes were NOT restored; publish.yml names the steps only.
2. Both standalone drafts DISCARDED: Zenodo 23411021 and Figshare 34562538 were each confirmed unpublished first; both deletes returned 204 and both now 404. State cleared (3635f9d).
3. Rebuilt with build_deposit at 3635f9d: 0 overfull / 0 undefined, 5/5 SHA256SUMS OK; validate shows 5 files.
Fresh read-only GET just now:
- Zenodo 20074427 is done, v0.5.2, still the latest in concept 19716140.
- Figshare 32086920 is public v5 with its 3 original files.
- Figshare author is still 'Mangyin Mo', so the publish run will refuse until the profile is renamed.
Next: the payload goes to the principal for the FIRST WRITE (the two --dry-run revisions); publication is a separate go.
next_handoff: principal first-write go
