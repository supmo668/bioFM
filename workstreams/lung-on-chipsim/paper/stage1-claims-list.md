# Stage 1 registered report — CLAIMS LIST

*The entry condition for CTO rigour review (design spec §6.1). One row per claim the report will
make, each bound to the artifact or approval-log row that supports it, or marked **NOT MEASURED**.*

**A claim with no artifact is CUT, not softened.** Rows marked `CUT` below are recorded so a
reviewer can see what was proposed and dropped, rather than discovering the absence.

**Measured at:** plan r2.50c (`ae894db`), branch `lung-on-chipsim`, 2026-09-29. Every count here is
regenerated from the artifact named beside it; none is carried from prose.

---

## A. Methods — the model

| # | claim | artifact | status |
|---|---|---|---|
| A1 | The transport model is a two-compartment ODE. | `chipsim/transport/ode.py` | SUPPORTED |
| A2 | The fit is a MAP estimate of exactly two free parameters in log space. | `chipsim/transport/fit.py`; A&D §2 objective T3 | SUPPORTED |
| A3 | The model is a proof-of-concept, **not** a physiological model. | design spec §3 "not claimed"; stated in limitations §1 | SUPPORTED (a limitation, claimed as such) |
| A4 | Any fitted parameter value, goodness of fit, or comparison to data. | — | **NOT MEASURED — no fit has been performed.** CUT from Stage 1. |

## B. Methods — determinism

| # | claim | artifact | status |
|---|---|---|---|
| B1 | Given `(θ, drug, schedule, seed)`, replay is bit-comparable. | A&D "Determinism requirement"; `tests/test_replay_determinism.py` | SUPPORTED |
| B2 | Determinism is load-bearing: without it the keep-or-revert ratchet is meaningless. | A&D; the ratchet's own definition | SUPPORTED (argument, not measurement) |
| B3 | The Nelder-Mead start is deterministic, with its reason recorded rather than assumed. | `fit.py`, the recorded reason beside the start | SUPPORTED |

## C. Methods — priors and the refusal to invent

| # | claim | artifact | status |
|---|---|---|---|
| C1 | Every θ entry is SI-typed and carries a citation; an unsourced entry is flagged `assumed: true`. | A&D §2; `theta.py`'s `ThetaField`; `configs/templates/theta_priors.scaffold.yaml` | SUPPORTED (schema and validator exist) |
| C2 | The fit **refuses to run** without sourced θ. | `chipsim/transport/fit.py` — `_require_sourced_theta` (by symbol, not line) | SUPPORTED, verified by reading the call site |
| C3 | θ priors, the transport prior and `assumptions.yaml` exist. | — | **NOT MEASURED — absent; scaffold templates only.** Stated in limitations §1. |
| C4 | Agents cannot author biological values; the agent writes the schema and the validator that rejects an unsourced entry. | Global Constraint 1; `_require_sourced_theta` | SUPPORTED |

## D. Pre-registration

| # | claim | artifact | status |
|---|---|---|---|
| D1 | The metric is a **vector**: a gate scalar plus vetoes, and vetoes are absolute. | A&D §2A | SUPPORTED |
| D2 | Four vetoes are held: target-shuffle, cliff-stratified accuracy, non-monotonicity, calibration. | A&D §2A | SUPPORTED |
| D3 | Selection budget: 20–30 gated diffs per milestone, pre-registered; locked test set opened ≤2× in the project's lifetime; the gate-evaluation count is reported next to coverage. | A&D §2A selection budget | SUPPORTED (pre-registered; unexercised) |
| D4 | The two P-gp subgroups are fixed **before** any coverage is computed. | build-plan M5; A&D §2D | SUPPORTED |
| D5 | The 3-fold ordering gate holds / coverage is calibrated. | — | **NOT MEASURED — untested, uncomputed.** CUT. |

## E. Integrity — the content guard

| # | claim | artifact | status |
|---|---|---|---|
| E1 | Content guards fail **closed**. | E-22/E-23 range; `tests/shape_scan.py`; `qgr/evidence/bracket.py` | SUPPORTED |
| E2 | The guard's own blind spots are **measured rather than asserted**. | gates 6–9 findings files; gate-6 survivor analysis | SUPPORTED — this is the strongest integrity claim in the report |
| E3 | 141 of 141 in-scope sites are classified. | `qgr/evidence/r250-classify-87d5c46.json` (written by `r250-classify.py`) | SUPPORTED **only in qualified form** — see E4. May not appear unqualified (CTO #512). |
| E4 | The classification covers **provenance adjacency only**; the name-association and coined-title prohibitions are measured by nothing, the accession detector is shaped for one database, and the citation predicate is positively correlated with the violation. | gate-9 findings; limitations §2 | SUPPORTED — and it is the qualification E3 must always carry |
| E5 | 445 shapes in 20 files are outside guard scope; 62 sites in 14 files need human curation. | `qgr/evidence/r250-classify-87d5c46.json`; limitations §3 | SUPPORTED |
| E6 | The guard prevents real accessions, coined titles or name↔identifier associations from reaching tracked files. | — | **NOT MEASURED for two of the three prohibitions.** CUT in that form; replaced by E4. |

## F. The audit trail — the novel contribution

| # | claim | artifact | status |
|---|---|---|---|
| F1 | `plan-approval-log.md` is a contemporaneous, append-only, hash-locked record of methodological revisions, each bound to the plan text it approved. | `workstreams/lung-on-chipsim/plan/plan-approval-log.md`; `plan-gate verify` | SUPPORTED |
| F2 | The log carries **61 numbered revisions** plus 4 non-numbered rows (65 data rows). | `qgr/evidence/route-distribution-af17cd2.json` | SUPPORTED |
| F3 | Of **61** numbered revisions: **47 standing-delegation, 5 principal-directed, 2 human-direct, 2 standing-ruling-applied, 2 CTO-correction, 3 principal-verbatim**. | `qgr/evidence/route-distribution-af17cd2.json`, under the stated first-match-wins rule | SUPPORTED — **CORRECTED**: the first draft said "49 of 59 … 4 principal-directed", mixing substring and exact matching in one sentence with neither rule stated |
| F4 | The log records **reversals beside decisions**, not in place of them. | `#14`/`#15` (a revision that never landed, kept); the 2026-09-28 16:06 row superseded by an appended correction | SUPPORTED |
| F5 | A route convention was adopted mid-project requiring a verbatim quote or a resolvable reference for any claimed principal decision, with `inferred` as an honest fourth category. | approval-log convention row, 2026-09-29; raised by the agent, ruled by the CTO | SUPPORTED |
| F6 | **Zero rows are marked `inferred`.** | `qgr/evidence/route-distribution-af17cd2.json` | SUPPORTED — stated because the category exists and has not been needed |
| F7 | The route column was **wrong once and corrected by appending**, after the agent reported it could not distinguish two readings. | the 2026-09-28 16:06 row and its correction at the 2026-09-29 00:25 (route correction) row; the principal's verbatim confirmation | SUPPORTED — this is F4's sharpest instance |
| F8 | The distribution shows how much methodology was chosen by a human versus by an agent under delegation. | F3 | SUPPORTED as a *reported datum*, NOT as a measure of quality |

## G. The stopping rule and the gate record

| # | claim | artifact | status |
|---|---|---|---|
| G1 | Four gates (6, 7, 8, 9) returned FAIL and were accepted rather than repaired. | `qgr/gate6-…`, `gate7-…`, `gate8-findings.md`, `gate9-findings.md` | SUPPORTED |
| G2 | **No QGR receipt was signed for any failed gate**, because a receipt is a completion claim. | the absence itself; each findings file states it | SUPPORTED |
| G3 | The gate-9 stopping rule was fixed by the principal **before** the gate ran and honoured against the author's own work. | approval-log the 2026-09-28 11:30 row (the time box), applied at the 2026-09-28 16:06 row, gate-9 verdict `#58` | SUPPORTED |
| G4 | Reviewer isolation held: a content digest over a pinned file set, unchanged across the review. | `qgr/evidence/gate9-bracket-before.json`; the after-half comparison | SUPPORTED |
| G5 | The recurring defect family was **closed**. | — | **NOT MEASURED — it was not closed.** Gate 9 found it inside the mechanisms built to stop it. CUT; replaced by G6. |
| G6 | The family recurred across nine gates and is reported unclosed, with its instances measured. | gate-9 findings; limitations §5 | SUPPORTED |

## H. Claims about this report's own production

| # | claim | artifact | status |
|---|---|---|---|
| H1 | No agent authored a biological value in this report. | Global Constraint 1; `qgr/evidence/scan-artifacts-87d5c46.json` | SUPPORTED — repointed 2026-09-30 from the superseded 10-file scan record, whose file list omitted the documents asserting this very claim |
| H2 | Identifier lines flagged in two tracked plan files were escalated by the agent, inspected by the CTO, ruled by the principal, and recorded. | approval-log `#59`; limitations §6 | SUPPORTED |
| H3 | A count published in the gate-9 verdict was measured at the wrong point in time, self-reported and corrected inline. | `gate9-findings.md` correction block | SUPPORTED — recorded because it is an instance of the family in this report's own production |
| H4 | Every artifact was scanned for shaped content AND checked against the gate-9 citation predicate, over a surface derived from the SAME `git ls-files` corpus the classifier uses, then filtered to the prose/code suffixes the scanner reads — so it is a strict SUBSET of the named scope, not equal to it (`eligible_by_suffix` 127 of `tracked_in_scope` 160 in `projects/`; the remainder are data files and dotfiles, counted instead by the classifier's descope, which applies no suffix filter): 724 scanned, 0 unreadable, 30 carrying unaccounted shapes, 10 reading as cited, **7 of them inside the classified scope**. Surface vs scope, per root: `projects/` 127/127 eligible reached (0 not reached); `workstreams/` 109/109 (0 not reached). | `qgr/evidence/scan-artifacts-87d5c46.json` | SUPPORTED — restated twice; see the CUT row H5 for the claim this replaces |
| H5 | *(withdrawn H4 form)* No file reading as cited lies inside the classified scope, so none can swallow a site. | `qgr/evidence/scan-artifacts-87d5c46.json` | **NOT MEASURED in the form claimed — CUT 2026-09-30.** The predicate's scope named `projects/lung-on-chipsim/` and `workstreams/lung-on-chipsim/`, but the scan's globs reached neither fully, so the zero was computed over a partial intersection of scope and surface. Measured over the whole scope: **7** cited in-scope files, of which **5** are also placed in bucket F by the classifier and account **48** sites there (the record's seven per-file `sites_into_F` values total more than this; that total is arithmetic over the record, not a measured quantity, and is not comparable to bucket F) against a classifier bucket F of **48** at the same commit — the two instruments AGREE here. An earlier draft of this row reported a `48`-vs-`46` disagreement; that was a fresh scan compared against a STALE classifier record, not a disagreement, and it is recorded as a fabricated finding avoided rather than a result. Ruled by CTO #540 (1b). |

---

## Rebinding after rigour review pass 1

Three claims were bound to an **instrument** or an **action** rather than to a stored measurement,
which §6.2 fails rather than footnotes. Fixed by producing artifacts, not by rewording:

| was bound to | now bound to |
|---|---|
| "`r250-classify.py`, regenerated" | `r250-classify-87d5c46.json`, written by that script and committed |
| "the log's route column, counted" | `route-distribution-af17cd2.json`, under a **stated** first-match-wins rule with a per-row audit mapping |
| "the scans, run per artifact" | `scan-artifacts-87d5c46.json`, one row per artifact |

**F3 was wrong and is corrected above.** The first draft mixed substring matching ("49
standing-delegation") with exact matching ("4 principal-directed") in a single sentence and stated
neither rule. Under one consistent, stated rule the numbers are 46 and 5. That is the recurring
family occurring *in the sentence that reports the family*, caught by the CTO's traceability pass.

The route script reports an `UNCLASSIFIED` count rather than falling back silently. On its first run
that count was **1** — a row reading `CTO (route correction, principal-confirmed)` that the pattern
missed. A silent fallback would have absorbed it into a neighbouring category and the table would
have looked complete. It is 0 now because the rule was widened to its intent, not because the row
was hidden.

## Summary for the rigour review

- **41 claim rows: 35 SUPPORTED, 6 NOT MEASURED / CUT** (A4, C3, D5, E6, G5, H5) — each recorded here
  rather than softened in prose.

> *Counted structurally from the table above (`^\| [A-H]\d+ \|` rows, partitioned on the status
> column), not by hand. The first draft of this line typed "31 supported" and was wrong by four —
> caught by counting. Recorded because a typed count in the summary of a claims list is the same
> defect the report documents, and because the identity `supported + cut = total` is the check that
> caught it.*
- Two claims (E3, F8) may appear **only in qualified form**, and the qualification travels with them.

The mandatory not-claimed list (design spec §3) is carried in full in `stage1-limitations.md` §1 and
must appear in **both** granularities. The short form will be written **from this list**, never by
truncating the long form.
