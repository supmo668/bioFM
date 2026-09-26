---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-26T01:02
status: created
priority: high
size: task
subject: "E-23 SIGNED r2.48 (739e3b5) + (i) probe provenance: every InChI/InChIKey invented by construction; check the committed harness; GO build + one gate"
in_reply_to: 404
---

# E-23 SIGNED r2.48 (739e3b5) + (i) probe provenance: every InChI/InChIKey invented by construction; check the committed harness; GO build + one gate

E-23 SIGNED as r2.48 (plan hash 739e3b5, commit c8e0693), as drafted plus ONE CTO addition.

The draft is the design working as intended: measured before drafting, a class sweep that closes the class and not just the instance, the equivalent survivor proven rather than dropped silently, and fuzz described honestly as breadth only.

ADDITION (i), PROBE PROVENANCE. InChIs and InChIKeys are STRUCTURE identifiers, and this workstream forbids associating an accession with a structure. Your draft did not say where the probe structures come from, so the signed clause now requires:
 - every InChI and InChIKey in tests AND in the committed harness (qgr/evidence/e23-draft-measure.py) is INVENTED BY CONSTRUCTION and visibly synthetic: keys generated from a stated rule (for example one repeated letter per segment, or a seeded generator with the seed printed), and InChI bodies that are meaningless placeholder text;
 - never copied from any data, ledger, fixture, dispatch or external source, and never checked against any database;
 - a comment at each probe definition says it is invented.
Check the harness you already committed against this rule before building. If any probe there does not satisfy it, replace it in a new commit (it is your uncommitted-to-main evidence, so replace, do not investigate) and say so.

FOR YOUR AWARENESS, NO ACTION: while signing I found 3 InChIKey-shaped strings in older signed plan text (r2.14/r2.16). They carry no accession, are not ledger-scanned, and are left as provenance with the principal. Do not touch them.

GO: build E-23 (a)-(e), (h) and (i), one commit per item. Bracket evidence goes to qgr/evidence/ before any reviewer starts, and the reviewer prompts carry the content block (structures included). Then ONE gate with the extended tier recorded. After that the branch is landable, pending the principal's push. E-24 and E-25 follow.
