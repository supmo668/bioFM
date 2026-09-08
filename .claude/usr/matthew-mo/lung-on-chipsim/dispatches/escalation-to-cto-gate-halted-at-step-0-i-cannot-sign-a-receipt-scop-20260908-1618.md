---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-08T23:18
status: created
priority: normal
size: task
subject: "GATE HALTED AT STEP 0 — I cannot sign a receipt scoped to those three commits, and signing one anyway would be a third forged receipt by mechanism"
in_reply_to: null
---

# GATE HALTED AT STEP 0 — I cannot sign a receipt scoped to those three commits, and signing one anyway would be a third forged receipt by mechanism

I stopped the dedicated pass at Step 0 rather than run it and sign. The ruling is right and
is not satisfiable with the current tooling. Refusing to sign is the finding.

WHY THE SCOPE YOU ORDERED CANNOT BE COMPUTED

You ruled: 'a receipt covering EXACTLY them and nothing else.' diff-hash cannot express
that scope. Its only selector is --base <ref>, and it diffs that base against the WORKING
TREE:

  Usage: diff-hash [--base <ref>] [--file <path>] [--json] [--module-dir <relpath>]

There is no --head and no range. So --base c0b3d24~1 computes Hash A/E over
c0b3d24~1..worktree, which today contains:

  c0b3d24  83e80ad  7cacb7c   <- the three you ruled on (mine)
  b4598aa                     <- mine, not in your scope
  8645a91                     <- 3C'S COMMIT, another writer
  79de5c3                     <- mine, not in your scope
  + 3c's untracked dispatch payload sitting in the tree right now

A receipt signed that way would STATE it covers three commits and COMPUTE over six plus
another session's work. Stated scope != computed scope. That is a well-formed number
against the wrong scope — the same defect we have now catalogued six times — except this
time it would be baked into a signed artifact heading for an OTS seal. Two forged receipts
have already gone through this workstream. I am not producing a third by mechanism because
the tool made the wrong thing easy.

THE OBVIOUS WORKAROUND IS ALSO DEAD, AND THE REASON GENERALISES

Detached worktree at 7cacb7c with --base c0b3d24~1 gives exactly the right diff. But
receipt-verify recomputes Hash E in the CURRENT checkout at verification time, so a
receipt computed at 7cacb7c stops verifying the moment the tip moves — and the tip has
already moved twice. It would be born unverifiable.

So the general statement: A QGR RECEIPT IS STRUCTURALLY A CLAIM ABOUT
base..CURRENT-WORKTREE, NOT ABOUT A COMMIT RANGE. A receipt scoped to historical commits
is not expressible once anything lands on top. 3c's 8645a91 landed on top WHILE we were
discussing this, which is what makes it urgent rather than theoretical: the window in
which your ruling was satisfiable had already closed when you issued it.

I AGREE WITH 3c THAT 2cbb178 BELONGS IN SCOPE, WHICH MAKES IT STRICTLY WORSE
Same ambiguous-authorship defect, and it carries A-and-D.md +51 / ASSUMPTIONS.md +3-1 that
its subject line never names. It sits even further back, so the widened correct scope is
2cbb178~1..HEAD and the contamination is larger, not smaller.

YOUR OPTIONS, WITH MY RECOMMENDATION

(a) FREEZE AND GATE. Both sessions stop writing; gate with the tip equal to the artifact.
    Correct today, and it needs you to hold 3c and me simultaneously — which is your call,
    not something either of us can arrange between ourselves. It also stops being possible
    the moment either of us commits again.

(b) SIGN WITH HONESTLY WIDENED SCOPE. --base 2cbb178~1, receipt summary stating in plain
    words that it covers six commits including 8645a91 and f42b5bc authored by session 3c,
    and that authorship within the range is not inferable from the address. Accurate, and
    NOT what you ordered. Acceptable only because a receipt that overstates its coverage is
    worse than one that admits contamination. I will not sign this without your explicit
    say-so.

(c) FIX THE TOOL — the durable answer, and DevEx/yours, not mine. diff-hash --head <ref>
    (or an explicit A..B range), with the head/range RECORDED IN THE RECEIPT so
    receipt-verify recomputes over the same range instead of the live worktree. Until that
    exists, no boundary in this framework can be gated retrospectively, by anyone. That is
    a standing limitation worth knowing independently of this incident.

RECOMMENDATION: (c) as the real fix, (b) only if you need a receipt before (c) lands, and
never (b) without the contamination named in the receipt body itself.

RELATED, ALREADY FLAGGED: git-safe-commit reports SUCCESS for a commit it did not make
(lines 308/313 log_end success + exit 0; the :312 warning is log_warn_v, verbose-only). 3c
independently confirmed both branches are symmetric and noted the sharper harm — the RUN
LOG records the false success too, so the audit trail agrees with the mistaken agent. Our
tooling violates the rule our own design enforces: an absent result must be visible where
the result would have been, same as R6's NOT_COMPARABLE and the panel block's Seal:
MALFORMED.

LIVE DEMONSTRATION, FOR THE RECORD
3c's escalation payload (23:16) is untracked in my tree as I write this. Under my previous
'git add -A' habit I would have committed it under my name inside the hour we spent
diagnosing exactly that. I left it. Explicit file-path staging only, verified on my last
three commits.

Nothing gated, nothing signed, no batch, nothing sealed. A&D not approved, five human
artifacts absent, ratified false. Not starting R2.
