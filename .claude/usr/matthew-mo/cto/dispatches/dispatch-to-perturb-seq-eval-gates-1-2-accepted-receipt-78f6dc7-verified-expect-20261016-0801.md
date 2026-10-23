---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-16T07:01
status: created
priority: normal
size: task
subject: "Gates 1-2 accepted: receipt 78f6dc7 verified, expected_author line read. You turned my 'GET and report' into a DraftMismatchError refusal — third time you've upgraded an instruction into a tool that won't proceed. Profile not renamed; publish correctly refuses. Park."
in_reply_to: null
---

# Gates 1-2 accepted: receipt 78f6dc7 verified, expected_author line read. You turned my 'GET and report' into a DraftMismatchError refusal — third time you've upgraded an instruction into a tool that won't proceed. Profile not renamed; publish correctly refuses. Park.

# Gates 1 and 2 accepted. You upgraded gate 2 from a check into a refusal — that is the right instinct, again.

## Verified

Receipt **`78f6dc7` VERIFIED**; boundary `29c9da6` **is an ancestor** of `origin/perturb-seq-eval` (`d3e3028`); `publish.yml:164` carries `expected_author: "Mang-yin Mo"`. Read the line.

## What you did better than I asked

I set gate 2 as *"GET-confirm the author name and report the exact string"* — a check whose force depends on whoever runs it remembering to look. You made it **`DraftMismatchError` against `expected_author`**, so a publish run **refuses** unless the draft's authors match exactly. That is the third time you have turned one of my instructions into a mechanical refusal (`DraftRequiredError`, the no-hardcoded-version grep, now this), and each time it was the right upgrade: **an instruction I have to remember to enforce is weaker than a tool that will not proceed.**

And it never touches `/authors` — the fix stays the profile, never the payload, as ruled. Testing the unrenamed, duplicate and empty cases rather than only the happy path is what makes that credible.

**C1 is the catch worth noting:** a comment had contradicted the deliberate name-form difference. That is precisely the "somebody later 'fixes' one to match the other" failure I asked you to guard against, and it had already started — in a comment, in the same change that established the convention. Found by the gate.

## State, plainly

**The profile is NOT renamed.** Your GET returns `['Mangyin Mo']`; `expected_author` is `Mang-yin Mo`. So a publish run **refuses today, by design**. Nothing is wrong and nothing needs fixing — the system is correctly blocked on a human action.

I have told the principal exactly what is needed: rename the Figshare profile to **`Mang-yin Mo`**, that exact string, hyphen included. The guard is an equality check, so "Mangyin Mo" or "Mang-Yin Mo" will keep refusing.

## Remaining

- **Gate 3** — re-assert the superseded records by GET immediately before the publish go. Not from the earlier dispatch; fresh.
- **Gate 4** — payload back to the principal for their **separate publish go**.

Park until the rename. Do not re-GET on a loop waiting for it; the principal will say when it is done.
