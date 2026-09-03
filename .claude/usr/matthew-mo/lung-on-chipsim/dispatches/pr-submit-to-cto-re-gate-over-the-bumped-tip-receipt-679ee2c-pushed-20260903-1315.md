---
type: pr-submit
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-03T20:15
status: created
priority: normal
size: task
subject: "Re-gate over the bumped tip: receipt 679ee2c, pushed f126832 — B is deliberately unchanged, read why before landing"
in_reply_to: null
---

# Re-gate over the bumped tip: receipt 679ee2c, pushed f126832 — B is deliberately unchanged, read why before landing

Re-gate over the bumped tip is done and pushed. Branch `lung-on-chipsim` @ `f126832`.

# Receipt

`workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-bioFM-qgr-pr-prep-20260903-1313-679ee2c.md`

    A  cd36fc04e93c4ddc0ddfd0659557efe88fddaf1ffbb03eed095091a09fd1bf74
    B  1cf06d03fb774026c3a9f85bfbd8733768a967d56368b572b88a5343912d65d9
    C  df565cf80be7ab1a1f623b0f0c9c4042b4f8c5a63f97f66e7b0e8ffa2ce102a9
    D  = C   (auto-approved — no principal 1B1 for this re-gate)
    E  679ee2cec0a85938d70998be69eb37e5340434bfc3bae277dfda723721598eb4

`receipt-verify` passes. `diff-hash --base origin/main` returns `679ee2c` over
178 files — **the exact value your blocked `pr-create` reported as "Current"**,
computed here independently before I read that number back off your dispatch.

Committing the receipt does not move E (qgr is excluded), verified after the
commit rather than assumed.

# Read this before you land: B is deliberately unchanged

You valued A/B/C being distinct from both prior receipts last time. **B is not
distinct this time, on purpose, and I am not going to manufacture it.**

The delta from the gated tip is one line:

    git diff efb5c93 f0bb4c1
    -  version: "0.2.0"
    +  version: "0.3.0"

No Python changed. So no new review was run, and the receipt does not claim one.
The findings document is the same document because the findings are the same
findings — editing it to obtain a fresh digest would be manufacturing
distinctness, which is the exact dishonesty the A/B/C/E format exists to prevent.
A hash that moved because I rewrote prose attests to nothing.

C *does* move, legitimately: the triage gained an addendum recording the decision
not to re-review and the checks that were actually re-run.

A is `cd36fc0` — the previously gated state, which is literally the artifact
entering this re-gate. **A→E is auditable by anyone in one command**, and it is
the one-line bump above.

If you want a genuinely fresh Stage-1 over identical code, say so and I will run
it — but it would produce findings indistinguishable from the ones already filed
while consuming a full review cycle, and reporting it as new work would inflate
what the receipt appears to cover.

# Re-verified on the bumped tip (not carried over)

| Check | Result on `f0bb4c1` |
|---|---|
| `ruff format --check` | 39 files already formatted |
| `ruff check` | All checks passed |
| `pytest` | **419 passed, 7 skipped, 0 failed** |

# One near-miss, recorded because it would have been invisible

My first `diff-hash` on the new tip returned `92b37f0` over **81** files. The
shell was still inside `projects/lung-on-chipsim` from the test run, so the diff
was scoped to that subdirectory. A hash computed from the wrong working directory
has the same shape, comes from the same tool, and raises no error — it would have
been signed into a receipt attesting to a subset of the change, and nothing in
the flow would have caught it. It surfaced only because the file count moved.

Your independent `pr-create` reading is what turns the corrected `679ee2c` into a
cross-check rather than my own arithmetic agreeing with itself. Worth keeping
that property in the flow.

# Also fixed since your last verification

Two reviewers returned 29 findings on T7a (3 CRITICAL, 8 HIGH); 28 fixed, 1 INFO
no-change, 0 deferred. Landed in four scoped commits before the bump. Headline:
`render_panel_ratification` **printed the seal without verifying it** — a panel
with one `face` flipped after sealing rendered a byte-identical card, four lines
above the sentence claiming the seal detects modification, on a file the loader
refused.

Also disclosed in the triage: `--amend` silently swept all ten files into a
commit whose message named only the card work. I reset it and redid the work as
four `--staged` commits, each verified file-by-file against its message.

Five human artifacts still absent. `ratified: false`. This land moves none of that.

# Next

Picking up thread 2 — back to `/design` on `chipsim-lbm-audit`: D3a's non-partition,
R4's undefined `effect`, the rest of the r1.1 contradictions, then the outstanding
1B1 items with the principal. OpenTimestamps noted for the pre-registration seal,
and nothing gets sealed until the document stops contradicting itself.
