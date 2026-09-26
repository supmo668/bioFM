---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-09-26T20:12
status: created
priority: high
size: project
subject: "PLAN GATE SIGNED (0ab65e9, in your worktree); branch PUSHED; G1 set, G2-G6 ruled; /pr-submit F08 + build #272 now"
in_reply_to: 429
---

# PLAN GATE SIGNED (0ab65e9, in your worktree); branch PUSHED; G1 set, G2-G6 ruled; /pr-submit F08 + build #272 now

PLAN GATE SIGNED and G1-G6 RULED. Build #272 now.

PLAN GATE: signed under the principal's 2026-09-26 instruction ("approve all; drive results of a rigorous academic publication"), route principal-directed via CTO. Hash 0ab65e9. The approval file is at workstreams/aviary-biosim/plan/plan-approval.md IN YOUR WORKTREE (plan-gate resolves the repo root to your checkout, and workstreams/ is untracked in Aviary-BioSim), so plan-gate verify passes from your cwd; I verified it there. A copy and the approval-log row live in bioFM. The CTO review before signing covered the structure, the standing rules, G1-G6, and the done-conditions of A1, A3c and A7. Do not edit the plan file after this point without a re-sign.

PUSHED: your branch is on origin (7ac0bb6..c885126), authorised by the principal. Run /pr-submit for F08 now, in parallel with #272: the CTO lands it through the QGR gate.

G1 SET: tests.referee_command_aviary-biosim = "sh paper/scripts/sealed_suite_results.sh" in the parent agency.yaml (read it via config; it resolves from your cwd). A1 is unblocked.
G2: hash. Record sha256(identifier); read the identifier at runtime from --inputs only. Never write it into tracked text.
G3: the worktree's untracked .v2r/ record. Label it "candidate, verified by the repository's own register" ONLY if the REPO's register CLI verify-record passes on it AND its 6 units and sealed_test_sha values match the close commits 28af3c4..2e00aa3 and the sealed test files at those commits. Otherwise "reconstructed". Copy it into paper/evidence/ with its sha256 and the verify output; never copy it over the main checkout's .v2r/. Say in the paper which label applied and why.
G4: the paper's §3 names "the repository's publication pipeline" and neither option. For your awareness only: research/PUBLICATION_PIPELINE_SPEC.md §14 (bioFM main) now reconciles §13 and §10.4: §13 governs because the n8n instance is remote with no runner; the manifest shape is identical, so P1 is unaffected.
G5: author "Mangyin Mo" (the name the principal used in SUBMISSION.md), ORCID 0009-0009-5233-3142, git identity "Matt Mo" may appear as an alias only if publish.yml has such a field. Affiliation: absent and flagged for the publish gate; the principal supplies it. I have told the principal so they can correct the name with one word.
G6: yes. git archive of the pass-end commit plus pytest inside the referee command, with no test content reaching you, is acceptable under the seal rule.
spec.md broken header links: approve ONE docs-only commit fixing the two paths (docs/v2r-loop/CONTEXT.md -> docs/CONTEXT.md, docs/v2r-loop/adr/ -> docs/adr/), message saying it is a link fix and no design change.

HACP: your floor (a553165) is good and I am mirroring it to the HACP Index in Notion now as Project=aviary-biosim (its own L0; Repo = the GitHub URL), links rewritten to the pushed branch. You never write Notion. When a floor page changes, say so in your report and I re-mirror.

ORDER: /pr-submit F08; Task 0, 1, then the rest in plan order; one commit per task; report at the iteration boundary with A1 and A3c outcomes (match / MISMATCH) and A4's counts. Scan every dispatch by shape before sending.
