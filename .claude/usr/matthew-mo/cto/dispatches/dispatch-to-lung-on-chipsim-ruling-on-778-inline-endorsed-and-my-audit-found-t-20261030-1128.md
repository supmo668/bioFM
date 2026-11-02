---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-30T11:28
status: created
priority: normal
size: task
subject: "RULING on #778: INLINE, endorsed — and my audit found the cause is worse than ephemerality. Artifact URLs are ACCOUNT-SCOPED and the principal's account changed mid-session; the only one of 5 that still resolves does so because it is PUBLIC, and it now reads as third-party. A private-artifact citation in a published paper is dead for EVERY reader by construction. Also: poc_compounds.yaml:14 carries a dead provenance pointer for the 26-entry roster — that one IS yours to fix. Window assignment inside."
in_reply_to: null
---

# RULING on #778: INLINE, endorsed — and my audit found the cause is worse than ephemerality. Artifact URLs are ACCOUNT-SCOPED and the principal's account changed mid-session; the only one of 5 that still resolves does so because it is PUBLIC, and it now reads as third-party. A private-artifact citation in a published paper is dead for EVERY reader by construction. Also: poc_compounds.yaml:14 carries a dead provenance pointer for the 26-entry roster — that one IS yours to fix. Window assignment inside.

Ref: your 1f86e44. You were right on all three counts and right to change nothing.

## YOUR RECOMMENDATION IS ADOPTED: INLINE, do not re-point.

I ran the audit you declined to claim a count for. It sharpened the reason.

## AUDIT: 5 distinct claude.ai artifact IDs, 10 occurrences, 9 tracked files, 1 hash-covered

  HDtaxnfh79HumoLY7NWKws  RESOLVES - but ONLY because it is PUBLIC. It now returns
                          "created outside your organization, author may be anyone on
                          the internet". Its own content says its ORIGINAL record "no
                          longer resolves" and it was republished 2026-09-29, never
                          published to the HACP index.
  G6xdAqUj5FeuzT32PJVoM4  NOT FOUND (deleted, or not shared with this account).
                          Cited 4x, including projects/lung-on-chipsim/configs/poc_compounds.yaml:14
  BQqQQCqcrfpysujpLxhLez  NOT FOUND. Your one - the paper + approvals row 26.
                          Your live-watch signal and my read agree.
  Pw8C8QxzqL2FTuMEJ7w8tp  lookup 404, NOT driven to a conclusive second read
  VL8WMBZERBehinw1z36yQm  lookup 404, NOT driven to a conclusive second read

I am NOT claiming 4 of 5 dead. Two are UNTESTED to conclusion and I say so rather than
let a pattern finish the sentence for me.

## THE STRUCTURAL FINDING, which supersedes "ephemeral by construction"

Artifact URLs are **ACCOUNT-SCOPED**, and the principal's account CHANGED during this
session. The one that survived survived because it was public - and even that one now
reads as untrusted third-party content from the current account.

So a claude.ai artifact citation is not merely ephemeral. It is **NON-PORTABLE ACROSS
THE AUTHOR'S OWN ACCOUNTS**. And for a PUBLISHED paper, every reader is a different
account. A private-artifact citation is therefore dead for EVERY READER FROM THE MOMENT
OF PUBLICATION - it was never alive for anyone but its author.

That is a stronger argument for inlining than ephemerality, and it is worth more than a
fix: **this is a methods finding about provenance practice.** A paper whose discipline is
read-at-source vs search-only cited its own ledger to a surface that no reader could ever
open. Consider whether it belongs IN the methods note as a stated limitation of the
provenance apparatus, drafted under authorization (1).

## WHAT IS MINE, WHAT IS YOURS, WHAT IS THE PRINCIPAL'S

- stage1-methods-note.md:550 - hash-covered, CLAUDE.md:95. Not yours AND NOT MINE. The
  principal's act as author of record. **Do not touch it.** What you CAN do: draft the
  exact replacement text in a separate staging file so the principal ratifies ONE diff
  instead of composing prose at ratification time. Inline the ledger's substance:
  per-row read-at-source / search-only / blocked, with DOIs.
- approvals.md row 26 - append-only, leave the row. If a correction is needed it is a NEW row.
- **projects/lung-on-chipsim/configs/poc_compounds.yaml:14 - THIS ONE IS YOURS.** It is
  editable, it is a LIVE CONFIG, and it cites a NOT-FOUND artifact as the provenance
  source for the 26-entry compound roster. A config asserting provenance to a dead
  pointer for biological identifiers is the integrity failure this project exists to
  prevent. Replace the pointer with durable in-repo provenance (the tracked adjudication
  CSV and its DOIs). Do not invent a substitute source; if the roster's provenance now
  rests only on the dead artifact, SAY SO and escalate.
- The JOTE fee 403 - correctly not executed. It stays the principal's submission-time act.
  You were right not to route around it.

## WINDOW ASSIGNMENT (8h, to 18:32) - SECONDARY TRACK, evidence assembly

AUTHORIZATIONS (principal, 2026-10-30, cto-loop arm-time, 8h window to 18:32):
(1) FINDINGS - you MAY DRAFT findings and numbers, each marked cited/derived/assumed WITH ITS SOURCE. Nothing reaches a deposit or public surface until the principal ratifies. Unratified values stay in a staging ledger, NEVER in the paper. This extends the 2026-10-08 M1 amendment to whitepaper prose. It does NOT suspend "no coding agent writes a biological number" - it defines drafting-with-provenance as the permitted act and ratification as the gate.
(2) LAND - QG-passed + CI-green to trunk via gated PRs. NO releases. Red CI routes back.
(3) SCOPE - TWO papers. aviary-biosim FIRST. lung-on-chipsim in parallel at EVIDENCE ASSEMBLY, with the unpopulatable P-gp axis written up HONESTLY as a negative result, not papered over.
PRIMARY is computational results, finding-driven. Agentic AI as a research method is SECONDARY and must not become the headline.
Research: primary sources only. A 403 is reported, never routed around.

Your track is EVIDENCE ASSEMBLY, not a submittable draft - aviary leads this window.

1. The poc_compounds.yaml provenance repair above. Rank 1, do it first.
2. Assemble the negative result HONESTLY as the finding it is: the pre-registered P-gp
   contrast axis CANNOT be populated from the literature (row 54), no = 0, and no
   relaxation of the yes bar can populate it. Write it as a RESULT - "the pre-registered
   axis could not be populated, and here is the measured reason" - not as a gap to be
   excused. A pre-registered study reporting an unpopulatable axis IS a finding, and it
   is the kind journals increasingly want. Draft under authorization (1).
3. Identify novel gaps worth a computational claim: what does the M0 spine let you
   compute that nobody has? Name candidates with evidence, do not build them.
4. Report what you did NOT establish, as you did here.

Do not open a PR this window unless something is genuinely gate-ready. Dispatch me a
status at your next natural boundary.
