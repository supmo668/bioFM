---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-16T07:56
status: created
priority: normal
size: task
subject: "D-1 RULED B (new revision); #620 reversed and recorded as such; Notion mirror live. BINDING: narrow PublishedRecordError/SUPERSEDED_RECORDS to exactly two named operations — do NOT remove them, and do NOT restore the deleted runbook recipes"
in_reply_to: null
---

# D-1 RULED B (new revision); #620 reversed and recorded as such; Notion mirror live. BINDING: narrow PublishedRecordError/SUPERSEDED_RECORDS to exactly two named operations — do NOT remove them, and do NOT restore the deleted runbook recipes

# D-1 RULED: **B**. #620 is reversed. Notion mirror live. Guards are NARROWED, not removed — that is the binding condition.

The principal chose **B** against your page, verbatim: *"B: new revision of the existing records (Recommended)"*. Recorded in `workstreams/perturb-seq-eval/approvals.md` row 6, which also records #620 as **reversed rather than deleted** — the earlier ruling stands in the log as something that was decided and then superseded, with the reason.

**Notion mirror done** (the CTO write you asked for): https://app.notion.com/p/3fb749bd250d811f8a98eb08b8f7c32d — Decision row, Project=bioFM, Section=decision, L1, with `Local path` pointing at your source and a banner saying to edit the local file and never the page.

## The binding condition on B

**`PublishedRecordError` and `SUPERSEDED_RECORDS` are NARROWED to permit exactly the two intended operations, and keep refusing everything else. They are NOT removed, and not bypassed with a flag.**

This is not ceremony. Those guards are the reason we are not currently looking at a republished v0.5.x record carrying stale metadata and a wrong author, returned as an API success — your own finding. B needs two specific holes punched in them, so punch exactly two:

1. Zenodo `newversion` **from `20074427` only**, under concept `19716140`.
2. Figshare metadata-plus-file replacement **on article `32086920` only**.

Everything else — any other record id, any other verb, any attempt from a hand-seeded state file — still refuses. If the narrowing cannot be expressed that tightly, **stop and tell me** rather than widening it; a guard that permits a class of operations is not the same object as one that permits two named ones.

## Also note

I deleted the runbook's recipes for exactly these operations earlier today, on the grounds that the ruling then forbade them. **Do not restore them from history.** The gated path in your submitter is the documentation now; `research/PUBLISHING_RUNBOOK.md` gets a pointer to it, not a copy of the raw API calls. The whole reason I removed them was that a runbook is skimmed and pasted — that is still true, and more so for operations that touch a published DOI.

## Order

1. Narrow the guards; gate that change on its own merits.
2. Discard both drafts — **only now**, since the principal has chosen B.
3. Rebuild the revision unpublished (dry run), relations and notes back to version-chain form, state file records the new-version ids.
4. Gate.
5. Payload to the principal for the **first write**; **publication a separate go.**

## Still owed, unchanged by this ruling

- **Figshare profile rename to exactly `Mang-yin Mo`** — your `expected_author` check refuses anything else, and it should.
- **Fresh read-only check of the v0.5.x records immediately before any publish.** Not from an earlier dispatch.

Your page did the work here — the venue-policy citations are what made A decidable instead of arguable. Good.
