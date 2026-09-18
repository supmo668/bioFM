---
type: plugin-feedback
target: aiadlc plugin (aiadlc-plugins)
plugin_version: 0.56.0
reporter: biofm/matthew-mo/cto
date: 2026-09-17
scope: plugin / operating-system behavior — NOT repo/app work
---

# Feedback filed from a worktree never reaches the trunk and stays invisible

Found while auditing this log for duplicates, corroborated independently by the
aiadlc CTO session against a second repo. **This defect determines whether any
other entry in this log is findable**, which is why it is filed alone.

## 🔴 1. `/feedback` writes to the current branch, so a worktree quarantines its own findings

**File:** `skills/feedback/SKILL.md` — "Where it goes (isolated, on purpose)" and
step 4 ("Commit it as a coordination artifact (`/coord-commit`)")

**Symptom.** Feedback filed from a worktree lands in that worktree's branch. Until
the branch merges, no one reading the trunk can see it — and nothing anywhere says
so. The author sees a committed file and reasonably concludes it is recorded.

**Measured, in two repos, with the same query:**

```
                              in any ref   on HEAD   invisible
bioFM                             21          18         3
SyntropyHealth-Applications      141          81        60
```

bioFM's three, all on the `lung-on-chipsim` branch:

```
.claude/aiadlc-feedback/2026-08-30-catchup-false-clear.md
.claude/aiadlc-feedback/2026-09-14-results-reported-by-commit-not-dispatch.md
.claude/aiadlc-feedback/2026-09-15-iteration-complete-dispatch-type-workitem-format-receipt-scope.md
```

Eight of the other repo's invisible files are dated 2026-09-10 or later, so this is
not an archive of merged-and-renamed material — it is current feedback. One of them,
`2026-09-17-detached-worktree-mints-identity-head.md`, was filed **today** and is
already invisible.

**Root cause.** The skill argues — correctly — that plugin feedback is
"cross-cutting and not a per-workstream artifact", and on that basis deliberately
keeps it OUT of `usr/<principal>/.../dispatches/`. It then specifies a path
(`.claude/aiadlc-feedback/`) resolved against the *current working tree*, and a
commit into the *current branch*. A worktree branch is a per-workstream location.
The skill's own reasoning defeats its own implementation.

**Why this is worse than the burial problem it compounds.** A finding buried as
item 3 under someone else's title is a *regex* problem — a better instrument finds
it. A finding on an unmerged branch is a *ref* problem, and no amount of reading a
checkout improves it. Both of the scans that missed this (a title scan here, a
working-tree walk in the aiadlc session) were measuring a checkout and calling it a
corpus.

**The worst-case shape, which actually happened.** `eafe558` on `lung-on-chipsim`
is a well-formed 40-line report of three framework defects. The CTO of the day
acknowledged it in the reply to dispatch #110 with *"the durable record is your
feedback file (eafe558); nothing further needed from you."* Everyone did everything
right, and everyone was wrong: the file has been invisible to every trunk reader
since 2026-09-15, and the branch holding it is 54+ commits ahead under a
push-and-land freeze imposed on unrelated gating grounds. **Feedback is hostage to
a hold that has nothing to do with it.** One defect in that file — `dispatch`'s
`VALID_TYPES` omitting `iteration-complete`, which `skills/iteration-complete/SKILL.md:187`
prescribes — is still live in 0.56.0 and was two rounds away from being re-fixed
from scratch by an agent that could not see the report.

**Fix.** Resolve the **main checkout's** feedback path and write there, whichever
worktree invoked the skill — `git rev-parse --git-common-dir` gives the shared
`.git`, and its parent is the main checkout. Feedback is cross-cutting by the
skill's own argument; it should live at a cross-cutting ref. A warning instead of a
relocation is not sufficient: a warning is a thing people learn to scroll past, and
the failure is silent precisely because everything looked successful.

Add the audit query to the skill, since scanning a checkout cannot answer the
question:

```bash
git log --all --diff-filter=A --format='' --name-only -- '*aiadlc-feedback/*' \
  | grep -E 'aiadlc-feedback/.+\.md$' | sort -u          # every file ever filed
git ls-files '*aiadlc-feedback/*' | sort -u              # what a trunk reader sees
# the difference is the quarantined set
```

**Effect once applied.** Feedback filed from any worktree is visible to every
reader immediately, and the log stops being a per-branch artifact that reports on
cross-cutting tooling.

**Secondary, same root:** the `/feedback` skill's "append to today's file, one entry
per finding" guidance also produces multi-finding files under single titles — this
log carries ~24 findings across 18 files, in three incompatible burial conventions
(numbered `🔴 1.`, lettered `(a)`–`(d)`, and bare prose such as *"A second defect the
workaround exposes…"*). One defect per file, with the defect in the filename. Owned
by the aiadlc CTO session, recorded there as owed.

**Status:** open — the `/feedback` fix is owned by the aiadlc CTO session
(`aiadlc-e4`), recorded as owed, not yet started. bioFM's three quarantined files
are NOT copied to `main` deliberately: same-path adds would conflict when
`lung-on-chipsim` merges, and that branch is another session's lane.
