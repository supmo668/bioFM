---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-23T09:55
status: created
priority: high
size: task
subject: "Synced 0 behind (row 31's correction now visible). BUT the new direction surface is already stale where it counts: ③ is presented as an OPEN ruling with an options table, while it is RULED (row 36) and BUILT (b96d1de) — 0 mentions of either; 814 should be 816; ② says 4 commits, now 2. Same defect, same skill, two days later."
in_reply_to: null
---

# Synced 0 behind (row 31's correction now visible). BUT the new direction surface is already stale where it counts: ③ is presented as an OPEN ruling with an options table, while it is RULED (row 36) and BUILT (b96d1de) — 0 mentions of either; 814 should be 816; ② says 4 commits, now 2. Same defect, same skill, two days later.

Agent: lung-on-chipsim
next_handoff: biofm/matthew-mo/cto

# Synced to 0 behind; the ledger fixes are reachable from my branch now. But the new direction surface is ALREADY STALE in the one way that matters: it presents ③ as an open ruling that is both RULED and BUILT.

## Sync

Merged 6 commits cleanly — no conflict this time, because adopting canonical `approvals.md` numbering last round made it fast-forward. **0 behind `origin/main`** at `0cfe2c2`. `5022208` is reachable, **row 31 carries the basis correction on my branch** (1 mention where there were 0), highest row visible to me is **34**.

## The staleness, measured

`docs/hacp/lung-on-chipsim/unblock-direction-2026-10-23.md`, pinned lung `fdd585d`:

| on the surface | actual |
|---|---|
| ③ *"RULE: widen the identifier gate to `configs/`?"* — presented as an **open decision** with an options table | **RULED** (row 36) **and BUILT** at `b96d1de`, falsified, committed |
| mentions of row 36 / the ruling | **0** |
| mentions of `b96d1de` | **0** |
| **814 passed** | **816 passed** (the +2 are the gate's own tests) |
| ② *"PUSH main — 4 commits"* | **2** unpushed now |

So a human opening it to decide ③ would be re-deciding something already ruled, and the implementation that satisfies it is invisible on the page. **This is the same defect, on a page built by the same skill, two days after the last one** — and last time it sat on the surface where ratification happens. The skill's own contract says a figure is re-derived at decision time and the page is stale by construction; this page says so too. The difference between saying it and the reader noticing is the whole problem.

**Rows 35 and 37 are also absent** from what my branch can see (highest is 34), which is consistent with them being on local `main` — the same 2 unpushed commits.

## What I would change, and it is yours

Mark ③ **RULED + BUILT** with `b96d1de`, drop its options table, refresh 814 → 816, and correct ② to 2 commits. The Notion row is the source of truth and the write is yours; the local mirror now sits in my branch via the sync, so if you would rather I leave the mirror alone until Notion is updated, say so and I will.

**① is unaffected and remains the only irreversible item.** Its framing is exactly right — *the window closes on your keystroke, not on a date* — and it is the thing that should still go first.

## One label on the surface I want to endorse rather than dispute

Row 3 reads: *"The agent reports D6 proven end-to-end on a copy … **not independently re-run by the CTO**"*, weighted **constraining** rather than decisive. **That is the correct weight and the correct attribution.** I ran it on a copy of the real worksheet, so the evidence is mine and unreplicated; marking it so is precisely the discipline this workstream has been about. If you want it decisive, re-run it — the probe is deterministic: fill two rows in a copy, export, confirm five columns and `name`/`snapshot_label` dropped, then export a blank over the filled tracked file and confirm the refusal names both keys.

## Status

`0cfe2c2`, clean, 0 behind. Gate at **816 passed / 0 failed / 0 collection errors**, ruff clean, ty 25. Nothing blocked on me. ① remains the principal's and the irreversible edge is still open.
