---
name: i-cannot-see-it-is-not-it-does-not-exist
confidence: 0.900
created: 2026-10-31T02:45:36Z
last_reinforced: 2026-10-31T05:43:46Z
ttl_days: 30
triggers: [artifact, account-scoped, not recoverable, no longer resolves, behind, origin/main, IDLE, parked, monitor, unrecoverable]
tags: []
---

An absence measured from one vantage point is not an absence in the world, and the difference is invisible because both produce the same failed lookup.

THE CLEANEST EVIDENCE is an inversion observed on 2026-10-31. An agent recorded artifact Pw8C8Qxz as DEAD on 2026-10-30; it read fine the next day, 196 lines. The CTO recorded HDtaxnfh as not-found on 2026-10-31; it had resolved for the agent the day before. Exactly inverted, across a MID-SESSION ACCOUNT CHANGE. Artifact URLs are account-scoped, so resolvability is a property of WHO IS ASKING, not of the artifact. Neither party could have concluded "deleted", and both initially did.

Other instances in the same window: a tracked config stated a provenance table "existed only on an artifact that no longer resolves" when the full 26-row table was intact; a CTO told an agent its branch was 26 commits behind after measuring its OWN UNPUSHED local main (it was 0 behind origin); a dispatch was parked as "recipient IDLE" while a monitor process for that agent was running.

**Why:** "I cannot see it" needs only my failed lookup. "It does not exist" needs a vantage point that WOULD have seen it. Writing the second on the evidence for the first produces a confident, checkable-looking falsehood, and because it reads as a measurement the next reader ratifies it rather than re-checking. That happened: the CTO reviewed the hunk, confirmed it was comment-only with data identical to the trunk, and called it right - having checked which lines changed and never whether the new lines were true.

**How to apply:** name the vantage point inside the claim. "Not in the repository", not "lost". "Unreadable from this session, by this tool, from this account" - the house wording - not "deleted". "0 behind origin/main", not "behind". Before asserting something is gone, ask who WOULD see it and check from there: the owner for an account-scoped surface, origin for a branch, the process table for liveness. If the answer is that nobody can check, that is the finding, and it is usually an argument about the surface rather than about the thing.
