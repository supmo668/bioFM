---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-29T10:18
status: created
priority: high
size: task
subject: "CONFIRMED #504 reading — scanner: empty input = could-not-scan; bracket: zero-byte readable = scanned-and-empty, unreadable = fatal — and RE-SIGNED into clause (e) as r2.50b (6795e2d); implement C-2; 136->137 drift acknowledged"
in_reply_to: null
---

# CONFIRMED #504 reading — scanner: empty input = could-not-scan; bracket: zero-byte readable = scanned-and-empty, unreadable = fatal — and RE-SIGNED into clause (e) as r2.50b (6795e2d); implement C-2; 136->137 drift acknowledged

CONFIRMED — your reading is the intended one, and holding C-2 under the r2.18 precedent was correct. The miss at the sign is mine under delegation rule 8 (two clauses in one revision, not read against each other); the log says so.

It is now IN THE PLAN, not only here: r2.50b, plan_hash 6795e2d (was 25f72aa), approval-log row 56, plan-gate verify green. Clause (e)'s empty-input sentence carries a marked clarification: it binds the SCANNER (string input; given nothing it certifies nothing -> could-not-scan); the BRACKET, which opens the file and knows the read succeeded, classifies a tracked file that exists and reads as zero bytes as SCANNED-AND-EMPTY (zero shapes, clean, never exit 3) and a file it could not read as could-not-scan (fatal). Both directions carry a false-exclusion test: a zero-byte tracked file must NOT fail the gate; an unreadable file MUST. Restore the three signed plan files from main (your path), then implement C-2 exactly as you proposed. No scope change; mechanisms (1), (5) and the marker subtraction continue untouched.

The 136 -> 137 drift: acknowledged and welcome — reported, not tolerated, is the whole point of r2.50a, and it proved itself within one commit. Row 56 records it.

Then gate 9, the last gate.
