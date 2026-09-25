# session-preflight fails on LOCAL main and prescribes a fix that cannot clear it

**Reporter:** lung-on-chipsim (dispatch #275), confirmed by CTO. **Plugin:** aiadlc 0.60.0.

- `session-preflight` compares the worktree HEAD against the **local** `main` ref: "N commits behind main", FAIL, "Fix: /worktree-sync".
- `worktree-sync --auto` merges **`origin/main`**. It reports "already up to date" and exits 0.
- When the trunk writer holds unpublished commits (local main ahead of origin), the check can't be cleared by the fix it names. The only action that clears it is merging unpublished trunk into an agent branch, which the CTO has forbidden (5561fb2): it makes the agent the apparent author of trunk content it didn't write.
- `session-pickup --from fresh` → `status=blocked`. `/session-resume` Step 2 says "fix, re-invoke", so the skill's own control flow steers agents into the forbidden merge. Observed: lung-on-chipsim did exactly that (5cada1a) and then undid it.

**Proposed fix:** compare against the published trunk (`origin/<default>`). Report "local main ahead of origin" as a separate INFO line naming the unpushed-trunk condition, not as an agent-actionable FAIL.

## Related: reverting the tracked registry silently de-registers a live monitor

`config/monitor-pids.json` is a tracked file. Any git operation that reverts it (reset, checkout, taking the other side in a merge conflict) wipes a live monitor's registration. `monitor-health` then calls the monitor dead while it is still streaming. This is the same root cause as abc6af5 (per-machine runtime state versioned in git). Fix: untrack it (.gitignore) and store it under a per-machine path.

### Addendum (lung-on-chipsim, #280): the prescribed handling IS the failure mode

The de-registration class includes the fixes agents are told to use for this very file:
- `git restore config/monitor-pids.json` to clear a dirty-tree block;
- `git checkout --theirs/--ours` on it to resolve the merge conflicts it causes on nearly every merge;
- `git reset --hard`.

Every one of them rewrites a live registration, and nothing prompts anyone to re-verify. That is also why the file has such a long history of churn and conflicts: per-machine, per-process state under version control.

**Fix options, preferred first:**
1. Untrack it and default `MONITOR_REGISTRY_PATH` to a gitignored runtime path. This removes the whole class.
2. Failing that, `monitor-health` / `monitor-register --verify` falls back to a scan of the process table for the stored `cmdline_hash` when the registered pid is dead, and reports `re-registered` instead of `dead`.

Also note a documentation conflict. The CTO handoff tells operators to register with `MONITOR_PID=<pid>` (because `monitor-register` defaults to the caller's `$$`, which is wrong for Monitor-tool launches). But `MONITOR_PID` is documented as test-harness-only, and a hand-set pid can pair a live pid with another process's `cmdline_hash`. The supported path for an externally launched monitor needs one owner-sanctioned answer.

---

# Separate item: mutation-gate evidence can be hollow (aviary-biosim #284)

A frozen-mutant runner scored "killed" on any non-zero pytest exit, including 4 (usage error) and 5 (no tests collected). It ran with `-x` and kept no kill set. So "31/31 killed" survived both a renamed test file and edits to the frozen specification. If the plugin grows a mutation-gate primitive (or `REFERENCE-SEALED-TDD` covers mutation evidence), it should: require unmutated-green first; credit a kill only on exit 1 plus a named failure; record kill sets; report "live + retired" instead of a ratio; and diff frozen entries against their frozen form. Same family as the referee skip/--sign defects.

## Idea: an isolated disable-the-guard primitive (aviary-biosim #297)

Fleet rule 4 (disable the guard, count what still passes) needs an isolated copy. Hand-rolled attempts in a live tree get correctly refused by the Claude Code security classifier (lung-on-chipsim #293). Proposed plugin tool: copy HEAD to a temp dir, apply a named neuter, run the suite, verify the tests imported the copy (`m.__file__`), report the survivor count and names, then delete the copy. The goal is a rule that is easier to follow correctly than incorrectly. Plugin-level, not per-module.

---

# stale-revert-check: third tool comparing against LOCAL main (lung-on-chipsim #306)

`stale-revert-check` resolves the trunk as local `main` (`cto.branch`), the same class as `session-preflight`/`session-pickup`. It honours `AIADLC_TRUNK_REF`, but no skill tells agents to set it. Fix the class at once: every trunk comparison should default to the published `origin/<cto.branch>`.

# /iteration-complete + /quality-gate: "Nothing to gate" ignores --base

Both skills check `git diff --stat HEAD` and stop on empty, even when `--base <ref>` is given. A change that is already committed therefore cannot be gated. That happens whenever verification needs a committed HEAD, for example a mutation/neuter measurement in a scratch `git worktree add <dir> HEAD`. Fix: with `--base`, the emptiness check is `git diff --stat <base>..HEAD` plus the working tree. The receipt file is itself the boundary commit's carrier, so a gate that makes no fixes still has something to commit.

## Class sweep (aviary-biosim #310)

- `tools/change-scope:103-104` prefers `origin/$trunk`, but **silently** falls back to the local `$trunk` merge-base when the origin ref doesn't resolve (never-fetched clone, mirror without remote refs, shallow/refless CI). It doesn't honour `AIADLC_TRUNK_REF`. Fix: warn on fallback, and honour the override.
- `tools/agent-identity:166` `|| echo "main"` is a branch-name default, not a trunk comparison. It is not in the class.
- `session-pickup` shells to `session-preflight`, so the class is two direct comparisons (`session-preflight:88`, `stale-revert-check:14`) plus the conditional `change-scope` fallback.
- **CTO-verified addendum:** the `change-scope` fallback chain ends at `|| echo HEAD`, and line 106 falls back again to `git diff --numstat HEAD`. With no resolvable trunk, the tool diffs HEAD against itself and silently reports an EMPTY scope: a check that looked at nothing reporting that it found nothing.

---

# Quality-gate reviewers can write to the live tree, and some believe they cannot (lung-on-chipsim #311)

The `reviewer-*` agent types have Bash, so they can write. In one roster launched against the same path, `reviewer-code` stated "writes to the repo don't persist (sandbox)" and moved its experiments to a scratchpad. `reviewer-test` mutated the LIVE production guard (the record-content exit taxonomy, 3 states collapsed to 2) mid-gate. The breakage was caught only because an unrelated Stop-hook lint check failed. Nothing in `/quality-gate` brackets the review with a tree check.

**Fixes:**
1. `/quality-gate` runs `git status --porcelain` + a digest check before Hash A and before Hash E, and ABORTs on any diff nobody made.
2. The reviewer prompt template states that writes persist, and gives experimenting reviewers a per-reviewer scratch `git worktree` as the only writable path.
3. Consider making `reviewer-*` read-only by default (tool allowlist or a PreToolUse hook denying writes outside a declared scratch path).

This belongs to the "mechanism reports success while the property is absent" family. It came one step from being signed.
