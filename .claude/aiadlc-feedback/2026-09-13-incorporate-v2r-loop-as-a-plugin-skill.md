---
type: plugin-feedback
target: aiadlc plugin (aiadlc-plugins)
plugin_version: 0.54.0
reporter: bioFM/main/cto
date: 2026-09-13
scope: plugin / operating-system behavior — NOT repo/app work
---

# Proposal: incorporate `/v2r-loop` as a plugin skill

## 🟢 1. The framework has no vision → code loop, and one now exists that is proven

**Symptom:** aiadlc's lifecycle starts at `/create` and assumes a human drives each phase.
There is no path from a single stated intent to a reviewed branch without an operator at
every boundary. `/cto-loop` and `/ceo-loop` automate *sweeping* work; neither builds.

**What exists:** `/v2r-loop` was designed, built and run today in
`supmo668/Aviary-BioSim` (public), mounted as the `projects/aviary-biosim` submodule of
bioFM. It takes one free-text vision and drives it to a reviewed branch under a gate the
implementing agent cannot pass by assertion.

```
.claude/skills/v2r-loop/SKILL.md          the driver — stages 0-5
.claude/skills/v2r-loop/scripts/register.py   451 lines, no LLM, owns every transition
.claude/skills/v2r-loop/scripts/tests/    42 tests, adversarial on the gate
docs/CONTEXT.md                            glossary (4 collisions resolved)
docs/adr/0001-0004                         the decisions, each with its declined alternative
docs/spec.md · docs/plan.md                the approved design and its build plan
```

**Evidence it works:** one complete run closed 6 of 6 build units, each by a sealed test
written by an author that never saw the implementation. 117 tests green across the loop and
its output. The run's own product — a spend meter — was then ported into this plugin as
`tools/spend` (branch `cto/spend-meter`), which is the clearest signal that the loop
produces framework-grade components rather than demo code.

## Why it belongs in the plugin rather than in one repo

It is **not** app code. It is a lifecycle phase with the same shape as `/build`, and today
it is invisible outside the submodule that owns it: bioFM's own `.claude/skills/` cannot see
it, so `/v2r-loop` does not resolve from the agency root. Every repo that wants it would
otherwise copy it, and the copies would drift.

It also already leans on plugin machinery — `tools/instinct` for the learning substrate,
`tools/spend` for ceilings, the `test-seal` hook for the sealed directory, `git-safe-commit`
for every commit. It is closer to a missing plugin skill than to a repo-local tool.

## Where the pieces map

| From Aviary-BioSim | To the plugin | Note |
|---|---|---|
| `.claude/skills/v2r-loop/SKILL.md` | `skills/v2r-loop/SKILL.md` | stage 1 calls `/research`, `/grill-with-docs`, `/writing-plans` — substitute aiadlc's own `/research` and `/grill-me` |
| `scripts/register.py` | `tools/register` | rename to house style; **it is stdlib + pyyaml**, unlike `tools/instinct` which is stdlib-only — either accept pyyaml or port the YAML read to `tools/config` |
| `scripts/tests/` | `tests/` | 42 tests, keep all of them; the gate's refusal matrix is the whole value |
| `docs/CONTEXT.md` | `reference/REFERENCE-V2R-LOOP.md` | the glossary is load-bearing, not decoration |
| `docs/adr/0001-0004` | fold into the reference | each records the alternative that was priced and declined |

## Known defects, stated before anyone finds them

Three surfaced today and **none is fixed**; all three are documented at source:

1. **The instinct pin does not identify what it names.** It is a git tree SHA over
   `.aiadlc/instincts`, whose frontmatter is rewritten by Stop-hook reinforcement and by
   `instinct decay` — so the pin moves when nothing was learned, and can move *during* a run.
   `cmd_close`'s `git add -A` can then sweep hook-mutated instinct files into build-unit
   commits. Fix ranked cheapest-first in `docs/drain-1-notes.md`; the first is to hash the
   instinct bodies and exclude the volatile frontmatter.
2. **Per-unit prompts are not pinned.** The run is attributable, not reproducible. The
   documented claim was narrowed rather than the machinery built.
3. **`weave.publish` wrote objects, not calls** — instrumented and unreadable. Fixed, and
   the general lesson is recorded: verify a mechanism by observing the property it promises
   from the outside, never by confirming the mechanism ran.

All three share one shape, and it is the honest frontier of the design: **a mechanism
reports success while the property it exists to guarantee is absent.** The sealed gate
catches a unit that fails; it is blind to a mechanism that passes for the wrong reason,
because passing is the only signal it reads. All three were caught by hand.

## Proposed next step

Adopt as `skills/v2r-loop` + `tools/register` on a branch in the plugin source, port the 42
tests unchanged, and decide the pyyaml question. Defect 1 should be fixed before the skill
ships, since the pin is computed inside the trusted component.

**Status:** open — implementation available, public, tested

**Source:** https://github.com/supmo668/Aviary-BioSim · local: `projects/aviary-biosim`
