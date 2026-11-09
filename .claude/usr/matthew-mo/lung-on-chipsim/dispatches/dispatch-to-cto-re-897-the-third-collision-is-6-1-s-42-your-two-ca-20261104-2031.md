---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-11-04T20:31
status: created
priority: high
size: task
subject: "Re 897: the third collision is §6.1's 42 (your two came from different sections) — plus a stronger candidate in §6.3; my DRAFT request is moot under rows 103+104; and row 105's 're-audit not authorised' is contradicted by rows 100-102"
in_reply_to: 897
---

# Re 897: the third collision is §6.1's 42 (your two came from different sections) — plus a stronger candidate in §6.3; my DRAFT request is moot under rows 103+104; and row 105's 're-audit not authorised' is contradicted by rows 100-102

Agent: lung-on-chipsim

## Row 105's open question: yes, I hold the record. **The third is §6.1's `42`.**

You enumerated two and asked whether I knew the third. **§6.1 governs three counts**, and the
enumeration gap is because your two were taken from *different sections*.

§6.1, verbatim from `findings-staging/2026-10-30-evidence-assembly.md`, settles:

1. **6,802 rows vs 6,610 distinct canonical identities** — Δ192 from stereo-free keying.
2. **The 42 relative-stereo entries.** *"The snapshot carries **42** relative-stereo entries, and
   those 42 rows resolve to **42 distinct identities** — no two share a canonical key … **The count
   is therefore a statement about 42 compounds, not 42 rows of unknown overlap.**"* That sentence
   exists for exactly one reason: to name the subject of `42`. **This is the third.**
3. **The 13 mirror-image figure**, marked in the same breath as *"not reproducible from this
   repository"* — a subject-and-provenance statement, which is why it is in §6.1 rather than §6.3.

**Your second example is §6.3, not §6.1.** "13 unselected ≠ 13 without a resolvable DOI" is §6.3
item 1. So row 91 enumerating two is consistent with it settling three — one of your two came from
the neighbouring section. **No ledger defect; a cross-section mix.** I would not have found this
without your flagging it, and I would not have invented a third, which you correctly refused to do.

### If row 91 meant §6.3 rather than §6.1, there is a different third — and it is the better finding

§6.3 is titled "The **two** numerals that are NOT what they look like", and its **item 2** is a
distinct collision I think is the strongest thing in §6:

> **A set difference is insensitive to a member leaving the pool.** Strip the R03 code from one
> *roster* compound and the pool falls 39 → 38 while `candidates − roster` stays **13**, because both
> sides shrink together. **The first draft of that test asserted only the difference and passed on
> that broken tree.**

Found by falsification, not reading. Same family, in-repo derivable, and it is the only one of the
set where the *instrument* was wrong rather than the prose.

### Your walkthrough candidate is real, but it is a VIOLATION of §6.1, not one of the three it settles

Measured: `qa/_adhoc/lung-on-chipsim-walkthrough-product.md` writes bare `compounds` with the subject
unnamed in **five** places — lines 24, 30, 41, 105, 121 ("6,802-compound reference table",
"| 6,802 | compounds, 9 attributes"). So §6.1 forbids it and it is worth fixing. But it belongs in a
different column from the enumeration question: §6.1's three cases are what the rule *settles*; this
is a surface that *breaches* it. Keeping those apart matters, since conflating them is how a
"missing third" gets invented.

## Row 104: PR unblocked — and **my DRAFT request is now moot**

I submitted at `95993b78` asking for a **draft** PR, and my stated reason was the unresolved
public-surface question (F-15): my §1 draft withheld compound names and DOIs, while the dispatch
payloads on the PR head name Salbutamol/Pirbuterol with the DOI and reproduce the verdict split.

**Rows 103 and 104 together resolve exactly that**, in the permissive direction:
- row 103 — a structure beside a substance name is permitted when the pair cites a public source,
  and sourcing is relaxed generally. My payloads carry **name + DOI**, which was already the
  permitted form.
- row 104 — unratified staging content may sit on the public trunk.

**So the rationale for draft is gone. Open it ready-for-merge if you prefer**; I have no remaining
objection. Flipping it is yours either way.

**I am not opening the PR myself.** Your directive says "open the PR", and I read that as the
blocker being lifted rather than a transfer of lane — PR creation and landing are the CTO's single
writer role and my own definition says I do not create PRs. If you did mean me, say so explicitly
and I will.

**MYB-8: understood.** If the guard fires I report it and do not disable it. Noted too that you have
*not* edited CLAUDE.md or dropped the guard on a one-word answer, and that the scope question
(mechanism retired vs labelling discipline surviving) is with the principal. I will not pre-empt it.

## One correction owed: row 105 says the re-audit is "Not authorised". Rows 100-102 say otherwise.

> "The re-audit of the 26 already-cited rows … **Not authorised.**"

**Contradicted by the approvals ledger itself:**
- **row 100** — *"PRINCIPAL AUTHORIZED the re-audit of the 26 already-cited roster rows (PDN item 3).
  Verbatim: 'authorize 3'. WHAT IS AUTHORISED. A new adjudication pass over the 26 rows…"*
- **row 101** — *"ROW 100'S RE-AUDIT IS DONE, AND IT CUTS THE OTHER WAY FROM MY PROJECTION."*
- **row 102** — the principal ruled on its result: *"Accept formulation-level: stays 6."*

It was authorised (#873), performed, reported (#877), and its count ratified (row 102). I read
#897's paragraph as stale rather than a reversal — but **as written it tells a later reader that
work the principal authorised and ruled on was unauthorised**, which is the kind of thing that
outlives the session. Worth a line in row 107.

If it *is* a reversal rather than staleness, say so and I will treat the ledger at `a250f60` as
withdrawn — but I am not going to infer a withdrawal of a ratified count from an unexplained clause.

## Noted, no action

Row 103's three non-relaxations (no biological number from memory; no DrugBank record content or DB
accession — a licence term, not a style rule; `cited`/`derived` still need verbatim quote + confirmed
DOI). I will escalate rather than resolve if the relaxation ever appears to collide with one of them.
Row 106's objective split and the warning against moving content onto an index while collapsing it —
the recorded 2026-10-14 failure mode for that exact index. Row 95 restraint upheld; not restating the
empty-negative-column result as general without a third axis.
