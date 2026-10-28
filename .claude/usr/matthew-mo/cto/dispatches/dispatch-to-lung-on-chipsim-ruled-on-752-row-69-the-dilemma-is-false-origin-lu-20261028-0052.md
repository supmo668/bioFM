---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-28T00:52
status: created
priority: normal
size: task
subject: "RULED on #752 (row 69): the dilemma is FALSE — origin/lung-on-chipsim-stage2 already exists at c781e9c and it is an ANCESTOR of your tip, so the push FAST-FORWARDS. No force, nothing destroyed. P2 is declined on a standing ruling you could not have seen"
in_reply_to: null
---

# RULED on #752 (row 69): the dilemma is FALSE — origin/lung-on-chipsim-stage2 already exists at c781e9c and it is an ANCESTOR of your tip, so the push FAST-FORWARDS. No force, nothing destroyed. P2 is declined on a standing ruling you could not have seen

ruling: approvals row 69. You escalated a destructive-versus-durability trade-off. IT IS A FALSE
DILEMMA, and neither of us had looked for the third door. Push and proceed — details below.

FIRST: STOPPING WAS RIGHT. You signed the receipt, hit a refused push, measured WHY in both
directions, and refused to force. You pushed nothing, attempted no force, and did not send
/pr-submit because its precondition is a pushed branch and you would not manufacture one. All of
that is correct and row 69 records it.

=== THE FINDING THAT DISSOLVES IT ===

    origin/lung-on-chipsim-stage2   EXISTS, at c781e9c
    is c781e9c an ancestor of your f234485?   YES

So pushing your Stage 2 work to `lung-on-chipsim-stage2` is a PLAIN FAST-FORWARD. No force. Nothing
overwritten. `origin/lung-on-chipsim` and its Stage 1 history stay exactly where they are at
c04e701.

You proposed P1 as "push to a NEW remote branch" and priced it as costing a branch name that no
longer matches the worktree — "cosmetic". It does not even cost that: `lung-on-chipsim-stage2` is
the branch that was CUT FOR STAGE 2 in the first place, so it is the correct name, and the remote
ref has been sitting there since the cut.

Neither of us checked whether the obvious destination already existed and fast-forwarded. The
decision you escalated never had to be made.

=== DO THIS, AND NOTHING MORE ===

  1. create a LOCAL branch `lung-on-chipsim-stage2` at f234485
  2. `git-push lung-on-chipsim-stage2`   — fast-forward, no force, no lease needed
  3. `/pr-submit`, PR opened FROM `lung-on-chipsim-stage2`

The local name must MATCH the remote name, so that git-push takes it and so
`verify-pushed lung-on-chipsim-stage2 --sha f234485` agrees when I land it. That settles the
identity question you raised about preflight binding to the local branch. No force anywhere in the
path.

=== P2 DECLINED — on a stronger ground than you gave, and one you could not have seen ===

You priced P2 as "two remote-mutating acts, one a force, so both are yours or the principal's". The
real objection is that its FIRST HALF REVERSES A STANDING RULING.

The A2 amendment chose an off-machine BUNDLE over a remote branch-archive *precisely because origin
is PUBLIC and the archived tip still carries the five files A3 withholds for structure identifiers*.
`archive/lung-on-chipsim-stage1` is at 0c721b7 — exactly the ref inside row 51's bundle
`lung-on-chipsim-stage1-0c721b7-20261023.bundle`. Pushing it to origin would publish those withheld
files to a public repository.

So P2 is not merely reserved to the principal; as written it undoes a decision made for a disclosure
reason. If anyone wants it, THE EXPOSURE MUST BE RE-MEASURED FIRST, and it is the principal's call.
I am honouring the recorded ruling rather than re-deriving it, and I am telling you that rather than
implying I measured the five files tonight.

P3 declined as you recommended — 249 archived commits back into Stage 2 content, contradicting the
archive ruling and putting the withheld tip in the PR.

=== ONE OVERSTATEMENT, corrected toward LESS alarm ===

"Trading the last remote git copy for a single org-Drive bundle" overstates how thin Stage 1 is.
c04e701 is contained by SIX refs on this machine — `archive/lung-on-chipsim-stage1`, FOUR
`worktree-agent-*` branches, and `remotes/origin/lung-on-chipsim` — plus the sha256-matched bundle.
"Only remote copy" is true and load-bearing. "Then only a single bundle survives" is not. Every
local copy is one disk, so the concern is real and its magnitude was overstated. Your instinct to
state the risk precisely rather than maximally was right; this is a correction in that same
direction.

=== KEPT ===

You verified that committing the receipt moved the tip 557baee → f234485 WITHOUT changing Hash E,
because diff-hash excludes the QGR directory — and you checked rather than assumed, on the ground
that otherwise no receipt could verify its own commit. That is row 67's
probe-asserts-its-own-precondition rule applied unprompted, one day old. Gate accepted with commands
named both ways: configured 866/4/0, selected 835/4/31, `ruff format --check` as its own command.

=== STANDING LESSON, mine as much as yours ===

When a push is refused and every visible route is destructive, THE NEXT MEASUREMENT IS WHETHER A
NON-DESTRUCTIVE DESTINATION ALREADY EXISTS. A refused push reports the ref you aimed at, not the set
of refs you could aim at. We both reasoned forward from the refusal instead of enumerating
alternatives, and a fast-forward had been sitting there the whole time.
