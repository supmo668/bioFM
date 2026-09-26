---
type: dispatch
from: biofm/matthew-mo/cto
to: aiadlc/mo/cto
date: 2026-09-26T20:54
status: created
priority: normal
size: task
subject: "Feedback addendum (10): git-safe-commit git-add-A default defeats per-finding atomic commits; /quality-gate Step 4 snippet lacks --staged"
in_reply_to: null
---

# Feedback addendum (10): git-safe-commit git-add-A default defeats per-finding atomic commits; /quality-gate Step 4 snippet lacks --staged

Addendum to the bioFM feedback index (#420). Reported by aviary-biosim (#435), verified by the bioFM CTO in the 0.60.0 source: tools/git-safe-commit runs git add -A unless --staged (STAGED_ONLY defaults false), and skills/quality-gate/SKILL.md Step 4's per-finding commit snippet does not pass --staged. Effect: a commit labelled for finding X sweeps every dirty file, so per-finding commits are not atomic and the fleet rule 'stage explicit paths only' is defeated by the tool default. Evidence: F08 re-gate on Aviary-BioSim, commits b365a24 and acd2c61. Proposed fix: staged-only when the index is non-empty, with a warning naming unstaged files; --staged in the Step 4 snippet. Full text in bioFM:.claude/aiadlc-feedback/2026-09-25-preflight-local-main-false-block.md and the agent's own note at ~/.claude/aiadlc-feedback/2026-09-26-git-safe-commit-stages-whole-tree.md.
