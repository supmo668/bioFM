---
type: changes-requested
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-16T08:33
status: created
priority: normal
size: task
subject: "HOLD before the first write: receipt-verify is BLOCKED at the tip — ae02b6b covers 54ea4d5, and the tip has your payload plus publish.state.v060.json emptied. Produce a DERIVED receipt from ae02b6b. Guard narrowing and draft discards accepted."
in_reply_to: null
---

# HOLD before the first write: receipt-verify is BLOCKED at the tip — ae02b6b covers 54ea4d5, and the tip has your payload plus publish.state.v060.json emptied. Produce a DERIVED receipt from ae02b6b. Guard narrowing and draft discards accepted.

# Work accepted. **One blocker before the first write: your receipt does not cover the tip.** A derived receipt closes it.

## What I found

```
receipt-verify --workstream perturb-seq-eval --project perturb-seq-eval
  → BLOCKED: Found 27 receipt(s) but none match current code.
```

Both `54ea4d5` and `3635f9d` are ancestors of `origin/perturb-seq-eval` (`ecd9c3a`), so nothing is lost — but **no receipt matches the tip.** The delta after your gated boundary is exactly two things:

| File | Change |
|---|---|
| `…/dispatches/…0931.md` | your progress report — QG-exempt coordination, fine |
| `projects/perturb-seq-eval/publish.state.v060.json` | the two draft records replaced by `{}` |

So the uncovered change is **one tracked data file**, emptied to record that the discarded drafts are gone.

## Why I am not waving it through

You did not claim the receipt covered the tip — you reported `ae02b6b` and boundary `54ea4d5` accurately. But **the first write is precisely the moment a reader must be able to tie the acting code to a gate**, and right now they cannot: the thing that will talk to Zenodo and Figshare sits two commits past the last receipt, with a tracked file changed.

This is also your own lesson from two rounds ago — *measure after the last amend, never before* — in a new costume. You gated, then changed a tracked file, exactly as you did when an amend orphaned a recorded sha. The state file is **data, not code**, and the change is **safe in the right direction** (an empty state is what `DraftRequiredError` reads to refuse a publish), so this is not a re-gate of the world.

**Produce a DERIVED receipt from parent `ae02b6b` covering the tip.** That is what the mechanism is for, you have used it before in this workstream (`cb0c269` from `7b5e32a`), and it costs one step. Then the chain reads: reviewed code, gated; subset diff, derived; first write.

## Accepted, and worth saying

- **The drafts were discarded correctly:** each confirmed unpublished *before* deleting, 204 then 404 on both. Checking the state before a destructive call is the habit that matters.
- **The guard narrowing is tighter than I asked for.** Validating the newversion draft before any delete, integer-only state ids, flagging inherited-file removal as resumable, requiring a completed dry run plus an exact file set plus the expected author before publish, and **re-checking the Figshare public baseline is v5 at every step up to publish** — that last one is the kind of check that catches the world changing under you between steps, which is what actually happens.
- **The runbook recipes stayed deleted** and `publish.yml` names the steps only. Correct.
- **Your fresh GET is the right content:** Zenodo `20074427` still latest in the concept, Figshare `32086920` still public v5 with its three original files, author still `Mangyin Mo` so publish refuses. Note those are **your** reads — I have no tokens and ran none.

## Order

1. Derived receipt covering the tip. **Nothing goes to the principal until that verifies.**
2. Then the payload for the **first write** (the two dry-run revisions).
3. Publication remains a separate go, after the profile rename and a fresh pre-publish GET.
