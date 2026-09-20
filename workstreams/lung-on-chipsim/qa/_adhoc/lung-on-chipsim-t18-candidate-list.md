---
type: candidate-list
task: T18 (roster) — CTO-owed precondition, hand-off
workstream: lung-on-chipsim
date: 2026-09-19
surface: https://claude.ai/artifact/G6xdAqUj5FeuzT32PJVoM4
evidence_source: PubMed
selection_reserved_to: principal
---

# T18 candidate list — the hand-off the plan requires

The plan: the roster is authored on a **guarded candidate list handed over by the CTO**, with the
milestone clock running *from the day of that hand-off*. No such list had ever been generated and no
command existed to produce one. This discharges it.

**Derivation (mechanical):** every compound in the parsed snapshot carrying an **ATC R03** code
(drugs for obstructive airway diseases) — **39 candidates**, against a roster band of 20–40. ATC code
is source data, not a curation judgement. Keyed by `canonical_inchikey`; the tri-state
`label_disagrees_with_key` returned **unresolved for all 39** (the reference admits only L-/D-
enantiomer base names; none qualify). `stereo_is_relative` false for all 39.

**Evidence (external):** all 39 searched via PubMed. **26 carry a resolvable DOI**; 13 do not, each
with its reason recorded. Of the 26, **9 rest on measured human lung exposure or deposition**; the
rest establish class pharmacology, clinical inhaled use, or in-vitro deposition.

Full table — compound, key, ATC, what each source shows, DOI, confidence tier — is on the surface
linked above.

## What was rejected, and why it matters

- A formulary newsletter listing every respiratory drug ranked **first for three different
  compounds** and carries **no DOI**. Discarded.
- One record ranked top for **four** compounds and then failed to resolve metadata. Discarded.
- Four sources with genuinely good content (notably bambuterol — *"prodrug with sustained lung
  affinity"*, metabolised in lung tissue) carry **no DOI**, so they cannot populate `evidence_doi`.
- Two of my own searches initially returned **hundreds of thousands** of unrelated records through an
  operator-precedence error (`X AND pk AND lung OR airway OR ...`). Re-run correctly; the bad hits
  discarded, not used.
- `Choline` and `Piperazine` at R03D are almost certainly ATC coding artifacts. Recommend excluding.

## What this is not

**Not a roster.** No entries are selected here. T18 is human-owned because *which* 20–40 compounds are
"lung-relevant with published exposure" is a curation claim, and a claim attributed to a human who did
not make it is a provenance falsehood. 26 cited candidates for a 20–40 band leaves the judgement
genuinely open — which is the point.

**Not a full-strength pool.** If the bar is *measured target-site exposure*, the pool is 9, not 26.
