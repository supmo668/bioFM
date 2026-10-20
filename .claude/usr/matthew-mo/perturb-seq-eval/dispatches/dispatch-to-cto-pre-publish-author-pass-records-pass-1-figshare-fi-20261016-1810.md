---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-16T17:10
status: created
priority: normal
size: task
subject: "Pre-publish: author PASS, records PASS, 1 Figshare file still processing (polling); HACP publish review + D-2 written (231dce1), please mirror; nothing published"
in_reply_to: null
---

# Pre-publish: author PASS, records PASS, 1 Figshare file still processing (polling); HACP publish review + D-2 written (231dce1), please mirror; nothing published

Pre-publish status (principal, in my session: '1 is done ... complete 2 & 3 autonomously, provide HACP review surface for 4').
- Gate (#651 guard): receipt 8795772 (QGR qgr-avail-*). A Figshare publish refuses while any file is not 'available'; 4 test gaps from the review were fixed (stale listing, missing status, every file, plain path), and all 6 surviving mutations are now caught. 1218 tests pass.
- Check 1 (author): PASS. The draft and public views read 'Mang-yin Mo' (the principal renamed the profile).
- Check 2 (all 5 files available): PENDING. 4/5 are available; v060_run_artifacts.zip is still 'ic_success' after ~20 min. The publish run refuses until it changes. A read-only background poll (GET only, 5-min interval, up to ~60 min) is watching it.
- Check 3 (fresh GET): PASS.
  - Zenodo 20074427 is published with the same 3 files and is still the latest in concept 19716140.
  - Figshare public view is still v5 with its 3 original files.
  - The prepared Zenodo draft 23422745 holds the 5 files.
  - The old standalone drafts are 404.
  - The Figshare account holds only 32086920; the Zenodo account holds only draft 23422745.
- HACP for item 4 written (231dce1): docs/hacp/perturb-seq-eval/publish-review.md (payload, irreversibility, checks, and the profile clean-up the principal asked for: OSF preprint dhu4z_v1 / ORCID / Scholar) and docs/hacp/decision.md Open row 4 (D-2). PLEASE MIRROR to Notion (CTO-only write).
- OSF: api.osf.io did not respond to read-only requests (timeouts), so the page says the preprint's live state is unverified.
Nothing published. The publish go is the principal's (D-2).
next_handoff: CTO: Notion mirror of D-2; principal: D-2
