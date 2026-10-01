# CTO disposition — lung-on-chipsim Stage 1, archived with the record preserved

**Written by the CTO 2026-10-01. This is a separate note, not an edit:** everything beside it in this
directory was authored by the lung-on-chipsim agent and is covered by Hash A
`0219b888…c68f9` over 116 files. Hash-covered evidence is never rewritten here; corrections are
appended, and a retroactive edit to it is the principal's alone.

## The ruling

The final gate FAILED on the same mechanism (escalation #562). Under approval-log row 61 (principal,
verbatim *"Stop; the mechanism is the result"*) and CTO #541, Stage 1 **closes at the scope reached**:
no QGR receipt is signed, nothing is pushed, the branch does not land.

Asked what should become of the branch, the principal chose, 2026-10-01:
**“Archive; preserve the record on main.”** So the branch is archived unlanded and unpushed, and its
record is copied here so the evidence does not depend on one machine's disk.

## What was verified before copying, and what was withheld

The CTO does not accept a closure on its own report. Verified independently at the branch tip:
no receipt exists in `qgr/` for this gate; the remote `lung-on-chipsim` is still at `c04e701`,
435 commits behind the local HEAD, so nothing from this work was pushed; the tree is clean.

bioFM is a **public** repository, so the agent's own content-scan instrument
(`qgr/evidence/scan-artifacts.py`) was re-run read-only at the tip rather than trusting the last
recorded scan. Verdict **PASS**, `shapes_on_audit_surface: 0`.

**78 of the 83 files were preserved. Five were withheld, each carrying structure shapes:**

| Withheld | Shapes | Why |
|---|---|---|
| `reports/2026-09-15-stereo-guard-tms/merge_report.json` | 229 structure | inside a classified root — reported, not fatal, *there*; publishing it to a public trunk is a different exposure |
| `reports/2026-09-15-stereo-guard-tms/merge_report.md` | 98 structure | same |
| `parked/README.md` | 9 structure | same |
| `qgr/evidence/e23-draft-measure.py` | 10 structure | same |
| `qgr/findings-20260917-s7.md` | 1 structure | same |

They remain on the archived branch. Publishing them would require redaction, and redacting
hash-covered evidence is the principal's decision, not the CTO's — so they were excluded rather than
edited. **This note is the record of that gap**: the preserved set is the record minus these five.

## What the closure establishes (the agent's result, not the CTO's summary of it)

Read `stage1-closure.md`. One mechanism: *a fix is verified against the thing that was changed, not
against the property the claim names.* Nine dated instances; **six were introduced by the repair of a
previous instance**, which is what makes it a mechanism rather than a list of mistakes.

Two things the CTO carries forward as its own, because they bear on every workstream here:

1. **An artifact that measures the process which approves it must pin its measurements to a revision
   of that process, and re-derive them at the moment of approval.** The paper pinned to plan hash
   `ae894db`; rows #58–#61 all carry that hash "(unchanged)", so the pin could not discriminate, and
   the published figure was two rows stale at its own closing. The agent's first draft called this a
   fixed point, then **withdrew the stronger claim in the document that publishes it** — the behaviour
   the branch exists to demonstrate.
2. **A timing ceiling measured under load is not a ceiling.** 453 s clean versus 900 s killed at 82 %
   with 23 concurrent pytest processes. Reported as TIMEOUT, not as substantive failure. The samples
   are not comparable and a clean re-measurement is owed before any future ceiling call. That is the
   CTO's to schedule.

## Carried forward elsewhere

- `tree-bracket` returned `TREE_UNCHANGED` mid-review, but the final verification could not be
  produced: its token was reaped from the system temp directory, so the attestation for the full
  window is **UNKNOWN**, recorded as UNKNOWN rather than as a pass. Sent to the airdlc maintainer as
  framework feedback (a fixed per-repo token path).
- **R-10's extent grew (S-20)**: `fatal_counts` is a new fatal key on an instrument the register binds
  as untested, so row 61's deferral was taken at a smaller extent than now exists. Recorded against
  the deferral.

## For a successor

The agent's guidance is adopted as written: read **S-01, S-02, S-06, S-07, S-20** first, and do **not**
open by repairing the register — on this branch's record, repair is how six of the nine instances
arrived.
