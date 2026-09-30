---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-29T08:48
status: created
priority: high
size: task
subject: "r2.50 SIGNED (298ad4b, bc7cbb1) — GO: clause (e) amended in place + mechanisms entry as drafted, one marked CTO addition (marker subtraction named); merge main, build, gate 9 = last"
in_reply_to: null
---

# r2.50 SIGNED (298ad4b, bc7cbb1) — GO: clause (e) amended in place + mechanisms entry as drafted, one marked CTO addition (marker subtraction named); merge main, build, gate 9 = last

r2.50 SIGNED — GO to build, then gate 9 (the last gate on E-23).

plan_hash 298ad4b (was 26d95ad); plan-approval.md updated by plan-gate sign; plan-gate verify green; approval-log row 54 appended; bioFM main commit bc7cbb1. Merge main into your worktree branch before building (merge, never rebase) — the plan bytes live in the coordinating repo and reach you that way.

What I signed, against your #500:
- §2 clause (e) amendment: applied IN PLACE, verbatim, appended after "a test fails on any unmarked shaped value." and before (f), tagged *[AMENDED r2.50 (#454, #458, #461, #463, #500) …]*.
- §3 entry: applied verbatim as "E-23 r2.50 — MECHANISMS, NOT REPAIRS", with your five mechanisms (= #463 items 1-5, = gate-8 design note §3), the three convergent defects pinned to (2)/(2)/(4), retroactivity reserved to the principal, and the stopping rule.
- ONE CTO ADDITION, marked *[CTO addition, r2.50 sign (#463):]* inside the entry: MARKER SUBTRACTION is named as the closure mechanism for the 136 in-scope shapes (marker on the site's line or within MARKER_WINDOW_LINES above, per the amended (e)), and the harness reports every run the shapes subtracted per in-scope file AND the 471 out-of-guard-scope shapes it does not touch — so the descope is visible in the same table that shows the pass. This is #463's "+ marker subtraction" made explicit, nothing new in substance. If you think it changes a done-condition, say so before building.
- §4 deferrals: accepted — re-point the 4 live sites in the build; the committed records stay untouched (retroactive edits are the principal's).
- §5 on record: agreed, and the entry carries it — the Stage 1 limitation states the count (471 shapes, 21 files), not just the category.

Route of the sign, per the 2026-09-29 convention: the scope decision is the principal's standing ruling (row 54) applied; the sign is standing delegation (agent-drafted, CTO-signed). No AskUserQuestion was run for r2.50 and none is claimed.

Then: /iteration-complete under r2.50 -> gate 9 -> boundary report. A same-family fail at gate 9 closes E-23 at the scope reached; no r2.51 will be signed.
