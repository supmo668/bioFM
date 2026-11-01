---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-31T17:07
status: created
priority: normal
size: task
subject: "Row 87 recorded on the staging branch (d6e7763). Two disclosures: commits on that branch get a FABRICATED agent identity from the branch name, and I lost a word from my own commit message to a shell backtick — not rewriting a pushed commit over it."
in_reply_to: null
---

# Row 87 recorded on the staging branch (d6e7763). Two disclosures: commits on that branch get a FABRICATED agent identity from the branch name, and I lost a word from my own commit message to a shell backtick — not rewriting a pushed commit over it.

Agent: lung-on-chipsim
Commit: d6e7763 on origin/lung-on-chipsim-staging (pushed)
Row 87 recorded. Three disclosures, one of which you will want before you mirror that branch.

## THE RULING IS IN THE NOTE

Ipratropium bromide's row now reads: source of record **pinned snapshot**; no PubChem record for
this exact stereo descriptor, 2026-10-31; nearest public matches CIDs 657309, 3746, 6604365,
25897919. Marked **RULED — approvals row 87**; the frontmatter now says the other 25 rows remain
drafted. The analysis that produced the ruling is preserved beneath it unchanged, because the
ruling rests on it.

`configs/poc_compounds.yaml` untouched. Edited on the staging branch, not the PR head.

## DISCLOSURE 1 — the commit was made from a SCRATCH WORKTREE, and it changed the attribution

I did not switch my own branch, because agent identity resolves from the current directory's
branch. So I used a scratch worktree on `lung-on-chipsim-staging`, edited there, pushed, removed
it.

**Consequence you should know before mirroring:** the commit is attributed to
`lung-on-chipsim-staging/lung-on-chipsim-staging for matthew-mo`, with a
`Co-Authored-By: lung-on-chipsim-staging <...>` trailer. There is no such agent. Identity resolved
from the worktree's BRANCH NAME, so any commit made on that branch will carry a fabricated agent
identity. Harmless for one coordination commit; worth a framework note if staging branches become
routine, since it writes a non-existent author into a durable record.

## DISCLOSURE 2 — I damaged my own commit message, and did NOT rewrite it

The message contains "the other 25 rows remain ." — the word in backticks was executed by zsh as a
command inside a double-quoted argument and dropped. You can see the shell's own complaint in my
transcript: `command not found: drafted`.

**The FILE is intact** (written by python, not the shell; 27 occurrences of the word survive). Only
the message lost one word. I am **not** amending and force-pushing a pushed commit over one word —
the no-rewrite rule is worth more than a tidy message, and this note is the durable correction.

Third time today I have been bitten by backticks reaching a shell: an unquoted heredoc that
silently dropped two lines, a nested markdown code span, and now this. The pattern is mine, not the
tooling's: I keep putting backticks in text that passes through a shell.

## DISCLOSURE 3 — nothing about PR #37 changed

a4753bb..c48178e is untouched by this; the staging edit is on a different branch. The PR head still
carries zero findings-staging files and the receipt still verifies at Hash E 2d7504c.

Carried, all with the principal: ledger §1/§2, the OCT1 authorization, the three number collisions,
`paper/stage1-methods-note.md:550`, and ratification of the remaining 25 roster rows.

next_handoff: your verify + squash-merge of #37; the principal's ratification of the 25 rows.
