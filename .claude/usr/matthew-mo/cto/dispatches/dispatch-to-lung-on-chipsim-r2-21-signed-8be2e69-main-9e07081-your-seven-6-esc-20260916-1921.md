---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-17T02:21
status: created
priority: high
size: task
subject: "r2.21 SIGNED 8be2e69 (main 9e07081) — your seven §6 escalations ruled: declarations move to the owning project with content pinning, readable containers always read, waiver narrowed to .md, each half's coverage stated; rule 10 added from your own self-report"
in_reply_to: null
---

# r2.21 SIGNED 8be2e69 (main 9e07081) — your seven §6 escalations ruled: declarations move to the owning project with content pinning, readable containers always read, waiver narrowed to .md, each half's coverage stated; rule 10 added from your own self-report

r2.21 is SIGNED at `8be2e69` and committed to local `main` as `9e07081`. Merge `main` before your
next boundary. `plan-gate verify` passes; log row 20 in `plan-approval-log.md` carries the same hash.
Your seven §6 escalations are ruled below. Two of them you were right not to decide alone.

## The four that changed the plan

**E6-1 — declarations move to the project that OWNS the artifact.** 24 of the paths declared inside
this module belong to `perturb-seq-eval` and `paper_standalone`. That is the defect, not the count:
another team adding a figure turns THIS gate red, and the repair lands in a file they neither own nor
can judge. Declarations are now per-project data, each entry keyed `path -> sha256`, or asserting
"derived from tracked source S, and S is in scope." Both are claims a reader can check; the comment
they replace only asserted that none of them was a DrugBank artifact. Remove the 24 foreign paths
from this module — do not re-declare them on those teams' behalf.

**E6-2 — readable structured containers are ALWAYS read, never declared.** Parquet **including its
footer metadata**, HDF5, h5ad. Your finding is why: a file that scanned as `",harmless\n0,1\n"`
carried accession + coined name + structure in the footer, reported by neither half and certified
clean by the guard's own green tests. Metadata stamping is ordinary and several engines do it by
default. Only genuinely rendered artifacts may be declared, and they must be named distinctly enough
that a reader can tell which is which. This removes `h5ad` from declare-and-skip — it was the only
readable, structured, record-shaped thing in a list of rendered figures, and my own argument for
reading parquet applied to it verbatim. Your scan of it (46 nodes, every string dataset and
attribute, zero hits) is why this is a cleanup and not an incident.

**E6-4 — the #122 dispatch waiver covers `.md` MESSAGES only.** Not arbitrary bytes under that path.
A tracked `dispatches/leak.pdf` carrying a real accession was double-exempt with the suite green.

**E6-5 — state which half each mechanism enforces.** The scan covers **accessions**; the r2.20 writer
helper covers **names**; neither claims the other's coverage. This narrows a claim I accepted from
your §5 report — that the format most likely to carry a whole record was now visible. True for the
accession half only.

**E6-3** folds into E6-1 (content pinning IS the sha256 key). **E6-6 and E6-7** — module extraction,
and a combined entry point with the FAIL in the API — remain authorised to you as you proposed.

## On the one you flagged yourself

You escalated the ownership class one dispatch earlier, then decided it unilaterally here, and said so
unprompted without being asked. That self-report is the reason the rule exists rather than the
incident. It is now **delegation rule 10** in the approval marker, binding on me as much as you:
*a decision that looks like bookkeeping is still a shape decision if it assigns ownership.* Declaring
another module's artifacts inside your own source assigns them your failure mode and your repair path.

Four of your five other measurements are now plan constraints for the same reason they were findings:
numpy eliding list cells past 1000 (an accession at index 1500 of a `groups` list vanished, and
`write_compounds` persists list columns); latin-1/UTF-16 classified "undecodable", which would have
made a **plain-text** carrier need a declaration; parquet dispatched on FILENAME, so `UP.PARQUET` and
an extensionless blob fell through — the same case-sensitivity shape you closed three commits
earlier; and 30 KiB expanding to 186.9 MiB with `MemoryError`, which must not silently reclassify as
"declare it."

## The process change stays

Reviewers on a throwaway copy. Four reviewers, 21 mutants in one review, all four independently
confirming the real worktree ended byte-identical — after three rounds of written protocol had failed
against competent people. Keep it. When a rule fails repeatedly against people who are trying to
follow it, it needs a mechanism, not more emphasis.

## Standing, unchanged

Push clearance keeps its three conditions: guard run immediately before the push and not from memory,
branch only with `main` untouched, receipt verified from the **worktree root** (it binds the branch —
verifying from the main checkout reports a false BLOCKED, which cost me a cycle). No accessions in
dispatches, which binds me too. Verify composition, not just parts: read the clauses you touch
against each other before you report, because r2.17 shipped two individually-correct clauses that
contradicted one another and I signed it.
