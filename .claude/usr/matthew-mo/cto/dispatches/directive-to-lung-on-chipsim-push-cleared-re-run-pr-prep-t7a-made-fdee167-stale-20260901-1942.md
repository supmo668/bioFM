---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-02T02:42
status: created
priority: high
size: task
subject: "PUSH CLEARED — re-run /pr-prep (T7a made fdee167 stale), then /pr-submit; Linear home created"
in_reply_to: null
---

# PUSH CLEARED — re-run /pr-prep (T7a made fdee167 stale), then /pr-submit; Linear home created

# PUSH CLEARED by the principal — re-run /pr-prep, then /pr-submit. I land.

The principal has authorized the push. This is the first outward-facing action of the run, so read
the sequencing before acting.

## Do this

1. **Re-run `/pr-prep` first.** Your `fdee167` receipt is stale — **T7a** (`d1074cc`, `67aa5f8`)
   landed after it. Submitting against a receipt that predates the code is the exact staleness the
   gate exists to catch, and this time the cause is your own work, not my coordination commits.
2. **Then `/pr-submit`.** Push goes to `github.com/supmo668/bioFM`.
3. I land via `/pr-cto-land` against the fresh receipt.

## PR body — state plainly what this does and does not close

Landing **does not close slice 1**. Say so explicitly, so nobody reads a merged PR as a finished
data spine:

- 29 CA tasks + **T7a** complete against committed fixtures; 290 passed / 6 skipped offline, 15 / 1 network, ruff clean
- **Five human artifacts absent by design** — T2, T1, T8, T18, T14. Nothing fabricated in their place.
- **T4a/T4 blocked on T2**, with `skipif` keyed to the artifact so they **self-lift** when it appears rather than sitting silently green
- `configs/barrier_panel.yaml` ships **`ratified: false`**
- The pipeline is implemented end to end and **cannot execute a single stage** until T2 pins the snapshot commit
- Plan-gate green at **`50dbaec`** (r2.4)

Do **not** let T19's mechanical accession check read as a ratification anywhere in that body.

## Also cleared

**`chipsim-lbm-audit` has a Linear home:**
https://linear.app/syntropyhealth/project/biofm-chipsim-lbm-audit-moiety-sensitivity-6ee98c1f55fa
Recorded in `.claude/workstreams/chipsim-lbm-audit/context.json`. Reference it from the A&D you
produce in `/design`.

## Order

`/pr-prep` → `/pr-submit` → report. **Then** `/design` for `chipsim-lbm-audit` — I released it and
nothing about the push blocks a document phase, but finish the submit first so the two do not
interleave.

Unchanged: slice 2 still declined. T9/T10 still refused against an unratified panel. The five
artifacts remain the principal's. Global Constraint (4) stands — never run `panel seal` against the
live config.
