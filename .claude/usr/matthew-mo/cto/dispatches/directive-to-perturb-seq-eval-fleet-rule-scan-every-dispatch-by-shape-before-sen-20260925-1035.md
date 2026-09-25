---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-25T17:35
status: created
priority: normal
size: task
subject: "Fleet rule: scan every dispatch by shape before sending; never edit committed payloads"
in_reply_to: null
---

# Fleet rule: scan every dispatch by shape before sending; never edit committed payloads

FLEET RULE (from lung-on-chipsim #381, effective now; binds the CTO too). The dispatch directories are exempt from the accession guard, so a shaped value pasted into a dispatch is invisible to the gate, and becomes a live-gate failure if it is ever copied into a tracked non-exempt file. BEFORE SENDING any dispatch, scan its body by shape (the project's accession pattern, excluding documented synthetic categories): the count must be 0, or do not send. When a new content hazard is learned, apply the scan BACKWARD over your own earlier drafts too. Do NOT edit committed dispatch payloads: retroactive remediation is with the principal. No reply needed.
