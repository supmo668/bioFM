---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-20T16:57
status: created
priority: high
size: task
subject: "Divergence RULED on a HACP surface (844e33a, approvals row 26) + tier1+2 EXECUTED (25e494e, 9M/0A). HARD CONFLICT: adjudication.py:23 imports the A1-EXCLUDED chipsim.guards.output_roots, so D6's export is restored but UNIMPORTABLE — A1's exclusion and the principal's mechanical take are incompatible. Red narrowed 8->7, blockers now 4 named per-file modules. Notion write is yours. Also disclosing a broken-instrument near-miss."
in_reply_to: null
---

# Divergence RULED on a HACP surface (844e33a, approvals row 26) + tier1+2 EXECUTED (25e494e, 9M/0A). HARD CONFLICT: adjudication.py:23 imports the A1-EXCLUDED chipsim.guards.output_roots, so D6's export is restored but UNIMPORTABLE — A1's exclusion and the principal's mechanical take are incompatible. Red narrowed 8->7, blockers now 4 named per-file modules. Notion write is yours. Also disclosing a broken-instrument near-miss.

Agent: lung-on-chipsim
next_handoff: biofm/matthew-mo/cto

# Divergence RULED on a published decision surface, tier 1+2 EXECUTED (25e494e) — and it surfaced a HARD CONFLICT between A1's exclusions and the ruling itself. D6 is still blocked, for a sharper reason.

## How it was ruled

Prose dispatches had not moved this, so I built a **HACP decision surface** — `docs/hacp/lung-on-chipsim/stage2-divergence-2026-10-20.md`, committed `844e33a`, pinned `f79f066`, Kind=Decision / L1 / Section=decision / Project=bioFM. **The Notion write is yours** — the local mirror is ready; `docs-plan place Decision` gives the contract and the row must be read back after writing.

Principal's selection, recorded as approvals row 26: **"Tiered by measured direction"**.

## What the measurement said, and why it killed the obvious option

Blob-compared both refs; line counts from `diff`; symbol counts from top-level extraction. **The instrument was validated against a known value (adjudication.py = 389/26) before the table was generated** — see the disclosure at the end for why that mattered.

| tier | n | rule | disposition |
|---|---|---|---|
| 1 | 1 | 0 Stage-2-only lines | mechanical |
| 2 | 8 | Stage-1-only ≫ Stage-2-only **and 0 Stage-2-only symbols** | mechanical |
| 3 | 2 | Stage 2 has as many or more unique lines | per-file |
| 4 | 7 | **Stage 2 has its own symbols** — `pipeline.py` 7, `transport/prior.py` 12, `transport/theta.py` 15 | per-file |
| 5 | 6 | config/build, Stage 2 larger in 3 of 6 | per-file |

**Only 1 of 24 is a clean Stage-1 win.** "Stage 1 wholesale" would have destroyed 12 and 15 Stage-2-only symbols in the two transport modules plus Stage 2's added dependencies — so A2's "only copy" clause is not merely half false: **Stage 2 has *more* symbols than Stage 1 in `prior.py` and `theta.py`.**

## Executed: tier 1+2, nine files

`25e494e` — **9 M, 0 A.** Per-file tiers verified untouched: transport, `pipeline.py`, deps, templates, `sources.yaml`, `README.md`, and the four contested tests.

Collection errors **8 → 7**, and the remaining blockers are now **precisely four modules, every one in the per-file tier**:

- `_STRUCTURE_RE`, `DVC_POINTERS` ← `chipsim.ingest.drugbank_snapshot` *(tier 4)*
- `ETL_SUBCOMMANDS` ← `chipsim.pipeline` *(tier 4)*
- `REQUIRED_FIELDS` ← `chipsim.transport.theta` *(tier 4)*

That is real progress: the red is no longer diffuse, it is four named per-file calls.

## THE CONFLICT — A1's exclusions vs the ruling, and D6 is the casualty

**`chipsim/harmonize/adjudication.py:23`:**

    from chipsim.guards.output_roots import refuse_unless_declared_output_root

**`chipsim/guards/` is A1-EXCLUDED BY NAME.** Measured: **0 source files, 0 tracked in git.** The import is unconditional at module top level, so **`adjudication.py` cannot be imported at all.**

**Consequence: D6's protection is now present and UNUSABLE.** `export_tracked_adjudication` is back (6 occurrences, `TRACKED_COLUMNS` 11) but the module carrying it will not import. So D6 is still blocked — not by a missing export any more, but by **an excluded dependency the export's own module requires**. This is a ruling conflict, not a bug: A1 excludes `guards/`, and the principal's mechanical take requires it.

**Three ways out, none of them mine:** un-exclude `guards/output_roots.py` as an A1 amendment; take `adjudication.py` in a non-wholesale form without that import; or satisfy the guard another way. **I have changed nothing and will not pick.**

**Housekeeping, and it is the `.pyc` shape again:** `chipsim/guards/` holds **22 orphaned `.pyc` files** with zero source and zero tracked files — residue from the old branch, which makes the directory *look* populated to anything listing it. It did not rescue the import (Python will not load from an orphaned `__pycache__`, correctly), but it is the same defect class as the aviary `.pyc` finding and should be swept.

## A disclosure, because it nearly poisoned this entire analysis

My **first** classification run reported all 24 files as identical — `0/0/0/0` across the board. It was wrong: the script double-prefixed its paths, every `git show` returned empty, and two empty files compare as identical. **A broken instrument produced a confident, uniform all-clear.**

It was caught only because the output contradicted a number I had measured by hand earlier (389/26). I then rebuilt the list and **validated the instrument against that known value before using it** — which is the step I should have taken first.

**And one earlier claim of mine rested on the same broken list:** "disjoint — confirmed" for the 41-file unit vs the divergent set. The conclusion is still true, but the evidence I gave for it was invalid; what actually proves it is the commit showing **41 A / 0 M**. Right answer, invalid reasoning, corrected on the surface and here.

## Still open

Tiers 3-5, fifteen files, **deps first for evidence validity** then the rest; the `guards/` conflict above, which gates D6; **A2 and A1 both to the principal** — A2's clause half false in the stronger sense now measured, A1 misclassifying five divergent files as transfers *and* excluding a module its own mechanical take requires. Not pushed; `origin/lung-on-chipsim` still `c04e701`.
