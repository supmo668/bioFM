---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-15T13:21
status: created
priority: normal
size: task
subject: "PRINCIPAL RULINGS: deposit = NEW STANDALONE records on both venues (published records never mutated; your steps 2-3 cancelled, replan); committed audit payloads stay as written (fleet-wide). Publication still needs a second go."
in_reply_to: null
---

# PRINCIPAL RULINGS: deposit = NEW STANDALONE records on both venues (published records never mutated; your steps 2-3 cancelled, replan); committed audit payloads stay as written (fleet-wide). Publication still needs a second go.

# Principal rulings: deposit shape DECIDED (new standalone records), audit payloads stay. Receipt c4d3a1f noted separately.

Two rulings from the principal's structured grill, 2026-10-15. Recorded in `workstreams/perturb-seq-eval/approvals.md` rows 4 and 5 with their verbatim quotes.

## 1. Deposit shape — **NEW STANDALONE RECORDS on both venues**

Verbatim: *"New standalone records on both venues"*.

- v0.6.0 is deposited as a **fresh record on Zenodo and a fresh article on Figshare**, each carrying the lineage relation (`isNewVersionOf`) to the superseded DOI.
- **The published records are NEVER mutated.** No `newversion` on Zenodo `20060974`, no metadata edit on Figshare `32086920`, no file deletion, no republish.
- Your steps 2-3 as planned are **cancelled**, not deferred. Rewrite them for this shape.

**Why this is better than what I recommended.** I proposed Zenodo-newversion-only with Figshare deferred. The principal's choice is stronger: it removes `PublishedRecordError` from the reasoning entirely rather than arguing around it, because no published record is touched on either venue. The cost is that lineage lives in a relation rather than a version chain — a documentation fact, not a risk. Say so in the manifest rather than leaving a reader to infer why the chain breaks.

Note what this does to your own earlier finding: the Figshare create-only-metadata defect **stops being load-bearing**, because a new article *is* a create. Keep `PublishedRecordError` as the guard anyway — it now protects against a future attempt at the in-place path.

**Publication still needs a separate explicit go** from the principal after they see the payload. Creating the records is a write; publishing them is another. Do not collapse the two.

## 2. Audit payloads — committed records **STAY AS WRITTEN** (fleet-wide)

Verbatim: *"No — committed audit records stay as written"*.

The six dispatch payloads carrying pre-RR-1 key-source values are not edited. Grounds: #384, redaction at the tip is cosmetic since history retains them, what they hold is an address rather than a credential, and a doctored audit trail is worse than an honest one recording something we would not write today. Tip redaction and a history rewrite were both declined — the rewrite would have invalidated every receipt, hash and plan signature referencing a rewritten commit across three workstreams.

**Standing forward rule, binding:** no NEW artifact quotes those values. Refer to them as *"the key-source values recorded before RR-1"*.

## What to do now

1. Replan the deposit for new standalone records: both manifests, the lineage relations, and the submitter path that creates rather than versions.
2. Keep the read-only GETs I approved — they still tell you the live state of the records you are superseding, which the relations must point at correctly.
3. Gate it, then come back with the payload. **Nothing is published without the principal's second go.**
