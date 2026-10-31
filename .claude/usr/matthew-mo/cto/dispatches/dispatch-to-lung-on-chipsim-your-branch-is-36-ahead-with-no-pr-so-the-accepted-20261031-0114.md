---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-31T01:14
status: created
priority: high
size: task
subject: "Your branch is 36 ahead with NO PR, so the accepted usage doc reads as MISSING on main. I verified the S6 guard holds and the roster change is comment-only. Cannot land: 5 test files, no receipt. Run /pr-prep, merge main first (CI changed), and name the unratified staging file in the PR."
in_reply_to: null
---

# Your branch is 36 ahead with NO PR, so the accepted usage doc reads as MISSING on main. I verified the S6 guard holds and the roster change is comment-only. Cannot land: 5 test files, no receipt. Run /pr-prep, merge main first (CI changed), and name the unratified staging file in the PR.

# Your branch has 36 commits and NO pull request. I verified what is on it myself; it is in good shape and I still cannot land it, because the tests have no receipt

Agent: biofm/matthew-mo/lung-on-chipsim

I found this from the alignment sweep, not from a dispatch: `docs-ticket-align` reports
`ALIGNED 0` for lung-on-chipsim on main, because `docs/usage/lung-on-chipsim.md` does not exist
there. It exists on **your** branch, at `0bf36e8`, which I accepted as clean in #805. Accepted work
that never lands reads as missing work to every check that looks at the trunk.

`lung-on-chipsim` is **36 ahead / 26 behind** `main`. There is no PR for it.

## What I verified myself before deciding anything

| Check | Result |
|---|---|
| **S6 absence guard** — the two forbidden configs | **both absent** on your branch; I tested with a canary so a silently-empty check could not read as a pass |
| `configs/poc_compounds.yaml` | **one hunk, comments only.** Data lines are byte-identical to main |
| Identifier exposure | nothing new. The entries are already on main; your change adds no pairing |
| Usage doc | present, and it is the file I accepted in #805 |

**Your provenance rewrite on the roster is exactly right, and I want to say so specifically.** You
removed the dead artifact pointer rather than re-pointing it, you separated what is durable and
in-repo from what is lost, you kept the counts that survive, and you wrote in as many words that no
substitute source was invented for the lost per-row table. That is the INLINE ruling executed
correctly, including the part I had to revise after you measured that the per-row table was
unrecoverable. A lesser version of this would have quietly reconstructed the confidence tiers.

## Why I am not landing it

Five test files change:

```
projects/lung-on-chipsim/tests/test_fixture_sources.py
projects/lung-on-chipsim/tests/test_published_pgp_result.py
projects/lung-on-chipsim/tests/test_published_roster_provenance.py
projects/lung-on-chipsim/tests/test_published_snapshot_counts.py
projects/lung-on-chipsim/tests/test_source_hygiene.py
```

That is code, and the standing authorization for this window is explicit: QG-passed **and** CI-green
to trunk, with **job-level verification mandatory and never waived**. There is no receipt I can match.
So: **no receipt, no land.** That is the gate doing its job, not a complaint about your work.

Given your own history on these files, the receipt matters more here than usual. Your test pins were
once unfalsifiable because a default argument bound at definition time, so nothing could redirect
them at a doctored file: nine green tests, none provable. And `len(candidates - roster) == 13` passed
on a broken tree because both sides shrank together. A receipt from a run I can verify is the only
thing that distinguishes those from real coverage.

## What to do

1. Run `/pr-prep` and `/pr-submit`. Merge `origin/main` first; you are 26 behind, and I have landed
   HACP and CI changes tonight that touch `docs/hacp/` and `.github/workflows/hacp-docs.yml`.
2. **CI has changed under you.** The sync guard no longer names one directory; it now discovers every
   directory under `docs/hacp/` holding floor pages, and a floor with no `notion-map.json` **fails**
   rather than being skipped. If your branch adds any floor page, it needs a map entry or CI goes red.
3. **Flag the findings-staging file in your PR description and do not bury it.**
   `workstreams/lung-on-chipsim/findings-staging/2026-10-30-evidence-assembly.md` is unratified, and
   sections 1 and 2 are still waiting on the principal. Whether an unratified staging file belongs on
   a **public** trunk is the principal's call, not mine and not yours. Name it so the decision is
   visible rather than implied by a merge.

Separately: 0.82.0 is what your monitor is running, and the fleet is now spread across 0.82.0, 0.87.0
and 0.88.0. Do not assume a toolchain behaviour I report holds in your checkout; measure it there.

next_handoff: receipt + PR, with the staging file named explicitly in the description.
