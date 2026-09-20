---
type: plugin-feedback
target: aiadlc plugin — skills (/research, /grill-me)
plugin_version: 0.59.0
reporter: bioFM/matthew-mo/cto
date: 2026-09-19
scope: plugin / operating-system behavior — NOT repo/app work
requested_by: principal
---

# 🟠 Request: `/expert` — a domain-calibrated research pass

**Requested by the principal.** Shape: `/grill-me`'s interaction discipline plus `/research`'s
externalised investigation, run at domain-expert calibration so a blocked decision is carried as far
as evidence can take it.

## The gap, with evidence from an actual run

`/research` fans out generic `researcher` subagents with no domain calibration — no field
vocabulary, no source hierarchy, no prior on what counts as strong evidence in the field being
searched. I ran ~30 literature searches this session assembling evidence for a compound roster, and
running generalist cost measurably:

- **Two searches returned 528,282 and 1,404,935 records** from an operator-precedence error in my own
  query (`X AND pk AND lung OR airway OR …` binds as `(X AND pk AND lung) OR airway OR …`). Both
  produced plausible-looking record IDs unrelated to the drug. Caught only because the counts were
  absurd — a subtler version would have passed.
- **A formulary newsletter ranked first for three different compounds** and carries no DOI at all. A
  calibrated pass would hold a prior against that source class; I had to open and reject it manually.
- **One record ranked top for four compounds** and then failed to resolve. Same story.
- Source selection leaned on a regulatory classification code as a relevance proxy. Defensible, and
  visibly crude — it admitted at least two coding artifacts that a domain reader spots instantly.

Net: 26 of 39 candidates ended with a resolvable citation, 9 of those resting on measured evidence.
A calibrated pass should beat that on both counts and waste fewer cycles on rejects.

## What `/expert` should carry

1. **A domain profile** — field vocabulary and synonyms, the source hierarchy (primary measurement >
   trial > review > formulary listing), known-low-value sources, and what "strong evidence" means
   here. Supplied per invocation or per workstream, not hard-coded.
2. **Query discipline** — the precedence bug above is mechanical and catchable. Any result count
   wildly disproportionate to the question should halt rather than return a top hit.
3. **`/grill-me`'s loop, inverted outward** — one question at a time, each with a recommended answer
   *and its citation*, resolving externally rather than from the operator's memory. This is the
   `grill-with-res` shape already written up in the feedback filed alongside this one; `/expert` is
   that skill with the calibration layer added.

## One scoping decision the plugin author has to make explicitly

"Unblock autonomously" has two readings and they are not close:

- **(a) autonomously exhaust everything resolvable** — drive the evidence to completion so the human's
  residual decision is small and fully cited. Safe, high value, and what the run above was reaching
  for.
- **(b) autonomously make the reserved claim** — write the artifact a task marked human-owned exists
  to reserve.

If `/expert` can do (b) by default, the human-owned task category stops meaning anything, and any
downstream record attributes a claim to someone who did not make it. Worth deciding on purpose
rather than arriving at by accident.

**Suggested shape that gets most of (b)'s value safely:** `/expert` may produce a *recommended*
selection, clearly marked unratified, which cannot be written into the human-owned artifact without
an explicit ratification step that records who ratified it and when. The human's work drops from
authoring to reviewing; the record stays true about who decided.

**Status:** open — requested, not yet designed.

## Routing note

`plugin.source_path` resolves to an editable checkout, so this is actionable rather than merely
logged. But no maintainer agent address exists in this repo's dispatch DB, the plugin source repo has
no `agency.yaml`, and no collaboration repos are configured — so there is no sanctioned route from
here to an aiadlc agent. Logged rather than dispatched to an address that does not exist.
