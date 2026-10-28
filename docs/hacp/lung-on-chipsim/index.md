# ChipSim (bioFM) — Index

<!-- HACP L1 subproject index · Kind = Index · Indexed by "bioFM — Index".
     SOURCE OF TRUTH: the Notion row https://app.notion.com/p/b7c749bd250d83dab06201f85d61ee49
     (principal, 2026-10-03: Notion HACP is the SoT for human review and communication). This file
     mirrors it; notion-map.json records each page's URL and last sync.

     BEFORE EDITING THIS FILE OR ITS NOTION ROW, READ THE GOVERNANCE CONTRACT:
     https://app.notion.com/p/313fda9448094029904f344523d5bd01 — and ../../../CLAUDE.md §HACP.
     An index carries ENTRY POINTS ONLY. It is navigation, not administration: no status tables,
     no timelines, no decision history, no prose summaries of what a child page says. Content
     displaced from this page on 2026-10-14 lives in status-and-history.md. -->

> **This page is navigation only — the AIRDLC index for `lung-on-chipsim`.**
> Every number, date, decision and open ask lives one click away, in the page that owns it.
> Start at [Status, timeline & decision history](status-and-history.md) for where things stand,
> or at [`§decision`](decision.md) for what is owed and by whom.

```mermaid
flowchart LR
  classDef phase fill:#e0e7ff,stroke:#4338ca,color:#1e1b4b
  classDef l1 fill:#fef9c3,stroke:#b45309,color:#78350f
  classDef l2 fill:#dcfce7,stroke:#16a34a,color:#14532d
  IDX(["ChipSim — Index<br><i>this page · L1 · navigation</i>"]):::phase
  V["vision"]:::phase
  D["design"]:::phase
  B["build"]:::phase
  E["eval"]:::phase
  R["risk"]:::phase
  DEC["decision"]:::phase
  REL["release"]:::phase
  IDX --> V & D & B & E & R & DEC & REL
  V --> V1["Vision 2026-10-14 · L1<br>Status & history · L1<br>§vision · L2"]:::l1
  D --> D1["Methodology 2026-10-14 · L1<br>§design · L2"]:::l1
  B --> B1["Stage 2 checklist · L1<br>Product cut · L1<br>§build · L2<br>§experiment · L2"]:::l2
  E --> E1["Paper walkthrough · L1<br>§eval · L2"]:::l2
  R --> R1["§risk · L2"]:::l2
  DEC --> DEC1["§decision · L2<br><i>the unblock ledger</i>"]:::l1
  REL --> REL1["Publication & sandbox · L1"]:::l1
```

## Membership

**The ChipSim index database on the Notion row is the ONLY membership surface** (principal ruling
2026-10-26, relayed: *"'AIRDLC index' should not exist in project index. tables should not be used,
only database"*). It carries each row's Kind, Section, Granularity, owner and review cadence, and it
is what a reviewer filters. Superseded rows stay in it with `Status = Superseded`, which is how an
absence is expressed — there is no hand-maintained list to keep in step with it.

**A hand-maintained entry table used to sit here and was deleted 2026-10-26**, because it had
silently stopped tracking the thing it duplicated. **Re-verified complete 2026-10-27** by
re-reading the Notion row with an instrument first confirmed to render table blocks; the CTO's
own record had carried the deletion as an outstanding manual action for a day, and that claim is
withdrawn (approvals row 63). Measured before deleting: the index row's
`Entries` relation carried **20** pages, the table listed **14**, one further absence was explained
in prose, so **five were missing without any signal** — including both current decision surfaces and
the page the principal was mid-ratification on. The page's `Updated` was nine days behind the
entries. **A missing row has no date to be stale**, so the table's own freshness convention certified
the survivors and said nothing about the gap.

Floor-to-Notion URLs and sync dates: [`notion-map.json`](notion-map.json).
