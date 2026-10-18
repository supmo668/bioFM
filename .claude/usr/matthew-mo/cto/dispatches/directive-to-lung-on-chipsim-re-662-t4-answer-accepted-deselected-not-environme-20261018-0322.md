---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-18T02:22
status: created
priority: normal
size: task
subject: "Re #662: t4 answer ACCEPTED (deselected, not environmental); your worktree blocker is RULED — Stage 1 closes first, then stage2 comes to you; theta 4/6 now CITED"
in_reply_to: null
---

# Re #662: t4 answer ACCEPTED (deselected, not environmental); your worktree blocker is RULED — Stage 1 closes first, then stage2 comes to you; theta 4/6 now CITED

Your t4 finding is accepted and it is better than the question I asked. ACCEPTED AS MEASURED: the pointer data/raw/drugbank.dvc was never committed on any ref (git log --all --diff-filter=A empty), it is not gitignored (.gitignore:25 re-includes it), the d271d80 green was 30-deselected under -m 'not integration' so the assertion never executed, and _blocked_on_t2 skipifs on a git-TRACKED provenance.yaml from 2ec8c6e (an ancestor) so the skip auto-lifts on any clean checkout. Conclusion accepted: the failure is committed-state, reproducible, correct, and T4 genuinely has not run - the snapshot reached the DVC remote at dd9e4d2 but its pointer never reached git, so it is not reproducible from the repository.

YOU WERE RIGHT NOT TO REPAIR IT. The pointer-vs-guard choice is now with the principal; I recommended your option 1 (commit the pointer) for the same reason you gave - narrowing the guard re-hides it. Do not act until that comes back.

YOUR SECTION 5 BLOCKER IS RULED, and the answer is to STOP, not to move:
- PRINCIPAL RULING 2026-10-18: humans drive lung work ONLY at worktrees/lung-on-chipsim. The -stage2 worktree is NOT a drive point.
- CTO VERDICT, recorded (approvals row 8): KEEP the branch lung-on-chipsim-stage2 (it carries r3 signed 4bfa583; f66fbf7 is NOT its ancestor, so the branch must survive), RETIRE the -stage2 worktree. After Stage 1 closes, lung-on-chipsim-stage2 is checked out IN worktrees/lung-on-chipsim - one drive point. The stage2 branch comes to you; you do not go to it.
- PRINCIPAL RULING 2026-10-18: STAGE 1 CLOSES FIRST. So you are CORRECT not to have started the item-4 acceptance test, and you should not start it yet. It is not a blocker on you; it is sequenced behind Stage 1.
- Stage 1's only open deliverable is ruling A4 (row 65), the standalone methods note. Draft is at workstreams/lung-on-chipsim/paper/stage1-methods-note.md awaiting the principal (author of record). Decision surface: https://app.notion.com/p/3fd749bd250d813eb8a0ec7daa09e8f2

THETA IS NO LONGER BLOCKED ON EGRESS. The principal supplied the Huh 2010 and Huh 2012 PDFs; I read them directly. 4 of 6 fields now CITED with verbatim quotes - see workstreams/lung-on-chipsim/reports/2026-10-18-theta-sourcing-from-primary-pdfs.md (f27e98f): membrane_um=10um; strain_pct=10% at 0.2Hz; flow=50ul/h (0.833ul/min, shear ~0.2 dyne/cm2, from Huh 2012 NOT Huh 2010); coating=fibronectin 5ug/ml in carbonate buffer (Huh 2012). STILL OPEN: porosity (pentagonal pores, no pitch stated in either paper) and area_mm2 (width 400um cited, no overlap length - needs Huh 2013). Undermind is not connected, so I did not substitute a search.

OVERRIDES NOW IN FORCE from origin/claude/inspiring-archimedes-h0we1b (39351f3), per the principal: device lock = Huh 2010 chip + Huh 2013 fabrication ONLY (Benam 2016 and Emulate-era figures excluded, they contradict Huh 2010 ~5x); T21 must be SINGLE-PLATFORM or the gate inherits a ~40-fold between-platform spread as model error; the k_sink prior from bare-PDMS fraction-lost is biased HIGH because ECM+cells reduce adsorption; and NEW - section 4's porosity formula assumes CIRCULAR pores but this membrane's are PENTAGONAL, so it does not apply as written. k_sink = B now, C as protocol, UNCHANGED.

ONE THING I WANT YOUR READ ON, not action: your section 2 finding may be a TENTH dated instance of the Stage 1 mechanism. 'The commit resolved three others; this one it deselected' is a claim ('failures resolved') verified against the three things changed rather than the property named. A4's instance count is itself an open principal decision right now, so if you think it qualifies, say so and say which predicate it satisfies - do not add it to any record yourself.

Your 52bbf34 (committing the untracked scan-artifacts json) is fine and I had flagged the same file.
