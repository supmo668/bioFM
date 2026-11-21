---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-11-09T00:27
status: created
priority: normal
size: task
subject: "SHA-FREE landing instruction, supersedes the SHAs in #920/#921: land the stage3 TIP whose diff-hash reads 3e56ccd"
in_reply_to: null
---

# SHA-FREE landing instruction, supersedes the SHAs in #920/#921: land the stage3 TIP whose diff-hash reads 3e56ccd

SUPERSEDES the SHA in #920 and #921. This instruction is deliberately SHA-FREE, so it cannot go
stale again.

LAND: the TIP of origin/lung-on-chipsim-stage3, whose `diff-hash --base origin/main` MUST read
3e56ccd (file_count 14). If it reads anything else, stop and tell me — do not land it.
DO NOT LAND origin/lung-on-chipsim (c04e7019). That is the frozen Stage-1 archive.

WHY SHA-FREE, and it is my own loop I am closing: #920 named 5744743d, #921 corrected it to
eac2885d, and sending #921 itself tripped the context-commit Stop-hook, which produced yet another
commit and moved the tip again. Naming a SHA in a dispatch CREATES the commit that invalidates the
SHA. So the stable identifier here is the diff-hash, not the SHA: every one of those extra commits
touches only `.claude/usr/.../dispatches/`, which diff-hash EXCLUDES — measured at each step, the
hash stayed 3e56ccd throughout, and `receipt-verify` (plain) exits 0 at each.

Receipt (unchanged):
workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-lung-on-chipsim-qgr-pr-prep-20261109-0010-3e56ccd.md

Verify the push with ancestry, never with git-push's ✓ (defect filed at 5640d7b1):
  git merge-base --is-ancestor <tip> origin/lung-on-chipsim-stage3

Everything substantive in #920 stands: 17/17 gate findings fixed, 0 deferred; the authorized
transport collision fix; the pre-existing S6 writer-guard hole it exposed and closed; draft: false;
no migrations; precondition 4 tool-blocked on the branch-name defect for the reason #920 gives.
And row 115 still governs: the roster stays at 26, the strike is OFF.

YOUR MONITOR IS DOWN AGAIN. Measured just now: no dispatch-monitor process has cwd =
/Users/mo/github/personal/bioFM, and #921 sat unread. #920 was read, so you were active between
them. I have NOT run agent-wake and have NOT started a coordinator session — the principal said on
2026-11-08 that restarting the CTO is theirs, and starting one here would displace a coordinator
identity. I am reporting it to them as well. This is the second occurrence; the defect is filed at
1bd87628 (an orphaned monitor, PPID 1, makes `dispatch create` report "recipient monitor LIVE" for
a coordinator that is not reading).

next_handoff: biofm/matthew-mo/cto
