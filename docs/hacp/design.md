# §design — bioFM

Architecture, interfaces, and decisions with their declined alternatives.

## Where the design lives

- **lung-on-chipsim** — `workstreams/lung-on-chipsim/A-and-D.md`, and a build plan carried across
  52 hash-locked revisions in `plan/build-plan.md`.
- **perturb-seq-eval** — `workstreams/perturb-seq-eval/AND.md`, with decisions D1–D5.

## The decision record is itself an artifact

`plan-approval-log.md` is append-only and each revision is hash-locked to the plan text it
approved, with the approval route recorded per row. It captures declined alternatives and
reversals contemporaneously rather than reconstructing them afterwards.
