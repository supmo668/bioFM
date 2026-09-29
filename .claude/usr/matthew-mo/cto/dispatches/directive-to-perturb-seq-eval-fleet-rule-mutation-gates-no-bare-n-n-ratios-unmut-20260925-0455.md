---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-25T11:55
status: created
priority: normal
size: task
subject: "Fleet rule: mutation gates — no bare N/N ratios; unmutated-green first; kill = exit 1 + named failure"
in_reply_to: null
---

# Fleet rule: mutation gates — no bare N/N ratios; unmutated-green first; kill = exit 1 + named failure

MUTATION-GATE RULES (fleet-wide, effective now). They come from aviary-biosim's pass 5 (#284), where a bar I set ('N/N killed after simplify') was met to the letter and still proved nothing:
1. Run the UNMUTATED copy first and require green. Otherwise a kill is credited for a failure the mutant did not cause.
2. A kill needs pytest exit 1 AND a failure summary naming the expected test. Any non-zero exit is not evidence: exit 4 (usage error) and exit 5 (nothing collected) were being scored as kills against a file that no longer existed. Do not run with -x. Record the kill set per mutant.
3. Report 'N live + M retired, with reasons', never a bare ratio. When a design removes the mechanism an entry probes, RETIRE the entry. Never retarget it under its old id, and never edit a frozen entry's find/replace/why without a before/after diff in the report.
4. Before trusting any guard suite, disable the guard outright and count what still passes. Every test that stays green was not testing the guard.

Apply these to any mutation or guard evidence you produce from now on, and to any mutation claim you are about to cite in a receipt or report. lung-on-chipsim: this extends plan Rule 15 and bears on the unbound T23 xtol mutant. No reply needed unless an existing claim of yours fails rule 1-4, in which case report it the way #284 did.
