---
type: plugin-feedback
target: aiadlc plugin (bioFM) — quality-gate / QGR receipts
plugin_version: 0.56.0
reporter: bioFM/matthew-mo/cto
date: 2026-09-24
scope: plugin / operating-system behavior — NOT repo/app work
---

# 🟠 Receipt hashes B and C attest to findings files that live in scratch and are then deleted

**Reported by:** `biofm/matthew-mo/aviary-biosim`, dispatch #211, in answer to a
question I asked it (where is deferred finding F08 recorded?).

## Symptom

Two quality gates produced **42 findings, 19 of them deferred or rejected with
stated reasons**. The full text of every one lived in scratch files under
`/private/tmp/.../` (`raw_findings.md`, `findings_scored.md`, `triage.md`). The
re-gate's scratch directory is already gone; those files no longer exist.

The QGR receipts hash them — **Hash B is "findings", Hash C is "triage"**. So the
receipts now attest to content that nobody can produce, and the reasons 19 findings
were deferred are unrecoverable.

Measured consequence: asked where a specific deferred finding was recorded, the agent
found it in **no repository document at all** — only a one-line token in two
dispatches and a bare token in a handoff list. Confirmed independently: a repo-wide
grep for that finding id, and for `importlib` / `import-mode` / `collection order`,
returns nothing outside dispatch prose.

## This is documented design, and still a defect

`reference/REFERENCE-RECEIPT-INFRASTRUCTURE.md:5-6` is explicit and honest:

> independently verifiable hashes (A and E) plus a **procedural attestation log
> (B, C, D)** — NOT a five-link cryptographic "chain of trust."

So B and C were never claimed to be verifiable, and this is not a spec violation.
The defect is narrower and worth separating from the claim: **hashing a file at a
path that is guaranteed to be destroyed makes the attestation unfalsifiable rather
than merely unverified.** An attestation that cannot be checked even in principle,
because its referent is designed to evaporate, is doing no work — and it *reads* as
though it is, which is the harm. A reviewer seeing "Hash B: findings" reasonably
infers the findings are retained somewhere.

Same family as the ambient-state defects filed 2026-09-16/17, 2026-09-20 and
2026-09-24: **a surface reports on something adjacent to the thing it describes.**
Here the receipt reports that a stage ran while the evidence it attests to is absent.

## Suggested fixes, in order

1. **Write findings to a durable and TRACKED path before hashing.** Findings belong
   beside the receipt, e.g. `<dir>/<receipt-id>/{raw_findings,triage}.md` — the gate
   already produces the files, so the only change is where.

   **Correction, same day (see amendment 2 below): `paths.workstreams_root` is NOT a
   durable path.** My first draft named it, and an agent applied it by hand; in the
   aviary-biosim submodule `.gitignore:13` ignores `workstreams/`, and
   `git ls-files workstreams/` is empty. Findings written there survive scratch
   cleanup but still die with the worktree and are invisible to everyone else. The
   destination must be a path the repo actually tracks.
2. **If findings must stay ephemeral, stop hashing them.** A hash of a deleted file
   is worse than no hash: it implies retention. Replace B and C with a plain count
   (`findings: 42, deferred: 19`) so the receipt claims only what it can support.
3. **Require a disposition line per deferred finding in a durable file.** The reason
   a finding was deferred is the part with the longest useful life, and it is exactly
   what was lost here. One line per deferral, in the repo, is cheap.

## Second-order finding: there is no deferred-findings register

Because of the above, "promote this finding out of the deferred set" is not an
operation anyone can perform — there is no register to promote out of, only a grep
through dispatch history. The agent proposed one and correctly did not author it
unasked. I have now authorised it (one row per finding: id, source gate, severity,
one-line description, disposition, raising dispatch id, receipt Hash E, and whether a
live reproduction exists). That is a repo-level fix for a framework-level gap; the
framework should arguably emit the register itself as part of the gate.

## Amendment 2 — the durable path I named is itself gitignored

The agent applied ranked fix 1 by hand for its next gate: findings and triage now sit
at `workstreams/aviary-biosim/qgr/<receipt-id>/`, and Hash B and Hash C point at files
that exist. Verified. **But that directory is gitignored** (`.gitignore:13` in the
submodule), and nothing under `workstreams/` is tracked, so the evidence is still
worktree-local and invisible to any other reader.

So the fix improves longevity (it outlives `/private/tmp` cleanup) without achieving
durability. **My own ranked fix was wrong on its central point**, and wrong in a way
already filed: `2026-09-17-feedback-filed-from-a-worktree-never-reaches-the-trunk-and-stays-invisible.md`
records the same shape — an artifact written in a worktree under an untracked path
stays invisible. I walked into a known trap while proposing a remedy for a related one.

**Revised guidance:** the gate must write findings to a path that is both outside
scratch *and* tracked by the repo. Which path is a repo-level decision, but
`paths.workstreams_root` cannot be assumed durable, because in at least this repo it is
explicitly ignored. A framework fix should either write to a tracked location or state
plainly that receipts' B and C are worktree-local by design.

## Status

open. Locally mitigated by authorising a hand-maintained register in a **tracked**
location (the submodule's `docs/`, not `workstreams/`), which does not help any other
workstream.
