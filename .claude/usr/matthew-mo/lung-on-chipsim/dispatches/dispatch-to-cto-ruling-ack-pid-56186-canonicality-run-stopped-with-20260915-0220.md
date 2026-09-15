---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-15T09:20
status: created
priority: normal
size: task
subject: "Ruling ack (pid 56186): canonicality run stopped with no result; malate correction accepted; Dicoumarol + oxalosuccinate are ambiguous keto/enol splits under {t,m,s}; {t,m,s} is 36 stereo, not 40; aldose/ketose reported separately"
in_reply_to: 106
---

# Ruling ack (pid 56186): canonicality run stopped with no result; malate correction accepted; Dicoumarol + oxalosuccinate are ambiguous keto/enol splits under {t,m,s}; {t,m,s} is 36 stereo, not 40; aldose/ketose reported separately

# Ruling acknowledged. Canonicality run stopped with no result. Dicoumarol classified. Aldose/ketose reported separately.

**Sender: interactive session, claude pid 56186**, read-only, no git or module writes.

## 1 · #106 acknowledged and forwarded to b9

I read #106, so b9's monitor may show it as already read. I sent the ruling to b9
(pid 49951, the writer) directly, with your six implementation items. I also gave b9 advance
notice that the **41 `{t,m,s}` splits are not all clean stereoisomers**. Otherwise its merge
report would look like it disagrees with your expected figures. The mixed cases are §3 and §4
below.

## 2 · The canonicality measurement was stood down before it produced anything

I started the run at bound `maxTautomers=100`. #106 arrived while the reused setup stage was
still running, before the first progress checkpoint. I stopped it. **No input-dependence figure
exists, so there is no footnote.** I have not reported a partial number as if it were one.

## 3 · Correction accepted: malate

#104 said Malate Ion | Malate Like Intermediate "differ only in protonation (/p-2 vs /p-1)". **That
was wrong.** The source strings also differ in the H layer
(`h2,5H,1H2,(H,6,7)(H,8,9)` vs `h1-2,5-7H,(H,8,9)`), so they are tautomers, not one compound at two
protonation states. I had those strings in front of me when I wrote the sentence. The
description was wrong, and the loss itself is unaffected.

## 4 · Dicoumarol | Bishydroxy[…]: ambiguous. It SPLITS under the ruled {t,m,s} guard.

The two entries have the same formula and connectivity (`C19H12O6`, identical `/c` layer). They
differ in the H layer, and only one of them has stereo:

    DB00266 Dicoumarol    .../h1-8,20-21H,9H2                  bis-enol: OH on O20/O21, no stereo
    DB04392 Bishydroxy[…] .../h1-8,12-13H,9H2/t12-,13+          diketo:   H on C12/C13, two stereocentres

These are **keto/enol tautomers of one compound, and their stereo does not correspond**. The diketo
form carries sp3 centres at C12 and C13 that cannot exist in the enol form. That puts the pair in
the same category as **2-Oxalosuccinic Acid | 4-Hydroxy-Aconitate Ion**. It is **not** a stereoisomer
separation and **not** a clean tautomer loss, so I am calling it **ambiguous** rather than choosing a
side.

Under the ruled `{t,m,s}` guard it **splits**: the cause is `/t` on DB04392. So the 41 `{t,m,s}`
splits break down, by my hand classification, as follows:

    stereoisomer separations (as intended)                     36
    Dicoumarol | Bishydroxy[…]                                  1   ambiguous (this section)
    2-Oxalosuccinic Acid | 4-Hydroxy-Aconitate Ion              1   ambiguous (same category)
    Dihydroxyacetone | (2R)-glyceraldehyde                      1   incidental, aldose/ketose (§5)
    Glyceraldehyde-3-P | DHAP                                   1   incidental, aldose/ketose (§5)
    Malate Ion | Malate Like Intermediate                       1   accepted known loss
                                                              ----
                                                               41

I checked this against the 41 `{t,m,s}` split lines in my saved table output, not from memory.
The first draft of this paragraph placed oxalosuccinate outside `{t,m,s}` and left one split
unaccounted for. Both were wrong. 4-Hydroxy-Aconitate's changed layers are `b,m,s,t`, and
because that includes `t` the `{t,m,s}` guard fires on it too.

**#104's "40 stereo separations" for `{t,m,s}` was my heuristic's count before these hand checks,
and it was wrong.** The heuristic labelled Dicoumarol, oxalosuccinate and both aldose/ketose
pairs "stereoisomers separated", because their pre-tautomer `/t` differs. The true figure is
**36**. b9's merge report on the real module will list all 41 by name, and that list is the
record of reference.

## 5 · Separate from the stereo ruling: aldose/ketose merging

Per #105, this is not folded into the ruling.

Tautomer canonicalisation, under the default enumerator the pipeline uses, merges an aldose with
its ketose isomer through the enediol interconversion:

    Dihydroxyacetone              | (2R)-2,3-Dihydroxypropanal (glyceraldehyde)
    1,3-Dihydroxyacetonephosphate | Glyceraldehyde-3-Phosphate

Biochemically these are **distinct metabolites**. An isomerase interconverts them (triose-phosphate
isomerase for G3P/DHAP); they do not interconvert spontaneously on any timescale that matters for
binding. The ruled guard **does** separate both pairs, but only because glyceraldehyde carries a
stereocentre that the ketose lacks, so the stereo change trips the fallback. **The separation rests
on a stereo coincidence, not on a rule about aldoses and ketoses**: an aldose/ketose pair with no
stereocentre stays merged under the ruling.

The open question, independent of the layer set: **should tautomer canonicalisation be allowed to
merge an aldose with its ketose?** I have not counted how many such pairs exist beyond these two.
That would be a separate measurement, and only if you want it.
