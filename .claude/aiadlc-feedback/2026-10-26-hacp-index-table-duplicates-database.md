---
type: plugin-feedback
target: airdlc plugin (airdlc-plugins/airdlc)
plugin_version: 0.82.0 (cache dir); this repo's framework.version is 0.3.0 — two different numbers, named so they are not conflated
reporter: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-26
scope: plugin / operating-system behavior — NOT repo/app work
---

# HACP L0: the prescribed index table duplicates the `Indexed by`/`Entries` relation, and nothing checks the two agree

## 🔴 1. `REFERENCE-HACP.md` prescribes a hand-maintained index table over membership that is already a relation

**File:** `reference/REFERENCE-HACP.md:294–298` (the **L0** contract, items 5–7 and the rule that follows)

**Symptom.** On `bioFM`'s `lung-on-chipsim` index row
(`https://app.notion.com/p/b7c749bd250d83dab06201f85d61ee49`) the prescribed table — rendered
there as `## AIRDLC index`, five columns, *Phase / Entry / Layer / Holds / State* — had **stopped
tracking the database it duplicates nine days earlier, and nothing failed.** Measured, not
estimated:

| measured | value |
|---|---|
| pages on the index row's `Entries` relation | **20** |
| rows in the hand-maintained table | **14** |
| absences explained in the page's own prose | **1** |
| **silently missing** | **5** |

The five: `stage1-closure-2026-10-18`, `reconciliation-decision-2026-10-20`, `stage2-divergence`,
`unblock-direction-2026-10-23`, `pgp-verdicts-2026-10-24`. **The last two are the project's current
decision surfaces**, and `pgp-verdicts` is the page a principal was linked to for a live
ratification thread one hour before this was found. Page `Updated` was `2026-10-16`; entries kept
landing through `10-24`.

**Root cause** (proven from the reference text, not inferred). The L0 contract asks for a
**Sections** item — *"one line each, tagged, linking down, with its state and the date it was last
updated"* — plus a decisions table, on a page whose membership is **already** the `Indexed by`
relation with `Entries` as its reciprocal (`REFERENCE-HACP.md:348–349`, 391: *"Membership is the
`Indexed by` relation, not a visual sub-item tree"*). So the same fact is stored twice: once as a
relation the platform maintains, once as prose a human or agent must remember to edit. Line **520**
of this very file states the principle being violated — *"A ruleset copied into three skills drifts
into three rulesets."* The index table is that, with membership instead of rules.

**The date requirement makes it worse, not better.** `REFERENCE-HACP.md:296`: *"Every table on an
index page carries a date … A reader must be able to tell a live row from a stale one without
opening it."* Every row in the drifted table **did** carry a date (`· 2026-10-04`,
`renewed · 2026-10-04`). Dates distinguish a stale row from a live one; they say **nothing** about a
row that was never added. A missing row has no date to be stale, so the mechanism meant to expose
staleness certifies the remaining rows as fresh while the table is five entries short. The reader is
*more* confident and *less* correct — which is this defect family exactly: a true signal at the
wrong extent.

**Fix.** Smallest viable change, in the L0 contract:

- Replace the prescribed entries/sections **table** with the **inline database view** of the
  `Indexed by` relation, filtered and sorted for reading. Notion already renders it; it cannot
  drift from itself.
- Keep a table on an index page only for facts the database does **not** hold, and say so.
- Keep the date rule, scoped to those: *a table on an index page carries a date **when it holds
  anything the index database does not** — and membership is never one of those things.*

**Effect.** Index membership becomes underivable-by-hand and therefore undriftable. The 5-missing
case cannot occur, because there is no second copy to forget.

**Status:** open

---

## 🟠 2. No check compares an index page's listed entries to its database membership

**File:** `tools/docs-plan` (subcommands: `add done iteration list none owed place plan probe root`)

**Symptom.** A row can be created, placed and `Indexed by` an index correctly, and never appear in
that index's table. Nothing anywhere reports it. This is how defect 1 reached five.

**Root cause.** The shipped checks verify different properties: `docs-plan place` validates *where a
row belongs*, and the repo-side `hacp_linkcheck.py` / `hacp_sync_check.py` verify *links resolve* and
*floor↔Notion sync dates*. **None compares the set of entries a page lists against the set the
database says it holds.** Each check is correct about its own subject, and the drift lives between
them.

**Fix.** Add `docs-plan audit-index <index-url>`: fetch the index row's `Entries`, extract the
mentions from its body, and exit non-zero on a set difference, printing the missing and the extra
by title. Fail-closed on a fetch error — *"could not read"* must not report as *"nothing
missing"*. (That exact swallow is the finding at `approvals` row 41 in this workstream.)

**Effect.** Drift becomes a failing check instead of something a reader notices five entries late —
and it is the kind of check that cannot be satisfied vacuously, because an empty fetch fails.

**Status:** open

---

## Provenance

Found while a principal ruled *"'AIRDLC index' should not exist in project index .tables should not
be used, only database"* (recorded at `workstreams/lung-on-chipsim/approvals.md`, route `principal`).
The counts above were re-derived here against `docs/hacp/lung-on-chipsim/notion-map.json` and the
live index row rather than quoted from that ruling. The repo-local half of the fix — deleting the
section, amending the `Surface skill` property and `notion-map.json`'s `rule` — is dispatched to the
CTO, since Notion writes and `docs/hacp/` are outside this agent's lane. **This entry is the
framework half: without it, the next project's index is built the same way.**
