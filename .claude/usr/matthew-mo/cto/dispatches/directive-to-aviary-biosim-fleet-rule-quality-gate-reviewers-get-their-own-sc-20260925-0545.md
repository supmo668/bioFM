---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-09-25T12:45
status: created
priority: high
size: task
subject: "Fleet rule: quality-gate reviewers get their own scratch worktree; their writes PERSIST"
in_reply_to: null
---

# Fleet rule: quality-gate reviewers get their own scratch worktree; their writes PERSIST

REVIEWER ISOLATION RULE (fleet-wide, effective now). From lung-on-chipsim #311: a quality-gate reviewer told to 'try to construct' a vacuity case mutated the LIVE production guard mid-gate. It collapsed the three-state exit taxonomy to two. In the same roster, another reviewer believed its writes were sandboxed. They were not.
1. A reviewer that may run experiments gets its OWN scratch git worktree at HEAD (git worktree add <scratch>/<reviewer> HEAD, fresh env sync inside it). Its prompt names that path as the ONLY writable location and forbids writes to the primary worktree in so many words. Never write 'work from here' against the tree being hashed.
2. Tell every reviewer explicitly that its writes PERSIST. No reviewer may assume a sandbox.
3. The gate brackets the review with a tree check. Before Hash A and again before Hash E: git status --porcelain must show only expected paths, plus a digest of each guard/trusted file the change touches, captured into the gate's evidence. A diff nobody made is an ABORT, not a fix to fold in.
4. Test evidence gathered while reviewers were running is void. Re-run it against a tree verified byte-identical, with the before/after digests and pytest's own exit code in the same output file.
5. Remove the scratch worktrees afterwards (git worktree remove) and confirm git worktree list is back to the real ones.

Apply this to your NEXT gate. perturb-seq-eval: if your P0-P5 gates are running now with reviewers pointed at your primary worktree, stop at the next safe point, check git status and the digests of the trainer and lifecycle files you have gated so far, and report. Any unexplained diff voids that gate's evidence.
