# `/coord-commit` step 7 stages precisely with a wrapper that **blocks** `-A` — and step 8 runs `git add -A` and throws that index away

**Components:** `skills/coord-commit/SKILL.md` (steps 3, 4, 7, 8), `tools/git-safe-commit` (line 327), `tools/git-safe` (plugin 0.56.0)
**Severity:** high — the prescribed sequence silently commits every dirty file in the tree, including files under an explicit do-not-touch constraint, *after* the agent has verified the index is correct
**Observed:** 2026-09-18, bioFM. Self-reported by the `lung-on-chipsim` worktree agent within minutes of it happening; mechanism confirmed line-by-line by the CTO.

## The contradiction is inside one prescribed sequence

`/coord-commit` spends three steps establishing a precise index:

- **step 3** — "Stage ONLY coordination artifacts — never application code."
- **step 4** — `git-safe diff --cached --stat` to verify what's staged.
- **step 7** — `git-safe add <file>` for each file separately, *"the tool blocks `-A`, `--all`, `.`, wildcards"*.

Then:

- **step 8** — `git-safe-commit "message" --no-work-item`. **No `--staged`.**

And `git-safe-commit:327`:

```bash
if [ "$STAGED_ONLY" = false ]; then
    log_step "Staging all changes"
    git add -A
fi
```

`git-safe add` exists to make bulk staging impossible. Step 8 performs exactly the bulk staging step 7's tool refuses to perform, one command later, in the same prescribed sequence, from the same tool family.

## What it produced

The agent staged one file, verified with `git-safe diff --cached --stat` that exactly one file was staged, ran step 8 as written, and committed **two** files. The extra one was `config/monitor-pids.json` — a file under an explicit, previously-issued do-not-touch constraint from its coordinator.

It had passed `--staged` on every other commit that session, which is why this was the first time the defect was reachable.

## Why "the agent should have passed `--staged`" is the wrong lesson

The verification at step 4 was **correct and correctly performed**. The index was right when it was checked. The defect is that **`git-safe add`'s guarantee has no lifetime** — nothing preserves it across the very next command the skill instructs the agent to run.

A safety wrapper whose promise expires one prescribed step later is worse than no wrapper, because it purchases confidence that the sequence then invalidates. The agent did the careful thing and got the careless outcome, which is the signature of a tooling defect rather than an operator error.

It also composes badly with anything that makes the tree dirty for reasons outside the agent's control. In this repo `config/monitor-pids.json` is a **tracked file holding per-machine runtime state** (filed separately, same week), so it is dirty essentially always for anyone running a monitor. Any `git add -A` anywhere in this repository will keep sweeping it into unrelated commits — the two defects multiply.

## Suggested fixes, in order

1. **Add `--staged` to step 8 in the skill.** One word, fixes the prescribed path immediately.
2. **Invert `git-safe-commit`'s default.** Staging-all should be opt-in (`--all`), not opt-out (`--staged`). A commit tool in a "safe" family should not default to the behaviour its sibling tool blocks outright.
3. **Refuse the combination.** If `git-safe add` has staged anything in this session and `git-safe-commit` is called without `--staged`, error out and name the conflict rather than silently widening the commit.
4. **Log what step 8 actually staged.** `log_step "Staging all changes"` goes to the tool's log, not to the agent's verification surface. The agent's last observation of the index (step 4) disagreed with the committed result and nothing surfaced the divergence — the commit's own file list is the only evidence, and it appears after the fact.

## Credit where the process worked

The failure was caught by the agent itself, disclosed immediately as an escalation rather than folded into the next commit message, and reported at the moment it was easiest not to — its coordinator had just told it "nothing outstanding". It also declined to amend the unpushed commit to erase the evidence, on the grounds that rewriting history to hide one's own violation is the wrong default even when the history is private. None of that reduces the severity of the tool defect; it is the only reason the tool defect was observed at all.
