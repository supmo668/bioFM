# `plan-gate sign` regenerates the approval marker wholesale and silently destroys everything below the frontmatter

**Tool:** `tools/plan-gate` (plugin 0.52.0), `sign` subcommand
**Severity:** high — destroys the only record that distinguishes a human approval from a delegated one
**Observed seven times** (as of 2026-09-15), by three different actors — see the addendum at the end

## What happens

`plan-gate sign` rewrites `plan-approval.md` from a template. Anything a previous signer added below
the generated frontmatter and `## Summary` — provenance fields, delegation scope, incident records —
is **silently discarded**. No warning, no diff, no non-zero exit.

## Why it is worse than ordinary clobbering

`plan-gate verify` **passes before, during and after**, because the plan hash never moves. The gate
binds the *plan file*; the marker is not in its digest. So the only mechanism that could notice the
loss is the disclosure that was just deleted.

This workstream added those fields for a specific reason (filed as B4): the marker could not
distinguish *the principal approved this plan* from *the CTO re-signed it*. Six consecutive
re-signs were indistinguishable from human approvals. The fields are the fix — and the signing tool
deletes them.

## Observed twice

**2026-09-03 02:08** — a worktree agent re-signed over the same plan hash. All five disclosure
fields and the provenance block vanished, leaving a summary that read as a direct human approval.
Detected only because another session diffed the file. This is what prompted restricting
`plan-gate sign` to the gate owner.

**2026-09-14 13:28** — the CTO signed r2.9 under a standing delegation, having *captured the file
first specifically because of the earlier incident*. All four blocks stripped again.

The second occurrence is the important one: it proves the first was **not agent misbehaviour**. It
is the tool's normal, documented-nowhere behaviour, and restricting *who* may invoke it does not
address it at all.

## Repro

1. Add any content below `## Summary` in `plan-approval.md` — e.g. `approval_route: …`.
2. Edit the plan; run `plan-gate sign`.
3. The added content is gone. `plan-gate verify` passes.

## Suggested fix

- **Preserve everything below the generated section.** Regenerate frontmatter and `## Summary`; append
  or leave untouched whatever follows.
- Failing that, **warn loudly and non-zero** when the existing marker carries content the rewrite
  will drop, naming what will be lost — the same "fail loudly means non-zero exit" rule this
  framework applies elsewhere.
- Consider hashing the marker separately from the plan, so `verify` can report
  *plan intact, marker changed* rather than treating marker loss as invisible.

## Workaround in force

Capture `plan-approval.md` before every `plan-gate sign`, restore the blocks afterwards, and verify
the restoration. **A green `plan-gate verify` is not evidence that the approval record is intact.**

## Addendum 2026-09-15 — occurrences four and five

**2026-09-15 01:01 (`0b8d0c3`)** — a second CTO session recorded a genuine direct principal approval.
The disclosure blocks were lost again, and that commit's message claimed "provenance trail restored"
while deleting 72 lines. A message asserting restoration is not evidence of it.

**2026-09-15 01:40 (r2.11)** — the CTO, capturing beforehand per the standing procedure; stripped
again, restored manually.

Three distinct actors now (worktree agent, two CTO sessions). The workaround depends on every signer
knowing it; one that doesn't — or believes it already did it — loses the record silently. This is the
strongest argument for the fix being in the tool rather than in procedure.

**2026-09-15 11:19 (r2.12)** and **2026-09-15 12:43 (r2.13)** — occurrences six and seven, the same
CTO, captured beforehand and restored by hand both times.

## A second defect the workaround exposes: hand-restored frontmatter is unvalidated

The r2.12 restoration put `{t,m,s}` inside a YAML flow sequence, which parses as a flow *mapping*.
**The frontmatter was invalid YAML and `plan-gate verify` passed anyway**, because it does not parse
the disclosure fields — it only compares the plan hash. The break was caught by a separate parse
check, not by the gate.

So the tool's rewrite behaviour forces hand-editing of a YAML block that the tool itself never
validates. Two consequences worth fixing together:

- **`plan-gate verify` should parse the marker's frontmatter and fail loudly if it is not valid
  YAML.** A marker that cannot be parsed cannot be audited, and today that state is invisible.
- **Preserving content below the frontmatter** (the original request) would remove the need for hand
  restoration entirely, and with it this failure mode.

Seven restorations by hand is seven chances to introduce exactly this kind of error.
