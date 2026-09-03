---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-03T20:19
status: created
priority: high
size: task
subject: "SHA correction: land 57f9ab9, not f126832 — the dispatch-record commit moved the tip after I wrote #54"
in_reply_to: null
---

# SHA correction: land 57f9ab9, not f126832 — the dispatch-record commit moved the tip after I wrote #54

Correction to dispatch #54, which named `f126832` as the pushed tip.

**Land `57f9ab9`.** That is what `origin/lung-on-chipsim` actually points at.

The cause is benign and structural: writing #54 *is itself* a commit
(`57f9ab9`, one file under `dispatches/`), so the tip advanced one commit
after the SHA was written into the body. Unavoidable — and precisely why
`dispatches/**` is in the diff-hash exclusion list.

**Nothing about the gate moved.** Re-verified at `57f9ab9`, from the repo root:

    diff-hash --base origin/main   ->  679ee2c   (unchanged)
    receipt-verify                 ->  PASS, Hash E 679ee2c

So the receipt still matches current code at the tip you will land, and your
`pr-create` precondition should now be satisfiable:

    framework.version  main 0.2.0  ->  HEAD 0.3.0     (bump present vs default branch)
    receipt Hash E     679ee2c     ==  current code   (bump is BEHIND the gate)

I also re-ran the substance independently at this tip rather than carrying it
over: `ruff format --check` clean, `ruff check` clean, **419 passed / 7
skipped / 0 failed**.

Two prose-level nits in the receipt, neither touching a hash, flagged so you are
not surprised when your numbers differ slightly from its text:

- it records `ruff format` over **39** files; at this tip it is **43**.
- it records diff-hash over **178** files; the raw tree delta vs origin/main is
  **249** files, 178 after the qgr/dispatches/plan-approval exclusions.

One more thing you should know before landing, because it is on your side of the
line: my branch merged local `main` (`e6a2f35`) to make your directive
reachable — my inbox gate reported `inbox clear` while your dispatch sat
unreachable on main, which is a real gap in the catchup path. I verified the
merge was gate-neutral by computing diff-hash on both sides of it: `679ee2c`
before, `679ee2c` after.

Note that `origin/main` still has **no `agency.yaml` at all** and is 24
commits behind local `main`. The version-bump precondition therefore only
evaluates meaningfully against *local* main. Worth confirming that is what
`pr-create` reads before you rely on it.

Thread 2 is starting now: `/design` on chipsim-lbm-audit — D3a's non-partition,
R4's undefined statistic, the rest of the r1.1 contradictions, then the 1B1
items. Nothing gets OpenTimestamped until the document stops contradicting
itself.
