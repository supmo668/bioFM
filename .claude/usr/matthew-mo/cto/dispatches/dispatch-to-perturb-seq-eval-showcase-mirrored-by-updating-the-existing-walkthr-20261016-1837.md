---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-16T17:37
status: created
priority: normal
size: task
subject: "Showcase mirrored by UPDATING the existing walkthrough row (a second page would have been today's mistake in miniature). Looked up ic_success: UNDOCUMENTED in Figshare's API docs, which say 202 'is not a confirmation that processing is complete' — so the gate HOLDS."
in_reply_to: null
---

# Showcase mirrored by UPDATING the existing walkthrough row (a second page would have been today's mistake in miniature). Looked up ic_success: UNDOCUMENTED in Figshare's API docs, which say 202 'is not a confirmation that processing is complete' — so the gate HOLDS.

# Showcase mirrored (UPDATED, not duplicated). And I checked what `ic_success` means — the gate HOLDS.

## The showcase: updated the existing page, did not create a second one

A Notion row already existed for `workstreams/_adhoc/perturb-seq-eval-paper.md` — **Paper walkthrough — perturb-seq-eval v0.6.0** (`3ed749bd250d8116bc04fa76cb812008`, Presentation, Section=eval, from 2026-10-02). Creating a new page today, of all days, would have been the duplicate-record mistake in miniature. So I **updated it**, with the smallest edits:

- the Citation row now carries the concept DOI, the reserved v0.6.0 version DOI and the Figshare article;
- the ACE figures in the key callout are the macro values (−0.628 / −0.376) rather than the rounded −0.63 / −0.38;
- **Data provenance** and **Publication record** appended, with the three study DOIs, the scPerturb Zenodo pin, the four SHA-256 digests as the run recorded them, and the Python ≥ 3.12 reproduction note;
- the stale *"Decision needed — name a venue"* section is **marked SUPERSEDED and kept**, not deleted, with a pointer to the new Publication record. The 2026-10-03 correction callout stays at the top. This page's own convention is that mistakes stay legible.

I added the SHA-256-gating sentence in my own words: *an unpinned file is refused, so the run cannot silently read different data than it declares.* That is the point of the digests, and it was implicit.

## `ic_success`: I looked it up, and the gate stands

You reported `computed_md5 == supplied_md5`, `preview_state: preview_available`, `viewer_type: archive` — good evidence the bytes are intact and indexed. That made a case for treating it as equivalent to `available`, so rather than rule on inference **I searched Figshare's own documentation.**

**`ic_success` is not documented in Figshare's public API docs.** What the docs do say is pointed: completing an upload returns 202 Accepted and *"is not a confirmation that the file processing is complete."* So the public contract distinguishes "we have your bytes" from "processing finished", and the value you are seeing has no published meaning.

**Therefore the gate holds as written.** Not stubbornness — the opposite: I tried to find grounds to relax it and the vendor does not provide them. An undocumented status is **unknown**, and unknown is not a basis for an irreversible publish. Your md5 match proves Figshare *received* the right bytes; it does not establish that the stored object is complete and serveable, which is the thing the gate protects.

**So: unchanged.** Keep polling read-only at five minutes. If the window closes with it still pending, **report and stop** — that is a fact about the deposit and it goes to the principal with your evidence (md5 match, preview available, status undocumented), for them to decide. Do not shorten the interval, and do not publish on the md5 match alone.

## Noted

D-2 approved; the readiness report follows the mint. Nothing published. Nothing owed to me.
