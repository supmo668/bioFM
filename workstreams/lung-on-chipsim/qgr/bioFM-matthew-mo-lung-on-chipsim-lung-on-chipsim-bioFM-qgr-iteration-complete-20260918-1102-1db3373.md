---
receipt_version: 2
type: qgr
boundary: iteration-complete
org: bioFM
principal: matthew-mo
agent: lung-on-chipsim
workstream: lung-on-chipsim
project: bioFM
diff_base: 773e64d
hash_a: 1db337346857dda99817f9d79fb5e6554b0321bcfb959c54fe71e24533ec443d
hash_b: 1d08376de5d3bd3f3220bbfc1deeb631d227779450194dfd1347e8848772d8b7
hash_c: 1d08376de5d3bd3f3220bbfc1deeb631d227779450194dfd1347e8848772d8b7
hash_d: 1d08376de5d3bd3f3220bbfc1deeb631d227779450194dfd1347e8848772d8b7
hash_d_source: "auto-approved — no principal 1B1"
hash_e: 1db337346857dda99817f9d79fb5e6554b0321bcfb959c54fe71e24533ec443d
date: 2026-09-18T11:02
---

# Receipt: iteration-complete — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 1db3373 — artifact entering the gate
- E (final):    1db3373 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  1d08376
- C (triage):    1d08376
- D (principal): 1d08376 — auto-approved — no principal 1B1

## Review Summary
§13.3: CTO Ruling 1 — a staged tree that lands in the tree it scans is a guard reading its own output, reachable via $TMPDIR alone; SIGKILL residual accepted and documented; gitlink domain pinned. Hash A == Hash E: rulings, not a review-and-fix cycle.
