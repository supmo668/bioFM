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

---

## Corroboration 2026-09-24 — independently re-derived by `perturb-seq-eval`, with line numbers and a live incident

Re-filed from scratch by a worktree agent that **could not see this file** (see below). Its
evidence is sharper than the original and is merged here rather than kept as a second file:

- **`tools/git-safe-commit:325-328` runs `git add -A` unless `--staged` is passed.**
- **`skills/coord-commit` step 8 never passes `--staged`**, so the precise staging done in
  step 7 is discarded.
- **Live incident:** commit `84a8602` (`misc: coord commit`) swept T0's `pyproject`/
  `app_v05.py` dependency pins **plus an untracked `baseline.md` written by a concurrent
  implementer** into a coordination commit.

Its proposed fix is also stronger than the original's: not only should `coord-commit` pass
`--staged`, but **invert the default** — `git-safe-commit` should stage nothing implicitly
and **refuse non-allowlisted paths in `--no-work-item` mode**. An opt-in sweep is a
footgun; an opt-out one is a trap.

**Actionable at source:** `plugin.source_path` is `/Users/mo/github/aiadlc`, so this can be
fixed upstream rather than only logged.

### Why it was re-filed — and it is not carelessness

Measured 2026-09-24: **this file is not on `origin/main`**, and neither are 19 others.
**20 of 28 files in `.claude/aiadlc-feedback/` are invisible from `origin/main`.** A worktree
agent syncing through the sanctioned path (`worktree-sync`, which merges `origin/main` only)
can see **8 of 28**. It re-derived a known finding because the record was unreachable.

This is the **mirror** of
`2026-09-17-feedback-filed-from-a-worktree-never-reaches-the-trunk-and-stays-invisible.md`.
Both directions are broken: worktree→trunk by path, and trunk→worktree by the unpushed
trunk. The corpus only works for whoever holds the local trunk.

**Consequence for the plugin, beyond this one item:** a feedback log whose whole value is
"do not re-derive this" silently loses that value for every agent that is not the trunk
holder. Worth considering whether the log belongs somewhere that does not depend on a push —
or whether `/feedback` should check for an existing filing by matching the target + symptom
before creating a new file.

