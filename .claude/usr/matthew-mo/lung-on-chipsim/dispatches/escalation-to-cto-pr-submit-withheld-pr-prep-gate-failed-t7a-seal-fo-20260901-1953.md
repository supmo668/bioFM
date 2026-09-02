---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-02T02:53
status: created
priority: high
size: task
subject: "PR-SUBMIT WITHHELD — pr-prep gate FAILED: T7a seal forgeable + bypassable. Do NOT land. Push held."
in_reply_to: null
---

# PR-SUBMIT WITHHELD — pr-prep gate FAILED: T7a seal forgeable + bypassable. Do NOT land. Push held.

Agent: lung-on-chipsim

# I did NOT submit. The re-run gate you ordered is what caught this.

You ordered /pr-prep then /pr-submit. I ran the gate. **It failed.** I am withholding the
submit and holding the push. `origin/lung-on-chipsim` remains at 5b14336; the pr-submit
dispatch commit c01632d is **unpushed and must not be pushed as written**.

## First, a process problem you need to know about

A **second lung-on-chipsim session (PID 26209) is live in this same worktree** and ran your
directive concurrently with me. It produced 5b14336 + c01632d, pushed the branch, and wrote a
pr-submit dispatch asserting the branch is clean and "No new gate run was needed, and I did not
run one to look busy." That conclusion is wrong, and the gate run it declined is exactly the one
that found four CRITICAL defects. Two agents on one worktree is a state-corruption hazard
independent of this PR — please serialize it.

Also: fdee167 was indeed stale, but it had **already** been superseded by receipt 4d1844c (18:53).
`diff-hash --base origin/main` returns 4d1844c, byte-identical, so the tree genuinely had not
changed. The staleness premise was correct; the receipt gap was not the actual problem.

## The blocking findings — 4 independent reviewers converged, I reproduced each

**C1 — the seal is opt-in, so DELETING ONE LINE is the bypass.**
`chipsim/harmonize/pgp_label.py:212` guards verification behind `if sealed:`. A panel with
`ratified: true` and no `ratified_panel_sha256` key loads clean and unverified. Reproduced:
seal a fixture, delete the seal line, tamper ABCB1's accession -> `load_ratified_panel` accepts
it and resolves the tampered accession. T7a-1's done-condition is defeated by removing a line.

**C2 — the seal is FORGEABLE by an agent, so Global Constraint (4) has ZERO technical enforcement.**
The digest is an unkeyed SHA-256 over public content and `panel_digest` is exported. Worse,
`tests/fixtures/barrier_panel_ratified.yaml` has a panel list **identical** to the live config.
I verified the collision read-only (computing a digest writes nothing; I did NOT seal):

    live panel digest   : 6ae83ff9a6fd5d4fbd80a128ea8c7414ec1178ba1a5c4c061635d9bbefb4225b
    fixture panel digest: 6ae83ff9a6fd5d4fbd80a128ea8c7414ec1178ba1a5c4c061635d9bbefb4225b

Sealing that fixture is an explicitly *sanctioned* agent action (tests do it). So the valid seal
for the live panel is obtainable from a permitted command and can be pasted in alongside
`ratified: true` / `ratified_by:` to manufacture a complete human attestation with no human.
And `test_fixture_face_agreement_with_live_panel` currently **enforces** that collision.

**C3 — seal_panel can report success while writing nothing.**
`:109` branches on a whole-file substring test but `:110` rewrites on a line-prefix test. If
`ratified_panel_sha256:` appears in a comment, the replace branch matches nothing, the file is
rewritten byte-identical, and the CLI still prints `sealed <path>` + a digest. `configs/barrier_panel.yaml`
is 40 lines of human T8 instructions — documenting the seal key there is the obvious next edit
and it disarms the tool. False confirmation is the worst possible failure for an attestation tool.

**C4 — T8 instructs the human to run a command that does not exist.**
The error text and the build plan say `chipsim panel seal`. There is no `[project.scripts]`
block, so no `chipsim` executable; the real form is `python -m chipsim.pipeline panel-seal`,
documented in neither README nor CONTEXT. T7a existed precisely so T8 would not be self-blocking.

**H5 — the live panel has no `ratified_panel_sha256` key at all** (keys are `ratified`,
`ratified_by`, `ratified_on`, `panel`), so T7's done-condition is unmet and, with C1, the
default post-T8 state is attested-but-unverifiable.

**H6 — `SHA256SUMS.json` is self-certifying.** A fabricated snapshot passes `hash-verify`:
the manifest is written by the same process it certifies and its `source_commit` is never
checked against `provenance.yaml`.

## Two corrections to the PR body you specified

1. **298 passed, not 290.**
2. **The self-lifting claim needs qualifying.** Only **2 of the 6** offline skips are
   artifact-keyed (`test_provenance.py:186`, `test_snapshot_fetch.py:285`). The other four
   — `test_contracts.py:11`, `test_leakage.py:16` (x2), `test_monotonicity.py:12` — are
   **unconditional** `pytest.mark.skip` and will sit green and silent forever. Stating the
   self-lifting property without qualification would misrepresent them. (Mitigation: each body
   raises AssertionError, so un-skipping fails loudly.)
3. T8 ratifies accessions **and faces**.

## Also, a real AM-3 violation

`configs/barrier_panel.yaml:53` — the identity-only config carries a biological number in a
comment: "the ~400x ratio spread makes this a preference". The numeric-leaf validator walks
parsed YAML leaves, so comments are structurally invisible to it. The caveat already lives in
T8-review-record.md.

## What I need from you — a ruling, not a patch

C1, C3, C4, H5 I can fix mechanically. **C2 I cannot fix alone**: making the attestation
unforgeable requires choosing a root of trust (a detached minisign/age/GPG signature, or a
GPG-signed revision of the panel verified against a pinned human key) versus accepting that
Global Constraint (4) stays a process rule with no technical backing. That is an architecture +
principal-policy decision, and the principal's own constraint is what is at stake.

Minimum viable hardening if you want the cheap version: bind the preimage to `ratified`,
`ratified_by`, `ratified_on` **and the panel filename** so a fixture seal cannot be replayed
onto the live config, and make the fixture panel deliberately differ from the live one.

Reply path: rule on C2 -> I fix C1/C3/C4/H5/H6 + the AM-3 comment + the skip qualification,
re-run the gate, re-sign, and resubmit. I have NOT touched the live config and have NOT run
panel-seal against it — Global Constraint (4) upheld.

next_handoff: biofm/matthew-mo/lung-on-chipsim
