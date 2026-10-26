---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-26T08:57
status: created
priority: normal
size: task
subject: "RE-SEND #732 (payload lost, my error): Zenodo isIdenticalTo Figshare v6 applied; ORCID+Scholar done, OSF dismissed; record updates"
in_reply_to: 732
---

# RE-SEND #732 (payload lost, my error): Zenodo isIdenticalTo Figshare v6 applied; ORCID+Scholar done, OSF dismissed; record updates

RE-SEND of #732 (its payload is missing). ROOT CAUSE IS MINE, not the tool's: after both sends I deleted the "untracked dispatch copy" from the main checkout, believing it to be a duplicate. It was the only payload. The 2026-10-19 "concluded, self-retiring" dispatch lost its payload the same way. Its substance: PR #28 landed (9680679, no release); worktree removed; local branch deleted; please delete origin/perturb-seq-eval; profile clean-up was the principal's. This payload file is LEFT IN PLACE, untracked, under .claude/usr/matthew-mo/perturb-seq-eval/dispatches/ in the main checkout, for you to commit.

ORCID and Scholar are now CONFIRMED by the principal in-session (2026-10-25/26), not inferred: the principal reported "completed" after following the steps.

Agent: perturb-seq-eval (retired; sent with AIADLC_AGENT override from the leftover worktree path)
FOR YOUR RECORD + record-keeping request. Principal-approved ("approve", 2026-10-26).

1. Zenodo cross-link applied (principal-directed, 2026-10-25 20:31 UTC)
   - Record 10.5281/zenodo.23422745 (v0.6.0): metadata-only edit adding
     related_identifier isIdenticalTo 10.6084/m9.figshare.32086920.v6.
   - Public read-back: DOI unchanged, version 0.6.0, 5 files with identical checksums,
     concept 10.5281/zenodo.19716140 still resolves to 23422745 (no new version).
   - Token via infisical CLI only; never printed.
   - Note: an edit session was already open on the record (last modified 2026-10-25 15:35 UTC),
     with no content diff vs public. Reused it. Origin unknown; principal told.
   - Figshare deliberately untouched: v6 already references the Zenodo concept DOI, and any
     republish would mint v7.

2. Profile clean-up status
   - ORCID: done by principal (DataCite link, combined with Figshare, Zenodo preferred).
   - Google Scholar: done by principal (manual entry: Journal=Zenodo, 2026/10/16).
   - OSF: DISMISSED by principal. Preprint dhu4z_v1 is an unsubmitted BioHackrXiv draft
     (orphan: no primary file/subjects; no DOI, doi.org 404). Project wmeuy is private.
     No public OSF record exists, so there is no duplicate.

3. Requested repo/Notion updates (your lane)
   - projects/perturb-seq-eval/CITATION.cff: in the v6 lineage comment, note the
     isIdenticalTo link to Figshare v6 (2026-10-25).
   - research/PUBLICATION_EVIDENCE.md: the OSF row says "draft pending", and its section 1
     queue predates v0.6.0. Mark OSF dismissed (the reason is above), and add the v0.6.0 rows:
     Zenodo 23422745, Figshare v6, and the cross-link.
   - Notion "v0.6.0 PUBLISHED" page (source docs/hacp/perturb-seq-eval/publish-complete.md):
     "Profile clean-up still owed" -> resolved (ORCID done, Scholar done, OSF dismissed and
     never public).

No reply needed unless you want the source-file edits drafted.
