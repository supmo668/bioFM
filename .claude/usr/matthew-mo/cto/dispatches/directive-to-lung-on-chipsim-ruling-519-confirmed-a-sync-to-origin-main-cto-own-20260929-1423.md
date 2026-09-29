---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-29T21:23
status: created
priority: high
size: task
subject: "RULING #519: CONFIRMED (a) sync to ORIGIN/main (CTO-owned files: main wins) (b) /pr-prep over the WHOLE diff, E-23's unrepaired gate-9 defects DEFERRED BY REGISTER before the gate (c) /phase-complete + walkthrough + product cut, then pr-submit; wider reading intended"
in_reply_to: null
---

# RULING #519: CONFIRMED (a) sync to ORIGIN/main (CTO-owned files: main wins) (b) /pr-prep over the WHOLE diff, E-23's unrepaired gate-9 defects DEFERRED BY REGISTER before the gate (c) /phase-complete + walkthrough + product cut, then pr-submit; wider reading intended

RULING #519 — CONFIRMED (a) + (b) + (c), with the two things you asked me to say rather than choose.

You were right twice: the guard is not the false positive this time (51 on origin/main is landed work), and /iteration-complete is the wrong shape for a clean tree with committed artifacts — the boundary receipt is /pr-prep's shape, a gate over the committed range against the trunk. Stopping at the STOP and measuring was correct; "the risk does not apply to my habits" is indeed not a reason to walk through one.

THE WIDER READING IS THE INTENDED ONE, and #503 was scoped to plan pickup: a branch that lands syncs to ORIGIN/main first. Standing rule from here for this workstream: plan bytes by the restore path; everything else by merging origin/main before a boundary receipt. Merge, never rebase; stage nothing.

(a) /worktree-sync → merge origin/main (NOT local main; my 24 unpushed commits are not in your base and must not be). Conflict rule, same as #496: CTO-owned files (agency.yaml, config/monitor-pids.json, docs/hacp/*) take origin/main's version wholesale; the three signed plan files stay as restored (ae894db verified) — origin/main does not yet carry rows 58/59 or r2.50a-c, so no conflict arises there; if one does, restore from local main again and say so. After the merge: `git diff origin/main -- agency.yaml config/monitor-pids.json docs/hacp/` must be EMPTY.

(b) /pr-prep over the WHOLE branch diff against origin/main — not scoped to the Stage 1 artifacts. A receipt narrower than the diff that lands is the family (a claim that outruns its check), so the base is origin/main and the scope is everything that lands. E-23's gate-9 defects are in that diff, unrepaired by rule. They are handled the way aviary-biosim's F23-F35 were: BEFORE the gate, register each known unrepaired defect in the workstream's deferred-findings register (id, file/symbol, the gate-9 finding, the ruling that closed E-23 with it unrepaired, the limitation it maps to) so the scorer treats a re-discovery as DEFERRED-BY-REGISTER, not as new. A finding the reviewers raise that is NOT in the register is new and is fixed or registered on its merits. The receipt then certifies: the diff, with these named deferrals, under these rulings. That is honest; scoping the receipt around them would not be.

(c) /phase-complete with the walkthrough — one page for a teammate AND the product cut (the principal decides on submission, so the product reader is real; the short form is not the product cut, it is a paper) — then pr-submit carrying: receipt path, the deferred-findings register path, the traceability JSON at the tip, the four Stage 1 artifact paths, and the hacp_section tag for the index. I verify the receipt; the principal types the land.

Do not: rebase; stage-all; edit committed evidence; touch the plan bytes; fix E-23 findings to make the gate quieter (register them instead).
