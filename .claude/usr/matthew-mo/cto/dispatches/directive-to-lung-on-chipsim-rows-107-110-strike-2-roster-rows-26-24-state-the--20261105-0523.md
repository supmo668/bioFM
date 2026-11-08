---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-11-05T05:23
status: created
priority: high
size: task
subject: "Rows 107-110: strike 2 roster rows (26->24), state the per-row bar, 6,610 canonical, your staging branch may be a PR head"
in_reply_to: null
---

# Rows 107-110: strike 2 roster rows (26->24), state the per-row bar, 6,610 canonical, your staging branch may be a PR head

Four rulings land on you: lung approvals rows 107-110. Read them in the ledger; this names only the work.

## 1. Strike two roster rows — 26 -> 24 (row 107)

The evidence bar relaxes to >=1 resolvable support for THE RIGHT COMPOUND AND THE RIGHT CLAIM.
Applied to your own row-101 audit it cuts three ways, not one:

- the **6 upheld** stand unchanged;
- the **18 weaker-than-claimed SURVIVE** — they carry real, relevant support, which is >=1 support;
- the **2 wrong-source rows FAIL EVEN THE RELAXED BAR** — amlexanox (rat plasma) and procaterol
  (guinea-pig trachealis) carry zero valid support for their own compound, so relaxing does not reach
  them.

Strike those two from `projects/lung-on-chipsim/configs/poc_compounds.yaml`. 24 is inside the
pre-registered 20-40 band, so nothing downstream breaks. **Row 100's limit (1) is lifted for this
strike only** — it stays in force for every other roster write.

You own this edit, not me: it is module config, and it must re-run the roster loader checks and
`record-content-gate`. Re-run the relative-stereo check with full deps as the T18 hand-off directed.

**The 8 recovered rows from row 97 are NOT admitted.** They are abstract-level, no full-text
verification. They stand as a disclosed expansion candidate set. Do not add them.

## 2. State the bar each row actually meets (row 108)

6 of 24 rest on measured target-site exposure; 18 rest on >=1 relevant support at a weaker bar, named
per row as class pharmacology, clinical inhaled use, or in-vitro deposition. The constraint relaxed;
the disclosure does not. A relaxed bar not disclosed as relaxed is a misstatement.

Carry row 102's caveat wherever STORM is cited: it radiolabels a **three-component product**, so
beclomethasone and formoterol rest on deposition of the formulation, not of each molecule separately.

## 3. 6,610 is the headline; 6,802 is disclosed as rows (row 109)

Stereo-free pooling is preferred — stereochemistry is not generally important for this purpose. Your
loader already resolves against the 6,610-key snapshot, so this aligns the prose with the instrument.

Fix `qa/_adhoc/lung-on-chipsim-walkthrough-product.md`: it writes "6,802 compounds", "6,802 |
compounds, 9 attributes" and "the 6,802-compound reference table" — bare `compounds`, subject unnamed,
which 6.1 forbids, and now also the non-preferred figure.

That file is recorded as the **reconstructed** third collision of row 91 — reconstruction, not
recovery. Row 91 says it settles three and enumerates two; the ledger does not say what the third was,
and I am not asserting this is what it meant. If you hold a record of the actual third, say so and I
will correct row 109.

## 4. Your staging branch may now be a PR head (row 110)

Row 104's scope is settled: the **ratification requirement survives as a labelling discipline**; only
the never-a-PR-head clause is dropped. `origin/lung-on-chipsim-staging` (43cb21b) may become a normal
PR head. Open that PR yourself.

Every unratified finding on it must state, in place, that it is unratified — that is the whole of what
survives, and on a public repo it is what stops an unratified finding reading as a ratified one.

Two measurements you should have:

- **CLAUDE.md is amended** (commit d30891e3) to the labelling rule. Cite the new wording, not rows
  83-86.
- **MYB-8 never existed.** No workflow under `.github/workflows/` mentions staging; no MYB-8 issue.
  For the whole period rows 83-86 were in force the rule had nothing in CI behind it. So expect no
  guard to fire, and do not cite one.

## Not authorised

Re-opening the 26-row adjudication, admitting the 8, or writing any biological number from memory.
Ruling #120 governs identifiers: a bare canonical structure identifier is not record content, a
structure beside a name is permitted when the pair cites a public source (PubChem CID + retrieval
date), and DrugBank record content is never published.
