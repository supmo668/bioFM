---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-16T06:52
status: created
priority: normal
size: task
subject: "First write DONE on the principal's go: Zenodo draft 23411021 + Figshare draft 34562538 (unpublished, verified); Figshare double-author defect found and fixed"
in_reply_to: null
---

# First write DONE on the principal's go: Zenodo draft 23411021 + Figshare draft 34562538 (unpublished, verified); Figshare double-author defect found and fixed

FIRST WRITE DONE on the principal's explicit go, given in my session with the full payload in front of them. NOTHING PUBLISHED.
- Zenodo draft 23411021: unsubmitted; DOI 10.5281/zenodo.23411021 reserved.
- Figshare draft 34562538: private; DOI 10.6084/m9.figshare.34562538 reserved.
- IDs committed in publish.state.v060.json (834dbb8).

Read-only verification (GETs):
- Both drafts hold exactly the 5 payload files, md5-identical to validate's.
- The Zenodo draft metadata is exactly as specified: version 0.6.0, 'Mo, Mang-yin', cc-by-4.0, preprint; relations isSupplementedBy the repo @ce5f237, isNewVersionOf 20074427, isNewVersionOf figshare 32086920.v5; the notes.
- The SUPERSEDED records are UNCHANGED: Zenodo 20074427 is still done with the same files; Figshare 32086920 is still public v5 with the same files.

DEFECT FOUND AND FIXED: the Figshare draft listed the author TWICE. Figshare auto-adds the account owner from their profile ('Mangyin Mo') and the script also sent 'Mo, Mang-yin'.
Principal chose 'Profile renamed, one author':
- 382ed39: the Figshare create and resume payloads no longer send authors (tested); 1193 tests pass.
- The duplicate name-only author was deleted from draft 34562538 only. The script was guarded to the v060 state's article id, private and unpublished, exactly one name-only duplicate. HTTP 204; one author remains.
- The principal is renaming their Figshare profile to 'Mang-yin Mo'. I will confirm the author name by GET before any publish.
This fix is ungated so far: it gets its gate with the remaining work before the publish go.

Next: profile-rename check (GET) -> gate 382ed39 -> payload review by the principal -> their SEPARATE publish go.
next_handoff: principal: profile rename, then the publish go
