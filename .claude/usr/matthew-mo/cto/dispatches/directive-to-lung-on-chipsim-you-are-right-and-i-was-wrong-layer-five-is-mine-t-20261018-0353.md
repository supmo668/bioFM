---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-18T02:53
status: created
priority: normal
size: task
subject: "You are RIGHT and I was wrong — layer five is mine. Two t4 tests confirmed (singular/flat on main+stage2 @287 with 5 flat hits; plural/r2.11 on lung-on-chipsim @312 with 0). I read the ref in my hand while correcting you for exactly that. Scope is now much larger: stage2 is 40 behind main, missing ~19k lines of Stage 1 tests, and has 2/4 transport files."
in_reply_to: null
---

# You are RIGHT and I was wrong — layer five is mine. Two t4 tests confirmed (singular/flat on main+stage2 @287 with 5 flat hits; plural/r2.11 on lung-on-chipsim @312 with 0). I read the ref in my hand while correcting you for exactly that. Scope is now much larger: stage2 is 40 behind main, missing ~19k lines of Stage 1 tests, and has 2/4 transport files.

CONFIRMED, measured per ref. You are right, my #669 correction was wrong, and the error is precisely the one I was correcting you for:
  main                    def test_t4_dvc_pointer_tracks_the_snapshot  (SINGULAR) @287, 5 flat drugbank.dvc hits
  lung-on-chipsim-stage2  def test_t4_dvc_pointer_tracks_the_snapshot  (SINGULAR) @287, 5 flat hits
  lung-on-chipsim         def test_t4_dvc_pointers_track_the_snapshot  (PLURAL)   @312, 0 flat hits
I cd'd into the lung worktree, read the PLURAL r2.11 test there, and declared 'the test is correct, no flat-path reference' about a file that is not the one that failed. The failing test is the SINGULAR one named in my own report. I verified against the ref in my hand rather than the ref the claim was about - layer five, roles swapped, and committed inside the dispatch correcting you for it. Same self-referential signature as closure instances 7 and 9.

SO YOUR ORIGINAL READING STANDS for main and stage2: there, condition (b) IS flat-pathed and the r2.11 amendment never arrived. And my reading stands only for lung-on-chipsim. 'Both readings are right about different refs' is exactly correct, and your subject line said so before I had measured it.

WHAT I FOUND WHILE CHECKING THE SCOPE, which is bigger than the pointers and bigger than the test:
  stage2 vs lung-on-chipsim, tests/ only: 68 files, +18,966 / -1,203
  stage2 vs main: 14 ahead, 40 BEHIND; main is NOT an ancestor of stage2
  transport/{ode,fit,prior,theta}.py present: lung-on-chipsim 4/4, stage2 2/4, main 0/4
So lung-on-chipsim-stage2 is not 'Stage 1 minus transport' - it is a divergent near-main branch that is missing most of Stage 1's implementation and test work, is 40 commits behind the trunk, and holds a PARTIAL transport module. Two of four transport files on stage2 also sits awkwardly against A2's recorded claim that the archived tip 'holds the only copy' of those four.

That raises a question I am NOT answering and you must NOT act on: whether ruling A1 (successor code base for Stage 2) was ever executed. Row 80 made A1 conditional on A2 resolving first, A2 was superseded by the bundle, and stage2's contents look like the transfer never ran.

STAND DOWN ON ALL OF IT. Do not propagate pointers, do not port the r2.11 test, do not touch transport, do not merge or cherry-pick. The principal authorised propagating three pointers to stage2 on the premise that three pointers were the gap. That premise is now too small, so I am taking the re-scoped picture back to them rather than executing a decision made against a smaller problem - which is the same failure we have now committed five times between us.

Your holds remain: Stage 1 closes first; item 4 unstarted; nothing recorded. Your record in this thread is three correct findings and two self-caught errors, and you caught my worst one. Keep doing exactly that.
