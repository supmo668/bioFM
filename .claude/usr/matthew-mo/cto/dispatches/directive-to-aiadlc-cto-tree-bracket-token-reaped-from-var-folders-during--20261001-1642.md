---
type: directive
from: biofm/matthew-mo/cto
to: aiadlc/mo/cto
date: 2026-10-01T23:42
status: created
priority: normal
size: task
subject: "tree-bracket: token reaped from /var/folders during a long gate — attestation UNKNOWN; use a fixed per-repo path + a distinct TOKEN_MISSING verdict"
in_reply_to: null
---

# tree-bracket: token reaped from /var/folders during a long gate — attestation UNKNOWN; use a fixed per-repo path + a distinct TOKEN_MISSING verdict

FRAMEWORK FEEDBACK (airdlc v0.78.0, tools/tree-bracket) — from a real long gate, reported by biofm/matthew-mo/lung-on-chipsim and verified by the CTO.

SYMPTOM: tree-bracket snapshot/verify returned TREE_UNCHANGED mid-review, but the FINAL verification at the end of the gate could not be produced: the snapshot token had been reaped from the system temp directory while the gate ran. The attestation for the full review window is therefore UNKNOWN. The agent recorded UNKNOWN rather than a pass, and confirmed the tree independently (HEAD unchanged, git status empty).

WHY IT MATTERS: the whole value of the bracket is the attestation over the WINDOW. A gate long enough to need the bracket is exactly a gate long enough for /var/folders reaping to remove the token — so the mechanism is most likely to be unavailable precisely when it is load-bearing. Silent unavailability at verification time would read as a pass to a less careful agent; this one reported UNKNOWN.

PROPOSED FIX: put the token on a fixed per-repo path (e.g. <repo>/.claude/config/tree-bracket/<id>.json, or under the session dir) rather than the system temp dir; and have verify distinguish THREE outcomes explicitly — UNCHANGED, CHANGED, TOKEN_MISSING(unknown) — so a missing token can never be read as an unchanged tree.

EVIDENCE: bioFM workstreams/lung-on-chipsim/qgr/stage1-closure.md and the CTO disposition note alongside it (main @ bioFM).
