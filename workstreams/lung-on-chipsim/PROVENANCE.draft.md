# DrugBank snapshot — provenance and licence posture

<!--
DRAFT — CTO-drafted 2026-09-15 under plan r2.15 item 1; NOT YET RATIFIED.
The principal edits this into his own words, then ratifies. Until the block at the
bottom carries `ratified: true`, this file does not satisfy T1 and T11 must not pass.
Nothing below is new: every decision restated here is already recorded in
`provenance.yaml` (structured half, decided 2026-09-09) and build-plan §3.
-->

## What we use, and where it comes from

The DrugBank data in this project is **not** a licensed DrugBank download. It is the public
2015 snapshot published by Daniel Himmelstein at `github.com/dhimmel/drugbank`, pinned to a
single commit (`3e87872d…`, recorded in `provenance.yaml` and `SHA256SUMS.json`), and fetched
at build time — never vendored into this repository. It corresponds to DrugBank **4.2**,
snapshot date **2015-03-19**. Three files are used: `drugbank.tsv`, `drugbank-slim.tsv`,
`proteins.tsv`. Their SHA-256 digests are recorded at fetch time and checked on every load.

We chose a pinned public snapshot over an application-gated licence for one reason, stated in
the plan's Goal: **zero administrative lead time**. The cost is staleness — this is 2015 data —
and that cost is accepted for the M0 data spine, whose purpose is compound identity and
drug→transporter edges, not currency.

## What it contributes, and what it must never contribute

DrugBank contributes **drug → protein edges** (target, enzyme, transporter, carrier) and
compound identity (InChI/InChIKey, names, IDs). It contributes **no affinities and no
biological numbers**. That boundary is structural, not a preference: the plan's actor rule says
no coding agent writes a biological number, and DrugBank is the one source in the spine that an
agent parses end-to-end.

## The licence, in plain terms

Two statements govern this data:

1. **CC BY-NC 4.0** on the derived tables (Himmelstein's release). Attribution is required;
   **non-commercial use only**.
2. **DrugBank's own terms**: the underlying content is free for academic and non-commercial
   research; any commercial use requires a licence from DrugBank/OMx.

Our posture follows from both, and is the sentence recorded in `provenance.yaml`:

> DrugBank-derived data and anything computed from it are used solely for non-commercial
> research; academic publication and preprints are permitted, and no DrugBank-derived artifact
> may enter a product, service, or customer-facing deliverable — any commercial use requires
> rebuilding the DrugBank leg from a licensed source first.

"Derived" is read broadly and deliberately: the edge table, the canonical-identity columns, the
barrier-panel join, the P-gp labels that use DrugBank transporter edges as one input, and any
model whose training or evaluation set includes those labels. If the answer to "does this
artifact exist because DrugBank data went into it?" is yes, it is covered.

## Attribution

- Wishart DS et al. *DrugBank 4.0: shedding new light on drug metabolism.* Nucleic Acids Res
  (2014). doi:10.1093/nar/gkt1068
- Himmelstein DS et al. *User-friendly extensions of the DrugBank database v1.0.* Zenodo.
  doi:10.5281/zenodo.45579
- Licence discussion: Thinklab d213. doi:10.15363/thinklab.d213

## What would change this

If any commercial use is ever contemplated, the DrugBank leg is **rebuilt from a licensed
source** before that use — the pinned snapshot is not re-licensed after the fact. If the pinned
commit ever changes, `provenance.yaml` must carry a non-empty `commit_change_rationale`
(CTO ruling E-1) and this file must be re-ratified.

---

```yaml
ratified: false            # set true only by the principal, in his own hand
ratified_by:               # e.g. Matthew Mo
ratified_on:               # YYYY-MM-DD
digest_sha256:             # over the ratified text above this block; computed by the seal tool
drafted_by: biofm/matthew-mo/cto (session biofm-14), 2026-09-15 — plan r2.15 item 1
```
