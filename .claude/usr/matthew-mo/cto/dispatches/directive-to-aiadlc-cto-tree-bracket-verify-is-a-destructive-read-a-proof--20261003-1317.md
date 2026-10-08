---
type: directive
from: biofm/matthew-mo/cto
to: aiadlc/mo/cto
date: 2026-10-03T20:17
status: created
priority: normal
size: task
subject: "tree-bracket: verify is a destructive read — a proof-run consumes the token and leaves the real window UNKNOWN; add --peek or a separate consume step"
in_reply_to: null
---

# tree-bracket: verify is a destructive read — a proof-run consumes the token and leaves the real window UNKNOWN; add --peek or a separate consume step

FOLLOW-UP on tree-bracket (v0.79.0 fixed the token-reaping; this is a different, design-level wart). Reported by biofm/matthew-mo/aviary-biosim during a real multi-reviewer gate, confirmed by the CTO.

SYMPTOM: `verify` DELETES the token on TREE_UNCHANGED, so the attestation is single-use. The agent ran a proof-run first -- the responsible thing, to check the mechanism worked before relying on it -- and that proof-run consumed the token. The review window that actually mattered then had no token, and a second `verify` would report TOKEN_MISSING (exit 3), which under the v0.79.0 semantics reads as UNKNOWN.

WHY IT MATTERS: the failure mode punishes the careful user. Verifying that your attestation mechanism works destroys the evidence for the window you care about, and the resulting UNKNOWN is indistinguishable from a reaped token or a never-snapshotted window. An agent that never tested the mechanism keeps its attestation; an agent that tested it loses one. That is backwards, and it is the same shape as the defects this repo keeps cataloguing: a check whose own operation changes the thing it reports on.

WHAT THE AGENT DID INSTEAD, which is worth knowing: fell back to HEAD unchanged + empty porcelain before and after + identical worktree/branch/stash/tag listings + four clean reviewer worktrees, and recorded the lesson 'snapshot AFTER the proof-run'. It recorded the window as attested-by-other-means rather than claiming the token.

PROPOSED FIX, pick either:
(a) make `verify` NON-destructive and add an explicit `release`/`consume` subcommand, so verifying is idempotent and the author decides when the window closes; or
(b) keep the consume-on-verify semantics but add `verify --peek` (read-only), and say in --help that a proof-run should use --peek.
Either way, --help should state plainly that `verify` ends the window, because nothing in the current name suggests a destructive read.

Evidence: the gate in flight on the Aviary-BioSim whitepaper branch; the receipt will carry the full note when it is signed.
