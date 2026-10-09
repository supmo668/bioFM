---
type: decision
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-04T06:00
status: created
priority: high
size: task
subject: "Stage 2 unblock grill 2026-10-04: TWELVE rulings, locked 'Over and out'. A1 ruled (successor branch BY CONTENT), A2 archive push due 10-06, A3 withheld files stay, A4 publishable as a standalone methods note, C1/C2/C3 closed, B1-B4 dated 10-14, B6 single curator. Fold as r3 and sign; carry each as a numbered approval-log row; merge the HACP floor to main"
in_reply_to: null
---

# Stage 2 unblock grill 2026-10-04: twelve rulings, locked "Over and out". Fold as r3, sign, carry the rows, merge the floor

Full text: `workstreams/lung-on-chipsim/grill-2026-10-04-stage2-unblock.md` on
`claude/inspiring-archimedes-h0we1b`. It is a **DRAFT amendment — not folded into `build-plan.md`
and not signed.** The plan of record is unchanged until you fold it as r3 and sign.

Route, for the convention of approval-log row 70: structured 1B1 in Claude session
`session_0181c6Cgx1w4D61dgPg73r7f` (https://claude.ai/code/session_0181c6Cgx1w4D61dgPg73r7f),
closed with the principal's 1B1 lock, verbatim **"Over and out"**. Each ruling in the record names
the option chosen and the alternatives declined.

## What binds you now

1. **A1 is ruled, not proposed.** Cut the successor branch from `main`; bring the science-bearing
   files over **by content** (roster, the three DVC pointers + `SHA256SUMS.json`, parquet sidecar,
   `label_structure_reference.yaml`, `unparseable_compounds.yaml`,
   `harmonize/{label_reference,merge_report}.py`, `audit/`, the T13 worksheet CLI and its tests,
   the S13/S14 templates, and `transport/` once A2 lands). **Exclude** `guards/`,
   `record_content.py`, `tests/shape_scan.py` and the E-21…E-23 evidence tooling. Read-only
   `scan-artifacts.py` pass before the land, as on 2026-10-01. The cut waits on the **r3 signature
   only**.

2. **The clean suite re-measurement is owed at cut time** — no concurrent pytest processes,
   recorded with its wall time. The 900 s killed run and the 453 s clean run are not comparable
   and neither supports a timing-ceiling call.

3. **A2 is the principal's, due 2026-10-06.** Until
   `archive/lung-on-chipsim-stage1` resolves on `origin`, take everything but `transport/`.

4. **A3: the five withheld files stay on the archived branch.** No redaction, no publication. The
   gap in `qgr/2026-10-01-cto-disposition.md` stands as the record.

5. **A4: you draft the Stage 1 closure as a standalone short methods note**, from
   `qgr/stage1-closure.md` — the mechanism, its nine instances (six introduced by repair) and the
   pinning rule. The **principal is the author of record** and ratifies under the T8 pattern. Draft
   by **2026-10-17**; venue chosen on the draft.

6. **C1 / C2 / C3 are closed.** SLC15A1 kept under the T8 criterion, re-checked with the three
   provisional faces at the M1 re-ratification (minisign at M1 per r2.15 item 5). The AM-6
   residual is **struck as superseded by ADR-0002** — carry the strike in the C4 README
   regeneration. Row 59 closes item H; no further per-site pass.

7. **Dates fixed: B1, B2, B3, B4 all 2026-10-14.** Emit the typed templates and validators in
   week 1 right after A1 so the principal can fill them. The r2.15 item-7 relative window is
   superseded for these items.

8. **B6: the principal curates alone.** Write and gate the M0b record schema, its validator and
   the sealed-allocation tool **before the first record is curated**; seal the three-way allocation
   before any record is read. The 3–4 week figure is a planning assumption, replaced by the
   measured rate after ten records.

9. **The HACP floor is yours to merge.** `docs/hacp/lung-on-chipsim/` on
   `claude/inspiring-archimedes-h0we1b` → `main`. The principal ruled that no pull request is
   opened from an agent session. Until it lands, every `Local path` on the ChipSim Notion rows
   points at a branch path and the weekly sync routine falls back to that branch.

## Also owed, carried from 2026-10-03

The **T18 roster approval** (26 entries, final) still needs its signed approval-log row. Its route
is the principal's session instruction of 2026-10-03, quoted in the ledger.

## Where the review surface is

The Notion HACP rows are the source of truth for review (principal, 2026-10-03). The ChipSim index
is `b7c749bd250d83dab06201f85d61ee49`; the ledger carrying all twelve rulings is
`b51749bd250d83e19016816d349af66f`. The floor mirrors them, `notion-map.json` records each row's
URL and last sync, CI fails on drift, and a weekly routine re-mirrors.

Reply with the r3 hash and the approval-log row numbers once folded.
