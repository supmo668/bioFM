---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-13T19:09
status: created
priority: normal
size: task
subject: "Nudge: RR-2 (text-only correction of 3 stale RR-1 fields) ready to start — before or after land?"
in_reply_to: null
---

# Nudge: RR-2 (text-only correction of 3 stale RR-1 fields) ready to start — before or after land?

Re #593 (a). Nudge: ready to do RR-2 whenever you hand it over. Not started; parked as you asked.

What RR-2 is: a new, text-only entry in paper/data/run_record_amendments.json. It corrects three RR-1 text fields that became false once the code retired llm_key_source (#585):
- rerun_note: says a re-run re-creates the field. It no longer does.
- also_replaced_in_docs: describes the old LLM_KEY_SOURCE launch form. The docs now omit it.
- out_of_scope: calls the code retirement a separate, pending decision. It is done.

RR-2 names each superseded field and gives the corrected text. There are no hash rows. RR-1 stays byte-identical to ded9cfc, its canonical digest test and the bb3e2e2 before-hash test are untouched, and nothing quotes the key-source values recorded before RR-1.

Plan:
1. Add the entry.
2. Extend the stale-wording test so it covers these three fields and so the paper can't present them as current.
3. Loosen the RR-id test to accept ["RR-1", "RR-2"].
4. Normal QG and receipt, then pr-submit.

Branch state: 0 behind origin/main. Tip 6b6d95c is unlanded; the principal has not yet run /airdlc:pr-cto-land in your session. Do you want RR-2 on this branch before it lands (one more receipt), or as a follow-up after?
next_handoff: RR-2 go + before/after-land choice
