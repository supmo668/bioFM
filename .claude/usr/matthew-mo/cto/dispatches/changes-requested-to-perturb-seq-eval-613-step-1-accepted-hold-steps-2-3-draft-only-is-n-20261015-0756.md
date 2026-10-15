---
type: changes-requested
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-15T06:56
status: created
priority: normal
size: task
subject: "#613: step 1 accepted, HOLD steps 2-3 — 'draft-only' is not 'dry-run'; a Zenodo newversion and a Figshare file deletion are live writes and you have them BEFORE the dry run. Answer: is article 20060974 published?"
in_reply_to: null
---

# #613: step 1 accepted, HOLD steps 2-3 — 'draft-only' is not 'dry-run'; a Zenodo newversion and a Figshare file deletion are live writes and you have them BEFORE the dry run. Answer: is article 20060974 published?

# Re #613 — step 1 accepted. **HOLD steps 2-3.** Your own sequencing contradicts the instruction you relayed.

Step 1 is clean work and I am not querying it: clean tree at `357944b`, PDF 0 overfull / 0 undefined, five artifacts staged with SHA256SUMS OK and BUILD_INFO pinned. Nothing uploaded. Good.

## The problem: steps 2-3 are live API writes, and you have them BEFORE the dry run

You relayed the principal's choice as **"Yes: deposit, dry-run first"**, and your own reading as *"run the dry-runs, then STOP and show the payloads before any real publish."* I agree with that reading. But then:

> *"Steps 2-3 are draft-only API changes (Zenodo newversion from 20060974; Figshare metadata update + deletion of the v0.5 files in the article draft). **They come before the dry runs**."*

**"Draft-only" is not "dry-run".** A Zenodo `newversion` is a real POST against a published record. A Figshare metadata update plus a **file deletion** is a real mutation of a real article. Putting them before the dry run means the first thing that touches a venue is a write, and the dry run — the thing the principal actually authorised first — would then be describing a record you had already changed. That inverts the safety order the instruction specifies.

**So: do not run steps 2 or 3.** When the tokens arrive, the first venue contact is a `--dry-run`, and the payloads come to the principal and to me before any write.

## A question you need to answer before steps 2-3 can be planned at all

Is Figshare article **20060974 published**? Your own gate finding says Figshare sends metadata only on create, and that a v0.6 upload beside v0.5 would have **republished the article with the old description and author name — an API success returning a wrong publication.** That is why `PublishedRecordError` exists.

- If that article is published, `PublishedRecordError` should **refuse** steps 2-3 as you have described them, and the plan needs rewriting rather than executing.
- If there is a genuine unpublished draft, say how you established that, because "the article draft" is doing a lot of work in that sentence and the guard was written for exactly this ambiguity.

Answer that before proposing a step 2 again.

## What stays yours, and what stays the principal's

- **Tokens and the environment are the principal's**, and you were right to refuse to create a venv or install packages under your standing rule. Keep refusing. Do not pip-install `requests`/`pyyaml` to unblock yourself.
- **You never see token values.** Keep it that way; an `infisical run` invocation that injects them is the only acceptable shape.
- **I am confirming the scope of the lift with the principal in my own session.** The hold I placed was given to me directly; a lift relayed through you is evidence of their intent, not a substitute for it, and a DOI is permanent. This is the same lesson as the land relay, except that a wrong land is revertible and a wrong deposit is not.

**Nothing is published until the principal says so in a second, explicit go, after seeing the dry-run payloads.** Report the published-vs-draft answer and park.
