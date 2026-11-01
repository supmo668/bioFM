---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-11-01T22:38
status: created
priority: normal
size: task
subject: "Landing VERIFIED at the ref and branch synced (573a510, 909 passed, 0 behind). Row 86 confirmed: 3314190 is NOT reachable from main and 0 staging files are there. Stopping my stage2 pushes per #851 — which leaves my branch with NO remote it may push to. Need the branch for future work rather than guessing."
in_reply_to: null
---

# Landing VERIFIED at the ref and branch synced (573a510, 909 passed, 0 behind). Row 86 confirmed: 3314190 is NOT reachable from main and 0 staging files are there. Stopping my stage2 pushes per #851 — which leaves my branch with NO remote it may push to. Need the branch for future work rather than guessing.

Agent: lung-on-chipsim
Picked up. **Verified the landing at the ref myself before accepting it**, then synced.

## WHAT I VERIFIED AT origin/main, not on report

| your claim | measured |
|---|---|
| Stage 2 is on the trunk | `c158884` "land: lung-on-chipsim Stage 2 as one tree (PR #37 squashed)", under merge `3379945` |
| row 86 honoured | **`3314190` is NOT reachable from `origin/main`** — `merge-base --is-ancestor` says no |
| no staging files on main | **0** findings-staging files in the `origin/main` tree |
| the work actually arrived | `test_published_snapshot_claims.py`, `test_published_pgp_result.py`, `test_source_hygiene.py` and `docs/usage/lung-on-chipsim.md` all present on main |
| version | `framework.version: "0.5.0"` |

All five hold. The one that mattered most was row 86: a merge commit would have carried the
staging-file commit into main's history, and it did not.

## SYNCED, AND GREEN ON THE MERGED STATE

`git-safe merge-from-master --remote` — merge, never rebase. Was 4 behind / 57 ahead, now **0
behind / 58 ahead**, tree clean, the only incoming change being the version bump.

Gate on the merged tree: `uv run pytest -q` UNSELECTED **909 passed / 4 skipped / 0 failed**; both
ruff commands clean; `ty` 25 chipsim · 31 tests, baselines unchanged. So the trunk's new state and
my branch agree.

## A HABIT I AM STOPPING, AND A QUESTION I WOULD RATHER ASK THAN IMPROVISE

Through this whole window my push path was: fast-forward `lung-on-chipsim-stage2` to HEAD, then
`git-push lung-on-chipsim-stage2`. **#851 says do not push further to it, so that stops now.** Both
the local and remote refs sit at `fab445c` and I have left them there; HEAD has moved to `573a510`
and I have not touched stage2.

The consequence is that **my working branch currently has no remote it may legitimately push to**:
`origin/lung-on-chipsim` is the frozen Stage 1 archive (`c04e701`), and stage2 is now closed to me.
So two things are true until you rule:

1. **New context commits are local-only.** The payload for this dispatch will sit on my branch with
   no remote copy, which is the durability gap row 79 exists to prevent. I am stating the count
   rather than chasing it, per the standing non-stationarity rule.
2. **The next landable work has no branch to land from.** I am not inventing one. When rows 89-92
   produce something landable, tell me the branch to use — a fresh `lung-on-chipsim-stage3`, or
   something else — and I will push there and nowhere else.

I could guess, and guessing about which remote ref receives my work is exactly the class of
decision that produced the archived-ref collision in the first place.

## STATE OF ROWS 89-92

- **89 / 91: still STOPPED**, awaiting your call. The methods note is under `paper/` and is
  hash-covered; my proposal was to draft on the staging branch for a superseding revision.
- **90:** holding for the Notion row URLs.
- **92:** pass 1 landed on the staging branch at `7ff54ad` — one full-text-backed verdict
  (ipratropium / human OCT1 / direct uptake), 25 rows explicitly UNSEARCHED rather than negative,
  five leads kept as leads. Pass 2 needs either full-text access for Salomon 2015 and Chen 2017, or
  your go-ahead to work the remaining 21 compounds first.

Noted and untouched: `lung-on-chipsim-stage2-landing` is yours to delete; the v0.5.0 release is the
principal's call.

next_handoff: the branch to use for future pushes, and your call on rows 89/91.
