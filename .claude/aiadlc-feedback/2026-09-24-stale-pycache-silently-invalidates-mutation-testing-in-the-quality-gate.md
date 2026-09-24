---
type: plugin-feedback
target: aiadlc plugin (bioFM) — quality-gate mutation step
plugin_version: 0.56.0
reporter: bioFM/matthew-mo/cto
date: 2026-09-24
scope: plugin / operating-system behavior — NOT repo/app work
---

# 🔴 Stale `__pycache__` silently invalidates mutation testing, and the two obvious checks cannot detect it

**Reported by:** `biofm/matthew-mo/aviary-biosim`, dispatch #215. Reproduced
independently by its test reviewer, then **proved** by its scorer, which constructed a
valid stale `.pyc` and showed a normal import serves it.

## Symptom

The quality gate's mutation step follows a mutate → run → restore loop. When those
steps complete inside one second, CPython can leave a `.pyc` whose recorded
`(mtime, size)` pair still validates against the restored source. The next run then
**executes the mutant while the file on disk is correct**.

Consequence: a mutation is reported as *surviving* (or as *caught*) on the basis of a
run that did not execute the code being claimed. The agent lost time to two false
failures before finding it.

## Why it is hard to catch — both natural checks fail

This is the part worth propagating, because the obvious defences do not work:

| check | why it passes anyway |
|---|---|
| `inspect.getsource(fn)` | reads the **source file**, not the code object, so it shows the correct body while the mutant executes |
| `cmp` / `diff` against the backup | the source **is** identical — restore succeeded; the stale artifact is the `.pyc` |

So an agent doing the responsible thing — verify the file was restored — gets a green
answer from both instruments. The invalidation is invisible at the level anyone would
think to look.

Same family as the other items filed today: **an instrument reports on something
adjacent to the thing it describes.** Here the adjacent thing is the source file, while
what executes is the cached bytecode.

## Blast radius — it reaches backwards

Every mutation claim produced by that loop without cache clearing is **unverified**.
For this repo that is the `#152` gate and its re-gate. The fixes themselves are not in
doubt (separately reviewed, suites green); the *mutation counts* cited as evidence of
gate effectiveness are.

Measured before ruling on a re-run: the "eight false fixes, all caught" figure appears
in **no repository document** — a repo-wide markdown grep returns nothing, and no public
doc in the submodule cites mutation counts. It exists only in dispatch prose, so no
published claim currently depends on it. Ruling was therefore: record it as unverified
in the deferred-findings register rather than spend compute re-verifying prose, and
re-run before it is ever published.

## Suggested fixes, in order

1. **Run the gate's mutation step with bytecode writing disabled** — `python -B`, or
   `PYTHONDONTWRITEBYTECODE=1` in the gate's environment. One environment variable
   removes the entire class.
2. **Or clear `__pycache__` between mutate and run**, which is heavier and easy to
   forget; prefer 1.
3. **State the hazard in the mutation guidance**, together with the fact that
   `inspect.getsource` and a source `cmp` do *not* detect it — otherwise the next agent
   re-derives this at the same cost.
4. **Have the mutation step assert that the mutant actually ran** (e.g. the mutated
   line raises, or a sentinel is observed), rather than inferring execution from the
   test outcome. This is the only fix that is robust to the next caching surprise
   rather than to this one.

## Status

open. Locally mitigated by convention: mutation runs under `python -B` going forward,
and the affected historical counts are to be recorded as unverified rather than
restated.
