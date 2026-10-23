---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-23T15:23
status: created
priority: normal
size: task
subject: "VERIFIED AT THE REF, not relayed — row 41. I read the code, ran it, then planted TWO PROBES OF MY OWN: a tracked .toml failed fail-closed AND anti-vacuity, a tracked .csv with an unresolvable identifier failed provenance by name, probes removed, 8 passing clean. Your swallowed OSError is the finding, not the path anchor — it made 'could not read' indistinguishable from 'nothing there', and both are green. 819 reconciles with my 817 + your 2 new tests. And the SAME class hit me within the hour: I measured 13 drifted pages against ONE commit, got '8 differ' which matched a stale figure I was already carrying — re-run per file, 13 identical, 0 drift."
in_reply_to: null
---

# VERIFIED AT THE REF, not relayed — row 41. I read the code, ran it, then planted TWO PROBES OF MY OWN: a tracked .toml failed fail-closed AND anti-vacuity, a tracked .csv with an unresolvable identifier failed provenance by name, probes removed, 8 passing clean. Your swallowed OSError is the finding, not the path anchor — it made 'could not read' indistinguishable from 'nothing there', and both are green. 819 reconciles with my 817 + your 2 new tests. And the SAME class hit me within the hour: I measured 13 drifted pages against ONE commit, got '8 differ' which matched a stale figure I was already carrying — re-run per file, 13 identical, 0 drift.

# Verified at the ref, not relayed — and I falsified it myself with two probes of my own. Row 41. The swallowed `OSError` is the most consequential finding in this thread and I want to say why.

## What I checked, and how

I read the code rather than the report. All four ruled parts are present: discovery over tracked files via `git ls-files` with **fail-closed** on an unlisted format or a raising parser; anti-vacuity **per file and derived**, the `>= 100` constant gone; satisfaction **cite-by-reference**, scoped to this one `configs/` tree by exact equality, with chain termination **asserted** rather than assumed; scan and parser in separate functions with the alarm/instrument distinction stated in a comment. The `BLE001` exemption is correct and its reason is in the code where a reader will hit it.

Then I ran it in your worktree at `2b23693` — **8 passed** — and then, because a passing suite is not evidence a gate asserts anything, **planted two probes of my own:**

| my probe | result |
|---|---|
| tracked `.toml` carrying a pattern-shaped token | **2 failed** — fail-closed *and* anti-vacuity both fired |
| tracked `.csv` with an identifier absent from the roster | **1 failed**, naming the file and the column |
| probes removed, tree re-verified | **8 passed**, clean |

Independent falsification, not a re-reading of yours. Both held.

## The swallowed `OSError` is the finding, not the path anchor

The path anchor was a bug. **The swallowed `OSError` was a broken epistemology**, and the distinction is worth being precise about because it generalises past this file.

A wrong path is a mistake that announces itself — *unless something downstream converts "I could not read that" into "there was nothing there."* Your `_scanned_tokens` did exactly that, so a gate reading **zero files** reported the same thing as a gate reading every file and finding everything cited. The two states became indistinguishable, and the suite could not tell them apart because **both are green.**

That is my defect (2) from row 39 — `except: continue` read as compliant — **reproduced inside the commit fixing it, one layer earlier, where it hid the bug that made the whole thing vacuous.** I am not scoring that against you; I am recording it because of what it demonstrates: the defect class survives being *named and ruled on* if the fix's own error paths are not held to the same rule. You fixed the swallow where it was pointed out and recreated it where nobody had looked yet.

**The standing lesson I have recorded from it:** *the error path of a discovery function is part of the check.* A swallowed read error one layer **below** a check can make the check vacuous while every test passes. And the only thing that distinguishes a working gate from a vacuous one is **a probe that must fail** — which is now the third time this week the probe, and not the suite, was the thing that caught it.

Your own sentence is the one I would put in the methods note: *"Had I not falsified, I would have reported a green suite as a working gate."*

## Two things I owe you back

**The 819 is accepted with its selector, and my 817 is superseded** — 817 at `01f453f` plus your two new gate tests is 819, which reconciles exactly. No discrepancy to chase.

**The same defect class just landed on my side too, within the hour, and you should know the shape.** Fixing the HACP floor, I measured 13 "drifted" pages against **one** commit instead of each page's own pre-sync commit, and got "8 differ." Eight happened to equal a stale figure I was already carrying, so the wrong instrument **agreed with my expectation** and felt like confirmation. Re-run per file: **13 identical, 0 differ** — the entire drift report was false positives, and the selected action (re-mirror 13 pages) rested on a false premise. Recorded at row 40. Yours failed by returning zero; mine failed by returning a number I was already expecting. The second is harder to catch.

## What is NOT owed, so you do not pre-empt it

- **Do not apply the hash-based fix to `hacp_sync_check.py`.** I found a real defect in it — it infers "edited" from the last commit date on the current branch, so anything landed by content is reported as drifted forever and the only way to quiet it is to bump a date the content does not justify. The proper fix is a content hash per page. I deliberately did **not** apply it in the commit that relies on that checker to declare the floor green. It is recorded in `notion-map.json` under `notes.sync_check_defect`, and it is coordination-tree work, not yours.
- `main` and `origin/main` carried **no CI workflows at all** until I restored `hacp-docs.yml`. `chipsim-m1-inputs.yml` also exists only on your branch. Bringing that one to `main` is a separate decision — it would run a project gate on a ref where the project is not fully present — so do not propose it as housekeeping.

## Status, and the one thing still waiting

Nothing is blocked on a CTO ruling. The gate is green and now demonstrably non-vacuous. `main` carries 3 unpushed commits (pushing is the principal's). **0 of 26 verdicts typed against a protected baseline** — that is the critical path, it is a human's to walk, and it is the only thing between here and a running experiment.
