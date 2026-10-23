---
type: master-updated
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-19T17:42
status: created
priority: normal
size: task
subject: "PR #28 LANDED — merge 9680679, NO release (principal chose --no-release). Self-retire worktrees/perturb-seq-eval when clear. CI did not run."
in_reply_to: null
---

# PR #28 LANDED — merge 9680679, NO release (principal chose --no-release). Self-retire worktrees/perturb-seq-eval when clear. CI did not run.

LANDED. Your #676 work is on origin/main.

pr: supmo668/bioFM#28
merge_commit: 9680679c30d5d6e97ab4ed957e92708dae1a3f13
landed_tip: bdc4703 (NOT the e27eeba your dispatch quoted - see below)
receipt: ...-qgr-pr-prep-20261018-0449-7ba0ff9.md, Hash E 7ba0ff9, re-verified at PR creation and reported as DERIVED from parent gate 8795772 (review evidence INHERITED, subset diff gated by hash_e). I quoted that qualifier in the PR body rather than writing a bare 'verified'.
version: NO BUMP, NO RELEASE. The principal typed the land without --no-release, but I asked before mutating because framework.version 0.3.0 -> 0.4.0 would have cut a PUBLIC tag v0.4.0 on a repo whose DOIs cite research v0.6.0 - an avoidable number collision. They chose --no-release. So agency.yaml is untouched and no GitHub release exists. Used pr-create --no-bump.
origin/main: 357944b -> 9680679.

TWO THINGS I CORRECTED, both worth your attention:

1) YOUR SUBMITTED SHA WAS STALE. #676 said e27eeba; the pushed tip was bdc4703, one commit ahead - your own pr-submit artifact (one file, 25 lines, under .claude/usr/.../dispatches/). I verified it was safe rather than assuming: the diff vs origin/main EXCLUDING .claude hashes identically at both tips (e1259b6788f3). Benign, but a land targeting e27eeba would have failed precondition 4 opaquely. Structural: committing the submit artifact moves the tip past the sha the submit names. Already filed as framework feedback.

2) I HAD TO CORRECT MY OWN CI CLAIM, publicly, before merging. I told you 'bioFM has NO workflows on main'. GitHub actually lists THREE ACTIVE workflows for the repo (chipsim-m1-inputs.yml, hacp-docs.yml, dependabot graph) - but NONE of their files exists on origin/main; the two real ones live only on an unlanded branch. Substantively my point held (zero checks, statusCheckRollup empty) but the sentence as written was false, so I rewrote the PR body to say precisely that. Same subject-specification discipline that cost us six layers on the lung thread: 'the repo has no workflows' and 'no workflow exists on the ref this PR targets' are different claims.

CI DID NOT RUN - do not let this be written up as 'CI green'. statusCheckRollup was empty. The only test evidence is your measured 1218 passed at 1ae73e4 plus fill_v060_numbers --check matching. Your disclosures are in the PR body verbatim: C3 as a declared CHANGELOG gap per the principal's 2026-10-18 call, and ruff 0.17 pre-existing lint that main also fails.

MERGE SYNC HIT A CONFLICT and I resolved it as a UNION, nothing dropped: docs/hacp/decision.md - your two 2026-10-16 rows (D-1 deposit B, D-2 published with both DOIs) vs five older CTO rows. Both sets kept, newest first to preserve the table's date-descending order. Concluded as beb79bb. If you think a row belongs elsewhere, say so.

YOUR ACTION: self-retire worktrees/perturb-seq-eval when you have no pending work - /worktree-delete perturb-seq-eval. I have NOT deleted the branch or the worktree; the post-land audit lists both and deletion is confirm-gated. origin/perturb-seq-eval and the local branch both still exist at bdc4703.

NOT DEPLOYED, and that is correct rather than skipped: no DevEx role is configured in this repo and this change ships no runtime service. The artefacts were already live on Zenodo and Figshare since 2026-10-16; this PR landed the repository record of that publication.
