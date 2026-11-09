---
type: candidate-list
task: T18 (roster) — CTO-owed precondition, hand-off
workstream: lung-on-chipsim
date: 2026-09-19
surface: https://app.notion.com/p/40c749bd250d8115bf43ebc648952c57
# Re-pointed 2026-11-02 (lung approvals rows 90, 98). The surface was
# claude.ai/artifact/G6xdAqUj5FeuzT32PJVoM4, which is account-scoped and so unreadable for
# every reader but its author. It was read in full and MIGRATED to the Notion row above.
# The artifact still resolves for its author; it is simply no longer the surface.
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

Full table — compound, key, ATC, what each source shows, DOI, confidence tier — **WAS on the surface
linked in this file's `surface:` frontmatter, and that surface NO LONGER RESOLVES** (confirmed
2026-10-30 by a live watch signal and an independent CTO read; ruling by CTO dispatch 2026-10-30 —
NO approvals row covers it, and the "approvals row 79" citation used here until 2026-10-31 was
wrong). **CORRECTED 2026-10-31:** that surface does not resolve *for this agent*; it is
**account-scoped** and resolves for its owner. The CTO read it at 02:20 on 2026-10-31 and the full
per-row table is **INTACT** — all 26 cited candidates with compound, key, ATC, what each source
shows, DOI and confidence tier, plus the 13 without a usable citation. The earlier wording here
said the table was "not recoverable", which was false: what was measured was an inability to read,
and what was written was a non-existence.

The true, narrower claim: **the table is not IN this repository, and its only copy is a surface
readable only by its owner.** What survives *here* is the mechanical derivation, the tri-state
results and the aggregate counts above. It is deliberately **not transcribed in** — every row
pairs a substance name with a structure key, and whether such a pairing may sit on a public surface
is unresolved with the principal.

The `surface:` field is left in the frontmatter deliberately rather than deleted: this is a dated
hand-off record, and removing the pointer would erase the evidence that the table ever existed. It
is annotated as dead instead. **Do not re-point it at a new artifact** — claude.ai artifact URLs are
ACCOUNT-SCOPED, so such a citation is unreadable from any account but its author's, and dead for
every reader of a published paper from the moment of publication. Durable provenance goes in-repo.

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

**CORRECTED 2026-11-07 (approvals row 103, principal-ratified; and row 102).** The two paragraphs
above and below this block are left as written, because they record what was claimed. Two figures in
them are now superseded:

- **"26 cited candidates" is true only of the citation count, not of citation support.** Two of the
  26 carry a source that does not support the entry: **Amlexanox** (`10.1002/bmc.5288` — rat plasma,
  Wistar rats, no `Humans` MeSH, and a method-validation paper) and **Procaterol**
  (`10.3390/ijms19071999` — guinea pig trachealis). The principal ruled on 2026-11-07 to **keep the
  roster at 26 and disclose both as defects** rather than strike them, so these two are **retained by
  ruling, not by evidence.** Anyone counting cited rows must carry that; it is part of the ruling, not
  a limitation of it.
- **"the pool is 9" is REFUTED.** At the measured-target-site bar the reproducible figure is **6**,
  established by the 26-row re-audit and ratified at approvals row 102 — not 9 (the original claim)
  and not 13 (an intermediate revision that was also not reproducible).

**The sentence to carry, never the bare 6:** *6 of 26 rest on measured target-site exposure — three
of them from one 12-volunteer cohort (`10.1111/bph.15621`), two more from a single formulation
study.* **Binding:** any text citing STORM (`10.1089/jamp.2021.0046`) for Beclomethasone or
Formoterol target-site exposure must carry the **formulation qualification** — STORM radiolabels a
three-component formulation, so it is not per-molecule deposition. Dropping that qualification
re-admits the exact misstate-the-source defect the re-audit exists to catch.

**Ratification states, not to be implied from one another:** the **count** of 6 is ratified (row 102)
and the **disposition** of the two defective entries is ratified (row 103); the **26 per-row
verdicts** of the re-audit **remain drafted and unratified**.

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
