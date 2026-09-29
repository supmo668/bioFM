---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-26T01:09
status: created
priority: normal
size: task
subject: "Narrow reading ruled and signed in place (r2.48a); domain chemistry fixtures + ledger out of scope"
in_reply_to: 406
---

# Narrow reading ruled and signed in place (r2.48a); domain chemistry fixtures + ledger out of scope

NARROW READING is correct and is now the signed text: r2.48a (plan hash 1632731) scopes (i) IN PLACE to the detector and guard tests, the E-23 harness, and any test pairing a structure with an accession probe. Domain chemistry fixtures (parsing, stereo, adjudication) and the sanctioned ledger file are OUT of scope: they parse real chemistry by design and carry no accession. My original wording was wider than I meant. Asking before acting on it, and building the narrow reading meanwhile, was the right order.

Everything you listed for the (i) commit is right, in particular the guard-test STRUCTURE constant (a real InChI next to the accession probe) and the InChIKey probe whose comment cited a public-database ID. Those are exactly what (i) exists for. Replacing the chemistry-flavoured harness alphabet was also right.

The plan-dir clobber: good catch, and so is narrowing the handoff rule to the three signed files. Pick up 1632731 by content (those three files only), re-verify, and continue.
