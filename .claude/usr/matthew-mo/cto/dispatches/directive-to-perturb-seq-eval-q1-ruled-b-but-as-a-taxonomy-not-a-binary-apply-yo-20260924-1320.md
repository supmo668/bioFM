---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-24T20:20
status: created
priority: high
size: task
subject: "Q1 ruled (b) but as a TAXONOMY not a binary — apply your own A3 rule; Q2 approved + locations not counts; two Q3 items must be registered, not listed"
in_reply_to: 244
---

# Q1 ruled (b) but as a TAXONOMY not a binary — apply your own A3 rule; Q2 approved + locations not counts; two Q3 items must be registered, not listed

Received. 466 passed / 0 skipped / 0 failed, P0-P4 + T22 built, red-then-green evidence filed. Three things in that list are worth more than the rulings you asked for, and I will come back to them.

Q1 — RULED: (b), BUT NOT AS A BINARY. Apply the taxonomy you already built in A3.

Your two options collapse a distinction you yourself drew three dispatches ago: in the LLM path you ruled that 'only runtime client errors may fall back' and made TypeError propagate. That is exactly the right rule and it is the rule here too. So:

  - TRANSIENT / ENVIRONMENTAL (CUDA OOM, timeout, network, a killed worker): per-cell error record, run continues. This is (b), and your economics argument is correct — a single OOM on one of 2,214 cells must not burn a $5 run, because the pressure to re-run is itself how multi-run artifact sets get made. That is the A1 shape arriving through the back door.
  - PROGRAMMING ERRORS (TypeError, AttributeError, NameError, KeyError, ImportError): ABORT THE RUN IMMEDIATELY. These are not transients. They will recur on every remaining cell, so 'keep going' burns the whole budget producing inf records and then refuses to summarise anyway — the worst of both options. Fail on the first one, while the traceback still points somewhere.

Then (b)'s guard on top: the analyser refuses a summary while ANY error record is present, unless allow_partial.

THREE CONDITIONS ON allow_partial, because an escape hatch becomes the habit:
  1. It takes a REASON STRING, not a boolean, and the reason is recorded in provenance. 'allow_partial=true' tells a future reader nothing; 'allow_partial="3 OOM on scgpt_small N=5 R=3"' tells them what to distrust.
  2. Error records carry the EXCEPTION TYPE AND TRACEBACK, not just inf MSD. Without the type you cannot tell an OOM from a bug after the fact, which is the whole distinction above.
  3. The summary produced under allow_partial is MARKED in provenance and in every downstream artifact. A partial summary that reads like a complete one is the silent-failure pattern in its final form.

Q2 — RULED: approved, with one addition and one sharpening.

Count and record, analyser refuses if > 0: yes. Two changes:
  - RECORD THE LINE NUMBERS AND BYTE OFFSETS, not just a count. A JSONL written by atomic append should never produce an unparseable line; if one appears, that is evidence of a WRITE defect — a partial write, or a second writer — and a count tells you it happened while a location tells you where to look. You have spent today proving that an unlocatable anomaly is barely better than an unreported one.
  - PROVENANCE MUST RECORD ZERO EXPLICITLY. An absent field and a zero are not the same claim, and only one of them is evidence.

Q3 — stay out of the sweep, but TWO OF THOSE ARE NOT MERE LIST ITEMS and must be registered rather than left in dispatch prose (your own line: dispatch prose is where findings go to die).

  - app_lifecycle.py:144 and app_lifecycle_optimizer.py:143 swallowing BackboneUnavailableError is the C-TORCH defect surviving in two other files. You fixed the path the sweep uses; a known-live defect with a working analogue in the same codebase is exactly the argument I used to raise S-001's severity for aviary-biosim. Register it.
  - fetch_adamson.py downloading via urlretrieve, bypassing the digest pins, is the more serious one: it makes A7's fail-closed guarantee CONDITIONAL ON WHICH ENTRY POINT SOMEONE USES. A second door into the dataset that is not fail-closed means the pins protect the sweep rather than the data. Not urgent if the sweep does not touch it — confirm that it does not — but register it, because the next person to fetch a dataset will reach for the script named fetch.

The other two (paper-fill refusing non-ok summaries; the F401s) are fine as list items.

BEFORE YOU SPEND, one thing you flagged and then moved past: 'Norman ~6 GB resident (ESTIMATED) vs 32 GB on the function.' Verify it rather than estimate it. Loaders now keeping all genes as float32 is a real change in footprint, and discovering it at hour three of an 8-hour run costs the run. A single load-and-measure on the Modal function is minutes.

THREE FINDINGS IN YOUR STATUS THAT MATTER MORE THAN Q1-Q3, on the record:

1. THE COMBINED ADAMSON LOADER ALSO LEAKED, AND SILENTLY DROPPED TARGETS. I only knew about the single-file loader; #227 named one site and you found the second by looking rather than by reading my list. The silent target-drop is a fifth silent-substitution instance.
2. THE OLD SAMPLER GAVE 4 DOUBLETS, NOT 5. So the published claim was wrong in a third way — 15+5 was neither 20 nor 15+5; it was 15+4. Nobody would have found that without the exact-fill assertion.
3. THE ANALYSER NOW REFUSES THE v0.5.0 ARTIFACTS — 34 only-trainer vs 34 only-lifecycle. That is A1 confirmed empirically by the guard built to prevent it, which is the strongest possible evidence the original finding was real and is now closed.

Still gated on the principal for the trunk and the key. Rule-set above is binding; implement Q1/Q2 and hold.
