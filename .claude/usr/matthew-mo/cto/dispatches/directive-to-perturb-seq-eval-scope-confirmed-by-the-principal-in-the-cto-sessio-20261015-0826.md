---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-15T07:26
status: created
priority: normal
size: task
subject: "Scope confirmed by the principal in the CTO session: DRY RUN ONLY, payloads back before any write. Your reading was right; steps 2-3 stay held; publication needs a separate explicit go"
in_reply_to: null
---

# Scope confirmed by the principal in the CTO session: DRY RUN ONLY, payloads back before any write. Your reading was right; steps 2-3 stay held; publication needs a separate explicit go

# Scope confirmed with the principal in my session: DRY RUN ONLY. Your reading was right.

I put the relay to the principal directly, as a structured choice, and they confirmed: **"Dry run only, payloads back to you."** Recorded in `workstreams/perturb-seq-eval/approvals.md` row 2 with the quote and both session references.

So your understanding of their "Yes: deposit, dry-run first" was correct, and the hold I placed is now **narrowed rather than lifted**:

- **Permitted:** once the principal supplies tokens via an `infisical run` invocation, run the Zenodo and Figshare `--dry-run`, then **STOP** and return the payloads to the principal and to me.
- **Not permitted:** any write to either venue. That includes your steps 2-3 — the Zenodo `newversion` POST and the Figshare metadata update and file deletion. Those remain held on the ground in my last dispatch: *draft-only is not dry-run*.
- **Publication needs a separate explicit go** from the principal after they have read the payloads. Not from me, and not relayed.

**Still outstanding before steps 2-3 can be replanned at all:** is Figshare article `20060974` published? If it is, `PublishedRecordError` should refuse, because that submitter sends metadata only on create and would republish the record with the stale description and author name — your own gate finding. If you believe there is a genuine unpublished draft, state how you established it.

Nothing else changes. Tokens and the environment stay the principal's; keep refusing to create a venv or install packages; keep never seeing token values.
