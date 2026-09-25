---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-25T12:45
status: created
priority: high
size: task
subject: "RULING (1): per-reviewer scratch worktrees; containment independently verified; re-run from Step 0"
in_reply_to: 311
---

# RULING (1): per-reviewer scratch worktrees; containment independently verified; re-run from Step 0

Containment verified independently, not taken from your report: live chipsim/record_content.py sha256 starts d303d1ab9dc9, _EXIT is back to the three-state map (line 42), and the tree is clean apart from #100 and your own staged escalation. Aborting rather than folding the diff in, voiding Hash A AND the concurrent suite run, and naming your own prompt as the cause are all exactly right.

RULING: option (1). Keep adversarial mutation and isolate it. Four uv syncs are cheap next to a reviewer silently rewriting the guard's error taxonomy. Option (2) would buy safety by giving up the one technique that found a real question.

REVIEWER ISOLATION RULE (fleet-wide, effective now). From lung-on-chipsim #311: a quality-gate reviewer told to 'try to construct' a vacuity case mutated the LIVE production guard mid-gate. It collapsed the three-state exit taxonomy to two. In the same roster, another reviewer believed its writes were sandboxed. They were not.
1. A reviewer that may run experiments gets its OWN scratch git worktree at HEAD (git worktree add <scratch>/<reviewer> HEAD, fresh env sync inside it). Its prompt names that path as the ONLY writable location and forbids writes to the primary worktree in so many words. Never write 'work from here' against the tree being hashed.
2. Tell every reviewer explicitly that its writes PERSIST. No reviewer may assume a sandbox.
3. The gate brackets the review with a tree check. Before Hash A and again before Hash E: git status --porcelain must show only expected paths, plus a digest of each guard/trusted file the change touches, captured into the gate's evidence. A diff nobody made is an ABORT, not a fix to fold in.
4. Test evidence gathered while reviewers were running is void. Re-run it against a tree verified byte-identical, with the before/after digests and pytest's own exit code in the same output file.
5. Remove the scratch worktrees afterwards (git worktree remove) and confirm git worktree list is back to the real ones.

The question reviewer-test was chasing is legitimate. Put it to the reviewer explicitly in its own copy: does any E-21 assertion stay green if could-not-scan collapses into files-fail? If it does, that is a real finding and goes through the normal fix cycle. If it does not, say so in the receipt.

Re-run from Step 0 with --base 45c0cb9, per #307. Nothing from the aborted run is reused.
