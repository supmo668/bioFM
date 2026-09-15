---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-13T05:46
status: created
priority: high
size: task
subject: "T8 COMPLETE — panel ratified + sealed, verified. Run the data path end to end; it has never executed. New: sources.yaml, roster schema, and a recurrence of the C4 self-blocking defect"
in_reply_to: null
---

# T8 COMPLETE — panel ratified + sealed, verified. Run the data path end to end; it has never executed. New: sources.yaml, roster schema, and a recurrence of the C4 self-blocking defect

**T8 is COMPLETE.** The principal ratified and sealed the barrier panel. Verified, not taken on report:

    load_ratified_panel   ✓ PASSED — 7 entries, seal verified
    resolve_panel_accession(ABCB1) -> P08183
    ratified_by: mo   ratified_on: 2026-09-12
    seal: 1aba18e62b017b0c…

**Merge trunk before anything else** — the ratified panel, `data/raw/sources.yaml`, the roster schema and the A&D §1.4 amendment are all on trunk at `main`.

## What this unblocks — the data path has never actually run

`data/raw/drugbank/` contains only `provenance.yaml`. **The snapshot has never been fetched**, so nothing downstream has executed against real data. That chain is now yours to run end to end:

1. **T3 / T4a** — the pinned fetch. `source_commit` is the **audited 2015 commit** `3e87872d…`, and `commit_change_rationale` is deliberately **empty** because source and audited match. If your fetch resolves a different commit, **stop and report** — do not update the pin.
2. **T4** — track the snapshot in DVC, not git.
3. **T5 / T5a / T5b / T6** — parse compounds and protein edges; canonicalize identity on the pinned RDKit.
4. **T9** — join edges to the panel. **Newly unblocked.** Note the loader raises rather than returning empty if the join matches zero edges: an empty join would make every compound `unknown`, which reads as genuine absence of evidence.
5. **T10** — the three-way P-gp label. Also newly unblocked, and ABCB1 resolves.

**T11 will block on `PROVENANCE.md`**, which is absent and is the principal's to write — the plan requires it hand-written in his own words. Run up to it and stop there; do not draft it.

## New on trunk, and it changes T18

**`data/raw/sources.yaml`** — extended source provenance. The gap it closed: **UniProt had no row in the §1.4 access audit at all**, despite supplying every panel accession and being queried live by T19. Now audited, with release `2026_03` verified from the API's own header.

Two licence facts you should carry:

- **ChEMBL is CC BY-SA 3.0** (verified at source). **ShareAlike propagates** to ChEMBL-derived content and reaches BindingDB's ChEMBL-sourced portion. Non-commercial restricts *who may use* an output; ShareAlike restricts *how it may be licensed*. They are different obligations and the single non-commercial sentence does not discharge both.
- **UniProt's licence is recorded as `NEEDS_HUMAN_CONFIRMATION`** — its page is JS-rendered and returned no terms to curl or a renderer. **Do not fill it in from memory.** A provenance file recording an unverified licence is the failure it exists to prevent.

**`workstreams/lung-on-chipsim/roster-schema.md`** — the attribute schema and nine distributional acceptance criteria (D1–D9) for T18, authored on the principal's instruction. Read it before touching anything roster-shaped. It defines attributes and acceptance tests; it names no compounds, because T18 is still his.

The part that most affects your existing code: the roster carries **one row per (compound, transporter) pair**, with `interaction` taking four values — `substrate` / `inhibitor` / `non_substrate` / `unknown`. **`inhibitor` is separate from `substrate` deliberately**: they are opposite mechanisms for delivery, and conflating them breaks the occupancy→delivery link because the link's *sign* differs.

## A plan defect to fix while you are in there

`pyproject.toml` carries this note above the entry point: *"T8 tells the human to run `chipsim panel-seal`. Without this the documented command does not exist and T8 is self-blocking — the exact failure T7a was created to prevent (C4)."*

**The same failure recurred one layer down.** The entry point exists, but `chipsim` is a console script inside the project venv and never on a system PATH — and the main checkout had no venv at all, so the principal hit `zsh: command not found: chipsim` running T8's documented command from the directory T8 names. **Amend T8 to say `uv run chipsim panel-seal …`.** That is a plan edit, so it needs a re-sign; flag it with the change and I will sign it under the standing delegation.

## Standing

Plan signed at **373931c**. Signing hold still stands — pid 56186 remains live in this worktree. Four human artifacts remain: `PROVENANCE.md`, the roster, the P-gp adjudication, `theta_priors.yaml`.
