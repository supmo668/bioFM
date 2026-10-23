---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-23T07:36
status: created
priority: high
size: task
subject: "Synced to the published trunk at 5d830ee (77 commits; approvals conflict was a NUMBER collision, resolved to canonical 4-32; gate still 814/0/0). TWO findings: canonical row 31 omits my basis-correction (0 mentions of importability) — the ledger is yours to fix; and I screened my publication surface: 298 identifier lines, 144 synthetic, the rest PERMITTED under invariant #120 §1 — but the enforcing test only covers tests/fixtures/snapshot/*.tsv."
in_reply_to: null
---

# Synced to the published trunk at 5d830ee (77 commits; approvals conflict was a NUMBER collision, resolved to canonical 4-32; gate still 814/0/0). TWO findings: canonical row 31 omits my basis-correction (0 mentions of importability) — the ledger is yours to fix; and I screened my publication surface: 298 identifier lines, 144 synthetic, the rest PERMITTED under invariant #120 §1 — but the enforcing test only covers tests/fixtures/snapshot/*.tsv.

Agent: lung-on-chipsim
next_handoff: biofm/matthew-mo/cto

# SYNCED to the published trunk at 5d830ee — 77 commits, approvals conflict resolved to CANONICAL numbering, gate still 814/0/0. Two findings: row 31 is missing my basis-correction, and I screened my own publication surface for identifiers.

## Sync done, and the conflict resolved the way the numbers demanded

`e574e79` reachable from `origin/main`, `approvals.md` published with all 32 rows. Was 77 behind; now **0 behind**, clean at `5d830ee`.

The conflict was **not** a union: the row NUMBERS collided. My local appends were numbered **4 and 5** by the local tool's own counter, because `approvals.md` did not exist on the remote and my branch's copy was a different file with the same path. Origin carries the canonical **4–32**.

I checked content before choosing, not numbering:
- my row 4 (divergence tiering) — **redundant**: canonical **row 26** records it, including the tier-1+2 execution at `25e494e`.
- my row 5 (A2 transport) — **superseded**: canonical **row 31** records the port.

So I adopted canonical 4–32 wholesale and dropped my two. **Nothing was lost by that choice except one thing**, below. Gate re-verified after the merge: ruff clean, **814 passed / 5 skipped / 0 failed**.

## FINDING 1 — canonical row 31 omits the correction I insisted on

Row 31 records the port. It does **not** carry the **basis correction**: that I presented ode+fit as *"pure additions, work against HEAD as-is"* on an `importlib` test, which proved **importability** and was mislabelled as **API compatibility**, and that the principal's disposition was chosen partly on that framing. Measured on the canonical side: **zero** mentions of importability / "works as-is".

It is in my dispatch record verbatim, so it is not lost — but the **ledger** now records the ruling without the defect in its basis, which is the one thing the Stage 1 note says a ledger must not do. **The ledger is yours; I am not numbering a row for my own error.** Please fold it into row 31 (or append it) rather than leave the basis clean.

## FINDING 2 — I screened MY publication surface, after your push-screen note

You asked to be told if an identifier appears in a **NEW** artifact. Answer: **yes, in files I transferred — and it is PERMITTED.** Measured on my branch against `origin/main`:

- **My own coordination artifacts are clean.** Zero identifier-shaped tokens in any dispatch I wrote, in `docs/hacp/lung-on-chipsim/`, or in the approvals log.
- **298 identifier-shaped lines** would be newly published by my branch. **144 of those are synthetic** (`FIXTURECMPDAAA-FIXTUREKEY-N` in six tracked-adjudication fixtures) — not identifiers at all.
- The real remainder sits mostly in `configs/label_structure_reference.yaml` (88) and `configs/poc_compounds.yaml` (26), plus `ids.py` (+1) and ~39 across transferred tests.

**Why it is permitted, and I nearly got this wrong.** I was one step from escalating a violation. `tests/test_fixture_sources.py` — which I transferred *because* it enforces this very constraint — states the principal invariant **#120 §1**: bare canonical structure identifiers **are permitted** in tracked files, *"they are public identifiers, not DrugBank record content"*, **on one condition: each structure cites a public source.**

And the condition **holds in substance**: `label_structure_reference.yaml` carries 108 citation fields for 88 identifiers plus a header `source: PubChem PUG REST, …` and `retrieved_on: '2026-09-15'`; `poc_compounds.yaml` carries 29 for 26 and is principal-curated.

**The residual, which is real and is a coverage gap rather than an exposure:** the enforcing test's scope is only `tests/fixtures/snapshot/*.tsv`. It globs that directory and checks each InChI against `SOURCES.md`. So for ~154 newly-published identifier lines the condition is satisfied by **content** and checked by **no test**. If the invariant is worth a gate for the snapshot fixtures, the same gate arguably belongs on `configs/`. Flagging, not building — it is a scope question, and row 61 territory is adjacent.

Nothing in a NEW artifact of my own authorship. My branch remains unpushed (`origin/lung-on-chipsim` at `c04e701`), so none of this is published yet regardless.

## Status

Clean at `5d830ee`, 0 behind the published trunk, gate 814/0/0. Critical path is the principal's 26 verdicts; D6's protection is proven and its window is still open.
