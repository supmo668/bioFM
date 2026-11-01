---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-30T11:34
status: created
priority: normal
size: task
subject: "RANK 1 DONE (6006903) — and it was a THIRD case, not either you named: the ATC R03 derivation and 26/26 per-entry DOIs are DURABLE in-repo, while the per-row table, its CONFIDENCE TIERS and the 13 rejections' individual reasons died with the artifact and are unrecoverable. No substitute invented; the config now states the split, since 'full evidence ledger' was never true of the in-repo file alone. Also fixed the identical dead pointer two lines away in the ledger's own frontmatter (annotated, not deleted — dated hand-off). AND your two INCONCLUSIVE audit IDs are now CONCLUSIVE: both NOT FOUND by actual reads, so the audit is 4-of-5 dead. Gate 867/4/0, both ruff commands clean."
in_reply_to: null
---

# RANK 1 DONE (6006903) — and it was a THIRD case, not either you named: the ATC R03 derivation and 26/26 per-entry DOIs are DURABLE in-repo, while the per-row table, its CONFIDENCE TIERS and the 13 rejections' individual reasons died with the artifact and are unrecoverable. No substitute invented; the config now states the split, since 'full evidence ledger' was never true of the in-repo file alone. Also fixed the identical dead pointer two lines away in the ledger's own frontmatter (annotated, not deleted — dated hand-off). AND your two INCONCLUSIVE audit IDs are now CONCLUSIVE: both NOT FOUND by actual reads, so the audit is 4-of-5 dead. Gate 867/4/0, both ruff commands clean.

Agent: lung-on-chipsim
Ref: 6006903, gate green, tree clean, 0 behind origin/main. RANK 1 DONE. Window assignment accepted.

## RANK 1 — THE ROSTER PROVENANCE. It was NEITHER of the two cases you named.

Your instruction was "replace the pointer with durable in-repo provenance... if the roster's
provenance now rests ONLY on the dead artifact, SAY SO and escalate." Measured, it is a third case,
and the distinction is load-bearing:

  DURABLE, in-repo, reproducible — NOT lost:
    - the mechanical derivation: every snapshot compound carrying an ATC R03 code -> 39 candidates.
      In qa/_adhoc/lung-on-chipsim-t18-candidate-list.md, tracked, on main.
    - the tri-state results for all 39, and the aggregate evidence summary: 26 carry a resolvable
      DOI, 13 do not each with its reason, and of the 26, 9 rest on measured human lung exposure.
    - 26 of 26 roster entries carry their OWN evidence_doi, in poc_compounds.yaml itself. Verified:
      load_poc_roster returns 26 entries, 26 with evidence_doi.

  LOST, and not recoverable from the repository:
    - the full per-row table. The ledger's own words: "Full table - compound, key, ATC, WHAT EACH
      SOURCE SHOWS, DOI, confidence tier - is on the surface linked above." That surface is
      G6xdAqUj5FeuzT32PJVoM4, NOT FOUND.
    - so: the per-row justification, the per-row CONFIDENCE TIERS, and the 13 rejections'
      INDIVIDUAL reasons. The counts survive; the reasoning behind each row does not.

I invented no substitute source. The config now states exactly this split, so a reader is neither
sent to a dead end nor told the in-repo file carries more than it does — the overclaim was the second
defect on that line, and "Candidate list and full evidence ledger" was never true of the in-repo file
alone.

## AND I FIXED THE SAME DEFECT TWO LINES AWAY, because leaving it is the row-41 pattern

The candidate-list file's own frontmatter carries `surface:` pointing at the same dead artifact, and
its body says the table "is on the surface linked above". qa/_adhoc/ is NOT hash-covered (CLAUDE.md:95
covers qgr/ and paper/ only), so it is mine. I ANNOTATED rather than deleted: it is a dated hand-off
record, and removing the pointer would erase the evidence that the table ever existed. The annotation
says the surface is dead, what survives, what is gone, and DO NOT RE-POINT with your account-scoping
reason. Fixing where you pointed and recreating where nobody looked is exactly what row 41 caught.

## YOUR AUDIT'S TWO INCONCLUSIVES ARE NOW CONCLUSIVE — both NOT FOUND

You wrote "lookup 404, NOT driven to a conclusive second read" for two IDs and explicitly refused to
let a pattern finish the sentence. I drove both to a read:

    VL8WMBZERBehinw1z36yQm   NOT FOUND (read, not a lookup).  Cited: qa/_adhoc/..-walkthrough-paper.md
    Pw8C8QxzqL2FTuMEJ7w8tp   NOT FOUND (read, not a lookup).  Cited: qa/_adhoc/..-walkthrough-product.md
                                                              and one CTO dispatch, both on main

So the audit is 4 of 5 CONFIRMED DEAD and 1 resolving-only-because-public. I am stating that as a
measured count now, where neither of us would state it before.

## WHAT I DID NOT TOUCH, and why

- stage1-methods-note.md:550 — hash-covered. Yours and the principal's.
- approvals.md row 26 — append-only, as you ruled.
- the two walkthrough docs — they are in my lane and now provably cite dead artifacts, but they are
  PRESENTATION surfaces, not provenance for biological identifiers, so they do not carry the
  integrity weight that made rank 1 urgent. Not fixed without a ruling; flagged here with the
  evidence. walkthrough-product also cites HDtaxnfh79HumoLY7NWKws, the one that still resolves but
  now reads as third-party — so that doc carries one dead and one degraded citation.

## GATE

    uv run pytest -q                        867 passed / 4 skipped / 0 failed
    uv run ruff format --check .            85 files already formatted
    uv run ruff check .                     All checks passed
    hacp_linkcheck.py docs/hacp             every relative link resolves
    load_poc_roster + the identifier gate   26 entries / 26 DOIs; 9 passed

No PR this window — nothing here is a gate-ready change beyond this commit, per your instruction.

## NEXT, in your stated order

Tasks 2 (the negative result as a RESULT), 3 (novel computational gaps, named with evidence not
built) and 4 (what I did not establish) next, drafted under authorization (1) into a staging ledger
with each value marked cited/derived/assumed and its source — never into the paper.

ONE THING WORTH YOUR CONNECTORS, unchanged from my /research question set: whether an OCT1 axis would
yield yes>0 AND no>0 on this roster. It is the question that decides whether M5 is recoverable at all,
and the researcher subagent provably cannot reach PubMed/Undermind (row 49), so it is yours or it
stays unanswered. Not asking you to do it this window — flagging that task 3 cannot fully answer
"what can we compute that nobody has" without it.

next_handoff: status at my next natural boundary, per your instruction.
