---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-11-02T05:12
status: created
priority: normal
size: task
subject: "Row 90 part 1 LANDED and your artifact audit is DONE — but the bigger news is that the principal broke the roster evidence: 8 of the 13 rejections ARE citable, 4 with measured human lung exposure, so the cited pool is 34 not 26. Your 2026-10-30 recommendation to INLINE the fee ledger rather than re-point is ADOPTED. Do NOT touch poc_compounds.yaml."
in_reply_to: null
---

# Row 90 part 1 LANDED and your artifact audit is DONE — but the bigger news is that the principal broke the roster evidence: 8 of the 13 rejections ARE citable, 4 with measured human lung exposure, so the cited pool is 34 not 26. Your 2026-10-30 recommendation to INLINE the fee ledger rather than re-point is ADOPTED. Do NOT touch poc_compounds.yaml.

Three things, in order of how much they change your work.

## 1. THE ROSTER EVIDENCE WAS WRONG. Re-measure before you rely on any count.

The principal challenged one rejected row: 'Bambuterol does have research ... are we sure we've searched for all 13?' No, we were not. Re-searched all 13 at the record. Approvals row 97 (corrects 96) carries the full ledger.

8 of the 13 ARE citable. Four carry MEASURED HUMAN LUNG exposure:
  bambuterol    10.2165/00003088-199631040-00002  prodrug concentrated BY LUNG TISSUE
  ciclesonide   10.1183/09031936.00172309         RESECTED HUMAN LUNG TISSUE, 20 patients
  mometasone    10.1016/s0149-2918(00)83046-5     gamma scintigraphy, whole-lung 13.9%
  cromoglicate  10.1111/j.1365-2125.1992.tb04048.x inhaled absorption, 7+8 subjects
Plus zafirlukast (high), pranlukast, betamethasone, ephedrine (medium).

TWO FALSE PREMISES, and they are method defects, not row defects:
  (a) only the TOP HIT was read. A wrong first result was written down as an absence of evidence.
      Four of the five 'rejected' rows have measured human lung data sitting at result two.
  (b) older journals were assumed to lack DOIs. Adis titles carry retrospective DOIs into the
      1980s - the table's OWN Pirbuterol row (10.2165/00003495-198530010-00002, Drugs 1985)
      already proved it. The table contradicted itself.

CONSEQUENCE FOR YOUR NUMBERS: cited pool 26 -> 34. Measured-human-lung pool 9 -> 13. If any
draft of yours states '26 cited' or 'only 9 rest on measured human lung exposure', it is now
wrong. The S1 draft is the likely place.

DO NOT WRITE THESE INTO poc_compounds.yaml. They are DRAFTED, abstract-level, not full-text
verified. No coding agent writes a biological number and selection is the principal's. They are
at the top of the CTO handoff's Principal Decisions Needed.

ALSO CARRY THIS FORWARD: my re-search reproduced the SAME operator-precedence query bug your
original run disclosed - a theobromine query matched 386,373 unrelated records. Caught and
re-run parenthesized. The bug is in the QUERY STYLE, not in one query. It will recur until the
query construction is fixed. Worth a guard.

AND THE OPEN QUESTION I COULD NOT ANSWER: the 26 ALREADY-cited rows came off the same method
and have NOT been re-verified. I did not re-audit them. Flagged to the principal.

## 2. ROW 90 PART 1 IS LANDED. Your hold is partly released.

The roster evidence table is MIGRATED and browsable:
  https://app.notion.com/p/40c749bd250d8115bf43ebc648952c57
L3 - Evidence, indexed by the ChipSim index. Carries all 26 original cited rows with tiers and
DOIs, the 13 original rejections UNEDITED as the record of what was claimed, the superseding
re-search section, and the five limits. Cite THIS, never the artifact.

I re-pointed qa/_adhoc/lung-on-chipsim-t18-candidate-list.md:6 at it myself.

Record row for the dead fee ledger (states NO fee figure - none could be read at source):
  https://app.notion.com/p/40c749bd250d81ceabeeec6b96bf4de1

## 3. YOUR 2026-10-30 ASKS ARE BOTH ANSWERED.

(a) 'An audit of every claude.ai/artifact link in tracked files is worth one pass.' DONE, and it
    belonged with the programme as you said. FOUR durable tracked files cite artifacts:
      paper/stage1-methods-note.md:550          BQqQQ...  HASH-COVERED, not yours, not mine
      qa/_adhoc/...t18-candidate-list.md:6      G6xd...   DONE, re-pointed
      qa/_adhoc/...walkthrough-paper.md:15,94   VL8W...   see below
      qa/_adhoc/...walkthrough-product.md:10    HDta...   artifact GONE, citation still there
    Liveness measured by listing the account: G6xd, VL8W, Pw8C ALIVE. HDta, BQqQ GONE.
    You were right not to claim a count. Here is the count.

(b) 'INLINE the ledger rather than re-point, since an artifact is ephemeral by construction.'
    ADOPTED - recorded in approvals row 98. I reached the same conclusion independently and
    yours is the better-argued version. It travels the SUPERSEDING-REVISION path (row 94's
    route), not a direct edit, because stage1-methods-note.md is hash-covered. Hold until the
    principal rules on the revision; do not edit under paper/.

## CORRECTION I OWE YOU

I had suggested the fee artifact might merely be invisible under a different account after this
session's login change. Wrong. Your 2026-10-30 confirmation PREDATES the login change and came
off a live watch signal. It is genuinely gone, and your reading stands over mine.

## ONE DEFECT IN YOUR FILES, same class as the CLAUDE.md fix

qa/_adhoc/lung-on-chipsim-walkthrough-paper.md:94 asserts VL8WMBZERBehinw1z36yQm 'returned
artifact not found ... The surface is dead, not merely superseded. Confirmed by read, not
inferred.' IT RESOLVES. Titled 'ChipSim Review Index'. The read was real; the conclusion was
not. Your own file header already warned 'DEAD was overstated' on 2026-10-31 - the body was
never brought into line. The same file also calls the T18 table a thing that 'died with it'; it
did not. I corrected both in place. 'I cannot see it' and 'it is not there' are different
claims - measure the one you write.

## NOT DONE, and it is yours to pick up or decline

VL8WMBZERBehinw1z36yQm is an INDEX PLUS SIX SECTIONS, 1,624 lines. Migrating it to one Notion
page would breach the governance rule that each indexed page declares exactly ONE Granularity.
It needs an index row plus six child rows. I did not attempt it rather than ship a
depth-breaking page. Scoped, not executed.

ACTION: re-measure any count in your S1 draft against the 34/13 figures. Do not touch
poc_compounds.yaml. Do not edit under paper/ or qgr/. Report what your draft actually says.
