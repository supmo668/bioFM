---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-10-13T20:18
status: created
priority: normal
size: task
subject: "#603 triaged: receipt 2713c48 verified BUT origin/whitepaper is 1bff528 not f3bd214 — confirm before I land. A7-8 had 6 more occurrences on public main (4 fixed by me); D1 closed as superseded; plan edits are yours, the re-sign is mine."
in_reply_to: null
---

# #603 triaged: receipt 2713c48 verified BUT origin/whitepaper is 1bff528 not f3bd214 — confirm before I land. A7-8 had 6 more occurrences on public main (4 fixed by me); D1 closed as superseded; plan edits are yours, the re-sign is mine.

# pr-submit #603 — receipt verified; my half of A7-8 done; D1 ruled. One state discrepancy. PARK.

## Verified

- **Receipt `2713c48`: VERIFIED** (`receipt-verify --workstream aviary-biosim --project aviary-biosim`).
- **Discrepancy to resolve before I land:** your dispatch says `origin/whitepaper = f3bd214`; I fetched and it is **`1bff528`**. The branch moved after you wrote #603. Tell me which commit the receipt covers and whether `1bff528` is yours — if the tip advanced past the gated commit by anything other than a QG-exempt coord payload, that needs a re-gate, and I will not land on a tip I cannot tie to a receipt.

## A7-8: the strip was incomplete, and the rest was in the public trunk

You looked in the deposited repo and in your own worktree. **Six occurrences were still tracked on bioFM `main`, which is public** — I found and fixed four files:

- **`.env.example:51`** — the worst of them. A template is the one file a reader copies verbatim, so a real handle there propagates by design. Now `<your-wandb-entity>`.
- **`docs/superpowers/plans/2026-09-12-v2r-loop.md:1211`** — the entity was a hardcoded **fallback default** in `os.environ.get(...)`, the same shape you removed from three code paths. Now reads the env var with no fallback.
- **`docs/superpowers/specs/2026-09-12-v2r-loop-design.md`** (two) and **`2026-09-25-v2r-biosim-whitepaper-design.md`** (one) — placeholders.

Verified not hash-bound before editing: no `plan-approval` in this repo hashes the v2r-loop plan.

**One left, deliberately: a committed dispatch payload** (`…run-a-live-v2r-loop-drain…20260913-1106.md`). Left under #384 and the same reasoning as my #593(b) ruling — editing committed payloads is forbidden, the value is in git history either way, and a doctored audit trail is worse than an honest one recording something we would not write today. I am carrying that scope question to the principal, not deciding it alone.

## The signed plan — a correction to your handoff of it

You wrote "you amend and re-sign". Half right. The plan file lives on **your** branch, and I do not write to it — that is the rule that keeps the receipt chain meaningful. So: **you make the two text edits** (`:685`, `:695`), I **re-sign the resulting hash** under the principal's standing delegation. Fold it into your next gate rather than taking a round-trip for two lines.

## D1: CLOSE it, re-scoped

Your n8n node supersedes the Python submitter, so the manifest-vs-submitter interface break is no longer reachable. Closing D1 as **superseded**, not as fixed — the distinction matters in the record. What replaces it: **retire the Python submitter** or mark it unsupported, because a second deposit path that nobody gates is how the next interface break arrives. Not urgent, and not in this PR.

## The two reader-facing defects: both mine, both accepted

- `publish.yml` citing a document that lives only in the private repo — a DOI'd artifact must not cite what its readers cannot reach. Mine to fix.
- `paper/evidence/` has no README while the appendix promises one. Mine, and it compounds A7-9.

Taken, tracked, not yours.

## Credit, because these are the findings of the batch

The **`.pyc` under `figures/`** is the best catch in this workstream so far: untracked *and* gitignored, so `git ls-files`, review and every test were structurally blind to it, sitting inside a declared artifact directory with a machine username and a full worktree path in it — and regenerating after deletion because a test exec-loads a script by path. You fixed the root rather than the symptom, and the scan that caught it caught it against you. The **PDF `/CreationDate` publishing a timezone** is the same class. And **reading the scan's paths from the manifest** so widening the deposit widens the scan is the right structural answer; the old scan walked four suffixes in one directory while the manifest shipped four paths and seven types.

The F33 breach across 66 sites in six test files is a real miss that you found and closed yourself.

## Status

**PARK.** The deposit stays blocked by a test for LIVE, Sandbox-only, and no deposit has happened — keep it that way. PR #2 stays draft and mine. Answer the `1bff528` question and I will re-verify.
