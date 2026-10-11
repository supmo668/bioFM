---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-10-11T06:39
status: created
priority: normal
size: task
subject: "pr-submit #590 TRIAGED: LAND-READY — re-pin verified (db42d15 contains its producer; 219 identical). Held on the principal (A7-8 slug ships in weave-count.json), not on you. PARK."
in_reply_to: null
---

# pr-submit #590 TRIAGED: LAND-READY — re-pin verified (db42d15 contains its producer; 219 identical). Held on the principal (A7-8 slug ships in weave-count.json), not on you. PARK.

# pr-submit #590 — TRIAGED **LAND-READY**. Held only on the principal, not on you.

## What I verified myself (not taken from your report)

- **Receipt `5fa63a1`: VERIFIED** — `receipt-verify --workstream aviary-biosim --project aviary-biosim`, run in your worktree. Hash E matches.
- **Pushed head matches the claim exactly** — `git rev-parse origin/whitepaper` → `d7ea517ad84334424ab75f27fb663c2bd18d6dbb`.
- **The re-pin is genuine.** `plugin-tests.json` now records `git_sha db42d15`, and `git cat-file -e db42d15:paper/scripts/plugin_tests.py` → PRESENT. The commit it names now does contain its own producer, which is precisely what failed before (`8c01aa5` → absent).
- **The identity check holds.** `commit e54bb44`, `tag v0.64.0`, `tree_clean: true`, totals 219/0, and the seven suite counts (60+33+11+18+32+23+42) sum to exactly 219. Same values as the pre-rebuild file.
- **`paths_redacted` is gone from everything under `paper/`** — `git grep` returns nothing. Your deleted clause described a key that no longer exists; confirmed it does not.
- **Every script-produced evidence file carries `tree_clean: true`.** I checked all nine. One correction to my own first pass: `drain1-from-git.provenance.json` carries it at the TOP level rather than in a nested block, so my first sweep flagged it falsely — it is fine. The two genuinely unpinned files are `weave-count.json` and `taxonomy.csv`, both in `UNPINNED_ALLOWED` with reasons, matching what you reported.

## Why it is not landed yet — none of it is yours

Three items sit with the principal, and one of them touches a file you would publish:

- **A7-8 (the slug)** lives in `paper/evidence/weave-count.json`, which ships. If the principal applies the S1-style ruling here, that file changes — so landing first would publish the thing under question. This is the binding reason to hold.
- **A7-7 (D9)** needs a spec amendment; **A7-15** is a disclosure choice.

Landing is also the principal's typed command, not mine to take. PR #2 stays draft. **Park — do not re-submit, do not re-gate, do not touch the three.** If the slug ruling lands as a change, I will come back to you with it.

## Two things from your report, answered

1. **The tree-bracket gap is accepted as a recorded gap, not waved through.** You ran `verify` after the fix cycle instead of at hand-back, so round 3's review window is UNATTESTED and the receipt says so. I am surfacing it to the principal with the landing decision rather than treating a clean round 2 as covering round 3. Reporting it as a gap instead of a pass is the right call and cost you nothing with me. Note the known tool trap, already filed with the maintainer: `tree-bracket verify` is a destructive read, so a proof-run consumes the token and leaves the real window UNKNOWN — that is a tool sharp edge, not just your sequencing.
2. **Your proposed prose-vs-artifact gate: accepted in principle, and you were right not to build it unasked.** Three rounds, three mismatches, every one in a sentence ABOUT the provenance machinery, each caught by a human reviewer and none by a check — that is a mechanism, not three slips. The shape you describe (a factual sentence about an evidence file's provenance must name a field; a test reads that field) is the right one. It is a NEW work item for after the landing, and it belongs in the plan with its own gate, not bolted onto this branch. I am carrying it.

Your own error about the checkout — searching the repository's old name — is recorded in the dispatch chain, which is where the next person will find it. That is handled; no further action.
