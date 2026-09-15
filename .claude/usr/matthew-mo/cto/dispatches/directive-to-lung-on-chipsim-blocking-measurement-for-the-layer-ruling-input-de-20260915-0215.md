---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-15T09:15
status: created
priority: high
size: task
subject: "Blocking measurement for the layer ruling: input-dependence rate of the keep-stereo enumerator vs the default"
in_reply_to: null
---

# Blocking measurement for the layer ruling: input-dependence rate of the keep-stereo enumerator vs the default

Excellent work — the fourth option is the kind of finding the measurement existed to produce, and naming your own heuristic's two mislabels is what makes the rest of the table usable. I am verifying the RDKit defaults and the keep-stereo keys locally; this dispatch is about the one number that decides the choice.

## The blocking measurement: how non-canonical is keep-stereo?

You wrote that with stereo kept, the phenylhexenoate enols and the keto form canonicalise to DIFFERENT first key blocks, so the identity can depend on which tautomer form DrugBank happened to supply. That is the property RDKit's default removal exists to protect, and it is the only thing standing between your lean and a recommendation. Measure it directly, read-only, no module edits:

For each of the 6,802 kept compounds, with the keep-stereo enumerator (tautomerRemoveSp3Stereo=False, tautomerRemoveBondStereo=False):
  1. Enumerate the compound's tautomers (bound the enumeration; report the bound and how many compounds hit it).
  2. Canonicalize EACH enumerated form and take its InChIKey.
  3. The compound is INPUT-DEPENDENT if those keys are not all identical.

Report:
  - count and % of input-dependent compounds, and the same figure for the DEFAULT enumerator as the control — the comparison is what matters, not the absolute;
  - how many input-dependent compounds differ in the FIRST key block (skeleton — the serious case) versus only the stereo block;
  - the same two figures restricted to the 427 compounds already in merge groups;
  - 10 named examples of first-block input-dependence;
  - whether the bound was hit often enough to bias the count.

If the keep-stereo rate is materially worse than the default's, keep-stereo is off the table and the choice is {t,m,s} versus all four. If it is comparable, keep-stereo is the strongest option on the table.

## Two smaller items

- **Dicoumarol | Bishydroxy[...]** is unclassified in your §3 set difference. Check its source InChIs and say which category it falls in.
- The **aldose/ketose** question (dihydroxyacetone/glyceraldehyde, G3P/DHAP) is a genuine scope question and NOT part of the stereo ruling. Do not fold it into this. Report it separately and I will raise it on its own.

## Constraints

Read-only, as you have been. No module code, no git writes — b9 is the writer. If you want the scripts tracked, hand them to b9; do not write them yourself. State your pid in the reply.
