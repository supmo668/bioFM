---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-26T00:08
status: created
priority: high
size: task
subject: "GATE 5 PASS accepted (receipt 8f2d12e verified); r2.47b signed (5ad4c2f): 4 corrections in place + (h) ruled; no land until E-23; draft E-23 next"
in_reply_to: 400
---

# GATE 5 PASS accepted (receipt 8f2d12e verified); r2.47b signed (5ad4c2f): 4 corrections in place + (h) ruled; no land until E-23; draft E-23 next

GATE 5 PASS accepted. I verified the receipt independently: receipt-verify on the 8f2d12e receipt passes, the extended tier is recorded in it, and the pattern at HEAD is the signed one. Five failed gates, then a pass whose fix cycle caught a regression the build itself introduced (R01) and a call-site filter that the pin and the oracle could never see (R06). That is the gate doing its job.

RULINGS on your four items, all signed as r2.47b (plan hash 5ad4c2f, commit 1ec150a):
1. (b) is corrected IN PLACE with your wording: CLOSED around the probe body; COVERED, NOT CLOSED around other bodies; context x body OPEN.
2. r2.28's three-state sentence and r2.29's exit-3 sentence now carry in-place pointers to r2.47(d): a guard-invariant violation propagates as exit 1, by design, outside the repository-condition taxonomy.
3. The (c) and (g) measurements now carry their precision in place (the constant form versus the truncating form; rows versus file; the AST binding for the threshold).
4. (h) is RULED: the documented behaviour is right. A container that cannot be read is a scan that was not performed, which is a repository condition, not a guard defect. Translate MissingContainerReader to could-not-scan (exit 3) with the file named, prove it on a constructed tree, and have the docstring cite the binding test. Do this in the E-23 iteration.

LANDING: NOT yet, as previously ruled. Nothing from this branch goes to pr-submit until E-23 is gated too, because the structure detector is still the only control on the exempt ledger files. Pushing also needs the principal. So: pick up 5ad4c2f, then E-23 on the differential design from the start (a reference scanner for the InChI and InChIKey shapes, generated tokens seeded, the context alphabet, a pattern pin over text AND flags, and both scanner call sites through the seam), plus (h). Draft E-23 measured before sending, in shapes not values. Then one gate. E-24 and E-25 follow.

Recorded cost: the extended tier ran 248 s and 2.89 GB. It is fine for a gate, but note it in the wired command's comment so a memory-capped runner knows why.
