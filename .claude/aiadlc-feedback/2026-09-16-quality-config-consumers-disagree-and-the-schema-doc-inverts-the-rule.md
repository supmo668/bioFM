# Two consumers of `quality.*_command` disagree about the same config, one of them fails silently, and the schema doc states the rule backwards

**Components:** `hooks/quality-check.sh`, `tools/commit-precheck`, `config/agency.schema.md`
(plugin 0.56.0)
**Severity:** high for the doc error — it is the root cause; medium for the consumer disagreement
**Found by:** the lung-on-chipsim worktree agent, while correcting a change it had made on the
doc's authority

## (a) The schema doc states the resolution rule backwards, and omits the keys the hook implements

`config/agency.schema.md:38` says per-agent quality keys are unimplemented. The **blocking** Stop
hook `hooks/quality-check.sh` resolves `<key>_<agent>` **first** and **skips the global** when
`project.modules` is non-empty — the opposite of what the doc says — and the doc never documents the
`quality.*_command_<agent>` rows the hook actually reads.

An agent read the doc, concluded the per-agent form did nothing, and committed that conclusion as a
comment stating it as fact. The doc is the root cause: every repo that reads it inherits the same
wrong belief, and the belief is only falsifiable by reading the hook.

## (b) `tools/commit-precheck` and `hooks/quality-check.sh` resolve the same config differently

`commit-precheck` reads only the **plain** key; `quality-check.sh` resolves **per-agent**. With the
globals correctly empty (the right configuration for a monorepo where each module has its own
toolchain), the result is:

- `commit-precheck` finds nothing and **skips**;
- the Stop hook finds the per-agent command and **enforces**.

Two mechanical consumers, one config, opposite conclusions. Neither is wrong on its own terms.

## (c) A window where the precheck ran a permanently-failing check with output discarded

Between two commits, `commit-precheck` ran format/lint **non-blocking with output discarded**, so
three commits passed a check that was failing every time and showing nothing. That is strictly worse
than the honest `not configured — skipping` it replaced: a skipped check is visibly absent, while a
silenced failing check looks like a pass.

## (d) Anchoring — a consequence worth stating for whoever fixes the above

Both consumers `cd` to the **git toplevel**, which in a worktree is the worktree root. A command
like `uv run ruff check .` exits 2 there (`Failed to spawn: ruff`) because the Python project lives
in a subdirectory. Any documented example should be anchored (`cd <project> && …`), or the tooling
should resolve the module directory itself.

The same repo's sibling agents make this concrete: an unanchored global would have handed
**three** agents a permanently red blocking check — one using setuptools, one using Poetry (where a
`uv run` would write a stray `uv.lock` into a Poetry project), and one a submodule with no Python
packaging at all that nevertheless resolves the same `agency.yaml`.

## Suggested fixes, in order

1. **Correct `config/agency.schema.md`** and document the `quality.*_command_<agent>` rows, including
   the "per-agent first, global skipped when `project.modules` is non-empty" rule.
2. **Make the two consumers agree** — `commit-precheck` should use the same resolution as the hook.
3. **Never discard output from a check that can fail.** If a configured check fails, say so; if it is
   not configured, say that instead.
4. Document anchoring in the example values.

## Cross-reference

This is the third instance today of a tool deriving behaviour from ambient context rather than from
an explicit statement — see the monitor-identity and receipt-verification reports filed alongside.
Here it is the working directory again, plus a doc that disagrees with the code it documents.
