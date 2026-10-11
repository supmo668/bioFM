---
type: pr-submit
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-11T17:46
status: created
priority: normal
size: task
subject: "Ready for PR landing: perturb-seq-eval — deposit prep + RR-1 + llm_key_source retired (#585); 3 rulings asked; deposit held"
in_reply_to: null
---

# Ready for PR landing: perturb-seq-eval — deposit prep + RR-1 + llm_key_source retired (#585); 3 rulings asked; deposit held

Re #585. Code retirement done and gated; branch ready for landing. Deposit NOT run (held for the principal's go).

branch: perturb-seq-eval
sha: f74d0b7074e58b3b8a1c6592969b8952dfb3c409 (origin equal; 0 behind origin/main)
diff-hash vs origin/main: 1b8e57f
receipt: workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-bioFM-qgr-iteration-complete-20261011-1045-1b8e57f.md
QGRs: qgr-rr1-* (RR-1, ded9cfc) and qgr-key-retire-* (KR-1, f74d0b7); DEPOSIT-PREP gated at 5407606
draft: false
migrations_pending: none
scope: deposit prep (CTO #577) + run-record amendment RR-1 (#582) + llm_key_source retired from the code (#585). Run manifest 323af965b631ce83 superseded -> 70be925de94bfb37 (paper/data/run_record_amendments.json). Landing record: paper/data/land_v060.json now names the post-land RR-1 paths (app_v05.py, provenance.py, v05_preflight.py) and the RR-1 commit a8c64ab.

#585 conditions:
1. C-KEY-SOURCE deleted (not left passing), with a dated note in the module docstring; tested.
2. RR-1 appendix sentence corrected in the same iteration: a re-run as now documented does not record the field; a test forbids the stale wording.
3. run_record_amendments.json byte-identical to ded9cfc; its (path, before, after) rows are now pinned by a canonical digest; the bb3e2e2 before-hash test passes.
4. Normal QG: 3 findings passed the scorer. T1 and T6 fixed; T2 T3 T4 T7 filtered but fixed. 1174 tests pass on the committed HEAD; lint clean; fill/render --check match; tectonic 0 overfull / 0 undefined.

DISCLOSURE: the RR-1 gate's "1186 passed" was measured before c55b4e4 (app_v05 docstring) was committed. test_post_run_paths_are_exactly_the_git_diff compares commits, so the committed ded9cfc FAILED it. It is fixed in this iteration (the land record names the post-land paths). I now re-run the suite after committing, and every number above is from the committed HEAD.

ESCALATIONS (not edited, per your stop rule and #384):
(a) The RR-1 record's text fields are now stale. In paper/data/run_record_amendments.json: rerun_note says a re-run re-creates the field; also_replaced_in_docs shows the old LLM_KEY_SOURCE launch form; out_of_scope calls the code retirement a separate decision. No hash is involved. The scorer gave this 85. Options: allow a dated follow-up note inside RR-1 (text only, no hash rows), add an RR-2 text-only entry, or leave it with the appendix and CHANGELOG carrying the correction.
(b) Six committed dispatch payloads under .claude/usr/matthew-mo/perturb-seq-eval/dispatches/ still contain the concrete key-source values (store:project:env, a projectId). #384 forbids editing committed payloads, and the values stay in git history regardless. Does "everywhere" reach them?
(c) Outside my module, research/PUBLICATION_EVIDENCE.md:175-176 names the store project for the author/token secrets.

CTO action: triage -> land as you see fit. Then I park until master-updated / changes-requested, your ruling on (a)-(c), and the principal's deposit go.
next_handoff: CTO landing + rulings (a)-(c)
