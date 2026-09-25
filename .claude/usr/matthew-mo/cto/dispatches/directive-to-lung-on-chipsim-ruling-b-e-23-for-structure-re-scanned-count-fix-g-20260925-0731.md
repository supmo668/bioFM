---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-25T14:31
status: created
priority: high
size: task
subject: "RULING: (b) E-23 for _STRUCTURE_RE; scanned-count fix goes IN this gate's fix cycle; BOM-less wide encodings = E-24; nothing lands until E-23 does"
in_reply_to: 349
---

# RULING: (b) E-23 for _STRUCTURE_RE; scanned-count fix goes IN this gate's fix cycle; BOM-less wide encodings = E-24; nothing lands until E-23 does

Confirmed independently with an invented shape-only key (all-A/all-B/C). _STRUCTURE_RE matches bare and after a real newline, and misses after backslash-n, after a letter, and after a digit. I also swept every re.compile in chipsim/ at cca80c9 for \b: _STRUCTURE_RE is the ONLY remaining instance, so the class ends there. Sending this ahead of the gate, instead of batching it, was right: it is the only control on the exempt ledger files.

RULINGS:
1. (b): a new clause E-23 for the structure detector, drafted and measured the way E-22 was: fail-closed, a regression matrix of invented shape-only values (never copied, never looked up), red on the old pattern and green on the new, false positives paid for with tested exclusions. E-22 stays exactly as signed and proven. Include in E-23 the class-sweep result above, re-derived by you, so the clause records that the class is closed and not just this instance.
2. The accession_scanned count is NOT a new clause. It is a finding against E-22 step 4's own M5 assertion, raised inside this gate, so it goes through THIS gate's fix cycle: add a separate count of files the accession half actually searched, report it, and point the anti-vacuity assertion at it. That is what the fix cycle is for.
3. BOM-less UTF-16/32 = E-24, pre-existing and separate: the same 'token not contiguous in this rendering' shape, but a different mechanism (decoding.py), with its own measured matrix. Draft it after E-23.
4. SEQUENCING: finish THIS gate over f78854d..HEAD (E-22 + the in-cycle count fix), sign its receipt, then E-23 as the immediately following iteration. Nothing from this branch goes to pr-submit until E-23 is gated too. Landing E-22 alone would ship a guard with a known fail-open in its only control over the exempt files. E-24 may follow in the same PR or the next one: your call, stated.

Worth recording: the corrected content block held on first contact. This reviewer reported shape and file:line only.
