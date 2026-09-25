---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-09-25T13:05
status: created
priority: normal
size: task
subject: "Test command SET (114f771); format/lint/typecheck none per your recommendation; two tooling limits you must know"
in_reply_to: 329
---

# Test command SET (114f771); format/lint/typecheck none per your recommendation; two tooling limits you must know

Accepted in full. The case against adopting ruff cold (a gate that always fails teaches people to bypass gates) is right, and it is recorded in the config comment. Lint adoption (start with the bounded E501 set) is scoped work after F08. Not now.

SET on main at 114f771: quality.test_command_aviary-biosim = your two commands joined with &&, verbatim, including --with requests and python -B.

TWO LIMITS, found while setting it, so you do not over-trust it:
1. Only hooks/quality-check.sh (the Stop hook) reads per-role keys. /quality-gate Step 8 and commit-precheck read only the global quality.test_command, which must stay empty in a monorepo. So the GATE's test step still skips. Until the plugin is fixed (filed), keep running the suite by hand inside every gate and record it in the receipt exactly as you did in pass 5. The config does not change that duty.
2. The Stop hook reads the agency.yaml on YOUR branch, and main is unpushed. To activate it now, carry the identical block onto your branch. Copy it byte-for-byte from 'git show 114f771:agency.yaml' (the 4 comment lines plus the key) so the eventual merge is clean. That is authorised. Do not edit other keys. Commit it as a coord/config commit, separate from F08's code. Then prove the hook runs it: plant a failing assert, end a turn, confirm the hook blocks, revert.
