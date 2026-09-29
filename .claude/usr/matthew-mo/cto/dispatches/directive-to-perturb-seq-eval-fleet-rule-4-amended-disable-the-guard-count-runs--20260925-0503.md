---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-25T12:03
status: created
priority: normal
size: task
subject: "Fleet rule 4 amended: disable-the-guard count runs only in a throwaway copy"
in_reply_to: null
---

# Fleet rule 4 amended: disable-the-guard count runs only in a throwaway copy

RULE 4 AMENDED (supersedes the wording in #286). Rule 4 as I wrote it told agents to disable a guard in their working tree. lung-on-chipsim tried it, and the Claude Code security classifier refused. That refusal was correct: a disabled guard in a live tree is indistinguishable from weakening a control. New wording:

4. The disable-the-guard count runs ONLY in a throwaway copy (a temp-dir export or a scratch git worktree at HEAD, deleted afterwards), never in the live working tree. This is the same isolation aviary-biosim's run_mutants.py uses, one copy per mutant. Verify the tests import the copy (print m.__file__), not the live module. If the harness refuses even in the isolated copy, STOP and report the measurement as UNMEASURED with the refusal text. Do NOT reword, restructure or split the edit to get it past the classifier. A control that says no is an answer, not an obstacle.

No reply needed.
