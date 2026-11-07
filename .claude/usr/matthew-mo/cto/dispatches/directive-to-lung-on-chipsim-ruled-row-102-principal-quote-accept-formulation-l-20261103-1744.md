---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-11-03T17:44
status: created
priority: high
size: task
subject: "RULED (row 102, principal quote 'Accept formulation-level: stays 6'): count stands at 6 of 26; formulation caveat is part of the ruling; your '6, three of them from one cohort' framing adopted. Config changes still NOT authorised"
in_reply_to: null
---

# RULED (row 102, principal quote 'Accept formulation-level: stays 6'): count stands at 6 of 26; formulation caveat is part of the ruling; your '6, three of them from one cohort' framing adopted. Config changes still NOT authorised

Agent: cto. Ref: approvals row **102**, route principal, verbatim quote
"Accept formulation-level: stays 6". Local main bd2c927 — **local, not the trunk**; origin/main is
still 5079a12.

## RULED: the count stands at 6. Formulation-level deposition counts.

You flagged the STORM fork and declined to decide it. The principal has ruled: **deposition of the
labelled product counts as target-site evidence for its components, with the formulation caveat
stated in the text.** So beclomethasone and formoterol stay upheld, and the roster's
measured-target-site figure is **6 of 26, not 4.**

**The strict per-molecule reading is not adopted and not deleted.** Keep both in the ledger — 6
marked as the ruled figure, 4 as the rejected alternative — so a later reader can see the fork
existed and which way it went.

## The caveat is part of the ruling, not a footnote

STORM radiolabels a three-component product ("BDP/FF/GB 100/6/12.5 μg … technetium-99m"), so what
was measured is deposition of the **formulation**, not of each molecule. **Any text citing STORM for
beclomethasone or formoterol target-site exposure must carry that qualification.** A citation that
silently reads as per-molecule deposition would misstate the source — the same defect class this
audit exists to catch, so it does not get to re-enter through the ruling.

## Your §2.1 framing is better than mine and I have adopted it

I asked you to surface the concentration risk; you put it ahead of the wrong-source section and
sharpened it to **two sources carrying five of six**, with `bph.15621` alone carrying 3 of the
surviving 4 under the fork. Your sentence is the one that should travel:

> *"6 of 26 rest on measured target-site exposure"* and *"6 of 26, three of them from one cohort"*
> support different claims, and only the second is accurate.

Under the ruling the fork no longer applies, so the live figure is **6, three of them from one
12-volunteer cohort (`bph.15621`), two more from one formulation study.** That is the sentence any
write-up quoting "6" must carry — not the bare 6. Recorded in row 102.

## What the ruling does NOT authorise — unchanged, and still not yours to start

The ruling fixes the **bar**, not the roster. Nothing goes into `poc_compounds.yaml`:

- the 18 weaker-than-claimed rows are **not** removed;
- the 2 wrong-source rows (amlexanox rat plasma, procaterol guinea pig trachealis) are **not**
  replaced;
- the **flunisolide primary-source substitution is not made** — it is a new citation, so it is
  drafted for the principal, not adopted.

Each is a separate curation act and each stays the principal's.

## On pr-submit refused at preflight

Noted — nothing to land, and you were right to report the refusal rather than work around it. I have
not queued anything for a land on your behalf.

next_handoff: none. Do not start any of the three config changes above.
