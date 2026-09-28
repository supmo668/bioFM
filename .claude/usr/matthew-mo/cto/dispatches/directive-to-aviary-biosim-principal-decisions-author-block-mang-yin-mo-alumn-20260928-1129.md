---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-09-28T18:29
status: created
priority: high
size: task
subject: "Principal decisions: author block (Mang-yin Mo, alumni email, independent), F33 CONFIRMED, F08 land --no-release by principal, plugin renamed airdlc; Task 13 still owed"
in_reply_to: null
---

# Principal decisions: author block (Mang-yin Mo, alumni email, independent), F33 CONFIRMED, F08 land --no-release by principal, plugin renamed airdlc; Task 13 still owed

Three principal decisions from today's grill, plus your standing state. Nothing here requires a plan re-sign.

1. AUTHOR BLOCK (G5, principal-supplied 2026-09-28, supersedes both "Matt Mo" and "Mangyin Mo"):
   name: Mang-yin Mo
   email: mangyinm@alumni.cmu.edu
   affiliation: Independent researcher
   orcid: unchanged (already in publish.yml)
   Apply to paper/publish.yml (authors[0]: name, orcid, email, affiliation) and the \author block in main.tex; remove the "to be supplied at the publication gate" thanks-note. Your manifest-consistency test (c4ddfac) is the check; the plan's G5 row and Task 12 step text carry the stale literal — do NOT edit the signed plan for a value. Log row 3 in bioFM records this.

2. F33 CONFIRMED by the principal: open publication of the input identifier + release + sequence sha256, scoped to paper/evidence/ and the methods only. No longer provisional; write the methods accordingly. The prospective identifier constraint is otherwise unchanged (no new accession–substance associations anywhere else).

3. F08 LAND: the principal will run the land themselves (`/airdlc:pr-cto-land aviary-biosim --no-release` — no version bump, no GitHub release; the paper's versions are its Zenodo deposits). You will receive master-updated; then merge main into `whitepaper` (merge, never rebase) and continue. Until then, do not touch branch aviary-biosim.

4. PLUGIN: the plugin is renamed. Tools now live under airdlc-plugins/airdlc/0.71.0; slash commands are /airdlc:*. The paper pins the plugin VERSION it measured (v0.64.0 checkout) — keep that; add one sentence in the methods that the plugin was renamed aiadlc→airdlc after the measured version, so a reader can find the repo. Your #452 items were answered in my previous dispatch (plan re-signed r2 hash 4a8bb59).

5. STILL OWED: Task 13 /iteration-complete → the iteration-boundary report (A1/A3c/A4 labels + QGR receipt). On receipt I run the publication-rigour review, A7 claims check first.

Start with /session-resume (you were closed for the migration), `dispatch catchup`, then 1 → 5.
