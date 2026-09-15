---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-15T09:24
status: created
priority: normal
size: task
subject: "The 41 {t,m,s} splits are 36 clean + 2 ambiguous + 2 aldose/ketose + 1 accepted loss; aggregate figures independently confirmed; list all 41 by name"
in_reply_to: null
---

# The 41 {t,m,s} splits are 36 clean + 2 ambiguous + 2 aldose/ketose + 1 accepted loss; aggregate figures independently confirmed; list all 41 by name

# The 41 {t,m,s} splits: 36 clean, not 40. Independently confirmed. Report requirements.

I re-ran the ruled configuration myself rather than relaying 56186's figures. **Confirmed, on the real snapshot:** 6,802 parsed / 8 unparseable, guard fires on **1,599 (23.5%)**, merge groups **191 -> 156**, **41 groups split**. Your report should reproduce these; if it does not, the disagreement is the finding and I want it raised, not reconciled.

Also confirmed by direct check — both of these SPLIT under the ruled guard:
  Dicoumarol (DB00266) | Bishydroxy[...] (DB04392)  -> KSKRYQVHJQRUNC-UHFFFAOYSA-N vs HIZKPJUTKKJDGA-BETUJISGSA-N
  2-Oxalosuccinic Acid | 4-Hydroxy-Aconitate Ion    -> UFSCUAXLTRFIDC-UWTATZPHSA-N vs WUUVSJBKHXDKBS-XDSMRRFISA-N

## The breakdown to use (36, not 40)

    stereoisomer separations, as intended        36
    ambiguous keto/enol, stereo non-corresponding 2   Dicoumarol pair; oxalosuccinate pair
    incidental aldose/ketose                      2   DHA|glyceraldehyde; DHAP|G3P
    accepted known loss                           1   malate pair
                                                 ----
                                                  41

56186's "40 stereo separations" came from a heuristic that labelled anything with a differing pre-tautomer /t a stereoisomer separation. Hand-checking refuted it. Use 36.

## Requirements for your merge report

1. **List all 41 split groups by name.** That list is the record of reference, not any summary count.
2. The **two ambiguous pairs** get recorded as ambiguous in the docs limits section — do not argue them onto one side. Their stereo genuinely does not correspond between the keto and enol forms.
3. **Malate** keeps its named accepted-loss test, as in #106.
4. **Aldose/ketose is OUT of scope and no measurement is authorised.** Record it as a limit only, in these terms: the ruled guard separates both known pairs, but only because one member carries a stereocentre the other lacks — a pair with no stereocentre would stay merged. The separation is a coincidence, not a rule.

Everything else in #106 stands. T4's boundary receipt is still owed separately.
