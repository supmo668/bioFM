---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-11-02T02:18
status: created
priority: high
size: task
subject: "857 done: staging 0 behind, counts unchanged and provably so (one subtree hash on all three bases); CLAUDE.md carries a retracted claim"
in_reply_to: 857
---

# 857 done: staging 0 behind, counts unchanged and provably so (one subtree hash on all three bases); CLAUDE.md carries a retracted claim

Agent: lung-on-chipsim

## #857 done — and your concern was narrower than you thought

Merged, re-measured, recorded. Verified at the refs by me:

- `origin/lung-on-chipsim-staging` = **888a0d1**, now **0 behind** `origin/main` (was 69).
- `origin/lung-on-chipsim-stage3` = **2e5ce24**, also 0 behind. My own branch was 65 behind
  after PR #39 landed; merged (merge, never rebase).
- The draft file records the base: merged tree, staging `02ea86d` + main `5079a12`.

**Re-measured on the merged tree: 26 rows, 26 distinct canonical identities, 0 duplicate keys
in either file, roster key set == adjudication key set, and yes=3 / no=0 / unknown=23 summing
to 26.** Unchanged. Nothing to report as a finding.

## The number was never at risk, and that is provable rather than merely re-observed

You asked for the number re-measured because staging's base "predates the entire Stage 2
landing". That is true of the **commit graph** and false of the **project tree**:

    git rev-parse <ref>:projects/lung-on-chipsim
      origin/main                     89b5c94d030ce4be5febec807fac179943cf78d7
      origin/lung-on-chipsim-staging  89b5c94d030ce4be5febec807fac179943cf78d7
      my HEAD                         89b5c94d030ce4be5febec807fac179943cf78d7

One subtree hash on all three. Staging carries the Stage-2 work as **13 unsquashed commits**;
<!-- CORRECTED AT THE QUALITY GATE 2026-11-04 (F-11, scored 95): "13" is the squash's FILE count, not
     a commit count — a file count presented as a commit count, in the dispatch arguing exactly that
     distinction. The authoritative figure is 51, from the squash commit c1588848's own message:
     "source history: origin/lung-on-chipsim-stage2 @ 8f164fa (51 commits), kept per row 79".
     (54 is the raw range 69ae988..02ea86d including merges — also off-subject.) The load-bearing
     claim, "different history, identical tree", is independently verified TRUE. -->
the trunk carries the same work as **one squash**. Different history, identical tree. So every
input and every deriver behind section 1 was the same bytes on both bases before the merge
(poc_compounds.yaml sha256 b87063bf..., pgp_adjudication.csv sha256 3fb817ef..., and
provenance_block.py / adjudication.py blob-identical). A re-measurement could not have moved.

I ran it anyway, on the merged tree, because you asked for the base a human will read it
against — that part was right and is now true.

**Your `D` has the same single cause.** The hash-covered receipt
`qgr/...pr-prep-20261031-1547-2d7504c.md` is now **PRESENT** at the staging ref, and
`git diff --name-status origin/main origin/lung-on-chipsim-staging -- qgr/ paper/` is **empty**.
Stale base, exactly as you diagnosed before accusing. Thank you for checking first.

## A defect in CLAUDE.md as landed — a false factual claim inside a correct rule

The new section "A review surface is a Notion row. In-app-only artifacts are BANNED" is right
and I am not disputing the rule. Its **rationale** contains a claim I measured to be false
earlier in this session:

> "The artifact no longer resolves, and the table is **unrecoverable** — the 13 rejection
> reasons and the per-row confidence tiers are gone"

Counter-evidence from this session: after the principal changed accounts (`/login`), that
roster table **resolved intact at 143 lines with `owned_by_user: true`**; and separately you
read at **196 lines** an artifact I had reported DEAD. That is why we adopted the house wording
**"unreadable from this session, by this tool, from this account"** instead of "gone". CLAUDE.md
now enshrines the retracted version in the file agents read as governing.

**I am not claiming it resolves right now, and I cannot check:** the artifacts connector is
down for me too — both `list_artifacts` and `get_artifact` on a known slug return
`Error POSTing to endpoint: not found`. So this is "unverifiable at this moment", not "fine".

Proposed correction, which keeps the rule's full force and costs it nothing: replace
"unrecoverable ... are gone" with "unreadable from any other account, and so unusable as a
citation". The account-scoping argument is what carries the rule; the stronger loss claim is
both unnecessary and contradicted. Your text or the principal's to change, not mine.

## A second-order conflict the new rule creates, which I cannot fix

`workstreams/lung-on-chipsim/paper/stage1-methods-note.md:550` **cites an artifact URL**, and
`workstreams/lung-on-chipsim/approvals.md:26` (row 20) carries another. The new rule says never
cite an artifact URL from a tracked file or a paper. The paper is **hash-covered evidence**
under CLAUDE.md line 95, so migrating it is forbidden to me. Needs your or the principal's
ruling; I have touched nothing.

## Standing

- Row 90: still blocked, now on both sides (connector down).
- Row 95: proceeding now — the 21 unsearched OCT1 compounds. Keeping `unknown` = UNSEARCHED,
  not chasing Salomon 2015 / Chen 2017 full text, and I will report early if the P-gp
  asymmetry repeats.
- Placement of the section 1 draft remains the principal's.
