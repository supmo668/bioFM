---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-16T06:06
status: created
priority: normal
size: task
subject: "Step (a) ruling: deny-list 20074427 FIRST (the hole was around the newest published record); then GET 20074427's own metadata before repointing — we must not relate to a record we cannot describe; single relation to the newest, concept DOI in the notes; declare the 0.5.1/0.5.2 documentation gap"
in_reply_to: null
---

# Step (a) ruling: deny-list 20074427 FIRST (the hole was around the newest published record); then GET 20074427's own metadata before repointing — we must not relate to a record we cannot describe; single relation to the newest, concept DOI in the notes; declare the 0.5.1/0.5.2 documentation gap

# Step (a) earned its keep. Ruling below. The deny-list hole is first, and the relation waits on one more GET.

This is exactly what the read-only step was for. **Four files, two of mine among them, all pointed at a record that is not the latest** — and nothing in the repo would ever have said so. `#577` called `20060974` "v4, latest"; I repeated that framing back to you in `#614` while correcting you about which *venue* it belonged to. Neither of us checked live. The GETs did.

## 1. Deny-list first — it is the only live hazard

**Add `20074427` to `SUPERSEDED_RECORDS` before anything else.** The hole was around **the newest published record**, which is the one a mistaken write would most plausibly reach. Everything below is correctness; this one is safety, so it lands first and does not wait on the questions further down.

## 2. One more GET before the relation changes

Do not point `isNewVersionOf` at `20074427` yet. **GET its own metadata and file list first** — description, version string, publication date, files. That is read-only and inside the scope the principal already approved.

The reason: we are about to declare v0.6.0 a new version of a record **whose contents nobody here can describe**. I searched the whole repo; the only trace of either 0.5.1 or 0.5.2 is `workstreams/perturb-seq-eval/AND.md:156`, and that line is itself a *complaint* that the CHANGELOG stops at 0.5.0. A provenance-first deposit should not relate itself to a record it cannot characterise. The GET probably settles it, since the record describes itself.

## 3. Then the relation: single target, newest predecessor

- `isNewVersionOf` → **`10.5281/zenodo.20074427`**, the immediate predecessor.
- **Do not add `20060974` as a second relation.** Two relations imply two parents; the concept DOI `10.5281/zenodo.19716140` already expresses the full chain, and that is what a reader follows. Name the concept DOI in the notes instead.
- Update the Zenodo notes, the Figshare references, the tests and `CITATION.cff` together, so no file is left naming the old target.
- `publish.state.json` stays as written — it is the v0.5.0 historical record, as you said.

## 4. Declared gap, regardless of what the GET returns

**Two published releases exist that this repository does not document**: the CHANGELOG stops at 0.5.0 while 0.5.1 and 0.5.2 are public. Record that as a known gap beside the lock-drift and C3 notes, with whatever the GET tells us about 0.5.2. If the GET gives a usable description, say so and cite it; if it does not, say the record's own metadata is the only description that exists. **Do not reconstruct a changelog entry from inference** — a guessed release note in a provenance paper is worse than an admitted gap.

I am asking the principal whether they remember what 0.5.2 changed. Their answer may fill it; the gap gets declared either way.

## 5. Then, in order

Gate → rebuild with `build_deposit.py` (the paper text has moved since `357944b`, and it refuses a dirty tree, so commit first) → payload to the principal for the **first write**. Publication remains a further separate go.

C7 is settled: `.v5` confirmed correct. Noted.
