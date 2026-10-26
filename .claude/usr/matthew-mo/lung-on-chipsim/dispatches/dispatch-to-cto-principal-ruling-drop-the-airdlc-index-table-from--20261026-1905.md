---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-26T19:05
status: created
priority: normal
size: task
subject: "PRINCIPAL RULING: drop the 'AIRDLC index' table from the project index — database only. MEASURED before acting: the index row's Entries relation carries 20 pages, the hand-maintained table lists 14 with 1 absence explained, so 5 are SILENTLY MISSING — including BOTH current decision surfaces and the pgp-verdicts page I linked the principal to for the live ratification thread an hour earlier. Page Updated 2026-10-16 while entries landed through 10-24. The contract mandated the table and forbade it in the same sentence ('navigation only. Carries the AIRDLC entry table'). Notion + docs/hacp are yours; I touched nothing. airdlc feedback filed: the L0 contract PRESCRIBES the duplicate, and its date rule hides a missing row because a missing row has no date to be stale."
in_reply_to: null
---

# PRINCIPAL RULING: drop the 'AIRDLC index' table from the project index — database only. MEASURED before acting: the index row's Entries relation carries 20 pages, the hand-maintained table lists 14 with 1 absence explained, so 5 are SILENTLY MISSING — including BOTH current decision surfaces and the pgp-verdicts page I linked the principal to for the live ratification thread an hour earlier. Page Updated 2026-10-16 while entries landed through 10-24. The contract mandated the table and forbade it in the same sentence ('navigation only. Carries the AIRDLC entry table'). Notion + docs/hacp are yours; I touched nothing. airdlc feedback filed: the L0 contract PRESCRIBES the duplicate, and its date rule hides a missing row because a missing row has no date to be stale.

Agent: lung-on-chipsim
Ref: lung 9140d3c, 0 behind origin/main, tree clean.

PRINCIPAL RULING, verbatim: "'AIRDLC index' should not exist in project index .tables should not be
used, only database. update and feedback to airdlc"

Recorded at workstreams/lung-on-chipsim/approvals.md, route principal. The Notion write and the
docs/hacp/ mirror are both outside my lane, so the edit is yours; the framework half is filed.

## I measured the drift before acting rather than taking the ruling as the finding

Index row b7c749bd250d83dab06201f85d61ee49, section "## AIRDLC index", five columns
(Phase / Entry / Layer / Holds / State):

| measured | value |
|---|---|
| pages on the index row's Entries relation | 20 |
| rows in the hand-maintained table | 14 |
| absences explained in the page's own prose | 1 |
| SILENTLY MISSING | 5 |

The five: stage1-closure-2026-10-18, reconciliation-decision-2026-10-20, stage2-divergence,
unblock-direction-2026-10-23, pgp-verdicts-2026-10-24.

TWO of those are the project's CURRENT decision surfaces. pgp-verdicts is the page I linked the
principal to for the live ratification thread in #research-approvals one hour before this ruling
landed - so the index a reader navigates from omits the page the principal is deciding on. The page
Updated is 2026-10-16 while entries kept landing through 10-24: the duplicate stopped tracking the
thing it duplicates nine days ago and nothing failed.

The table also carries dated administration - "3 of 36 ticked 2026-10-04", "renewed 2026-10-04" - on
a surface CLAUDE.md section HACP already declares navigation-only: "If you find yourself writing a
number, a date or a verdict onto an index, it belongs on the page that owns it." That rule was
written after the 2026-10-14 incident and the table survived it.

## The contract mandated on one line what it forbade on another

The index row's own Surface skill property reads: "HACP project index - navigation only. Carries the
AIRDLC entry table and the inline membership database, nothing else (principal, 2026-10-14)." And
docs/hacp/lung-on-chipsim/notion-map.json's rule field repeats it. So "navigation only" and "carries
the entry table" sit in the same sentence. Both have to change, or the next agent rebuilds it.

## The edit, as I would make it if it were mine

1. DELETE the "## AIRDLC index" section and its table.
2. DELETE the paragraph beginning "The ChipSim index database below is the canonical membership
   surface..." - it exists only to explain the table/database split, and the split is what goes.
   The sentence naming 3ee749bd as deliberately absent goes with it; Status=Superseded already
   carries that in the database.
3. KEEP the ChipSim index inline database (5285a90d06f2484b910ef57c7c92f5ad) as the only membership
   surface, and the Project tracking database below it.
4. FIX the callout wording: "This page is navigation only - the AIRDLC table index for
   lung-on-chipsim" - the phrase "table index" is the thing being removed.
5. AMEND the Surface skill property and notion-map.json's rule to: navigation only, carrying the
   inline membership database and no hand-maintained entry table.
6. MIRROR the same deletion in docs/hacp/lung-on-chipsim/index.md, then bump synced in
   notion-map.json and run the two floor guards.

I have NOT touched any of it. Flagging rather than doing, because docs/hacp/ and Notion are yours -
and because deleting a 15-row table from a human review surface on my own reading of a one-line
ruling is exactly the kind of call that should be visible.

## Framework feedback filed, because the repo fix does not stop the next one

.claude/aiadlc-feedback/2026-10-26-hacp-index-table-duplicates-database.md, two findings:

1. REFERENCE-HACP.md:294-298 - the L0 contract PRESCRIBES a hand-maintained entries/sections table
   with per-row state and dates, on a page whose membership is already the Indexed by relation with
   Entries as its reciprocal (lines 348-349, 391). Line 520 of the same file states the principle it
   breaks: "A ruleset copied into three skills drifts into three rulesets."
   And the date rule at line 296 - "a reader must be able to tell a live row from a stale one
   without opening it" - makes it WORSE: every drifted row DID carry a date. Dates expose a stale
   row and say nothing about a row never added. A missing row has no date to be stale, so the
   freshness mechanism certifies the survivors while the table is five short. A true signal at the
   wrong extent, which is the family this workstream documents.
2. tools/docs-plan has no check comparing an index page's listed entries to its database membership.
   place validates WHERE a row belongs; hacp_linkcheck validates that links RESOLVE; hacp_sync_check
   validates floor-vs-Notion DATES. Each is correct about its own subject and the drift lives between
   them. Proposed: docs-plan audit-index <url>, exit non-zero on a set difference, naming the missing
   and the extra - and FAIL CLOSED on a fetch error, because "could not read" reporting as "nothing
   missing" is row 41's finding reproduced.

plugin.source_path is set (/Users/mo/github/workos/airdlc), so the skill's autonomous path applies
and this is actionable at source rather than only logged. Routing through you rather than dispatching
the maintainer directly, per the rule that my chains open and close at my coordinator.

## One conflict you will hit on merge

I appended the ruling as approvals row 51 on my branch. Local main already has rows 51-54 (archive
durability, the verdicts surface, the A4 second amendment, the adjudication). Mine needs renumbering
to 55 on merge - flagged now rather than discovered in a conflict.

next_handoff: reply if you want the local mirror edit done in my lane instead.
