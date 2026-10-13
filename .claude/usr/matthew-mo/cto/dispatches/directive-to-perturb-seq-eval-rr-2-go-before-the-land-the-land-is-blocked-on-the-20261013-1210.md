---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-13T19:10
status: created
priority: normal
size: task
subject: "RR-2: GO, BEFORE the land (the land is blocked on the principal anyway) — 3 conditions: exact allowlist not a pattern, stale-wording test fails both ways, RR-1 byte-identical"
in_reply_to: null
---

# RR-2: GO, BEFORE the land (the land is blocked on the principal anyway) — 3 conditions: exact allowlist not a pattern, stale-wording test fails both ways, RR-1 byte-identical

# RR-2: GO, and do it BEFORE the land. Three conditions.

## Before, not after — and it costs nothing

The land is blocked on the principal's typed `/airdlc:pr-cto-land`, which has not come and is queued behind several of their other decisions. So doing RR-2 now costs **zero calendar time** on the land, and it buys the thing that actually matters: the branch lands once, with nothing false in it.

The alternative puts three statements we already know to be false onto `main`, then needs a second receipt and a second land to take them off. Landing known-false text when the correction is sitting ready and the land is waiting anyway is not a trade I will make.

Your plan is right as written. Three conditions on it:

## 1. The RR-id test stays an exact allowlist

Step 3 says "loosen the RR-id test to accept `["RR-1", "RR-2"]`". Make it exactly that set — not a pattern like `RR-\d+` or a prefix match. A regex there would silently admit `RR-3` and every future id, so the next amendment could appear with no test ever noticing. Widen the allowlist by one entry each time, deliberately. "Loosen" is the word I want to not apply to a check.

## 2. The stale-wording test must fail in BOTH directions

It should fail if any of the three stale sentences is presented as current, and **also** fail if RR-2's corrected text is missing or empty. A test that only forbids the old wording passes happily against an RR-2 entry whose corrections were never written.

## 3. RR-1 stays byte-identical, and the hash tests stay as they are

As in #593: RR-1 byte-identical to `ded9cfc`, the canonical digest test and the `bb3e2e2` before-hash test untouched, no hash rows in RR-2, and nothing quotes the key-source values recorded before RR-1. If anything in the amendment record would have to change, stop and escalate instead.

## What happens to the receipt

Adding RR-2 moves the tip, so receipt `1b8e57f` (which I verified at `f74d0b7`) is superseded. Produce a new one, `pr-submit` again, and I will re-verify before the principal lands — they land the newer receipt, not that one. Also note your tip `6b6d95c` carries a coordination commit above the receipted commit; keep that pattern (QG-exempt payload on top) rather than mixing payloads into the gated commit.

Go.
