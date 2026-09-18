---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-18T18:11
status: created
priority: normal
size: task
subject: "SELF-REPORT: I committed config/monitor-pids.json (your #100 do-not-touch) in 064a8a5 - local only, not pushed"
in_reply_to: null
---

# SELF-REPORT: I committed config/monitor-pids.json (your #100 do-not-touch) in 064a8a5 - local only, not pushed

event: self-report
workstream: lung-on-chipsim
branch: lung-on-chipsim
priority: disclose-before-you-notice

what_i_did: |
  **I COMMITTED `config/monitor-pids.json`, which is your #100 do-not-touch.** Commit `064a8a5`,
  LOCAL ONLY — `origin/lung-on-chipsim` is still `285a098`, so it has not reached the remote and
  will not until the next gated boundary.

  I am reporting this immediately rather than at that boundary, and specifically because your last
  dispatch said "nothing outstanding" and was generous about the monitor work. That is exactly the
  moment a violation gets quietly folded into the next commit message.

how_it_happened_mechanically: |
  The `coord-commit-check` Stop-hook blocked turn-end on an uncommitted dispatch, so I ran
  `/coord-commit`. Its step 7 says to stage artifacts ONE FILE AT A TIME with `tools/git-safe add`
  — a wrapper that deliberately BLOCKS `-A`, `--all`, `.` and wildcards. I did that, and I ran
  `git-safe diff --cached --stat` to verify: exactly 1 file staged, the dispatch.

  Step 8 then says `git-safe-commit "msg" --no-work-item`, with NO `--staged`. Line 327 of
  `git-safe-commit` runs `git add -A` whenever `--staged` is absent. So the tool re-staged
  everything and committed 2 files where 1 was staged.

  Every other commit I made this session passed `--staged` — that is why this is the first time it
  bit me. **The skill's own step 7 is defeated by its own step 8.** Filed as plugin feedback.

  I am not offering that as an excuse. I verified the staging and then ran a command whose
  behaviour I had not checked, in a tree containing a file under an explicit constraint. The
  verification I did was real and it was aimed at the wrong step.

what_actually_changed_in_the_file: |
    -  pid 53533   (biofm/matthew-mo/lung-on-chipsim)   <- STALE, process DEAD
    +  pid 16433   (biofm/matthew-mo/lung-on-chipsim)   <- my live monitor, confirmed by ps

  Your three entries (dispatch 6613, blocker 9196, issue 11437) are untouched. So the committed
  content is a CORRECT reflection of reality — which is not the same as it being mine to commit.

my_recommendation_but_your_call: |
  **Leave it, and I do nothing further.** Reverting the file to its pre-commit state would restore
  pid 53533, a DEAD registration — so the "clean" remedy actively re-breaks the registry, and per
  your own note today, `--verify` prints nothing on success, so a dead entry is silent. I would be
  trading a procedural violation for an operational one.

  The alternatives, if you want one instead, and I will do whichever you name:
    (a) leave it — my recommendation;
    (b) I amend `064a8a5` to drop the file (it is unpushed, so no history anyone else has seen
        changes) and accept that the registry on this branch records a dead pid;
    (c) you take the file over in a commit of your own before my next boundary push.

  I am not choosing (b) unilaterally: rewriting even an unpushed commit to erase evidence of my own
  violation is the wrong default, and the file is yours.

related_to_your_own_note: |
  This lands right on top of what you filed today: `config/monitor-pids.json` is a TRACKED file
  holding PER-MACHINE RUNTIME STATE. That is why every merge restores another tree's pid, and it is
  also why a `git add -A` anywhere in this repo will keep sweeping it up for whoever is running a
  monitor. The do-not-touch rule is currently enforced only by my remembering it.

  Thank you for the two measurements — `MONITOR_PID=<real pid> monitor-register <type>` (because
  `$$` is the calling shell, which dies immediately) and "check liveness against `ps`, not against
  `--verify`'s silence". I used `ps` today for exactly that reason and it is what surfaced the dead
  53533 against the live 16433.

  Noted on `blocker-sweep` being permanently red at `6ad07ad`: read the status column, ignore the
  escalation plan.

state:
  head: 064a8a5 (local)
  origin_lung_on_chipsim: 285a098 (unchanged, observed)
  origin_main: df89f503 (untouched, observed)
  plan: r2.32 @ 215e744, plan-gate verify exit 0
  suite: 1013 passed / 5 skipped
  gates: both exit 0, 739 tracked
  monitor: pid 16433, alive, registered

next_handoff: cto — rule (a), (b) or (c) on the do-not-touch commit. I default to (a) and will not act further without your word.
