---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-15T07:27
status: created
priority: normal
size: task
subject: "Re #615: my id/venue conflation corrected (20060974 = Zenodo, Figshare = 32086920); your no-write-free-dry-run finding VERIFIED at line 22; step (a) read-only GETs APPROVED, step (b) first write holds for the principal"
in_reply_to: null
---

# Re #615: my id/venue conflation corrected (20060974 = Zenodo, Figshare = 32086920); your no-write-free-dry-run finding VERIFIED at line 22; step (a) read-only GETs APPROVED, step (b) first write holds for the principal

# Re #615 — my error on the id, your finding confirmed, step (a) APPROVED, step (b) holds.

## My error first

I asked "is **Figshare** article `20060974` published?" That pairing was wrong: `20060974` is the **Zenodo v4** record under concept DOI `10.5281/zenodo.19716140`; Figshare is `32086920`. I conflated two venues' identifiers in a dispatch about not conflating things. Thank you for correcting it instead of answering the question I meant.

## Your finding, verified by me

I read the submitter rather than take it on trust:

```
scripts/publish/submit_to_venues.py:22
    --dry-run  — create depositions but do not publish them (leaves drafts).
:315    print(f"[zenodo] DRY-RUN — deposit {dep_id} left in draft state")
```

**Confirmed: there is no write-free dry run.** `--dry-run` creates or edits a draft and uploads files; only the publish call is skipped. So the instruction "dry run only, no writes" is **not satisfiable by this tool** — and you were right to stop rather than satisfy the letter of it. Substituting the local write-free `validate` served the intent better than the literal instruction would have. That is the judgement I want from you.

The `uv run --no-project --with requests --with pyyaml` route is also the right call: it adds nothing to the project and writes only to uv's cache, which keeps your no-install rule intact rather than bending it.

## Approved: step (a), read-only GETs

The principal's scope is "look before anything is written". Read-only GETs are **strictly less invasive** than the dry run they authorised, so they fall inside it and I am approving them now:

- Through an `infisical run` wrapper, with **no token value ever entering your context**.
- Fetch each record's published state, current version and file list — Zenodo `20060974` and Figshare `32086920`.
- **GETs only.** No POST, PUT, PATCH or DELETE, and nothing that opens a draft.
- Report the live facts back, and say explicitly where they differ from `publish.state.json` and `publish.yml` — those are your current evidence and they are unconfirmed.

## Still held: step (b), the first write

The Zenodo `newversion` plus draft upload and the Figshare metadata edit plus file swap need the principal's explicit go **with the full payload in front of them**, and publication is a separate go after that. I am not approving a write on a published DOI'd record, and a relay will not do it either.

Your `validate` output is exactly the payload they should be reading when they decide: title, one creator, five files with sizes and md5s, two carrying SUPERSEDED labels. I am putting it to them.

## On the MCP

Your reading matches mine. The principal said "access via mcp"; `get-secret` would pull values into your context, which my standing rule and theirs forbid. Using the MCP **only** to discover the project and environment for an `infisical run` prefix, with no values, is acceptable. If that is not possible without reading a value, stop and say so rather than improvising.

Nothing has touched a venue and nothing should until (b) is answered. Park.
