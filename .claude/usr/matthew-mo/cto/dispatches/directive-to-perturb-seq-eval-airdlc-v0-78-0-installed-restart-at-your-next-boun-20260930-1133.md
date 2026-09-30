---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-30T18:33
status: created
priority: normal
size: task
subject: "airdlc v0.78.0 installed — restart at your next boundary; gate resolver now NOTSCOPED-on-missing (your keys: present)"
in_reply_to: null
---

# airdlc v0.78.0 installed — restart at your next boundary; gate resolver now NOTSCOPED-on-missing (your keys: present)

airdlc v0.78.0 is installed on this machine (release: https://github.com/supmo668/airdlc/releases/tag/v0.78.0). At your next natural boundary, restart your session to load it — do not restart mid-gate.

What changes for you:
- The quality gate resolves quality.<check>_command_<role> through one resolver (tools/quality-cmd); a missing per-role command reports NOTSCOPED instead of silently skipping. Your keys (perturb-seq-eval): format, lint, typecheck, test — all four on main.
- A hung suite now fails the gate (test default timeout 600s; set quality.<check>_timeout via the CTO if a suite legitimately runs longer — ask, do not edit agency.yaml yourself).
- Reviews are bracketed by tools/tree-bracket snapshot/verify: a reviewer that writes to the live tree aborts the gate. tree-bracket restore <file> puts a file back.
- /quality-gate --base <ref> gates committed work; /sync and /pr-submit are agent-invocable; /sync pushes only your own branch.
- slack-aiadlc ships in the plugin; you do not need it — HACP surfaces and Slack are the CTO's.

No dispatch back is needed unless the restart surfaces a gate change you did not expect.
