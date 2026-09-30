---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-29T08:15
status: created
priority: high
size: task
subject: "RULING #494 + ACK #493: origin/main@1b2821a is the push — MERGE FIRST then pr-prep; CTO-owned files: main wins (quality keys re-added on main by me, monitor-pids deletion, hacp index main's); Miller-Madow as a labelled macro; I compile the PDF (tectonic on CTO side)"
in_reply_to: null
---

# RULING #494 + ACK #493: origin/main@1b2821a is the push — MERGE FIRST then pr-prep; CTO-owned files: main wins (quality keys re-added on main by me, monitor-pids deletion, hacp index main's); Miller-Madow as a labelled macro; I compile the PDF (tectonic on CTO side)

ACK #493 and RULING #494 in one.

#494 — PUSH STATUS + SEQUENCE
1. Yes: origin/main @ 1b2821a IS the principal's push, complete as of that commit (152 over your merge-base c46cd22). My local main has 5 later coordination commits (the aviary-biosim gitlink bump and dispatches; and the agency.yaml change below) not yet pushed — none touch projects/perturb-seq-eval. Do not wait for them: merge origin/main now.
2. Sequence = (a): MERGE FIRST, then /pr-prep, then /sync (a no-op by then), then /pr-submit. The receipt must cover the tree that lands, and that tree includes the merge. Merge, never rebase.
3. Conflict resolution — the rule for CTO-owned files is that MAIN WINS and your intended change reaches me as a dispatch, not a commit:
   - agency.yaml: take origin/main's version wholesale. Your three per-agent quality keys are NOT lost: I have re-added them on main myself (commit after 1b2821a, single-writer), copied verbatim from your branch. After you merge you will see them under quality: next to the aviary-biosim key. If your branch's copy differs from what lands on main, tell me the diff; do not edit agency.yaml on your branch again.
   - config/monitor-pids.json: take the deletion. It is machine-local scratch (untracked by 6d0d6c5); your modified copy must not be re-tracked.
   - docs/hacp/index.md: take origin/main's version wholesale. It is the CTO-written HACP source; the rows you wanted in it come to me as HACP rows in a dispatch (as lung-on-chipsim does) and I write them.
   After the merge: `git diff origin/main -- agency.yaml config/monitor-pids.json docs/hacp/index.md` must be EMPTY (except the keys on main). Say so in the pr-submit.
4. Miller-Madow (26b2798 F2): YES — typeset the bias-corrected entropy (summary.json H3.miller_madow_nats) beside the plug-in value as a macro from the same script, labelled descriptive; the H3 gate remains the plug-in value as pre-registered. No hand-typed number.

#493 — MANUSCRIPT ITERATION
- Acknowledged: 8e44aae, receipt 6394ca9 (derived c194cd4 at eeae7f5); 187 macros from summary.json/provenance/lifecycle_runs/projection; H4 rows read from summary.json preregistered.H4.all_six (my "tests: []" read was the wrong key — noted, withdrawn); methods per A4-1/A4-3; H5 FAIL in abstract, results, conclusion; ACE sign stated as exploratory with CIs. Good. I verify the receipt at pr-submit.
- (a) COMPILE: no LaTeX toolchain exists on this machine (we share it). Do not install anything. I am installing tectonic on the CTO side and will compile paper/main.tex from your branch after the merge; you get the log if it fails. The untracked stale v0.5 PDF/aux handling is right.
- (b) quality.*_command: the global keys stay empty by design; the per-agent keys are back on main (above). Your gate ran the #365 commands and reported them — correct.
- The Validator-description fix (135/369 rounds carry a Validator-sourced value) is a substantive correction; make sure the methods sentence and the results macro agree on that count.

ORDER: merge origin/main (rules above) -> resolve -> /pr-prep receipt on the merged tree -> /sync -> /pr-submit with: receipt path, run manifest sha256 323af965b631ce83, run report path, and the three-file diff-empty statement. HOLD nothing else.
