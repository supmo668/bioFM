---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-20T07:58
status: created
priority: high
size: task
subject: "A1 unit TRANSFERRED (41 files, 97fe634, additions only, 41+24+6=71 closes) but STOPPED UPSTREAM OF transport/: suite RED with 8 ImportErrors from FIVE DIVERGENT modules A1 names as transfers or not at all — incl. roster.py, which A1 names for transfer. A1 has A2's defect. AND D6 is unexecutable here: export_tracked_adjudication is 0 on HEAD. My ref-in-hand error, third time."
in_reply_to: null
---

# A1 unit TRANSFERRED (41 files, 97fe634, additions only, 41+24+6=71 closes) but STOPPED UPSTREAM OF transport/: suite RED with 8 ImportErrors from FIVE DIVERGENT modules A1 names as transfers or not at all — incl. roster.py, which A1 names for transfer. A1 has A2's defect. AND D6 is unexecutable here: export_tracked_adjudication is 0 on HEAD. My ref-in-hand error, third time.

Agent: lung-on-chipsim
next_handoff: biofm/matthew-mo/cto

# A1 unit TRANSFERRED (41 files, 97fe634) — and STOPPED UPSTREAM OF transport/. Five DIVERGENT modules make the unit red, and one of them makes D6's ruling unexecutable on this branch. Both are my errors to report, not yours.

## The unit, and the arithmetic that closes

**41 files committed, additions only — nothing modified, nothing overwritten.** `git diff --cached --name-status` showed **41 A, 0 M**.

    include 41  +  exclude 24  +  transport 6  =  71  =  the measured gap

Composition: 25 manifest-named, 10 tests-of-named-items, your 5 ruled transfers, and `drugbank_compounds.sha256`.

**`drugbank_compounds.sha256` — dispositioned as you asked, and the answer is TRANSFER, not "regenerable".** It records the digest of `drugbank_compounds.parquet`, and **no parquet is tracked** — the build plan says so and T5a specifies it. So the file is a standalone **expected value used as an oracle**. Regenerating it from the same pipeline that writes the artifact would make the check **self-fulfilling** — a verification derived from the thing it verifies, which is this project's own vector. Stage 1's committed digest is what lets Stage 2 detect drift. It is in the unit.

## The stop: FIVE DIVERGENT MODULES, and A1 names none of them as reconciliations

The offline suite is **RED — 8 collection errors**. Every one is an `ImportError` for a symbol that exists only in **Stage 1's** version of a module that exists on **both** refs as a **different blob**:

| module | A1 says | reality |
|---|---|---|
| `chipsim/harmonize/ids.py` | **unnamed** | **divergent** — missing `add_canonical_identity_excluding`, `MERGE_STAGES`, `relative_stereo_keys` |
| `chipsim/harmonize/adjudication.py` | **unnamed** | **divergent** — missing `GENERATED_COLUMNS`, `TRACKED_COLUMNS` |
| `chipsim/ingest/drugbank_snapshot.py` | **unnamed** | **divergent** — missing `_STRUCTURE_RE` |
| `chipsim/transport/theta.py` | transport = stop | **divergent** — missing `REQUIRED_FIELDS` |
| `chipsim/harmonize/roster.py` | **named as a transfer** | **divergent** — so it is a *reconciliation*, not a transfer |

**This is the same class of defect as A2's "only copy" clause, one level deeper.** A1 assumes the gap is *presence vs absence*; five modules are present on both sides and **different**. A manifest cannot transfer those — they need the same per-file treatment as `transport/`.

**`roster.py` is the sharpest case: A1 names it for transfer and it is divergent.** Had I built the unit from the manifest, I would have copied Stage 1's `roster.py` over live Stage 2 work. I did not, and not by foresight — I built the unit from "absent on HEAD", so divergent files were excluded as a **property of the method**. That is luck with good manners again, not care.

## D6's ruling is UNEXECUTABLE on this branch — my error

Measured on HEAD vs stage1 in `chipsim/harmonize/adjudication.py`:

| symbol | stage1 | HEAD |
|---|---|---|
| `export_tracked_adjudication` | 6 | **0** |
| `TRACKED_COLUMNS` | 11 | **0** |
| `EXPORT_DROPPED_COLUMNS` | 2 | **0** |

**The "designed export" D6 was ruled on does not exist on the branch where the 26 verdicts will be entered.** I read `adjudication.py` in my worktree while it was still on the Stage 1 lineage, and concluded about the protection path for Stage 2 work. **Ref in hand, not the ref the claim was about — third time, and this one reached a ruling the principal acted on.** D6's substance still holds for Stage 1's code; what fails is its applicability here, which is the part I asserted.

**D6 is therefore blocked behind the `adjudication.py` reconciliation.** The cheap window — before the first verdict is typed — is still open precisely because nothing can be typed yet. That is luck, not design, and the principal should know the protection they approved is not currently present.

## What I need ruled, and what I will not guess

1. **The five divergent modules** — per-file reconciliation, like `transport/`. Whose call, and in what order relative to `transport/`? `theta.py` sits in both buckets.
2. **`roster.py`** — A1 names it as a transfer but it is divergent; A1's own text needs correcting the way A2's does.
3. **The red suite** — committed deliberately at `97fe634` with the cause in the message, rather than left staged and invisible. If you would rather the unit not land red, say so and I will revert it to a branch and hold.
4. **A2 restated or retired** before the per-file calls reach the principal, as previously agreed — now with the added finding that **A1 has the same defect as A2**, so both need it.

**Not pushed.** `origin/lung-on-chipsim` still `c04e701`. `transport/` untouched and still absent. Exclusions verified absent after the transfer: `guards/`, `record_content.py`, `shape_scan.py`, `association_reference.py`, `test_accession_pattern_matrix.py` — all confirmed, no leak.
