# The run journal does not record git state

**Status:** accepted (principal, 2026-09-02)

A&D §4.4a requires every run record to carry enough environment to prove two runs were the
same computation, and it originally listed the git commit, a dirty flag, and the dirty file
list. Capturing those meant shelling out to `git` with a caller-supplied working directory —
and `git` executes repo-local `core.fsmonitor`, so a planted repository ran arbitrary commands
as the pipeline user. This was reproduced three times independently during the S12 quality
gate. Under n8n or cron, `CHIPSIM_PROJECT_ROOT` is exactly the kind of value that arrives from
workflow config, so it is untrusted input rather than a convenience knob.

**We deleted the feature rather than hardening it.** A PoC run journal has no need to run
`git` at runtime; removing the sub-feature takes the attack surface to zero, where validating
the path and disabling repo-local config would only shrink it. The code version is recorded
from what the installed package reports instead.

## Consequences

A run record **cannot prove the working tree was clean when it ran.** That is a real loss —
A&D §4.4a put dirty-tree detection in bold — and it is stated on the run record's own
documentation rather than papered over. Dirty-tree detection returns if and when there is an
independent reason to run `git` at runtime.

A second effect worth knowing: this removed the `dirty_files -> []` mutant, which was the
worst of the four that left the test suite 29/29 green while hiding a dirty tree.

## Considered options

- **Harden in place** — validate `project_root` and disable repo-local config. Rejected: keeps
  a subprocess-with-untrusted-cwd in a PoC that never needs one, and leaves attack surface > 0.
- **Keep git state, accept the risk** — rejected outright; it is remote code execution.
