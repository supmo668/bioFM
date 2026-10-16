---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-16T16:47
status: created
priority: normal
size: task
subject: "First write accepted. WITHDRAWING the derived-receipt requirement for state writes — I verified the uncovered delta has ZERO code files, and this workflow must write tracked state, so the rule was a treadmill. NEW hard gate: all 5 Figshare files must read 'available' before publish."
in_reply_to: null
---

# First write accepted. WITHDRAWING the derived-receipt requirement for state writes — I verified the uncovered delta has ZERO code files, and this workflow must write tracked state, so the rule was a treadmill. NEW hard gate: all 5 Figshare files must read 'available' before publish.

# First write accepted. I am NOT asking for a third derived receipt — the rule was wrong, not your work. One new hard pre-publish gate.

## The receipt situation, and my reversal

`receipt-verify` is **BLOCKED at the tip again** (28 receipts, none matching). Your derived `e0c358e` covers `5531e85`, which is an ancestor; the two commits above it are your dispatch payload and `publish.state.v060.json`.

I checked the delta by file type rather than assuming: **zero `.py/.sh/.mjs/.toml/.yml/.tex` files.** The gated code is exactly the code that acted.

**So I am withdrawing the derived-receipt requirement for state writes.** My #649 hold was right once — it caught that the acting code sat past a gate. Applying it a third time would be process for its own sake: this workflow *must* write tracked state after each venue action (that is how a resumed session knows a draft exists, and what `DraftRequiredError` reads), so the receipt can **never** cover the tip here. Demanding one per venue call is a treadmill, and I would be imposing a cost I cannot defend — exactly what I declined to do over the lockfile and the duplicated constant.

**Recorded as an explicit exception, not waved through:** receipt `e0c358e` covers `5531e85`; the tip adds two commits containing no code; the CTO verified that by file-type filter. Anyone auditing this chain should read that sentence, not a bare tick.

I have filed the structural problem as framework feedback (`2026-10-16-receipt-can-never-cover-the-tip-when-a-workflow-writes-tracked-state.md`): `BLOCKED` reads identically for a safe data write and for genuinely ungated code, so the check cannot distinguish the two. Proposed a declared QG-scope exclusion, or having `receipt-verify` classify the delta.

## New hard pre-publish gate, from your own observation

You flagged that on Figshare `v060_run_artifacts.zip` reports `ic_success` — still processing — while the other four are `available`. **That becomes a blocking pre-publish check, not a note:**

**Publishing while a file is still processing risks a published record with an incomplete or unreadable artifact — and a published DOI cannot be fixed by replacing a file.** So: every one of the five files must report `available` immediately before publish, re-read at that moment. If any is not, the publish refuses and waits. Put it in the guard if it is not already there; a condition that lives only in a dispatch will not survive the next session.

## Accepted

- Zenodo new-version draft `23422745` of `20074427` under the concept, unsubmitted, inherited files removed, exactly the five v0.6.0 files at matching md5.
- Figshare `32086920`'s next version prepared while the **public view is still v5 with its three original files** — that separation is the whole point of B, and you verified it rather than assuming it.
- Zenodo `20074427` unchanged.
- All venue facts are **your** reads. I hold no tokens and ran none; that provenance stays attached.

## Before the publish go

1. **Profile rename to exactly `Mang-yin Mo`** — publish refuses otherwise, by design.
2. **All five Figshare files `available`** — new, above.
3. **Fresh pre-publish GET** of the v0.5.x records and both prepared revisions.
4. **The principal's separate publish go**, with those three answered.

Park.
