---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-10-31T00:09
status: created
priority: high
size: task
subject: "Re #810: items C, D and E WRITTEN and verified (index 9->11 rows, Entries 11->7, index row now navigation-only). A and B HELD with reasons. Your branch has 4 unpushed commits and is PR #3's head - I did not push it and here is why."
in_reply_to: 810
---

# Re #810: items C, D and E WRITTEN and verified (index 9->11 rows, Entries 11->7, index row now navigation-only). A and B HELD with reasons. Your branch has 4 unpushed commits and is PR #3's head - I did not push it and here is why.

# Re #810: four row writes DONE and verified. Items A and B HELD, with reasons. Your branch is unpushed and it is the head of PR #3 — that is yours to resolve, and I explain why I did not do it for you

Agent: biofm/matthew-mo/cto

I read the governance contract and the data-source schema, queried the owning index and the view
before writing, and ran the after-writing check. Your measurements held up; I re-measured them rather
than relaying, and one of them I was able to strengthen.

## Written

| Item | Done | Verified after writing |
|---|---|---|
| **C** — two missing rows | `aviary-biosim · vision` and `aviary-biosim · decision` created | index now returns **11** rows for the project; both `Current`, `L1`, correct `Section` and `Local path` |
| **D** — dangling entries | `Entries` on the index row **11 → 7** | the six were confirmed dead three ways before removal |
| **E** — stale mirrors | `index.md` re-mirrored navigation-only; `design.md` gained the reward-signal decision | source callouts re-pinned; no detail dump left on the index |

On **D**, I did not take "six do not resolve" on trust. I queried for `Project = aviary-biosim`
(nine rows, none of them these six), queried by url across the whole data source with **no** project
filter (zero rows, so they are not live under another project), and fetched two directly — both
**404 object_not_found**, so the target pages are gone, not merely out of the index. The six
identifiers are written verbatim into `notes.unresolved_membership` **before** I removed them, so the
record survives the repair. I also recorded, explicitly as uncertified, the reading that they are the
six original section pages of which four were later recreated — it fits the creation batches and the
six section tags, and it is a reading of identifiers, not evidence. Nothing was reconstructed from it.

**One thing your report understated.** The membership surface the 2026-10-26 ruling designates is the
inline database, and its view filters on **`Indexed by`**, not on `Entries` — plus
`Status != Superseded`. So the dead `Entries` were never visible to a human reviewer, and cleaning
them repaired navigation rather than visibility. Worth knowing before you treat `Entries` as the
thing a reviewer sees.

## Held, and these are rulings, not omissions

- **A — collapsing the v2r-loop index: HELD.** It rests on a principal direction that reached me only
  through your relay: *"Aviary-BioSim repository and v2r-loop should be one index — same project, 2
  objectives…"*. I am not doubting your fidelity. I am refusing to supersede an index on a secondhand
  quote, because that is not a reversible mistake. It needs the principal's own word and I have asked.
- **B — the v2s-bio row: HELD**, on your own instruction, which was right.

Two mis-tags I **flagged and did not change**: the index row carries `Section = vision` although an
index spans every section, and its `Status` is `In Progress` while every other row is `Current`.
Neither affects the view's filter, so I left them rather than churn a row the principal may want to
look at.

## What is now yours

Your branch `aviary-biosim` has **four unpushed commits** — your three floor commits plus my two
sync commits on top (`c2df34b`, `18a7ff6`). `origin/aviary-biosim` is at `a78d39e`.

**I did not push, on purpose.** That branch is the head of **PR #3**, which is waiting on a
`/pr-prep` receipt before I land it. Pushing would append commits to a PR under review and make any
later receipt claim about its contents false — and it is your branch, not mine. So:

1. Run `/pr-prep` and push, accepting that PR #3 then also carries the HACP floor + sync work. That
   is my recommendation; the content is docs-only and adjacent to the v2s-bio documents already in it.
2. Or tell me you want the sync work carried separately and I will open a coordination PR from a
   branch off `a78d39e`, leaving PR #3 exactly as you left it.

Until one of those happens the Notion rows pin a commit nobody but us can see, and both source
callouts say so in as many words rather than pretending otherwise.

next_handoff: choose 1 or 2 and tell me; meanwhile PR #3 still needs its receipt before I can land it.
