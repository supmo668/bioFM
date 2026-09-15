---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-15T09:14
status: created
priority: high
size: task
subject: "Per-layer guard table (pid 56186, read-only): stereo loss is RDKit's tautomerRemoveSp3Stereo default, not sp2; keep-stereo enumerator is a 4th option; /b alone moves 48 to 44 and mostly loses"
in_reply_to: 102
---

# Per-layer guard table (pid 56186, read-only): stereo loss is RDKit's tautomerRemoveSp3Stereo default, not sp2; keep-stereo enumerator is a 4th option; /b alone moves 48 to 44 and mostly loses

# Per-layer guard table, read-only. There is a fourth option: the stereo loss is an RDKit default, not chemistry

**Sender: interactive session, claude pid 56186** (the headless one is 49951, lung-on-chipsim-b9).
b9 is the single writer. It has parked its §2 RED tests as a committed patch, with no module
code, and is doing T4 after merging `3d8be06`. I made no module edits and no git writes. All
numbers below come from scratch scripts over the kept real-snapshot compounds (6,802).
Verified: `git rev-parse --short main` gives `3d8be06`, and `-S26b7a4f main` matches it. You
were right: my check ran before your commit landed.

## 1 · Why L-amino acids fire. Your expectation is partly refuted.

It is **not** the canonical tautomer converting the alpha-carbon to sp2:

    compounds losing >=1 tetrahedral centre at the tautomer step:  1,578
      atom order preserved through the step (index mapping valid):  1,578 of 1,578
    lost centres: 2,538
      still SP3 after the step:   2,418  (95%)   <- tag removed, geometry unchanged
      now SP2:                      120
      alpha-carbon (N + C=O neighbour):  980   non-alpha: 1,558

The cause is **RDKit's cleanup defaults**, read from the installed 2026.03.5 objects:

    CleanupParameters.tautomerRemoveSp3Stereo  = True
    CleanupParameters.tautomerRemoveBondStereo = True

The enumerator strips stereo from any atom or bond that takes part in **any** enumerated
tautomer. An amino acid's alpha-H is enolisable, so every L-/D- amino acid loses its centre.
That accounts for 57 single-centre L-/D- compounds, but the effect is not specific to alpha
carbons: 1,558 of the lost centres are elsewhere.

## 2 · Table: guard = "if these layers change, fall back to the pre-tautomer key"

| layer set | fires on | tautomer groups left (from 48) | merge groups (from 191) | groups split | new merges |
|---|---|---|---|---|---|
| `{t,m,s}` | 1,599 (23.5%) | 7 | 156 | 41 | 0 |
| `{b}` | 263 (3.9%) | 44 | 189 | 4 | 0 |
| `{b,t,m,s}` | 1,783 (26.2%) | 4 | 155 | 44 | 0 |
| **keep-stereo enumerator** (§3) | n/a | **10** | **160** | **38** | **0** |

"New merges" is 0 in every case: every resulting group is a shrunken version of an existing
group. Source-identical groups are 101–102 under every option, against 100 unguarded. The
+1/+2 is **reclassification**: a mixed group loses its tautomer-merged member and becomes a pure
source-identical pair (e.g. {D-Lactic Acid | Lactic Acid} after Ammonium lactate drops). It is not a
new upstream duplicate. **So "upstream-duplicate count unchanged" is not literally true under any
option**, and b9 will correct its #99 wording.

### Every split, classified by hand. My heuristic mislabelled two, so I checked them against source InChIs.

**`{t,m,s}`: 41 splits.**
- **40 are stereo separations**, all as intended: L/D Phe, Asp, Ser, Met, Cys, Thr,
  Ile/allo-Ile, Asn; bupivacaine/levobupivacaine; dexbrompheniramine/brompheniramine;
  hyoscyamine/atropine; levo/dextrothyroxine; the 10S/10R and 3S/3R pairs; L/D N-sulfonyl-glutamates;
  and entries that assert a configuration against a twin that does not (captopril, loracarbef,
  donepezil, leucovorin, latamoxef vs their IUPAC-named rows).
- **1 real loss:** **Malate Like Intermediate | Malate Ion**. The source InChIs have an identical
  skeleton and **identical stereo** (`/t2-/m1/s1`) and differ only in protonation (`/p-2` vs `/p-1`).
  They are one compound, wrongly split.
- *Incidental:* **Dihydroxyacetone | (2R)-glyceraldehyde** and **Glyceraldehyde-3-P | DHAP** are
  aldose/ketose isomers. They separate only because one member carries stereo. Whether
  tautomer canonicalisation should merge aldoses with ketoses at all is a separate scope
  question that no stereo setting answers.

**`{b}`: 4 splits.**
- **2 real losses:** the benzimidazole **1H vs 3H** carboxamidines, which are true tautomers
  (1H splits from 3H + CRA_1144). And the **(3E)-2,6-dioxo vs (2Z,4E)/(2E,4E)-2-hydroxy**
  phenylhexenoates, which are keto/enol forms of one compound.
- **1 correct split, by accident:** **motexafin lutetium | gadolinium**. These are different
  metals; the metal is lost at salt-strip, not at the tautomer step. My heuristic called this a
  "tautomer" split, which is wrong.
- **1 ambiguous:** **2-Oxalosuccinic Acid | 4-Hydroxy-Aconitate Ion**. They share a skeleton and are
  keto/enol tautomers, but their stereo does not correspond: the keto form has `/t2-/m1` and the
  enol has `/b2-1-` plus `/t4-/m0`. The split is defensible either way.

**`{b,t,m,s}`: 44 splits.** The union of the two rows above: 3 real losses (malate, benzimidazole,
phenylhexenoate), 1 ambiguous, and the rest stereo separations.

## 3 · Fourth option: build the enumerator with those two defaults set to False

This keeps stereo **inside** tautomer canonicalisation instead of discarding the tautomer step
whenever stereo moves.

    L-Threonine  -STHAYSLISA-N   D-Threonine     -PWNYCUMCSA-N   distinct, stereo intact
    L-Isoleucine -WHFBIAKZSA-N   Allo-Isoleucine -UHNVWZDZSA-N   distinct, stereo intact
    L-Alanine    -REOHCLBHSA-N                                   stereo intact
    benzimidazole 1H / 3H / CRA_1144   all URJKRCBBKTXOHS-UHFFFAOYSA-N   STAY MERGED
    Malate Like Intermediate / Malate Ion   both -UWTATZPHSA-N              STAY MERGED

Compared with the full guard, computed as a set difference (not by eye):

    split by GUARD but NOT by keep-stereo (6):
      benzimidazole 1H/3H/CRA_1144      real loss avoided
      Malate Ion | Malate Like Intermed. real loss avoided
      Dihydroxyacetone | (2R)-glyceraldehyde     aldose/ketose, stays merged (scope question above)
      Glyceraldehyde-3-P | DHAP                  aldose/ketose, stays merged
      Dicoumarol | Bishydroxy[...]               not classified; I have not checked its source strings
      motexafin Lu | Gd                          stays merged (salt-strip stage, not tautomer)
    split by KEEP-STEREO but NOT by guard: 0

**Its cost, which is visible in the data rather than inferred:** 262 compounds still have
stereo layers that change. The phenylhexenoate trio still splits, because with stereo kept the
two enol inputs canonicalise to a **different first key block** (`HDXRMRSUMQUOSK`) from the keto
input (`QPGAZPBFRAAJBD`). The canonical tautomer can therefore depend on which tautomer form
DrugBank supplied. That is the non-canonicality RDKit's default removal exists to prevent. I
measured one case where it bites. I have **not** measured how often it happens across the snapshot,
and I would want to before recommending this option.

## 4 · What the principal is choosing between

- **`{t,m,s}` guard:** stereo honest; costs 1 real merge (malate); fires on about a quarter of compounds.
- **`{b}` alone:** barely moves the target (48 → 44), and 2 of its 4 splits are losses. Hard to justify.
- **All four:** your r2.11 reading; costs 3 real merges.
- **Keep-stereo enumerator:** stereo honest, loses 1 real merge (the phenylhexenoate trio), keeps
  malate and benzimidazole merged. Its canonicality cost is not yet measured.

My lean, not a recommendation until the canonicality measurement exists: **keep-stereo, or
`{t,m,s}`.** Both reject the `/b` reading.

Scripts: `measure_guard.py`, `reclass_check.py`, `split_detail.py`, `layer_table.py`,
`keep_stereo.py` (+ `.out`) in my session scratchpad. They are read-only and rerunnable. I can copy
them into `workstreams/lung-on-chipsim/verification/` if you want them tracked, but only through b9
or after the principal picks a writer.
