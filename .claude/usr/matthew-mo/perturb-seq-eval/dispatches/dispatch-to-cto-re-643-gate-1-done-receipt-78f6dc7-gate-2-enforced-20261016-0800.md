---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-16T07:00
status: created
priority: normal
size: task
subject: "Re #643: gate 1 done (receipt 78f6dc7); gate 2 enforced in code; author GET = 'Mangyin Mo' (profile not yet renamed)"
in_reply_to: null
---

# Re #643: gate 1 done (receipt 78f6dc7); gate 2 enforced in code; author GET = 'Mangyin Mo' (profile not yet renamed)

Re #643. Gate 1 DONE: the author-payload change plus a publish-time author check is gated, receipt 78f6dc7 (QGR qgr-fsauth-*), boundary 29c9da6, pushed.
- C1 fixed: the comment had contradicted the deliberate name-form difference.
- Gate 2 is also ENFORCED IN CODE, not only by my GET: a Figshare publish run refuses (DraftMismatchError) unless the draft's authors are exactly publish.yml venues.figshare.expected_author = ['Mang-yin Mo']. It never touches /authors; the fix is the profile, never the payload, as you ruled. Tested for match, unrenamed profile, duplicate and empty.

Gate 2 GET just now (read-only): Figshare draft 34562538 is private; authors = ['Mangyin Mo']. The profile is NOT yet renamed, so a publish run would refuse today. Waiting on the principal.
Gate 3 (superseded records, by GET) runs immediately before the publish go.
Nothing published.
next_handoff: principal renames the Figshare profile
