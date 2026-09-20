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

---

## FINALIZED — 2026-09-20

**Principal ruling (AskUserQuestion):** roster confirmed at **26 entries** — every candidate
carrying a resolvable DOI from the evidence ledger above. Selection made by the principal from
the assembled evidence; no agent selected or filtered candidates.

**Authorship of the tracked file (AskUserQuestion, explicit):** given the PROVENANCE.md precedent
(human-only authorship reserved even when content is agent-supplied), the principal was asked
whether the CTO should write `configs/poc_compounds.yaml` directly or supply copy-paste-ready
content for the principal to commit. **Ruled: the CTO writes it.** Stated grounds — narrower than
PROVENANCE.md: principal-directed transcription of a decision already made, identity+citation
only, no biological numbers, no curation judgment by the agent. This is not a change to T18's
standing ownership rule.

**Verification before hand-off:**
- 26 recounted independently from this document (26 `class="doi"` rows on the surface).
- Full InChIKeys resolved fresh from the parquet, cross-checked against the skeleton blocks
  already committed here — exact match.
- Schema + snapshot check run against the **actual** `chipsim.harmonize.roster.load_poc_roster`
  (not a re-implementation) from the worktree's own package: 26/26 pass, all keys resolve in the
  6,610-key snapshot, zero duplicates, zero empty fields.
- Relative-stereo check: the real function's `relative_stereo_keys` parameter needs `rdkit`,
  unavailable in the CTO's verification environment. Substituted by reading `stereo_is_relative`
  directly off the parquet for all 26 keys against the snapshot's 42 flagged relative-stereo
  keys — zero overlap. **Not a run of the production check; the lung-on-chipsim agent is
  directed to re-run it with full deps before treating T18 as gate-clear.**
- `record-content-gate` was NOT run against the new file by the CTO. Directed to the agent.

**Hand-off:** dispatched to `biofm/matthew-mo/lung-on-chipsim` (directive, high priority) with
the full validated YAML content. Recipient was idle; woken via `agent-wake` given priority.

**Not done by the CTO:** curation/selection (principal's), final gate verification (agent's, with
full deps this session lacked).
