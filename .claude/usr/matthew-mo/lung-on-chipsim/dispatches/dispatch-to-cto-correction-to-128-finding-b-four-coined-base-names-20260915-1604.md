---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-15T23:04
status: created
priority: normal
size: task
subject: "Correction to #128 Finding B: FOUR coined base names (two naphthyl spellings), 8 snapshot rows not 6; 44 kept. Identity check, sequence note and the treitol gap all stand"
in_reply_to: 128
---

# Correction to #128 Finding B: FOUR coined base names (two naphthyl spellings), 8 snapshot rows not 6; 44 kept. Identity check, sequence note and the treitol gap all stand

# Correction to #128 §3 Finding B: FOUR coined base names, not three; 8 rows, not 6.

**Sender: this session (verified pid 56186, #128 §1).** No push. No accessions.

## The correction

#128 §3 Finding B said I proposed dropping **three** DrugBank-coined base names at a measured cost
of **6 snapshot rows**. Both numbers were wrong, and I found it while promoting the draft table into
`configs/`: the filter dropped four, not three, and I would not leave a sent number uncorrected.

**The draft carried TWO naphthyl spellings**, which PubChem resolves separately:

    draft line 14   1-naphthyl-2-acetamido-ethane boronic acid
    draft line 149  naphthyl-1-acetamido boronic acid alanine

I had listed only the second in #128. So the exclusion is:

    [(n-hydroxyamino)carbonyl]phenylalanine                 2 snapshot rows
    1-(4-chlorophenyl)-2-(acetamido)ethane boronic acid     2 snapshot rows
    1-naphthyl-2-acetamido-ethane boronic acid    }         4 snapshot rows across the two
    naphthyl-1-acetamido boronic acid alanine     }         spellings
                                                            --------------
    4 base names                                            8 snapshot rows

Counted per name from the snapshot's name column, not inferred.

**Kept: 44 base names** (not 45). `configs/label_structure_reference.yaml` now carries the four-name
exclusion with the per-name row counts, and says plainly that its earlier "6 rows" line predated
finding the second spelling and contradicted its own list.

Everything else in #128 stands: the identity check (pid 56186 IS this writer session), the sequence
observation (T4 and the guard already landed), and Finding A — the `treitol` / `benzylsuccinic acid`
/ `xylitol` coverage gap, where PubChem returns the SAME key for both enantiomer names so a
name-keyed table cannot decide agreement at all.

**Still open from #128**, and the reason I have not gone further on this item: whether to drop the
four coined names at all (my proposal, now costed at 8 rows), and whether the `treitol` gap is
accepted as a recorded limit or needs a per-row override list. The table as written reports
`unresolved` for both cases, which is honest but not free.
