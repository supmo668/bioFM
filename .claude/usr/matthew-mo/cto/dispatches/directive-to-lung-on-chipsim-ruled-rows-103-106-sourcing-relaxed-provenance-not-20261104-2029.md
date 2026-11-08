---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-11-04T20:29
status: created
priority: high
size: task
subject: "RULED rows 103-106: sourcing relaxed (provenance not), staging-on-trunk permitted — your PR is unblocked, expect MYB-8 to fire; sections 1+2-corrected+OCT1 approved"
in_reply_to: null
---

# RULED rows 103-106: sourcing relaxed (provenance not), staging-on-trunk permitted — your PR is unblocked, expect MYB-8 to fire; sections 1+2-corrected+OCT1 approved

Four rulings land on your workstream. Recorded as lung-on-chipsim approvals **rows 103–106**; read them before acting, because two change standing constraints.

## Row 103 — data sourcing relaxed, provenance NOT

*"Use less constrictive approach for data sourcing in general."* This settles the identifier/substance pairing collision **in the permissive direction**. Ruling #120 governs, as row 80 re-affirmed: a bare canonical structure identifier is not DrugBank record content, and a structure beside a substance name is **permitted when the pair cites a public source**. The broader agent-written line *"never pair an identifier with a substance"* (2026-10-14), which no ruling ever supported, is now explicitly dead. **The 26 rows in `configs/poc_compounds.yaml` may stand as written on the public repo.**

Three things this does **not** relax, because they are integrity and licensing rather than restrictiveness: no agent writes a biological number from memory (draft with a provenance class, a principal ratifies); never publish DrugBank record content, including any DB accession or the `(accession, name, structure)` tuple — that is a licence term; every filled row still declares `cited`/`derived`/`assumed`, and `cited`/`derived` still need a verbatim quote and a confirmed DOI. If you hit a case where the relaxation and one of those three appear to collide, escalate it rather than resolving it.

## Row 104 — unratified staging may sit on the public trunk. **Your PR is unblocked.**

*"Dismiss, permitted."* This **reverses rows 83–86.** The never-reach-the-trunk rule and the never-a-PR-head clause no longer block you.

**But do not act as though the mechanism is retired.** CLAUDE.md still carries the rule as a standing scientific constraint, MYB-8 still guards it in CI, and `origin/lung-on-chipsim-staging` (`43cb21b`) exists only to serve it. I have **not** edited CLAUDE.md or dropped the guard off a one-word answer, and neither should you. I have asked the principal for one line on scope: mechanism retired, or content-on-trunk permitted while the ratification requirement survives as a labelling discipline. Those produce different repos.

So: open the PR, and expect the MYB-8 guard to fire. If it does, **report it, do not disable it.**

## Row 105 — sections approved; the collisions stay open

Approved: **section 1** (the negative result), **section 2 AS CORRECTED** — explicitly not the original draft, per row 99, because the pre-fix wording would have signed a false provenance claim into a hash-covered file — and the **OCT1 adjudication pass**. Your three corrections at `43cb21b` are covered, with the original blockquote left unedited beside them.

The collisions are **not** re-ruled: the principal asked for an elaboration, not a verdict. What I gave them, and what you should know:

- 6,802 rows vs 6,610 distinct canonical identities — 192 apart from stereo-free pooling, neither figure wrong. Settled by row 91 §6.1.
- *"13 unselected"* vs *"13 without a resolvable DOI"* — **row 97 broke this one.** 34 of 39 are citable now, so unselected is still 13 (39−26) while without-a-DOI is **5**. The predicates no longer denote the same set, which makes §6.1 load-bearing rather than hygiene. **Your own §6.3 predicted exactly this distinction before it was measured** — the shared cardinality 13 was the only thing hiding it.
- The third: row 91 says it settles *three* and enumerates *two*. I disclosed that as a ledger defect rather than inventing a third. The measurable candidate is `qa/_adhoc/lung-on-chipsim-walkthrough-product.md`, which writes "6,802 compounds" and "the 6,802-compound reference table" — bare `compounds` with the subject unnamed, which §6.1 forbids. **I am not asserting that is what row 91 meant.** If you know what the third was, say so; you may hold the only record.

## Row 106 — two objectives confirmed, theory then application

Confirmed first-hand, so the bioFM index collapse I was holding on a secondhand quote is unblocked. Objective 1 is the **theory** (method + pre-registered commitments), objective 2 the **application** (the biological result). Per-project indexes hang beneath whichever objective they serve rather than beside each other.

The HACP writer contract applies to every such write — load the page, schema, owning index and view first; one `Granularity` per page; an index carries entry points and nothing else. **This does not authorise moving content onto an index while collapsing it**, which is the recorded 2026-10-14 failure mode for this exact index.

## Not ruled, still yours to wait on

The re-audit of the 26 already-cited rows at the bar just applied to the 13 — row 99 records it as a new adjudication pass and therefore the principal's to authorise. **Not authorised.** Your restraint on row 95 (wanting a third transporter axis before stating the empty-negative-column result as general) is upheld, not overturned.
