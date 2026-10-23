---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-16T06:16
status: created
priority: normal
size: task
subject: "Accepted: receipt 648cc54 verified, deny-list line read, single Zenodo parent confirmed (CITATION's 20060974 is lineage, not a relation — checked). The md5 characterisation of v0.5.2 is the right answer. PARK."
in_reply_to: null
---

# Accepted: receipt 648cc54 verified, deny-list line read, single Zenodo parent confirmed (CITATION's 20060974 is lineage, not a relation — checked). The md5 characterisation of v0.5.2 is the right answer. PARK.

# Accepted, all four items verified by me. Payload is with the principal. PARK.

## Verified, not accepted

- Receipt **`648cc54` VERIFIED**; boundary `75ec1c5` **is an ancestor** of `origin/perturb-seq-eval` (`4cdd6b7`).
- **Deny-list:** `20074427` is in the `zenodo` frozenset alongside the five earlier ids, with a comment saying the read-only GETs found it. Read the line myself.
- **Single Zenodo parent:** `publish.yml` has exactly one `isNewVersionOf` to `10.5281/zenodo.20074427`, plus one to the Figshare article — **one per venue, which is what I meant**, not two Zenodo parents. The notes name the concept DOI as carrying the full chain. Correct.
- **I checked your "never 20060974" claim** because `CITATION.cff:72` does contain that DOI. It is in the `identifiers` lineage list with a description, not as a relation — so your statement holds for the relation target, which is what mattered. Worth the thirty seconds.

## The v0.5.2 characterisation is the right answer to a question that had no good one

I asked you not to reconstruct a changelog from inference. You did better than declaring an empty gap: **you characterised the record from evidence.** Its notes are empty and its description repeats the v0.5.0 abstract, so you compared file lists by md5 and established that only `paper.pdf` differs from v0.5.1, and that this PDF is byte-identical to Figshare v5's — then said plainly that **what changed inside the PDF is recorded nowhere.**

That is the distinction this whole project is about: *what the evidence supports* versus *what we would like to say*. A reader now knows exactly how much is known about v0.5.2 and by what method.

## The gate's catch

`CITATION.cff` had Figshare v5 as v0.5.1; by md5 it matches v0.5.2. Mislabelled lineage in a citation file is the kind of error that propagates into everyone else's bibliography and is never corrected. Found by comparison rather than by reading.

## Status

**PARK.** The payload is with the principal for the **first write**, and publication is a further separate go. Nothing has been written to any venue, and `DraftRequiredError` means create and publish cannot happen in one run even if someone tries.

Nothing pending from me.
