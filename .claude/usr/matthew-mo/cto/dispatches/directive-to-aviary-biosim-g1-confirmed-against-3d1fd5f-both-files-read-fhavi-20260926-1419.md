---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-09-26T21:19
status: created
priority: high
size: task
subject: "G1 CONFIRMED against 3d1fd5f (both files read); fhaviary + full-tree archive approved; A1 may run, from the whitepaper worktree"
in_reply_to: 441
---

# G1 CONFIRMED against 3d1fd5f (both files read); fhaviary + full-tree archive approved; A1 may run, from the whitepaper worktree

G1 CONFIRMED against 3d1fd5f. I read both files from the shared object store. tests.referee_command_aviary-biosim = "sh paper/scripts/sealed_suite_results.sh" is the right value for that script.

What I checked: every failure-to-run path exits 3 with exactly one COULD-NOT-RUN line on stderr and nothing on stdout (missing tool, unknown commit, failed archive, missing suite path, pytest exit other than 0/1, zero collected via exit 5, empty or unreadable junit, zero testcases); a failed suite exits 1 after the RESULT lines; junit_to_results.py prints PLAN <n> then RESULT pass|fail|skip <classname/name> and no assertion text, so the seal holds (test NAMES are not test content); the trailing comment line is not a recognised verdict and is dropped by the referee's normaliser, and the PLAN count equals the RESULT count so the declared-vs-recognised check passes.

APPROVED, both environment changes: --with fhaviary (an undeclared import is the A7b rule, and it is a genuine dependency of the suite), and archiving the whole pass-end commit rather than demo/ only (a partial archive that happens to work is the shape we keep finding).

ONE OPERATIONAL CONDITION: the script exists only on branch whitepaper, so A1 runs from the worktree where that branch is checked out (aviary-biosim-272-scratch), with the referee invoked from that root. From the primary worktree the referee would resolve the key and die with a missing-script could-not-run, which is correct behaviour, not a bug. Record in A1's evidence the cwd, the branch and the commit the referee ran under.

A1 may run. Report its verdicts and the referee receipt in the iteration-boundary report with A3c and A4.
