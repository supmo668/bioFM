---
type: plugin-feedback
target: aiadlc plugin (bioFM) — dispatch identity / coordinator concurrency
plugin_version: 0.56.0
reporter: bioFM/matthew-mo/cto
date: 2026-09-24
scope: plugin / operating-system behavior — NOT repo/app work
---

# 🔴 Two CTO sessions share one dispatch identity, and issued opposite rulings to the same agent three minutes apart

**Self-caused in the sense that one of the two sessions is me.** Caught by the
`coord-commit-check` Stop hook, not by any dispatch surface.

## What happened

| time | dispatch | ruling |
|---|---|---|
| 2026-09-24T19:11 | to `perturb-seq-eval`, from `biofm/matthew-mo/cto` | "HOLD LIFTED on #203 — **principal chose (a)**: consolidate Python, n8n orchestrates. #203 stands as written." |
| 2026-09-24T19:14 | #229, to `perturb-seq-eval`, from `biofm/matthew-mo/cto` | "SUPERSEDES #203 — **principal ruled (b)**. Consolidation **CANCELLED**." |

Mutually exclusive: under (a) the agent builds a consolidated Python CLI; under (b) that
CLI is deleted. Both carry the same `from` address, the same authority, and no marker
distinguishing their origin. The recipient cannot tell which is current — and "later
timestamp wins" is not sound, because neither session knows the other exists.

In this session I put the fork to the principal explicitly and the literal reply was `b`.
I cannot see what the other session asked or was told, so I have not declared my own
ruling authoritative.

## How it surfaced — which is the real finding

**No dispatch surface reported it.** `dispatch create` succeeded twice. The recipient's
inbox shows two unread directives from one sender. What caught it was the
**`coord-commit-check` Stop hook**, complaining about an *uncommitted file* — because the
other session's dispatch was sitting untracked in the shared directory. I noticed the
contradiction only because the filename contained `principal-chose-a` and I read it before
committing.

So the mechanism that surfaced a contradictory ruling was a **hygiene check about git
cleanliness**, entirely by accident. Had that session committed its own dispatch, the hook
would have stayed silent and I would have had no signal at all.

## Root cause

Dispatch identity is `<repo>/<principal>/<agent>` with **no session discriminator**. The
single-trunk-writer invariant constrains who may *land*, and says nothing about who may
*rule*. Two sessions of the same coordinator therefore have equal, indistinguishable
authority over the same recipients, and a shared `dispatches/` directory with no locking.

This is the same family as `2026-09-20-agent-wake-spawns-a-second-writer-into-a-worktree-already-confirmed-alive.md`
— two processes under one identity, no mutual awareness — and of the tracked
`monitor-pids.json` defect. **A third mechanism producing the same class of harm:** there,
two writers to one branch; here, two rulers over one agent.

## Suggested fixes, in order

1. **Stamp a session discriminator into every dispatch** (pid, session id, or boot time) as
   a frontmatter field, and **print it on `dispatch read`.** The recipient then sees that
   two directives came from different sessions and can refuse to act instead of guessing.
2. **Have `dispatch create` warn when an unresolved dispatch to the same recipient already
   exists from the same address within N minutes**, especially one it did not itself write.
   Cheap, and it would have caught this at 19:14.
3. **Refuse, or loudly warn, when a coordinator address already has a live session** —
   `lsof -d cwd` on the coordinator's checkout is the same check already recommended for
   `agent-wake`. A second coordinator session is a legitimate thing to want; being unaware
   of the first is not.
4. **Do not rely on timestamp ordering for supersession.** `in_reply_to` exists; a ruling
   that supersedes another should name the dispatch id it voids, and a dispatch naming no
   predecessor should not be assumed to be the latest word.

## Containment

- Sent #230 telling the agent to act on **neither**, and that `#202` (unrelated) remains
  its priority, so it is not idle.
- Committed the other session's dispatch **unchanged** — it is a real artifact and the
  record has to stay honest — with the conflict documented in the commit message.
- Escalated the disambiguation to the principal rather than declaring my own ruling the
  winner, which would have converted a visible conflict into a silent one.
- The (b) work already built is **inactive**, holds no credentials, and has published
  nothing, so no harm reached a venue.

## Status

open.
