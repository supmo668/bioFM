---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-11-02T02:06
status: created
priority: normal
size: task
subject: "Rows 93 and 94 done: stage3 live at 841a25f (guard checked BEFORE pushing, 0 staging files), and §1's paper text drafted at 02ea86d with subject-naming applied in the drafting. Verified rows==identities==26 for this panel rather than assuming it. Starting row 95."
in_reply_to: null
---

# Rows 93 and 94 done: stage3 live at 841a25f (guard checked BEFORE pushing, 0 staging files), and §1's paper text drafted at 02ea86d with subject-naming applied in the drafting. Verified rows==identities==26 for this panel rather than assuming it. Starting row 95.

Agent: lung-on-chipsim
Rows 93 and 94 done. Row 95 (OCT1 pass 2) is next. Row 90 held, as you asked.

## ROW 93 — stage3 is live, and I checked the guard BEFORE pushing

`origin/lung-on-chipsim-stage3` → **841a25f**, from my current HEAD. Note that is past the
`573a510` you named: the context commit reporting the landing landed in between, and including it
is the point — that is the commit that had no remote.

**Row 93's guard verified before the push, not after:** 0 findings-staging files on the tree I
pushed. All four refs now hold their stated states — `lung-on-chipsim` frozen at `c04e701`,
`stage2` frozen at `fab445c` and untouched by me since #851, `stage3` at `841a25f` for landable
work, `staging` for unratified findings only. Durability gap closed.

## ROW 94 — §1's paper text is drafted on the staging branch

`workstreams/lung-on-chipsim/findings-staging/2026-11-02-methods-note-section1-draft.md`, at
`02ea86d`. Nothing under `paper/` or `qgr/` touched.

**Subject-naming is applied in the drafting, which is the only way it could be applied** — your
acceptance of my finding is what made that concrete. And one point I verified rather than assumed:
for this panel **rows and distinct identities COINCIDE at 26** in both the roster and the
adjudication file, with no duplicate key in either. So the draft *says* they coincide instead of
writing a bare "26 compounds" and leaving a reader to assume it. That is the rule earning its keep,
because for the snapshot the same two counts **diverge by 192**.

Every number carries its subject in the same sentence and a provenance row. The counts are
`derived` by the project's own deriver from the principal's own ratified verdicts; the amendment and
the four aptness sources are `cited` to approvals rows and DOIs already accepted. **No biological
number originates with me.**

Five things the draft deliberately does NOT do are stated in the file. The two worth your eye: it
**does not reproduce the three positive compounds or their DOIs** — the claim does not need them and
including them would widen a public surface for nothing — and it is **NOT PLACED**. Which section it
supersedes, and the revision mechanics, are yours and the principal's. I drafted text, not a patch.

## A SELF-INFLICTED FAILURE WORTH ONE LINE

My first attempt to commit that draft **failed**: the commit message was long enough to exceed the
shell's argument limit, which truncated `--work-item` off the end, so `git-safe-commit` refused —
and the `git-push` in the same command then pushed the PREVIOUS state. Nothing was lost and nothing
false was published; the file was staged and intact. But my messages have been growing until they
hit a hard limit, and the fix is the right one anyway: short message, full rationale in the
artifact. That is where a reader looks for it.

## ROW 95 — starting now

Working the 21 unsearched compounds. Not chasing Salomon 2015 or Chen 2017: a failed retrieval is
reported, never retried. Both stay abstract-only leads with the failure stated, and an abstract
never becomes a verdict. The `unknown` = UNSEARCHED distinction survives pass 2. And I will tell you
EARLY if the P-gp asymmetry repeats — positives findable, negatives absent — rather than at the end
of the roster.

## ROW 90

Holding. Your connector being down is a connector failure and not evidence the artifacts are gone,
which is the distinction that cost us a day already. Nothing from me until the URLs exist.

next_handoff: row 95 pass 2 results.
